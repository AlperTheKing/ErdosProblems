#include <boost/hash2/sha2.hpp>
#include <boost/json.hpp>
#include <boost/json/src.hpp>
#include <boost/multiprecision/cpp_int.hpp>

#include <algorithm>
#include <array>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace json = boost::json;
using boost::multiprecision::cpp_int;

namespace {

constexpr std::string_view kMagic = "Q5_TORSOR_LANE_V1";
constexpr std::string_view kResultKind = "Q5_TORSOR_LANE_RESULT";
constexpr std::string_view kCanonicalMode = "canonical_positive_u_positive_y";
constexpr std::string_view kAuditMode = "audit_signed_u_both_y";
constexpr std::uint64_t kLaneCount = 64;

volatile std::sig_atomic_t g_stop_requested = 0;

void signal_handler(int) { g_stop_requested = 1; }

class ScanError final : public std::runtime_error {
public:
  using std::runtime_error::runtime_error;
};

cpp_int abs_big(cpp_int value) { return value < 0 ? -value : value; }

cpp_int gcd_big(cpp_int left, cpp_int right) {
  left = abs_big(std::move(left));
  right = abs_big(std::move(right));
  while (right != 0) {
    cpp_int remainder = left % right;
    left = std::move(right);
    right = std::move(remainder);
  }
  return left;
}

cpp_int lcm_big(const cpp_int &left, const cpp_int &right) {
  return left == 0 || right == 0
             ? cpp_int(0)
             : abs_big((left / gcd_big(left, right)) * right);
}

cpp_int pow2(const cpp_int &value) { return value * value; }

cpp_int pow3(const cpp_int &value) { return value * value * value; }

cpp_int pow4(const cpp_int &value) {
  const cpp_int square = value * value;
  return square * square;
}

cpp_int pow5(const cpp_int &value) {
  const cpp_int square = value * value;
  return square * square * value;
}

cpp_int pow6(const cpp_int &value) {
  const cpp_int cube = value * value * value;
  return cube * cube;
}

std::string big_text(const cpp_int &value) {
  return value.convert_to<std::string>();
}

bool exact_integer_square_root(const cpp_int &value, cpp_int &root) {
  if (value < 0) {
    return false;
  }
  if (value == 0) {
    root = 0;
    return true;
  }
  root = boost::multiprecision::sqrt(value);
  while (root * root > value) {
    --root;
  }
  while ((root + 1) * (root + 1) <= value) {
    ++root;
  }
  return root * root == value;
}

struct Rational {
  cpp_int numerator;
  cpp_int denominator;

  Rational() : numerator(0), denominator(1) {}

  Rational(cpp_int num, cpp_int den = 1)
      : numerator(std::move(num)), denominator(std::move(den)) {
    if (denominator == 0) {
      throw ScanError("zero rational denominator");
    }
    if (denominator < 0) {
      numerator = -numerator;
      denominator = -denominator;
    }
    const cpp_int common = gcd_big(numerator, denominator);
    numerator /= common;
    denominator /= common;
  }
};

Rational operator+(const Rational &left, const Rational &right) {
  return Rational(left.numerator * right.denominator +
                      right.numerator * left.denominator,
                  left.denominator * right.denominator);
}

Rational operator-(const Rational &left, const Rational &right) {
  return Rational(left.numerator * right.denominator -
                      right.numerator * left.denominator,
                  left.denominator * right.denominator);
}

Rational operator/(const Rational &value, const cpp_int &divisor) {
  if (divisor == 0) {
    throw ScanError("division by zero");
  }
  return Rational(value.numerator, value.denominator * divisor);
}

bool operator!=(const Rational &left, const Rational &right) {
  return left.numerator != right.numerator ||
         left.denominator != right.denominator;
}

bool operator<(const Rational &left, const Rational &right) {
  return left.numerator * right.denominator <
         right.numerator * left.denominator;
}

std::string rational_text(const Rational &value) {
  return value.denominator == 1
             ? big_text(value.numerator)
             : big_text(value.numerator) + "/" + big_text(value.denominator);
}

bool rational_square_root(const Rational &value, Rational &root) {
  if (value.numerator < 0) {
    return false;
  }
  cpp_int numerator_root;
  cpp_int denominator_root;
  if (!exact_integer_square_root(value.numerator, numerator_root) ||
      !exact_integer_square_root(value.denominator, denominator_root)) {
    return false;
  }
  root = Rational(numerator_root, denominator_root);
  return true;
}

std::array<cpp_int, 4> clear_primitive(const std::array<Rational, 4> &values) {
  cpp_int common_denominator = 1;
  for (const Rational &value : values) {
    common_denominator = lcm_big(common_denominator, value.denominator);
  }
  std::array<cpp_int, 4> integers{};
  cpp_int common_gcd = 0;
  for (std::size_t index = 0; index < values.size(); ++index) {
    integers[index] = values[index].numerator *
                      (common_denominator / values[index].denominator);
    common_gcd = gcd_big(common_gcd, integers[index]);
  }
  if (common_gcd == 0) {
    throw ScanError("cannot normalize an all-zero quadruple");
  }
  for (cpp_int &value : integers) {
    value /= common_gcd;
  }
  return integers;
}

bool integer_certificate_valid(const std::array<cpp_int, 4> &values) {
  const bool positive =
      std::all_of(values.begin(), values.end(),
                  [](const cpp_int &value) { return value > 0; });
  const bool equality =
      pow5(values[0]) + pow5(values[1]) == pow5(values[2]) + pow5(values[3]);
  const bool cross_disjoint = values[0] != values[2] &&
                              values[0] != values[3] &&
                              values[1] != values[2] && values[1] != values[3];
  return positive && equality && cross_disjoint;
}

class Sha256 final {
public:
  Sha256()
      : state_{0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
               0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U} {}

  void update(std::string_view input) {
    for (const char character : input) {
      const auto byte =
          static_cast<std::uint8_t>(static_cast<unsigned char>(character));
      buffer_[buffer_size_++] = byte;
      if (buffer_size_ == buffer_.size()) {
        transform();
        bit_length_ += 512U;
        buffer_size_ = 0;
      }
    }
  }

  std::string finish() {
    const std::uint64_t total_bits =
        bit_length_ + static_cast<std::uint64_t>(buffer_size_) * 8U;
    buffer_[buffer_size_++] = 0x80U;
    if (buffer_size_ > 56U) {
      while (buffer_size_ < 64U) {
        buffer_[buffer_size_++] = 0U;
      }
      transform();
      buffer_size_ = 0;
    }
    while (buffer_size_ < 56U) {
      buffer_[buffer_size_++] = 0U;
    }
    for (int shift = 56; shift >= 0; shift -= 8) {
      buffer_[buffer_size_++] = static_cast<std::uint8_t>(
          (total_bits >> static_cast<unsigned int>(shift)) & 0xffU);
    }
    transform();
    std::ostringstream output;
    output << std::hex << std::setfill('0');
    for (const std::uint32_t word : state_) {
      output << std::setw(8) << word;
    }
    return output.str();
  }

private:
  static constexpr std::array<std::uint32_t, 64> constants_{
      0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U, 0x3956c25bU,
      0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U, 0xd807aa98U, 0x12835b01U,
      0x243185beU, 0x550c7dc3U, 0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U,
      0xc19bf174U, 0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU,
      0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU, 0x983e5152U,
      0xa831c66dU, 0xb00327c8U, 0xbf597fc7U, 0xc6e00bf3U, 0xd5a79147U,
      0x06ca6351U, 0x14292967U, 0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU,
      0x53380d13U, 0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
      0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U, 0xd192e819U,
      0xd6990624U, 0xf40e3585U, 0x106aa070U, 0x19a4c116U, 0x1e376c08U,
      0x2748774cU, 0x34b0bcb5U, 0x391c0cb3U, 0x4ed8aa4U,  0x5b9cca4fU,
      0x682e6ff3U, 0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
      0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U};

  static std::uint32_t rotate_right(std::uint32_t value, unsigned int bits) {
    return (value >> bits) | (value << (32U - bits));
  }

  void transform() {
    std::array<std::uint32_t, 64> words{};
    for (std::size_t index = 0; index < 16U; ++index) {
      const std::size_t offset = index * 4U;
      words[index] = (static_cast<std::uint32_t>(buffer_[offset]) << 24U) |
                     (static_cast<std::uint32_t>(buffer_[offset + 1U]) << 16U) |
                     (static_cast<std::uint32_t>(buffer_[offset + 2U]) << 8U) |
                     static_cast<std::uint32_t>(buffer_[offset + 3U]);
    }
    for (std::size_t index = 16U; index < words.size(); ++index) {
      const std::uint32_t s0 = rotate_right(words[index - 15U], 7U) ^
                               rotate_right(words[index - 15U], 18U) ^
                               (words[index - 15U] >> 3U);
      const std::uint32_t s1 = rotate_right(words[index - 2U], 17U) ^
                               rotate_right(words[index - 2U], 19U) ^
                               (words[index - 2U] >> 10U);
      words[index] = words[index - 16U] + s0 + words[index - 7U] + s1;
    }
    std::uint32_t a = state_[0];
    std::uint32_t b = state_[1];
    std::uint32_t c = state_[2];
    std::uint32_t d = state_[3];
    std::uint32_t e = state_[4];
    std::uint32_t f = state_[5];
    std::uint32_t g = state_[6];
    std::uint32_t h = state_[7];
    for (std::size_t index = 0; index < words.size(); ++index) {
      const std::uint32_t sigma1 =
          rotate_right(e, 6U) ^ rotate_right(e, 11U) ^ rotate_right(e, 25U);
      const std::uint32_t choice = (e & f) ^ ((~e) & g);
      const std::uint32_t temp1 =
          h + sigma1 + choice + constants_[index] + words[index];
      const std::uint32_t sigma0 =
          rotate_right(a, 2U) ^ rotate_right(a, 13U) ^ rotate_right(a, 22U);
      const std::uint32_t majority = (a & b) ^ (a & c) ^ (b & c);
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
    state_[0] += a;
    state_[1] += b;
    state_[2] += c;
    state_[3] += d;
    state_[4] += e;
    state_[5] += f;
    state_[6] += g;
    state_[7] += h;
  }

  std::array<std::uint32_t, 8> state_;
  std::array<std::uint8_t, 64> buffer_{};
  std::size_t buffer_size_ = 0;
  std::uint64_t bit_length_ = 0;
};

std::string sha256(std::string_view bytes) {
  boost::hash2::sha2_256 hasher;
  hasher.update(bytes.data(), bytes.size());
  return boost::hash2::to_string(hasher.result());
}

void validate_hex_digest(const std::string &digest, std::string_view field) {
  if (digest.size() != 64U ||
      !std::all_of(digest.begin(), digest.end(), [](unsigned char byte) {
        return (byte >= static_cast<unsigned char>('0') &&
                byte <= static_cast<unsigned char>('9')) ||
               (byte >= static_cast<unsigned char>('a') &&
                byte <= static_cast<unsigned char>('f'));
      })) {
    throw ScanError(std::string(field) + " must be 64 lowercase hex digits");
  }
}

std::string read_binary_file(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  if (!input) {
    throw ScanError("cannot open lane file: " + path.string());
  }
  std::ostringstream contents;
  contents << input.rdbuf();
  if (!input.good() && !input.eof()) {
    throw ScanError("cannot read lane file: " + path.string());
  }
  return contents.str();
}

std::string required_environment(std::string_view name) {
  const std::string key(name);
  const char *value = std::getenv(key.c_str());
  if (value == nullptr || *value == '\0') {
    throw ScanError("missing required environment variable: " + key);
  }
  return value;
}

std::uint64_t parse_u64(std::string_view text, std::string_view field) {
  if (text.empty() || (text.size() > 1U && text.front() == '0') ||
      !std::all_of(text.begin(), text.end(), [](unsigned char byte) {
        return byte >= static_cast<unsigned char>('0') &&
               byte <= static_cast<unsigned char>('9');
      })) {
    throw ScanError(std::string(field) +
                    " must be a canonical unsigned decimal");
  }
  std::uint64_t value = 0;
  for (const char character : text) {
    const auto digit = static_cast<std::uint64_t>(character - '0');
    if (value > (std::numeric_limits<std::uint64_t>::max() - digit) / 10U) {
      throw ScanError(std::string(field) + " is outside uint64 range");
    }
    value = value * 10U + digit;
  }
  return value;
}

std::vector<std::string> split_exact(std::string_view text, char delimiter) {
  std::vector<std::string> pieces;
  std::size_t start = 0;
  while (true) {
    const std::size_t found = text.find(delimiter, start);
    if (found == std::string_view::npos) {
      pieces.emplace_back(text.substr(start));
      break;
    }
    pieces.emplace_back(text.substr(start, found - start));
    start = found + 1U;
  }
  return pieces;
}

void validate_campaign_id(const std::string &campaign_id) {
  auto alphanumeric = [](unsigned char byte) {
    return (byte >= static_cast<unsigned char>('0') &&
            byte <= static_cast<unsigned char>('9')) ||
           (byte >= static_cast<unsigned char>('A') &&
            byte <= static_cast<unsigned char>('Z')) ||
           (byte >= static_cast<unsigned char>('a') &&
            byte <= static_cast<unsigned char>('z'));
  };
  if (campaign_id.empty() || campaign_id.size() > 128U ||
      !alphanumeric(static_cast<unsigned char>(campaign_id.front())) ||
      !std::all_of(campaign_id.begin() + 1, campaign_id.end(),
                   [&](unsigned char byte) {
                     return alphanumeric(byte) ||
                            byte == static_cast<unsigned char>('_') ||
                            byte == static_cast<unsigned char>('.') ||
                            byte == static_cast<unsigned char>('-');
                   })) {
    throw ScanError("campaign_id violates the frozen ASCII grammar");
  }
}

struct Arguments {
  std::filesystem::path lane_file_path;
  std::uint64_t lane_id = std::numeric_limits<std::uint64_t>::max();
  std::uint64_t threads = 0;
  std::filesystem::path result_path;
  bool emit_torsor_points = false;
};

Arguments parse_arguments(int argc, char **argv) {
  Arguments arguments;
  bool lane_file_seen = false;
  bool lane_id_seen = false;
  bool threads_seen = false;
  bool result_seen = false;
  for (int index = 1; index < argc; ++index) {
    const std::string option = argv[index];
    if (option == "--emit-torsor-points") {
      if (arguments.emit_torsor_points) {
        throw ScanError("duplicate --emit-torsor-points");
      }
      arguments.emit_torsor_points = true;
      continue;
    }
    if (index + 1 >= argc) {
      throw ScanError("missing value for argument: " + option);
    }
    const std::string value = argv[++index];
    if (option == "--lane-file") {
      if (lane_file_seen) {
        throw ScanError("duplicate --lane-file");
      }
      arguments.lane_file_path = value;
      lane_file_seen = true;
    } else if (option == "--lane-id") {
      if (lane_id_seen) {
        throw ScanError("duplicate --lane-id");
      }
      arguments.lane_id = parse_u64(value, "lane id");
      lane_id_seen = true;
    } else if (option == "--threads") {
      if (threads_seen) {
        throw ScanError("duplicate --threads");
      }
      arguments.threads = parse_u64(value, "threads");
      threads_seen = true;
    } else if (option == "--result") {
      if (result_seen) {
        throw ScanError("duplicate --result");
      }
      arguments.result_path = value;
      result_seen = true;
    } else {
      throw ScanError("unknown argument: " + option);
    }
  }
  if (!lane_file_seen || !lane_id_seen || !threads_seen || !result_seen) {
    throw ScanError(
        "require --lane-file PATH --lane-id ID --threads 1 --result PATH");
  }
  if (arguments.threads != 1U) {
    throw ScanError("scanner is single-threaded; --threads must equal 1");
  }
  return arguments;
}

struct Specialization {
  std::uint64_t p;
  std::uint64_t q;
  std::uint64_t estimated_work;
};

struct LaneConfig {
  std::string campaign_id;
  std::string deadline_text;
  std::string search_mode;
  std::uint64_t lane_id;
  std::uint64_t p_bound;
  std::uint64_t q_bound;
  std::uint64_t n_bound;
  std::uint64_t d_bound;
  std::string assignment_sha256;
  std::string lane_file_sha256;
  std::string manifest_payload_sha256;
  std::vector<Specialization> specializations;
};

cpp_int estimated_work_exact(std::uint64_t p, std::uint64_t q,
                             std::uint64_t n_bound, std::uint64_t d_bound,
                             bool audit_mode) {
  const cpp_int full_loop =
      cpp_int(d_bound) *
      (audit_mode ? 2 * cpp_int(n_bound) + 1 : cpp_int(n_bound));
  cpp_int total = full_loop;
  const cpp_int big_p = p;
  const cpp_int big_q = q;
  for (std::uint64_t d = 1; d <= d_bound; ++d) {
    const cpp_int quotient = (big_p * d - 1) / big_q;
    const cpp_int maximum =
        cpp_int(n_bound) < quotient ? cpp_int(n_bound) : quotient;
    total += audit_mode ? 1 + 2 * maximum : maximum;
    if (d == d_bound) {
      break;
    }
  }
  return total;
}

std::uint64_t big_to_u64(const cpp_int &value, std::string_view field) {
  if (value < 0 || value > std::numeric_limits<std::uint64_t>::max()) {
    throw ScanError(std::string(field) + " is outside uint64 range");
  }
  return value.convert_to<std::uint64_t>();
}

std::string
assignment_canonical_json(const std::vector<Specialization> &specializations) {
  std::string result = "[";
  bool first = true;
  for (const Specialization &item : specializations) {
    if (!first) {
      result.push_back(',');
    }
    first = false;
    result += "{\"estimated_work\":" + std::to_string(item.estimated_work) +
              ",\"p\":" + std::to_string(item.p) +
              ",\"q\":" + std::to_string(item.q) + "}";
  }
  result.push_back(']');
  return result;
}

std::chrono::system_clock::time_point parse_deadline(const std::string &text) {
  if (text.size() != 20U || text[4] != '-' || text[7] != '-' ||
      text[10] != 'T' || text[13] != ':' || text[16] != ':' ||
      text[19] != 'Z') {
    throw ScanError("deadline must be canonical YYYY-MM-DDTHH:MM:SSZ");
  }
  auto decimal = [&text](std::size_t start, std::size_t length) {
    const std::string_view field = std::string_view(text).substr(start, length);
    if (!std::all_of(field.begin(), field.end(), [](unsigned char byte) {
          return byte >= static_cast<unsigned char>('0') &&
                 byte <= static_cast<unsigned char>('9');
        })) {
      throw ScanError("deadline field is not decimal");
    }
    std::uint64_t value = 0;
    for (const char character : field) {
      value = value * 10U + static_cast<std::uint64_t>(character - '0');
    }
    return value;
  };
  const int year = static_cast<int>(decimal(0, 4));
  const unsigned int month = static_cast<unsigned int>(decimal(5, 2));
  const unsigned int day = static_cast<unsigned int>(decimal(8, 2));
  const std::uint64_t hour = decimal(11, 2);
  const std::uint64_t minute = decimal(14, 2);
  const std::uint64_t second = decimal(17, 2);
  const std::chrono::year_month_day date{std::chrono::year{year},
                                         std::chrono::month{month},
                                         std::chrono::day{day}};
  if (!date.ok() || hour > 23U || minute > 59U || second > 59U) {
    throw ScanError("deadline contains an out-of-range UTC field");
  }
  return std::chrono::sys_days{date} + std::chrono::hours{hour} +
         std::chrono::minutes{minute} + std::chrono::seconds{second};
}

LaneConfig load_lane_file(const Arguments &arguments) {
  const std::string raw = read_binary_file(arguments.lane_file_path);
  const std::string expected_lane_digest =
      required_environment("Q5_LANE_FILE_SHA256");
  validate_hex_digest(expected_lane_digest, "Q5_LANE_FILE_SHA256");
  const std::string computed_lane_digest = sha256(raw);
  if (computed_lane_digest != expected_lane_digest) {
    throw ScanError(
        "lane-file SHA-256 mismatch: computed=" + computed_lane_digest +
        ", expected=" + expected_lane_digest);
  }
  if (raw.empty() || raw.back() != '\n' ||
      raw.find('\r') != std::string::npos ||
      raw.find('\0') != std::string::npos) {
    throw ScanError(
        "lane file must be nonempty strict LF text without CR or NUL");
  }
  for (const char character : raw) {
    const auto byte = static_cast<unsigned char>(character);
    if (character != '\n' && character != '\t' &&
        (byte < 0x20U || byte > 0x7eU)) {
      throw ScanError("lane file contains non-ASCII or control bytes");
    }
  }
  std::vector<std::string> lines = split_exact(raw, '\n');
  if (lines.empty() || !lines.back().empty()) {
    throw ScanError("lane file must end in exactly one LF");
  }
  lines.pop_back();
  if (lines.size() < 12U || lines[0] != kMagic) {
    throw ScanError("lane file has wrong magic or too few lines");
  }
  const std::array<std::string_view, 10> metadata_keys{
      "campaign_id", "deadline", "search_mode", "lane_id", "lane_count",
      "P",           "Q",        "N",           "D",       "assignment_sha256"};
  std::array<std::string, 10> metadata_values{};
  for (std::size_t index = 0; index < metadata_keys.size(); ++index) {
    const std::vector<std::string> fields =
        split_exact(lines[index + 1U], '\t');
    if (fields.size() != 2U || fields[0] != metadata_keys[index] ||
        fields[1].empty()) {
      throw ScanError("lane metadata field order/content mismatch at " +
                      std::string(metadata_keys[index]));
    }
    metadata_values[index] = fields[1];
  }
  const std::vector<std::string> count_fields = split_exact(lines[11], '\t');
  if (count_fields.size() != 2U || count_fields[0] != "count") {
    throw ScanError("lane count metadata line is malformed");
  }
  const std::uint64_t declared_count = parse_u64(count_fields[1], "count");
  if (lines.size() != 13U + declared_count ||
      lines[12] != "p\tq\testimated_work") {
    throw ScanError("lane row count/header mismatch");
  }

  LaneConfig config{metadata_values[0],
                    metadata_values[1],
                    metadata_values[2],
                    parse_u64(metadata_values[3], "lane_id"),
                    parse_u64(metadata_values[5], "P"),
                    parse_u64(metadata_values[6], "Q"),
                    parse_u64(metadata_values[7], "N"),
                    parse_u64(metadata_values[8], "D"),
                    metadata_values[9],
                    computed_lane_digest,
                    required_environment("Q5_MANIFEST_PAYLOAD_SHA256"),
                    {}};
  validate_campaign_id(config.campaign_id);
  validate_hex_digest(config.assignment_sha256, "assignment_sha256");
  validate_hex_digest(config.manifest_payload_sha256,
                      "Q5_MANIFEST_PAYLOAD_SHA256");
  if (parse_u64(metadata_values[4], "lane_count") != kLaneCount ||
      config.lane_id >= kLaneCount || config.lane_id != arguments.lane_id) {
    throw ScanError("lane_count/lane_id contract mismatch");
  }
  if (config.search_mode != kCanonicalMode &&
      config.search_mode != kAuditMode) {
    throw ScanError("unsupported search_mode");
  }
  if (config.p_bound == 0U || config.q_bound == 0U || config.d_bound == 0U ||
      config.n_bound > static_cast<std::uint64_t>(
                           std::numeric_limits<std::int64_t>::max() - 1)) {
    throw ScanError("bounds require P,Q,D>=1 and an enumerable N>=0");
  }
  const std::string environment_deadline =
      required_environment("Q5_DEADLINE_UTC");
  if (config.deadline_text != environment_deadline) {
    throw ScanError("TSV deadline disagrees with Q5_DEADLINE_UTC");
  }
  const auto deadline = parse_deadline(config.deadline_text);
  if (std::chrono::system_clock::now() >= deadline) {
    throw ScanError("lane deadline is already expired");
  }

  const bool audit_mode = config.search_mode == kAuditMode;
  std::set<std::pair<std::uint64_t, std::uint64_t>> seen;
  for (std::size_t row = 0; row < declared_count; ++row) {
    const std::vector<std::string> fields = split_exact(lines[13U + row], '\t');
    if (fields.size() != 3U) {
      throw ScanError("specialization row must have exactly three TSV fields");
    }
    Specialization item{parse_u64(fields[0], "p"), parse_u64(fields[1], "q"),
                        parse_u64(fields[2], "estimated_work")};
    if (item.p == 0U || item.q == 0U || item.p > config.p_bound ||
        item.q > config.q_bound || std::gcd(item.p, item.q) != 1U ||
        !seen.emplace(item.p, item.q).second) {
      throw ScanError(
          "specialization is duplicate, unreduced, or outside bounds");
    }
    const cpp_int expected_work = estimated_work_exact(
        item.p, item.q, config.n_bound, config.d_bound, audit_mode);
    if (item.estimated_work != big_to_u64(expected_work, "estimated_work")) {
      throw ScanError("specialization estimated_work mismatch");
    }
    config.specializations.push_back(item);
  }
  const std::string computed_assignment =
      sha256(assignment_canonical_json(config.specializations));
  if (computed_assignment != config.assignment_sha256) {
    throw ScanError("assignment SHA-256 mismatch");
  }
  return config;
}

struct Counts {
  cpp_int reduced_t_values = 0;
  cpp_int reduced_u_values = 0;
  cpp_int pairs_considered = 0;
  cpp_int admissible_specializations = 0;
  cpp_int zero_u_tested = 0;
  cpp_int radicand_squares = 0;
  cpp_int y_signs_tested = 0;
  cpp_int nonnegative_z = 0;
  cpp_int z_squares = 0;
  cpp_int bounded_z_squares = 0;
  cpp_int repeated_entry_rejections = 0;
  cpp_int candidate_records = 0;
  cpp_int verified_integer_certificates = 0;
};

json::object counts_json(const Counts &counts) {
  json::object object;
  object["reduced_t_values"] = big_text(counts.reduced_t_values);
  object["reduced_u_values"] = big_text(counts.reduced_u_values);
  object["pairs_considered"] = big_text(counts.pairs_considered);
  object["admissible_specializations"] =
      big_text(counts.admissible_specializations);
  object["zero_u_tested"] = big_text(counts.zero_u_tested);
  object["radicand_squares"] = big_text(counts.radicand_squares);
  object["y_signs_tested"] = big_text(counts.y_signs_tested);
  object["nonnegative_z"] = big_text(counts.nonnegative_z);
  object["z_squares"] = big_text(counts.z_squares);
  object["bounded_z_squares"] = big_text(counts.bounded_z_squares);
  object["repeated_entry_rejections"] =
      big_text(counts.repeated_entry_rejections);
  object["candidate_records"] = big_text(counts.candidate_records);
  object["verified_integer_certificates"] =
      big_text(counts.verified_integer_certificates);
  return object;
}

struct ScanOutcome {
  std::string status = "NO_HIT";
  std::uint64_t completed_specializations = 0;
  Counts counts;
  json::array candidates;
  json::array torsor_points;
};

bool stop_due(std::chrono::system_clock::time_point deadline) {
  return g_stop_requested != 0 || std::chrono::system_clock::now() >= deadline;
}

json::object branch_record(int sign, const Rational &y, const Rational &z,
                           bool z_nonnegative, bool z_below_bound,
                           bool z_square) {
  json::object branch;
  branch["sign"] = sign;
  branch["Y"] = rational_text(y);
  branch["Z"] = rational_text(z);
  branch["z_nonnegative"] = z_nonnegative;
  branch["z_lt_T_squared"] = z_below_bound;
  branch["z_rational_square"] = z_square;
  return branch;
}

template <typename Function>
bool enumerate_numerators(bool audit_mode, std::uint64_t n_bound,
                          Function &&function) {
  if (audit_mode) {
    const std::int64_t limit = static_cast<std::int64_t>(n_bound);
    for (std::int64_t n = -limit; n <= limit; ++n) {
      if (!function(n)) {
        return false;
      }
    }
  } else {
    for (std::uint64_t positive = 1; positive <= n_bound; ++positive) {
      if (!function(static_cast<std::int64_t>(positive))) {
        return false;
      }
      if (positive == n_bound) {
        break;
      }
    }
  }
  return true;
}

ScanOutcome scan_lane(const LaneConfig &config, bool emit_torsor_points,
                      std::chrono::system_clock::time_point deadline) {
  ScanOutcome outcome;
  const bool audit_mode = config.search_mode == kAuditMode;
  outcome.counts.reduced_t_values = config.specializations.size();

  for (std::uint64_t denominator = 1; denominator <= config.d_bound;
       ++denominator) {
    enumerate_numerators(
        audit_mode, config.n_bound, [&](std::int64_t numerator) {
          const std::uint64_t absolute = static_cast<std::uint64_t>(
              numerator < 0 ? -numerator : numerator);
          if (std::gcd(absolute, denominator) == 1U) {
            ++outcome.counts.reduced_u_values;
          }
          return true;
        });
    if (denominator == config.d_bound) {
      break;
    }
  }

  for (const Specialization &specialization : config.specializations) {
    if (stop_due(deadline)) {
      outcome.status = "TIMEOUT_INCOMPLETE";
      return outcome;
    }
    const cpp_int p = specialization.p;
    const cpp_int q = specialization.q;
    const cpp_int sum = p + q;
    const cpp_int q2 = pow2(q);
    const cpp_int q3 = pow3(q);
    const cpp_int q4 = pow4(q);
    const cpp_int p3 = pow3(p);
    const cpp_int p5 = pow5(p);
    const cpp_int sum2 = pow2(sum);
    const cpp_int sum3 = pow3(sum);
    const cpp_int sum6 = pow6(sum);
    const Rational t(p, q);
    const Rational capital_t(sum, q);
    const Rational capital_t_squared(sum2, q2);
    bool specialization_complete = true;

    for (std::uint64_t d_small = 1; d_small <= config.d_bound; ++d_small) {
      const cpp_int d = d_small;
      const cpp_int d2 = pow2(d);
      const cpp_int d4 = pow4(d);
      const bool numerator_complete = enumerate_numerators(
          audit_mode, config.n_bound, [&](std::int64_t n_small) {
            if ((outcome.counts.pairs_considered & 4095) == 0 &&
                stop_due(deadline)) {
              return false;
            }
            const std::uint64_t absolute =
                static_cast<std::uint64_t>(n_small < 0 ? -n_small : n_small);
            if (std::gcd(absolute, d_small) != 1U) {
              return true;
            }
            ++outcome.counts.pairs_considered;
            const cpp_int n = n_small;
            if (abs_big(n) * q >= p * d) {
              return true;
            }
            ++outcome.counts.admissible_specializations;
            if (n == 0) {
              ++outcome.counts.zero_u_tested;
            }
            const cpp_int n2 = pow2(n);
            const cpp_int n4 = pow4(n);
            const cpp_int inner =
                p5 * d4 + 10 * p3 * n2 * q2 * d2 + 5 * p * n4 * q4;
            const cpp_int radicand_numerator =
                80 * sum6 * d4 + 20 * sum * inner;
            cpp_int y_numerator;
            if (!exact_integer_square_root(radicand_numerator, y_numerator)) {
              return true;
            }
            ++outcome.counts.radicand_squares;
            const cpp_int y_denominator = q3 * d2;
            json::object point;
            if (emit_torsor_points) {
              point["p"] = specialization.p;
              point["q"] = specialization.q;
              point["u_numerator"] = std::to_string(n_small);
              point["u_denominator"] = d_small;
              point["t"] = rational_text(t);
              point["u"] = rational_text(Rational(n, d));
              point["Y_prime_abs"] = rational_text(Rational(y_numerator, d2));
              point["branches"] = json::array{};
            }
            const std::array<int, 2> audit_signs{1, -1};
            const std::array<int, 1> canonical_signs{1};
            auto evaluate_sign = [&](int sign) {
              ++outcome.counts.y_signs_tested;
              const cpp_int signed_y = sign > 0 ? y_numerator : -y_numerator;
              const Rational y(signed_y, y_denominator);
              const Rational z(signed_y - 10 * sum3 * d2, 10 * sum * q2 * d2);
              const bool nonnegative = z.numerator >= 0;
              const bool below_bound = z < capital_t_squared;
              if (nonnegative) {
                ++outcome.counts.nonnegative_z;
              }
              Rational v;
              const bool square = rational_square_root(z, v);
              if (square) {
                ++outcome.counts.z_squares;
              }
              if (emit_torsor_points) {
                point["branches"].as_array().emplace_back(branch_record(
                    sign, y, z, nonnegative, below_bound, square));
              }
              if (!(nonnegative && below_bound && square)) {
                return true;
              }
              ++outcome.counts.bounded_z_squares;
              if (n == 0 || z.numerator == 0) {
                ++outcome.counts.repeated_entry_rejections;
                return true;
              }
              const Rational u(n, d);
              const std::array<Rational, 4> rational_values{
                  (t - u) / 2, (t + u) / 2, (capital_t - v) / 2,
                  (capital_t + v) / 2};
              const bool rational_positive = std::all_of(
                  rational_values.begin(), rational_values.end(),
                  [](const Rational &value) { return value.numerator > 0; });
              const bool rational_cross_disjoint =
                  rational_values[0] != rational_values[2] &&
                  rational_values[0] != rational_values[3] &&
                  rational_values[1] != rational_values[2] &&
                  rational_values[1] != rational_values[3];
              if (!rational_positive || !rational_cross_disjoint) {
                ++outcome.counts.repeated_entry_rejections;
                return true;
              }
              ++outcome.counts.candidate_records;
              const std::array<cpp_int, 4> integers =
                  clear_primitive(rational_values);
              if (!integer_certificate_valid(integers)) {
                throw ScanError(
                    "target candidate failed exact final certificate replay");
              }
              const cpp_int h =
                  integers[2] + integers[3] - integers[0] - integers[1];
              if (h <= 0 || h % 30 != 0) {
                throw ScanError(
                    "target candidate failed the 30-divides-h invariant");
              }
              ++outcome.counts.verified_integer_certificates;
              json::object candidate;
              candidate["source_p"] = specialization.p;
              candidate["source_q"] = specialization.q;
              candidate["source_u_numerator"] = std::to_string(n_small);
              candidate["source_u_denominator"] = d_small;
              candidate["Y"] = rational_text(y);
              candidate["Z"] = rational_text(z);
              candidate["v"] = rational_text(v);
              candidate["h"] = big_text(h);
              json::array rational_quadruple;
              json::array integer_quadruple;
              for (std::size_t index = 0; index < 4U; ++index) {
                rational_quadruple.emplace_back(
                    rational_text(rational_values[index]));
                integer_quadruple.emplace_back(big_text(integers[index]));
              }
              candidate["rational_quadruple"] = std::move(rational_quadruple);
              candidate["integer_quadruple"] = std::move(integer_quadruple);
              candidate["exact_verification"] = true;
              outcome.candidates.emplace_back(std::move(candidate));
              outcome.status = "HIT";
              return false;
            };
            if (audit_mode) {
              for (const int sign : audit_signs) {
                if (!evaluate_sign(sign)) {
                  return false;
                }
              }
            } else {
              for (const int sign : canonical_signs) {
                if (!evaluate_sign(sign)) {
                  return false;
                }
              }
            }
            if (emit_torsor_points) {
              outcome.torsor_points.emplace_back(std::move(point));
            }
            return true;
          });
      if (!numerator_complete) {
        if (outcome.status == "HIT") {
          return outcome;
        }
        specialization_complete = false;
        break;
      }
      if (d_small == config.d_bound) {
        break;
      }
    }
    if (!specialization_complete) {
      outcome.status = "TIMEOUT_INCOMPLETE";
      return outcome;
    }
    ++outcome.completed_specializations;
  }
  return outcome;
}

json::object make_result(const LaneConfig &config, const ScanOutcome &outcome,
                         std::chrono::milliseconds elapsed,
                         bool emit_torsor_points) {
  json::object result;
  result["schema_version"] = 1;
  result["kind"] = kResultKind;
  result["campaign_id"] = config.campaign_id;
  result["manifest_payload_sha256"] = config.manifest_payload_sha256;
  result["lane_file_sha256"] = config.lane_file_sha256;
  result["lane_id"] = config.lane_id;
  result["assignment_sha256"] = config.assignment_sha256;
  result["search_mode"] = config.search_mode;
  result["status"] = outcome.status;
  result["assigned_specializations"] = config.specializations.size();
  result["completed_specializations"] = outcome.completed_specializations;
  result["signed_u_symmetry_pruned"] = config.search_mode == kCanonicalMode;
  result["negative_y_pruned"] = config.search_mode == kCanonicalMode;
  result["zero_u_pruned"] = config.search_mode == kCanonicalMode;
  result["zero_z_rejected_as_nontarget"] = true;
  result["emit_torsor_points"] = emit_torsor_points;
  result["counts"] = counts_json(outcome.counts);
  result["candidates"] = outcome.candidates;
  result["elapsed_milliseconds"] = std::to_string(elapsed.count());
  result["complete"] =
      outcome.status == "NO_HIT" &&
      outcome.completed_specializations == config.specializations.size();
  if (emit_torsor_points) {
    result["torsor_points"] = outcome.torsor_points;
  }
  return result;
}

json::object fail_closed_result(std::uint64_t lane_id,
                                const std::string &error_message) {
  json::object result;
  result["schema_version"] = 1;
  result["kind"] = kResultKind;
  result["campaign_id"] = "";
  result["manifest_payload_sha256"] = "";
  result["lane_file_sha256"] = "";
  result["lane_id"] = lane_id;
  result["assignment_sha256"] = "";
  result["search_mode"] = "";
  result["status"] = "FAIL_CLOSED";
  result["assigned_specializations"] = 0;
  result["completed_specializations"] = 0;
  result["counts"] = json::object{};
  result["candidates"] = json::array{};
  result["error"] = error_message;
  result["complete"] = false;
  return result;
}

void write_result_atomic(const std::filesystem::path &path,
                         const json::object &result) {
  if (!path.is_absolute()) {
    throw ScanError("--result must be an absolute path");
  }
  const std::filesystem::path parent = path.parent_path();
  if (parent.empty() || !std::filesystem::is_directory(parent)) {
    throw ScanError("result parent directory does not exist");
  }
  if (std::filesystem::exists(path)) {
    throw ScanError("refusing to overwrite an existing result file");
  }
  const auto nonce =
      std::chrono::steady_clock::now().time_since_epoch().count();
  const std::filesystem::path temporary =
      path.string() + ".tmp." + std::to_string(nonce);
  {
    std::ofstream output(temporary, std::ios::binary | std::ios::trunc);
    if (!output) {
      throw ScanError("cannot create temporary result file");
    }
    output << json::serialize(result) << '\n';
    output.flush();
    if (!output) {
      throw ScanError("cannot write temporary result file");
    }
  }
  std::filesystem::rename(temporary, path);
}

} // namespace

int main(int argc, char **argv) {
  std::optional<Arguments> arguments;
  try {
    arguments = parse_arguments(argc, argv);
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);
    const auto started = std::chrono::steady_clock::now();
    const LaneConfig config = load_lane_file(*arguments);
    const auto deadline = parse_deadline(config.deadline_text);
    const ScanOutcome outcome =
        scan_lane(config, arguments->emit_torsor_points, deadline);
    const auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - started);
    if (outcome.status == "NO_HIT" &&
        outcome.completed_specializations != config.specializations.size()) {
      throw ScanError("NO_HIT does not cover every assigned specialization");
    }
    if (outcome.status == "HIT" && outcome.candidates.empty()) {
      throw ScanError("HIT result has no candidate");
    }
    write_result_atomic(
        arguments->result_path,
        make_result(config, outcome, elapsed, arguments->emit_torsor_points));
    if (outcome.status == "HIT") {
      return 10;
    }
    if (outcome.status == "TIMEOUT_INCOMPLETE") {
      return 3;
    }
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "FAIL_CLOSED: " << error.what() << '\n';
    if (arguments.has_value()) {
      try {
        write_result_atomic(
            arguments->result_path,
            fail_closed_result(arguments->lane_id, error.what()));
      } catch (const std::exception &write_error) {
        std::cerr << "FAIL_CLOSED_RESULT_WRITE: " << write_error.what() << '\n';
      }
    }
    return 2;
  }
}
