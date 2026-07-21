// Independent raw-adjacency auditor for unrestricted oriented graphs.
//
// This file does not include or call the production search engine.  It parses
// {"n":...,"out_neighbors":[...]} and recomputes all semantics from scratch
// using 64-bit masks and explicit length-two witness counts.

#include <algorithm>
#include <bit>
#include <cctype>
#include <cstdint>
#include <exception>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace {

struct JsonError final : std::runtime_error {
  using std::runtime_error::runtime_error;
};

struct RawGraph {
  int n = 0;
  std::vector<std::vector<int>> rows;
};

class Parser {
 public:
  explicit Parser(std::string_view input) : input_(input) {}

  RawGraph parse_graph() {
    RawGraph graph;
    bool have_n = false;
    bool have_rows = false;
    skip_ws();
    expect('{');
    skip_ws();
    if (consume('}')) {
      throw JsonError("object is missing n and out_neighbors");
    }
    while (true) {
      const std::string key = parse_string();
      skip_ws();
      expect(':');
      if (key == "n") {
        if (have_n) {
          throw JsonError("duplicate n key");
        }
        graph.n = parse_nonnegative_int();
        have_n = true;
      } else if (key == "out_neighbors") {
        if (have_rows) {
          throw JsonError("duplicate out_neighbors key");
        }
        graph.rows = parse_rows();
        have_rows = true;
      } else {
        throw JsonError("unknown key: " + key);
      }
      skip_ws();
      if (consume('}')) {
        break;
      }
      expect(',');
    }
    skip_ws();
    if (position_ != input_.size()) {
      throw JsonError("trailing data after JSON object");
    }
    if (!have_n || !have_rows) {
      throw JsonError("object must contain n and out_neighbors");
    }
    return graph;
  }

 private:
  std::string_view input_;
  std::size_t position_ = 0;

  void skip_ws() {
    while (position_ < input_.size() &&
           std::isspace(static_cast<unsigned char>(input_[position_]))) {
      ++position_;
    }
  }

  bool consume(char expected) {
    skip_ws();
    if (position_ < input_.size() && input_[position_] == expected) {
      ++position_;
      return true;
    }
    return false;
  }

  void expect(char expected) {
    if (!consume(expected)) {
      throw JsonError(std::string("expected '") + expected + "'");
    }
  }

  std::string parse_string() {
    skip_ws();
    if (position_ >= input_.size() || input_[position_] != '"') {
      throw JsonError("expected JSON string");
    }
    ++position_;
    std::string result;
    while (position_ < input_.size()) {
      const char ch = input_[position_++];
      if (ch == '"') {
        return result;
      }
      if (ch == '\\' || static_cast<unsigned char>(ch) < 0x20U) {
        throw JsonError("escaped/control characters are forbidden in keys");
      }
      result.push_back(ch);
    }
    throw JsonError("unterminated JSON string");
  }

  int parse_nonnegative_int() {
    skip_ws();
    if (position_ >= input_.size() ||
        !std::isdigit(static_cast<unsigned char>(input_[position_]))) {
      throw JsonError("expected nonnegative integer");
    }
    std::uint64_t value = 0;
    while (position_ < input_.size() &&
           std::isdigit(static_cast<unsigned char>(input_[position_]))) {
      value = value * 10U + static_cast<unsigned>(input_[position_] - '0');
      if (value > static_cast<std::uint64_t>(std::numeric_limits<int>::max())) {
        throw JsonError("integer overflow");
      }
      ++position_;
    }
    return static_cast<int>(value);
  }

  std::vector<int> parse_int_array() {
    std::vector<int> values;
    expect('[');
    skip_ws();
    if (consume(']')) {
      return values;
    }
    while (true) {
      values.push_back(parse_nonnegative_int());
      skip_ws();
      if (consume(']')) {
        break;
      }
      expect(',');
    }
    return values;
  }

  std::vector<std::vector<int>> parse_rows() {
    std::vector<std::vector<int>> rows;
    expect('[');
    skip_ws();
    if (consume(']')) {
      return rows;
    }
    while (true) {
      rows.push_back(parse_int_array());
      skip_ws();
      if (consume(']')) {
        break;
      }
      expect(',');
    }
    return rows;
  }
};

struct RowAudit {
  int vertex = 0;
  std::uint64_t direct = 0;
  std::uint64_t second = 0;
  std::uint64_t unreachable = 0;
  std::vector<int> witness_counts;
  int d1 = 0;
  int d2 = 0;
  bool strict = false;
  std::uint64_t exact_penalty = 0;
  std::uint64_t witness_mass = 0;
  std::uint64_t witness_energy = 0;
};

struct Audit {
  RawGraph raw;
  std::vector<std::uint64_t> out;
  std::vector<RowAudit> rows;
  int minimum_outdegree = 0;
  int missing_pairs = 0;
  bool all_strict = false;
  bool in_n19_domain = false;
  bool accepted_counterexample = false;
  std::uint64_t exact_objective = 0;
  std::uint64_t witness_energy = 0;
};

std::uint64_t bit(int vertex) {
  return std::uint64_t{1} << static_cast<unsigned>(vertex);
}

Audit audit_raw(RawGraph raw) {
  if (raw.n < 1 || raw.n > 63) {
    throw JsonError("n must lie in [1,63]");
  }
  if (raw.rows.size() != static_cast<std::size_t>(raw.n)) {
    throw JsonError("out_neighbors must contain exactly n rows");
  }

  Audit audit;
  audit.raw = std::move(raw);
  audit.out.assign(static_cast<std::size_t>(audit.raw.n), 0);
  for (int source = 0; source < audit.raw.n; ++source) {
    int previous = -1;
    for (const int target : audit.raw.rows[static_cast<std::size_t>(source)]) {
      if (target < 0 || target >= audit.raw.n) {
        throw JsonError("target is out of range");
      }
      if (target <= previous) {
        throw JsonError("each adjacency row must be sorted and unique");
      }
      if (target == source) {
        throw JsonError("loop in raw adjacency");
      }
      previous = target;
      audit.out[static_cast<std::size_t>(source)] |= bit(target);
    }
  }

  for (int a = 0; a < audit.raw.n; ++a) {
    for (int b = a + 1; b < audit.raw.n; ++b) {
      if ((audit.out[static_cast<std::size_t>(a)] & bit(b)) != 0 &&
          (audit.out[static_cast<std::size_t>(b)] & bit(a)) != 0) {
        throw JsonError("digon in raw adjacency");
      }
    }
  }

  std::vector<std::uint64_t> incoming(static_cast<std::size_t>(audit.raw.n), 0);
  int total_arcs = 0;
  audit.minimum_outdegree = audit.raw.n;
  for (int source = 0; source < audit.raw.n; ++source) {
    const int degree =
        std::popcount(audit.out[static_cast<std::size_t>(source)]);
    total_arcs += degree;
    audit.minimum_outdegree = std::min(audit.minimum_outdegree, degree);
    for (int target = 0; target < audit.raw.n; ++target) {
      if ((audit.out[static_cast<std::size_t>(source)] & bit(target)) != 0) {
        incoming[static_cast<std::size_t>(target)] |= bit(source);
      }
    }
  }
  audit.missing_pairs =
      audit.raw.n * (audit.raw.n - 1) / 2 - total_arcs;

  const std::uint64_t universe =
      (std::uint64_t{1} << static_cast<unsigned>(audit.raw.n)) - 1U;
  audit.rows.reserve(static_cast<std::size_t>(audit.raw.n));
  audit.all_strict = true;
  for (int source = 0; source < audit.raw.n; ++source) {
    RowAudit row;
    row.vertex = source;
    row.direct = audit.out[static_cast<std::size_t>(source)];
    row.witness_counts.assign(static_cast<std::size_t>(audit.raw.n), 0);

    std::uint64_t reached = 0;
    for (int middle = 0; middle < audit.raw.n; ++middle) {
      if ((row.direct & bit(middle)) != 0) {
        reached |= audit.out[static_cast<std::size_t>(middle)];
      }
    }
    row.second = reached & ~row.direct & ~bit(source) & universe;
    row.unreachable = universe & ~row.direct & ~row.second & ~bit(source);
    row.d1 = std::popcount(row.direct);
    row.d2 = std::popcount(row.second);
    row.strict = row.d2 < row.d1;
    audit.all_strict = audit.all_strict && row.strict;

    std::vector<int> eligible_witness_counts;
    for (int target = 0; target < audit.raw.n; ++target) {
      const int witnesses = std::popcount(
          row.direct & incoming[static_cast<std::size_t>(target)]);
      row.witness_counts[static_cast<std::size_t>(target)] = witnesses;
      if (target != source && (row.direct & bit(target)) == 0) {
        eligible_witness_counts.push_back(witnesses);
      }
      if ((row.second & bit(target)) != 0) {
        row.witness_mass += static_cast<std::uint64_t>(witnesses) *
                            static_cast<std::uint64_t>(witnesses + 1) / 2U;
      }
    }

    std::sort(eligible_witness_counts.begin(), eligible_witness_counts.end());
    const int need = std::max(0, audit.raw.n - 2 * row.d1);
    const int available = static_cast<int>(eligible_witness_counts.size());
    for (int index = 0; index < std::min(need, available); ++index) {
      row.witness_energy += static_cast<std::uint64_t>(
          eligible_witness_counts[static_cast<std::size_t>(index)]);
    }
    if (need > available) {
      row.witness_energy += static_cast<std::uint64_t>(need - available);
    }

    if (!row.strict) {
      row.exact_penalty =
          static_cast<std::uint64_t>(row.d2 - row.d1 + 1);
    }
    audit.exact_objective += row.exact_penalty;
    audit.witness_energy += row.witness_energy;
    audit.rows.push_back(std::move(row));
  }

  audit.in_n19_domain = audit.raw.n == 19 && audit.minimum_outdegree >= 8;
  audit.accepted_counterexample = audit.in_n19_domain && audit.all_strict;
  if ((audit.exact_objective == 0) != audit.all_strict ||
      (audit.witness_energy == 0) != audit.all_strict) {
    throw std::logic_error("zero-equivalence invariant failed");
  }
  return audit;
}

void write_mask_array(std::ostream& output, std::uint64_t mask, int n) {
  output << '[';
  bool first = true;
  for (int vertex = 0; vertex < n; ++vertex) {
    if ((mask & bit(vertex)) == 0) {
      continue;
    }
    if (!first) {
      output << ',';
    }
    first = false;
    output << vertex;
  }
  output << ']';
}

void write_int_array(std::ostream& output, const std::vector<int>& values) {
  output << '[';
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index != 0) {
      output << ',';
    }
    output << values[index];
  }
  output << ']';
}

void write_audit(std::ostream& output, const Audit& audit) {
  output << '{';
  output << "\"status\":\""
         << (audit.accepted_counterexample ? "VERIFIED_COUNTEREXAMPLE"
                                           : "VERIFIED_NONHIT")
         << "\",";
  output << "\"n\":" << audit.raw.n << ',';
  output << "\"minimum_outdegree\":" << audit.minimum_outdegree << ',';
  output << "\"missing_pairs\":" << audit.missing_pairs << ',';
  output << "\"in_n19_domain\":"
         << (audit.in_n19_domain ? "true" : "false") << ',';
  output << "\"all_strict\":" << (audit.all_strict ? "true" : "false")
         << ',';
  output << "\"accepted_counterexample\":"
         << (audit.accepted_counterexample ? "true" : "false") << ',';
  output << "\"exact_objective\":" << audit.exact_objective << ',';
  output << "\"witness_energy\":" << audit.witness_energy << ',';
  output << "\"rows\":[";
  for (std::size_t index = 0; index < audit.rows.size(); ++index) {
    if (index != 0) {
      output << ',';
    }
    const RowAudit& row = audit.rows[index];
    output << '{';
    output << "\"vertex\":" << row.vertex << ',';
    output << "\"out_neighbors\":";
    write_mask_array(output, row.direct, audit.raw.n);
    output << ",\"second_neighbors\":";
    write_mask_array(output, row.second, audit.raw.n);
    output << ",\"unreachable\":";
    write_mask_array(output, row.unreachable, audit.raw.n);
    output << ",\"witness_counts\":";
    write_int_array(output, row.witness_counts);
    output << ",\"d1\":" << row.d1;
    output << ",\"d2\":" << row.d2;
    output << ",\"strict\":" << (row.strict ? "true" : "false");
    output << ",\"exact_penalty\":" << row.exact_penalty;
    output << ",\"witness_mass\":" << row.witness_mass;
    output << ",\"witness_energy\":" << row.witness_energy;
    output << '}';
  }
  output << "]}";
}

std::string read_all_stdin() {
  std::ostringstream buffer;
  buffer << std::cin.rdbuf();
  return buffer.str();
}

Audit parse_and_audit(const std::string& input) {
  Parser parser(input);
  return audit_raw(parser.parse_graph());
}

}  // namespace

int main(int argc, char** argv) {
  bool jsonl = false;
  if (argc == 2 && std::string_view(argv[1]) == "--jsonl") {
    jsonl = true;
  } else if (argc != 1) {
    std::cerr << "usage: audit_unrestricted19_raw [--jsonl]\n";
    return 2;
  }

  try {
    if (jsonl) {
      std::string line;
      while (std::getline(std::cin, line)) {
        if (line.empty()) {
          continue;
        }
        const Audit audit = parse_and_audit(line);
        write_audit(std::cout, audit);
        std::cout << '\n';
      }
    } else {
      const Audit audit = parse_and_audit(read_all_stdin());
      write_audit(std::cout, audit);
      std::cout << '\n';
    }
  } catch (const std::exception& error) {
    std::cerr << "AUDIT_ERROR: " << error.what() << '\n';
    return 2;
  }
  return 0;
}
