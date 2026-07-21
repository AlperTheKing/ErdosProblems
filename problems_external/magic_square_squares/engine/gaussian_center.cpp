#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <regex>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <unordered_map>
#include <utility>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#else
#include <sys/wait.h>
#endif

namespace fs = std::filesystem;

namespace {

using u64 = std::uint64_t;
using i64 = std::int64_t;
using u128 = unsigned __int128;
using i128 = __int128;

constexpr const char* kSchema = "gaussian-center-v1";

#ifdef _WIN32
std::atomic<u64> g_atomic_replace_transient_retries{0};
#endif

std::string u128_decimal(u128 value) {
    if (value == 0) {
        return "0";
    }
    std::string result;
    while (value != 0) {
        result.push_back(static_cast<char>('0' + value % 10));
        value /= 10;
    }
    std::reverse(result.begin(), result.end());
    return result;
}

u128 parse_u128(const std::string& text) {
    if (text.empty()) {
        throw std::runtime_error("empty unsigned integer");
    }
    u128 value = 0;
    const u128 maximum = ~static_cast<u128>(0);
    for (const char ch : text) {
        if (ch < '0' || ch > '9') {
            throw std::runtime_error("invalid unsigned integer: " + text);
        }
        const unsigned digit = static_cast<unsigned>(ch - '0');
        if (value > (maximum - digit) / 10) {
            throw std::runtime_error("unsigned integer overflow: " + text);
        }
        value = value * 10 + digit;
    }
    return value;
}

u64 parse_u64(const std::string& text) {
    const u128 value = parse_u128(text);
    if (value > std::numeric_limits<u64>::max()) {
        throw std::runtime_error("uint64 overflow: " + text);
    }
    return static_cast<u64>(value);
}

u128 square_u64(u64 value) {
    return static_cast<u128>(value) * value;
}

u64 floor_sqrt_u64(u64 value) {
    u64 root = static_cast<u64>(std::sqrt(static_cast<long double>(value)));
    while (static_cast<u128>(root + 1) * (root + 1) <= value) {
        ++root;
    }
    while (static_cast<u128>(root) * root > value) {
        --root;
    }
    return root;
}

std::string json_escape(const std::string& input) {
    std::ostringstream out;
    for (const unsigned char ch : input) {
        switch (ch) {
            case '"':
                out << "\\\"";
                break;
            case '\\':
                out << "\\\\";
                break;
            case '\b':
                out << "\\b";
                break;
            case '\f':
                out << "\\f";
                break;
            case '\n':
                out << "\\n";
                break;
            case '\r':
                out << "\\r";
                break;
            case '\t':
                out << "\\t";
                break;
            default:
                if (ch < 0x20) {
                    out << "\\u" << std::hex << std::setw(4)
                        << std::setfill('0') << static_cast<unsigned>(ch)
                        << std::dec << std::setfill(' ');
                } else {
                    out << static_cast<char>(ch);
                }
        }
    }
    return out.str();
}

std::string read_file(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("cannot read file: " + path.string());
    }
    std::ostringstream buffer;
    buffer << input.rdbuf();
    if (!input.good() && !input.eof()) {
        throw std::runtime_error("read failure: " + path.string());
    }
    return buffer.str();
}

void atomic_write(const fs::path& target, const std::string& contents) {
    fs::create_directories(target.parent_path());
    fs::path temporary = target;
    static std::atomic<u64> temporary_sequence{0};
    std::ostringstream temporary_suffix;
    temporary_suffix << ".tmp.";
#ifdef _WIN32
    temporary_suffix << GetCurrentProcessId() << '.' << GetCurrentThreadId()
                     << '.';
#else
    temporary_suffix
        << std::chrono::steady_clock::now().time_since_epoch().count() << '.';
#endif
    temporary_suffix
        << temporary_sequence.fetch_add(1, std::memory_order_relaxed);
    temporary += temporary_suffix.str();
    {
        std::ofstream output(temporary, std::ios::binary | std::ios::trunc);
        if (!output) {
            throw std::runtime_error("cannot write temporary file: " +
                                     temporary.string());
        }
        output.write(contents.data(),
                     static_cast<std::streamsize>(contents.size()));
        output.flush();
        if (!output) {
            throw std::runtime_error("write failure: " + temporary.string());
        }
    }
#ifdef _WIN32
    constexpr unsigned kMaximumReplaceAttempts = 128;
    for (unsigned attempt = 1; attempt <= kMaximumReplaceAttempts; ++attempt) {
        if (MoveFileExW(temporary.c_str(),
                        target.c_str(),
                        MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
            return;
        }
        const DWORD error = GetLastError();
        std::error_code target_status_error;
        const bool access_denied_to_regular_target =
            error == ERROR_ACCESS_DENIED &&
            fs::is_regular_file(target, target_status_error) &&
            !target_status_error;
        const bool transient = error == ERROR_SHARING_VIOLATION ||
                               error == ERROR_LOCK_VIOLATION ||
                               access_denied_to_regular_target;
        if (!transient || attempt == kMaximumReplaceAttempts) {
            std::error_code ignored;
            fs::remove(temporary, ignored);
            throw std::runtime_error(
                "atomic replace failed for: " + target.string() +
                " (Windows error " + std::to_string(error) +
                ", attempts " + std::to_string(attempt) + ")");
        }
        g_atomic_replace_transient_retries.fetch_add(
            1, std::memory_order_relaxed);
        const DWORD delay_ms =
            static_cast<DWORD>(std::min(8U, 1U + attempt / 16U));
        Sleep(delay_ms);
    }
#else
    if (std::rename(temporary.c_str(), target.c_str()) != 0) {
        throw std::runtime_error("atomic replace failed for: " +
                                 target.string());
    }
#endif
}

std::vector<std::uint32_t> primes_through(u64 limit) {
    if (limit > 50000000ULL) {
        throw std::runtime_error(
            "sieve limit exceeds the explicit 50,000,000 safety bound");
    }
    std::vector<bool> composite(static_cast<std::size_t>(limit + 1), false);
    for (u64 p = 2; p * p <= limit; ++p) {
        if (!composite[static_cast<std::size_t>(p)]) {
            for (u64 multiple = p * p; multiple <= limit; multiple += p) {
                composite[static_cast<std::size_t>(multiple)] = true;
            }
        }
    }
    std::vector<std::uint32_t> primes;
    for (u64 p = 2; p <= limit; ++p) {
        if (!composite[static_cast<std::size_t>(p)]) {
            primes.push_back(static_cast<std::uint32_t>(p));
        }
    }
    return primes;
}

struct PrimePower {
    u64 prime = 0;
    unsigned exponent = 0;
};

using Factorization = std::vector<PrimePower>;

std::vector<Factorization> factor_closed_chunk(
    u64 first,
    u64 last,
    const std::vector<std::uint32_t>& primes) {
    if (first == 0 || last < first) {
        throw std::runtime_error("invalid positive factorization interval");
    }
    const u64 width_u64 = last - first + 1;
    if (width_u64 > std::numeric_limits<std::size_t>::max()) {
        throw std::runtime_error("factorization chunk is too wide");
    }
    const std::size_t width = static_cast<std::size_t>(width_u64);
    std::vector<u64> remaining(width);
    std::vector<Factorization> factors(width);
    for (std::size_t i = 0; i < width; ++i) {
        remaining[i] = first + static_cast<u64>(i);
    }

    for (const std::uint32_t p32 : primes) {
        const u64 p = p32;
        const u64 remainder = first % p;
        const u64 delta = remainder == 0 ? 0 : p - remainder;
        if (delta > last - first) {
            continue;
        }
        u64 multiple = first + delta;
        for (;;) {
            const std::size_t index =
                static_cast<std::size_t>(multiple - first);
            unsigned exponent = 0;
            while (remaining[index] % p == 0) {
                remaining[index] /= p;
                ++exponent;
            }
            if (exponent != 0) {
                factors[index].push_back({p, exponent});
            }
            if (last - multiple < p) {
                break;
            }
            multiple += p;
        }
    }

    for (std::size_t i = 0; i < width; ++i) {
        if (remaining[i] > 1) {
            factors[i].push_back({remaining[i], 1});
        }
        u128 reconstructed = 1;
        for (const PrimePower& factor : factors[i]) {
            for (unsigned e = 0; e < factor.exponent; ++e) {
                reconstructed *= factor.prime;
            }
        }
        const u64 original = first + static_cast<u64>(i);
        if (reconstructed != original) {
            throw std::runtime_error(
                "factorization reconstruction failed at m=" +
                std::to_string(original));
        }
    }
    return factors;
}

u64 modular_multiply(u64 a, u64 b, u64 modulus) {
    return static_cast<u64>((static_cast<u128>(a) * b) % modulus);
}

u64 modular_power(u64 base, u64 exponent, u64 modulus) {
    u64 result = 1 % modulus;
    while (exponent != 0) {
        if ((exponent & 1U) != 0) {
            result = modular_multiply(result, base, modulus);
        }
        exponent >>= 1U;
        if (exponent != 0) {
            base = modular_multiply(base, base, modulus);
        }
    }
    return result;
}

std::pair<u64, u64> cornacchia_attempt(u64 prime, u64 root_minus_one) {
    u64 previous = prime;
    u64 current = root_minus_one;
    while (static_cast<u128>(current) * current > prime) {
        const u64 next = previous % current;
        previous = current;
        current = next;
        if (current == 0) {
            return {0, 0};
        }
    }
    const u64 a = current;
    const u64 b_squared = prime - a * a;
    const u64 b = floor_sqrt_u64(b_squared);
    if (static_cast<u128>(b) * b != b_squared || a == 0 || b == 0) {
        return {0, 0};
    }
    return std::minmax(a, b);
}

std::pair<u64, u64> prime_as_two_squares(u64 prime) {
    if (prime % 4 != 1 || prime < 5) {
        throw std::runtime_error(
            "two-square decomposition requested for invalid prime");
    }
    u64 nonresidue = 2;
    while (modular_power(nonresidue, (prime - 1) / 2, prime) != prime - 1) {
        ++nonresidue;
    }
    const u64 root_minus_one =
        modular_power(nonresidue, (prime - 1) / 4, prime);
    if (modular_multiply(root_minus_one, root_minus_one, prime) !=
        prime - 1) {
        throw std::runtime_error("modular square root audit failed");
    }
    auto result = cornacchia_attempt(prime, root_minus_one);
    if (result.first == 0) {
        result = cornacchia_attempt(prime, prime - root_minus_one);
    }
    if (result.first == 0 ||
        static_cast<u128>(result.first) * result.first +
                static_cast<u128>(result.second) * result.second !=
            prime) {
        throw std::runtime_error(
            "Cornacchia decomposition failed for p=" +
            std::to_string(prime));
    }
    return result;
}

struct Gaussian {
    i128 real = 0;
    i128 imag = 0;
};

Gaussian gaussian_multiply(const Gaussian& left, const Gaussian& right) {
    return {
        left.real * right.real - left.imag * right.imag,
        left.real * right.imag + left.imag * right.real,
    };
}

std::vector<Gaussian> gaussian_powers(const Gaussian& base,
                                     unsigned maximum) {
    std::vector<Gaussian> result(maximum + 1);
    result[0] = {1, 0};
    for (unsigned exponent = 1; exponent <= maximum; ++exponent) {
        result[exponent] =
            gaussian_multiply(result[exponent - 1], base);
    }
    return result;
}

i128 absolute_i128(i128 value) {
    return value < 0 ? -value : value;
}

i64 checked_i64(i128 value) {
    if (value < std::numeric_limits<i64>::min() ||
        value > std::numeric_limits<i64>::max()) {
        throw std::runtime_error("Gaussian coordinate exceeds int64");
    }
    return static_cast<i64>(value);
}

struct RootPair {
    u64 minus_root = 0;
    u64 plus_root = 0;
};

struct CenterData {
    u64 m = 0;
    u128 expected_r2 = 0;
    std::size_t enumerated_r2 = 0;
    u128 selection_count = 0;
    std::map<u128, RootPair> deviations;
};

class GaussianEnumerator {
  public:
    explicit GaussianEnumerator(u64 small_prime_cache_limit)
        : small_prime_cache_limit_(small_prime_cache_limit) {}

    CenterData enumerate(u64 m, const Factorization& factors) {
        unsigned exponent_two = 0;
        u64 inert_scalar = 1;
        struct SplitFactor {
            u64 prime;
            unsigned exponent;
            std::pair<u64, u64> decomposition;
        };
        std::vector<SplitFactor> split_factors;

        u128 reconstructed = 1;
        u128 selection_count = 1;
        for (const PrimePower& factor : factors) {
            for (unsigned e = 0; e < factor.exponent; ++e) {
                reconstructed *= factor.prime;
            }
            if (factor.prime == 2) {
                exponent_two = factor.exponent;
            } else if (factor.prime % 4 == 1) {
                selection_count *= 2 * factor.exponent + 1;
                split_factors.push_back(
                    {factor.prime,
                     factor.exponent,
                     split_prime(factor.prime)});
            } else if (factor.prime % 4 == 3) {
                u128 scalar = inert_scalar;
                for (unsigned e = 0; e < factor.exponent; ++e) {
                    scalar *= factor.prime;
                }
                if (scalar > std::numeric_limits<u64>::max()) {
                    throw std::runtime_error("inert scalar overflow");
                }
                inert_scalar = static_cast<u64>(scalar);
            } else {
                throw std::runtime_error("factor is neither 2 nor odd");
            }
        }
        if (reconstructed != m) {
            throw std::runtime_error("center factorization audit failed");
        }
        if (selection_count >
            static_cast<u128>(std::numeric_limits<std::size_t>::max())) {
            throw std::runtime_error("representation count exceeds size_t");
        }

        Gaussian base = gaussian_powers(
            {1, 1}, 2 * exponent_two + 1).back();
        base.real *= inert_scalar;
        base.imag *= inert_scalar;

        std::vector<std::vector<Gaussian>> choices;
        choices.reserve(split_factors.size());
        for (const SplitFactor& factor : split_factors) {
            const unsigned total = 2 * factor.exponent;
            const Gaussian pi = {
                static_cast<i128>(factor.decomposition.first),
                static_cast<i128>(factor.decomposition.second)};
            const Gaussian conjugate = {pi.real, -pi.imag};
            const auto powers_pi = gaussian_powers(pi, total);
            const auto powers_conjugate =
                gaussian_powers(conjugate, total);
            std::vector<Gaussian> factor_choices;
            factor_choices.reserve(total + 1);
            for (unsigned k = 0; k <= total; ++k) {
                factor_choices.push_back(gaussian_multiply(
                    powers_pi[k], powers_conjugate[total - k]));
            }
            choices.push_back(std::move(factor_choices));
        }

        std::set<std::pair<i64, i64>> all_representations;
        std::function<void(std::size_t, Gaussian)> recurse =
            [&](std::size_t index, Gaussian value) {
                if (index == choices.size()) {
                    const std::array<Gaussian, 4> unit_multiples = {{
                        value,
                        {-value.imag, value.real},
                        {-value.real, -value.imag},
                        {value.imag, -value.real},
                    }};
                    for (const Gaussian& representation : unit_multiples) {
                        all_representations.insert(
                            {checked_i64(representation.real),
                             checked_i64(representation.imag)});
                    }
                    return;
                }
                for (const Gaussian& choice : choices[index]) {
                    recurse(index + 1,
                            gaussian_multiply(value, choice));
                }
            };
        recurse(0, base);

        const u128 expected_r2 = 4 * selection_count;
        if (static_cast<u128>(all_representations.size()) != expected_r2) {
            throw std::runtime_error(
                "r2 representation-count audit failed at m=" +
                std::to_string(m) + ": expected " +
                u128_decimal(expected_r2) + ", enumerated " +
                std::to_string(all_representations.size()));
        }

        const u128 target_norm = 2 * square_u64(m);
        std::map<u128, RootPair> deviations;
        for (const auto& representation : all_representations) {
            const u64 x = static_cast<u64>(
                absolute_i128(static_cast<i128>(representation.first)));
            const u64 y = static_cast<u64>(
                absolute_i128(static_cast<i128>(representation.second)));
            if (static_cast<u128>(x) * x +
                    static_cast<u128>(y) * y !=
                target_norm) {
                throw std::runtime_error(
                    "Gaussian norm audit failed at m=" +
                    std::to_string(m));
            }
            if (x == 0 || y == 0) {
                throw std::runtime_error(
                    "unexpected zero coordinate at m=" +
                    std::to_string(m));
            }
            const u64 lower = std::min(x, y);
            const u64 upper = std::max(x, y);
            if (lower == upper) {
                continue;
            }
            const u128 lower_square = square_u64(lower);
            const u128 upper_square = square_u64(upper);
            if ((upper_square - lower_square) % 2 != 0) {
                throw std::runtime_error(
                    "deviation parity audit failed at m=" +
                    std::to_string(m));
            }
            const u128 deviation =
                (upper_square - lower_square) / 2;
            const u128 center_square = square_u64(m);
            if (lower_square + deviation != center_square ||
                center_square + deviation != upper_square) {
                throw std::runtime_error(
                    "deviation root audit failed at m=" +
                    std::to_string(m));
            }
            const auto [iterator, inserted] =
                deviations.emplace(deviation,
                                   RootPair{lower, upper});
            if (!inserted &&
                (iterator->second.minus_root != lower ||
                 iterator->second.plus_root != upper)) {
                throw std::runtime_error(
                    "deviation collision audit failed at m=" +
                    std::to_string(m));
            }
        }

        const u128 expected_deviations = (selection_count - 1) / 2;
        if (static_cast<u128>(deviations.size()) !=
            expected_deviations) {
            throw std::runtime_error(
                "D-set cardinality audit failed at m=" +
                std::to_string(m) + ": expected " +
                u128_decimal(expected_deviations) + ", enumerated " +
                std::to_string(deviations.size()));
        }

        return {
            m,
            expected_r2,
            all_representations.size(),
            selection_count,
            std::move(deviations),
        };
    }

  private:
    std::pair<u64, u64> split_prime(u64 prime) {
        if (prime <= small_prime_cache_limit_) {
            const auto found = split_prime_cache_.find(prime);
            if (found != split_prime_cache_.end()) {
                return found->second;
            }
            const auto result = prime_as_two_squares(prime);
            split_prime_cache_.emplace(prime, result);
            return result;
        }
        return prime_as_two_squares(prime);
    }

    u64 small_prime_cache_limit_;
    std::unordered_map<u64, std::pair<u64, u64>> split_prime_cache_;
};

struct Candidate {
    u64 source_m = 0;
    u64 m = 0;
    u128 b = 0;
    u128 c = 0;
    RootPair b_roots;
    RootPair c_roots;
    RootPair sum_roots;
    RootPair difference_roots;
    u64 primitive_gcd = 1;
    std::array<u128, 9> matrix{};
};

std::array<u128, 9> candidate_matrix(
    u64 m,
    u128 b,
    u128 c) {
    const u128 center = square_u64(m);
    return {{
        center - b,
        center + b + c,
        center - c,
        center + b - c,
        center,
        center - b + c,
        center + c,
        center - b - c,
        center + b,
    }};
}

bool internally_valid_candidate(const Candidate& candidate) {
    if (candidate.m == 0 || candidate.b <= candidate.c ||
        candidate.c == 0) {
        return false;
    }
    const u128 center = square_u64(candidate.m);
    const std::array<std::pair<u128, RootPair>, 4> memberships = {{
        {candidate.b, candidate.b_roots},
        {candidate.c, candidate.c_roots},
        {candidate.b + candidate.c, candidate.sum_roots},
        {candidate.b - candidate.c, candidate.difference_roots},
    }};
    for (const auto& membership : memberships) {
        const u128 deviation = membership.first;
        const RootPair roots = membership.second;
        if (roots.minus_root == 0 || roots.plus_root == 0 ||
            square_u64(roots.minus_root) + deviation != center ||
            center + deviation != square_u64(roots.plus_root)) {
            return false;
        }
    }
    const auto matrix =
        candidate_matrix(candidate.m, candidate.b, candidate.c);
    for (const u128 entry : matrix) {
        if (entry == 0) {
            return false;
        }
    }
    for (std::size_t i = 0; i < matrix.size(); ++i) {
        for (std::size_t j = i + 1; j < matrix.size(); ++j) {
            if (matrix[i] == matrix[j]) {
                return false;
            }
        }
    }
    static constexpr std::array<std::array<int, 3>, 8> lines = {{
        {{0, 1, 2}},
        {{3, 4, 5}},
        {{6, 7, 8}},
        {{0, 3, 6}},
        {{1, 4, 7}},
        {{2, 5, 8}},
        {{0, 4, 8}},
        {{2, 4, 6}},
    }};
    const u128 expected = matrix[0] + matrix[1] + matrix[2];
    for (const auto& line : lines) {
        if (matrix[static_cast<std::size_t>(line[0])] +
                matrix[static_cast<std::size_t>(line[1])] +
                matrix[static_cast<std::size_t>(line[2])] !=
            expected) {
            return false;
        }
    }
    return expected == 3 * center;
}

Candidate make_primitive_candidate(
    u64 source_m,
    u128 b,
    u128 c,
    const RootPair& b_roots,
    const RootPair& c_roots,
    const RootPair& sum_roots,
    const RootPair& difference_roots) {
    const std::array<u64, 9> roots = {{
        source_m,
        b_roots.minus_root,
        b_roots.plus_root,
        c_roots.minus_root,
        c_roots.plus_root,
        sum_roots.minus_root,
        sum_roots.plus_root,
        difference_roots.minus_root,
        difference_roots.plus_root,
    }};
    u64 divisor = 0;
    for (const u64 root : roots) {
        divisor = std::gcd(divisor, root);
    }
    if (divisor == 0) {
        throw std::runtime_error("zero primitive gcd");
    }
    const u128 divisor_square = square_u64(divisor);
    if (b % divisor_square != 0 || c % divisor_square != 0) {
        throw std::runtime_error("primitive deviation division failed");
    }
    const auto scale_pair = [divisor](const RootPair& roots_pair) {
        if (roots_pair.minus_root % divisor != 0 ||
            roots_pair.plus_root % divisor != 0) {
            throw std::runtime_error("primitive root division failed");
        }
        return RootPair{
            roots_pair.minus_root / divisor,
            roots_pair.plus_root / divisor,
        };
    };
    Candidate result;
    result.source_m = source_m;
    result.m = source_m / divisor;
    result.b = b / divisor_square;
    result.c = c / divisor_square;
    result.b_roots = scale_pair(b_roots);
    result.c_roots = scale_pair(c_roots);
    result.sum_roots = scale_pair(sum_roots);
    result.difference_roots = scale_pair(difference_roots);
    result.primitive_gcd = divisor;
    result.matrix = candidate_matrix(result.m, result.b, result.c);
    if (!internally_valid_candidate(result)) {
        throw std::runtime_error("primitive candidate internal audit failed");
    }
    return result;
}

std::optional<Candidate> find_candidate(
    const CenterData& center,
    u128& additive_triples) {
    std::vector<std::pair<u128, RootPair>> deviations(
        center.deviations.begin(), center.deviations.end());
    for (std::size_t b_index = 1;
         b_index < deviations.size();
         ++b_index) {
        const u128 b = deviations[b_index].first;
        for (std::size_t c_index = 0;
             c_index < b_index;
             ++c_index) {
            const u128 c = deviations[c_index].first;
            const u128 sum = b + c;
            const auto sum_found = center.deviations.find(sum);
            if (sum_found == center.deviations.end()) {
                continue;
            }
            ++additive_triples;
            const u128 difference = b - c;
            const auto difference_found =
                center.deviations.find(difference);
            if (difference_found == center.deviations.end()) {
                continue;
            }
            Candidate candidate = make_primitive_candidate(
                center.m,
                b,
                c,
                deviations[b_index].second,
                deviations[c_index].second,
                sum_found->second,
                difference_found->second);
            if (internally_valid_candidate(candidate)) {
                return candidate;
            }
        }
    }
    return std::nullopt;
}

// Compact standalone SHA-256 for stable primitive-certificate filenames.
std::uint32_t rotate_right(std::uint32_t value, unsigned amount) {
    return (value >> amount) | (value << (32U - amount));
}

std::string sha256(const std::string& input) {
    static constexpr std::array<std::uint32_t, 64> constants = {{
        0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U,
        0x3956c25bU, 0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U,
        0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U,
        0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U,
        0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU,
        0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
        0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U,
        0xc6e00bf3U, 0xd5a79147U, 0x06ca6351U, 0x14292967U,
        0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U,
        0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
        0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U,
        0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
        0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U,
        0x391c0cb3U, 0x4ed8aa4aU, 0x5b9cca4fU, 0x682e6ff3U,
        0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
        0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U,
    }};
    std::vector<std::uint8_t> message(input.begin(), input.end());
    const std::uint64_t bit_length =
        static_cast<std::uint64_t>(message.size()) * 8U;
    message.push_back(0x80U);
    while (message.size() % 64 != 56) {
        message.push_back(0);
    }
    for (int shift = 56; shift >= 0; shift -= 8) {
        message.push_back(
            static_cast<std::uint8_t>(bit_length >> shift));
    }

    std::array<std::uint32_t, 8> state = {{
        0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
        0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U,
    }};
    for (std::size_t offset = 0; offset < message.size(); offset += 64) {
        std::array<std::uint32_t, 64> words{};
        for (std::size_t i = 0; i < 16; ++i) {
            const std::size_t at = offset + 4 * i;
            words[i] =
                (static_cast<std::uint32_t>(message[at]) << 24U) |
                (static_cast<std::uint32_t>(message[at + 1]) << 16U) |
                (static_cast<std::uint32_t>(message[at + 2]) << 8U) |
                static_cast<std::uint32_t>(message[at + 3]);
        }
        for (std::size_t i = 16; i < 64; ++i) {
            const std::uint32_t s0 =
                rotate_right(words[i - 15], 7) ^
                rotate_right(words[i - 15], 18) ^
                (words[i - 15] >> 3U);
            const std::uint32_t s1 =
                rotate_right(words[i - 2], 17) ^
                rotate_right(words[i - 2], 19) ^
                (words[i - 2] >> 10U);
            words[i] =
                words[i - 16] + s0 + words[i - 7] + s1;
        }
        std::uint32_t a = state[0];
        std::uint32_t b = state[1];
        std::uint32_t c = state[2];
        std::uint32_t d = state[3];
        std::uint32_t e = state[4];
        std::uint32_t f = state[5];
        std::uint32_t g = state[6];
        std::uint32_t h = state[7];
        for (std::size_t i = 0; i < 64; ++i) {
            const std::uint32_t sigma1 =
                rotate_right(e, 6) ^ rotate_right(e, 11) ^
                rotate_right(e, 25);
            const std::uint32_t choose = (e & f) ^ ((~e) & g);
            const std::uint32_t temp1 =
                h + sigma1 + choose + constants[i] + words[i];
            const std::uint32_t sigma0 =
                rotate_right(a, 2) ^ rotate_right(a, 13) ^
                rotate_right(a, 22);
            const std::uint32_t majority =
                (a & b) ^ (a & c) ^ (b & c);
            const std::uint32_t temp2 = sigma0 + majority;
            h = g;
            g = f;
            f = e;
            e = d + temp1;
            d = c;
            c = b;
            b = a;
            a = temp1 + temp2;
        }
        state[0] += a;
        state[1] += b;
        state[2] += c;
        state[3] += d;
        state[4] += e;
        state[5] += f;
        state[6] += g;
        state[7] += h;
    }
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (const std::uint32_t word : state) {
        out << std::setw(8) << word;
    }
    return out.str();
}

std::string candidate_key(const Candidate& candidate) {
    const std::array<u64, 8> roots = {{
        candidate.b_roots.minus_root,
        candidate.b_roots.plus_root,
        candidate.c_roots.minus_root,
        candidate.c_roots.plus_root,
        candidate.sum_roots.minus_root,
        candidate.sum_roots.plus_root,
        candidate.difference_roots.minus_root,
        candidate.difference_roots.plus_root,
    }};
    std::ostringstream key;
    key << candidate.m << ',' << u128_decimal(candidate.b) << ','
        << u128_decimal(candidate.c);
    for (const u64 root : roots) {
        key << ',' << root;
    }
    return key.str();
}

std::string command_quote(const std::string& argument) {
    if (argument.find('"') != std::string::npos ||
        argument.find('\r') != std::string::npos ||
        argument.find('\n') != std::string::npos) {
        throw std::runtime_error("unsafe quote in command argument");
    }
    return '"' + argument + '"';
}

int normalize_system_exit(int raw_exit) {
    if (raw_exit == -1) {
        return -1;
    }
#ifdef _WIN32
    return raw_exit;
#else
    if (WIFEXITED(raw_exit)) {
        return WEXITSTATUS(raw_exit);
    }
    return -1;
#endif
}

struct VerifierConfig {
    std::string python;
    fs::path scalar;
    fs::path independent;
    fs::path run_directory;
};

struct VerifierEvidence {
    int scalar_exit = -1;
    int independent_exit = -1;
    std::string scalar_output;
    std::string independent_output;
};

VerifierEvidence run_both_verifiers(
    const Candidate& candidate,
    const VerifierConfig& config) {
    const fs::path scalar_output =
        config.run_directory / "scalar_verifier.pending.txt";
    const fs::path independent_output =
        config.run_directory / "independent_verifier.pending.txt";

    std::ostringstream scalar_command;
    scalar_command << command_quote(config.python) << ' '
                   << command_quote(config.scalar.string())
                   << " --msq-d " << candidate.m << ' '
                   << u128_decimal(candidate.b) << ' '
                   << u128_decimal(candidate.c) << " > "
                   << command_quote(scalar_output.string()) << " 2>&1";

    std::ostringstream independent_command;
    independent_command << command_quote(config.independent.string());
    for (const u128 entry : candidate.matrix) {
        independent_command << ' ' << u128_decimal(entry);
    }
    independent_command << " > "
                        << command_quote(independent_output.string())
                        << " 2>&1";

    VerifierEvidence evidence;
    evidence.scalar_exit =
        normalize_system_exit(std::system(scalar_command.str().c_str()));
    evidence.independent_exit = normalize_system_exit(
        std::system(independent_command.str().c_str()));
    evidence.scalar_output = read_file(scalar_output);
    evidence.independent_output = read_file(independent_output);

    std::error_code ignored;
    fs::remove(scalar_output, ignored);
    fs::remove(independent_output, ignored);
    return evidence;
}

std::string factorization_json(const Factorization& factors) {
    std::ostringstream out;
    out << '[';
    for (std::size_t i = 0; i < factors.size(); ++i) {
        if (i != 0) {
            out << ',';
        }
        out << "[\"" << factors[i].prime << "\","
            << factors[i].exponent << ']';
    }
    out << ']';
    return out.str();
}

std::string candidate_json(const Candidate& candidate,
                           const std::string& mode,
                           const Factorization& source_factorization,
                           const CenterData& center,
                           const VerifierEvidence& evidence,
                           const std::string& digest) {
    const auto roots_json = [](const RootPair& roots) {
        return std::string("[\"") + std::to_string(roots.minus_root) +
               "\",\"" + std::to_string(roots.plus_root) + "\"]";
    };
    std::ostringstream out;
    out << "{\n"
        << "  \"schema\":\"msq-d-gaussian-candidate-v1\",\n"
        << "  \"mode\":\"" << mode << "\",\n"
        << "  \"sha256\":\"" << digest << "\",\n"
        << "  \"source_m\":\"" << candidate.source_m << "\",\n"
        << "  \"source_factorization\":"
        << factorization_json(source_factorization) << ",\n"
        << "  \"source_r2_expected\":\""
        << u128_decimal(center.expected_r2) << "\",\n"
        << "  \"source_r2_enumerated\":\""
        << center.enumerated_r2 << "\",\n"
        << "  \"primitive_gcd\":\"" << candidate.primitive_gcd
        << "\",\n"
        << "  \"W\":{\"m\":\"" << candidate.m << "\",\"b\":\""
        << u128_decimal(candidate.b) << "\",\"c\":\""
        << u128_decimal(candidate.c) << "\",\"b_roots\":"
        << roots_json(candidate.b_roots) << ",\"c_roots\":"
        << roots_json(candidate.c_roots) << ",\"sum_roots\":"
        << roots_json(candidate.sum_roots)
        << ",\"difference_roots\":"
        << roots_json(candidate.difference_roots) << "},\n"
        << "  \"matrix\":[";
    for (std::size_t i = 0; i < candidate.matrix.size(); ++i) {
        if (i != 0) {
            out << ',';
        }
        out << '"' << u128_decimal(candidate.matrix[i]) << '"';
    }
    out << "],\n"
        << "  \"scalar_verifier\":{\"exit\":"
        << evidence.scalar_exit << ",\"output\":\""
        << json_escape(evidence.scalar_output) << "\"},\n"
        << "  \"independent_verifier\":{\"exit\":"
        << evidence.independent_exit << ",\"output\":\""
        << json_escape(evidence.independent_output) << "\"}\n"
        << "}\n";
    return out.str();
}

struct Options {
    bool inspect = false;
    std::string mode;
    u64 start = 0;
    u64 end = 0;
    u64 chunk_size = 65536;
    fs::path run_directory;
    fs::path scalar_verifier;
    fs::path independent_verifier;
    std::string python = "python";
    u64 deadline_unix = 0;
    bool resume = false;
};

Options parse_options(int argc, char* argv[]) {
    Options options;
    auto require_value = [&](int& index, const std::string& flag) {
        if (index + 1 >= argc) {
            throw std::runtime_error("missing value for " + flag);
        }
        return std::string(argv[++index]);
    };
    for (int i = 1; i < argc; ++i) {
        const std::string argument = argv[i];
        if (argument == "--inspect") {
            options.inspect = true;
        } else if (argument == "--mode") {
            options.mode = require_value(i, argument);
        } else if (argument == "--start") {
            options.start = parse_u64(require_value(i, argument));
        } else if (argument == "--end") {
            options.end = parse_u64(require_value(i, argument));
        } else if (argument == "--chunk-size") {
            options.chunk_size =
                parse_u64(require_value(i, argument));
        } else if (argument == "--run-dir") {
            options.run_directory = require_value(i, argument);
        } else if (argument == "--scalar-verifier") {
            options.scalar_verifier = require_value(i, argument);
        } else if (argument == "--independent-verifier") {
            options.independent_verifier = require_value(i, argument);
        } else if (argument == "--python") {
            options.python = require_value(i, argument);
        } else if (argument == "--deadline-unix") {
            options.deadline_unix =
                parse_u64(require_value(i, argument));
        } else if (argument == "--resume") {
            options.resume = true;
        } else if (argument == "--help" || argument == "-h") {
            std::cout
                << "Inspect: gaussian_center --inspect --start M --end M "
                   "[--chunk-size N]\n"
                << "Search: gaussian_center --mode G|N --start M --end M "
                   "--chunk-size N --run-dir DIR --scalar-verifier FILE "
                   "--independent-verifier EXE [--python EXE] "
                   "[--deadline-unix SEC] [--resume]\n";
            std::exit(0);
        } else {
            throw std::runtime_error("unknown option: " + argument);
        }
    }
    if (options.start == 0 || options.end < options.start ||
        options.end == std::numeric_limits<u64>::max()) {
        throw std::runtime_error(
            "a closed positive --start/--end range is required");
    }
    if (options.chunk_size == 0 ||
        options.chunk_size > 10000000ULL) {
        throw std::runtime_error(
            "--chunk-size must be in 1..10,000,000");
    }
    if (!options.inspect) {
        if (options.mode != "G" && options.mode != "N") {
            throw std::runtime_error("--mode must be G or N");
        }
        if (options.run_directory.empty() ||
            options.scalar_verifier.empty() ||
            options.independent_verifier.empty()) {
            throw std::runtime_error(
                "search mode requires run directory and both verifiers");
        }
    }
    return options;
}

struct RunState {
    u64 next_m = 0;
    u64 processed_centers = 0;
    u128 r2_total = 0;
    u128 deviation_total = 0;
    u128 additive_triples = 0;
    u64 verified_candidates = 0;
    int scalar_exit = -1;
    int independent_exit = -1;
    std::string status = "RUNNING";
    std::string candidate_sha256;
    std::string candidate_file;
    std::string error;
};

std::string summary_json(const Options& options,
                         const RunState& state) {
    std::ostringstream out;
    out << "{\n"
        << "  \"schema\":\"" << kSchema << "\",\n"
        << "  \"mode\":\"" << options.mode << "\",\n"
        << "  \"range_start\":\"" << options.start << "\",\n"
        << "  \"range_end\":\"" << options.end << "\",\n"
        << "  \"chunk_size\":\"" << options.chunk_size << "\",\n"
        << "  \"single_threaded\":true,\n"
        << "  \"status\":\"" << state.status << "\",\n"
        << "  \"next_m\":\"" << state.next_m << "\",\n"
        << "  \"processed_centers\":\"" << state.processed_centers
        << "\",\n"
        << "  \"r2_total\":\"" << u128_decimal(state.r2_total)
        << "\",\n"
        << "  \"deviation_total\":\""
        << u128_decimal(state.deviation_total) << "\",\n"
        << "  \"additive_triples\":\""
        << u128_decimal(state.additive_triples) << "\",\n"
        << "  \"verified_candidates\":\""
        << state.verified_candidates << "\",\n"
        << "  \"verification\":{\"scalar_exit\":"
        << state.scalar_exit << ",\"independent_exit\":"
        << state.independent_exit << "},\n"
        << "  \"candidate_sha256\":\""
        << json_escape(state.candidate_sha256) << "\",\n"
        << "  \"candidate_file\":\""
        << json_escape(state.candidate_file) << "\",\n"
        << "  \"error\":\"" << json_escape(state.error) << "\",\n"
        << "  \"result_scope\":\"closed_input_range_only\"\n"
        << "}\n";
    return out.str();
}

std::string extract_json_string(const std::string& json,
                                const std::string& key) {
    const std::regex pattern(
        "\"" + key + "\"\\s*:\\s*\"([^\"]*)\"");
    std::smatch match;
    if (!std::regex_search(json, match, pattern)) {
        throw std::runtime_error("summary missing key: " + key);
    }
    return match[1].str();
}

int extract_json_integer(const std::string& json,
                         const std::string& key) {
    const std::regex pattern(
        "\"" + key + "\"\\s*:\\s*(-?[0-9]+)");
    std::smatch match;
    if (!std::regex_search(json, match, pattern)) {
        throw std::runtime_error("summary missing integer key: " + key);
    }
    const long long value = std::stoll(match[1].str());
    if (value < std::numeric_limits<int>::min() ||
        value > std::numeric_limits<int>::max()) {
        throw std::runtime_error("summary integer out of range: " + key);
    }
    return static_cast<int>(value);
}

RunState load_summary(const Options& options,
                      const fs::path& path) {
    const std::string json = read_file(path);
    if (extract_json_string(json, "schema") != kSchema ||
        extract_json_string(json, "mode") != options.mode ||
        parse_u64(extract_json_string(json, "range_start")) !=
            options.start ||
        parse_u64(extract_json_string(json, "range_end")) != options.end ||
        parse_u64(extract_json_string(json, "chunk_size")) !=
            options.chunk_size) {
        throw std::runtime_error(
            "resume summary configuration mismatch");
    }
    RunState state;
    state.status = extract_json_string(json, "status");
    state.next_m = parse_u64(extract_json_string(json, "next_m"));
    state.processed_centers =
        parse_u64(extract_json_string(json, "processed_centers"));
    state.r2_total =
        parse_u128(extract_json_string(json, "r2_total"));
    state.deviation_total =
        parse_u128(extract_json_string(json, "deviation_total"));
    state.additive_triples =
        parse_u128(extract_json_string(json, "additive_triples"));
    state.verified_candidates =
        parse_u64(extract_json_string(json, "verified_candidates"));
    state.scalar_exit =
        extract_json_integer(json, "scalar_exit");
    state.independent_exit =
        extract_json_integer(json, "independent_exit");
    state.candidate_sha256 =
        extract_json_string(json, "candidate_sha256");
    state.candidate_file =
        extract_json_string(json, "candidate_file");
    state.error = extract_json_string(json, "error");
    return state;
}

u64 unix_seconds_now() {
    return static_cast<u64>(
        std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch())
            .count());
}

void emit_inspection(const CenterData& center) {
    std::cout << "{\"m\":" << center.m << ",\"r2\":"
              << center.enumerated_r2 << ",\"pairs\":[";
    bool first = true;
    for (const auto& item : center.deviations) {
        if (!first) {
            std::cout << ',';
        }
        first = false;
        std::cout << "[\"" << u128_decimal(item.first) << "\","
                  << item.second.minus_root << ','
                  << item.second.plus_root << ']';
    }
    std::cout << "]}\n";
}

int inspect_range(const Options& options) {
    const u64 sieve_limit = floor_sqrt_u64(options.end);
    const auto primes = primes_through(sieve_limit);
    GaussianEnumerator enumerator(sieve_limit);
    u64 next = options.start;
    while (next <= options.end) {
        const u64 remaining = options.end - next;
        const u64 span =
            std::min(options.chunk_size - 1, remaining);
        const u64 chunk_end = next + span;
        const auto factors =
            factor_closed_chunk(next, chunk_end, primes);
        for (std::size_t index = 0; index < factors.size(); ++index) {
            const u64 m = next + static_cast<u64>(index);
            emit_inspection(enumerator.enumerate(m, factors[index]));
        }
        next = chunk_end + 1;
    }
    return 0;
}

int search_range(const Options& options) {
    fs::create_directories(options.run_directory);
    const fs::path summary_path =
        options.run_directory / "summary.json";
    RunState state;
    if (fs::exists(summary_path)) {
        if (!options.resume) {
            throw std::runtime_error(
                "summary exists; pass --resume or choose a new run dir");
        }
        state = load_summary(options, summary_path);
        if (state.status == "G_FAIL" || state.status == "N_FAIL" ||
            state.status == "CANDIDATE_VERIFIED") {
            std::cout << summary_json(options, state);
            return 0;
        }
        if (state.status == "FAILED") {
            throw std::runtime_error(
                "refusing to resume FAILED state: " + state.error);
        }
        if (state.status != "RUNNING" &&
            state.status != "TIMEOUT_INCOMPLETE") {
            throw std::runtime_error(
                "unrecognized resumable status: " + state.status);
        }
        state.status = "RUNNING";
        state.error.clear();
    } else {
        state.next_m = options.start;
        atomic_write(summary_path, summary_json(options, state));
    }

    const u64 sieve_limit = floor_sqrt_u64(options.end);
    const auto primes = primes_through(sieve_limit);
    GaussianEnumerator enumerator(sieve_limit);
    const VerifierConfig verifier_config = {
        options.python,
        fs::absolute(options.scalar_verifier),
        fs::absolute(options.independent_verifier),
        fs::absolute(options.run_directory),
    };

    while (state.next_m <= options.end) {
        if (options.deadline_unix != 0 &&
            unix_seconds_now() >= options.deadline_unix) {
            state.status = "TIMEOUT_INCOMPLETE";
            atomic_write(summary_path, summary_json(options, state));
            std::cout << summary_json(options, state);
            return 0;
        }
        const u64 chunk_start = state.next_m;
        const u64 span = std::min(
            options.chunk_size - 1, options.end - chunk_start);
        const u64 chunk_end = chunk_start + span;
        const auto chunk_factors =
            factor_closed_chunk(chunk_start, chunk_end, primes);
        for (std::size_t index = 0;
             index < chunk_factors.size();
             ++index) {
            const u64 m = chunk_start + static_cast<u64>(index);
            if (options.deadline_unix != 0 &&
                unix_seconds_now() >= options.deadline_unix) {
                state.next_m = m;
                state.status = "TIMEOUT_INCOMPLETE";
                atomic_write(summary_path, summary_json(options, state));
                std::cout << summary_json(options, state);
                return 0;
            }
            const CenterData center =
                enumerator.enumerate(m, chunk_factors[index]);
            u128 center_additive_triples = 0;
            const auto candidate =
                find_candidate(center, center_additive_triples);
            state.r2_total += center.expected_r2;
            state.deviation_total += center.deviations.size();
            state.additive_triples += center_additive_triples;
            ++state.processed_centers;
            state.next_m = m + 1;

            if (candidate.has_value()) {
                const VerifierEvidence evidence =
                    run_both_verifiers(*candidate, verifier_config);
                state.scalar_exit = evidence.scalar_exit;
                state.independent_exit = evidence.independent_exit;
                if (evidence.scalar_exit != 0 ||
                    evidence.independent_exit != 0) {
                    state.status = "FAILED";
                    state.error =
                        "internal candidate rejected by verifier exits " +
                        std::to_string(evidence.scalar_exit) + "," +
                        std::to_string(evidence.independent_exit);
                    atomic_write(summary_path,
                                 summary_json(options, state));
                    throw std::runtime_error(state.error);
                }
                const std::string key = candidate_key(*candidate);
                const std::string digest = sha256(key);
                const fs::path candidate_path =
                    options.run_directory / "candidates" /
                    (digest + ".json");
                const std::string output = candidate_json(
                    *candidate,
                    options.mode,
                    chunk_factors[index],
                    center,
                    evidence,
                    digest);
                atomic_write(candidate_path, output);
                state.status = "CANDIDATE_VERIFIED";
                state.candidate_sha256 = digest;
                state.candidate_file =
                    fs::absolute(candidate_path).string();
                state.verified_candidates = 1;
                atomic_write(summary_path, summary_json(options, state));
                std::cout << summary_json(options, state);
                return 0;
            }
        }
        atomic_write(summary_path, summary_json(options, state));
    }

    state.status = options.mode == "G" ? "G_FAIL" : "N_FAIL";
    atomic_write(summary_path, summary_json(options, state));
    std::cout << summary_json(options, state);
    return 0;
}

}  // namespace

int main(int argc, char* argv[]) {
    std::optional<Options> options;
    try {
        options = parse_options(argc, argv);
        if (options->inspect) {
            return inspect_range(*options);
        }
        return search_range(*options);
    } catch (const std::exception& error) {
        if (options.has_value() && !options->inspect &&
            !options->run_directory.empty()) {
            try {
                const fs::path summary_path =
                    options->run_directory / "summary.json";
                RunState state;
                if (fs::exists(summary_path)) {
                    state = load_summary(*options, summary_path);
                } else {
                    state.next_m = options->start;
                }
                state.status = "FAILED";
                state.error = error.what();
                atomic_write(summary_path,
                             summary_json(*options, state));
            } catch (...) {
            }
        }
        std::cerr << "{\"status\":\"FAILED\",\"error\":\""
                  << json_escape(error.what()) << "\"}\n";
        return 2;
    }
}
