#define NOMINMAX
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cassert>
#include <charconv>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <mutex>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>
#ifdef _WIN32
#include <windows.h>
#else
#include <cerrno>
#endif

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

namespace ssnc {

constexpr int kTargetN = 19;
constexpr int kMinOutdegree = 8;
constexpr int kMaxN = 19;
constexpr std::uint64_t kDefaultSelfTestStates = 100000;

struct Graph {
  int n = 0;
  std::array<std::uint32_t, kMaxN> out{};

  [[nodiscard]] std::uint32_t mask() const {
    if (n <= 0 || n > kMaxN) return 0;
    return (std::uint32_t{1} << n) - 1U;
  }

  [[nodiscard]] int pair_state(int a, int b) const {
    if (!(0 <= a && a < b && b < n)) {
      throw std::invalid_argument("pair_state requires 0 <= a < b < n");
    }
    const bool ab = ((out[a] >> b) & 1U) != 0;
    const bool ba = ((out[b] >> a) & 1U) != 0;
    if (ab && ba) return 3;
    if (ab) return 1;
    if (ba) return 2;
    return 0;
  }

  void set_pair_state(int a, int b, int state) {
    if (!(0 <= a && a < b && b < n) || state < 0 || state > 2) {
      throw std::invalid_argument("bad pair state mutation");
    }
    out[a] &= ~(std::uint32_t{1} << b);
    out[b] &= ~(std::uint32_t{1} << a);
    if (state == 1) out[a] |= std::uint32_t{1} << b;
    if (state == 2) out[b] |= std::uint32_t{1} << a;
  }

  [[nodiscard]] bool operator==(const Graph& other) const {
    if (n != other.n) return false;
    for (int v = 0; v < n; ++v) {
      if (out[v] != other.out[v]) return false;
    }
    return true;
  }
};

struct Evaluation {
  bool structural_valid = false;
  bool domain_valid = false;
  bool strict_all = false;
  int strict_objective = 0;
  int smooth_energy = 0;
  int domain_deficit = 0;
  int objective = 0;
  int failing_vertices = 0;
  int actual_min_outdegree = 0;
  std::array<int, kMaxN> d1{};
  std::array<int, kMaxN> d2{};
  std::array<int, kMaxN> row_penalty{};
  std::array<int, kMaxN> row_smooth{};
  std::array<std::uint32_t, kMaxN> second{};

  [[nodiscard]] bool score_zero() const {
    return structural_valid && objective == 0;
  }
};

[[nodiscard]] Evaluation evaluate_bitset(const Graph& g, int min_outdegree) {
  Evaluation e;
  if (g.n <= 0 || g.n > kMaxN || min_outdegree < 0) return e;
  const std::uint32_t universe = g.mask();
  bool structural = true;
  for (int v = 0; v < g.n; ++v) {
    if ((g.out[v] & ~universe) != 0U) structural = false;
    if (((g.out[v] >> v) & 1U) != 0U) structural = false;
  }
  for (int a = 0; a < g.n; ++a) {
    for (int b = a + 1; b < g.n; ++b) {
      if (((g.out[a] >> b) & 1U) != 0U &&
          ((g.out[b] >> a) & 1U) != 0U) {
        structural = false;
      }
    }
  }
  e.structural_valid = structural;
  e.actual_min_outdegree = g.n;
  for (int v = 0; v < g.n; ++v) {
    const std::uint32_t direct = g.out[v] & universe;
    std::uint32_t reached2 = 0;
    std::uint32_t pending = direct;
    while (pending != 0U) {
      const int middle = std::countr_zero(pending);
      pending &= pending - 1U;
      reached2 |= g.out[middle] & universe;
    }
    const std::uint32_t new_second =
        reached2 & ~direct & ~(std::uint32_t{1} << v) & universe;
    const int d1 = std::popcount(direct);
    const int d2 = std::popcount(new_second);
    const int row_penalty = std::max(0, d2 - d1 + 1);
    std::vector<int> witness_counts;
    for (int target = 0; target < g.n; ++target) {
      if (target == v || ((direct >> target) & 1U) != 0U) continue;
      int witnesses = 0;
      std::uint32_t middles = direct;
      while (middles != 0U) {
        const int middle = std::countr_zero(middles);
        middles &= middles - 1U;
        witnesses += static_cast<int>((g.out[middle] >> target) & 1U);
      }
      witness_counts.push_back(witnesses);
    }
    std::sort(witness_counts.begin(), witness_counts.end());
    const int need = std::max(0, g.n - 2 * d1);
    int row_smooth = std::max(0, need - static_cast<int>(witness_counts.size()));
    for (int i = 0; i < std::min(need, static_cast<int>(witness_counts.size())); ++i) {
      row_smooth += witness_counts[static_cast<std::size_t>(i)];
    }
    const int degree_deficit = std::max(0, min_outdegree - d1);
    e.d1[v] = d1;
    e.d2[v] = d2;
    e.second[v] = new_second;
    e.row_penalty[v] = row_penalty;
    e.row_smooth[v] = row_smooth;
    e.strict_objective += row_penalty;
    e.smooth_energy += row_smooth;
    e.domain_deficit += degree_deficit;
    e.failing_vertices += (d2 >= d1) ? 1 : 0;
    e.actual_min_outdegree = std::min(e.actual_min_outdegree, d1);
  }
  e.strict_all = e.strict_objective == 0;
  e.domain_valid = e.domain_deficit == 0;
  e.objective = e.strict_objective + e.domain_deficit;
  return e;
}

[[nodiscard]] Evaluation evaluate_scalar(const Graph& g, int min_outdegree) {
  Evaluation e;
  if (g.n <= 0 || g.n > kMaxN || min_outdegree < 0) return e;
  std::vector<std::set<int>> rows(static_cast<std::size_t>(g.n));
  bool structural = true;
  const std::uint32_t universe = g.mask();
  for (int v = 0; v < g.n; ++v) {
    if ((g.out[v] & ~universe) != 0U) structural = false;
    for (int w = 0; w < g.n; ++w) {
      if (((g.out[v] >> w) & 1U) == 0U) continue;
      if (v == w) structural = false;
      rows[static_cast<std::size_t>(v)].insert(w);
    }
  }
  for (int a = 0; a < g.n; ++a) {
    for (int b = a + 1; b < g.n; ++b) {
      if (rows[static_cast<std::size_t>(a)].contains(b) &&
          rows[static_cast<std::size_t>(b)].contains(a)) {
        structural = false;
      }
    }
  }
  e.structural_valid = structural;
  e.actual_min_outdegree = g.n;
  for (int v = 0; v < g.n; ++v) {
    std::set<int> raw_length2;
    for (const int middle : rows[static_cast<std::size_t>(v)]) {
      for (const int target : rows[static_cast<std::size_t>(middle)]) {
        raw_length2.insert(target);
      }
    }
    std::set<int> new_second;
    for (const int target : raw_length2) {
      if (target != v &&
          !rows[static_cast<std::size_t>(v)].contains(target)) {
        new_second.insert(target);
      }
    }
    const int d1 = static_cast<int>(rows[static_cast<std::size_t>(v)].size());
    const int d2 = static_cast<int>(new_second.size());
    const int row_penalty = std::max(0, d2 - d1 + 1);
    std::vector<int> witness_counts;
    for (int target = 0; target < g.n; ++target) {
      if (target == v || rows[static_cast<std::size_t>(v)].contains(target)) continue;
      int witnesses = 0;
      for (const int middle : rows[static_cast<std::size_t>(v)]) {
        if (rows[static_cast<std::size_t>(middle)].contains(target)) ++witnesses;
      }
      witness_counts.push_back(witnesses);
    }
    std::sort(witness_counts.begin(), witness_counts.end());
    const int need = std::max(0, g.n - 2 * d1);
    int row_smooth = std::max(0, need - static_cast<int>(witness_counts.size()));
    for (int i = 0; i < std::min(need, static_cast<int>(witness_counts.size())); ++i) {
      row_smooth += witness_counts[static_cast<std::size_t>(i)];
    }
    const int degree_deficit = std::max(0, min_outdegree - d1);
    std::uint32_t second_mask = 0;
    for (const int target : new_second) {
      second_mask |= std::uint32_t{1} << target;
    }
    e.d1[v] = d1;
    e.d2[v] = d2;
    e.second[v] = second_mask;
    e.row_penalty[v] = row_penalty;
    e.row_smooth[v] = row_smooth;
    e.strict_objective += row_penalty;
    e.smooth_energy += row_smooth;
    e.domain_deficit += degree_deficit;
    e.failing_vertices += (d2 >= d1) ? 1 : 0;
    e.actual_min_outdegree = std::min(e.actual_min_outdegree, d1);
  }
  e.strict_all = e.strict_objective == 0;
  e.domain_valid = e.domain_deficit == 0;
  e.objective = e.strict_objective + e.domain_deficit;
  return e;
}
[[nodiscard]] bool evaluations_equal(const Evaluation& a,
                                     const Evaluation& b, int n,
                                     std::string* why = nullptr) {
  auto fail = [&](const std::string& message) {
    if (why != nullptr) *why = message;
    return false;
  };
  if (a.structural_valid != b.structural_valid) return fail("structural_valid");
  if (a.domain_valid != b.domain_valid) return fail("domain_valid");
  if (a.strict_all != b.strict_all) return fail("strict_all");
  if (a.strict_objective != b.strict_objective) return fail("strict_objective");
  if (a.smooth_energy != b.smooth_energy) return fail("smooth_energy");
  if (a.domain_deficit != b.domain_deficit) return fail("domain_deficit");
  if (a.objective != b.objective) return fail("objective");
  if (a.failing_vertices != b.failing_vertices) return fail("failing_vertices");
  if (a.actual_min_outdegree != b.actual_min_outdegree) {
    return fail("actual_min_outdegree");
  }
  if (a.score_zero() != b.score_zero()) return fail("score_zero");
  for (int v = 0; v < n; ++v) {
    if (a.d1[v] != b.d1[v]) return fail("d1[" + std::to_string(v) + "]");
    if (a.d2[v] != b.d2[v]) return fail("d2[" + std::to_string(v) + "]");
    if (a.row_penalty[v] != b.row_penalty[v]) {
      return fail("row_penalty[" + std::to_string(v) + "]");
    }
    if (a.row_smooth[v] != b.row_smooth[v]) {
      return fail("row_smooth[" + std::to_string(v) + "]");
    }
    if (a.second[v] != b.second[v]) {
      return fail("second[" + std::to_string(v) + "]");
    }
  }
  return true;
}

void require_oracle_agreement(const Graph& g, int min_outdegree,
                              std::string_view context) {
  const Evaluation fast = evaluate_bitset(g, min_outdegree);
  const Evaluation slow = evaluate_scalar(g, min_outdegree);
  std::string why;
  if (!evaluations_equal(fast, slow, g.n, &why)) {
    throw std::runtime_error(std::string(context) + ": oracle disagreement: " + why);
  }
  if ((fast.objective == 0) != (fast.domain_valid && fast.strict_all)) {
    throw std::runtime_error(std::string(context) +
                             ": objective-zero equivalence failed");
  }
  if ((fast.smooth_energy == 0) != fast.strict_all) {
    throw std::runtime_error(std::string(context) +
                             ": smooth-energy-zero equivalence failed");
  }
  if (fast.score_zero() !=
      (fast.structural_valid && fast.domain_valid && fast.strict_all)) {
    throw std::runtime_error(std::string(context) +
                             ": accepted-zero equivalence failed");
  }
}

[[nodiscard]] Graph cyclic_tournament(int n) {
  if (n <= 0 || n > kMaxN || n % 2 == 0) {
    throw std::invalid_argument("cyclic_tournament requires positive odd n");
  }
  Graph g;
  g.n = n;
  const int half = n / 2;
  for (int v = 0; v < n; ++v) {
    for (int delta = 1; delta <= half; ++delta) {
      const int w = (v + delta) % n;
      g.out[v] |= std::uint32_t{1} << w;
    }
  }
  return g;
}

[[nodiscard]] std::vector<std::pair<int, int>> pairs_for(int n) {
  std::vector<std::pair<int, int>> result;
  for (int a = 0; a < n; ++a) {
    for (int b = a + 1; b < n; ++b) result.emplace_back(a, b);
  }
  return result;
}

[[nodiscard]] std::uint64_t splitmix64(std::uint64_t x) {
  x += 0x9e3779b97f4a7c15ULL;
  x = (x ^ (x >> 30U)) * 0xbf58476d1ce4e5b9ULL;
  x = (x ^ (x >> 27U)) * 0x94d049bb133111ebULL;
  return x ^ (x >> 31U);
}

[[nodiscard]] std::string json_escape(std::string_view text) {
  std::ostringstream out;
  for (const unsigned char c : text) {
    switch (c) {
      case '\\': out << "\\\\"; break;
      case '"': out << "\\\""; break;
      case '\b': out << "\\b"; break;
      case '\f': out << "\\f"; break;
      case '\n': out << "\\n"; break;
      case '\r': out << "\\r"; break;
      case '\t': out << "\\t"; break;
      default:
        if (c < 0x20U) {
          out << "\\u" << std::hex << std::setw(4) << std::setfill('0')
              << static_cast<int>(c) << std::dec << std::setfill(' ');
        } else {
          out << static_cast<char>(c);
        }
    }
  }
  return out.str();
}

[[nodiscard]] std::string integer_list(std::uint32_t bits, int n) {
  std::ostringstream out;
  out << '[';
  bool first = true;
  for (int w = 0; w < n; ++w) {
    if (((bits >> w) & 1U) == 0U) continue;
    if (!first) out << ',';
    first = false;
    out << w;
  }
  out << ']';
  return out.str();
}

[[nodiscard]] std::string adjacency_json(const Graph& g) {
  std::ostringstream out;
  out << "[";
  for (int v = 0; v < g.n; ++v) {
    if (v != 0) out << ',';
    out << integer_list(g.out[v] & g.mask(), g.n);
  }
  out << ']';
  return out.str();
}

[[nodiscard]] std::string ledger_json(const Graph& g, const Evaluation& e) {
  std::ostringstream out;
  out << '[';
  const std::uint32_t universe = g.mask();
  for (int v = 0; v < g.n; ++v) {
    if (v != 0) out << ',';
    const std::uint32_t direct = g.out[v] & universe;
    const std::uint32_t unreachable =
        universe & ~(std::uint32_t{1} << v) & ~direct & ~e.second[v];
    out << "{\"vertex\":" << v
        << ",\"N+\":" << integer_list(direct, g.n)
        << ",\"new_N2+\":" << integer_list(e.second[v], g.n)
        << ",\"unreachable\":" << integer_list(unreachable, g.n)
        << ",\"out_degree\":" << e.d1[v]
        << ",\"new_second_degree\":" << e.d2[v]
        << ",\"strict\":" << (e.d2[v] < e.d1[v] ? "true" : "false")
        << ",\"row_penalty\":" << e.row_penalty[v]
        << ",\"smooth_witness_energy\":" << e.row_smooth[v] << '}';
  }
  out << ']';
  return out.str();
}

std::atomic<std::uint64_t> g_temp_serial{0};

void atomic_write_file(const fs::path& destination, const std::string& payload) {
  const std::uint64_t serial = g_temp_serial.fetch_add(1, std::memory_order_relaxed);
  fs::path temporary = destination;
  temporary += ".tmp." + std::to_string(serial);
  {
    std::ofstream stream(temporary, std::ios::binary | std::ios::trunc);
    if (!stream) throw std::runtime_error("cannot create " + temporary.string());
    stream.write(payload.data(), static_cast<std::streamsize>(payload.size()));
    stream.flush();
    if (!stream) throw std::runtime_error("cannot flush " + temporary.string());
  }
#ifdef _WIN32
  if (!MoveFileExW(temporary.c_str(), destination.c_str(),
                   MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
    const auto code = static_cast<unsigned long>(GetLastError());
    std::error_code ignored;
    fs::remove(temporary, ignored);
    throw std::runtime_error("atomic replace failed, win32=" + std::to_string(code));
  }
#else
  if (std::rename(temporary.c_str(), destination.c_str()) != 0) {
    const int code = errno;
    std::error_code ignored;
    fs::remove(temporary, ignored);
    throw std::runtime_error("atomic rename failed, errno=" + std::to_string(code));
  }
#endif
}
struct SelfTestReport {
  std::uint64_t exhaustive_graphs = 0;
  std::uint64_t exhaustive_rows = 0;
  std::uint64_t random_mutations = 0;
  std::uint64_t random_reverts = 0;
  std::uint64_t random_oracle_checks = 0;
  std::uint64_t random_domain_valid = 0;
  std::uint64_t random_domain_invalid = 0;
  std::uint64_t fixed_q_mutations = 0;
  std::uint64_t fixed_q_reverts = 0;
  std::uint64_t fixed_q_oracle_checks = 0;
  std::uint64_t fixed_q_domain_invalid = 0;
  std::uint64_t malformed_rejections = 0;
  std::array<std::array<std::uint64_t, 3>, 3> transitions{};
  std::uint64_t failures = 0;
};

[[nodiscard]] Graph degree_eight_boundary_graph() {
  Graph g = cyclic_tournament(kTargetN);
  for (int v = 0; v < kTargetN; ++v) {
    const int w = (v + 1) % kTargetN;
    const int a = std::min(v, w);
    const int b = std::max(v, w);
    g.set_pair_state(a, b, 0);
  }
  return g;
}

void exhaustive_small_self_test(SelfTestReport& report) {
  std::uint64_t expected_total = 0;
  for (int n = 1; n <= 5; ++n) {
    const auto pairs = pairs_for(n);
    std::uint64_t state_count = 1;
    for (std::size_t i = 0; i < pairs.size(); ++i) state_count *= 3ULL;
    expected_total += state_count;
    for (std::uint64_t code = 0; code < state_count; ++code) {
      Graph g;
      g.n = n;
      std::uint64_t digits = code;
      for (const auto& [a, b] : pairs) {
        const int state = static_cast<int>(digits % 3ULL);
        digits /= 3ULL;
        g.set_pair_state(a, b, state);
      }
      require_oracle_agreement(g, 0, "exhaustive-small");
      const Evaluation e = evaluate_bitset(g, 0);
      if (!e.structural_valid || !e.domain_valid ||
          ((e.objective == 0) != e.strict_all)) {
        throw std::runtime_error("exhaustive-small invariant failed");
      }
      ++report.exhaustive_graphs;
      report.exhaustive_rows += static_cast<std::uint64_t>(n);
    }
  }
  if (report.exhaustive_graphs != expected_total || expected_total != 59809ULL) {
    throw std::runtime_error("exhaustive-small count drifted");
  }
}

void explicit_fixture_self_test(SelfTestReport& report) {
  Graph transitive;
  transitive.n = 3;
  transitive.set_pair_state(0, 1, 1);
  transitive.set_pair_state(0, 2, 1);
  transitive.set_pair_state(1, 2, 1);
  require_oracle_agreement(transitive, 0, "direct-two-step-overlap");
  const Evaluation transitive_eval = evaluate_bitset(transitive, 0);
  if (transitive_eval.d1[0] != 2 || transitive_eval.d2[0] != 0 ||
      transitive_eval.second[0] != 0U) {
    throw std::runtime_error("direct out-neighbor was not excluded from new N2+");
  }

  Graph cycle;
  cycle.n = 3;
  cycle.set_pair_state(0, 1, 1);
  cycle.set_pair_state(1, 2, 1);
  cycle.set_pair_state(0, 2, 2);
  require_oracle_agreement(cycle, 0, "strict-versus-equality");
  const Evaluation cycle_eval = evaluate_bitset(cycle, 0);
  if (cycle_eval.strict_all || cycle_eval.strict_objective != 3 ||
      cycle_eval.objective == 0) {
    throw std::runtime_error("equality was incorrectly accepted as strict");
  }

  Graph boundary = degree_eight_boundary_graph();
  require_oracle_agreement(boundary, kMinOutdegree, "degree-eight-boundary");
  const Evaluation boundary_eval = evaluate_bitset(boundary, kMinOutdegree);
  if (!boundary_eval.domain_valid || boundary_eval.actual_min_outdegree != 8) {
    throw std::runtime_error("degree-eight boundary rejected");
  }
  Graph below = boundary;
  bool removed = false;
  for (int w = 0; w < below.n && !removed; ++w) {
    if (((below.out[0] >> w) & 1U) == 0U) continue;
    const int a = std::min(0, w);
    const int b = std::max(0, w);
    below.set_pair_state(a, b, 0);
    removed = true;
  }
  require_oracle_agreement(below, kMinOutdegree, "degree-seven-rejection");
  const Evaluation below_eval = evaluate_bitset(below, kMinOutdegree);
  if (!removed || below_eval.domain_valid || below_eval.domain_deficit != 1 ||
      below_eval.actual_min_outdegree != 7 || below_eval.score_zero()) {
    throw std::runtime_error("degree-seven graph was not rejected exactly");
  }

  Graph loop = cyclic_tournament(kTargetN);
  loop.out[0] |= 1U;
  require_oracle_agreement(loop, kMinOutdegree, "loop-rejection");
  if (evaluate_bitset(loop, kMinOutdegree).structural_valid) {
    throw std::runtime_error("loop was accepted");
  }
  ++report.malformed_rejections;

  Graph digon = cyclic_tournament(kTargetN);
  digon.out[0] |= std::uint32_t{1} << 1;
  digon.out[1] |= std::uint32_t{1} << 0;
  require_oracle_agreement(digon, kMinOutdegree, "digon-rejection");
  if (evaluate_bitset(digon, kMinOutdegree).structural_valid) {
    throw std::runtime_error("digon was accepted");
  }
  ++report.malformed_rejections;

  Graph outside = cyclic_tournament(kTargetN);
  outside.out[0] |= std::uint32_t{1} << kTargetN;
  require_oracle_agreement(outside, kMinOutdegree, "out-of-range-bit-rejection");
  if (evaluate_bitset(outside, kMinOutdegree).structural_valid) {
    throw std::runtime_error("out-of-range adjacency bit was accepted");
  }
  ++report.malformed_rejections;
}

void random_mutation_revert_self_test(SelfTestReport& report,
                                      std::uint64_t trials,
                                      std::uint64_t seed) {
  if (trials < kDefaultSelfTestStates) {
    throw std::invalid_argument("random self-test requires at least 100000 trials");
  }
  const auto pairs = pairs_for(kTargetN);
  std::mt19937_64 rng(seed);
  Graph walk = cyclic_tournament(kTargetN);
  for (std::uint64_t trial = 0; trial < trials; ++trial) {
    if (trial % 512ULL == 0ULL) {
      walk = ((trial / 512ULL) % 2ULL == 0ULL)
                 ? cyclic_tournament(kTargetN)
                 : degree_eight_boundary_graph();
    }
    const Graph before = walk;
    const Evaluation before_fast = evaluate_bitset(before, kMinOutdegree);
    const Evaluation before_slow = evaluate_scalar(before, kMinOutdegree);
    std::string before_why;
    if (!evaluations_equal(before_fast, before_slow, before.n, &before_why)) {
      throw std::runtime_error("random-before disagreement: " + before_why);
    }
    ++report.random_oracle_checks;

    const auto [a, b] = pairs[static_cast<std::size_t>(rng() % pairs.size())];
    const int old_state = walk.pair_state(a, b);
    const int offset = static_cast<int>(1ULL + (rng() & 1ULL));
    const int new_state = (old_state + offset) % 3;
    if (new_state == old_state) throw std::runtime_error("mutation did not change");
    ++report.transitions[static_cast<std::size_t>(old_state)]
                        [static_cast<std::size_t>(new_state)];
    walk.set_pair_state(a, b, new_state);
    require_oracle_agreement(walk, kMinOutdegree, "random-mutated");
    const Evaluation changed = evaluate_bitset(walk, kMinOutdegree);
    ++report.random_mutations;
    ++report.random_oracle_checks;
    if (changed.domain_valid) {
      ++report.random_domain_valid;
    } else {
      ++report.random_domain_invalid;
    }
    if (!changed.structural_valid || walk.pair_state(a, b) != new_state) {
      throw std::runtime_error("legal trit mutation violated orientation");
    }

    walk.set_pair_state(a, b, old_state);
    require_oracle_agreement(walk, kMinOutdegree, "random-reverted");
    const Evaluation restored = evaluate_bitset(walk, kMinOutdegree);
    std::string restored_why;
    if (!(walk == before) ||
        !evaluations_equal(before_fast, restored, walk.n, &restored_why)) {
      throw std::runtime_error("mutation/revert failed exact restoration: " +
                               restored_why);
    }
    ++report.random_reverts;
    ++report.random_oracle_checks;

    if ((rng() & 1ULL) != 0ULL) {
      walk.set_pair_state(a, b, new_state);
    }
  }
  for (int old_state = 0; old_state < 3; ++old_state) {
    for (int new_state = 0; new_state < 3; ++new_state) {
      if (old_state == new_state) continue;
      if (report.transitions[static_cast<std::size_t>(old_state)]
                            [static_cast<std::size_t>(new_state)] == 0ULL) {
        throw std::runtime_error("one legal ordered trit transition was untested");
      }
    }
  }
  if (report.random_domain_valid == 0 || report.random_domain_invalid == 0) {
    throw std::runtime_error("random audit missed a degree-domain side");
  }
}

[[nodiscard]] std::string self_test_json(const SelfTestReport& r,
                                         std::uint64_t seed) {
  std::ostringstream out;
  out << "{\"status\":\"SELF_TEST_PASS\""
      << ",\"production_run\":false"
      << ",\"seed\":" << seed
      << ",\"exhaustive_orders\":[1,2,3,4,5]"
      << ",\"exhaustive_graphs\":" << r.exhaustive_graphs
      << ",\"exhaustive_rows\":" << r.exhaustive_rows
      << ",\"random_mutations\":" << r.random_mutations
      << ",\"random_reverts\":" << r.random_reverts
      << ",\"random_oracle_checks\":" << r.random_oracle_checks
      << ",\"random_domain_valid\":" << r.random_domain_valid
      << ",\"random_domain_invalid\":" << r.random_domain_invalid
      << ",\"fixed_q_mutations\":" << r.fixed_q_mutations
      << ",\"fixed_q_reverts\":" << r.fixed_q_reverts
      << ",\"fixed_q_oracle_checks\":" << r.fixed_q_oracle_checks
      << ",\"fixed_q_domain_invalid\":" << r.fixed_q_domain_invalid
      << ",\"fixed_q_values_tested\":19"
      << ",\"malformed_rejections\":" << r.malformed_rejections
      << ",\"ordered_transition_counts\":[";
  bool first = true;
  for (int old_state = 0; old_state < 3; ++old_state) {
    for (int new_state = 0; new_state < 3; ++new_state) {
      if (old_state == new_state) continue;
      if (!first) out << ',';
      first = false;
      out << "{\"from\":" << old_state << ",\"to\":" << new_state
          << ",\"count\":"
          << r.transitions[static_cast<std::size_t>(old_state)]
                          [static_cast<std::size_t>(new_state)] << '}';
    }
  }
  out << "]"
      << ",\"audited\":[\"loops\",\"digons\",\"out_of_range_bits\","
         "\"minimum_outdegree_8_boundary\",\"degree_7_rejection\","
         "\"strict_vs_nonstrict\",\"direct_neighbor_exclusion\","
         "\"objective_zero_equivalence\",\"smooth_energy_zero_equivalence\",\"mutation_revert\"]"
      << ",\"failures\":" << r.failures << "}\n";
  return out.str();
}
struct SearchConfig {
  int threads = 0;
  int seconds = 0;
  std::uint64_t seed = 0;
  fs::path output_directory;
  std::uint64_t restart_steps = 250000;
  std::uint64_t warmup_steps = 5000;
  int checkpoint_ms = 5000;
};

struct AtomicCounters {
  std::atomic<std::uint64_t> evaluations{0};
  std::atomic<std::uint64_t> proposals{0};
  std::atomic<std::uint64_t> accepted{0};
  std::atomic<std::uint64_t> rejected{0};
  std::atomic<std::uint64_t> invalid_domain{0};
  std::atomic<std::uint64_t> warmup_kept{0};
  std::atomic<std::uint64_t> restarts{0};
  std::atomic<std::uint64_t> improvements{0};
  std::atomic<std::uint64_t> scalar_hit_replays{0};
};

struct CounterValues {
  std::uint64_t evaluations = 0;
  std::uint64_t proposals = 0;
  std::uint64_t accepted = 0;
  std::uint64_t rejected = 0;
  std::uint64_t invalid_domain = 0;
  std::uint64_t warmup_kept = 0;
  std::uint64_t restarts = 0;
  std::uint64_t improvements = 0;
  std::uint64_t scalar_hit_replays = 0;
};

[[nodiscard]] CounterValues read_counters(const AtomicCounters& c) {
  return {
      c.evaluations.load(std::memory_order_relaxed),
      c.proposals.load(std::memory_order_relaxed),
      c.accepted.load(std::memory_order_relaxed),
      c.rejected.load(std::memory_order_relaxed),
      c.invalid_domain.load(std::memory_order_relaxed),
      c.warmup_kept.load(std::memory_order_relaxed),
      c.restarts.load(std::memory_order_relaxed),
      c.improvements.load(std::memory_order_relaxed),
      c.scalar_hit_replays.load(std::memory_order_relaxed),
  };
}

[[nodiscard]] std::string counters_json(const CounterValues& c) {
  std::ostringstream out;
  out << "{\"evaluations\":" << c.evaluations
      << ",\"proposals\":" << c.proposals
      << ",\"accepted\":" << c.accepted
      << ",\"rejected\":" << c.rejected
      << ",\"invalid_domain\":" << c.invalid_domain
      << ",\"warmup_kept\":" << c.warmup_kept
      << ",\"restarts\":" << c.restarts
      << ",\"improvements\":" << c.improvements
      << ",\"scalar_hit_replays\":" << c.scalar_hit_replays << '}';
  return out.str();
}

struct BestSnapshot {
  bool present = false;
  Graph graph;
  Evaluation evaluation;
  int worker = -1;
  std::uint64_t worker_seed = 0;
  std::uint64_t restart = 0;
  std::uint64_t step = 0;
  std::uint64_t elapsed_ms = 0;
};

struct SharedSearch {
  explicit SharedSearch(const SearchConfig& input, Clock::time_point begin,
                        Clock::time_point finish)
      : config(input), start(begin), deadline(finish) {}

  SearchConfig config;
  Clock::time_point start;
  Clock::time_point deadline;
  std::atomic<bool> stop{false};
  std::atomic<bool> hit_claimed{false};
  std::atomic<bool> fatal{false};
  std::atomic<int> best_energy{std::numeric_limits<int>::max()};
  AtomicCounters counters;
  std::mutex best_mutex;
  BestSnapshot best;
  std::mutex error_mutex;
  std::string error;
};

[[nodiscard]] std::uint64_t elapsed_ms(const SharedSearch& shared) {
  return static_cast<std::uint64_t>(
      std::chrono::duration_cast<std::chrono::milliseconds>(Clock::now() -
                                                            shared.start)
          .count());
}

void record_fatal(SharedSearch& shared, const std::string& message) {
  {
    std::lock_guard<std::mutex> lock(shared.error_mutex);
    if (shared.error.empty()) shared.error = message;
  }
  shared.fatal.store(true, std::memory_order_release);
  shared.stop.store(true, std::memory_order_release);
}

void maybe_record_best(SharedSearch& shared, const Graph& graph,
                       const Evaluation& evaluation, int worker,
                       std::uint64_t worker_seed, std::uint64_t restart,
                       std::uint64_t step) {
  const int energy = evaluation.smooth_energy;
  int observed = shared.best_energy.load(std::memory_order_relaxed);
  while (energy < observed &&
         !shared.best_energy.compare_exchange_weak(
             observed, energy, std::memory_order_acq_rel,
             std::memory_order_relaxed)) {
  }
  if (energy != shared.best_energy.load(std::memory_order_acquire)) return;
  std::lock_guard<std::mutex> lock(shared.best_mutex);
  if (energy != shared.best_energy.load(std::memory_order_acquire)) return;
  if (shared.best.present &&
      shared.best.evaluation.smooth_energy <= energy) return;
  shared.best.present = true;
  shared.best.graph = graph;
  shared.best.evaluation = evaluation;
  shared.best.worker = worker;
  shared.best.worker_seed = worker_seed;
  shared.best.restart = restart;
  shared.best.step = step;
  shared.best.elapsed_ms = elapsed_ms(shared);
  shared.counters.improvements.fetch_add(1, std::memory_order_relaxed);
}
[[nodiscard]] std::string raw_candidate_json(const Graph& graph) {
  // Deliberately exactly these two keys: legacy scalar/bitset verifiers reject
  // any schema or metadata key in the raw-candidate file.
  std::ostringstream out;
  out << "{\"n\":" << graph.n
      << ",\"out_neighbors\":" << adjacency_json(graph) << "}\n";
  return out.str();
}

void raw_output_contract_self_test() {
  Graph graph;
  graph.n = 3;
  graph.set_pair_state(0, 1, 1);
  graph.set_pair_state(0, 2, 1);
  graph.set_pair_state(1, 2, 1);
  const std::string expected =
      "{\"n\":3,\"out_neighbors\":[[1,2],[2],[]]}\n";
  if (raw_candidate_json(graph) != expected) {
    throw std::runtime_error("raw hit candidate contract drifted");
  }
}

[[nodiscard]] int missing_pair_count(const Graph& graph);

[[nodiscard]] std::string snapshot_json(const BestSnapshot& snapshot,
                                        const CounterValues& counters) {
  std::ostringstream out;
  out << "{\"status\":\"BEST_CHECKPOINT_NOT_A_CERTIFICATE\""
      << ",\"n\":" << snapshot.graph.n
      << ",\"minimum_outdegree_required\":" << kMinOutdegree
      << ",\"q\":" << missing_pair_count(snapshot.graph)
      << ",\"worker\":" << snapshot.worker
      << ",\"worker_seed\":" << snapshot.worker_seed
      << ",\"restart\":" << snapshot.restart
      << ",\"step\":" << snapshot.step
      << ",\"elapsed_ms\":" << snapshot.elapsed_ms
      << ",\"structural_valid\":"
      << (snapshot.evaluation.structural_valid ? "true" : "false")
      << ",\"domain_valid\":"
      << (snapshot.evaluation.domain_valid ? "true" : "false")
      << ",\"strict_all\":"
      << (snapshot.evaluation.strict_all ? "true" : "false")
      << ",\"strict_objective\":" << snapshot.evaluation.strict_objective
      << ",\"smooth_witness_energy\":" << snapshot.evaluation.smooth_energy
      << ",\"domain_deficit\":" << snapshot.evaluation.domain_deficit
      << ",\"objective\":" << snapshot.evaluation.objective
      << ",\"failing_vertices\":" << snapshot.evaluation.failing_vertices
      << ",\"min_outdegree_actual\":"
      << snapshot.evaluation.actual_min_outdegree
      << ",\"out_neighbors\":" << adjacency_json(snapshot.graph)
      << ",\"ledger\":" << ledger_json(snapshot.graph, snapshot.evaluation)
      << ",\"counters\":" << counters_json(counters) << "}\n";
  return out.str();
}

[[nodiscard]] std::string hit_metadata_json(const Graph& graph,
                                            const Evaluation& evaluation,
                                            int worker,
                                            std::uint64_t worker_seed,
                                            std::uint64_t restart,
                                            std::uint64_t step,
                                            std::uint64_t elapsed,
                                            const CounterValues& counters) {
  std::ostringstream out;
  out << "{\"status\":\"RAW_HIT_PENDING_TWO_EXTERNAL_VERIFIERS\""
      << ",\"raw_candidate_file\":\"hit_candidate.json\""
      << ",\"n\":" << graph.n
      << ",\"minimum_outdegree_required\":" << kMinOutdegree
      << ",\"q\":" << missing_pair_count(graph)
      << ",\"worker\":" << worker
      << ",\"worker_seed\":" << worker_seed
      << ",\"restart\":" << restart
      << ",\"step\":" << step
      << ",\"elapsed_ms\":" << elapsed
      << ",\"structural_valid\":"
      << (evaluation.structural_valid ? "true" : "false")
      << ",\"domain_valid\":"
      << (evaluation.domain_valid ? "true" : "false")
      << ",\"strict_all\":" << (evaluation.strict_all ? "true" : "false")
      << ",\"objective\":" << evaluation.objective
      << ",\"smooth_witness_energy\":" << evaluation.smooth_energy
      << ",\"min_outdegree_actual\":" << evaluation.actual_min_outdegree
      << ",\"ledger\":" << ledger_json(graph, evaluation)
      << ",\"counters\":" << counters_json(counters) << "}\n";
  return out.str();
}
[[nodiscard]] int missing_pair_count(const Graph& graph) {
  int missing = 0;
  for (int a = 0; a < graph.n; ++a) {
    for (int b = a + 1; b < graph.n; ++b) {
      if (graph.pair_state(a, b) == 0) ++missing;
    }
  }
  return missing;
}

[[nodiscard]] Graph initial_graph_for_q(int q) {
  if (q < 1 || q > 19) throw std::invalid_argument("q must be in 1..19");
  Graph graph = cyclic_tournament(kTargetN);
  for (int v = 0; v < q; ++v) {
    const int w = (v + 1) % kTargetN;
    graph.set_pair_state(std::min(v, w), std::max(v, w), 0);
  }
  const Evaluation evaluation = evaluate_bitset(graph, kMinOutdegree);
  if (!evaluation.structural_valid || !evaluation.domain_valid ||
      missing_pair_count(graph) != q) {
    throw std::runtime_error("initial fixed-q construction failed");
  }
  return graph;
}

struct PairChange {
  int a = 0;
  int b = 0;
  int old_state = 0;
  int new_state = 0;
};

struct SearchMove {
  std::array<PairChange, 2> changes{};
  int count = 0;
};

[[nodiscard]] SearchMove propose_fixed_q_move(const Graph& graph,
                                              std::mt19937_64& rng) {
  const auto pairs = pairs_for(graph.n);
  std::vector<std::size_t> present;
  std::vector<std::size_t> missing;
  present.reserve(pairs.size());
  missing.reserve(pairs.size());
  for (std::size_t index = 0; index < pairs.size(); ++index) {
    const auto [a, b] = pairs[index];
    (graph.pair_state(a, b) == 0 ? missing : present).push_back(index);
  }
  if (present.empty()) throw std::runtime_error("no present pair for mutation");
  SearchMove move;
  const bool relocate = !missing.empty() && ((rng() & 1ULL) != 0ULL);
  if (!relocate) {
    const auto index = present[static_cast<std::size_t>(rng() % present.size())];
    const auto [a, b] = pairs[index];
    const int old_state = graph.pair_state(a, b);
    move.changes[0] = {a, b, old_state, old_state == 1 ? 2 : 1};
    move.count = 1;
    return move;
  }
  const auto missing_index =
      missing[static_cast<std::size_t>(rng() % missing.size())];
  const auto present_index =
      present[static_cast<std::size_t>(rng() % present.size())];
  const auto [ma, mb] = pairs[missing_index];
  const auto [pa, pb] = pairs[present_index];
  move.changes[0] = {ma, mb, 0, ((rng() & 1ULL) == 0ULL) ? 1 : 2};
  move.changes[1] = {pa, pb, graph.pair_state(pa, pb), 0};
  move.count = 2;
  return move;
}

void apply_move(Graph& graph, const SearchMove& move) {
  for (int i = 0; i < move.count; ++i) {
    const PairChange& change = move.changes[static_cast<std::size_t>(i)];
    if (graph.pair_state(change.a, change.b) != change.old_state) {
      throw std::runtime_error("move old-state mismatch");
    }
    graph.set_pair_state(change.a, change.b, change.new_state);
  }
}

void revert_move(Graph& graph, const SearchMove& move) {
  for (int i = move.count - 1; i >= 0; --i) {
    const PairChange& change = move.changes[static_cast<std::size_t>(i)];
    if (graph.pair_state(change.a, change.b) != change.new_state) {
      throw std::runtime_error("move new-state mismatch");
    }
    graph.set_pair_state(change.a, change.b, change.old_state);
  }
}

void fixed_q_move_self_test(SelfTestReport& report, std::uint64_t trials,
                            std::uint64_t seed) {
  if (trials < kDefaultSelfTestStates) {
    throw std::invalid_argument("fixed-q self-test requires at least 100000 trials");
  }
  std::array<Graph, 19> walks{};
  for (int q = 1; q <= 19; ++q) {
    walks[static_cast<std::size_t>(q - 1)] = initial_graph_for_q(q);
    require_oracle_agreement(walks[static_cast<std::size_t>(q - 1)],
                             kMinOutdegree, "fixed-q-initial");
  }
  std::mt19937_64 rng(splitmix64(seed ^ 0xa0761d6478bd642fULL));
  for (std::uint64_t trial = 0; trial < trials; ++trial) {
    const int q = 1 + static_cast<int>(trial % 19ULL);
    Graph& walk = walks[static_cast<std::size_t>(q - 1)];
    if (trial % (19ULL * 1024ULL) < 19ULL) walk = initial_graph_for_q(q);
    const Graph before = walk;
    const Evaluation before_eval = evaluate_bitset(before, kMinOutdegree);
    const SearchMove move = propose_fixed_q_move(walk, rng);
    apply_move(walk, move);
    require_oracle_agreement(walk, kMinOutdegree, "fixed-q-mutated");
    const Evaluation changed = evaluate_bitset(walk, kMinOutdegree);
    ++report.fixed_q_mutations;
    ++report.fixed_q_oracle_checks;
    if (!changed.structural_valid || missing_pair_count(walk) != q) {
      throw std::runtime_error("production move violated structure or fixed q");
    }
    if (!changed.domain_valid) ++report.fixed_q_domain_invalid;
    revert_move(walk, move);
    require_oracle_agreement(walk, kMinOutdegree, "fixed-q-reverted");
    const Evaluation restored = evaluate_bitset(walk, kMinOutdegree);
    std::string why;
    if (!(walk == before) ||
        !evaluations_equal(before_eval, restored, walk.n, &why) ||
        missing_pair_count(walk) != q) {
      throw std::runtime_error("fixed-q move/revert mismatch: " + why);
    }
    ++report.fixed_q_reverts;
    ++report.fixed_q_oracle_checks;
    if (changed.domain_valid && ((rng() & 1ULL) != 0ULL)) {
      apply_move(walk, move);
    }
  }
  if (report.fixed_q_domain_invalid == 0) {
    throw std::runtime_error("fixed-q audit never exercised degree rejection");
  }
}
[[nodiscard]] bool deadline_reached(const SharedSearch& shared) {
  return Clock::now() >= shared.deadline;
}

void claim_raw_hit(SharedSearch& shared, const Graph& graph,
                   const Evaluation& fast, int worker,
                   std::uint64_t worker_seed, std::uint64_t restart,
                   std::uint64_t step) {
  const Evaluation scalar = evaluate_scalar(graph, kMinOutdegree);
  shared.counters.scalar_hit_replays.fetch_add(1, std::memory_order_relaxed);
  std::string why;
  if (!evaluations_equal(fast, scalar, graph.n, &why)) {
    throw std::runtime_error("raw hit internal replay disagreement: " + why);
  }
  if (!fast.structural_valid || !fast.domain_valid || !fast.strict_all ||
      fast.objective != 0 || fast.smooth_energy != 0 || !fast.score_zero() ||
      graph.n != kTargetN) {
    throw std::runtime_error("raw hit failed exact predicate");
  }
  bool expected = false;
  if (!shared.hit_claimed.compare_exchange_strong(
          expected, true, std::memory_order_acq_rel)) {
    shared.stop.store(true, std::memory_order_release);
    return;
  }
  // Stop every lane before certificate I/O. Each file is then atomically
  // replaced from complete bytes; the raw file has no metadata keys.
  shared.stop.store(true, std::memory_order_release);
  const CounterValues counters = read_counters(shared.counters);
  atomic_write_file(shared.config.output_directory / "hit_candidate.json",
                    raw_candidate_json(graph));
  atomic_write_file(
      shared.config.output_directory / "hit_metadata.json",
      hit_metadata_json(graph, scalar, worker, worker_seed, restart, step,
                        elapsed_ms(shared), counters));
}

void evaluate_search_state(SharedSearch& shared, const Graph& graph,
                           int target_q, int worker,
                           std::uint64_t worker_seed,
                           std::uint64_t restart, std::uint64_t step,
                           const Evaluation& evaluation) {
  if (!evaluation.structural_valid) {
    throw std::runtime_error("fixed-q move created structural invalidity");
  }
  if (missing_pair_count(graph) != target_q) {
    throw std::runtime_error("fixed-q move changed missing-pair count");
  }
  maybe_record_best(shared, graph, evaluation, worker, worker_seed, restart,
                    step);
  if (evaluation.score_zero()) {
    claim_raw_hit(shared, graph, evaluation, worker, worker_seed, restart,
                  step);
  }
}

void search_worker(SharedSearch& shared, int worker) {
  try {
    const std::uint64_t worker_seed =
        splitmix64(shared.config.seed ^
                   (0xd1b54a32d192ed03ULL *
                    static_cast<std::uint64_t>(worker + 1)));
    std::mt19937_64 rng(worker_seed);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    std::uint64_t restart = 0;
    while (!shared.stop.load(std::memory_order_acquire) &&
           !deadline_reached(shared)) {
      const int target_q = 1 + static_cast<int>(
          (static_cast<std::uint64_t>(worker) +
           restart * static_cast<std::uint64_t>(shared.config.threads)) %
          19ULL);
      Graph graph = initial_graph_for_q(target_q);
      Evaluation current = evaluate_bitset(graph, kMinOutdegree);
      shared.counters.evaluations.fetch_add(1, std::memory_order_relaxed);
      shared.counters.restarts.fetch_add(1, std::memory_order_relaxed);
      evaluate_search_state(shared, graph, target_q, worker, worker_seed,
                            restart, 0, current);
      if (shared.stop.load(std::memory_order_acquire)) break;

      for (std::uint64_t warm = 0;
           warm < shared.config.warmup_steps &&
           !shared.stop.load(std::memory_order_acquire) &&
           !deadline_reached(shared);
           ++warm) {
        const SearchMove move = propose_fixed_q_move(graph, rng);
        apply_move(graph, move);
        const Evaluation candidate = evaluate_bitset(graph, kMinOutdegree);
        shared.counters.proposals.fetch_add(1, std::memory_order_relaxed);
        shared.counters.evaluations.fetch_add(1, std::memory_order_relaxed);
        if (!candidate.structural_valid || !candidate.domain_valid) {
          shared.counters.invalid_domain.fetch_add(1, std::memory_order_relaxed);
          revert_move(graph, move);
          continue;
        }
        current = candidate;
        shared.counters.warmup_kept.fetch_add(1, std::memory_order_relaxed);
        evaluate_search_state(shared, graph, target_q, worker, worker_seed,
                              restart, warm + 1, current);
      }

      for (std::uint64_t step = 0;
           step < shared.config.restart_steps &&
           !shared.stop.load(std::memory_order_acquire) &&
           !deadline_reached(shared);
           ++step) {
        const SearchMove move = propose_fixed_q_move(graph, rng);
        apply_move(graph, move);
        const Evaluation candidate = evaluate_bitset(graph, kMinOutdegree);
        shared.counters.proposals.fetch_add(1, std::memory_order_relaxed);
        shared.counters.evaluations.fetch_add(1, std::memory_order_relaxed);
        if (!candidate.structural_valid || !candidate.domain_valid) {
          shared.counters.invalid_domain.fetch_add(1, std::memory_order_relaxed);
          revert_move(graph, move);
          continue;
        }
        const int delta = candidate.smooth_energy - current.smooth_energy;
        const double phase = static_cast<double>(step % 50000ULL) / 50000.0;
        const double temperature = 0.05 + 2.95 * (1.0 - phase);
        const bool accept =
            delta <= 0 || unit(rng) < std::exp(-static_cast<double>(delta) /
                                               temperature);
        if (accept) {
          current = candidate;
          shared.counters.accepted.fetch_add(1, std::memory_order_relaxed);
          evaluate_search_state(shared, graph, target_q, worker, worker_seed,
                                restart, shared.config.warmup_steps + step + 1,
                                current);
        } else {
          revert_move(graph, move);
          shared.counters.rejected.fetch_add(1, std::memory_order_relaxed);
        }
      }
      ++restart;
    }
  } catch (const std::exception& error) {
    record_fatal(shared, "worker " + std::to_string(worker) + ": " +
                             error.what());
  } catch (...) {
    record_fatal(shared, "worker " + std::to_string(worker) +
                             ": unknown exception");
  }
}
[[nodiscard]] std::string config_json(const SearchConfig& config) {
  std::ostringstream out;
  out << "{\"schema\":\"ssnc-unrestricted19-search-config-v1\""
      << ",\"n\":19,\"minimum_outdegree\":8"
      << ",\"threads\":" << config.threads
      << ",\"seconds\":" << config.seconds
      << ",\"seed\":" << config.seed
      << ",\"restart_steps\":" << config.restart_steps
      << ",\"warmup_steps\":" << config.warmup_steps
      << ",\"checkpoint_ms\":" << config.checkpoint_ms
      << ",\"q_portfolio\":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]"
      << ",\"q_assignment\":\"1+((worker+restart*threads) mod 19)\""
      << ",\"q_zero_exclusion\":\"tournament case theorem\""
      << ",\"q_upper_bridge\":\"min outdegree 8 implies at least 152 of 171 pairs present\""
      << ",\"mutation_family\":\"arc reversal or missing-edge relocation, fixed q\""
      << ",\"search_energy\":\"sum over v of need smallest literal two-step witness counts, need=max(0,19-2*outdegree(v))\""
      << ",\"hit_predicate\":\"structural_valid and min_outdegree>=8 and every new_second_degree<out_degree\""
      << ",\"raw_hit_contract\":\"hit_candidate.json has exactly n,out_neighbors\""
      << ",\"result_semantics\":\"NO_HIT is bounded heuristic failure, not a proof\"}\n";
  return out.str();
}

void write_best_checkpoint(SharedSearch& shared) {
  BestSnapshot copy;
  {
    std::lock_guard<std::mutex> lock(shared.best_mutex);
    if (!shared.best.present) return;
    copy = shared.best;
  }
  atomic_write_file(shared.config.output_directory / "best_checkpoint.json",
                    snapshot_json(copy, read_counters(shared.counters)));
}

[[nodiscard]] std::string final_summary_json(SharedSearch& shared) {
  const CounterValues counters = read_counters(shared.counters);
  BestSnapshot best;
  {
    std::lock_guard<std::mutex> lock(shared.best_mutex);
    best = shared.best;
  }
  std::string error;
  {
    std::lock_guard<std::mutex> lock(shared.error_mutex);
    error = shared.error;
  }
  const bool fatal = shared.fatal.load(std::memory_order_acquire);
  const bool hit = shared.hit_claimed.load(std::memory_order_acquire);
  const char* status = fatal ? "FAILED"
                             : (hit ? "RAW_HIT_PENDING_TWO_EXTERNAL_VERIFIERS"
                                    : "NO_HIT");
  const bool counter_partition =
      counters.proposals == counters.invalid_domain + counters.warmup_kept +
                                counters.accepted + counters.rejected;
  const bool evaluation_partition =
      counters.evaluations == counters.proposals + counters.restarts;
  std::ostringstream out;
  out << "{\"schema\":\"ssnc-unrestricted19-search-summary-v1\""
      << ",\"status\":\"" << status << "\""
      << ",\"resolution_claimed\":false"
      << ",\"n\":19,\"minimum_outdegree\":8"
      << ",\"threads\":" << shared.config.threads
      << ",\"seconds_requested\":" << shared.config.seconds
      << ",\"elapsed_ms\":" << elapsed_ms(shared)
      << ",\"seed\":" << shared.config.seed
      << ",\"hit_candidate_file\":"
      << (hit ? "\"hit_candidate.json\"" : "null")
      << ",\"best_present\":" << (best.present ? "true" : "false");
  if (best.present) {
    out << ",\"best_smooth_witness_energy\":" << best.evaluation.smooth_energy
        << ",\"best_literal_objective\":" << best.evaluation.objective
        << ",\"best_strict_objective\":" << best.evaluation.strict_objective
        << ",\"best_failing_vertices\":" << best.evaluation.failing_vertices
        << ",\"best_q\":" << missing_pair_count(best.graph)
        << ",\"best_min_outdegree\":" << best.evaluation.actual_min_outdegree;
  }
  out << ",\"counter_partition_valid\":"
      << (counter_partition ? "true" : "false")
      << ",\"evaluation_partition_valid\":"
      << (evaluation_partition ? "true" : "false")
      << ",\"counters\":" << counters_json(counters)
      << ",\"error\":"
      << (error.empty() ? "null" : "\"" + json_escape(error) + "\"")
      << ",\"note\":\"NO_HIT is not UNSAT and does not resolve SSNC\"}\n";
  return out.str();
}

[[nodiscard]] std::string run_search(const SearchConfig& config) {
  if (config.threads < 1 || config.threads > 64) {
    throw std::invalid_argument("--threads must be in 1..64");
  }
  if (config.seconds < 1) throw std::invalid_argument("--seconds must be positive");
  if (config.output_directory.empty()) {
    throw std::invalid_argument("--output-dir is required");
  }
  if (config.checkpoint_ms < 100 || config.checkpoint_ms > 60000) {
    throw std::invalid_argument("--checkpoint-ms must be in 100..60000");
  }
  if (config.restart_steps == 0 || config.warmup_steps == 0) {
    throw std::invalid_argument("restart and warmup steps must be positive");
  }
  if (fs::exists(config.output_directory)) {
    if (!fs::is_directory(config.output_directory)) {
      throw std::invalid_argument("output path exists and is not a directory");
    }
    if (!fs::is_empty(config.output_directory)) {
      throw std::invalid_argument("refusing nonempty output directory");
    }
  } else if (!fs::create_directories(config.output_directory)) {
    throw std::runtime_error("could not create output directory");
  }
  atomic_write_file(config.output_directory / "config.json", config_json(config));

  const Clock::time_point start = Clock::now();
  const Clock::time_point deadline = start + std::chrono::seconds(config.seconds);
  SharedSearch shared(config, start, deadline);
  std::vector<std::thread> workers;
  workers.reserve(static_cast<std::size_t>(config.threads));
  try {
    for (int worker = 0; worker < config.threads; ++worker) {
      workers.emplace_back(search_worker, std::ref(shared), worker);
    }
  } catch (...) {
    shared.stop.store(true, std::memory_order_release);
    for (std::thread& worker : workers) worker.join();
    throw;
  }

  Clock::time_point next_checkpoint =
      start + std::chrono::milliseconds(config.checkpoint_ms);
  while (!shared.stop.load(std::memory_order_acquire) && Clock::now() < deadline) {
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    if (Clock::now() >= next_checkpoint) {
      try {
        write_best_checkpoint(shared);
      } catch (const std::exception& error) {
        record_fatal(shared, std::string("checkpoint: ") + error.what());
      }
      next_checkpoint += std::chrono::milliseconds(config.checkpoint_ms);
    }
  }
  shared.stop.store(true, std::memory_order_release);
  for (std::thread& worker : workers) worker.join();
  try {
    write_best_checkpoint(shared);
  } catch (const std::exception& error) {
    record_fatal(shared, std::string("final checkpoint: ") + error.what());
  }
  const std::string summary = final_summary_json(shared);
  atomic_write_file(config.output_directory / "summary.json", summary);
  return summary;
}

struct CommandLine {
  bool self_test = false;
  bool help = false;
  bool search_marker = false;
  bool seed_given = false;
  std::uint64_t self_test_random = kDefaultSelfTestStates;
  SearchConfig search;
};

template <typename Integer>
[[nodiscard]] Integer parse_integer(std::string_view text,
                                    std::string_view option) {
  Integer value{};
  const char* begin = text.data();
  const char* end = text.data() + text.size();
  const auto result = std::from_chars(begin, end, value);
  if (result.ec != std::errc{} || result.ptr != end) {
    throw std::invalid_argument(std::string(option) + " requires an integer");
  }
  return value;
}

[[nodiscard]] CommandLine parse_command_line(int argc, char** argv) {
  CommandLine options;
  for (int i = 1; i < argc; ++i) {
    const std::string_view argument(argv[i]);
    auto value = [&](std::string_view name) -> std::string_view {
      if (++i >= argc) throw std::invalid_argument(std::string(name) + " needs a value");
      return argv[i];
    };
    if (argument == "--help" || argument == "-h") {
      options.help = true;
    } else if (argument == "--self-test") {
      options.self_test = true;
    } else if (argument == "--search") {
      options.search_marker = true;
    } else if (argument == "--self-test-random") {
      options.self_test_random =
          parse_integer<std::uint64_t>(value(argument), argument);
    } else if (argument == "--threads") {
      options.search.threads = parse_integer<int>(value(argument), argument);
    } else if (argument == "--seconds") {
      options.search.seconds = parse_integer<int>(value(argument), argument);
    } else if (argument == "--seed") {
      options.search.seed = parse_integer<std::uint64_t>(value(argument), argument);
      options.seed_given = true;
    } else if (argument == "--output-dir") {
      options.search.output_directory = std::string(value(argument));
    } else if (argument == "--restart-steps") {
      options.search.restart_steps =
          parse_integer<std::uint64_t>(value(argument), argument);
    } else if (argument == "--warmup-steps") {
      options.search.warmup_steps =
          parse_integer<std::uint64_t>(value(argument), argument);
    } else if (argument == "--checkpoint-ms") {
      options.search.checkpoint_ms = parse_integer<int>(value(argument), argument);
    } else {
      throw std::invalid_argument("unknown option: " + std::string(argument));
    }
  }
  return options;
}

void print_usage() {
  std::cout
      << "Self-test only:\n"
      << "  unrestricted19_stochastic --self-test [--self-test-random N] [--seed S]\n"
      << "Production search (not started by default):\n"
      << "  unrestricted19_stochastic [--search] --threads 1..64 --seconds S --seed S --output-dir DIR\n";
}

}  // namespace ssnc

int main(int argc, char** argv) {
  try {
    ssnc::CommandLine options = ssnc::parse_command_line(argc, argv);
    if (options.help) {
      ssnc::print_usage();
      return 0;
    }
    if (options.self_test) {
      if (options.search_marker || options.search.threads != 0 ||
          options.search.seconds != 0 || !options.search.output_directory.empty()) {
        throw std::invalid_argument("self-test and search options cannot be mixed");
      }
      const std::uint64_t seed =
          options.seed_given ? options.search.seed : 19081993ULL;
      ssnc::SelfTestReport report;
      ssnc::exhaustive_small_self_test(report);
      ssnc::explicit_fixture_self_test(report);
      ssnc::raw_output_contract_self_test();
      ssnc::random_mutation_revert_self_test(report, options.self_test_random,
                                             seed);
      ssnc::fixed_q_move_self_test(report, options.self_test_random, seed);
      std::cout << ssnc::self_test_json(report, seed);
      return 0;
    }
    const bool search_requested =
        options.search_marker || options.search.threads != 0 ||
        options.search.seconds != 0 || !options.search.output_directory.empty();
    if (!search_requested) {
      throw std::invalid_argument("no mode selected; use --self-test or search flags");
    }
    if (!options.seed_given) throw std::invalid_argument("--seed is required for search");
    const std::string summary = ssnc::run_search(options.search);
    std::cout << summary;
    return summary.find("\"status\":\"FAILED\"") == std::string::npos ? 0 : 3;
  } catch (const std::exception& error) {
    std::cerr << "ERROR: " << error.what() << '\n';
    return 2;
  }
}