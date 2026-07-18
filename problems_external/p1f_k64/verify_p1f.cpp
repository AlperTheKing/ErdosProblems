#include <algorithm>
#include <charconv>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace {

using Edge = std::pair<int, int>;
using Matching = std::vector<int>;

struct Certificate {
    int modulus{};
    std::vector<Edge> pairs;
    std::string source;
};

struct CycleProfile {
    int components{};
    int largest_component{};
};

class VerificationError final : public std::runtime_error {
  public:
    explicit VerificationError(const std::string& message)
        : std::runtime_error(message) {}
};

[[nodiscard]] Certificate published_k56_certificate() {
    return Certificate{
        54,
        {{36, 17}, {44, 12}, {39, 45}, {18, 35}, {8, 50},
         {23, 15}, {42, 32}, {5, 46},  {19, 49}, {22, 37},
         {10, 6},  {33, 30}, {3, 41},  {14, 21}, {48, 43},
         {16, 52}, {25, 34}, {7, 38},  {11, 31}, {4, 2},
         {29, 28}, {1, 27},  {0, 40},  {13, 24}, {51, 26},
         {53, 20}},
        "Pike published K56 even starter"};
}

[[nodiscard]] std::vector<int> extract_integers(std::istream& input) {
    std::vector<int> values;
    std::string line;
    std::size_t line_number = 0;

    while (std::getline(input, line)) {
        ++line_number;
        const std::size_t comment = line.find('#');
        if (comment != std::string::npos) {
            line.erase(comment);
        }

        std::size_t position = 0;
        while (position < line.size()) {
            const unsigned char current =
                static_cast<unsigned char>(line[position]);
            const bool begins_with_digit = std::isdigit(current) != 0;
            const bool begins_with_sign =
                (line[position] == '-' || line[position] == '+') &&
                position + 1 < line.size() &&
                std::isdigit(static_cast<unsigned char>(line[position + 1])) !=
                    0;
            if (!begins_with_digit && !begins_with_sign) {
                ++position;
                continue;
            }

            const std::size_t begin = position;
            if (line[position] == '-' || line[position] == '+') {
                ++position;
            }
            while (position < line.size() &&
                   std::isdigit(static_cast<unsigned char>(line[position])) !=
                       0) {
                ++position;
            }

            int value = 0;
            const char* first = line.data() + begin;
            const char* last = line.data() + position;
            if (*first == '+') {
                ++first;
            }
            const auto parsed = std::from_chars(first, last, value);
            if (parsed.ec != std::errc{} || parsed.ptr != last) {
                throw VerificationError("invalid integer on input line " +
                                        std::to_string(line_number));
            }
            values.push_back(value);
        }
    }
    return values;
}

[[nodiscard]] Certificate read_certificate(
    std::istream& input, const std::string& source,
    const std::optional<int> modulus_override) {
    std::vector<int> values = extract_integers(input);
    if (values.empty()) {
        throw VerificationError("certificate contains no integers");
    }

    int modulus = 0;
    std::size_t first_edge_value = 0;
    if (modulus_override.has_value()) {
        modulus = *modulus_override;
    } else {
        modulus = values.front();
        first_edge_value = 1;
    }

    const std::size_t remaining = values.size() - first_edge_value;
    if (remaining % 2U != 0U) {
        throw VerificationError(
            "certificate must contain an even number of edge endpoints");
    }

    std::vector<Edge> pairs;
    pairs.reserve(remaining / 2U);
    for (std::size_t i = first_edge_value; i < values.size(); i += 2U) {
        pairs.emplace_back(values[i], values[i + 1U]);
    }
    return Certificate{modulus, std::move(pairs), source};
}

[[nodiscard]] int canonical_difference(const int x, const int y,
                                       const int modulus) {
    const int forward = (x - y + modulus) % modulus;
    const int backward = (y - x + modulus) % modulus;
    return std::min(forward, backward);
}

[[nodiscard]] std::vector<int> validate_even_starter(
    const Certificate& certificate) {
    const int modulus = certificate.modulus;
    if (modulus < 4 || modulus % 2 != 0) {
        throw VerificationError("modulus must be even and at least 4");
    }

    const std::size_t expected_pairs =
        static_cast<std::size_t>(modulus / 2 - 1);
    if (certificate.pairs.size() != expected_pairs) {
        throw VerificationError("expected " + std::to_string(expected_pairs) +
                                " pairs but read " +
                                std::to_string(certificate.pairs.size()));
    }

    std::vector<int> vertex_count(static_cast<std::size_t>(modulus), 0);
    std::vector<int> difference_count(
        static_cast<std::size_t>(modulus / 2), 0);

    for (std::size_t index = 0; index < certificate.pairs.size(); ++index) {
        const auto [x, y] = certificate.pairs[index];
        if (x < 0 || x >= modulus || y < 0 || y >= modulus) {
            throw VerificationError("pair " + std::to_string(index) +
                                    " has an endpoint outside ZMod " +
                                    std::to_string(modulus));
        }
        if (x == y) {
            throw VerificationError("pair " + std::to_string(index) +
                                    " is a loop");
        }
        ++vertex_count[static_cast<std::size_t>(x)];
        ++vertex_count[static_cast<std::size_t>(y)];

        const int difference = canonical_difference(x, y, modulus);
        if (difference <= 0 || difference >= modulus / 2) {
            throw VerificationError("pair " + std::to_string(index) +
                                    " has forbidden difference " +
                                    std::to_string(difference));
        }
        ++difference_count[static_cast<std::size_t>(difference)];
    }

    std::vector<int> holes;
    for (int vertex = 0; vertex < modulus; ++vertex) {
        const int count = vertex_count[static_cast<std::size_t>(vertex)];
        if (count == 0) {
            holes.push_back(vertex);
        } else if (count != 1) {
            throw VerificationError("finite vertex " +
                                    std::to_string(vertex) + " occurs " +
                                    std::to_string(count) + " times");
        }
    }
    if (holes.size() != 2U) {
        throw VerificationError("even starter must omit exactly two vertices");
    }

    for (int difference = 1; difference < modulus / 2; ++difference) {
        const int count =
            difference_count[static_cast<std::size_t>(difference)];
        if (count != 1) {
            throw VerificationError("canonical difference " +
                                    std::to_string(difference) + " occurs " +
                                    std::to_string(count) + " times");
        }
    }
    return holes;
}

void add_edge(Matching& matching, const int left, const int right,
              const std::string& context) {
    const int order = static_cast<int>(matching.size());
    if (left < 0 || left >= order || right < 0 || right >= order) {
        throw VerificationError(context + ": endpoint outside graph");
    }
    if (left == right) {
        throw VerificationError(context + ": loop");
    }
    if (matching[static_cast<std::size_t>(left)] != -1 ||
        matching[static_cast<std::size_t>(right)] != -1) {
        throw VerificationError(context + ": repeated matching endpoint");
    }
    matching[static_cast<std::size_t>(left)] = right;
    matching[static_cast<std::size_t>(right)] = left;
}

void validate_matching(const Matching& matching, const std::string& context) {
    for (std::size_t vertex = 0; vertex < matching.size(); ++vertex) {
        const int partner = matching[vertex];
        if (partner < 0 ||
            static_cast<std::size_t>(partner) >= matching.size()) {
            throw VerificationError(context + ": unmatched vertex " +
                                    std::to_string(vertex));
        }
        if (matching[static_cast<std::size_t>(partner)] !=
            static_cast<int>(vertex)) {
            throw VerificationError(context + ": partner map is not symmetric");
        }
    }
}

[[nodiscard]] std::vector<Matching> develop_factorisation(
    const Certificate& certificate, const std::vector<int>& holes) {
    const int modulus = certificate.modulus;
    const int order = modulus + 2;
    const int infinity_zero = modulus;
    const int infinity_one = modulus + 1;

    std::vector<Matching> factors;
    factors.reserve(static_cast<std::size_t>(modulus + 1));

    for (int shift = 0; shift < modulus; ++shift) {
        Matching factor(static_cast<std::size_t>(order), -1);
        const std::string context = "developed factor " +
                                    std::to_string(shift);
        for (const auto& [x, y] : certificate.pairs) {
            add_edge(factor, (x + shift) % modulus,
                     (y + shift) % modulus, context);
        }
        add_edge(factor, (holes[0] + shift) % modulus, infinity_zero,
                 context);
        add_edge(factor, (holes[1] + shift) % modulus, infinity_one,
                 context);
        validate_matching(factor, context);
        factors.push_back(std::move(factor));
    }

    Matching antipodal(static_cast<std::size_t>(order), -1);
    const std::string context = "antipodal factor";
    for (int x = 0; x < modulus / 2; ++x) {
        add_edge(antipodal, x, x + modulus / 2, context);
    }
    add_edge(antipodal, infinity_zero, infinity_one, context);
    validate_matching(antipodal, context);
    factors.push_back(std::move(antipodal));

    return factors;
}

[[nodiscard]] std::size_t validate_edge_partition(
    const std::vector<Matching>& factors) {
    if (factors.empty()) {
        throw VerificationError("factorisation is empty");
    }
    const std::size_t order = factors.front().size();
    if (factors.size() + 1U != order) {
        throw VerificationError("K_n factorisation must contain n-1 factors");
    }

    std::vector<int> counts(order * order, 0);
    std::size_t listed_edges = 0;
    for (std::size_t factor_index = 0; factor_index < factors.size();
         ++factor_index) {
        const Matching& factor = factors[factor_index];
        if (factor.size() != order) {
            throw VerificationError("factor order mismatch");
        }
        validate_matching(factor,
                          "factor " + std::to_string(factor_index));
        for (std::size_t left = 0; left < order; ++left) {
            const std::size_t right =
                static_cast<std::size_t>(factor[left]);
            if (left < right) {
                ++counts[left * order + right];
                ++listed_edges;
            }
        }
    }

    std::size_t complete_graph_edges = 0;
    for (std::size_t left = 0; left < order; ++left) {
        for (std::size_t right = left + 1U; right < order; ++right) {
            ++complete_graph_edges;
            const int count = counts[left * order + right];
            if (count != 1) {
                throw VerificationError("edge {" + std::to_string(left) +
                                        "," + std::to_string(right) +
                                        "} occurs " +
                                        std::to_string(count) + " times");
            }
        }
    }
    if (listed_edges != complete_graph_edges) {
        throw VerificationError("factor edge total does not equal |E(K_n)|");
    }
    return complete_graph_edges;
}

[[nodiscard]] CycleProfile cycle_profile(const Matching& first,
                                         const Matching& second) {
    if (first.size() != second.size()) {
        throw VerificationError("cannot union matchings of different orders");
    }
    const std::size_t order = first.size();
    std::vector<std::uint8_t> visited(order, 0U);
    CycleProfile profile{};
    std::vector<int> stack;
    stack.reserve(order);

    for (std::size_t start = 0; start < order; ++start) {
        if (visited[start] != 0U) {
            continue;
        }
        ++profile.components;
        int component_size = 0;
        stack.push_back(static_cast<int>(start));
        visited[start] = 1U;

        while (!stack.empty()) {
            const int vertex = stack.back();
            stack.pop_back();
            ++component_size;

            const int neighbours[2] = {
                first[static_cast<std::size_t>(vertex)],
                second[static_cast<std::size_t>(vertex)]};
            if (neighbours[0] == neighbours[1]) {
                throw VerificationError(
                    "two factors share an edge in a factor-pair union");
            }
            for (const int neighbour : neighbours) {
                const std::size_t index =
                    static_cast<std::size_t>(neighbour);
                if (visited[index] == 0U) {
                    visited[index] = 1U;
                    stack.push_back(neighbour);
                }
            }
        }
        profile.largest_component =
            std::max(profile.largest_component, component_size);
    }
    return profile;
}

[[nodiscard]] bool is_hamilton_union(const Matching& first,
                                     const Matching& second) {
    const CycleProfile profile = cycle_profile(first, second);
    return profile.components == 1 &&
           profile.largest_component == static_cast<int>(first.size());
}

struct HamiltonCheckSummary {
    std::size_t reduced_checks{};
    std::size_t full_checks{};
};

[[nodiscard]] HamiltonCheckSummary validate_hamilton_unions(
    const std::vector<Matching>& factors, const int modulus) {
    const std::size_t antipodal = static_cast<std::size_t>(modulus);
    std::vector<std::uint8_t> reduced(
        static_cast<std::size_t>(modulus / 2 + 1), 0U);

    reduced[0] =
        is_hamilton_union(factors[antipodal], factors[0]) ? 1U : 0U;
    if (reduced[0] == 0U) {
        throw VerificationError("reduced union M_* + M_0 is not Hamiltonian");
    }
    for (int difference = 1; difference <= modulus / 2; ++difference) {
        const bool hamilton = is_hamilton_union(
            factors[0], factors[static_cast<std::size_t>(difference)]);
        reduced[static_cast<std::size_t>(difference)] =
            hamilton ? 1U : 0U;
        if (!hamilton) {
            const CycleProfile profile = cycle_profile(
                factors[0], factors[static_cast<std::size_t>(difference)]);
            throw VerificationError(
                "reduced union M_0 + M_" + std::to_string(difference) +
                " has " + std::to_string(profile.components) +
                " components; largest has " +
                std::to_string(profile.largest_component) + " vertices");
        }
    }

    std::size_t full_checks = 0;
    for (std::size_t left = 0; left < factors.size(); ++left) {
        for (std::size_t right = left + 1U; right < factors.size(); ++right) {
            ++full_checks;
            const bool hamilton =
                is_hamilton_union(factors[left], factors[right]);

            std::size_t orbit = 0;
            if (left != antipodal && right != antipodal) {
                const int left_index = static_cast<int>(left);
                const int right_index = static_cast<int>(right);
                const int forward =
                    (right_index - left_index + modulus) % modulus;
                orbit = static_cast<std::size_t>(
                    std::min(forward, modulus - forward));
            }
            const bool reduced_hamilton = reduced[orbit] != 0U;
            if (hamilton != reduced_hamilton) {
                throw VerificationError(
                    "full factor-pair result disagrees with orbit representative");
            }
            if (!hamilton) {
                throw VerificationError("factor pair {" +
                                        std::to_string(left) + "," +
                                        std::to_string(right) +
                                        "} is not Hamiltonian");
            }
        }
    }

    return HamiltonCheckSummary{reduced.size(), full_checks};
}

void print_usage(const char* program) {
    std::cout
        << "Usage:\n"
        << "  " << program << " [--published-k56]\n"
        << "  " << program << " --file PATH [--modulus Q]\n"
        << "  " << program << " --stdin [--modulus Q]\n\n"
        << "Without --modulus, the first integer read is Q. Remaining "
           "integers are endpoint pairs.\n"
        << "Punctuation and # comments are ignored. With --modulus, every "
           "integer read is an endpoint.\n";
}

[[nodiscard]] int parse_modulus(const std::string_view text) {
    int value = 0;
    const char* first = text.data();
    const char* last = text.data() + text.size();
    const auto parsed = std::from_chars(first, last, value);
    if (parsed.ec != std::errc{} || parsed.ptr != last) {
        throw VerificationError("invalid --modulus value");
    }
    return value;
}

struct Options {
    enum class Source { published_k56, file, standard_input };
    Source source{Source::published_k56};
    std::string path;
    std::optional<int> modulus;
    bool help{};
};

[[nodiscard]] Options parse_options(const int argc, char* argv[]) {
    Options options;
    bool source_selected = false;

    for (int i = 1; i < argc; ++i) {
        const std::string argument = argv[i];
        if (argument == "--help" || argument == "-h") {
            options.help = true;
        } else if (argument == "--published-k56") {
            if (source_selected) {
                throw VerificationError("select exactly one certificate source");
            }
            options.source = Options::Source::published_k56;
            source_selected = true;
        } else if (argument == "--file") {
            if (source_selected || i + 1 >= argc) {
                throw VerificationError("--file requires one path and one source");
            }
            options.source = Options::Source::file;
            options.path = argv[++i];
            source_selected = true;
        } else if (argument == "--stdin") {
            if (source_selected) {
                throw VerificationError("select exactly one certificate source");
            }
            options.source = Options::Source::standard_input;
            source_selected = true;
        } else if (argument == "--modulus") {
            if (options.modulus.has_value() || i + 1 >= argc) {
                throw VerificationError("--modulus requires exactly one value");
            }
            options.modulus = parse_modulus(argv[++i]);
        } else {
            throw VerificationError("unknown argument: " + argument);
        }
    }

    if (options.source == Options::Source::published_k56 &&
        options.modulus.has_value()) {
        throw VerificationError("--modulus cannot override published K56");
    }
    return options;
}

[[nodiscard]] Certificate load_certificate(const Options& options) {
    if (options.source == Options::Source::published_k56) {
        return published_k56_certificate();
    }
    if (options.source == Options::Source::standard_input) {
        return read_certificate(std::cin, "standard input", options.modulus);
    }

    std::ifstream input(options.path);
    if (!input) {
        throw VerificationError("cannot open certificate file: " +
                                options.path);
    }
    return read_certificate(input, options.path, options.modulus);
}

void verify_and_report(const Certificate& certificate) {
    const std::vector<int> holes = validate_even_starter(certificate);
    const std::vector<Matching> factors =
        develop_factorisation(certificate, holes);
    const std::size_t edge_count = validate_edge_partition(factors);
    const HamiltonCheckSummary hamilton =
        validate_hamilton_unions(factors, certificate.modulus);

    std::cout << "CERT source=\"" << certificate.source << "\" modulus="
              << certificate.modulus << " order=" << certificate.modulus + 2
              << " pairs=" << certificate.pairs.size() << " holes="
              << holes[0] << ',' << holes[1] << '\n';
    std::cout << "EVEN_STARTER PASS differences="
              << certificate.modulus / 2 - 1 << '\n';
    std::cout << "EDGE_PARTITION PASS factors=" << factors.size()
              << " edges=" << edge_count << '\n';
    std::cout << "REDUCED_ORBITS PASS checks=" << hamilton.reduced_checks
              << '\n';
    std::cout << "FULL_P1F PASS factor_pairs=" << hamilton.full_checks
              << '\n';
    std::cout << "RESULT PASS\n";
}

}  // namespace

int main(const int argc, char* argv[]) {
    try {
        const Options options = parse_options(argc, argv);
        if (options.help) {
            print_usage(argv[0]);
            return 0;
        }
        verify_and_report(load_certificate(options));
        return 0;
    } catch (const VerificationError& error) {
        std::cerr << "RESULT FAIL: " << error.what() << '\n';
        return 1;
    } catch (const std::exception& error) {
        std::cerr << "RESULT ERROR: " << error.what() << '\n';
        return 2;
    }
}
