#include <cuda_runtime.h>

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr int kMaxN = 16;
constexpr int kMaxComparators = 64;
constexpr int kThreads = 256;

struct Score {
  std::uint32_t failures;
  std::uint32_t inversions;
};

struct Network {
  int channels = 0;
  std::vector<std::uint16_t> comparators;
};

struct Options {
  std::string mode = "verify";
  std::string network_path;
  std::string output_path = "best.net";
  int target_length = -1;
  int batch = 8192;
  int rounds = 10;
  int beam = 64;
  std::uint64_t seed = 130044;
};

struct GpuResult {
  std::vector<Score> scores;
  float kernel_ms = 0.0f;
};

struct Candidate {
  std::vector<std::uint16_t> network;
  Score score{};
};

#define CUDA_CHECK(expr)                                                       \
  do {                                                                         \
    const cudaError_t cuda_status_ = (expr);                                    \
    if (cuda_status_ != cudaSuccess) {                                          \
      throw std::runtime_error(std::string(#expr) + ": " +                    \
                               cudaGetErrorString(cuda_status_));               \
    }                                                                          \
  } while (false)

__global__ __launch_bounds__(kThreads)
void exact_score_kernel(const std::uint16_t* networks, int candidate_count,
                        int channels, int length, Score* scores) {
  const int candidate = static_cast<int>(blockIdx.x);
  if (candidate >= candidate_count) return;

  __shared__ std::uint16_t local_network[kMaxComparators];
  __shared__ std::uint32_t failure_sums[kThreads];
  __shared__ std::uint32_t inversion_sums[kThreads];

  for (int k = static_cast<int>(threadIdx.x); k < length; k += blockDim.x) {
    local_network[k] = networks[candidate * length + k];
  }
  __syncthreads();

  const std::uint32_t input_count = 1u << channels;
  const std::uint32_t channel_mask = input_count - 1u;
  std::uint32_t failures = 0;
  std::uint32_t inversion_total = 0;

  for (std::uint32_t input = threadIdx.x; input < input_count;
       input += blockDim.x) {
    std::uint32_t value = input;
    for (int k = 0; k < length; ++k) {
      const std::uint16_t packed = local_network[k];
      const unsigned a = packed & 0xffu;
      const unsigned b = packed >> 8;
      const unsigned low = (value >> a) & 1u;
      const unsigned high = (value >> b) & 1u;
      const unsigned exchange = low & (high ^ 1u);
      value ^= exchange * ((1u << a) | (1u << b));
    }

    std::uint32_t output_inversions = 0;
    for (int i = 0; i + 1 < channels; ++i) {
      if (((value >> i) & 1u) == 0u) continue;
      const std::uint32_t lower_bits = (1u << (i + 1)) - 1u;
      const std::uint32_t higher_mask = channel_mask & ~lower_bits;
      output_inversions += __popc((~value) & higher_mask);
    }
    failures += output_inversions != 0;
    inversion_total += output_inversions;
  }

  failure_sums[threadIdx.x] = failures;
  inversion_sums[threadIdx.x] = inversion_total;
  __syncthreads();

  for (int offset = kThreads / 2; offset != 0; offset >>= 1) {
    if (threadIdx.x < offset) {
      failure_sums[threadIdx.x] += failure_sums[threadIdx.x + offset];
      inversion_sums[threadIdx.x] += inversion_sums[threadIdx.x + offset];
    }
    __syncthreads();
  }
  if (threadIdx.x == 0) {
    scores[candidate] = {failure_sums[0], inversion_sums[0]};
  }
}

std::uint16_t pack_comparator(int a, int b) {
  if (a > b) std::swap(a, b);
  return static_cast<std::uint16_t>(a | (b << 8));
}

std::pair<int, int> unpack_comparator(std::uint16_t value) {
  return {value & 0xff, value >> 8};
}

bool score_less(const Score& a, const Score& b) {
  if (a.failures != b.failures) return a.failures < b.failures;
  return a.inversions < b.inversions;
}

bool score_equal(const Score& a, const Score& b) {
  return a.failures == b.failures && a.inversions == b.inversions;
}

Network read_network(const std::string& path) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot open network: " + path);

  Network result;
  std::string line;
  int line_number = 0;
  while (std::getline(input, line)) {
    ++line_number;
    const auto comment = line.find('#');
    if (comment != std::string::npos) line.erase(comment);
    std::istringstream fields(line);
    std::string first;
    if (!(fields >> first)) continue;
    if (first == "n") {
      if (!(fields >> result.channels)) {
        throw std::runtime_error("bad n header at line " +
                                 std::to_string(line_number));
      }
      continue;
    }
    int a = 0;
    int b = 0;
    try {
      a = std::stoi(first);
    } catch (...) {
      throw std::runtime_error("bad comparator at line " +
                               std::to_string(line_number));
    }
    if (!(fields >> b)) {
      throw std::runtime_error("bad comparator at line " +
                               std::to_string(line_number));
    }
    result.comparators.push_back(pack_comparator(a, b));
  }

  if (result.channels < 2 || result.channels > kMaxN) {
    throw std::runtime_error("channel count must be in [2,16]");
  }
  if (result.comparators.empty() ||
      result.comparators.size() > kMaxComparators) {
    throw std::runtime_error("comparator count must be in [1,64]");
  }
  for (const auto packed : result.comparators) {
    const auto [a, b] = unpack_comparator(packed);
    if (a < 0 || a >= b || b >= result.channels) {
      throw std::runtime_error("invalid comparator (" + std::to_string(a) +
                               "," + std::to_string(b) + ")");
    }
  }
  return result;
}

void write_network(const std::string& path, int channels,
                   const std::vector<std::uint16_t>& network) {
  std::ofstream output(path);
  if (!output) throw std::runtime_error("cannot write network: " + path);
  output << "# sn_gpu canonical certificate\n";
  output << "n " << channels << '\n';
  for (const auto packed : network) {
    const auto [a, b] = unpack_comparator(packed);
    output << a << ' ' << b << '\n';
  }
}

Score cpu_score(int channels, const std::vector<std::uint16_t>& network) {
  Score score{};
  const std::uint32_t input_count = 1u << channels;
  for (std::uint32_t input = 0; input < input_count; ++input) {
    std::uint32_t value = input;
    for (const auto packed : network) {
      const auto [a, b] = unpack_comparator(packed);
      const unsigned low = (value >> a) & 1u;
      const unsigned high = (value >> b) & 1u;
      if (low > high) value ^= (1u << a) | (1u << b);
    }
    std::uint32_t output_inversions = 0;
    for (int i = 0; i + 1 < channels; ++i) {
      if (((value >> i) & 1u) == 0u) continue;
      for (int j = i + 1; j < channels; ++j) {
        output_inversions += ((value >> j) & 1u) == 0u;
      }
    }
    score.failures += output_inversions != 0;
    score.inversions += output_inversions;
  }
  return score;
}

GpuResult gpu_score(int channels,
                    const std::vector<std::vector<std::uint16_t>>& networks) {
  if (networks.empty()) throw std::runtime_error("empty candidate batch");
  const std::size_t length = networks.front().size();
  if (length == 0 || length > kMaxComparators) {
    throw std::runtime_error("bad candidate length");
  }

  std::vector<std::uint16_t> flat;
  flat.reserve(networks.size() * length);
  for (const auto& network : networks) {
    if (network.size() != length) {
      throw std::runtime_error("mixed lengths in candidate batch");
    }
    flat.insert(flat.end(), network.begin(), network.end());
  }

  std::uint16_t* device_networks = nullptr;
  Score* device_scores = nullptr;
  cudaEvent_t start = nullptr;
  cudaEvent_t stop = nullptr;
  CUDA_CHECK(cudaMalloc(&device_networks, flat.size() * sizeof(std::uint16_t)));
  CUDA_CHECK(cudaMalloc(&device_scores, networks.size() * sizeof(Score)));
  CUDA_CHECK(cudaMemcpy(device_networks, flat.data(),
                        flat.size() * sizeof(std::uint16_t),
                        cudaMemcpyHostToDevice));
  CUDA_CHECK(cudaEventCreate(&start));
  CUDA_CHECK(cudaEventCreate(&stop));

  CUDA_CHECK(cudaEventRecord(start));
  exact_score_kernel<<<static_cast<unsigned>(networks.size()), kThreads>>>(
      device_networks, static_cast<int>(networks.size()), channels,
      static_cast<int>(length), device_scores);
  CUDA_CHECK(cudaGetLastError());
  CUDA_CHECK(cudaEventRecord(stop));
  CUDA_CHECK(cudaEventSynchronize(stop));

  GpuResult result;
  result.scores.resize(networks.size());
  CUDA_CHECK(cudaEventElapsedTime(&result.kernel_ms, start, stop));
  CUDA_CHECK(cudaMemcpy(result.scores.data(), device_scores,
                        result.scores.size() * sizeof(Score),
                        cudaMemcpyDeviceToHost));
  CUDA_CHECK(cudaEventDestroy(stop));
  CUDA_CHECK(cudaEventDestroy(start));
  CUDA_CHECK(cudaFree(device_scores));
  CUDA_CHECK(cudaFree(device_networks));
  return result;
}

std::vector<std::uint16_t> all_comparators(int channels) {
  std::vector<std::uint16_t> pairs;
  for (int a = 0; a < channels; ++a) {
    for (int b = a + 1; b < channels; ++b) {
      pairs.push_back(pack_comparator(a, b));
    }
  }
  return pairs;
}

void mutate(std::vector<std::uint16_t>& network,
            const std::vector<std::uint16_t>& pairs, std::mt19937_64& rng,
            int strength) {
  std::uniform_int_distribution<std::size_t> position(0, network.size() - 1);
  std::uniform_int_distribution<std::size_t> pair_index(0, pairs.size() - 1);
  for (int step = 0; step < strength; ++step) {
    const unsigned operation = static_cast<unsigned>(rng() % 5u);
    const std::size_t i = position(rng);
    if (operation <= 2) {
      std::uint16_t replacement;
      do {
        replacement = pairs[pair_index(rng)];
      } while (replacement == network[i]);
      network[i] = replacement;
    } else {
      std::size_t j = position(rng);
      if (operation == 3 && network.size() > 1) {
        while (j == i) j = position(rng);
      } else if (operation == 4) {
        j = (i + 1) % network.size();
      }
      std::swap(network[i], network[j]);
    }
  }
}

std::vector<std::vector<std::uint16_t>> initial_networks(
    const Network& source, int target_length) {
  std::vector<std::vector<std::uint16_t>> result;
  const int source_length = static_cast<int>(source.comparators.size());
  if (target_length == source_length) {
    result.push_back(source.comparators);
  } else if (target_length + 1 == source_length) {
    result.reserve(source_length);
    for (int drop = 0; drop < source_length; ++drop) {
      std::vector<std::uint16_t> candidate;
      candidate.reserve(target_length);
      for (int k = 0; k < source_length; ++k) {
        if (k != drop) candidate.push_back(source.comparators[k]);
      }
      result.push_back(std::move(candidate));
    }
  } else {
    throw std::runtime_error(
        "target length must equal source length or source length minus one");
  }
  return result;
}

std::vector<Candidate> select_elite(
    const std::vector<std::vector<std::uint16_t>>& networks,
    const std::vector<Score>& scores, int beam) {
  std::vector<std::size_t> order(networks.size());
  for (std::size_t i = 0; i < order.size(); ++i) order[i] = i;
  std::sort(order.begin(), order.end(), [&](std::size_t a, std::size_t b) {
    if (score_less(scores[a], scores[b])) return true;
    if (score_less(scores[b], scores[a])) return false;
    return networks[a] < networks[b];
  });

  std::set<std::vector<std::uint16_t>> seen;
  std::vector<Candidate> elite;
  for (const auto index : order) {
    if (!seen.insert(networks[index]).second) continue;
    elite.push_back({networks[index], scores[index]});
    if (static_cast<int>(elite.size()) == beam) break;
  }
  return elite;
}

void print_usage() {
  std::cout
      << "Usage: sn_gpu.exe --mode verify|benchmark|search --network FILE\n"
      << "  [--target-length L] [--batch N] [--rounds N] [--beam N]\n"
      << "  [--seed U64] [--output FILE]\n";
}

Options parse_options(int argc, char** argv) {
  Options options;
  for (int i = 1; i < argc; ++i) {
    const std::string argument = argv[i];
    auto value = [&]() -> std::string {
      if (++i >= argc) throw std::runtime_error("missing value for " + argument);
      return argv[i];
    };
    if (argument == "--mode") {
      options.mode = value();
    } else if (argument == "--network") {
      options.network_path = value();
    } else if (argument == "--target-length") {
      options.target_length = std::stoi(value());
    } else if (argument == "--batch") {
      options.batch = std::stoi(value());
    } else if (argument == "--rounds") {
      options.rounds = std::stoi(value());
    } else if (argument == "--beam") {
      options.beam = std::stoi(value());
    } else if (argument == "--seed") {
      options.seed = std::stoull(value());
    } else if (argument == "--output") {
      options.output_path = value();
    } else if (argument == "--help" || argument == "-h") {
      print_usage();
      std::exit(0);
    } else {
      throw std::runtime_error("unknown option: " + argument);
    }
  }
  if (options.network_path.empty()) throw std::runtime_error("--network required");
  if (options.batch < 1 || options.batch > 1000000) {
    throw std::runtime_error("--batch must be in [1,1000000]");
  }
  if (options.rounds < 1 || options.beam < 1 || options.beam > options.batch) {
    throw std::runtime_error("bad rounds/beam values");
  }
  return options;
}

int run_verify(const Network& network) {
  const std::vector<std::vector<std::uint16_t>> batch{network.comparators};
  const GpuResult gpu = gpu_score(network.channels, batch);
  const Score cpu = cpu_score(network.channels, network.comparators);
  if (!score_equal(gpu.scores[0], cpu)) {
    throw std::runtime_error("CPU/GPU score mismatch");
  }
  std::cout << "VERIFY {\"channels\":" << network.channels
            << ",\"length\":" << network.comparators.size()
            << ",\"binary_inputs\":" << (1u << network.channels)
            << ",\"failures\":" << cpu.failures
            << ",\"inversions\":" << cpu.inversions
            << ",\"gpu_ms\":" << std::fixed << std::setprecision(6)
            << gpu.kernel_ms << ",\"cpu_gpu_match\":true}\n";
  return cpu.failures == 0 ? 0 : 2;
}

int run_benchmark(const Network& network, const Options& options) {
  std::mt19937_64 rng(options.seed);
  const auto pairs = all_comparators(network.channels);
  std::vector<std::vector<std::uint16_t>> batch(
      static_cast<std::size_t>(options.batch), network.comparators);
  for (int i = 1; i < options.batch; ++i) {
    mutate(batch[i], pairs, rng, 1 + static_cast<int>(rng() % 3u));
  }

  (void)gpu_score(network.channels, batch);  // warm-up, not timed
  float kernel_ms = 0.0f;
  GpuResult last;
  const auto wall_start = std::chrono::steady_clock::now();
  for (int round = 0; round < options.rounds; ++round) {
    last = gpu_score(network.channels, batch);
    kernel_ms += last.kernel_ms;
  }
  const double wall_seconds = std::chrono::duration<double>(
      std::chrono::steady_clock::now() - wall_start).count();

  std::set<std::size_t> audits{0, batch.size() / 3, (2 * batch.size()) / 3,
                               batch.size() - 1};
  for (const auto index : audits) {
    const Score cpu = cpu_score(network.channels, batch[index]);
    if (!score_equal(cpu, last.scores[index])) {
      throw std::runtime_error("benchmark CPU/GPU audit mismatch at " +
                               std::to_string(index));
    }
  }
  const auto best = std::min_element(
      last.scores.begin(), last.scores.end(),
      [](const Score& a, const Score& b) { return score_less(a, b); });
  const double candidates =
      static_cast<double>(options.batch) * options.rounds;
  const double gpu_seconds = kernel_ms / 1000.0;
  const double binary_cases = candidates * (1u << network.channels);
  std::cout << "BENCHMARK {\"channels\":" << network.channels
            << ",\"length\":" << network.comparators.size()
            << ",\"batch\":" << options.batch
            << ",\"rounds\":" << options.rounds
            << ",\"audited_candidates\":" << audits.size()
            << ",\"gpu_seconds\":" << std::fixed << std::setprecision(6)
            << gpu_seconds << ",\"wall_seconds\":" << wall_seconds
            << ",\"candidates_per_gpu_second\":" << candidates / gpu_seconds
            << ",\"binary_cases_per_gpu_second\":"
            << binary_cases / gpu_seconds
            << ",\"best_failures\":" << best->failures
            << ",\"best_inversions\":" << best->inversions
            << ",\"cpu_gpu_audit\":true}\n";
  return 0;
}

int run_search(const Network& source, const Options& options) {
  const int target_length = options.target_length < 0
                                ? static_cast<int>(source.comparators.size())
                                : options.target_length;
  std::mt19937_64 rng(options.seed);
  const auto pairs = all_comparators(source.channels);
  auto networks = initial_networks(source, target_length);
  GpuResult scored = gpu_score(source.channels, networks);
  auto elite = select_elite(networks, scored.scores, options.beam);
  if (elite.empty()) throw std::runtime_error("empty elite set");

  double kernel_seconds = scored.kernel_ms / 1000.0;
  std::uint64_t evaluated = networks.size();
  for (int round = 0; round < options.rounds; ++round) {
    networks.clear();
    networks.reserve(options.batch);
    for (const auto& candidate : elite) networks.push_back(candidate.network);
    while (static_cast<int>(networks.size()) < options.batch) {
      const auto& parent = elite[static_cast<std::size_t>(rng() % elite.size())];
      auto child = parent.network;
      const int strength = 1 + static_cast<int>(rng() % (round % 8 == 7 ? 5u : 3u));
      mutate(child, pairs, rng, strength);
      networks.push_back(std::move(child));
    }

    scored = gpu_score(source.channels, networks);
    kernel_seconds += scored.kernel_ms / 1000.0;
    evaluated += networks.size();
    elite = select_elite(networks, scored.scores, options.beam);
    const Score cpu = cpu_score(source.channels, elite.front().network);
    if (!score_equal(cpu, elite.front().score)) {
      throw std::runtime_error("search best CPU/GPU mismatch");
    }
    std::cout << "ROUND {\"round\":" << (round + 1)
              << ",\"evaluated\":" << evaluated
              << ",\"best_failures\":" << cpu.failures
              << ",\"best_inversions\":" << cpu.inversions
              << ",\"kernel_seconds\":" << std::fixed
              << std::setprecision(6) << kernel_seconds << "}\n";
    if (cpu.failures == 0) {
      write_network(options.output_path, source.channels, elite.front().network);
      std::cout << "CERTIFICATE {\"path\":\"" << options.output_path
                << "\",\"channels\":" << source.channels
                << ",\"length\":" << target_length
                << ",\"failures\":0}\n";
      return 0;
    }
  }

  write_network(options.output_path, source.channels, elite.front().network);
  std::cout << "BEST {\"path\":\"" << options.output_path
            << "\",\"channels\":" << source.channels
            << ",\"length\":" << target_length
            << ",\"failures\":" << elite.front().score.failures
            << ",\"inversions\":" << elite.front().score.inversions
            << ",\"evaluated\":" << evaluated << "}\n";
  return 2;
}

}  // namespace

int main(int argc, char** argv) {
  try {
    const Options options = parse_options(argc, argv);
    int device = 0;
    CUDA_CHECK(cudaGetDevice(&device));
    cudaDeviceProp properties{};
    CUDA_CHECK(cudaGetDeviceProperties(&properties, device));
    std::cout << "DEVICE {\"name\":\"" << properties.name
              << "\",\"compute_capability\":\"" << properties.major << '.'
              << properties.minor << "\"}\n";

    const Network network = read_network(options.network_path);
    if (options.mode == "verify") return run_verify(network);
    if (options.mode == "benchmark") return run_benchmark(network, options);
    if (options.mode == "search") return run_search(network, options);
    throw std::runtime_error("mode must be verify, benchmark, or search");
  } catch (const std::exception& error) {
    std::cerr << "ERROR {\"message\":\"" << error.what() << "\"}\n";
    return 1;
  }
}
