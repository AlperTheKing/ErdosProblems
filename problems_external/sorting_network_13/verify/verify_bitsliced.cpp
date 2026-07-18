// Exhaustive bit-sliced verifier for binary sorting-network fixtures.
#include <cstdint>
#include <fstream>
#include <iostream>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct Fixture {
  std::string id;
  int channels = 0;
  int expected_comparators = 0;
  int expected_depth = 0;
  int parsed_depth = 0;
  std::vector<std::pair<int, int>> comparators;
};

static std::string read_all(const std::string& path) {
  std::ifstream input(path, std::ios::binary);
  if (!input) throw std::runtime_error("cannot open " + path);
  std::ostringstream buffer;
  buffer << input.rdbuf();
  return buffer.str();
}

static int integer_field(const std::string& text, const std::string& name) {
  const std::regex pattern("\"" + name + "\"\\s*:\\s*(\\d+)");
  std::smatch match;
  if (!std::regex_search(text, match, pattern)) {
    throw std::runtime_error("missing integer field: " + name);
  }
  return std::stoi(match[1].str());
}

static std::string string_field(const std::string& text,
                                const std::string& name) {
  const std::regex pattern("\"" + name + "\"\\s*:\\s*\"([^\"]+)\"");
  std::smatch match;
  if (!std::regex_search(text, match, pattern)) {
    throw std::runtime_error("missing string field: " + name);
  }
  return match[1].str();
}

static Fixture parse_fixture(const std::string& path) {
  const std::string text = read_all(path);
  if (string_field(text, "schema") != "sorting-network-fixture-v1") {
    throw std::runtime_error("unsupported fixture schema");
  }

  Fixture fixture;
  fixture.id = string_field(text, "id");
  fixture.channels = integer_field(text, "channels");
  fixture.expected_comparators = integer_field(text, "expected_comparators");
  fixture.expected_depth = integer_field(text, "expected_depth");

  const std::size_t key = text.find("\"layers\"");
  const std::size_t start = text.find('[', key);
  if (key == std::string::npos || start == std::string::npos) {
    throw std::runtime_error("missing layers array");
  }
  int depth = 0;
  std::size_t end = std::string::npos;
  for (std::size_t pos = start; pos < text.size(); ++pos) {
    if (text[pos] == '[') {
      if (depth == 1) ++fixture.parsed_depth;
      ++depth;
    } else if (text[pos] == ']') {
      --depth;
      if (depth == 0) {
        end = pos;
        break;
      }
      if (depth < 0) throw std::runtime_error("unbalanced brackets");
    }
  }
  if (end == std::string::npos) {
    throw std::runtime_error("unterminated layers array");
  }

  const std::string layers = text.substr(start, end - start + 1);
  const std::regex pair_pattern(R"(\[\s*(\d+)\s*,\s*(\d+)\s*\])");
  for (auto it = std::sregex_iterator(layers.begin(), layers.end(), pair_pattern);
       it != std::sregex_iterator(); ++it) {
    fixture.comparators.emplace_back(std::stoi((*it)[1].str()),
                                     std::stoi((*it)[2].str()));
  }

  if (fixture.channels < 2 || fixture.channels >= 63) {
    throw std::runtime_error("invalid channel count");
  }
  if (fixture.parsed_depth != fixture.expected_depth) {
    throw std::runtime_error("fixture depth mismatch");
  }
  if (static_cast<int>(fixture.comparators.size()) !=
      fixture.expected_comparators) {
    throw std::runtime_error("fixture comparator-count mismatch");
  }
  for (const auto& [low, high] : fixture.comparators) {
    if (!(0 <= low && low < high && high < fixture.channels)) {
      throw std::runtime_error("out-of-range comparator");
    }
  }
  return fixture;
}

static std::uint64_t popcount64(std::uint64_t value) {
#if defined(__GNUC__) || defined(__clang__)
  return static_cast<std::uint64_t>(__builtin_popcountll(value));
#else
  std::uint64_t count = 0;
  while (value != 0) {
    value &= value - 1;
    ++count;
  }
  return count;
#endif
}

struct Verification {
  Fixture fixture;
  std::uint64_t tested = 0;
  std::uint64_t failures = 0;
};

static Verification verify(Fixture fixture) {
  const std::uint64_t tested = UINT64_C(1) << fixture.channels;
  const std::size_t blocks = static_cast<std::size_t>((tested + 63) / 64);
  std::vector<std::vector<std::uint64_t>> wires(
      fixture.channels, std::vector<std::uint64_t>(blocks, 0));

  for (std::uint64_t input = 0; input < tested; ++input) {
    const std::size_t block = static_cast<std::size_t>(input >> 6);
    const unsigned offset = static_cast<unsigned>(input & 63);
    for (int channel = 0; channel < fixture.channels; ++channel) {
      if (((input >> channel) & 1) != 0) {
        wires[channel][block] |= UINT64_C(1) << offset;
      }
    }
  }

  for (const auto& [low, high] : fixture.comparators) {
    for (std::size_t block = 0; block < blocks; ++block) {
      const std::uint64_t a = wires[low][block];
      const std::uint64_t b = wires[high][block];
      wires[low][block] = a & b;
      wires[high][block] = a | b;
    }
  }

  std::vector<std::uint64_t> bad(blocks, 0);
  for (int channel = 0; channel + 1 < fixture.channels; ++channel) {
    for (std::size_t block = 0; block < blocks; ++block) {
      bad[block] |= wires[channel][block] & ~wires[channel + 1][block];
    }
  }

  std::uint64_t failures = 0;
  for (const std::uint64_t word : bad) failures += popcount64(word);
  return Verification{std::move(fixture), tested, failures};
}

static std::string json_escape(const std::string& value) {
  std::string out;
  for (const char c : value) {
    if (c == '\\' || c == '"') out.push_back('\\');
    out.push_back(c);
  }
  return out;
}

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: verify_bitsliced FIXTURE.json [...]" << std::endl;
    return 2;
  }
  try {
    bool accepted = true;
    std::cout
        << "{\"schema\":\"sorting-network-verification-v1\","
        << "\"verifier\":\"cpp-bitsliced-v1\","
        << "\"representation\":\"one bit position per binary input\","
        << "\"results\":[";
    for (int index = 1; index < argc; ++index) {
      if (index != 1) std::cout << ',';
      const Verification result = verify(parse_fixture(argv[index]));
      accepted = accepted && result.failures == 0;
      std::cout << "{\"fixture\":\"" << json_escape(result.fixture.id)
                << "\",\"channels\":" << result.fixture.channels
                << ",\"comparators\":" << result.fixture.comparators.size()
                << ",\"depth\":" << result.fixture.parsed_depth
                << ",\"binary_inputs_tested\":" << result.tested
                << ",\"failures\":" << result.failures
                << ",\"accepted\":"
                << (result.failures == 0 ? "true" : "false") << '}';
    }
    std::cout << "],\"accepted\":" << (accepted ? "true" : "false")
              << '}' << std::endl;
    return accepted ? 0 : 1;
  } catch (const std::exception& error) {
    std::cerr << "verification error: " << error.what() << std::endl;
    return 2;
  }
}
