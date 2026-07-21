#include <boost/multiprecision/cpp_int.hpp>

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <optional>
#include <sstream>
#include <string>
#include <thread>
#include <unordered_map>
#include <utility>
#include <vector>

#ifndef _WIN32
#include <sys/wait.h>
#endif

using boost::multiprecision::cpp_int;

namespace {

using u64 = std::uint64_t;
using u128 = unsigned __int128;

constexpr int kMaximumSupportedP = 32767;

struct Fraction {
    u64 numerator = 0;
    u64 denominator = 1;

    bool operator==(const Fraction& other) const noexcept {
        return numerator == other.numerator && denominator == other.denominator;
    }
};

struct FractionHash {
    std::size_t operator()(const Fraction& value) const noexcept {
        const std::size_t first = std::hash<u64>{}(value.numerator);
        const std::size_t second = std::hash<u64>{}(value.denominator);
        return first ^ (second + 0x9e3779b97f4a7c15ULL + (first << 6U) +
                        (first >> 2U));
    }
};

struct PairData {
    int p = 0;
    int q = 0;
    u64 h = 0;
    std::int64_t u = 0;
    std::int64_t v = 0;
    Fraction f;
};

struct Identity {
    std::array<std::size_t, 4> indices{};  // f1, f2, f3, f4
    bool candidate_valid = false;
};

struct Candidate {
    Identity identity;
    cpp_int m;
    cpp_int b;
    cpp_int c;
    std::array<cpp_int, 8> roots{};
    std::array<cpp_int, 9> matrix{};
};

struct Options {
    int p_min = 2;
    int p_max = 0;
    unsigned int threads = 1;
    double time_limit_seconds = 0.0;
    bool emit_identities = false;
    bool emit_values = false;
    std::filesystem::path output;
    std::filesystem::path scalar_verifier;
    std::filesystem::path independent_verifier;
    std::filesystem::path verification_dir = "s_lane_verification";
    std::string python = "python";
};

struct ThreadResult {
    u64 pair_comparisons = 0;
    u64 identity_count = 0;
    std::vector<Identity> identities;
    std::vector<Candidate> candidates;
};

struct VerificationResult {
    int scalar_exit = -1;
    int independent_exit = -1;
    std::filesystem::path candidate_path;
    std::filesystem::path scalar_output_path;
    std::filesystem::path scalar_error_path;
    std::filesystem::path independent_output_path;
    std::filesystem::path independent_error_path;
    std::string scalar_output;
    std::string independent_output;

    bool accepted() const {
        return scalar_exit == 0 && independent_exit == 0;
    }
};

u128 gcd128(u128 left, u128 right) {
    while (right != 0) {
        const u128 remainder = left % right;
        left = right;
        right = remainder;
    }
    return left;
}

bool fits_u64(u128 value) {
    return value <= static_cast<u128>(std::numeric_limits<u64>::max());
}

u64 to_u64(u128 value) {
    return static_cast<u64>(value);
}

Fraction reduced_fraction(u128 numerator, u128 denominator) {
    const u128 divisor = gcd128(numerator, denominator);
    numerator /= divisor;
    denominator /= divisor;
    if (!fits_u64(numerator) || !fits_u64(denominator)) {
        throw std::overflow_error("reduced fraction exceeds 64-bit storage");
    }
    return {to_u64(numerator), to_u64(denominator)};
}

std::optional<Fraction> reduced_fraction_if_storable(u128 numerator,
                                                     u128 denominator) {
    const u128 divisor = gcd128(numerator, denominator);
    numerator /= divisor;
    denominator /= divisor;
    if (!fits_u64(numerator) || !fits_u64(denominator)) {
        return std::nullopt;
    }
    return Fraction{to_u64(numerator), to_u64(denominator)};
}

bool fraction_less(const Fraction& left, const Fraction& right) {
    return static_cast<u128>(left.numerator) * right.denominator <
           static_cast<u128>(right.numerator) * left.denominator;
}

bool fraction_sum_at_least_one(const Fraction& left,
                               const Fraction& right) {
    const u128 numerator =
        static_cast<u128>(left.numerator) * right.denominator +
        static_cast<u128>(right.numerator) * left.denominator;
    const u128 denominator =
        static_cast<u128>(left.denominator) * right.denominator;
    return numerator >= denominator;
}

std::optional<Fraction> fraction_sum(const Fraction& left,
                                     const Fraction& right) {
    const u128 numerator =
        static_cast<u128>(left.numerator) * right.denominator +
        static_cast<u128>(right.numerator) * left.denominator;
    const u128 denominator =
        static_cast<u128>(left.denominator) * right.denominator;
    return reduced_fraction_if_storable(numerator, denominator);
}

std::optional<Fraction> fraction_difference(const Fraction& larger,
                                            const Fraction& smaller) {
    const u128 numerator =
        static_cast<u128>(larger.numerator) * smaller.denominator -
        static_cast<u128>(smaller.numerator) * larger.denominator;
    const u128 denominator =
        static_cast<u128>(larger.denominator) * smaller.denominator;
    return reduced_fraction_if_storable(numerator, denominator);
}

std::string fraction_text(const Fraction& value) {
    return std::to_string(value.numerator) + "/" +
           std::to_string(value.denominator);
}

std::string decimal(const cpp_int& value) {
    std::ostringstream output;
    output << value;
    return output.str();
}

cpp_int gcd_cpp(cpp_int left, cpp_int right) {
    if (left < 0) {
        left = -left;
    }
    if (right < 0) {
        right = -right;
    }
    while (right != 0) {
        const cpp_int remainder = left % right;
        left = right;
        right = remainder;
    }
    return left;
}

cpp_int lcm_cpp(const cpp_int& left, const cpp_int& right) {
    return left / gcd_cpp(left, right) * right;
}

std::string json_escape(const std::string& text) {
    std::ostringstream output;
    for (const unsigned char ch : text) {
        switch (ch) {
            case '\"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\b': output << "\\b"; break;
            case '\f': output << "\\f"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (ch < 0x20U) {
                    static constexpr char digits[] = "0123456789abcdef";
                    output << "\\u00" << digits[(ch >> 4U) & 0x0fU]
                           << digits[ch & 0x0fU];
                } else {
                    output << static_cast<char>(ch);
                }
        }
    }
    return output.str();
}

std::string read_file(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        return {};
    }
    std::ostringstream output;
    output << input.rdbuf();
    return output.str();
}

std::string shell_quote(const std::string& text) {
    std::string escaped;
    escaped.reserve(text.size() + 2U);
    escaped.push_back('\"');
    for (const char ch : text) {
        if (ch == '\"') {
            escaped += "\\\"";
        } else {
            escaped.push_back(ch);
        }
    }
    escaped.push_back('\"');
    return escaped;
}

std::string shell_quote(const std::filesystem::path& path) {
    return shell_quote(path.string());
}

int normalized_system_exit(int status) {
    if (status < 0) {
        return status;
    }
#ifdef _WIN32
    return status;
#else
    if (WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }
    return status;
#endif
}

bool pair_lex_less(const PairData& left, const PairData& right) {
    return std::pair<int, int>{left.p, left.q} <
           std::pair<int, int>{right.p, right.q};
}

std::pair<std::vector<PairData>, u64> generate_values(int p_max) {
    std::unordered_map<Fraction, PairData, FractionHash> unique;
    u64 generated = 0;

    for (int p = 2; p <= p_max; ++p) {
        for (int q = 1; q < p; ++q) {
            if (std::gcd(p, q) != 1 || ((p - q) & 1) == 0) {
                continue;
            }
            ++generated;
            const u64 p2 = static_cast<u64>(p) * p;
            const u64 q2 = static_cast<u64>(q) * q;
            const u64 h = p2 + q2;
            const std::int64_t u =
                static_cast<std::int64_t>(p2) -
                2LL * static_cast<std::int64_t>(p) * q -
                static_cast<std::int64_t>(q2);
            const std::int64_t v =
                static_cast<std::int64_t>(p2) +
                2LL * static_cast<std::int64_t>(p) * q -
                static_cast<std::int64_t>(q2);
            const u128 numerator =
                static_cast<u128>(4) * p * q * (p2 - q2);
            const u128 denominator = static_cast<u128>(h) * h;
            const u128 u_square = static_cast<u128>(u < 0 ? -u : u) *
                                  static_cast<u128>(u < 0 ? -u : u);
            const u128 v_square = static_cast<u128>(v) * v;
            if (u_square != denominator - numerator ||
                v_square != denominator + numerator) {
                throw std::logic_error("structural f identity failed");
            }
            const Fraction f = reduced_fraction(numerator, denominator);
            const PairData pair{p, q, h, u, v, f};
            auto iterator = unique.find(f);
            if (iterator == unique.end()) {
                unique.emplace(f, pair);
            } else if (pair_lex_less(pair, iterator->second)) {
                iterator->second = pair;
            }
        }
    }

    std::vector<PairData> values;
    values.reserve(unique.size());
    for (const auto& item : unique) {
        values.push_back(item.second);
    }
    std::sort(values.begin(), values.end(), [](const PairData& left,
                                               const PairData& right) {
        if (left.f == right.f) {
            return pair_lex_less(left, right);
        }
        return fraction_less(left.f, right.f);
    });
    return {std::move(values), generated};
}

int identity_max_p(const Identity& identity,
                   const std::vector<PairData>& values) {
    int result = 0;
    for (const std::size_t index : identity.indices) {
        result = std::max(result, values[index].p);
    }
    return result;
}

std::array<int, 8> identity_pair_key(const Identity& identity,
                                     const std::vector<PairData>& values) {
    std::array<int, 8> result{};
    for (std::size_t i = 0; i < identity.indices.size(); ++i) {
        result[2U * i] = values[identity.indices[i]].p;
        result[2U * i + 1U] = values[identity.indices[i]].q;
    }
    return result;
}

std::string identity_key(const Identity& identity,
                         const std::vector<PairData>& values) {
    std::ostringstream output;
    for (std::size_t i = 0; i < identity.indices.size(); ++i) {
        if (i != 0) {
            output << ';';
        }
        const PairData& pair = values[identity.indices[i]];
        output << pair.p << ',' << pair.q;
    }
    return output.str();
}

std::optional<Candidate> reconstruct_candidate(
    const Identity& identity,
    const std::vector<PairData>& values) {
    cpp_int m = 1;
    for (const std::size_t index : identity.indices) {
        const PairData& pair = values[index];
        const u64 absolute_u = static_cast<u64>(pair.u < 0 ? -pair.u : pair.u);
        const u64 lower_denominator = pair.h / std::gcd(pair.h, absolute_u);
        const u64 upper_denominator =
            pair.h / std::gcd(pair.h, static_cast<u64>(pair.v));
        m = lcm_cpp(m, cpp_int(lower_denominator));
        m = lcm_cpp(m, cpp_int(upper_denominator));
    }

    std::array<cpp_int, 8> roots{};
    for (std::size_t i = 0; i < identity.indices.size(); ++i) {
        const PairData& pair = values[identity.indices[i]];
        const u64 absolute_u = static_cast<u64>(pair.u < 0 ? -pair.u : pair.u);
        roots[2U * i] = m * absolute_u / pair.h;
        roots[2U * i + 1U] = m * pair.v / pair.h;
        if (roots[2U * i] == 0 || roots[2U * i + 1U] == 0) {
            return std::nullopt;
        }
    }

    const Fraction& first = values[identity.indices[0]].f;
    const Fraction& second = values[identity.indices[1]].f;
    cpp_int b = m * m * first.numerator / first.denominator;
    cpp_int c = m * m * second.numerator / second.denominator;

    cpp_int primitive_gcd = m;
    for (const cpp_int& root : roots) {
        primitive_gcd = gcd_cpp(primitive_gcd, root);
    }
    if (primitive_gcd > 1) {
        const cpp_int square_gcd = primitive_gcd * primitive_gcd;
        if (b % square_gcd != 0 || c % square_gcd != 0) {
            throw std::logic_error("primitive MSQ-D division is not exact");
        }
        m /= primitive_gcd;
        b /= square_gcd;
        c /= square_gcd;
        for (cpp_int& root : roots) {
            root /= primitive_gcd;
        }
    }

    if (m <= 0 || b <= c || c <= 0) {
        return std::nullopt;
    }
    const cpp_int center = m * m;
    std::array<cpp_int, 9> matrix = {
        center - b,
        center + b + c,
        center - c,
        center + b - c,
        center,
        center - b + c,
        center + c,
        center - b - c,
        center + b,
    };

    for (const cpp_int& value : matrix) {
        if (value <= 0) {
            return std::nullopt;
        }
    }
    for (std::size_t i = 0; i < matrix.size(); ++i) {
        for (std::size_t j = i + 1; j < matrix.size(); ++j) {
            if (matrix[i] == matrix[j]) {
                return std::nullopt;
            }
        }
    }

    const std::array<cpp_int, 9> square_from_roots = {
        roots[0] * roots[0],
        roots[5] * roots[5],
        roots[2] * roots[2],
        roots[7] * roots[7],
        m * m,
        roots[6] * roots[6],
        roots[3] * roots[3],
        roots[4] * roots[4],
        roots[1] * roots[1],
    };
    if (matrix != square_from_roots) {
        throw std::logic_error("reconstructed roots do not match B2 matrix");
    }

    static constexpr std::array<std::array<int, 3>, 8> lines = {{
        {{0, 1, 2}}, {{3, 4, 5}}, {{6, 7, 8}}, {{0, 3, 6}},
        {{1, 4, 7}}, {{2, 5, 8}}, {{0, 4, 8}}, {{2, 4, 6}},
    }};
    const auto line_sum = [&matrix](const std::array<int, 3>& line) {
        return matrix[static_cast<std::size_t>(line[0])] +
               matrix[static_cast<std::size_t>(line[1])] +
               matrix[static_cast<std::size_t>(line[2])];
    };
    const cpp_int expected = line_sum(lines[0]);
    for (const auto& line : lines) {
        if (line_sum(line) != expected) {
            throw std::logic_error("B2 matrix line-sum identity failed");
        }
    }

    return Candidate{identity, m, b, c, roots, matrix};
}

VerificationResult run_verifiers(const Candidate& candidate,
                                 std::size_t ordinal,
                                 const Options& options) {
    std::filesystem::create_directories(options.verification_dir);
    const std::string stem = "candidate_" + std::to_string(ordinal);
    VerificationResult result;
    result.candidate_path = options.verification_dir / (stem + ".txt");
    result.scalar_output_path =
        options.verification_dir / (stem + ".scalar.json");
    result.scalar_error_path =
        options.verification_dir / (stem + ".scalar.stderr.txt");
    result.independent_output_path =
        options.verification_dir / (stem + ".independent.json");
    result.independent_error_path =
        options.verification_dir / (stem + ".independent.stderr.txt");

    {
        std::ofstream output(result.candidate_path, std::ios::binary);
        if (!output) {
            throw std::runtime_error("cannot create verifier candidate file");
        }
        for (std::size_t i = 0; i < candidate.matrix.size(); ++i) {
            if (i != 0) {
                output << ' ';
            }
            output << candidate.matrix[i];
        }
        output << '\n';
    }

    const std::string scalar_command =
        shell_quote(options.python) + " " + shell_quote(options.scalar_verifier) +
        " --msq-d " + shell_quote(decimal(candidate.m)) + " " +
        shell_quote(decimal(candidate.b)) + " " +
        shell_quote(decimal(candidate.c)) + " > " +
        shell_quote(result.scalar_output_path) + " 2> " +
        shell_quote(result.scalar_error_path);
    result.scalar_exit = normalized_system_exit(std::system(scalar_command.c_str()));

    const std::string independent_command =
        shell_quote(options.independent_verifier) + " --file " +
        shell_quote(result.candidate_path) + " > " +
        shell_quote(result.independent_output_path) + " 2> " +
        shell_quote(result.independent_error_path);
    result.independent_exit =
        normalized_system_exit(std::system(independent_command.c_str()));
    result.scalar_output = read_file(result.scalar_output_path);
    result.independent_output = read_file(result.independent_output_path);
    return result;
}

void emit_value(std::ostream& output, const PairData& pair) {
    output << "{\"fraction\":\"" << fraction_text(pair.f)
           << "\",\"h\":" << pair.h << ",\"pair\":[" << pair.p << ','
           << pair.q << "],\"type\":\"value\",\"u\":" << pair.u
           << ",\"v\":" << pair.v << "}\n";
}

void emit_identity(std::ostream& output,
                   const Identity& identity,
                   const std::vector<PairData>& values) {
    output << "{\"candidate_valid\":"
           << (identity.candidate_valid ? "true" : "false")
           << ",\"fractions\":[";
    for (std::size_t i = 0; i < identity.indices.size(); ++i) {
        if (i != 0) {
            output << ',';
        }
        output << '\"' << fraction_text(values[identity.indices[i]].f) << '\"';
    }
    output << "],\"key\":\"" << identity_key(identity, values)
           << "\",\"max_p\":" << identity_max_p(identity, values)
           << ",\"pairs\":[";
    for (std::size_t i = 0; i < identity.indices.size(); ++i) {
        if (i != 0) {
            output << ',';
        }
        const PairData& pair = values[identity.indices[i]];
        output << '[' << pair.p << ',' << pair.q << ']';
    }
    output << "],\"type\":\"identity\"}\n";
}

void emit_candidate(std::ostream& output,
                    const Candidate& candidate,
                    const VerificationResult& verification,
                    const std::vector<PairData>& values) {
    output << "{\"independent_verifier\":{\"accepted\":"
           << (verification.independent_exit == 0 ? "true" : "false")
           << ",\"exit_code\":" << verification.independent_exit
           << ",\"output\":\"" << json_escape(verification.independent_output)
           << "\",\"output_path\":\""
           << json_escape(verification.independent_output_path.string())
           << "\"},\"key\":\"" << identity_key(candidate.identity, values)
           << "\",\"matrix\":[";
    for (std::size_t row = 0; row < 3; ++row) {
        if (row != 0) {
            output << ',';
        }
        output << '[';
        for (std::size_t column = 0; column < 3; ++column) {
            if (column != 0) {
                output << ',';
            }
            output << '\"' << decimal(candidate.matrix[3U * row + column]) << '\"';
        }
        output << ']';
    }
    output << "],\"msq_d\":{\"b\":\"" << decimal(candidate.b)
           << "\",\"c\":\"" << decimal(candidate.c) << "\",\"m\":\""
           << decimal(candidate.m) << "\"},\"roots\":[";
    for (std::size_t i = 0; i < candidate.roots.size(); ++i) {
        if (i != 0) {
            output << ',';
        }
        output << '\"' << decimal(candidate.roots[i]) << '\"';
    }
    output << "],\"scalar_verifier\":{\"accepted\":"
           << (verification.scalar_exit == 0 ? "true" : "false")
           << ",\"exit_code\":" << verification.scalar_exit
           << ",\"output\":\"" << json_escape(verification.scalar_output)
           << "\",\"output_path\":\""
           << json_escape(verification.scalar_output_path.string())
           << "\"},\"type\":\"candidate\",\"verified\":"
           << (verification.accepted() ? "true" : "false") << "}\n";
}

bool parse_integer(const std::string& text, int& value) {
    try {
        std::size_t used = 0;
        const long long parsed = std::stoll(text, &used, 10);
        if (used != text.size() || parsed < std::numeric_limits<int>::min() ||
            parsed > std::numeric_limits<int>::max()) {
            return false;
        }
        value = static_cast<int>(parsed);
        return true;
    } catch (...) {
        return false;
    }
}

bool parse_unsigned(const std::string& text, unsigned int& value) {
    int parsed = 0;
    if (!parse_integer(text, parsed) || parsed < 0) {
        return false;
    }
    value = static_cast<unsigned int>(parsed);
    return true;
}

bool parse_double(const std::string& text, double& value) {
    try {
        std::size_t used = 0;
        value = std::stod(text, &used);
        return used == text.size() && value >= 0.0;
    } catch (...) {
        return false;
    }
}

void print_usage(std::ostream& output) {
    output << "usage: s_lane_search --p-max N [--p-min N] [--threads N] "
              "[--time-limit-seconds S] [--emit-identities] [--emit-values] [--output FILE] "
              "[--scalar FILE] [--independent FILE] [--python EXE] "
              "[--verification-dir DIR]\n";
}

std::optional<Options> parse_options(int argc, char* argv[]) {
    Options options;
    const std::filesystem::path executable =
        std::filesystem::absolute(argv[0]).parent_path();
    options.scalar_verifier = executable / "verify_scalar.py";
    options.independent_verifier = executable / "verify_independent.exe";

    for (int index = 1; index < argc; ++index) {
        const std::string argument = argv[index];
        const auto require_value = [&]() -> std::optional<std::string> {
            if (index + 1 >= argc) {
                return std::nullopt;
            }
            return std::string(argv[++index]);
        };

        if (argument == "--emit-identities") {
            options.emit_identities = true;
        } else if (argument == "--emit-values") {
            options.emit_values = true;
        } else if (argument == "--p-min") {
            const auto value = require_value();
            if (!value || !parse_integer(*value, options.p_min)) return std::nullopt;
        } else if (argument == "--p-max") {
            const auto value = require_value();
            if (!value || !parse_integer(*value, options.p_max)) return std::nullopt;
        } else if (argument == "--threads") {
            const auto value = require_value();
            if (!value || !parse_unsigned(*value, options.threads)) return std::nullopt;
        } else if (argument == "--time-limit-seconds") {
            const auto value = require_value();
            if (!value || !parse_double(*value, options.time_limit_seconds)) return std::nullopt;
        } else if (argument == "--output") {
            const auto value = require_value();
            if (!value) return std::nullopt;
            options.output = *value;
        } else if (argument == "--scalar") {
            const auto value = require_value();
            if (!value) return std::nullopt;
            options.scalar_verifier = *value;
        } else if (argument == "--independent") {
            const auto value = require_value();
            if (!value) return std::nullopt;
            options.independent_verifier = *value;
        } else if (argument == "--python") {
            const auto value = require_value();
            if (!value) return std::nullopt;
            options.python = *value;
        } else if (argument == "--verification-dir") {
            const auto value = require_value();
            if (!value) return std::nullopt;
            options.verification_dir = *value;
        } else if (argument == "--help" || argument == "-h") {
            print_usage(std::cout);
            std::exit(0);
        } else {
            return std::nullopt;
        }
    }

    if (options.p_min < 2 || options.p_max < options.p_min ||
        options.p_max > kMaximumSupportedP || options.threads == 0 ||
        options.threads > 64) {
        return std::nullopt;
    }
    return options;
}

}  // namespace

int main(int argc, char* argv[]) {
    const std::optional<Options> parsed = parse_options(argc, argv);
    if (!parsed) {
        print_usage(std::cerr);
        return 2;
    }
    const Options options = *parsed;

    try {
        const auto start = std::chrono::steady_clock::now();
        const auto generated_result = generate_values(options.p_max);
        const std::vector<PairData>& values = generated_result.first;
        const u64 canonical_pair_count = generated_result.second;

        std::unordered_map<Fraction, std::size_t, FractionHash> lookup;
        lookup.reserve(values.size() * 2U + 1U);
        for (std::size_t index = 0; index < values.size(); ++index) {
            lookup.emplace(values[index].f, index);
        }

        std::atomic<std::size_t> next_index{1};
        std::atomic<bool> stop_requested{false};
        std::atomic<bool> timed_out{false};
        std::atomic<bool> candidate_found{false};
        const auto deadline = start +
            std::chrono::duration_cast<std::chrono::steady_clock::duration>(
                std::chrono::duration<double>(options.time_limit_seconds));
        std::vector<ThreadResult> thread_results(options.threads);
        std::vector<std::thread> workers;
        workers.reserve(options.threads);

        for (unsigned int thread_index = 0; thread_index < options.threads;
             ++thread_index) {
            workers.emplace_back([&, thread_index]() {
                ThreadResult& result = thread_results[thread_index];
                while (!stop_requested.load(std::memory_order_relaxed)) {
                    const std::size_t i =
                        next_index.fetch_add(1, std::memory_order_relaxed);
                    if (i >= values.size()) {
                        break;
                    }
                    if (options.time_limit_seconds > 0.0 &&
                        std::chrono::steady_clock::now() >= deadline) {
                        timed_out.store(true, std::memory_order_relaxed);
                        stop_requested.store(true, std::memory_order_relaxed);
                        break;
                    }

                    const PairData& first = values[i];
                    for (std::size_t j = 0; j < i; ++j) {
                        if ((result.pair_comparisons & 0xffffULL) == 0ULL &&
                            options.time_limit_seconds > 0.0 &&
                            std::chrono::steady_clock::now() >= deadline) {
                            timed_out.store(true, std::memory_order_relaxed);
                            stop_requested.store(true, std::memory_order_relaxed);
                            break;
                        }
                        const PairData& second = values[j];
                        if (fraction_sum_at_least_one(first.f, second.f)) {
                            break;
                        }
                        ++result.pair_comparisons;
                        const std::optional<Fraction> total =
                            fraction_sum(first.f, second.f);
                        if (!total) {
                            continue;
                        }
                        const auto third_iterator = lookup.find(*total);
                        if (third_iterator == lookup.end()) {
                            continue;
                        }
                        const std::optional<Fraction> difference =
                            fraction_difference(first.f, second.f);
                        if (!difference) {
                            continue;
                        }
                        const auto fourth_iterator = lookup.find(*difference);
                        if (fourth_iterator == lookup.end()) {
                            continue;
                        }

                        Identity identity{{i, j, third_iterator->second,
                                           fourth_iterator->second},
                                          false};
                        const int max_p = identity_max_p(identity, values);
                        if (max_p < options.p_min || max_p > options.p_max) {
                            continue;
                        }
                        ++result.identity_count;
                        std::optional<Candidate> candidate =
                            reconstruct_candidate(identity, values);
                        identity.candidate_valid = candidate.has_value();
                        if (options.emit_identities) {
                            result.identities.push_back(identity);
                        }
                        if (candidate) {
                            candidate->identity.candidate_valid = true;
                            result.candidates.push_back(std::move(*candidate));
                            candidate_found.store(true, std::memory_order_relaxed);
                            stop_requested.store(true, std::memory_order_relaxed);
                            break;
                        }
                    }
                }
            });
        }
        for (std::thread& worker : workers) {
            worker.join();
        }

        u64 pair_comparisons = 0;
        u64 identity_count = 0;
        std::vector<Identity> identities;
        std::vector<Candidate> candidates;
        for (ThreadResult& result : thread_results) {
            pair_comparisons += result.pair_comparisons;
            identity_count += result.identity_count;
            identities.insert(identities.end(), result.identities.begin(),
                              result.identities.end());
            candidates.insert(candidates.end(),
                              std::make_move_iterator(result.candidates.begin()),
                              std::make_move_iterator(result.candidates.end()));
        }
        const auto identity_less = [&values](const Identity& left,
                                             const Identity& right) {
            return identity_pair_key(left, values) <
                   identity_pair_key(right, values);
        };
        std::sort(identities.begin(), identities.end(), identity_less);
        std::sort(candidates.begin(), candidates.end(),
                  [&values](const Candidate& left, const Candidate& right) {
                      return identity_pair_key(left.identity, values) <
                             identity_pair_key(right.identity, values);
                  });

        std::ofstream output_file;
        std::ostream* output = &std::cout;
        if (!options.output.empty()) {
            output_file.open(options.output, std::ios::binary);
            if (!output_file) {
                throw std::runtime_error("cannot open output file");
            }
            output = &output_file;
        }

        if (options.emit_values) {
            for (const PairData& pair : values) {
                emit_value(*output, pair);
            }
        }
        if (options.emit_identities) {
            for (const Identity& identity : identities) {
                emit_identity(*output, identity, values);
            }
        }

        std::vector<VerificationResult> verifications;
        verifications.reserve(candidates.size());
        bool verified = false;
        for (std::size_t i = 0; i < candidates.size(); ++i) {
            verifications.push_back(run_verifiers(candidates[i], i, options));
            emit_candidate(*output, candidates[i], verifications.back(), values);
            verified = verified || verifications.back().accepted();
        }

        std::string status;
        int exit_code = 0;
        if (verified) {
            status = "SAT";
        } else if (candidate_found.load(std::memory_order_relaxed)) {
            status = "VERIFIER_FAILURE";
            exit_code = 4;
        } else if (timed_out.load(std::memory_order_relaxed)) {
            status = "TIMEOUT_INCOMPLETE";
        } else {
            status = "EXHAUSTED";
        }
        const double elapsed =
            std::chrono::duration<double>(std::chrono::steady_clock::now() - start)
                .count();
        *output << "{\"candidate_count\":" << candidates.size()
                << ",\"canonical_pair_count\":" << canonical_pair_count
                << ",\"elapsed_seconds\":" << elapsed
                << ",\"identity_count\":" << identity_count
                << ",\"implementation\":\"cpp_exact_hash_join\""
                << ",\"p_max\":" << options.p_max
                << ",\"p_min\":" << options.p_min
                << ",\"pair_comparisons\":" << pair_comparisons
                << ",\"status\":\"" << status << "\",\"threads\":"
                << options.threads << ",\"type\":\"summary\""
                << ",\"unique_f_count\":" << values.size()
                << ",\"verified_candidate_count\":"
                << (verified ? 1 : 0) << "}\n";
        return exit_code;
    } catch (const std::exception& error) {
        std::cerr << "s_lane_search: " << error.what() << '\n';
        return 3;
    }
}
