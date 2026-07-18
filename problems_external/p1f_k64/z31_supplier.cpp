#include <algorithm>
#include <array>
#include <bit>
#include <charconv>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <unordered_set>
#include <utility>
#include <vector>

namespace {

constexpr int kModulus = 31;
constexpr int kDifferences = 15;
constexpr std::uint8_t kNoVertex = std::numeric_limits<std::uint8_t>::max();

using Mate = std::array<std::uint8_t, static_cast<std::size_t>(kModulus)>;
using Endpoints = std::array<std::uint8_t, 2U * static_cast<std::size_t>(kDifferences)>;
using Record = std::array<std::uint8_t, 4U * static_cast<std::size_t>(kDifferences)>;
using PairKey = Record;

struct Starter {
    Mate mate{};
    Endpoints by_difference{};
};

int cyclic_abs_difference(const int x, const int y, const int modulus) {
    const int raw = std::abs(x - y);
    return std::min(raw, modulus - raw);
}

int mod31(const int x) {
    int result = x % kModulus;
    if (result < 0) {
        result += kModulus;
    }
    return result;
}

int inverse31(const int x) {
    const int target = mod31(x);
    for (int candidate = 1; candidate < kModulus; ++candidate) {
        if ((target * candidate) % kModulus == 1) {
            return candidate;
        }
    }
    throw std::logic_error("zero has no inverse in Z_31");
}

class StarterGenerator {
  public:
    explicit StarterGenerator(const std::size_t target) : target_(target) {
        mate_.fill(kNoVertex);
        endpoints_.fill(kNoVertex);
        output_.reserve(target);
    }

    std::vector<Starter> run() {
        constexpr std::uint32_t all_vertices = 0x7fffffffU;
        constexpr std::uint32_t nonzero_vertices = all_vertices & ~1U;
        search(nonzero_vertices, 0U);
        if (output_.size() != target_) {
            throw std::runtime_error("starter DFS exhausted before requested pool size");
        }
        return std::move(output_);
    }

  private:
    void search(const std::uint32_t remaining, const std::uint32_t used_differences) {
        if (output_.size() >= target_) {
            return;
        }
        if (remaining == 0U) {
            Starter starter;
            starter.mate = mate_;
            starter.by_difference = endpoints_;
            output_.push_back(starter);
            return;
        }

        const int x = static_cast<int>(std::countr_zero(remaining));
        const std::uint32_t x_bit = 1U << static_cast<unsigned int>(x);
        const std::uint32_t without_x = remaining & ~x_bit;
        std::uint32_t candidates = without_x;
        while (candidates != 0U) {
            const int y = static_cast<int>(std::countr_zero(candidates));
            const std::uint32_t y_bit = 1U << static_cast<unsigned int>(y);
            candidates &= ~y_bit;
            const int difference = cyclic_abs_difference(x, y, kModulus);
            const std::uint32_t difference_bit =
                1U << static_cast<unsigned int>(difference);
            if ((used_differences & difference_bit) != 0U) {
                continue;
            }

            mate_[static_cast<std::size_t>(x)] = static_cast<std::uint8_t>(y);
            mate_[static_cast<std::size_t>(y)] = static_cast<std::uint8_t>(x);
            const std::size_t slot = 2U * static_cast<std::size_t>(difference - 1);
            endpoints_[slot] = static_cast<std::uint8_t>(x);
            endpoints_[slot + 1U] = static_cast<std::uint8_t>(y);
            search(without_x & ~y_bit, used_differences | difference_bit);
            if (output_.size() >= target_) {
                return;
            }
            mate_[static_cast<std::size_t>(x)] = kNoVertex;
            mate_[static_cast<std::size_t>(y)] = kNoVertex;
            endpoints_[slot] = kNoVertex;
            endpoints_[slot + 1U] = kNoVertex;
        }
    }

    std::size_t target_;
    Mate mate_{};
    Endpoints endpoints_{};
    std::vector<Starter> output_;
};

void validate_starter(const Starter& starter) {
    std::uint32_t vertices = 1U;
    std::uint32_t differences = 0U;
    for (int difference = 1; difference <= kDifferences; ++difference) {
        const std::size_t slot = 2U * static_cast<std::size_t>(difference - 1);
        const int x = static_cast<int>(starter.by_difference[slot]);
        const int y = static_cast<int>(starter.by_difference[slot + 1U]);
        if (x <= 0 || x >= kModulus || y <= 0 || y >= kModulus || x == y) {
            throw std::runtime_error("starter endpoint is outside Z_31\\{0}");
        }
        const std::uint32_t x_bit = 1U << static_cast<unsigned int>(x);
        const std::uint32_t y_bit = 1U << static_cast<unsigned int>(y);
        if ((vertices & (x_bit | y_bit)) != 0U) {
            throw std::runtime_error("starter repeats a vertex");
        }
        vertices |= x_bit | y_bit;
        const int actual_difference = cyclic_abs_difference(x, y, kModulus);
        if (actual_difference != difference) {
            throw std::runtime_error("starter by-difference table is inconsistent");
        }
        differences |= 1U << static_cast<unsigned int>(difference);
        if (starter.mate[static_cast<std::size_t>(x)] != static_cast<std::uint8_t>(y) ||
            starter.mate[static_cast<std::size_t>(y)] != static_cast<std::uint8_t>(x)) {
            throw std::runtime_error("starter mate table is inconsistent");
        }
    }
    if (vertices != 0x7fffffffU || differences != 0x0000fffeU ||
        starter.mate[0] != kNoVertex) {
        throw std::runtime_error("starter exact-cover audit failed");
    }
}

using ShiftTable = std::array<Mate, static_cast<std::size_t>(kModulus)>;

ShiftTable all_shifts(const Starter& starter) {
    ShiftTable table{};
    for (int delta = 0; delta < kModulus; ++delta) {
        Mate shifted{};
        shifted.fill(kNoVertex);
        for (int vertex = 1; vertex < kModulus; ++vertex) {
            const int image = (vertex + delta) % kModulus;
            const int mate_image =
                (static_cast<int>(starter.mate[static_cast<std::size_t>(vertex)]) + delta) %
                kModulus;
            shifted[static_cast<std::size_t>(image)] =
                static_cast<std::uint8_t>(mate_image);
        }
        table[static_cast<std::size_t>(delta)] = shifted;
    }
    return table;
}

bool is_hamilton_path(const Mate& first, const Mate& second,
                      const int first_hole, const int second_hole,
                      std::array<std::uint8_t, static_cast<std::size_t>(kModulus)>* path) {
    std::uint32_t seen = 1U << static_cast<unsigned int>(first_hole);
    int vertex = first_hole;
    if (path != nullptr) {
        (*path)[0] = static_cast<std::uint8_t>(vertex);
    }
    for (int step = 0; step < kModulus - 1; ++step) {
        const Mate& matching = (step % 2 == 0) ? second : first;
        const std::uint8_t next_u8 = matching[static_cast<std::size_t>(vertex)];
        if (next_u8 == kNoVertex) {
            return false;
        }
        const int next = static_cast<int>(next_u8);
        const std::uint32_t next_bit = 1U << static_cast<unsigned int>(next);
        if ((seen & next_bit) != 0U) {
            return false;
        }
        seen |= next_bit;
        vertex = next;
        if (path != nullptr) {
            (*path)[static_cast<std::size_t>(step + 1)] = next_u8;
        }
    }
    return vertex == second_hole && seen == 0x7fffffffU;
}

using EncodedStarter = Endpoints;

EncodedStarter encode_affine(const Mate& mate, const int hole,
                             const int origin, const int multiplier) {
    std::array<std::pair<std::uint8_t, std::uint8_t>,
               static_cast<std::size_t>(kDifferences)>
        pairs{};
    std::size_t cursor = 0U;
    for (int x = 0; x < kModulus; ++x) {
        if (x == hole) {
            continue;
        }
        const int y = static_cast<int>(mate[static_cast<std::size_t>(x)]);
        if (x < y) {
            int image_x = mod31((x - origin) * multiplier);
            int image_y = mod31((y - origin) * multiplier);
            if (image_y < image_x) {
                std::swap(image_x, image_y);
            }
            pairs[cursor] = {static_cast<std::uint8_t>(image_x),
                             static_cast<std::uint8_t>(image_y)};
            ++cursor;
        }
    }
    if (cursor != static_cast<std::size_t>(kDifferences)) {
        throw std::logic_error("affine encoder received a malformed starter");
    }
    std::sort(pairs.begin(), pairs.end());
    EncodedStarter encoded{};
    for (std::size_t index = 0U; index < pairs.size(); ++index) {
        encoded[2U * index] = pairs[index].first;
        encoded[2U * index + 1U] = pairs[index].second;
    }
    return encoded;
}

EncodedStarter canonical_starter(const Mate& mate, const int hole) {
    EncodedStarter best{};
    best.fill(kNoVertex);
    for (int multiplier = 1; multiplier < kModulus; ++multiplier) {
        const EncodedStarter candidate = encode_affine(mate, hole, hole, multiplier);
        if (candidate < best) {
            best = candidate;
        }
    }
    return best;
}

PairKey concatenate(const EncodedStarter& first, const EncodedStarter& second) {
    PairKey result{};
    std::copy(first.begin(), first.end(), result.begin());
    std::copy(second.begin(), second.end(),
              result.begin() + static_cast<std::ptrdiff_t>(first.size()));
    return result;
}

PairKey canonical_pair(const Mate& first, const Mate& second,
                       const int first_hole, const int second_hole) {
    const int forward_multiplier = inverse31(second_hole - first_hole);
    const PairKey forward = concatenate(
        encode_affine(first, first_hole, first_hole, forward_multiplier),
        encode_affine(second, second_hole, first_hole, forward_multiplier));

    const int reverse_multiplier = inverse31(first_hole - second_hole);
    const PairKey reverse = concatenate(
        encode_affine(second, second_hole, second_hole, reverse_multiplier),
        encode_affine(first, first_hole, second_hole, reverse_multiplier));
    return std::min(forward, reverse);
}

struct PairKeyHash {
    std::size_t operator()(const PairKey& key) const noexcept {
        std::uint64_t hash = 1469598103934665603ULL;
        for (const std::uint8_t byte : key) {
            hash ^= static_cast<std::uint64_t>(byte);
            hash *= 1099511628211ULL;
        }
        return static_cast<std::size_t>(hash);
    }
};

Record make_record(const Starter& first, const Starter& second, const int delta) {
    Record record{};
    std::copy(first.by_difference.begin(), first.by_difference.end(), record.begin());
    const std::size_t offset = first.by_difference.size();
    for (std::size_t index = 0U; index < second.by_difference.size(); ++index) {
        record[offset + index] = static_cast<std::uint8_t>(
            (static_cast<int>(second.by_difference[index]) + delta) % kModulus);
    }
    return record;
}

std::uint64_t record_checksum(const Record& record) {
    std::uint64_t hash = 1469598103934665603ULL;
    for (const std::uint8_t byte : record) {
        hash ^= static_cast<std::uint64_t>(byte);
        hash *= 1099511628211ULL;
    }
    return hash;
}

std::vector<std::pair<int, int>> pike_s1() {
    return {{0, 1},   {7, 11},  {12, 17}, {20, 26}, {16, 25}, {8, 18},
            {10, 22}, {2, 4},   {3, 6},   {14, 21}, {15, 23}, {13, 24},
            {5, 19}};
}

std::vector<std::pair<int, int>> pike_s2() {
    return {{1, 2},   {6, 10},  {16, 21}, {12, 18}, {7, 25},  {5, 15},
            {8, 23},  {24, 26}, {19, 22}, {4, 11},  {9, 17},  {3, 14},
            {0, 13}};
}

std::vector<int> generic_mate(const int modulus, const int expected_hole,
                              const std::vector<std::pair<int, int>>& pairs) {
    std::vector<int> mate(static_cast<std::size_t>(modulus), -1);
    std::vector<bool> differences(static_cast<std::size_t>((modulus + 1) / 2), false);
    for (const auto& [x, y] : pairs) {
        if (x < 0 || x >= modulus || y < 0 || y >= modulus || x == y ||
            mate[static_cast<std::size_t>(x)] != -1 ||
            mate[static_cast<std::size_t>(y)] != -1) {
            throw std::runtime_error("generic starter has malformed endpoints");
        }
        mate[static_cast<std::size_t>(x)] = y;
        mate[static_cast<std::size_t>(y)] = x;
        const int difference = cyclic_abs_difference(x, y, modulus);
        if (differences[static_cast<std::size_t>(difference)]) {
            throw std::runtime_error("generic starter repeats a difference");
        }
        differences[static_cast<std::size_t>(difference)] = true;
    }
    for (int vertex = 0; vertex < modulus; ++vertex) {
        if ((mate[static_cast<std::size_t>(vertex)] == -1) != (vertex == expected_hole)) {
            throw std::runtime_error("generic starter has the wrong hole");
        }
    }
    for (int difference = 1; difference <= (modulus - 1) / 2; ++difference) {
        if (!differences[static_cast<std::size_t>(difference)]) {
            throw std::runtime_error("generic starter misses a difference");
        }
    }
    return mate;
}

void test_pike_z27() {
    constexpr int modulus = 27;
    constexpr int first_hole = 9;
    constexpr int second_hole = 20;
    const std::vector<int> first = generic_mate(modulus, first_hole, pike_s1());
    const std::vector<int> second = generic_mate(modulus, second_hole, pike_s2());
    std::vector<bool> seen(static_cast<std::size_t>(modulus), false);
    int vertex = first_hole;
    seen[static_cast<std::size_t>(vertex)] = true;
    for (int step = 0; step < modulus - 1; ++step) {
        const std::vector<int>& matching = (step % 2 == 0) ? second : first;
        vertex = matching[static_cast<std::size_t>(vertex)];
        if (vertex < 0 || seen[static_cast<std::size_t>(vertex)]) {
            throw std::runtime_error("Pike Z27 pair is not an alternating Hamilton path");
        }
        seen[static_cast<std::size_t>(vertex)] = true;
    }
    if (vertex != second_hole ||
        !std::all_of(seen.begin(), seen.end(), [](const bool value) { return value; })) {
        throw std::runtime_error("Pike Z27 path has the wrong terminal state");
    }
}

Mate affine_image(const Mate& mate, const int hole, const int offset,
                  const int multiplier) {
    Mate image{};
    image.fill(kNoVertex);
    for (int x = 0; x < kModulus; ++x) {
        if (x == hole) {
            continue;
        }
        const int y = static_cast<int>(mate[static_cast<std::size_t>(x)]);
        const int image_x = mod31(multiplier * x + offset);
        const int image_y = mod31(multiplier * y + offset);
        image[static_cast<std::size_t>(image_x)] = static_cast<std::uint8_t>(image_y);
    }
    return image;
}

void self_test() {
    test_pike_z27();
    std::vector<Starter> pool = StarterGenerator(128U).run();
    for (const Starter& starter : pool) {
        validate_starter(starter);
    }
    const EncodedStarter canonical = canonical_starter(pool.front().mate, 0);
    for (int multiplier = 1; multiplier < kModulus; ++multiplier) {
        const Mate image = affine_image(pool.front().mate, 0, 0, multiplier);
        if (canonical_starter(image, 0) != canonical) {
            throw std::runtime_error("starter canonicalization is not multiplier invariant");
        }
    }

    std::optional<std::tuple<std::size_t, std::size_t, int, PairKey>> witness;
    for (std::size_t i = 0U; i < pool.size() && !witness.has_value(); ++i) {
        for (std::size_t j = i + 1U; j < pool.size() && !witness.has_value(); ++j) {
            const ShiftTable shifts = all_shifts(pool[j]);
            for (int delta = 1; delta < kModulus; ++delta) {
                if (is_hamilton_path(pool[i].mate, shifts[static_cast<std::size_t>(delta)],
                                     0, delta, nullptr)) {
                    witness = std::make_tuple(
                        i, j, delta,
                        canonical_pair(pool[i].mate,
                                       shifts[static_cast<std::size_t>(delta)], 0, delta));
                    break;
                }
            }
        }
    }
    if (!witness.has_value()) {
        throw std::runtime_error("self-test pool contains no compatible pair");
    }
    const auto [i, j, delta, expected_key] = *witness;
    const ShiftTable shifts = all_shifts(pool[j]);
    const Mate second = shifts[static_cast<std::size_t>(delta)];
    for (int multiplier = 1; multiplier < kModulus; ++multiplier) {
        for (int offset = 0; offset < kModulus; ++offset) {
            const Mate first_image = affine_image(pool[i].mate, 0, offset, multiplier);
            const Mate second_image = affine_image(second, delta, offset, multiplier);
            const int first_hole = offset;
            const int second_hole = mod31(multiplier * delta + offset);
            if (canonical_pair(first_image, second_image, first_hole, second_hole) !=
                    expected_key ||
                canonical_pair(second_image, first_image, second_hole, first_hole) !=
                    expected_key) {
                throw std::runtime_error("pair canonicalization is not AGL/swap invariant");
            }
        }
    }
    std::cout << "self_test=PASS pike_z27=PASS z31_starters=" << pool.size()
              << " agl_pair_images=1860\n";
}

struct WarmupResult {
    std::uint64_t checked = 0U;
    std::uint64_t compatible = 0U;
    std::uint64_t canonical_duplicates = 0U;
    std::vector<Record> records;
    double seconds = 0.0;
};

WarmupResult make_warmup(const std::vector<Starter>& pool,
                         const std::vector<ShiftTable>& shifts,
                         const std::size_t requested) {
    WarmupResult result;
    result.records.reserve(requested);
    std::unordered_set<PairKey, PairKeyHash> seen;
    seen.reserve(requested * 2U + 1U);
    const auto start = std::chrono::steady_clock::now();
    for (std::size_t i = 0U; i < pool.size(); ++i) {
        for (std::size_t j = i + 1U; j < pool.size(); ++j) {
            for (int delta = 1; delta < kModulus; ++delta) {
                ++result.checked;
                const Mate& second =
                    shifts[j][static_cast<std::size_t>(delta)];
                if (!is_hamilton_path(pool[i].mate, second, 0, delta, nullptr)) {
                    continue;
                }
                ++result.compatible;
                const PairKey key = canonical_pair(pool[i].mate, second, 0, delta);
                const auto [unused, inserted] = seen.insert(key);
                static_cast<void>(unused);
                if (!inserted) {
                    ++result.canonical_duplicates;
                    continue;
                }
                result.records.push_back(make_record(pool[i], pool[j], delta));
                if (result.records.size() == requested) {
                    const auto stop = std::chrono::steady_clock::now();
                    result.seconds = std::chrono::duration<double>(stop - start).count();
                    return result;
                }
            }
        }
    }
    const auto stop = std::chrono::steady_clock::now();
    result.seconds = std::chrono::duration<double>(stop - start).count();
    throw std::runtime_error("pool exhausted before distinct warm-up target; found " +
                             std::to_string(result.records.size()));
}

void write_records(const std::string& path, const std::vector<Record>& records) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) {
        throw std::runtime_error("cannot open warm-up output: " + path);
    }
    output << records.size() << '\n';
    for (const Record& record : records) {
        for (std::size_t index = 0U; index < record.size(); ++index) {
            if (index != 0U) {
                output << ' ';
            }
            output << static_cast<unsigned int>(record[index]);
        }
        output << '\n';
    }
    if (!output) {
        throw std::runtime_error("failed while writing warm-up output: " + path);
    }
}

struct alignas(64) WorkerResult {
    std::uint64_t checked = 0U;
    std::uint64_t compatible = 0U;
    std::uint64_t checksum = 0U;
};

struct BenchmarkResult {
    std::uint64_t checked = 0U;
    std::uint64_t compatible = 0U;
    std::uint64_t checksum = 0U;
    double seconds = 0.0;
    bool exhausted = false;
};

BenchmarkResult benchmark_supplier(const std::vector<Starter>& pool,
                                   const std::vector<ShiftTable>& shifts,
                                   const unsigned int thread_count,
                                   const double requested_seconds) {
    std::vector<WorkerResult> results(static_cast<std::size_t>(thread_count));
    std::vector<std::thread> workers;
    workers.reserve(static_cast<std::size_t>(thread_count));
    const auto start = std::chrono::steady_clock::now();
    const auto deadline = start + std::chrono::duration<double>(requested_seconds);
    for (unsigned int thread_id = 0U; thread_id < thread_count; ++thread_id) {
        workers.emplace_back([&, thread_id]() {
            WorkerResult local;
            bool stop = false;
            for (std::size_t i = static_cast<std::size_t>(thread_id);
                 i + 1U < pool.size() && !stop;
                 i += static_cast<std::size_t>(thread_count)) {
                for (std::size_t j = i + 1U; j < pool.size() && !stop; ++j) {
                    for (int delta = 1; delta < kModulus; ++delta) {
                        ++local.checked;
                        if (is_hamilton_path(
                                pool[i].mate,
                                shifts[j][static_cast<std::size_t>(delta)], 0, delta,
                                nullptr)) {
                            ++local.compatible;
                            const Record record = make_record(pool[i], pool[j], delta);
                            local.checksum ^= record_checksum(record) + local.compatible;
                        }
                        if ((local.checked & 0x3fffU) == 0U &&
                            std::chrono::steady_clock::now() >= deadline) {
                            stop = true;
                            break;
                        }
                    }
                }
            }
            results[static_cast<std::size_t>(thread_id)] = local;
        });
    }
    for (std::thread& worker : workers) {
        worker.join();
    }
    const auto stop = std::chrono::steady_clock::now();
    BenchmarkResult total;
    total.seconds = std::chrono::duration<double>(stop - start).count();
    for (const WorkerResult& result : results) {
        total.checked += result.checked;
        total.compatible += result.compatible;
        total.checksum ^= result.checksum;
    }
    const std::uint64_t candidate_total =
        static_cast<std::uint64_t>(pool.size()) *
        static_cast<std::uint64_t>(pool.size() - 1U) / 2U *
        static_cast<std::uint64_t>(kModulus - 1);
    total.exhausted = total.checked == candidate_total;
    return total;
}

template <typename Integer>
Integer parse_integer(const std::string_view text, const std::string_view name) {
    Integer value{};
    const char* const begin = text.data();
    const char* const end = text.data() + text.size();
    const auto [position, error] = std::from_chars(begin, end, value);
    if (error != std::errc{} || position != end) {
        throw std::invalid_argument("invalid " + std::string(name) + ": " +
                                    std::string(text));
    }
    return value;
}

double parse_double(const std::string_view text, const std::string_view name) {
    std::string owned(text);
    char* end = nullptr;
    const double value = std::strtod(owned.c_str(), &end);
    if (end == owned.c_str() || end != owned.c_str() + owned.size() || value <= 0.0) {
        throw std::invalid_argument("invalid " + std::string(name) + ": " + owned);
    }
    return value;
}

struct Options {
    std::size_t pool_size = 4096U;
    std::size_t count = 0U;
    std::optional<std::string> emit_path;
    std::optional<double> benchmark_seconds;
    unsigned int threads = 1U;
    bool run_self_test = false;
};

Options parse_options(const int argc, char** argv) {
    Options options;
    for (int index = 1; index < argc; ++index) {
        const std::string_view argument(argv[index]);
        const auto require_value = [&]() -> std::string_view {
            if (index + 1 >= argc) {
                throw std::invalid_argument("missing value after " + std::string(argument));
            }
            ++index;
            return std::string_view(argv[index]);
        };
        if (argument == "--pool") {
            options.pool_size = parse_integer<std::size_t>(require_value(), "pool size");
        } else if (argument == "--count") {
            options.count = parse_integer<std::size_t>(require_value(), "record count");
        } else if (argument == "--emit") {
            options.emit_path = std::string(require_value());
        } else if (argument == "--benchmark-seconds") {
            options.benchmark_seconds =
                parse_double(require_value(), "benchmark seconds");
        } else if (argument == "--threads") {
            options.threads = parse_integer<unsigned int>(require_value(), "thread count");
        } else if (argument == "--self-test") {
            options.run_self_test = true;
        } else {
            throw std::invalid_argument("unknown option: " + std::string(argument));
        }
    }
    if (options.pool_size < 2U) {
        throw std::invalid_argument("pool size must be at least 2");
    }
    if (options.threads == 0U || options.threads > 64U) {
        throw std::invalid_argument("thread count must be in 1..64");
    }
    if (options.emit_path.has_value() != (options.count != 0U)) {
        throw std::invalid_argument("--emit and positive --count must be supplied together");
    }
    return options;
}

}  // namespace

int main(const int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        if (options.run_self_test) {
            self_test();
        }
        if (!options.emit_path.has_value() && !options.benchmark_seconds.has_value()) {
            if (!options.run_self_test) {
                throw std::invalid_argument(
                    "choose --self-test, --emit/--count, or --benchmark-seconds");
            }
            return 0;
        }

        const auto generation_start = std::chrono::steady_clock::now();
        std::vector<Starter> pool = StarterGenerator(options.pool_size).run();
        const auto generation_stop = std::chrono::steady_clock::now();
        for (const Starter& starter : pool) {
            validate_starter(starter);
        }
        const double generation_seconds =
            std::chrono::duration<double>(generation_stop - generation_start).count();
        std::cout << std::fixed << std::setprecision(3)
                  << "starter_pool=" << pool.size()
                  << " generation_seconds=" << generation_seconds
                  << " generation_rate="
                  << static_cast<double>(pool.size()) / generation_seconds << " starters/s\n";

        std::vector<ShiftTable> shifts;
        shifts.reserve(pool.size());
        for (const Starter& starter : pool) {
            shifts.push_back(all_shifts(starter));
        }

        if (options.emit_path.has_value()) {
            const WarmupResult warmup =
                make_warmup(pool, shifts, options.count);
            write_records(*options.emit_path, warmup.records);
            const double checked_rate =
                static_cast<double>(warmup.checked) / warmup.seconds;
            const double output_rate =
                static_cast<double>(warmup.records.size()) / warmup.seconds;
            std::uint64_t checksum = 0U;
            for (const Record& record : warmup.records) {
                checksum ^= record_checksum(record);
            }
            std::cout << "warmup_records=" << warmup.records.size()
                      << " checked=" << warmup.checked
                      << " compatible=" << warmup.compatible
                      << " canonical_duplicates=" << warmup.canonical_duplicates
                      << " seconds=" << warmup.seconds
                      << " checked_rate=" << checked_rate
                      << " distinct_rate=" << output_rate
                      << " checksum=" << checksum << '\n';
        }

        if (options.benchmark_seconds.has_value()) {
            const BenchmarkResult result = benchmark_supplier(
                pool, shifts, options.threads, *options.benchmark_seconds);
            const double candidate_rate =
                static_cast<double>(result.checked) / result.seconds;
            const double compatible_rate =
                static_cast<double>(result.compatible) / result.seconds;
            const long double assignment_rate =
                static_cast<long double>(compatible_rate) * 32768.0L;
            std::cout << "benchmark_threads=" << options.threads
                      << " seconds=" << result.seconds
                      << " candidates=" << result.checked
                      << " compatible_records=" << result.compatible
                      << " candidate_rate=" << candidate_rate
                      << " compatible_rate=" << compatible_rate
                      << " implied_assignment_rate="
                      << static_cast<double>(assignment_rate)
                      << " exhausted=" << (result.exhausted ? "yes" : "no")
                      << " checksum=" << result.checksum
                      << " supplier_threshold="
                      << (compatible_rate >= 300000.0 ? "PASS" : "FAIL") << '\n';
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }
}
