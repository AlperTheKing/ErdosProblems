#include <boost/multiprecision/cpp_int.hpp>
#include <omp.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using boost::multiprecision::cpp_int;
using Clock = std::chrono::steady_clock;

constexpr std::size_t EXPECTED_VERTEX_COUNT = 24'356;
constexpr std::uint64_t EXPECTED_PAIR_COUNT = 296'595'190ULL;
constexpr std::int64_t SCALE = 1'000'000'000'000LL;
constexpr std::int64_t HEIGHT_BOUND = 1'000LL;
constexpr std::array<std::uint32_t, 40> FILTERS = {
    65521, 65519, 65497, 65479, 65449, 65447, 65437, 65423,
    65419, 65413, 65407, 65393, 65381, 65371, 65357, 65353,
    65327, 65323, 65309, 65293, 65287, 65269, 65267, 65257,
    65239, 65213, 65203, 65183, 65179, 65173, 65171, 65167,
    65147, 65141, 65129, 65123, 65119, 65111, 65101, 65099,
};
constexpr std::int64_t HEIGHT_MATRIX[4][4] = {
    {3066644681814LL, -1604217266982LL, 2304106286354LL, -2647588945619LL},
    {-1604217266982LL, 4852120801592LL, 2186366222773LL, -805702796450LL},
    {2304106286354LL, 2186366222773LL, 8991728418553LL, -4979765774895LL},
    {-2647588945619LL, -805702796450LL, -4979765774895LL, 4515819823940LL},
};

struct Vertex {
    std::array<int, 4> lattice{};
    std::int64_t q12 = 0;
    cpp_int numerator;
    cpp_int denominator;
    std::array<std::uint16_t, FILTERS.size()> numerator_mod{};
    std::array<std::uint16_t, FILTERS.size()> denominator_mod{};
};

struct ReplayStats {
    std::array<std::uint64_t, 256> observed_codes{};
    std::array<std::uint64_t, FILTERS.size() + 1> expected_codes{};
    std::uint64_t invalid_codes = 0;
    std::uint64_t mismatches = 0;
    std::uint64_t first_mismatch_ordinal = std::numeric_limits<std::uint64_t>::max();
    std::uint64_t observed_zero_pairs = 0;
    std::uint64_t expected_zero_pairs = 0;
    std::uint64_t exact_tests = 0;
    std::vector<std::uint64_t> edges;
};

cpp_int absolute(cpp_int value) {
    return value < 0 ? -value : value;
}

cpp_int integer_gcd(cpp_int left, cpp_int right) {
    left = absolute(std::move(left));
    right = absolute(std::move(right));
    while (right != 0) {
        cpp_int remainder = left % right;
        left = std::move(right);
        right = std::move(remainder);
    }
    return left;
}

cpp_int integer_square_root(const cpp_int& value) {
    if (value < 0) {
        throw std::runtime_error("integer square root of a negative value");
    }
    if (value < 2) {
        return value;
    }
    const unsigned bit_length = boost::multiprecision::msb(value) + 1;
    cpp_int estimate = cpp_int(1) << ((bit_length + 1) / 2);
    while (true) {
        cpp_int next = (estimate + value / estimate) >> 1;
        if (next >= estimate) {
            while ((estimate + 1) * (estimate + 1) <= value) {
                ++estimate;
            }
            while (estimate * estimate > value) {
                --estimate;
            }
            return estimate;
        }
        estimate = std::move(next);
    }
}

bool is_square_integer(const cpp_int& value) {
    if (value < 0) {
        return false;
    }
    const cpp_int root = integer_square_root(value);
    return root * root == value;
}

// Independent criterion: reduce (a*c+b*d)/(b*d), then require the reduced
// numerator and denominator separately to be integer squares.  The producer
// instead tests whether (a*c+b*d)*(b*d) is an integer square.
bool compatible_after_reduction(const Vertex& left, const Vertex& right) {
    cpp_int denominator = left.denominator * right.denominator;
    cpp_int numerator = left.numerator * right.numerator + denominator;
    if (numerator < 0) {
        return false;
    }
    const cpp_int divisor = integer_gcd(numerator, denominator);
    numerator /= divisor;
    denominator /= divisor;
    return is_square_integer(numerator) && is_square_integer(denominator);
}

std::vector<std::string> split_tabs(const std::string& line) {
    std::vector<std::string> fields;
    std::size_t start = 0;
    while (true) {
        const std::size_t tab = line.find('\t', start);
        fields.push_back(line.substr(start, tab - start));
        if (tab == std::string::npos) {
            return fields;
        }
        start = tab + 1;
    }
}

long long parse_long_long(const std::string& text, const char* field) {
    std::size_t consumed = 0;
    long long value = 0;
    try {
        value = std::stoll(text, &consumed, 10);
    } catch (const std::exception&) {
        throw std::runtime_error(std::string("invalid integer in ") + field);
    }
    if (consumed != text.size()) {
        throw std::runtime_error(std::string("trailing text in ") + field);
    }
    return value;
}

cpp_int parse_big_integer(const std::string& text, const char* field) {
    std::istringstream stream(text);
    cpp_int value;
    stream >> value;
    if (!stream) {
        throw std::runtime_error(std::string("invalid big integer in ") + field);
    }
    stream >> std::ws;
    if (!stream.eof()) {
        throw std::runtime_error(std::string("trailing text in ") + field);
    }
    return value;
}

std::string rational_key(const cpp_int& numerator, const cpp_int& denominator) {
    std::ostringstream output;
    output << numerator << '/' << denominator;
    return output.str();
}

bool is_excluded_ace_value(const cpp_int& numerator, const cpp_int& denominator) {
    return numerator * 560 == cpp_int(243) * denominator
        || numerator * 63 == cpp_int(1100) * denominator
        || numerator * 112 == cpp_int(95) * denominator;
}

std::int64_t recompute_q12(const std::array<int, 4>& lattice) {
    __int128 value = 0;
    for (std::size_t row = 0; row < 4; ++row) {
        for (std::size_t column = 0; column < 4; ++column) {
            value += static_cast<__int128>(lattice[row])
                * HEIGHT_MATRIX[row][column] * lattice[column];
        }
    }
    if (value < 0 || value > std::numeric_limits<std::int64_t>::max()) {
        throw std::runtime_error("recomputed q12 is outside signed 64-bit range");
    }
    return static_cast<std::int64_t>(value);
}

std::uint16_t positive_mod(const cpp_int& value, std::uint32_t modulus) {
    long long remainder = (value % modulus).convert_to<long long>();
    if (remainder < 0) {
        remainder += modulus;
    }
    return static_cast<std::uint16_t>(remainder);
}

bool is_prime_by_trial_division(std::uint32_t value) {
    if (value < 2) {
        return false;
    }
    for (std::uint32_t divisor = 2; divisor * divisor <= value; ++divisor) {
        if (value % divisor == 0) {
            return false;
        }
    }
    return true;
}

std::vector<Vertex> read_vertices(const std::filesystem::path& path) {
    std::ifstream input(path);
    if (!input) {
        throw std::runtime_error("cannot open vertices.tsv");
    }
    std::string line;
    if (!std::getline(input, line)) {
        throw std::runtime_error("vertices.tsv is empty");
    }
    if (!line.empty() && line.back() == '\r') {
        line.pop_back();
    }
    if (line != "index\tk1\tk2\tk3\tk4\tq12_scaled\tnumerator\tdenominator") {
        throw std::runtime_error("unexpected vertices.tsv header");
    }

    std::vector<Vertex> vertices;
    vertices.reserve(EXPECTED_VERTEX_COUNT);
    std::set<std::string> unique_rationals;
    std::size_t line_number = 1;
    while (std::getline(input, line)) {
        ++line_number;
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (line.empty()) {
            throw std::runtime_error("blank row in vertices.tsv at line " + std::to_string(line_number));
        }
        const std::vector<std::string> fields = split_tabs(line);
        if (fields.size() != 8) {
            throw std::runtime_error("wrong column count at vertices.tsv line " + std::to_string(line_number));
        }
        const long long index = parse_long_long(fields[0], "index");
        if (index < 0 || static_cast<std::size_t>(index) != vertices.size()) {
            throw std::runtime_error("noncanonical vertex index at line " + std::to_string(line_number));
        }

        Vertex vertex;
        for (std::size_t coordinate = 0; coordinate < 4; ++coordinate) {
            const long long coefficient = parse_long_long(fields[coordinate + 1], "lattice coordinate");
            if (coefficient < std::numeric_limits<int>::min()
                || coefficient > std::numeric_limits<int>::max()) {
                throw std::runtime_error("lattice coordinate outside int range");
            }
            vertex.lattice[coordinate] = static_cast<int>(coefficient);
        }
        if (vertex.lattice[0] <= 0 || vertex.lattice[0] > 55
            || (absolute(cpp_int(vertex.lattice[0])) % 2) != 1
            || vertex.lattice[1] < -55 || vertex.lattice[1] > 55
            || (absolute(cpp_int(vertex.lattice[1])) % 2) != 1
            || vertex.lattice[2] < -55 || vertex.lattice[2] > 55
            || (absolute(cpp_int(vertex.lattice[2])) % 2) != 1
            || vertex.lattice[3] < -54 || vertex.lattice[3] > 54
            || (absolute(cpp_int(vertex.lattice[3])) % 2) != 0) {
            throw std::runtime_error("vertex violates the declared parity box at line " + std::to_string(line_number));
        }

        vertex.q12 = parse_long_long(fields[5], "q12_scaled");
        if (vertex.q12 != recompute_q12(vertex.lattice)) {
            throw std::runtime_error("q12 mismatch at line " + std::to_string(line_number));
        }
        if (vertex.q12 > HEIGHT_BOUND * SCALE) {
            throw std::runtime_error("vertex is outside q12<=1000 at line " + std::to_string(line_number));
        }

        vertex.numerator = parse_big_integer(fields[6], "numerator");
        vertex.denominator = parse_big_integer(fields[7], "denominator");
        if (vertex.numerator == 0 || vertex.denominator <= 0) {
            throw std::runtime_error("zero value or nonpositive denominator at line " + std::to_string(line_number));
        }
        if (integer_gcd(vertex.numerator, vertex.denominator) != 1) {
            throw std::runtime_error("unnormalized rational at line " + std::to_string(line_number));
        }
        if (is_excluded_ace_value(vertex.numerator, vertex.denominator)) {
            throw std::runtime_error("fixed ACE value appears as a vertex at line " + std::to_string(line_number));
        }
        if (!unique_rationals.insert(rational_key(vertex.numerator, vertex.denominator)).second) {
            throw std::runtime_error("duplicate rational vertex at line " + std::to_string(line_number));
        }

        for (std::size_t filter = 0; filter < FILTERS.size(); ++filter) {
            vertex.numerator_mod[filter] = positive_mod(vertex.numerator, FILTERS[filter]);
            vertex.denominator_mod[filter] = positive_mod(vertex.denominator, FILTERS[filter]);
        }
        vertices.push_back(std::move(vertex));
    }

    if (vertices.size() < 2) {
        throw std::runtime_error("at least two vertices are required");
    }
    if (vertices.size() != EXPECTED_VERTEX_COUNT) {
        throw std::runtime_error("vertex count differs from declared 24356");
    }
    return vertices;
}

std::vector<std::uint8_t> read_certificate(
    const std::filesystem::path& path,
    std::uint64_t expected_bytes
) {
    if (!std::filesystem::exists(path)) {
        throw std::runtime_error("pair_certificate.bin does not exist");
    }
    if (std::filesystem::file_size(path) != expected_bytes) {
        throw std::runtime_error("certificate byte length differs from the pair count");
    }
    std::vector<std::uint8_t> certificate(static_cast<std::size_t>(expected_bytes));
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("cannot open pair_certificate.bin");
    }
    input.read(
        reinterpret_cast<char*>(certificate.data()),
        static_cast<std::streamsize>(certificate.size())
    );
    if (!input || input.gcount() != static_cast<std::streamsize>(certificate.size())) {
        throw std::runtime_error("short read from pair_certificate.bin");
    }
    return certificate;
}

std::uint64_t pair_offset(std::uint64_t left, std::uint64_t vertex_count) {
    return left * (2 * vertex_count - left - 1) / 2;
}

std::uint8_t first_rejecting_filter(
    const Vertex& left,
    const Vertex& right,
    const std::array<std::vector<std::uint8_t>, FILTERS.size()>& square_residues
) {
    for (std::size_t filter = 0; filter < FILTERS.size(); ++filter) {
        const std::uint64_t modulus = FILTERS[filter];
        const std::uint64_t denominator_product =
            static_cast<std::uint64_t>(left.denominator_mod[filter])
            * right.denominator_mod[filter] % modulus;
        const std::uint64_t numerator_product =
            static_cast<std::uint64_t>(left.numerator_mod[filter])
            * right.numerator_mod[filter] % modulus;
        const std::uint64_t witness =
            ((numerator_product + denominator_product) % modulus)
            * denominator_product % modulus;
        if (square_residues[filter][witness] == 0) {
            return static_cast<std::uint8_t>(filter + 1);
        }
    }
    return 0;
}

ReplayStats replay_pairs(
    const std::vector<Vertex>& vertices,
    const std::vector<std::uint8_t>& certificate,
    int workers
) {
    std::array<std::vector<std::uint8_t>, FILTERS.size()> square_residues;
    for (std::size_t filter = 0; filter < FILTERS.size(); ++filter) {
        const std::uint32_t modulus = FILTERS[filter];
        square_residues[filter].assign(modulus, 0);
        for (std::uint32_t value = 0; value < modulus; ++value) {
            square_residues[filter][
                static_cast<std::uint64_t>(value) * value % modulus
            ] = 1;
        }
    }

    std::vector<ReplayStats> local(static_cast<std::size_t>(workers));
    const std::uint64_t vertex_count = vertices.size();
#pragma omp parallel for schedule(dynamic, 8) num_threads(workers)
    for (long long signed_left = 0;
         signed_left < static_cast<long long>(vertex_count);
         ++signed_left) {
        const std::uint64_t left = static_cast<std::uint64_t>(signed_left);
        ReplayStats& stats = local[static_cast<std::size_t>(omp_get_thread_num())];
        const std::uint64_t offset = pair_offset(left, vertex_count);
        for (std::uint64_t right = left + 1; right < vertex_count; ++right) {
            const std::uint64_t ordinal = offset + (right - left - 1);
            const std::uint8_t observed = certificate[static_cast<std::size_t>(ordinal)];
            const std::uint8_t expected = first_rejecting_filter(
                vertices[static_cast<std::size_t>(left)],
                vertices[static_cast<std::size_t>(right)],
                square_residues
            );
            ++stats.observed_codes[observed];
            ++stats.expected_codes[expected];
            if (observed > FILTERS.size()) {
                ++stats.invalid_codes;
            }
            if (observed != expected) {
                ++stats.mismatches;
                stats.first_mismatch_ordinal = std::min(stats.first_mismatch_ordinal, ordinal);
            }
            if (observed == 0) {
                ++stats.observed_zero_pairs;
            }
            if (expected == 0) {
                ++stats.expected_zero_pairs;
            }

            // Test the union so a malformed nonzero byte cannot hide an edge,
            // while every literal code-0 byte is still exact-tested.
            if (observed == 0 || expected == 0) {
                ++stats.exact_tests;
                const bool edge = compatible_after_reduction(
                    vertices[static_cast<std::size_t>(left)],
                    vertices[static_cast<std::size_t>(right)]
                );
                if (expected == 0 && edge) {
                    stats.edges.push_back((left << 32) | right);
                }
            }
        }
    }

    ReplayStats total;
    for (ReplayStats& stats : local) {
        for (std::size_t code = 0; code < total.observed_codes.size(); ++code) {
            total.observed_codes[code] += stats.observed_codes[code];
        }
        for (std::size_t code = 0; code < total.expected_codes.size(); ++code) {
            total.expected_codes[code] += stats.expected_codes[code];
        }
        total.invalid_codes += stats.invalid_codes;
        total.mismatches += stats.mismatches;
        total.first_mismatch_ordinal = std::min(
            total.first_mismatch_ordinal, stats.first_mismatch_ordinal
        );
        total.observed_zero_pairs += stats.observed_zero_pairs;
        total.expected_zero_pairs += stats.expected_zero_pairs;
        total.exact_tests += stats.exact_tests;
        total.edges.insert(
            total.edges.end(),
            std::make_move_iterator(stats.edges.begin()),
            std::make_move_iterator(stats.edges.end())
        );
    }
    std::sort(total.edges.begin(), total.edges.end());
    if (std::adjacent_find(total.edges.begin(), total.edges.end()) != total.edges.end()) {
        throw std::runtime_error("duplicate edge generated during replay");
    }
    return total;
}

std::array<std::uint32_t, 4> find_k4(
    std::size_t vertex_count,
    const std::vector<std::uint64_t>& edges,
    std::uint64_t& triangle_count
) {
    std::vector<std::vector<std::uint32_t>> forward(vertex_count);
    for (std::uint64_t encoded : edges) {
        const std::uint32_t left = static_cast<std::uint32_t>(encoded >> 32);
        const std::uint32_t right = static_cast<std::uint32_t>(encoded);
        if (left >= right || right >= vertex_count) {
            throw std::runtime_error("replayed edge has invalid orientation");
        }
        forward[left].push_back(right);
    }
    for (auto& neighbors : forward) {
        std::sort(neighbors.begin(), neighbors.end());
    }

    triangle_count = 0;
    std::vector<std::uint32_t> common;
    for (std::uint32_t left = 0; left < vertex_count; ++left) {
        for (std::uint32_t right : forward[left]) {
            common.clear();
            auto left_begin = std::upper_bound(forward[left].begin(), forward[left].end(), right);
            std::set_intersection(
                left_begin, forward[left].end(),
                forward[right].begin(), forward[right].end(),
                std::back_inserter(common)
            );
            triangle_count += common.size();
            for (std::size_t first = 0; first < common.size(); ++first) {
                for (std::size_t second = first + 1; second < common.size(); ++second) {
                    if (std::binary_search(
                        forward[common[first]].begin(),
                        forward[common[first]].end(),
                        common[second]
                    )) {
                        return {left, right, common[first], common[second]};
                    }
                }
            }
        }
    }
    return {
        std::numeric_limits<std::uint32_t>::max(),
        std::numeric_limits<std::uint32_t>::max(),
        std::numeric_limits<std::uint32_t>::max(),
        std::numeric_limits<std::uint32_t>::max(),
    };
}

double elapsed_seconds(const Clock::time_point& start) {
    return std::chrono::duration<double>(Clock::now() - start).count();
}

int run_self_test() {
    // {1,3,8,120} is a Diophantine quadruple.  The fifth value 2 is not
    // compatible with any of its members under this fixture.  The ten bytes
    // below were fixed independently in pair-ordinal order, not generated by
    // first_rejecting_filter: 00 00 00 04 00 00 03 00 01 01.
    const std::array<long long, 5> values = {1, 3, 8, 120, 2};
    std::vector<Vertex> vertices(values.size());
    for (std::size_t index = 0; index < values.size(); ++index) {
        vertices[index].numerator = values[index];
        vertices[index].denominator = 1;
        for (std::size_t filter = 0; filter < FILTERS.size(); ++filter) {
            vertices[index].numerator_mod[filter] = positive_mod(
                vertices[index].numerator, FILTERS[filter]
            );
            vertices[index].denominator_mod[filter] = 1;
        }
    }
    const std::vector<std::uint8_t> certificate = {
        0, 0, 0, 4,
        0, 0, 3,
        0, 1,
        1,
    };
    ReplayStats stats = replay_pairs(vertices, certificate, 2);
    std::uint64_t triangles = 0;
    const std::array<std::uint32_t, 4> clique = find_k4(
        vertices.size(), stats.edges, triangles
    );
    const bool pass = stats.invalid_codes == 0
        && stats.mismatches == 0
        && stats.observed_zero_pairs == 6
        && stats.expected_zero_pairs == 6
        && stats.exact_tests == 6
        && stats.edges.size() == 6
        && clique == std::array<std::uint32_t, 4>{0, 1, 2, 3};
    std::cout << "{\"status\":\"" << (pass ? "SELF_TEST_PASS" : "SELF_TEST_FAIL")
              << "\",\"certificate_bytes_scanned\":10,\"mismatches\":"
              << stats.mismatches << ",\"exact_tests\":" << stats.exact_tests
              << ",\"edge_count\":" << stats.edges.size() << ",\"clique\":["
              << clique[0] << ',' << clique[1] << ',' << clique[2] << ',' << clique[3]
              << "]}\n";
    return pass ? 0 : 1;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--self-test") {
            return run_self_test();
        }
        if (argc < 3 || argc > 4) {
            std::cerr << "usage: ace_graph_certificate_replay VERTICES_TSV "
                         "PAIR_CERTIFICATE_BIN [THREADS]\n"
                         "       ace_graph_certificate_replay --self-test\n";
            return 2;
        }
        int workers = 1;
        for (int argument = 3; argument < argc; ++argument) {
            const std::string value(argv[argument]);
            std::size_t consumed = 0;
            workers = std::stoi(value, &consumed);
            if (consumed != value.size()) {
                throw std::runtime_error("invalid worker count");
            }
        }
        if (workers < 1 || workers > 64) {
            throw std::runtime_error("worker count must be in [1,64]");
        }
        std::set<std::uint32_t> unique_filters;
        for (std::uint32_t filter : FILTERS) {
            if (!is_prime_by_trial_division(filter)) {
                throw std::runtime_error("declared filter is not prime");
            }
            if (!unique_filters.insert(filter).second) {
                throw std::runtime_error("duplicate declared filter");
            }
        }

        const Clock::time_point total_start = Clock::now();
        const Clock::time_point input_start = Clock::now();
        const std::vector<Vertex> vertices = read_vertices(argv[1]);
        const std::uint64_t vertex_count = vertices.size();
        const std::uint64_t pair_count = vertex_count * (vertex_count - 1) / 2;
        if (pair_count != EXPECTED_PAIR_COUNT) {
            throw std::runtime_error("pair count differs from declared 296595190");
        }
        const std::vector<std::uint8_t> certificate = read_certificate(argv[2], pair_count);
        const double input_seconds = elapsed_seconds(input_start);

        const Clock::time_point replay_start = Clock::now();
        ReplayStats stats = replay_pairs(vertices, certificate, workers);
        const double replay_seconds = elapsed_seconds(replay_start);

        std::uint64_t scanned = 0;
        for (std::uint64_t count : stats.observed_codes) {
            scanned += count;
        }
        if (scanned != pair_count) {
            throw std::runtime_error("internal replay count differs from pair count");
        }

        const Clock::time_point clique_start = Clock::now();
        std::uint64_t triangle_count = 0;
        const std::array<std::uint32_t, 4> clique = find_k4(
            vertices.size(), stats.edges, triangle_count
        );
        const bool hit = clique[0] != std::numeric_limits<std::uint32_t>::max();
        const double clique_seconds = elapsed_seconds(clique_start);
        const bool certificate_valid = stats.invalid_codes == 0 && stats.mismatches == 0;

        std::cout << "{\n"
                  << "  \"status\": \""
                  << (certificate_valid ? (hit ? "HIT" : "NO_HIT") : "INVALID_CERTIFICATE")
                  << "\",\n"
                  << "  \"mode\": \"DECLARED_ACE_Q12\",\n"
                  << "  \"workers\": " << workers << ",\n"
                  << "  \"vertex_count\": " << vertex_count << ",\n"
                  << "  \"certificate_bytes_scanned\": " << scanned << ",\n"
                  << "  \"expected_pair_count\": " << pair_count << ",\n"
                  << "  \"invalid_code_count\": " << stats.invalid_codes << ",\n"
                  << "  \"filter_code_mismatches\": " << stats.mismatches << ",\n"
                  << "  \"first_mismatch_ordinal\": ";
        if (stats.first_mismatch_ordinal == std::numeric_limits<std::uint64_t>::max()) {
            std::cout << "null";
        } else {
            std::cout << stats.first_mismatch_ordinal;
        }
        std::cout << ",\n"
                  << "  \"observed_code_zero_pairs\": " << stats.observed_zero_pairs << ",\n"
                  << "  \"recomputed_code_zero_pairs\": " << stats.expected_zero_pairs << ",\n"
                  << "  \"observed_code_counts_0_to_40\": [";
        for (std::size_t code = 0; code <= FILTERS.size(); ++code) {
            if (code != 0) std::cout << ',';
            std::cout << stats.observed_codes[code];
        }
        std::cout << "],\n  \"recomputed_code_counts_0_to_40\": [";
        for (std::size_t code = 0; code <= FILTERS.size(); ++code) {
            if (code != 0) std::cout << ',';
            std::cout << stats.expected_codes[code];
        }
        std::cout << "],\n"
                  << "  \"independent_exact_tests\": " << stats.exact_tests << ",\n"
                  << "  \"edge_count\": " << stats.edges.size() << ",\n"
                  << "  \"triangle_count_until_hit_or_exhaustion\": " << triangle_count << ",\n"
                  << "  \"clique\": ";
        if (hit) {
            std::cout << '[' << clique[0] << ',' << clique[1] << ','
                      << clique[2] << ',' << clique[3] << ']';
        } else {
            std::cout << "null";
        }
        std::cout << ",\n"
                  << "  \"input_seconds\": " << input_seconds << ",\n"
                  << "  \"replay_seconds\": " << replay_seconds << ",\n"
                  << "  \"clique_seconds\": " << clique_seconds << ",\n"
                  << "  \"total_seconds\": " << elapsed_seconds(total_start) << "\n"
                  << "}\n";
        return certificate_valid ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }
}
