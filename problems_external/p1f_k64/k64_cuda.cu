#include <cuda_runtime.h>

#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr int kStarterModulus = 31;
constexpr int kDifferences = 15;
constexpr int kResidueModulus = 62;
constexpr int kOrder = 64;
constexpr int kMasks = 1 << kDifferences;
constexpr int kThreads = 256;
constexpr int kLowBits = kThreads == 128 ? 7 : kThreads == 256 ? 8 : 9;
constexpr int kHighAssignments = 1 << (kDifferences - kLowBits);
constexpr int kSampleCount = 4;
__device__ __constant__ std::uint8_t kFailFastOrder[32] = {
    29, 30, 19, 12, 2, 21, 10, 23, 8, 24, 14, 15, 7, 1, 9, 26,
    4, 22, 25, 5, 13, 27, 16, 3, 11, 17, 20, 6, 28, 18, 0, 31};
__device__ __constant__ std::uint8_t kOrbitSeed[32] = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 63, 0, 0, 0, 50, 0,
    0, 0, 0, 0, 0, 63, 0, 0, 0, 0, 0, 0, 0, 2, 3, 0};
__host__ __device__ constexpr std::uint32_t sample_mask(const int index) {
    return index == 0 ? 0U
         : index == 1 ? 0x7fffU
         : index == 2 ? 0x2aaaU
                      : 0x5555U;
}

struct Edge {
    int x{};
    int y{};
};

struct RawRecord {
    std::array<Edge, kDifferences> starter1{};
    std::array<Edge, kDifferences> starter2{};
};

// meta byte: bits 0..3 = difference-1, bit 4 = lift-toggle constant,
// bit 5 = source is starter 1.  The mask convention is exactly that of
// gate_reference.py: bit d-1 says that S1's difference-d edge is High.
struct alignas(16) DeviceRecord {
    std::uint32_t pair_id{};
    std::uint32_t base_lift_mask{};
    std::uint32_t lift_basis[kDifferences]{};
    std::uint8_t path[kStarterModulus]{};
    std::uint8_t position[kStarterModulus]{};
    std::uint8_t meta[kStarterModulus - 1]{};
};

static_assert(sizeof(DeviceRecord) == 160, "device record layout changed");

struct DeviceTotals {
    unsigned long long candidates{};
    unsigned long long checksum_xor{};
    unsigned long long checksum_sum{};
};

struct Candidate {
    std::uint32_t pair_id{};
    std::uint32_t mask{};
    std::uint32_t lift_mask{};
    std::uint32_t pass_mask{};
};

struct Sample {
    std::uint32_t mask{};
    std::uint32_t lift_mask{};
    std::uint32_t pass_mask{};
    std::uint32_t reserved{};
};

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void cuda_check(const cudaError_t status, const char* operation) {
    if (status != cudaSuccess) {
        fail(std::string(operation) + ": " + cudaGetErrorString(status));
    }
}

__host__ __device__ constexpr int mod_positive(const int value,
                                               const int modulus) {
    const int reduced = value % modulus;
    return reduced < 0 ? reduced + modulus : reduced;
}

__host__ __device__ constexpr int canonical_difference(const int x,
                                                        const int y) {
    const int forward = mod_positive(y - x, kStarterModulus);
    return forward < kStarterModulus - forward
               ? forward
               : kStarterModulus - forward;
}

__host__ __device__ unsigned long long mix64(unsigned long long value) {
    value += 0x9e3779b97f4a7c15ULL;
    value = (value ^ (value >> 30U)) * 0xbf58476d1ce4e5b9ULL;
    value = (value ^ (value >> 27U)) * 0x94d049bb133111ebULL;
    return value ^ (value >> 31U);
}

struct AdjacencyEntry {
    int to{};
    int source{};
    int edge_id{};
};

int validate_starter(const std::array<Edge, kDifferences>& starter,
                     const char* label) {
    std::array<int, kStarterModulus> vertices{};
    std::array<int, kDifferences + 1> differences{};
    for (const Edge edge : starter) {
        if (edge.x < 0 || edge.x >= kStarterModulus || edge.y < 0 ||
            edge.y >= kStarterModulus || edge.x == edge.y) {
            fail(std::string(label) + ": invalid endpoint");
        }
        ++vertices[static_cast<std::size_t>(edge.x)];
        ++vertices[static_cast<std::size_t>(edge.y)];
        const int difference = canonical_difference(edge.x, edge.y);
        if (difference < 1 || difference > kDifferences) {
            fail(std::string(label) + ": invalid difference");
        }
        ++differences[static_cast<std::size_t>(difference)];
    }
    int missing = -1;
    for (int vertex = 0; vertex < kStarterModulus; ++vertex) {
        const int count = vertices[static_cast<std::size_t>(vertex)];
        if (count == 0) {
            if (missing != -1) {
                fail(std::string(label) + ": more than one missing vertex");
            }
            missing = vertex;
        } else if (count != 1) {
            fail(std::string(label) + ": repeated vertex");
        }
    }
    for (int difference = 1; difference <= kDifferences; ++difference) {
        if (differences[static_cast<std::size_t>(difference)] != 1) {
            fail(std::string(label) + ": differences are not 1..15");
        }
    }
    return missing;
}

DeviceRecord encode_record(const RawRecord& raw, const std::uint32_t pair_id) {
    const int missing1 = validate_starter(raw.starter1, "S1");
    const int missing2 = validate_starter(raw.starter2, "S2");
    if (missing1 == missing2) {
        fail("starter holes coincide");
    }

    std::array<std::array<AdjacencyEntry, 2>, kStarterModulus> adjacency{};
    std::array<int, kStarterModulus> degree{};
    std::array<std::array<int, kStarterModulus>, kStarterModulus> edge_seen{};
    auto add_starter = [&](const std::array<Edge, kDifferences>& starter,
                           const int source, const int edge_offset) {
        for (int index = 0; index < kDifferences; ++index) {
            const Edge edge = starter[static_cast<std::size_t>(index)];
            const int lo = edge.x < edge.y ? edge.x : edge.y;
            const int hi = edge.x < edge.y ? edge.y : edge.x;
            if (edge_seen[static_cast<std::size_t>(lo)]
                         [static_cast<std::size_t>(hi)] != 0) {
                fail("starters share an unordered edge");
            }
            edge_seen[static_cast<std::size_t>(lo)]
                     [static_cast<std::size_t>(hi)] = 1;
            const int edge_id = edge_offset + index;
            if (degree[static_cast<std::size_t>(edge.x)] >= 2 ||
                degree[static_cast<std::size_t>(edge.y)] >= 2) {
                fail("starter union degree exceeds two");
            }
            adjacency[static_cast<std::size_t>(edge.x)]
                     [static_cast<std::size_t>(degree[static_cast<std::size_t>(edge.x)]++)] =
                AdjacencyEntry{edge.y, source, edge_id};
            adjacency[static_cast<std::size_t>(edge.y)]
                     [static_cast<std::size_t>(degree[static_cast<std::size_t>(edge.y)]++)] =
                AdjacencyEntry{edge.x, source, edge_id};
        }
    };
    add_starter(raw.starter1, 1, 0);
    add_starter(raw.starter2, 2, kDifferences);

    for (int vertex = 0; vertex < kStarterModulus; ++vertex) {
        const int expected = (vertex == missing1 || vertex == missing2) ? 1 : 2;
        if (degree[static_cast<std::size_t>(vertex)] != expected) {
            fail("starter union does not have Hamilton-path degrees");
        }
    }

    DeviceRecord result{};
    result.pair_id = pair_id;
    std::array<bool, 2 * kDifferences> used{};
    int current = missing1;
    result.path[0] = static_cast<std::uint8_t>(current);
    result.position[static_cast<std::size_t>(current)] = 0U;
    for (int step = 0; step < kStarterModulus - 1; ++step) {
        const auto& entries = adjacency[static_cast<std::size_t>(current)];
        const int count = degree[static_cast<std::size_t>(current)];
        int selected = -1;
        for (int lane = 0; lane < count; ++lane) {
            const int edge_id = entries[static_cast<std::size_t>(lane)].edge_id;
            if (!used[static_cast<std::size_t>(edge_id)]) {
                if (selected != -1) {
                    fail("starter union closes a proper cycle");
                }
                selected = lane;
            }
        }
        if (selected == -1) {
            fail("starter union path ended early");
        }
        const AdjacencyEntry edge = entries[static_cast<std::size_t>(selected)];
        used[static_cast<std::size_t>(edge.edge_id)] = true;
        const int next = edge.to;
        const int difference = canonical_difference(current, next);

        const int target_minus = mod_positive(current - difference,
                                               kResidueModulus);
        const int target_plus = (current + difference) % kResidueModulus;
        int y_hat = -1;
        for (const int lift : {next, next + kStarterModulus}) {
            if (lift == target_minus || lift == target_plus) {
                if (y_hat != -1) {
                    fail("non-unique signed-difference lift");
                }
                y_hat = lift;
            }
        }
        if (y_hat == -1) {
            fail("signed-difference lift not found");
        }
        const int flip = y_hat >= kStarterModulus ? 1 : 0;
        const int toggle_constant = flip ^ (edge.source == 1 ? 1 : 0);
        result.meta[static_cast<std::size_t>(step)] =
            static_cast<std::uint8_t>((difference - 1) |
                                      (toggle_constant << 4) |
                                      ((edge.source == 1 ? 1 : 0) << 5));
        current = next;
        result.path[static_cast<std::size_t>(step + 1)] =
            static_cast<std::uint8_t>(current);
        result.position[static_cast<std::size_t>(current)] =
            static_cast<std::uint8_t>(step + 1);
    }
    if (current != missing2) {
        fail("starter union is not one spanning path");
    }
    for (const bool value : used) {
        if (!value) {
            fail("starter union left an edge unused");
        }
    }
    const auto calculate_lift_mask = [&](const std::uint32_t assignment) {
        unsigned lift = 1U;
        std::uint32_t mask = 1U;
        for (int edge = 0; edge < kStarterModulus - 1; ++edge) {
            const unsigned meta = result.meta[edge];
            lift ^= (assignment >> (meta & 15U)) & 1U;
            lift ^= (meta >> 4U) & 1U;
            mask |= lift << static_cast<unsigned>(edge + 1);
        }
        return mask;
    };
    result.base_lift_mask = calculate_lift_mask(0U);
    for (int bit = 0; bit < kDifferences; ++bit) {
        result.lift_basis[bit] =
            calculate_lift_mask(1U << static_cast<unsigned>(bit)) ^
            result.base_lift_mask;
    }
    return result;
}

__device__ __forceinline__ std::uint32_t lift_mask_for_low_byte(
    const DeviceRecord& record, const std::uint32_t low_byte) {
    std::uint32_t lift_mask = record.base_lift_mask;
#pragma unroll
    for (int bit = 0; bit < kLowBits; ++bit) {
        if ((low_byte & (1U << static_cast<unsigned>(bit))) != 0U) {
            lift_mask ^= record.lift_basis[bit];
        }
    }
    return lift_mask;
}

__device__ __forceinline__ int partner_zero(const DeviceRecord& record,
                                             const std::uint32_t lift_mask,
                                             const int vertex) {
    if (vertex == kResidueModulus) {
        return static_cast<int>(record.path[0]);
    }
    if (vertex == kResidueModulus + 1) {
        const int lift = static_cast<int>((lift_mask >> 30U) & 1U);
        return static_cast<int>(record.path[30]) + kStarterModulus * lift;
    }
    const int lift = vertex >= kStarterModulus ? 1 : 0;
    const int residue = vertex - kStarterModulus * lift;
    const int position = static_cast<int>(record.position[residue]);
    const int path_lift = static_cast<int>((lift_mask >> position) & 1U);
    if (position == 0 && lift != path_lift) {
        return kResidueModulus;
    }
    if (position == 30 && lift == path_lift) {
        return kResidueModulus + 1;
    }
    if (lift == path_lift) {
        const int next_lift =
            1 - static_cast<int>((lift_mask >> (position + 1)) & 1U);
        return static_cast<int>(record.path[position + 1]) +
               kStarterModulus * next_lift;
    }
    const int previous_lift =
        static_cast<int>((lift_mask >> (position - 1)) & 1U);
    return static_cast<int>(record.path[position - 1]) +
           kStarterModulus * previous_lift;
}

__device__ __forceinline__ int partner_shift(const DeviceRecord& record,
                                              const std::uint32_t lift_mask,
                                              const int vertex,
                                              const int shift) {
    if (vertex >= kResidueModulus) {
        const int sum = partner_zero(record, lift_mask, vertex) + shift;
        return sum >= kResidueModulus ? sum - kResidueModulus : sum;
    }
    int unshifted = vertex - shift;
    if (unshifted < 0) {
        unshifted += kResidueModulus;
    }
    const int partner = partner_zero(record, lift_mask, unshifted);
    if (partner >= kResidueModulus) {
        return partner;
    }
    const int sum = partner + shift;
    return sum >= kResidueModulus ? sum - kResidueModulus : sum;
}

__device__ __forceinline__ int partner_fixed(const int vertex) {
    if (vertex == kResidueModulus) {
        return kResidueModulus + 1;
    }
    if (vertex == kResidueModulus + 1) {
        return kResidueModulus;
    }
    return vertex < kStarterModulus ? vertex + kStarterModulus
                                    : vertex - kStarterModulus;
}

__device__ __forceinline__ bool orbit_is_hamilton(
    const DeviceRecord& record, const std::uint32_t lift_mask,
    const int orbit) {
    int vertex = static_cast<int>(kOrbitSeed[orbit]);
    const int start = vertex;
    if (orbit == 0) {
#pragma unroll 32
        for (int round = 0; round < kOrder / 2; ++round) {
            vertex = partner_zero(record, lift_mask, vertex);
            vertex = partner_fixed(vertex);
            if (vertex == start) {
                return round == kOrder / 2 - 1;
            }
        }
        return false;
    }
#pragma unroll 32
    for (int round = 0; round < kOrder / 2; ++round) {
        vertex = partner_zero(record, lift_mask, vertex);
        vertex = partner_shift(record, lift_mask, vertex, orbit);
        if (vertex == start) {
            return round == kOrder / 2 - 1;
        }
    }
    return false;
}

__device__ __forceinline__ std::uint32_t score_assignment(
    const DeviceRecord& record, const std::uint32_t lift_mask) {
    std::uint32_t pass_mask = 0U;
#pragma unroll
    for (int orbit = 0; orbit <= kStarterModulus; ++orbit) {
        if (orbit_is_hamilton(record, lift_mask, orbit)) {
            pass_mask |= 1U << static_cast<unsigned>(orbit);
        }
    }
    return pass_mask;
}

__device__ __forceinline__ bool is_candidate_fail_fast(
    const DeviceRecord& record, const std::uint32_t lift_mask) {
    for (int rank = 0; rank < 32; ++rank) {
        const int orbit = static_cast<int>(kFailFastOrder[rank]);
        if (!orbit_is_hamilton(record, lift_mask, orbit)) {
            return false;
        }
    }
    return true;
}

__global__ void evaluate_kernel(const DeviceRecord* records,
                                const std::uint32_t record_count,
                                const std::uint32_t run_nonce,
                                DeviceTotals* totals, Candidate* candidates,
                                const unsigned long long candidate_capacity,
                                Sample* samples) {
    const std::uint32_t record_index = blockIdx.x;
    if (record_index >= record_count) {
        return;
    }
    __shared__ DeviceRecord record;
    if (threadIdx.x == 0) {
        record = records[record_index];
    }
    __syncthreads();

    const std::uint32_t low_byte = threadIdx.x;
    std::uint32_t lift_mask = lift_mask_for_low_byte(record, low_byte);
    for (std::uint32_t high_index = 0; high_index < kHighAssignments;
         ++high_index) {
        const std::uint32_t high_gray = high_index ^ (high_index >> 1U);
        const std::uint32_t assignment =
            low_byte | (high_gray << static_cast<unsigned>(kLowBits));
        const bool candidate = is_candidate_fail_fast(record, lift_mask);
        if (candidate) {
            const unsigned long long slot = atomicAdd(&totals->candidates, 1ULL);
            if (slot < candidate_capacity) {
                candidates[slot] = Candidate{record.pair_id, assignment,
                                             lift_mask, 0xffffffffU};
            }
        }
        if (record_index == 0U && run_nonce == 0U) {
#pragma unroll
            for (int sample = 0; sample < kSampleCount; ++sample) {
                if (assignment == sample_mask(sample)) {
                    const std::uint32_t pass_mask =
                        candidate ? 0xffffffffU
                                  : score_assignment(record, lift_mask);
                    samples[sample] = Sample{assignment, lift_mask,
                                             pass_mask, 0U};
                }
            }
        }
        if (high_index + 1U < kHighAssignments) {
            const int changed_high_bit = __ffs(static_cast<int>(high_index + 1U)) - 1;
            lift_mask ^= record.lift_basis[kLowBits + changed_high_bit];
        }
    }
}

std::uint32_t cpu_materialize(const DeviceRecord& record,
                              const std::uint32_t assignment,
                              std::array<int, kOrder>& partner) {
    partner.fill(-1);
    int a = static_cast<int>(record.path[0]) + kStarterModulus;
    std::uint32_t lift_mask = 1U;
    for (int edge = 0; edge < kStarterModulus - 1; ++edge) {
        const int x = a % kStarterModulus;
        const int y = static_cast<int>(record.path[edge + 1]);
        if (x != static_cast<int>(record.path[edge])) {
            fail("CPU merger path/lift mismatch");
        }
        const int difference = canonical_difference(x, y);
        const int target_minus = mod_positive(a - difference, kResidueModulus);
        const int target_plus = (a + difference) % kResidueModulus;
        int y_hat = -1;
        for (const int lift : {y, y + kStarterModulus}) {
            if (lift == target_minus || lift == target_plus) {
                y_hat = lift;
            }
        }
        if (y_hat == -1) {
            fail("CPU merger could not select y_hat");
        }
        const int other = y_hat == y ? y + kStarterModulus : y;
        const bool source1 = (record.meta[edge] & 32U) != 0U;
        const bool s1_high =
            (assignment & (1U << static_cast<unsigned>(difference - 1))) != 0U;
        const bool is_low = source1 ? !s1_high : s1_high;
        const int b = is_low ? y_hat : other;
        const int next_a = is_low ? other : y_hat;
        if (partner[static_cast<std::size_t>(a)] != -1 ||
            partner[static_cast<std::size_t>(b)] != -1) {
            fail("CPU merger repeated a lift");
        }
        partner[static_cast<std::size_t>(a)] = b;
        partner[static_cast<std::size_t>(b)] = a;
        a = next_a;
        const unsigned lift = a >= kStarterModulus ? 1U : 0U;
        lift_mask |= lift << static_cast<unsigned>(edge + 1);
    }
    const int first_hole = static_cast<int>(record.path[0]);
    partner[static_cast<std::size_t>(first_hole)] = kResidueModulus;
    partner[kResidueModulus] = first_hole;
    partner[static_cast<std::size_t>(a)] = kResidueModulus + 1;
    partner[kResidueModulus + 1] = a;
    for (const int value : partner) {
        if (value < 0 || value >= kOrder) {
            fail("CPU merger left an unmatched vertex");
        }
    }
    return lift_mask;
}

int cpu_shift_partner(const std::array<int, kOrder>& partner,
                      const int vertex, const int shift) {
    if (vertex >= kResidueModulus) {
        return (partner[static_cast<std::size_t>(vertex)] + shift) %
               kResidueModulus;
    }
    const int unshifted = mod_positive(vertex - shift, kResidueModulus);
    const int base = partner[static_cast<std::size_t>(unshifted)];
    return base < kResidueModulus ? (base + shift) % kResidueModulus : base;
}

std::uint32_t cpu_score(const DeviceRecord& record,
                        const std::uint32_t assignment,
                        std::uint32_t& lift_mask) {
    std::array<int, kOrder> partner{};
    lift_mask = cpu_materialize(record, assignment, partner);
    std::uint32_t pass_mask = 0U;
    for (int orbit = 0; orbit <= kStarterModulus; ++orbit) {
        int vertex = 0;
        bool hamilton = false;
        for (int step = 0; step < kOrder; ++step) {
            if ((step & 1) == 0) {
                vertex = partner[static_cast<std::size_t>(vertex)];
            } else if (orbit == 0) {
                if (vertex == kResidueModulus) {
                    vertex = kResidueModulus + 1;
                } else if (vertex == kResidueModulus + 1) {
                    vertex = kResidueModulus;
                } else {
                    vertex = (vertex + kStarterModulus) % kResidueModulus;
                }
            } else {
                vertex = cpu_shift_partner(partner, vertex, orbit);
            }
            if (vertex == 0) {
                hamilton = step == kOrder - 1;
                break;
            }
        }
        if (hamilton) {
            pass_mask |= 1U << static_cast<unsigned>(orbit);
        }
    }
    return pass_mask;
}

RawRecord patterned_record(const int second_center) {
    RawRecord result{};
    for (int difference = 1; difference <= kDifferences; ++difference) {
        result.starter1[static_cast<std::size_t>(difference - 1)] =
            Edge{difference, mod_positive(-difference, kStarterModulus)};
        result.starter2[static_cast<std::size_t>(difference - 1)] = Edge{
            mod_positive(second_center + difference, kStarterModulus),
            mod_positive(second_center - difference, kStarterModulus)};
    }
    return result;
}

std::vector<DeviceRecord> read_records(const std::string& path) {
    std::ifstream input(path);
    if (!input) {
        fail("cannot open input: " + path);
    }
    std::uint64_t count = 0;
    if (!(input >> count) || count == 0 ||
        count > static_cast<std::uint64_t>(std::numeric_limits<std::uint32_t>::max())) {
        fail("invalid record count");
    }
    std::vector<DeviceRecord> records;
    records.reserve(static_cast<std::size_t>(count));
    for (std::uint64_t index = 0; index < count; ++index) {
        RawRecord raw{};
        for (Edge& edge : raw.starter1) {
            if (!(input >> edge.x >> edge.y)) {
                fail("truncated S1 record " + std::to_string(index));
            }
        }
        for (Edge& edge : raw.starter2) {
            if (!(input >> edge.x >> edge.y)) {
                fail("truncated S2 record " + std::to_string(index));
            }
        }
        records.push_back(encode_record(raw, static_cast<std::uint32_t>(index)));
    }
    long long extra = 0;
    if (input >> extra) {
        fail("input has trailing integers");
    }
    return records;
}

struct Options {
    std::string input;
    int synthetic{1};
    int repetitions{1};
    unsigned long long candidate_capacity{16ULL};
};

Options parse_options(const int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string argument = argv[i];
        auto require_value = [&]() -> std::string {
            if (++i >= argc) {
                fail(argument + " requires a value");
            }
            return argv[i];
        };
        if (argument == "--input") {
            options.input = require_value();
        } else if (argument == "--synthetic") {
            options.synthetic = std::stoi(require_value());
        } else if (argument == "--repetitions") {
            options.repetitions = std::stoi(require_value());
        } else if (argument == "--candidate-cap") {
            options.candidate_capacity = std::stoull(require_value());
        } else if (argument == "--help" || argument == "-h") {
            std::cout
                << "Usage: k64_cuda [--input records.txt | --synthetic N] "
                   "[--repetitions N] [--candidate-cap N]\n"
                << "Text input: R followed by 60 integers per record: "
                   "15 S1 pairs then 15 S2 pairs.\n";
            std::exit(0);
        } else {
            fail("unknown option: " + argument);
        }
    }
    if (options.repetitions < 1 || options.synthetic < 1 ||
        options.synthetic > 30) {
        fail("repetitions must be positive; synthetic count must be 1..30");
    }
    return options;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        const auto host_start = std::chrono::steady_clock::now();
        std::vector<DeviceRecord> records;
        if (!options.input.empty()) {
            records = read_records(options.input);
        } else {
            records.reserve(static_cast<std::size_t>(options.synthetic));
            for (int index = 0; index < options.synthetic; ++index) {
                records.push_back(encode_record(patterned_record(index + 1),
                                                static_cast<std::uint32_t>(index)));
            }
        }
        const auto host_end = std::chrono::steady_clock::now();
        const double host_seconds =
            std::chrono::duration<double>(host_end - host_start).count();

        DeviceRecord* device_records = nullptr;
        DeviceTotals* device_totals = nullptr;
        Candidate* device_candidates = nullptr;
        Sample* device_samples = nullptr;
        const std::size_t record_bytes = records.size() * sizeof(DeviceRecord);
        const std::size_t candidate_bytes =
            static_cast<std::size_t>(options.candidate_capacity) * sizeof(Candidate);
        const auto end_to_end_start = std::chrono::steady_clock::now();
        cuda_check(cudaMalloc(&device_records, record_bytes), "cudaMalloc records");
        cuda_check(cudaMalloc(&device_totals, sizeof(DeviceTotals)), "cudaMalloc totals");
        cuda_check(cudaMalloc(&device_candidates, candidate_bytes == 0 ? 1 : candidate_bytes),
                   "cudaMalloc candidates");
        cuda_check(cudaMalloc(&device_samples, sizeof(Sample) * kSampleCount),
                   "cudaMalloc samples");
        cuda_check(cudaMemcpy(device_records, records.data(), record_bytes,
                              cudaMemcpyHostToDevice),
                   "copy records");

        // Untimed warm-up catches launch failures before the measured region.
        cuda_check(cudaMemset(device_totals, 0, sizeof(DeviceTotals)), "clear totals");
        evaluate_kernel<<<static_cast<unsigned>(records.size()), kThreads>>>(
            device_records, static_cast<std::uint32_t>(records.size()), 0U,
            device_totals, device_candidates, options.candidate_capacity,
            device_samples);
        cuda_check(cudaGetLastError(), "warm-up launch");
        cuda_check(cudaDeviceSynchronize(), "warm-up synchronize");

        cuda_check(cudaMemset(device_totals, 0, sizeof(DeviceTotals)), "reset totals");
        cuda_check(cudaMemset(device_samples, 0xff, sizeof(Sample) * kSampleCount),
                   "reset samples");
        cudaEvent_t event_start{};
        cudaEvent_t event_end{};
        cuda_check(cudaEventCreate(&event_start), "create start event");
        cuda_check(cudaEventCreate(&event_end), "create end event");
        cuda_check(cudaEventRecord(event_start), "record start event");
        for (int run = 0; run < options.repetitions; ++run) {
            evaluate_kernel<<<static_cast<unsigned>(records.size()), kThreads>>>(
                device_records, static_cast<std::uint32_t>(records.size()),
                static_cast<std::uint32_t>(run), device_totals,
                device_candidates, options.candidate_capacity, device_samples);
        }
        cuda_check(cudaGetLastError(), "timed launch");
        cuda_check(cudaEventRecord(event_end), "record end event");
        cuda_check(cudaEventSynchronize(event_end), "timed synchronize");
        float milliseconds = 0.0F;
        cuda_check(cudaEventElapsedTime(&milliseconds, event_start, event_end),
                   "elapsed time");

        DeviceTotals totals{};
        std::array<Sample, kSampleCount> samples{};
        cuda_check(cudaMemcpy(&totals, device_totals, sizeof(totals),
                              cudaMemcpyDeviceToHost),
                   "copy totals");
        cuda_check(cudaMemcpy(samples.data(), device_samples,
                              sizeof(Sample) * samples.size(),
                              cudaMemcpyDeviceToHost),
                   "copy samples");
        const std::size_t stored_candidates = static_cast<std::size_t>(
            totals.candidates < options.candidate_capacity
                ? totals.candidates
                : options.candidate_capacity);
        std::vector<Candidate> candidates(stored_candidates);
        if (!candidates.empty()) {
            cuda_check(cudaMemcpy(candidates.data(), device_candidates,
                                  candidates.size() * sizeof(Candidate),
                                  cudaMemcpyDeviceToHost),
                       "copy candidates");
        }
        const auto end_to_end_end = std::chrono::steady_clock::now();

        cudaFuncAttributes attributes{};
        cuda_check(cudaFuncGetAttributes(&attributes, evaluate_kernel),
                   "kernel attributes");
        cudaDeviceProp properties{};
        int device = 0;
        cuda_check(cudaGetDevice(&device), "get device");
        cuda_check(cudaGetDeviceProperties(&properties, device), "device properties");

        bool samples_pass = true;
        unsigned long long sampled_checksum_xor = 0ULL;
        unsigned long long sampled_checksum_sum = 0ULL;
        for (int sample_index = 0; sample_index < kSampleCount; ++sample_index) {
            std::uint32_t cpu_lift_mask = 0U;
            const std::uint32_t cpu_pass = cpu_score(
                records[0], sample_mask(sample_index),
                cpu_lift_mask);
            const Sample gpu = samples[static_cast<std::size_t>(sample_index)];
            const bool agrees = gpu.mask == sample_mask(sample_index) &&
                                gpu.lift_mask == cpu_lift_mask &&
                                gpu.pass_mask == cpu_pass;
            samples_pass = samples_pass && agrees;
            unsigned long long sample_key =
                (static_cast<unsigned long long>(gpu.mask) << 32U) |
                static_cast<unsigned long long>(gpu.lift_mask);
            sample_key ^= static_cast<unsigned long long>(gpu.pass_mask) *
                          0xa5a3564e27f8862bULL;
            const unsigned long long sample_token = mix64(sample_key);
            sampled_checksum_xor ^= sample_token;
            sampled_checksum_sum += sample_token;
            std::cout << "SAMPLE pair_id=0 mask=0x" << std::hex << std::setw(4)
                      << std::setfill('0') << gpu.mask << " lift=0x" << std::setw(8)
                      << gpu.lift_mask << " pass=0x" << std::setw(8)
                      << gpu.pass_mask << std::dec << std::setfill(' ')
                      << " cpu_agree=" << (agrees ? "PASS" : "FAIL") << '\n';
        }

        const double kernel_seconds = static_cast<double>(milliseconds) / 1000.0;
        const double pair_evaluations =
            static_cast<double>(records.size()) * options.repetitions;
        const double assignments = pair_evaluations * kMasks;
        const double end_to_end_seconds =
            std::chrono::duration<double>(end_to_end_end - end_to_end_start).count();
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "DEVICE name=\"" << properties.name << "\" cc="
                  << properties.major << '.' << properties.minor << '\n';
        std::cout << "KERNEL regs_per_thread=" << attributes.numRegs
                  << " local_bytes_per_thread=" << attributes.localSizeBytes
                  << " static_shared_bytes=" << attributes.sharedSizeBytes
                  << " record_shared_bytes=" << sizeof(DeviceRecord) << '\n';
        std::cout << "HOST records=" << records.size() << " seconds=" << host_seconds
                  << " records_per_second=" << records.size() / host_seconds << '\n';
        std::cout << "GPU seconds=" << kernel_seconds
                  << " pair_evaluations=" << static_cast<unsigned long long>(pair_evaluations)
                  << " assignments=" << static_cast<unsigned long long>(assignments)
                  << " pairs_per_second=" << pair_evaluations / kernel_seconds
                  << " assignments_per_second=" << assignments / kernel_seconds << '\n';
        std::cout << "END_TO_END seconds=" << end_to_end_seconds
                  << " assignments_per_second=" << assignments / end_to_end_seconds << '\n';
        std::cout << "SAMPLED_CHECKSUM xor=0x" << std::hex
                  << sampled_checksum_xor << " sum=0x" << sampled_checksum_sum
                  << std::dec
                  << " candidates=" << totals.candidates
                  << " stored=" << candidates.size() << '\n';
        for (const Candidate candidate : candidates) {
            std::cout << "CANDIDATE pair_id=" << candidate.pair_id
                      << " mask=" << candidate.mask << " lift_mask=0x" << std::hex
                      << candidate.lift_mask << std::dec << '\n';
        }
        std::cout << "RESULT " << (samples_pass ? "PASS" : "FAIL") << '\n';

        cudaEventDestroy(event_start);
        cudaEventDestroy(event_end);
        cudaFree(device_samples);
        cudaFree(device_candidates);
        cudaFree(device_totals);
        cudaFree(device_records);
        return samples_pass ? 0 : 2;
    } catch (const std::exception& error) {
        std::cerr << "RESULT ERROR: " << error.what() << '\n';
        return 1;
    }
}
