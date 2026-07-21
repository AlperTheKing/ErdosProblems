#include <boost/multiprecision/cpp_int.hpp>

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#else
#include <sys/wait.h>
#endif

using boost::multiprecision::cpp_int;
namespace fs = std::filesystem;

namespace {

constexpr std::int64_t MANIFEST_MAX_X = 1LL << 20;
constexpr int MANIFEST_MAX_KAPPA = 1024;
constexpr int MAX_CHUNKS = 64;
constexpr double MAX_WALL_SECONDS = 8.0 * 60.0 * 60.0;

struct RootFraction {
    std::uint64_t numerator = 0;
    std::uint64_t denominator = 1;
};

cpp_int abs_cpp(cpp_int value) {
    return value < 0 ? -value : value;
}

cpp_int gcd_cpp(cpp_int a, cpp_int b) {
    a = abs_cpp(a);
    b = abs_cpp(b);
    while (b != 0) {
        cpp_int remainder = a % b;
        a = b;
        b = remainder;
    }
    return a;
}

cpp_int lcm_cpp(const cpp_int& a, const cpp_int& b) {
    if (a == 0 || b == 0) {
        return 0;
    }
    return abs_cpp((a / gcd_cpp(a, b)) * b);
}

std::string decimal(const cpp_int& value) {
    std::ostringstream out;
    out << value;
    return out.str();
}

struct BigRational {
    cpp_int numerator = 0;
    cpp_int denominator = 1;

    BigRational() = default;
    BigRational(cpp_int n, cpp_int d) : numerator(std::move(n)), denominator(std::move(d)) {
        normalize();
    }

    void normalize() {
        if (denominator == 0) {
            throw std::runtime_error("zero rational denominator");
        }
        if (denominator < 0) {
            numerator = -numerator;
            denominator = -denominator;
        }
        const cpp_int divisor = gcd_cpp(numerator, denominator);
        if (divisor != 0) {
            numerator /= divisor;
            denominator /= divisor;
        }
    }

    std::string key() const {
        return decimal(numerator) + "/" + decimal(denominator);
    }
};

BigRational operator+(const BigRational& lhs, const BigRational& rhs) {
    return BigRational(
        lhs.numerator * rhs.denominator + rhs.numerator * lhs.denominator,
        lhs.denominator * rhs.denominator);
}

BigRational operator-(const BigRational& lhs, const BigRational& rhs) {
    return BigRational(
        lhs.numerator * rhs.denominator - rhs.numerator * lhs.denominator,
        lhs.denominator * rhs.denominator);
}

BigRational half(const BigRational& value) {
    return BigRational(value.numerator, value.denominator * 2);
}

bool operator==(const BigRational& lhs, const BigRational& rhs) {
    return lhs.numerator == rhs.numerator && lhs.denominator == rhs.denominator;
}

BigRational square_fraction(const RootFraction& root) {
    const cpp_int n = cpp_int(root.numerator) * root.numerator;
    const cpp_int d = cpp_int(root.denominator) * root.denominator;
    return BigRational(n, d);
}

std::uint64_t abs_i128(__int128 value) {
    const unsigned __int128 magnitude =
        value < 0 ? static_cast<unsigned __int128>(-value)
                  : static_cast<unsigned __int128>(value);
    if (magnitude > std::numeric_limits<std::uint64_t>::max()) {
        throw std::runtime_error("manifest arithmetic exceeded uint64 range");
    }
    return static_cast<std::uint64_t>(magnitude);
}

RootFraction reduced_root(__int128 signed_numerator, std::uint64_t denominator) {
    const std::uint64_t numerator = abs_i128(signed_numerator);
    if (numerator == 0 || denominator == 0) {
        return {0, 1};
    }
    const std::uint64_t divisor = std::gcd(numerator, denominator);
    return {numerator / divisor, denominator / divisor};
}

std::uint64_t isqrt_u64(std::uint64_t value) {
    if (value == 0) {
        return 0;
    }
    std::uint64_t estimate = static_cast<std::uint64_t>(
        std::sqrt(static_cast<long double>(value)));
    while (static_cast<unsigned __int128>(estimate) * estimate > value) {
        --estimate;
    }
    while (estimate < std::numeric_limits<std::uint64_t>::max() &&
           static_cast<unsigned __int128>(estimate + 1) * (estimate + 1) <= value) {
        ++estimate;
    }
    return estimate;
}

cpp_int isqrt_cpp(const cpp_int& value) {
    if (value <= 0) {
        return 0;
    }
    const unsigned int bits = static_cast<unsigned int>(boost::multiprecision::msb(value)) + 1U;
    cpp_int estimate = cpp_int(1) << ((bits + 1U) / 2U);
    for (;;) {
        const cpp_int next = (estimate + value / estimate) >> 1;
        if (next >= estimate) {
            break;
        }
        estimate = next;
    }
    while (estimate * estimate > value) {
        --estimate;
    }
    while ((estimate + 1) * (estimate + 1) <= value) {
        ++estimate;
    }
    return estimate;
}

bool exact_square_cpp(const cpp_int& value, cpp_int& root) {
    if (value <= 0) {
        return false;
    }
    root = isqrt_cpp(value);
    return root * root == value;
}

bool is_squarefree(int value) {
    if (value <= 0) {
        return false;
    }
    for (int prime = 2; static_cast<long long>(prime) * prime <= value; ++prime) {
        const int square = prime * prime;
        if (value % square == 0) {
            return false;
        }
    }
    return true;
}

struct PointRecord {
    int kappa = 0;
    std::int64_t x = 0;
    std::uint64_t y = 0;
    RootFraction root_minus;
    RootFraction root_center;
    RootFraction root_plus;

    BigRational doubled_x() const {
        return square_fraction(root_center);
    }

    std::string doubled_x_key() const {
        return std::to_string(root_center.numerator) + "/" +
               std::to_string(root_center.denominator);
    }
};

std::optional<PointRecord> make_point_record(int kappa,
                                             std::int64_t x,
                                             std::uint64_t y) {
    const __int128 xx = x;
    const __int128 kk = kappa;
    const __int128 x_squared = xx * xx;
    const std::uint64_t denominator = 2 * y;
    const RootFraction center = reduced_root(x_squared + kk * kk, denominator);
    const RootFraction minus = reduced_root(x_squared - 2 * kk * xx - kk * kk, denominator);
    const RootFraction plus = reduced_root(x_squared + 2 * kk * xx - kk * kk, denominator);
    if (center.numerator == 0 || minus.numerator == 0 || plus.numerator == 0) {
        return std::nullopt;
    }

    const BigRational X = square_fraction(center);
    const BigRational expected_minus = X - BigRational(kappa, 1);
    const BigRational expected_plus = X + BigRational(kappa, 1);
    if (!(square_fraction(minus) == expected_minus) ||
        !(square_fraction(plus) == expected_plus) || expected_minus.numerator <= 0) {
        throw std::runtime_error("doubling root identity failed");
    }

    return PointRecord{kappa, x, y, minus, center, plus};
}

bool root_less(const RootFraction& lhs, const RootFraction& rhs) {
    return static_cast<unsigned __int128>(lhs.numerator) * rhs.denominator <
           static_cast<unsigned __int128>(rhs.numerator) * lhs.denominator;
}

std::string json_escape(const std::string& value) {
    std::ostringstream out;
    for (const unsigned char ch : value) {
        switch (ch) {
            case '\\': out << "\\\\"; break;
            case '"': out << "\\\""; break;
            case '\n': out << "\\n"; break;
            case '\r': out << "\\r"; break;
            case '\t': out << "\\t"; break;
            default:
                if (ch < 0x20) {
                    out << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                        << static_cast<int>(ch) << std::dec << std::setfill(' ');
                } else {
                    out << static_cast<char>(ch);
                }
        }
    }
    return out.str();
}

std::string utc_now() {
    const auto now = std::chrono::system_clock::now();
    const std::time_t time = std::chrono::system_clock::to_time_t(now);
    std::tm utc{};
#ifdef _WIN32
    gmtime_s(&utc, &time);
#else
    gmtime_r(&time, &utc);
#endif
    std::ostringstream out;
    out << std::put_time(&utc, "%Y-%m-%dT%H:%M:%SZ");
    return out.str();
}

void atomic_write(const fs::path& destination, const std::string& contents) {
    fs::create_directories(destination.parent_path());
    const auto nonce = std::chrono::high_resolution_clock::now().time_since_epoch().count();
    fs::path temporary = destination;
    temporary += ".tmp-" + std::to_string(nonce);
    {
        std::ofstream output(temporary, std::ios::binary | std::ios::trunc);
        if (!output) {
            throw std::runtime_error("cannot open temporary output " + temporary.string());
        }
        output.write(contents.data(), static_cast<std::streamsize>(contents.size()));
        output.flush();
        if (!output) {
            throw std::runtime_error("cannot flush temporary output " + temporary.string());
        }
    }
#ifdef _WIN32
    if (!MoveFileExW(temporary.wstring().c_str(), destination.wstring().c_str(),
                     MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
        const DWORD code = GetLastError();
        std::error_code ignored;
        fs::remove(temporary, ignored);
        throw std::runtime_error("atomic MoveFileEx failed with code " + std::to_string(code));
    }
#else
    std::error_code error;
    fs::rename(temporary, destination, error);
    if (error) {
        fs::remove(temporary);
        throw std::runtime_error("atomic rename failed: " + error.message());
    }
#endif
}

std::string shell_quote(const fs::path& path) {
    std::string value = path.string();
    std::string escaped;
    escaped.reserve(value.size() + 2);
    escaped.push_back('"');
    for (const char ch : value) {
        if (ch == '"') {
            escaped += "\\\"";
        } else {
            escaped.push_back(ch);
        }
    }
    escaped.push_back('"');
    return escaped;
}

std::string shell_quote_text(const std::string& value) {
    return shell_quote(fs::path(value));
}

int normalized_system_exit(int raw) {
    if (raw < 0) {
        return raw;
    }
#ifdef _WIN32
    return raw;
#else
    if (WIFEXITED(raw)) {
        return WEXITSTATUS(raw);
    }
    return raw;
#endif
}

struct Candidate {
    cpp_int m;
    cpp_int b;
    cpp_int c;
    cpp_int clearing_denominator;
    cpp_int primitive_gcd;
    std::array<cpp_int, 9> matrix;
    std::array<cpp_int, 9> roots;
    std::array<PointRecord, 3> points;
};

std::optional<Candidate> reconstruct_candidate(const PointRecord& low,
                                               const PointRecord& middle,
                                               const PointRecord& high) {
    const std::array<RootFraction, 9> rational_roots = {{
        low.root_center, high.root_plus, middle.root_minus,
        high.root_minus, middle.root_center, low.root_plus,
        middle.root_plus, low.root_minus, high.root_center,
    }};

    cpp_int clearing = 1;
    for (const RootFraction& root : rational_roots) {
        clearing = lcm_cpp(clearing, cpp_int(root.denominator));
    }

    std::array<cpp_int, 9> roots{};
    for (std::size_t index = 0; index < rational_roots.size(); ++index) {
        roots[index] = (clearing / rational_roots[index].denominator) *
                       rational_roots[index].numerator;
        if (roots[index] <= 0) {
            return std::nullopt;
        }
    }

    cpp_int primitive = 0;
    for (const cpp_int& root : roots) {
        primitive = gcd_cpp(primitive, root);
    }
    if (primitive <= 0) {
        return std::nullopt;
    }
    for (cpp_int& root : roots) {
        root /= primitive;
    }

    const cpp_int m = roots[4];
    const cpp_int center = m * m;
    cpp_int b = center - roots[0] * roots[0];
    cpp_int c = center - roots[2] * roots[2];
    if (b <= 0 || c <= 0 || b == c) {
        return std::nullopt;
    }
    if (b < c) {
        std::swap(b, c);
    }

    std::array<cpp_int, 9> matrix = {{
        center - b, center + b + c, center - c,
        center + b - c, center, center - b + c,
        center + c, center - b - c, center + b,
    }};
    std::array<cpp_int, 9> canonical_roots{};
    for (std::size_t index = 0; index < matrix.size(); ++index) {
        if (!exact_square_cpp(matrix[index], canonical_roots[index])) {
            return std::nullopt;
        }
        for (std::size_t prior = 0; prior < index; ++prior) {
            if (matrix[index] == matrix[prior]) {
                return std::nullopt;
            }
        }
    }

    static constexpr std::array<std::array<int, 3>, 8> lines = {{
        {{0, 1, 2}}, {{3, 4, 5}}, {{6, 7, 8}},
        {{0, 3, 6}}, {{1, 4, 7}}, {{2, 5, 8}},
        {{0, 4, 8}}, {{2, 4, 6}},
    }};
    const cpp_int expected = matrix[0] + matrix[1] + matrix[2];
    for (const auto& line : lines) {
        if (matrix[line[0]] + matrix[line[1]] + matrix[line[2]] != expected) {
            return std::nullopt;
        }
    }

    return Candidate{m, b, c, clearing, primitive, matrix, canonical_roots,
                     {low, middle, high}};
}

std::string fraction_json(const RootFraction& root) {
    return "{\"numerator\":\"" + std::to_string(root.numerator) +
           "\",\"denominator\":\"" + std::to_string(root.denominator) + "\"}";
}

std::string point_json(const PointRecord& point) {
    std::ostringstream out;
    out << "{\"x\":" << point.x << ",\"y\":" << point.y
        << ",\"sqrt_x_minus_kappa\":" << fraction_json(point.root_minus)
        << ",\"sqrt_x\":" << fraction_json(point.root_center)
        << ",\"sqrt_x_plus_kappa\":" << fraction_json(point.root_plus)
        << '}';
    return out.str();
}

std::string candidate_json(const Candidate& candidate, int kappa) {
    std::ostringstream out;
    out << "{\"kind\":\"E-W\",\"kappa\":" << kappa
        << ",\"msq_d\":{\"m\":" << candidate.m
        << ",\"b\":" << candidate.b << ",\"c\":" << candidate.c << "}"
        << ",\"clearing_denominator\":\"" << candidate.clearing_denominator
        << "\",\"primitive_gcd\":\"" << candidate.primitive_gcd << "\""
        << ",\"precursors\":[";
    for (std::size_t index = 0; index < candidate.points.size(); ++index) {
        if (index != 0) out << ',';
        out << point_json(candidate.points[index]);
    }
    out << "],\"doubled_x\":[";
    for (std::size_t index = 0; index < candidate.points.size(); ++index) {
        if (index != 0) out << ',';
        const BigRational X = candidate.points[index].doubled_x();
        out << "{\"numerator\":\"" << X.numerator
            << "\",\"denominator\":\"" << X.denominator << "\"}";
    }
    out << "],\"matrix_values\":[";
    for (std::size_t index = 0; index < candidate.matrix.size(); ++index) {
        if (index != 0) out << ',';
        out << candidate.matrix[index];
    }
    out << "],\"matrix_roots\":[";
    for (std::size_t index = 0; index < candidate.roots.size(); ++index) {
        if (index != 0) out << ',';
        out << candidate.roots[index];
    }
    out << "]}\n";
    return out.str();
}

std::string matrix_values_text(const Candidate& candidate) {
    std::ostringstream out;
    for (std::size_t index = 0; index < candidate.matrix.size(); ++index) {
        if (index != 0) out << ' ';
        out << candidate.matrix[index];
    }
    out << '\n';
    return out.str();
}

struct Options {
    std::string lane;
    int kappa_min = 0;
    int kappa_max = 0;
    std::int64_t x_bound = -1;
    int chunk_count = 1;
    int chunk_index = 0;
    double max_seconds = MAX_WALL_SECONDS;
    fs::path out_dir;
    bool emit_inventory = false;
    bool self_test = false;
    std::string python = "python";
    fs::path scalar_verifier;
    fs::path independent_verifier;
};

long long parse_integer(const std::string& text, const std::string& option) {
    std::size_t consumed = 0;
    long long value = 0;
    try {
        value = std::stoll(text, &consumed, 10);
    } catch (const std::exception&) {
        throw std::runtime_error("invalid integer for " + option + ": " + text);
    }
    if (consumed != text.size()) {
        throw std::runtime_error("invalid integer for " + option + ": " + text);
    }
    return value;
}

double parse_double(const std::string& text, const std::string& option) {
    std::size_t consumed = 0;
    double value = 0;
    try {
        value = std::stod(text, &consumed);
    } catch (const std::exception&) {
        throw std::runtime_error("invalid number for " + option + ": " + text);
    }
    if (consumed != text.size() || !std::isfinite(value)) {
        throw std::runtime_error("invalid number for " + option + ": " + text);
    }
    return value;
}

void apply_lane(Options& options) {
    if (options.lane.empty()) {
        return;
    }
    if (options.lane.size() != 3 || options.lane[0] != 'E' ||
        options.lane[1] < '0' || options.lane[1] > '9' ||
        options.lane[2] < '0' || options.lane[2] > '9') {
        throw std::runtime_error("lane must be E01 through E16");
    }
    const int number = (options.lane[1] - '0') * 10 + (options.lane[2] - '0');
    if (number < 1 || number > 16) {
        throw std::runtime_error("lane must be E01 through E16");
    }
    const int expected_min = 1 + (number - 1) * 64;
    const int expected_max = number * 64;
    if ((options.kappa_min != 0 && options.kappa_min != expected_min) ||
        (options.kappa_max != 0 && options.kappa_max != expected_max)) {
        throw std::runtime_error("explicit kappa range conflicts with lane " + options.lane);
    }
    options.kappa_min = expected_min;
    options.kappa_max = expected_max;
}

Options parse_options(int argc, char* argv[]) {
    Options options;
    for (int index = 1; index < argc; ++index) {
        const std::string argument = argv[index];
        const auto require_value = [&](const std::string& name) -> std::string {
            if (index + 1 >= argc) {
                throw std::runtime_error("missing value for " + name);
            }
            return argv[++index];
        };
        if (argument == "--lane") {
            options.lane = require_value(argument);
        } else if (argument == "--kappa-min") {
            options.kappa_min = static_cast<int>(parse_integer(require_value(argument), argument));
        } else if (argument == "--kappa-max") {
            options.kappa_max = static_cast<int>(parse_integer(require_value(argument), argument));
        } else if (argument == "--x-bound") {
            options.x_bound = parse_integer(require_value(argument), argument);
        } else if (argument == "--chunk-count") {
            options.chunk_count = static_cast<int>(parse_integer(require_value(argument), argument));
        } else if (argument == "--chunk-index") {
            options.chunk_index = static_cast<int>(parse_integer(require_value(argument), argument));
        } else if (argument == "--max-seconds") {
            options.max_seconds = parse_double(require_value(argument), argument);
        } else if (argument == "--out-dir") {
            options.out_dir = require_value(argument);
        } else if (argument == "--emit-inventory") {
            options.emit_inventory = true;
        } else if (argument == "--python") {
            options.python = require_value(argument);
        } else if (argument == "--scalar-verifier") {
            options.scalar_verifier = require_value(argument);
        } else if (argument == "--independent-verifier") {
            options.independent_verifier = require_value(argument);
        } else if (argument == "--self-test") {
            options.self_test = true;
        } else {
            throw std::runtime_error("unknown option: " + argument);
        }
    }
    if (options.self_test) {
        return options;
    }
    apply_lane(options);
    if (options.kappa_min <= 0 || options.kappa_max < options.kappa_min ||
        options.kappa_max > MANIFEST_MAX_KAPPA) {
        throw std::runtime_error("require 1 <= kappa-min <= kappa-max <= 1024");
    }
    if (options.x_bound < 0 || options.x_bound > MANIFEST_MAX_X) {
        throw std::runtime_error("require 0 <= x-bound <= 2^20");
    }
    if (options.chunk_count < 1 || options.chunk_count > MAX_CHUNKS ||
        options.chunk_index < 0 || options.chunk_index >= options.chunk_count) {
        throw std::runtime_error("require 1 <= chunk-count <= 64 and 0 <= chunk-index < chunk-count");
    }
    if (options.max_seconds <= 0 || options.max_seconds > MAX_WALL_SECONDS) {
        throw std::runtime_error("require 0 < max-seconds <= 28800");
    }
    if (options.out_dir.empty()) {
        throw std::runtime_error("--out-dir is required");
    }
    return options;
}

bool same_root(const RootFraction& root,
               std::uint64_t numerator,
               std::uint64_t denominator) {
    return root.numerator == numerator && root.denominator == denominator;
}

int run_self_test() {
    int checks = 0;
    const auto require = [&](bool condition, const std::string& label) {
        ++checks;
        if (!condition) {
            throw std::runtime_error("self-test failed: " + label);
        }
    };

    require(is_squarefree(5) && is_squarefree(6) && !is_squarefree(12), "squarefree");
    {
        const __int128 rhs = static_cast<__int128>(-4) * (16 - 25);
        require(rhs == 36 && isqrt_u64(36) == 6, "kappa=5 integral point");
        const auto point = make_point_record(5, -4, 6);
        require(point.has_value(), "kappa=5 point reconstruction");
        require(same_root(point->root_minus, 31, 12) &&
                same_root(point->root_center, 41, 12) &&
                same_root(point->root_plus, 49, 12), "kappa=5 doubled roots");
    }
    {
        const __int128 rhs = static_cast<__int128>(12) * (144 - 36);
        require(rhs == 1296 && isqrt_u64(1296) == 36, "kappa=6 integral point");
        const auto point = make_point_record(6, 12, 36);
        require(point.has_value(), "kappa=6 point reconstruction");
        require(same_root(point->root_minus, 1, 2) &&
                same_root(point->root_center, 5, 2) &&
                same_root(point->root_plus, 7, 2), "kappa=6 doubled roots");
    }
    require(half(BigRational(1, 4) + BigRational(9, 4)) == BigRational(5, 4),
            "AP midpoint arithmetic");

    std::cout << "{\"valid\":true,\"code\":\"SELF_TEST_OK\",\"checks\":"
              << checks << "}\n";
    return 0;
}

struct Counters {
    std::uint64_t kappas_selected = 0;
    std::uint64_t kappas_completed = 0;
    std::uint64_t x_tested = 0;
    std::uint64_t integral_points = 0;
    std::uint64_t distinct_doubled_x = 0;
    std::uint64_t ap_endpoint_pairs = 0;
    std::uint64_t ap_triples = 0;
    std::uint64_t candidates_reconstructed = 0;
    std::uint64_t verifier_attempts = 0;
};

struct VerificationResult {
    int scalar_exit = -1;
    int independent_exit = -1;
    fs::path candidate_path;
    fs::path matrix_path;
    fs::path scalar_stdout;
    fs::path scalar_stderr;
    fs::path independent_stdout;
    fs::path independent_stderr;
};

VerificationResult verify_candidate(const Candidate& candidate,
                                    int kappa,
                                    const Options& options,
                                    const fs::path& executable_path) {
    VerificationResult result;
    result.candidate_path = options.out_dir / "candidate.json";
    result.matrix_path = options.out_dir / "candidate_matrix.txt";
    result.scalar_stdout = options.out_dir / "scalar_verify.json";
    result.scalar_stderr = options.out_dir / "scalar_verify.stderr.txt";
    result.independent_stdout = options.out_dir / "independent_verify.json";
    result.independent_stderr = options.out_dir / "independent_verify.stderr.txt";
    atomic_write(result.candidate_path, candidate_json(candidate, kappa));
    atomic_write(result.matrix_path, matrix_values_text(candidate));

    const fs::path engine_dir = fs::absolute(executable_path).parent_path();
    const fs::path scalar = options.scalar_verifier.empty()
        ? engine_dir / "verify_scalar.py" : fs::absolute(options.scalar_verifier);
    const fs::path independent = options.independent_verifier.empty()
        ? engine_dir / "verify_independent.exe" : fs::absolute(options.independent_verifier);

    const std::string scalar_command =
        shell_quote_text(options.python) + " " + shell_quote(scalar) +
        " --input " + shell_quote(result.candidate_path) + " > " +
        shell_quote(result.scalar_stdout) + " 2> " + shell_quote(result.scalar_stderr);
    result.scalar_exit = normalized_system_exit(std::system(scalar_command.c_str()));

    const std::string independent_command =
        shell_quote(independent) + " --file " + shell_quote(result.matrix_path) +
        " > " + shell_quote(result.independent_stdout) + " 2> " +
        shell_quote(result.independent_stderr);
    result.independent_exit = normalized_system_exit(std::system(independent_command.c_str()));
    return result;
}

std::string inventory_line(const PointRecord& point) {
    const BigRational X = point.doubled_x();
    std::ostringstream out;
    out << "{\"kappa\":" << point.kappa
        << ",\"precursor_x\":" << point.x
        << ",\"precursor_y\":" << point.y
        << ",\"x2_num\":\"" << X.numerator
        << "\",\"x2_den\":\"" << X.denominator
        << "\",\"root_minus_num\":\"" << point.root_minus.numerator
        << "\",\"root_minus_den\":\"" << point.root_minus.denominator
        << "\",\"root_center_num\":\"" << point.root_center.numerator
        << "\",\"root_center_den\":\"" << point.root_center.denominator
        << "\",\"root_plus_num\":\"" << point.root_plus.numerator
        << "\",\"root_plus_den\":\"" << point.root_plus.denominator
        << "\"}\n";
    return out.str();
}

std::string summary_json(const Options& options,
                         const Counters& counters,
                         const std::string& status,
                         const std::string& started,
                         const std::string& finished,
                         double elapsed_seconds,
                         const std::optional<VerificationResult>& verification,
                         const std::string& error = "") {
    std::ostringstream out;
    out << "{\"schema_version\":1,\"engine\":\"elliptic_integral_search\""
        << ",\"status\":\"" << json_escape(status) << "\""
        << ",\"lane\":\"" << json_escape(options.lane) << "\""
        << ",\"kappa_min\":" << options.kappa_min
        << ",\"kappa_max\":" << options.kappa_max
        << ",\"squarefree_only\":true"
        << ",\"integral_precursors_only\":true"
        << ",\"x_bound\":" << options.x_bound
        << ",\"chunk_count\":" << options.chunk_count
        << ",\"chunk_index\":" << options.chunk_index
        << ",\"max_seconds\":" << std::fixed << std::setprecision(6)
        << options.max_seconds
        << ",\"started_utc\":\"" << started << "\""
        << ",\"finished_utc\":\"" << finished << "\""
        << ",\"elapsed_seconds\":" << elapsed_seconds
        << ",\"counts\":{\"kappas_selected\":" << counters.kappas_selected
        << ",\"kappas_completed\":" << counters.kappas_completed
        << ",\"x_tested\":" << counters.x_tested
        << ",\"integral_points\":" << counters.integral_points
        << ",\"distinct_doubled_x\":" << counters.distinct_doubled_x
        << ",\"ap_endpoint_pairs\":" << counters.ap_endpoint_pairs
        << ",\"ap_triples\":" << counters.ap_triples
        << ",\"candidates_reconstructed\":" << counters.candidates_reconstructed
        << ",\"verifier_attempts\":" << counters.verifier_attempts << '}';
    if (verification.has_value()) {
        out << ",\"verification\":{\"scalar_exit\":" << verification->scalar_exit
            << ",\"independent_exit\":" << verification->independent_exit
            << ",\"candidate_path\":\"" << json_escape(verification->candidate_path.string())
            << "\",\"matrix_path\":\"" << json_escape(verification->matrix_path.string())
            << "\",\"scalar_stdout\":\"" << json_escape(verification->scalar_stdout.string())
            << "\",\"independent_stdout\":\""
            << json_escape(verification->independent_stdout.string()) << "\"}";
    }
    if (!error.empty()) {
        out << ",\"error\":\"" << json_escape(error) << "\"";
    }
    out << "}\n";
    return out.str();
}

int run_search(const Options& options, const fs::path& executable_path) {
    fs::create_directories(options.out_dir);
    const std::string started = utc_now();
    const auto clock_start = std::chrono::steady_clock::now();
    Counters counters;
    std::ostringstream inventory;
    std::optional<VerificationResult> verification;
    std::string status = "NO_HIT";
    std::string error;
    bool timed_out = false;

    for (int kappa = options.kappa_min; kappa <= options.kappa_max; ++kappa) {
        if (!is_squarefree(kappa) ||
            ((kappa - options.kappa_min) % options.chunk_count) != options.chunk_index) {
            continue;
        }
        ++counters.kappas_selected;
    }

    try {
        for (int kappa = options.kappa_min; kappa <= options.kappa_max && !timed_out; ++kappa) {
            if (!is_squarefree(kappa) ||
                ((kappa - options.kappa_min) % options.chunk_count) != options.chunk_index) {
                continue;
            }

            std::unordered_map<std::string, PointRecord> deduplicated;
            for (std::int64_t x = -options.x_bound; x <= options.x_bound; ++x) {
                ++counters.x_tested;
                if ((counters.x_tested & 0xFFFFU) == 0) {
                    const double elapsed = std::chrono::duration<double>(
                        std::chrono::steady_clock::now() - clock_start).count();
                    if (elapsed >= options.max_seconds) {
                        timed_out = true;
                        break;
                    }
                }

                const __int128 xx = x;
                const __int128 kk = kappa;
                const __int128 rhs_signed = xx * (xx * xx - kk * kk);
                if (rhs_signed <= 0 ||
                    static_cast<unsigned __int128>(rhs_signed) >
                        std::numeric_limits<std::uint64_t>::max()) {
                    continue;
                }
                const std::uint64_t rhs = static_cast<std::uint64_t>(rhs_signed);
                static constexpr std::uint64_t square_residues_mod64 =
                    (1ULL << 0) | (1ULL << 1) | (1ULL << 4) | (1ULL << 9) |
                    (1ULL << 16) | (1ULL << 17) | (1ULL << 25) | (1ULL << 33) |
                    (1ULL << 36) | (1ULL << 41) | (1ULL << 49) | (1ULL << 57);
                if (((square_residues_mod64 >> (rhs & 63U)) & 1U) == 0) {
                    continue;
                }
                const std::uint64_t y = isqrt_u64(rhs);
                if (static_cast<unsigned __int128>(y) * y != rhs || y == 0) {
                    continue;
                }
                ++counters.integral_points;
                const auto record = make_point_record(kappa, x, y);
                if (!record.has_value()) {
                    continue;
                }
                const std::string key = record->doubled_x_key();
                const auto found = deduplicated.find(key);
                if (found == deduplicated.end() || record->x < found->second.x) {
                    deduplicated[key] = *record;
                }
            }
            if (timed_out) {
                break;
            }

            std::vector<PointRecord> points;
            points.reserve(deduplicated.size());
            for (auto& entry : deduplicated) {
                points.push_back(std::move(entry.second));
            }
            std::sort(points.begin(), points.end(), [](const PointRecord& lhs, const PointRecord& rhs) {
                return root_less(lhs.root_center, rhs.root_center);
            });
            counters.distinct_doubled_x += points.size();
            if (options.emit_inventory) {
                for (const PointRecord& point : points) {
                    inventory << inventory_line(point);
                }
            }

            std::unordered_map<std::string, std::size_t> x_index;
            for (std::size_t index = 0; index < points.size(); ++index) {
                x_index[points[index].doubled_x().key()] = index;
            }
            for (std::size_t low = 0; low < points.size(); ++low) {
                for (std::size_t high = low + 1; high < points.size(); ++high) {
                    ++counters.ap_endpoint_pairs;
                    const BigRational midpoint = half(
                        points[low].doubled_x() + points[high].doubled_x());
                    const auto found = x_index.find(midpoint.key());
                    if (found == x_index.end() || found->second <= low || found->second >= high) {
                        continue;
                    }
                    ++counters.ap_triples;
                    const auto candidate = reconstruct_candidate(
                        points[low], points[found->second], points[high]);
                    if (!candidate.has_value()) {
                        continue;
                    }
                    ++counters.candidates_reconstructed;
                    ++counters.verifier_attempts;
                    verification = verify_candidate(*candidate, kappa, options, executable_path);
                    if (verification->scalar_exit == 0 && verification->independent_exit == 0) {
                        status = "HIT_VERIFIED";
                    } else {
                        status = "FAILED_VERIFICATION";
                        error = "candidate disagreed with one or both required verifiers";
                    }
                    break;
                }
                if (verification.has_value()) {
                    break;
                }
            }
            ++counters.kappas_completed;
            if (verification.has_value()) {
                break;
            }
        }
    } catch (const std::exception& exception) {
        status = "FAILED";
        error = exception.what();
    }

    if (timed_out && !verification.has_value() && status != "FAILED") {
        status = "TIMEOUT_INCOMPLETE";
    }
    if (options.emit_inventory) {
        atomic_write(options.out_dir / "inventory.jsonl", inventory.str());
    }
    const double elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - clock_start).count();
    atomic_write(options.out_dir / "summary.json",
                 summary_json(options, counters, status, started, utc_now(), elapsed,
                              verification, error));
    std::cout << summary_json(options, counters, status, started, utc_now(), elapsed,
                             verification, error);
    if (status == "NO_HIT" || status == "HIT_VERIFIED") {
        return 0;
    }
    if (status == "TIMEOUT_INCOMPLETE") {
        return 4;
    }
    return 3;
}

}  // namespace

int main(int argc, char* argv[]) {
    try {
        const Options options = parse_options(argc, argv);
        if (options.self_test) {
            return run_self_test();
        }
        return run_search(options, fs::path(argv[0]));
    } catch (const std::exception& exception) {
        std::cerr << "elliptic_integral_search: " << exception.what() << '\n';
        return 2;
    }
}
