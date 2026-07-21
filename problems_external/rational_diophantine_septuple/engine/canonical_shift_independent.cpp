#include <boost/multiprecision/cpp_int.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>

#include <algorithm>
#include <array>
#include <bit>
#include <cctype>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

using boost::multiprecision::cpp_int;
namespace fs = std::filesystem;
namespace pt = boost::property_tree;

namespace {

constexpr std::string_view kSchema = "canonical_shift_manifest/v1";
constexpr std::string_view kRoute = "terminal embedded-triple canonical shift";
constexpr std::string_view kSourceRelative =
    "problems_external/rational_diophantine_septuple/sources/2001.sextuples.txt";
constexpr std::string_view kSourceSha =
    "426551F283946C238E0B2FF54B8D2C1454B1717F701DCA7862FD8C98892AF933";
constexpr std::string_view kPrimaryVerifierRelative =
    "problems_external/rational_diophantine_septuple/engine/verify_tuple.py";
constexpr std::string_view kPrimaryVerifierSha =
    "E0B86F53FFA3769EBF2D37F5571DC20414272DC0024944E75E61F217DAD36D33";
constexpr std::string_view kIndependentVerifierRelative =
    "problems_external/rational_diophantine_septuple/engine/verify_septuple_independent.py";
constexpr std::string_view kIndependentVerifierSha =
    "0750D1B36B8ADCCC191072BE4C2011AA7126986F3E16EAD64BE2CB17FB934679";
constexpr std::string_view kIndependentSourceRelative =
    "problems_external/rational_diophantine_septuple/engine/canonical_shift_independent.cpp";
constexpr std::string_view kIndependentBinaryRelative =
    "problems_external/rational_diophantine_septuple/engine/canonical_shift_independent.exe";
constexpr std::string_view kLedgerHeader =
    "ordinal\trecord_id\ti\tj\tk\tposition_mask\tsign\tr_num\tr_den\ts_num\ts_den\t"
    "t_num\tt_den\td_num\td_den\tdegeneracy\tcomp0\tcomp1\tcomp2\tsurvivor";
constexpr std::string_view kFullToken = "CANONICAL_SHIFT_ALL_80040_FROZEN";

const std::array<std::array<int, 3>, 20> kTriples{{
    {{0, 1, 2}}, {{0, 1, 3}}, {{0, 1, 4}}, {{0, 1, 5}},
    {{0, 2, 3}}, {{0, 2, 4}}, {{0, 2, 5}}, {{0, 3, 4}},
    {{0, 3, 5}}, {{0, 4, 5}}, {{1, 2, 3}}, {{1, 2, 4}},
    {{1, 2, 5}}, {{1, 3, 4}}, {{1, 3, 5}}, {{1, 4, 5}},
    {{2, 3, 4}}, {{2, 3, 5}}, {{2, 4, 5}}, {{3, 4, 5}},
}};
const std::array<int, 2> kSigns{{-1, 1}};
const std::array<int, 10> kCalibrationIds{{1, 2, 5, 12, 100, 251, 501, 1000, 1500, 2001}};

std::string trim(std::string text) {
    auto first = std::find_if_not(text.begin(), text.end(), [](unsigned char c) {
        return std::isspace(c) != 0;
    });
    auto last = std::find_if_not(text.rbegin(), text.rend(), [](unsigned char c) {
        return std::isspace(c) != 0;
    }).base();
    if (first >= last) {
        return {};
    }
    return std::string(first, last);
}

std::string upper_ascii(std::string text) {
    for (char& c : text) {
        c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
    }
    return text;
}

cpp_int absolute(cpp_int value) {
    return value < 0 ? -value : value;
}

cpp_int gcd(cpp_int left, cpp_int right) {
    left = absolute(left);
    right = absolute(right);
    while (right != 0) {
        cpp_int remainder = left % right;
        left = right;
        right = remainder;
    }
    return left;
}

cpp_int parse_integer(const std::string& raw) {
    const std::string text = trim(raw);
    if (text.empty()) {
        throw std::runtime_error("empty integer token");
    }
    std::size_t offset = 0;
    bool negative = false;
    if (text[offset] == '+' || text[offset] == '-') {
        negative = text[offset] == '-';
        ++offset;
    }
    if (offset == text.size()) {
        throw std::runtime_error("sign without integer digits: " + text);
    }
    cpp_int value = 0;
    for (; offset < text.size(); ++offset) {
        const unsigned char c = static_cast<unsigned char>(text[offset]);
        if (!std::isdigit(c)) {
            throw std::runtime_error("invalid integer token: " + text);
        }
        value *= 10;
        value += static_cast<unsigned>(c - '0');
    }
    return negative ? -value : value;
}

std::string integer_text(const cpp_int& value) {
    std::ostringstream stream;
    stream << value;
    return stream.str();
}

struct Rational {
    cpp_int num{0};
    cpp_int den{1};

    Rational() = default;
    Rational(long long integer) : num(integer), den(1) {}
    Rational(cpp_int numerator, cpp_int denominator) : num(std::move(numerator)), den(std::move(denominator)) {
        normalize();
    }

    void normalize() {
        if (den == 0) {
            throw std::runtime_error("zero rational denominator");
        }
        if (den < 0) {
            num = -num;
            den = -den;
        }
        if (num == 0) {
            den = 1;
            return;
        }
        const cpp_int divisor = gcd(num, den);
        num /= divisor;
        den /= divisor;
    }

    static Rational parse(const std::string& raw) {
        const std::string text = trim(raw);
        const std::size_t slash = text.find('/');
        if (slash == std::string::npos) {
            return Rational(parse_integer(text), 1);
        }
        if (text.find('/', slash + 1) != std::string::npos) {
            throw std::runtime_error("multiple rational separators: " + text);
        }
        return Rational(parse_integer(text.substr(0, slash)), parse_integer(text.substr(slash + 1)));
    }
};

Rational operator+(const Rational& left, const Rational& right) {
    return Rational(left.num * right.den + right.num * left.den, left.den * right.den);
}

Rational operator*(const Rational& left, const Rational& right) {
    if (left.num == 0 || right.num == 0) {
        return Rational(0);
    }
    cpp_int left_num = left.num;
    cpp_int left_den = left.den;
    cpp_int right_num = right.num;
    cpp_int right_den = right.den;
    const cpp_int cross_one = gcd(left_num, right_den);
    const cpp_int cross_two = gcd(right_num, left_den);
    left_num /= cross_one;
    right_den /= cross_one;
    right_num /= cross_two;
    left_den /= cross_two;
    return Rational(left_num * right_num, left_den * right_den);
}

bool operator==(const Rational& left, const Rational& right) {
    return left.num == right.num && left.den == right.den;
}

bool operator!=(const Rational& left, const Rational& right) {
    return !(left == right);
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
        const cpp_int next = (estimate + value / estimate) >> 1;
        if (next >= estimate) {
            break;
        }
        estimate = next;
    }
    while ((estimate + 1) * (estimate + 1) <= value) {
        ++estimate;
    }
    while (estimate * estimate > value) {
        --estimate;
    }
    return estimate;
}

std::optional<Rational> rational_square_root(const Rational& value) {
    if (value.num < 0) {
        return std::nullopt;
    }
    const cpp_int numerator_root = integer_square_root(value.num);
    if (numerator_root * numerator_root != value.num) {
        return std::nullopt;
    }
    const cpp_int denominator_root = integer_square_root(value.den);
    if (denominator_root * denominator_root != value.den) {
        return std::nullopt;
    }
    return Rational(numerator_root, denominator_root);
}

Rational product_plus_one(const Rational& left, const Rational& right) {
    return left * right + Rational(1);
}

// This SHA-256 implementation is self-contained so the independent executable
// does not rely on a shell utility or on the primary Python implementation.
class Sha256 {
  public:
    void update(const unsigned char* bytes, std::size_t length) {
        total_bytes_ += length;
        while (length > 0) {
            const std::size_t amount = std::min(length, block_.size() - block_used_);
            std::copy_n(bytes, amount, block_.begin() + static_cast<std::ptrdiff_t>(block_used_));
            block_used_ += amount;
            bytes += amount;
            length -= amount;
            if (block_used_ == block_.size()) {
                transform(block_.data());
                block_used_ = 0;
            }
        }
    }

    std::string finish() {
        const std::uint64_t bit_length = total_bytes_ * 8;
        block_[block_used_++] = 0x80;
        if (block_used_ > 56) {
            std::fill(block_.begin() + static_cast<std::ptrdiff_t>(block_used_), block_.end(), 0);
            transform(block_.data());
            block_used_ = 0;
        }
        std::fill(block_.begin() + static_cast<std::ptrdiff_t>(block_used_), block_.begin() + 56, 0);
        for (int index = 0; index < 8; ++index) {
            block_[63 - index] = static_cast<unsigned char>(bit_length >> (8 * index));
        }
        transform(block_.data());
        std::ostringstream stream;
        stream << std::uppercase << std::hex << std::setfill('0');
        for (std::uint32_t word : state_) {
            stream << std::setw(8) << word;
        }
        return stream.str();
    }

  private:
    static constexpr std::array<std::uint32_t, 64> constants_{{
        0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U, 0x3956c25bU, 0x59f111f1U,
        0x923f82a4U, 0xab1c5ed5U, 0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U,
        0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U, 0xe49b69c1U, 0xefbe4786U,
        0x0fc19dc6U, 0x240ca1ccU, 0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
        0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U, 0xc6e00bf3U, 0xd5a79147U,
        0x06ca6351U, 0x14292967U, 0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U,
        0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U, 0xa2bfe8a1U, 0xa81a664bU,
        0xc24b8b70U, 0xc76c51a3U, 0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
        0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U, 0x391c0cb3U, 0x4ed8aa4aU,
        0x5b9cca4fU, 0x682e6ff3U, 0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
        0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U,
    }};

    static std::uint32_t rotate_right(std::uint32_t value, unsigned count) {
        return (value >> count) | (value << (32 - count));
    }

    void transform(const unsigned char* bytes) {
        std::array<std::uint32_t, 64> words{};
        for (int index = 0; index < 16; ++index) {
            words[index] = (static_cast<std::uint32_t>(bytes[index * 4]) << 24) |
                           (static_cast<std::uint32_t>(bytes[index * 4 + 1]) << 16) |
                           (static_cast<std::uint32_t>(bytes[index * 4 + 2]) << 8) |
                           static_cast<std::uint32_t>(bytes[index * 4 + 3]);
        }
        for (int index = 16; index < 64; ++index) {
            const std::uint32_t s0 = rotate_right(words[index - 15], 7) ^
                                     rotate_right(words[index - 15], 18) ^
                                     (words[index - 15] >> 3);
            const std::uint32_t s1 = rotate_right(words[index - 2], 17) ^
                                     rotate_right(words[index - 2], 19) ^
                                     (words[index - 2] >> 10);
            words[index] = words[index - 16] + s0 + words[index - 7] + s1;
        }
        std::uint32_t a = state_[0];
        std::uint32_t b = state_[1];
        std::uint32_t c = state_[2];
        std::uint32_t d = state_[3];
        std::uint32_t e = state_[4];
        std::uint32_t f = state_[5];
        std::uint32_t g = state_[6];
        std::uint32_t h = state_[7];
        for (int index = 0; index < 64; ++index) {
            const std::uint32_t big_s1 = rotate_right(e, 6) ^ rotate_right(e, 11) ^ rotate_right(e, 25);
            const std::uint32_t choose = (e & f) ^ ((~e) & g);
            const std::uint32_t temp_one = h + big_s1 + choose + constants_[index] + words[index];
            const std::uint32_t big_s0 = rotate_right(a, 2) ^ rotate_right(a, 13) ^ rotate_right(a, 22);
            const std::uint32_t majority = (a & b) ^ (a & c) ^ (b & c);
            const std::uint32_t temp_two = big_s0 + majority;
            h = g;
            g = f;
            f = e;
            e = d + temp_one;
            d = c;
            c = b;
            b = a;
            a = temp_one + temp_two;
        }
        state_[0] += a;
        state_[1] += b;
        state_[2] += c;
        state_[3] += d;
        state_[4] += e;
        state_[5] += f;
        state_[6] += g;
        state_[7] += h;
    }

    std::array<std::uint32_t, 8> state_{{
        0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
        0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U,
    }};
    std::array<unsigned char, 64> block_{};
    std::size_t block_used_{0};
    std::uint64_t total_bytes_{0};
};

std::string sha256_file(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("cannot open file for SHA-256: " + path.string());
    }
    Sha256 hash;
    std::array<unsigned char, 1 << 16> buffer{};
    while (input) {
        input.read(reinterpret_cast<char*>(buffer.data()), static_cast<std::streamsize>(buffer.size()));
        const std::streamsize count = input.gcount();
        if (count > 0) {
            hash.update(buffer.data(), static_cast<std::size_t>(count));
        }
    }
    if (!input.eof()) {
        throw std::runtime_error("read failure during SHA-256: " + path.string());
    }
    return hash.finish();
}

struct Record {
    int id{};
    std::array<Rational, 6> values{};
};

std::vector<std::string> split_commas(const std::string& text) {
    std::vector<std::string> fields;
    std::size_t begin = 0;
    while (true) {
        const std::size_t comma = text.find(',', begin);
        fields.push_back(trim(text.substr(begin, comma == std::string::npos ? comma : comma - begin)));
        if (comma == std::string::npos) {
            break;
        }
        begin = comma + 1;
    }
    return fields;
}

std::vector<Record> parse_catalogue(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("cannot open catalogue: " + path.string());
    }
    std::vector<Record> records;
    std::string line;
    while (std::getline(input, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (line.size() < 5 || line[0] != '(' ||
            !std::isdigit(static_cast<unsigned char>(line[1]))) {
            continue;
        }
        const std::size_t close_parenthesis = line.find(')', 2);
        if (close_parenthesis == std::string::npos) {
            throw std::runtime_error("malformed record identifier line");
        }
        int id = 0;
        for (std::size_t index = 1; index < close_parenthesis; ++index) {
            const unsigned char c = static_cast<unsigned char>(line[index]);
            if (!std::isdigit(c)) {
                throw std::runtime_error("nondigit in record identifier");
            }
            id = id * 10 + static_cast<int>(c - '0');
        }
        std::size_t open_bracket = close_parenthesis + 1;
        if (open_bracket >= line.size() ||
            !std::isspace(static_cast<unsigned char>(line[open_bracket]))) {
            throw std::runtime_error("record identifier is not followed by whitespace");
        }
        while (open_bracket < line.size() &&
               std::isspace(static_cast<unsigned char>(line[open_bracket]))) {
            ++open_bracket;
        }
        if (open_bracket >= line.size() || line[open_bracket] != '[') {
            throw std::runtime_error("record values do not begin with '['");
        }
        const std::size_t close_bracket = line.find(']', open_bracket + 1);
        if (close_bracket == std::string::npos) {
            throw std::runtime_error("record values do not end with ']'");
        }
        const std::vector<std::string> fields =
            split_commas(line.substr(open_bracket + 1, close_bracket - open_bracket - 1));
        if (fields.size() != 6) {
            throw std::runtime_error("record " + std::to_string(id) + " does not contain six fields");
        }
        Record record;
        record.id = id;
        for (std::size_t index = 0; index < fields.size(); ++index) {
            record.values[index] = Rational::parse(fields[index]);
        }
        records.push_back(std::move(record));
    }
    if (!input.eof()) {
        throw std::runtime_error("catalogue read failure");
    }
    if (records.size() != 2001) {
        throw std::runtime_error("catalogue record count mismatch: " + std::to_string(records.size()));
    }
    for (std::size_t index = 0; index < records.size(); ++index) {
        if (records[index].id != static_cast<int>(index + 1)) {
            throw std::runtime_error("catalogue record identifiers are not consecutive");
        }
    }
    return records;
}

std::size_t validate_catalogue(const std::vector<Record>& records) {
    std::size_t square_count = 0;
    for (const Record& record : records) {
        for (int left = 0; left < 6; ++left) {
            if (record.values[left].num == 0) {
                throw std::runtime_error("zero source entry in record " + std::to_string(record.id));
            }
            for (int earlier = 0; earlier < left; ++earlier) {
                if (record.values[left] == record.values[earlier]) {
                    throw std::runtime_error("duplicate source entry in record " + std::to_string(record.id));
                }
            }
            for (int right = left + 1; right < 6; ++right) {
                if (!rational_square_root(product_plus_one(record.values[left], record.values[right]))) {
                    throw std::runtime_error("nonsquare source pair in record " + std::to_string(record.id) +
                                             " at " + std::to_string(left) + "," + std::to_string(right));
                }
                ++square_count;
            }
        }
    }
    if (square_count != 2001ULL * 15ULL) {
        throw std::runtime_error("source pair validation count mismatch");
    }
    return square_count;
}

template <typename T, std::size_t N>
void require_array(const pt::ptree& parent, const std::string& key, const std::array<T, N>& expected) {
    const auto& child = parent.get_child(key);
    std::size_t index = 0;
    for (const auto& element : child) {
        if (!element.first.empty() || index >= N || element.second.get_value<T>() != expected[index]) {
            throw std::runtime_error("manifest array mismatch: " + key);
        }
        ++index;
    }
    if (index != N) {
        throw std::runtime_error("manifest array length mismatch: " + key);
    }
}

void require_text(const pt::ptree& tree, const std::string& key, std::string_view expected) {
    if (tree.get<std::string>(key) != expected) {
        throw std::runtime_error("manifest field mismatch: " + key);
    }
}

template <typename T>
void require_value(const pt::ptree& tree, const std::string& key, const T& expected) {
    if (tree.get<T>(key) != expected) {
        throw std::runtime_error("manifest field mismatch: " + key);
    }
}

struct Manifest {
    pt::ptree tree;
    fs::path source_path;
    std::vector<int> calibration_ids;
    fs::path full_output_dir;
};

Manifest validate_manifest(const fs::path& manifest_path, const fs::path& workspace_root,
                           const std::string& expected_manifest_sha, bool full_mode) {
    const std::string observed_manifest_sha = sha256_file(manifest_path);
    if (upper_ascii(expected_manifest_sha) != observed_manifest_sha) {
        throw std::runtime_error("manifest SHA-256 mismatch: " + observed_manifest_sha);
    }
    std::ifstream manifest_text(manifest_path, std::ios::binary);
    std::ostringstream contents;
    contents << manifest_text.rdbuf();
    if (!manifest_text || (full_mode && contents.str().find("PENDING") != std::string::npos)) {
        throw std::runtime_error(full_mode ? "full mode rejects a manifest containing PENDING"
                                           : "manifest read failure");
    }

    Manifest result;
    pt::read_json(manifest_path.string(), result.tree);
    require_text(result.tree, "schema", kSchema);
    require_text(result.tree, "route", kRoute);
    require_text(result.tree, "source.path", kSourceRelative);
    require_text(result.tree, "source.sha256", kSourceSha);
    require_text(result.tree, "source.record_regex", R"(^\((\d+)\)\s+\[([^]]+)\])");
    require_value(result.tree, "source.record_count", 2001);
    require_value(result.tree, "source.values_per_record", 6);
    require_value(result.tree, "source.required_square_pairs_per_record", 15);
    require_value(result.tree, "enumeration.position_base", 0);
    require_array(result.tree, "enumeration.signs", kSigns);
    require_text(result.tree, "enumeration.root_convention",
                 "nonnegative reduced rational roots for ab+1, ac+1, bc+1");
    require_text(result.tree, "enumeration.candidate_formula",
                 "d=a+b+c+2*a*b*c+sign*2*r*s*t");
    require_text(result.tree, "enumeration.record_order", "increasing record_id 1..2001");
    require_text(result.tree, "enumeration.triple_order", "listed lexicographic order");
    require_text(result.tree, "enumeration.sign_order", "-1 then +1");
    require_value(result.tree, "enumeration.declared_contexts", 80040);

    const auto& manifest_triples = result.tree.get_child("enumeration.position_triples");
    std::size_t triple_index = 0;
    for (const auto& entry : manifest_triples) {
        if (!entry.first.empty() || triple_index >= kTriples.size()) {
            throw std::runtime_error("manifest position-triple array mismatch");
        }
        require_array(entry.second, "positions", kTriples[triple_index]);
        const int expected_mask = (1 << kTriples[triple_index][0]) |
                                  (1 << kTriples[triple_index][1]) |
                                  (1 << kTriples[triple_index][2]);
        require_value(entry.second, "mask", expected_mask);
        ++triple_index;
    }
    if (triple_index != kTriples.size()) {
        throw std::runtime_error("manifest position-triple count mismatch");
    }

    require_text(result.tree, "engines.independent_source.path", kIndependentSourceRelative);
    require_text(result.tree, "engines.independent_binary.path", kIndependentBinaryRelative);
    require_text(result.tree, "verifiers.primary.path", kPrimaryVerifierRelative);
    require_text(result.tree, "verifiers.primary.sha256", kPrimaryVerifierSha);
    require_text(result.tree, "verifiers.independent.path", kIndependentVerifierRelative);
    require_text(result.tree, "verifiers.independent.sha256", kIndependentVerifierSha);
    require_text(result.tree, "ledger.encoding", "ASCII TSV with LF");
    require_text(result.tree, "ledger.header", kLedgerHeader);
    require_text(result.tree, "ledger.rational_normalization",
                 "gcd-reduced numerator and positive denominator");
    require_text(result.tree, "ledger.complement_bits",
                 "three exact 0/1 square-test results in increasing complementary-position order");
    require_text(result.tree, "ledger.survivor_rule",
                 "1 exactly when degeneracy is DISTINCT_NONZERO and comp0=comp1=comp2=1");
    require_value(result.tree, "ledger.retain_every_context", true);
    require_text(result.tree, "ledger.full_ledger_filename", "ledger.tsv");
    require_text(result.tree, "ledger.full_summary_filename", "summary.json");
    require_text(result.tree, "ledger.full_survivors_filename", "survivors.json");
    require_array(result.tree, "calibration.record_ids", kCalibrationIds);
    require_value(result.tree, "calibration.declared_contexts", 400);

    const std::array<int, 2> ordinal_range{{0, 80039}};
    require_array(result.tree, "ledger.ordinal_range", ordinal_range);
    const std::array<std::string, 4> labels{{
        "ZERO", "SELECTED_DUPLICATE", "COMPLEMENT_DUPLICATE", "DISTINCT_NONZERO"}};
    require_array(result.tree, "ledger.degeneracy_labels", labels);
    require_array(result.tree, "ledger.degeneracy_precedence", labels);

    result.source_path = workspace_root / fs::path(std::string(kSourceRelative));
    result.full_output_dir = workspace_root / result.tree.get<std::string>("outputs.independent_dir");
    result.calibration_ids.assign(kCalibrationIds.begin(), kCalibrationIds.end());

    if (sha256_file(result.source_path) != kSourceSha) {
        throw std::runtime_error("catalogue SHA-256 does not match frozen manifest");
    }
    const fs::path primary_verifier = workspace_root / fs::path(std::string(kPrimaryVerifierRelative));
    const fs::path independent_verifier = workspace_root / fs::path(std::string(kIndependentVerifierRelative));
    if (sha256_file(primary_verifier) != kPrimaryVerifierSha ||
        sha256_file(independent_verifier) != kIndependentVerifierSha) {
        throw std::runtime_error("full-verifier SHA-256 mismatch");
    }
    const std::string source_sha = upper_ascii(result.tree.get<std::string>("engines.independent_source.sha256"));
    const std::string binary_sha = upper_ascii(result.tree.get<std::string>("engines.independent_binary.sha256"));
    if (source_sha != "PENDING" &&
        sha256_file(workspace_root / fs::path(std::string(kIndependentSourceRelative))) != source_sha) {
        throw std::runtime_error("independent source SHA-256 mismatch");
    }
    if (binary_sha != "PENDING" &&
        sha256_file(workspace_root / fs::path(std::string(kIndependentBinaryRelative))) != binary_sha) {
        throw std::runtime_error("independent binary SHA-256 mismatch");
    }
    if (full_mode) {
        if (sha256_file(workspace_root / fs::path(std::string(kIndependentSourceRelative))) != source_sha ||
            sha256_file(workspace_root / fs::path(std::string(kIndependentBinaryRelative))) != binary_sha) {
            throw std::runtime_error("independent engine SHA-256 mismatch");
        }
    }
    return result;
}

struct Options {
    fs::path workspace_root;
    fs::path manifest_path;
    fs::path output_path;
    fs::path summary_path;
    fs::path survivors_path;
    std::string manifest_sha;
    std::string mode;
    std::string full_token;
};

void usage() {
    std::cerr << "Usage: canonical_shift_independent.exe --workspace-root DIR --manifest FILE "
                 "--expected-manifest-sha256 HEX --mode calibration|full --output FILE "
                 "--summary FILE "
                 "[--survivors FILE --full-token CANONICAL_SHIFT_ALL_80040_FROZEN]\n";
}

Options parse_options(int argc, char** argv) {
    Options options;
    for (int index = 1; index < argc; ++index) {
        const std::string key = argv[index];
        if (index + 1 >= argc) {
            throw std::runtime_error("missing value after " + key);
        }
        const std::string value = argv[++index];
        if (key == "--workspace-root") {
            options.workspace_root = value;
        } else if (key == "--manifest") {
            options.manifest_path = value;
        } else if (key == "--expected-manifest-sha256") {
            options.manifest_sha = value;
        } else if (key == "--mode") {
            options.mode = value;
        } else if (key == "--output") {
            options.output_path = value;
        } else if (key == "--summary") {
            options.summary_path = value;
        } else if (key == "--survivors") {
            options.survivors_path = value;
        } else if (key == "--full-token") {
            options.full_token = value;
        } else {
            throw std::runtime_error("unknown option: " + key);
        }
    }
    if (options.workspace_root.empty() || options.manifest_path.empty() || options.output_path.empty() ||
        options.summary_path.empty() ||
        options.manifest_sha.empty() || (options.mode != "calibration" && options.mode != "full")) {
        throw std::runtime_error("missing or invalid required option");
    }
    options.workspace_root = fs::absolute(options.workspace_root).lexically_normal();
    options.manifest_path = fs::absolute(options.manifest_path).lexically_normal();
    options.output_path = fs::absolute(options.output_path).lexically_normal();
    options.summary_path = fs::absolute(options.summary_path).lexically_normal();
    if (!options.survivors_path.empty()) {
        options.survivors_path = fs::absolute(options.survivors_path).lexically_normal();
    }
    return options;
}

std::string classify(const Rational& candidate, const std::array<Rational, 3>& selected,
                     const std::array<Rational, 3>& complement) {
    if (candidate.num == 0) {
        return "ZERO";
    }
    if (std::find(selected.begin(), selected.end(), candidate) != selected.end()) {
        return "SELECTED_DUPLICATE";
    }
    if (std::find(complement.begin(), complement.end(), candidate) != complement.end()) {
        return "COMPLEMENT_DUPLICATE";
    }
    return "DISTINCT_NONZERO";
}

struct Counts {
    std::size_t rows{};
    std::size_t zero{};
    std::size_t selected_duplicate{};
    std::size_t complement_duplicate{};
    std::size_t distinct_nonzero{};
    std::size_t survivors{};
    std::array<std::size_t, 8> complement_patterns{};
};

struct Survivor {
    std::size_t ordinal{};
    int record_id{};
    std::array<int, 3> positions{};
    int sign{};
    std::array<Rational, 6> source_values{};
    Rational candidate{};
};

void enumerate_record(const Record& record, std::ostream& output, Counts& counts,
                      std::vector<Survivor>& survivors) {
    for (std::size_t triple_index = 0; triple_index < kTriples.size(); ++triple_index) {
        const auto positions = kTriples[triple_index];
        const int position_mask = (1 << positions[0]) | (1 << positions[1]) | (1 << positions[2]);
        const std::array<Rational, 3> selected{{
            record.values[positions[0]], record.values[positions[1]], record.values[positions[2]]}};
        std::array<Rational, 3> complement;
        std::size_t complement_index = 0;
        for (int position = 0; position < 6; ++position) {
            if ((position_mask & (1 << position)) == 0) {
                complement[complement_index++] = record.values[position];
            }
        }
        const auto root_r = rational_square_root(product_plus_one(selected[0], selected[1]));
        const auto root_s = rational_square_root(product_plus_one(selected[0], selected[2]));
        const auto root_t = rational_square_root(product_plus_one(selected[1], selected[2]));
        if (!root_r || !root_s || !root_t) {
            throw std::runtime_error("selected triple root failure in record " + std::to_string(record.id));
        }
        for (std::size_t sign_index = 0; sign_index < kSigns.size(); ++sign_index) {
            const int sign = kSigns[sign_index];
            const Rational abc = selected[0] * selected[1] * selected[2];
            const Rational rst = (*root_r) * (*root_s) * (*root_t);
            const Rational candidate = selected[0] + selected[1] + selected[2] +
                                       Rational(2) * abc + Rational(sign * 2) * rst;

            const Rational identity_a = selected[0] * (*root_t) + Rational(sign) * (*root_r) * (*root_s);
            const Rational identity_b = selected[1] * (*root_s) + Rational(sign) * (*root_r) * (*root_t);
            const Rational identity_c = selected[2] * (*root_r) + Rational(sign) * (*root_s) * (*root_t);
            if (product_plus_one(selected[0], candidate) != identity_a * identity_a ||
                product_plus_one(selected[1], candidate) != identity_b * identity_b ||
                product_plus_one(selected[2], candidate) != identity_c * identity_c) {
                throw std::runtime_error("canonical-shift identity failure in record " +
                                         std::to_string(record.id));
            }

            std::array<int, 3> complement_bits{};
            for (std::size_t index = 0; index < complement.size(); ++index) {
                complement_bits[index] = rational_square_root(product_plus_one(candidate, complement[index])) ? 1 : 0;
            }
            const std::string degeneracy = classify(candidate, selected, complement);
            const int survivor = degeneracy == "DISTINCT_NONZERO" && complement_bits[0] &&
                                         complement_bits[1] && complement_bits[2]
                                     ? 1
                                     : 0;
            const std::size_t ordinal = static_cast<std::size_t>(record.id - 1) * 40 +
                                        triple_index * 2 + sign_index;
            output << ordinal << '\t' << record.id << '\t' << positions[0] << '\t' << positions[1]
                   << '\t' << positions[2] << '\t' << position_mask << '\t' << sign << '\t'
                   << integer_text(root_r->num) << '\t' << integer_text(root_r->den) << '\t'
                   << integer_text(root_s->num) << '\t' << integer_text(root_s->den) << '\t'
                   << integer_text(root_t->num) << '\t' << integer_text(root_t->den) << '\t'
                   << integer_text(candidate.num) << '\t' << integer_text(candidate.den) << '\t'
                   << degeneracy << '\t' << complement_bits[0] << '\t' << complement_bits[1]
                   << '\t' << complement_bits[2] << '\t' << survivor << '\n';
            if (!output) {
                throw std::runtime_error("ledger write failure");
            }
            ++counts.rows;
            counts.zero += degeneracy == "ZERO";
            counts.selected_duplicate += degeneracy == "SELECTED_DUPLICATE";
            counts.complement_duplicate += degeneracy == "COMPLEMENT_DUPLICATE";
            counts.distinct_nonzero += degeneracy == "DISTINCT_NONZERO";
            counts.survivors += survivor;
            const int pattern = complement_bits[0] * 4 + complement_bits[1] * 2 + complement_bits[2];
            ++counts.complement_patterns[static_cast<std::size_t>(pattern)];
            if (survivor) {
                survivors.push_back(Survivor{
                    ordinal, record.id, positions, sign, record.values, candidate});
            }
        }
    }
}

std::string rational_text(const Rational& value) {
    if (value.den == 1) {
        return integer_text(value.num);
    }
    return integer_text(value.num) + "/" + integer_text(value.den);
}

std::string compact_survivors(const std::vector<Survivor>& survivors) {
    std::ostringstream output;
    output << "{\"schema\":\"canonical_shift_survivors/v1\",\"survivor_count\":"
           << survivors.size() << ",\"survivors\":[";
    for (std::size_t index = 0; index < survivors.size(); ++index) {
        if (index != 0) {
            output << ',';
        }
        const Survivor& survivor = survivors[index];
        output << "{\"candidate\":\"" << rational_text(survivor.candidate)
               << "\",\"ordinal\":" << survivor.ordinal
               << ",\"position_triple\":[" << survivor.positions[0] << ','
               << survivor.positions[1] << ',' << survivor.positions[2]
               << "],\"record_id\":" << survivor.record_id
               << ",\"sign\":" << survivor.sign << ",\"source_values\":[";
        for (std::size_t value_index = 0; value_index < survivor.source_values.size(); ++value_index) {
            if (value_index != 0) {
                output << ',';
            }
            output << '\"' << rational_text(survivor.source_values[value_index]) << '\"';
        }
        output << "]}";
    }
    output << "]}\n";
    return output.str();
}

std::string compact_summary(const Counts& counts, std::size_t ledger_bytes,
                            const std::string& ledger_sha, bool full_mode) {
    std::ostringstream output;
    output << "{\"complement_pattern_counts\":{\"000\":" << counts.complement_patterns[0]
           << ",\"001\":" << counts.complement_patterns[1]
           << ",\"010\":" << counts.complement_patterns[2]
           << ",\"011\":" << counts.complement_patterns[3]
           << ",\"100\":" << counts.complement_patterns[4]
           << ",\"101\":" << counts.complement_patterns[5]
           << ",\"110\":" << counts.complement_patterns[6]
           << ",\"111\":" << counts.complement_patterns[7]
           << "},\"context_count\":" << counts.rows
           << ",\"degeneracy_counts\":{\"COMPLEMENT_DUPLICATE\":" << counts.complement_duplicate
           << ",\"DISTINCT_NONZERO\":" << counts.distinct_nonzero
           << ",\"SELECTED_DUPLICATE\":" << counts.selected_duplicate
           << ",\"ZERO\":" << counts.zero
           << "},\"extension_identity_checks\":" << counts.rows * 3
           << ",\"ledger_byte_count\":" << ledger_bytes
           << ",\"ledger_sha256\":\"" << ledger_sha << "\""
           << ",\"record_count\":" << (full_mode ? 2001 : kCalibrationIds.size())
           << ",\"record_ids\":[";
    if (full_mode) {
        for (int id = 1; id <= 2001; ++id) {
            if (id != 1) {
                output << ',';
            }
            output << id;
        }
    } else {
        for (std::size_t index = 0; index < kCalibrationIds.size(); ++index) {
            if (index != 0) {
                output << ',';
            }
            output << kCalibrationIds[index];
        }
    }
    output << "],\"schema\":\""
           << (full_mode ? "canonical_shift_independent_summary/v1"
                         : "canonical_shift_calibration_summary/v1")
           << "\",\"source_pair_checks\":" << (full_mode ? 2001 * 15 : kCalibrationIds.size() * 15)
           << ",\"source_sha256\":\"" << kSourceSha << "\""
           << ",\"survivor_count\":" << counts.survivors << "}\n";
    return output.str();
}

void write_new_file(const fs::path& path, const std::string& contents) {
    const fs::path temporary = path.string() + ".tmp";
    if (fs::exists(path) || fs::exists(temporary)) {
        throw std::runtime_error("refusing to overwrite an existing output or temporary file");
    }
    fs::create_directories(path.parent_path());
    {
        std::ofstream output(temporary, std::ios::binary);
        output.write(contents.data(), static_cast<std::streamsize>(contents.size()));
        output.flush();
        if (!output) {
            throw std::runtime_error("summary write failure");
        }
    }
    fs::rename(temporary, path);
}

void run(const Options& options) {
    const bool full_mode = options.mode == "full";
    if (full_mode && options.full_token != kFullToken) {
        throw std::runtime_error("full mode requires the exact frozen authorization token");
    }
    if (full_mode && options.survivors_path.empty()) {
        throw std::runtime_error("full mode requires --survivors");
    }
    if (!full_mode && !options.survivors_path.empty()) {
        throw std::runtime_error("calibration mode does not emit a survivors file");
    }
    const Manifest manifest = validate_manifest(options.manifest_path, options.workspace_root,
                                                options.manifest_sha, full_mode);
    if (fs::exists(options.output_path) || fs::exists(options.output_path.string() + ".tmp") ||
        fs::exists(options.summary_path) || fs::exists(options.summary_path.string() + ".tmp") ||
        (!options.survivors_path.empty() &&
         (fs::exists(options.survivors_path) || fs::exists(options.survivors_path.string() + ".tmp")))) {
        throw std::runtime_error("refusing to overwrite an existing output or temporary file");
    }
    if (full_mode) {
        const fs::path expected_output = (manifest.full_output_dir / "ledger.tsv").lexically_normal();
        if (options.output_path != expected_output) {
            throw std::runtime_error("full-mode output must equal the frozen independent_dir/ledger.tsv");
        }
        const fs::path expected_summary = (manifest.full_output_dir / "summary.json").lexically_normal();
        if (options.summary_path != expected_summary) {
            throw std::runtime_error("full-mode summary must equal the frozen independent_dir/summary.json");
        }
        const fs::path expected_survivors = (manifest.full_output_dir / "survivors.json").lexically_normal();
        if (options.survivors_path != expected_survivors) {
            throw std::runtime_error("full-mode survivors must equal the frozen independent_dir/survivors.json");
        }
    }
    const std::vector<Record> records = parse_catalogue(manifest.source_path);
    const std::size_t validated_pairs = validate_catalogue(records);

    fs::create_directories(options.output_path.parent_path());
    const fs::path temporary = options.output_path.string() + ".tmp";
    Counts counts;
    std::vector<Survivor> survivors;
    {
        std::ofstream output(temporary, std::ios::binary);
        if (!output) {
            throw std::runtime_error("cannot create temporary ledger: " + temporary.string());
        }
        output << kLedgerHeader << '\n';
        if (full_mode) {
            for (const Record& record : records) {
                enumerate_record(record, output, counts, survivors);
            }
        } else {
            for (int record_id : manifest.calibration_ids) {
                enumerate_record(records.at(static_cast<std::size_t>(record_id - 1)), output, counts,
                                 survivors);
            }
        }
        output.flush();
        if (!output) {
            throw std::runtime_error("ledger flush failure");
        }
    }
    const std::size_t expected_rows = full_mode ? 80040 : 400;
    if (counts.rows != expected_rows ||
        counts.zero + counts.selected_duplicate + counts.complement_duplicate + counts.distinct_nonzero !=
            counts.rows) {
        throw std::runtime_error("terminal row accounting mismatch");
    }
    if (survivors.size() != counts.survivors ||
        !std::is_sorted(survivors.begin(), survivors.end(),
                        [](const Survivor& left, const Survivor& right) {
                            return left.ordinal < right.ordinal;
                        })) {
        throw std::runtime_error("survivor accounting or ordering mismatch");
    }
    if (full_mode) {
        require_value(manifest.tree, "enumeration.expected_extension_identity_checks", counts.rows * 3);
        require_value(manifest.tree, "enumeration.expected_degeneracy_counts.ZERO", counts.zero);
        require_value(manifest.tree, "enumeration.expected_degeneracy_counts.SELECTED_DUPLICATE",
                      counts.selected_duplicate);
        require_value(manifest.tree, "enumeration.expected_degeneracy_counts.COMPLEMENT_DUPLICATE",
                      counts.complement_duplicate);
        require_value(manifest.tree, "enumeration.expected_degeneracy_counts.DISTINCT_NONZERO",
                      counts.distinct_nonzero);
    }
    fs::rename(temporary, options.output_path);
    const std::string ledger_sha = sha256_file(options.output_path);
    const std::size_t ledger_bytes = static_cast<std::size_t>(fs::file_size(options.output_path));
    if (!full_mode) {
        require_value(manifest.tree, "calibration.expected_ledger_byte_count", ledger_bytes);
        require_text(manifest.tree, "calibration.expected_ledger_sha256", ledger_sha);
        require_value(manifest.tree, "calibration.expected_survivor_count", counts.survivors);
    }
    const std::string summary = compact_summary(counts, ledger_bytes, ledger_sha, full_mode);
    write_new_file(options.summary_path, summary);
    const std::string summary_sha = sha256_file(options.summary_path);
    if (!full_mode) {
        require_text(manifest.tree, "calibration.summary_schema",
                     "canonical_shift_calibration_summary/v1");
        require_text(manifest.tree, "calibration.expected_summary_sha256", summary_sha);
    }
    std::string survivors_sha;
    if (full_mode) {
        const std::string survivor_document = compact_survivors(survivors);
        write_new_file(options.survivors_path, survivor_document);
        survivors_sha = sha256_file(options.survivors_path);
    }
    std::cout << "status=OK\n"
              << "mode=" << options.mode << '\n'
              << "source_records=" << records.size() << '\n'
              << "validated_source_pairs=" << validated_pairs << '\n'
              << "rows=" << counts.rows << '\n'
              << "zero=" << counts.zero << '\n'
              << "selected_duplicate=" << counts.selected_duplicate << '\n'
              << "complement_duplicate=" << counts.complement_duplicate << '\n'
              << "distinct_nonzero=" << counts.distinct_nonzero << '\n'
              << "survivors=" << counts.survivors << '\n'
              << "ledger_sha256=" << ledger_sha << '\n'
              << "summary_sha256=" << summary_sha << '\n';
    if (full_mode) {
        std::cout << "survivors_sha256=" << survivors_sha << '\n';
    }
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        run(options);
        return 0;
    } catch (const std::exception& error) {
        usage();
        std::cerr << "ERROR: " << error.what() << '\n';
        return 2;
    }
}
