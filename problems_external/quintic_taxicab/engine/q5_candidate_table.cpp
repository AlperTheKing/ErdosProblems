#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <numeric>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#include <boost/multiprecision/cpp_int.hpp>

namespace {

using boost::multiprecision::cpp_int;
constexpr std::uint64_t kFirstH = 48;
constexpr std::uint64_t kLastH = 512;
constexpr std::uint64_t kLaneCount = 64;

std::uint64_t floor_sum(std::uint64_t n, std::uint64_t m,
                        std::uint64_t a, std::uint64_t b) {
  std::uint64_t answer = 0;
  while (true) {
    if (a >= m) {
      answer += (n - 1) * n * (a / m) / 2;
      a %= m;
    }
    if (b >= m) {
      answer += n * (b / m);
      b %= m;
    }
    const std::uint64_t y_max = a * n + b;
    if (y_max < m) {
      return answer;
    }
    n = y_max / m;
    b = y_max % m;
    std::swap(m, a);
  }
}

std::uint64_t canonical_work(std::uint64_t h, std::uint64_t p,
                             std::uint64_t q) {
  const std::uint64_t uncapped = std::min(h, h * q / p);
  const std::uint64_t admissible =
      floor_sum(uncapped, q, p, p - 1) + (h - uncapped) * h;
  return h * h + admissible;
}

unsigned bit_length(const cpp_int& value) {
  if (value <= 0) {
    throw std::runtime_error("bit_length requires a positive integer");
  }
  return static_cast<unsigned>(boost::multiprecision::msb(value) + 1);
}

cpp_int pow_integer(cpp_int base, unsigned exponent) {
  cpp_int result = 1;
  while (exponent > 0) {
    if ((exponent & 1U) != 0U) {
      result *= base;
    }
    exponent >>= 1U;
    if (exponent > 0) {
      base *= base;
    }
  }
  return result;
}

struct Job {
  std::uint64_t weight;
  std::uint64_t p;
  std::uint64_t q;
};

struct Row {
  std::uint64_t h;
  unsigned bits;
  bool balance_pass;
  std::uint64_t maximum;
  std::uint64_t minimum;
  bool oeis_gate_pass;
  std::size_t specialization_count;
};

Row build_row(std::uint64_t h) {
  std::vector<Job> jobs;
  jobs.reserve(static_cast<std::size_t>(h * h));
  for (std::uint64_t p = 1; p <= h; ++p) {
    for (std::uint64_t q = 1; q <= h; ++q) {
      if (std::gcd(p, q) == 1) {
        jobs.push_back(Job{canonical_work(h, p, q), p, q});
      }
    }
  }
  std::sort(jobs.begin(), jobs.end(), [](const Job& left, const Job& right) {
    if (left.weight != right.weight) {
      return left.weight > right.weight;
    }
    if (left.p != right.p) {
      return left.p < right.p;
    }
    return left.q < right.q;
  });

  using Lane = std::pair<std::uint64_t, std::uint64_t>;
  std::priority_queue<Lane, std::vector<Lane>, std::greater<Lane>> heap;
  std::array<std::uint64_t, kLaneCount> loads{};
  for (std::uint64_t lane = 0; lane < kLaneCount; ++lane) {
    heap.emplace(0, lane);
  }
  for (const Job& job : jobs) {
    auto [load, lane] = heap.top();
    heap.pop();
    load += job.weight;
    loads.at(static_cast<std::size_t>(lane)) = load;
    heap.emplace(load, lane);
  }
  const auto extrema = std::minmax_element(loads.begin(), loads.end());

  const cpp_int H = h;
  const cpp_int radicand_bound = cpp_int(5760) * pow_integer(H, 10);
  const cpp_int b_squared =
      cpp_int(40) * pow_integer(H, 2) * pow_integer(H, 4) *
      pow_integer(cpp_int(2) * H, 3);
  const bool oeis_pass =
      cpp_int(4) * pow_integer(b_squared, 5) > pow_integer(cpp_int(10), 66);

  return Row{h,
             bit_length(radicand_bound),
             (*extrema.second) * 4 <= (*extrema.first) * 5,
             *extrema.second,
             *extrema.first,
             oeis_pass,
             jobs.size()};
}

void write_table(const std::filesystem::path& output) {
  if (std::filesystem::exists(output)) {
    throw std::runtime_error("refusing to overwrite output");
  }
  const std::filesystem::path temporary =
      output.parent_path() /
      (std::string(".") + output.filename().string() + ".tmp");
  if (std::filesystem::exists(temporary)) {
    throw std::runtime_error("temporary output already exists");
  }

  std::ofstream stream(temporary, std::ios::binary | std::ios::out);
  if (!stream) {
    throw std::runtime_error("cannot create temporary output");
  }
  stream << "{\"kind\":\"Q5_TORSOR_CANDIDATE_TABLE\",\"rows\":[";
  bool first = true;
  for (std::uint64_t h = kFirstH; h <= kLastH; ++h) {
    const Row row = build_row(h);
    if (!first) {
      stream << ',';
    }
    first = false;
    stream << "{\"H\":" << row.h << ",\"b\":" << row.bits
           << ",\"balance_pass\":" << (row.balance_pass ? "true" : "false")
           << ",\"max_lane_weight\":" << row.maximum
           << ",\"min_lane_weight\":" << row.minimum
           << ",\"oeis_gate_pass\":" << (row.oeis_gate_pass ? "true" : "false")
           << ",\"specialization_count\":" << row.specialization_count << '}';
  }
  stream << "],\"schema_version\":1}\n";
  stream.flush();
  if (!stream) {
    throw std::runtime_error("candidate-table write failed");
  }
  stream.close();
  std::filesystem::rename(temporary, output);
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 3 || std::string(argv[1]) != "--output") {
      throw std::runtime_error("usage: q5_candidate_table --output PATH");
    }
    const std::filesystem::path output =
        std::filesystem::absolute(std::filesystem::path(argv[2]));
    if (output.parent_path().empty() ||
        !std::filesystem::is_directory(output.parent_path())) {
      throw std::runtime_error("output parent is not a directory");
    }
    write_table(output);
    return 0;
  } catch (const std::exception& exc) {
    std::cerr << "q5_candidate_table: " << exc.what() << '\n';
    return 2;
  }
}

