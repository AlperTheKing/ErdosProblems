// Independent exact branch-and-bound solver for Erdos Problem 864.
//
// The only symmetry reduction is translation to min(A) = 1.  If m=min(A),
// replacing every a by a-m+1 preserves every sum multiplicity (sum labels are
// merely translated) and keeps the set in [1,N].

#include <algorithm>
#include <atomic>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <mutex>
#include <numeric>
#include <optional>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;

struct Options {
  int n = -1;
  double timeout_seconds = 0.0;
  unsigned threads = 1;
  std::uint64_t seed = 864;
  int heuristic_restarts = 6000;
};

struct CheckResult {
  bool admissible = false;
  int exceptional_sum = -1;
  int exceptional_multiplicity = 0;
  std::string error;
};

CheckResult check_admissible(const std::vector<int>& input, int n) {
  CheckResult result;
  std::vector<int> a = input;
  std::sort(a.begin(), a.end());
  for (std::size_t i = 0; i < a.size(); ++i) {
    if (a[i] < 1 || a[i] > n) {
      result.error = "element-out-of-range";
      return result;
    }
    if (i != 0 && a[i] == a[i - 1]) {
      result.error = "duplicate-element";
      return result;
    }
  }

  std::vector<int> representations(static_cast<std::size_t>(2 * n + 1), 0);
  for (std::size_t i = 0; i < a.size(); ++i) {
    for (std::size_t j = i; j < a.size(); ++j) {
      ++representations[static_cast<std::size_t>(a[i] + a[j])];
    }
  }

  for (int s = 2; s <= 2 * n; ++s) {
    if (representations[static_cast<std::size_t>(s)] < 2) {
      continue;
    }
    if (result.exceptional_sum != -1) {
      result.error = "multiple-repeated-sum-values";
      return result;
    }
    result.exceptional_sum = s;
    result.exceptional_multiplicity =
        representations[static_cast<std::size_t>(s)];
  }
  result.admissible = true;
  return result;
}

std::string json_array(const std::vector<int>& values) {
  std::ostringstream out;
  out << '[';
  for (std::size_t i = 0; i < values.size(); ++i) {
    if (i != 0) {
      out << ',';
    }
    out << values[i];
  }
  out << ']';
  return out.str();
}

// Incremental state.  count[s] is exact, while exception is the unique sum
// whose count may exceed one.  New sums made by x are pairwise distinct:
// x+y for old y, and 2x.  This makes the collision test both simple and exact.
class State {
 public:
  struct Undo {
    int old_exception = -1;
    int old_exception_multiplicity = 0;
  };

  explicit State(int n)
      : n_(n), count_(static_cast<std::size_t>(2 * n + 1), 0) {}

  bool can_add(int x) const {
    int new_exception = -1;
    for (int y : chosen_) {
      if (!accept_collision(x + y, new_exception)) {
        return false;
      }
    }
    return accept_collision(2 * x, new_exception);
  }

  bool add(int x, Undo& undo) {
    if (!can_add(x)) {
      return false;
    }
    undo.old_exception = exception_;
    undo.old_exception_multiplicity = exception_multiplicity_;

    int collided_sum = -1;
    for (int y : chosen_) {
      const int s = x + y;
      if (count_[static_cast<std::size_t>(s)] != 0) {
        collided_sum = s;
      }
      if (count_[static_cast<std::size_t>(s)]++ == 0) {
        ++occupied_count_;
      }
    }
    const int diagonal = 2 * x;
    if (count_[static_cast<std::size_t>(diagonal)] != 0) {
      collided_sum = diagonal;
    }
    if (count_[static_cast<std::size_t>(diagonal)]++ == 0) {
      ++occupied_count_;
    }
    chosen_.push_back(x);

    if (exception_ == -1 && collided_sum != -1) {
      exception_ = collided_sum;
      exception_multiplicity_ = 2;
    } else if (exception_ != -1 && collided_sum == exception_) {
      ++exception_multiplicity_;
    }
    return true;
  }

  void undo(int x, const Undo& undo) {
    if (chosen_.empty() || chosen_.back() != x) {
      throw std::logic_error("non-LIFO State::undo");
    }
    chosen_.pop_back();
    for (int y : chosen_) {
      const int s = x + y;
      if (--count_[static_cast<std::size_t>(s)] == 0) {
        --occupied_count_;
      }
    }
    const int diagonal = 2 * x;
    if (--count_[static_cast<std::size_t>(diagonal)] == 0) {
      --occupied_count_;
    }
    exception_ = undo.old_exception;
    exception_multiplicity_ = undo.old_exception_multiplicity;
  }

  int n() const { return n_; }
  int size() const { return static_cast<int>(chosen_.size()); }
  int occupied_count() const { return occupied_count_; }
  int exception() const { return exception_; }
  int exception_multiplicity() const { return exception_multiplicity_; }
  const std::vector<int>& chosen() const { return chosen_; }

  int maximum() const {
    return chosen_.empty()
               ? 0
               : *std::max_element(chosen_.begin(), chosen_.end());
  }

 private:
  bool accept_collision(int sum, int& new_exception) const {
    if (count_[static_cast<std::size_t>(sum)] == 0) {
      return true;
    }
    if (exception_ != -1) {
      return sum == exception_;
    }
    if (new_exception == -1) {
      new_exception = sum;
      return true;
    }
    return new_exception == sum;
  }

  int n_;
  std::vector<std::uint16_t> count_;
  std::vector<int> chosen_;
  int occupied_count_ = 0;
  int exception_ = -1;
  int exception_multiplicity_ = 0;
};

long long pair_count(int k) {
  return static_cast<long long>(k) * (k + 1) / 2;
}

// Every representation of one fixed sum uses a disjoint pair of elements,
// except for at most one diagonal.  Hence its multiplicity is <= ceil(k/2).
long long minimum_distinct_sums(int k) {
  if (k == 0) {
    return 0;
  }
  return pair_count(k) - (k + 1) / 2 + 1;
}

int universal_upper_bound(int n) {
  int answer = 0;
  for (int k = 1; k <= n; ++k) {
    if (minimum_distinct_sums(k) <= 2LL * n - 1) {
      answer = k;
    } else {
      break;
    }
  }
  return answer;
}

// A Sidon subset of an interval of length L has C(k,2) distinct positive
// differences, all in [1,L-1].
int sidon_difference_cap(int interval_length) {
  if (interval_length <= 0) {
    return 0;
  }
  int k = 1;
  while (static_cast<long long>(k + 1) * k / 2 <= interval_length - 1) {
    ++k;
  }
  return k;
}

struct Shared {
  int n;
  Clock::time_point start;
  std::optional<Clock::time_point> deadline;
  std::atomic<int> best_size{0};
  std::atomic<bool> stop{false};
  std::atomic<bool> timed_out{false};
  std::atomic<bool> internal_error{false};
  std::atomic<std::uint64_t> nodes{0};
  std::mutex mutex;
  std::vector<int> best_set;
  std::string error_message;

  explicit Shared(int n_value) : n(n_value), start(Clock::now()) {}

  double elapsed_seconds() const {
    return std::chrono::duration<double>(Clock::now() - start).count();
  }

  bool deadline_reached() {
    if (!deadline || Clock::now() < *deadline) {
      return false;
    }
    timed_out.store(true, std::memory_order_relaxed);
    stop.store(true, std::memory_order_relaxed);
    return true;
  }

  void fail(const std::string& message) {
    std::lock_guard<std::mutex> lock(mutex);
    if (!internal_error.exchange(true, std::memory_order_relaxed)) {
      error_message = message;
    }
    stop.store(true, std::memory_order_relaxed);
  }

  void publish(std::vector<int> candidate) {
    std::sort(candidate.begin(), candidate.end());
    if (static_cast<int>(candidate.size()) <=
        best_size.load(std::memory_order_relaxed)) {
      return;
    }
    const CheckResult checked = check_admissible(candidate, n);
    if (!checked.admissible) {
      fail("incremental-state-candidate-failed-independent-check:" +
           checked.error);
      return;
    }

    std::lock_guard<std::mutex> lock(mutex);
    if (static_cast<int>(candidate.size()) <=
        best_size.load(std::memory_order_relaxed)) {
      return;
    }
    best_set = candidate;
    best_size.store(static_cast<int>(candidate.size()),
                    std::memory_order_relaxed);

    std::cout << "{\"type\":\"candidate\",\"n\":" << n
              << ",\"size\":" << candidate.size()
              << ",\"set\":" << json_array(candidate)
              << ",\"exceptional_sum\":";
    if (checked.exceptional_sum == -1) {
      std::cout << "null";
    } else {
      std::cout << checked.exceptional_sum;
    }
    std::cout << ",\"exceptional_multiplicity\":"
              << checked.exceptional_multiplicity
              << ",\"verified\":true,\"elapsed_seconds\":" << std::fixed
              << std::setprecision(6) << elapsed_seconds() << "}\n";
    std::cout.flush();
  }
};

int maximum_possible_exception_representations(
    const State& state, const std::vector<int>& candidates, int end) {
  if (state.exception() == -1) {
    return 0;
  }
  std::vector<unsigned char> available(static_cast<std::size_t>(state.n() + 1),
                                       0);
  for (int x : state.chosen()) {
    available[static_cast<std::size_t>(x)] = 1;
  }
  for (int i = 0; i < end; ++i) {
    available[static_cast<std::size_t>(candidates[static_cast<std::size_t>(i)])] =
        1;
  }

  int count = 0;
  const int e = state.exception();
  for (int x = std::max(1, e - state.n()); x <= e / 2; ++x) {
    const int y = e - x;
    if (y < 1 || y > state.n()) {
      continue;
    }
    if (available[static_cast<std::size_t>(x)] != 0 &&
        available[static_cast<std::size_t>(y)] != 0) {
      ++count;
    }
  }
  return count;
}

bool sum_capacity_allows(const State& state, int final_size, int final_max,
                         int exception_rep_cap) {
  const int current_size = state.size();
  const int additions = final_size - current_size;
  if (additions < 0) {
    return false;
  }

  const long long new_pair_occurrences =
      pair_count(final_size) - pair_count(current_size);
  long long maximum_saved_occurrences = 0;
  if (state.exception() == -1) {
    maximum_saved_occurrences =
        std::min(additions, (final_size + 1) / 2 - 1);
  } else {
    const int maximum_final_multiplicity =
        std::min({(final_size + 1) / 2, exception_rep_cap,
                  state.exception_multiplicity() + additions});
    maximum_saved_occurrences =
        std::max(0, maximum_final_multiplicity -
                        state.exception_multiplicity());
  }

  const long long fresh_sums_needed =
      new_pair_occurrences - maximum_saved_occurrences;
  const long long free_sum_values =
      (2LL * final_max - 1) - state.occupied_count();
  return fresh_sums_needed <= free_sum_values;
}

// Rigorous absolute cardinality bound for extensions using candidates[0,end).
// Besides the sum-slot bound, once an exception e is known, each half-line
// split at e/2 is an ordinary Sidon set.
int extension_upper_bound(const State& state,
                          const std::vector<int>& candidates, int end,
                          int coloring_addition_cap) {
  const int current_size = state.size();
  int upper = current_size + std::min(end, coloring_addition_cap);
  if (upper <= current_size) {
    return current_size;
  }

  int final_max = state.maximum();
  for (int i = 0; i < end; ++i) {
    final_max =
        std::max(final_max, candidates[static_cast<std::size_t>(i)]);
  }

  int exception_rep_cap = 0;
  if (state.exception() != -1) {
    exception_rep_cap =
        maximum_possible_exception_representations(state, candidates, end);

    const int split = state.exception() / 2;
    int low_count = 0;
    int high_count = 0;
    int low_min = state.n() + 1;
    int low_max = 0;
    int high_min = state.n() + 1;
    int high_max = 0;
    auto include_in_side_data = [&](int x) {
      if (x <= split) {
        ++low_count;
        low_min = std::min(low_min, x);
        low_max = std::max(low_max, x);
      } else {
        ++high_count;
        high_min = std::min(high_min, x);
        high_max = std::max(high_max, x);
      }
    };
    for (int x : state.chosen()) {
      include_in_side_data(x);
    }
    for (int i = 0; i < end; ++i) {
      include_in_side_data(candidates[static_cast<std::size_t>(i)]);
    }
    const int low_cap =
        low_count == 0
            ? 0
            : std::min(low_count,
                       sidon_difference_cap(low_max - low_min + 1));
    const int high_cap =
        high_count == 0
            ? 0
            : std::min(high_count,
                       sidon_difference_cap(high_max - high_min + 1));
    upper = std::min(upper, low_cap + high_cap);
  }

  while (upper > current_size &&
         !sum_capacity_allows(state, upper, final_max, exception_rep_cap)) {
    --upper;
  }
  return upper;
}

struct Coloring {
  std::vector<int> order;
  std::vector<int> original_index;
  std::vector<int> color_bound;
  std::vector<std::vector<std::uint64_t>> adjacency;
};

bool adjacent(const std::vector<std::vector<std::uint64_t>>& adjacency,
              int u, int v) {
  return (adjacency[static_cast<std::size_t>(u)]
                   [static_cast<std::size_t>(v / 64)] &
          (std::uint64_t{1} << (v % 64))) != 0;
}

void set_adjacent(std::vector<std::vector<std::uint64_t>>& adjacency, int u,
                  int v) {
  adjacency[static_cast<std::size_t>(u)][static_cast<std::size_t>(v / 64)] |=
      std::uint64_t{1} << (v % 64);
  adjacency[static_cast<std::size_t>(v)][static_cast<std::size_t>(u / 64)] |=
      std::uint64_t{1} << (u % 64);
}

Coloring build_coloring(State& state, const std::vector<int>& candidates) {
  const int p = static_cast<int>(candidates.size());
  const int words = (p + 63) / 64;
  Coloring result;
  result.adjacency.assign(
      static_cast<std::size_t>(p),
      std::vector<std::uint64_t>(static_cast<std::size_t>(words), 0));

  for (int i = 0; i < p; ++i) {
    State::Undo undo;
    if (!state.add(candidates[static_cast<std::size_t>(i)], undo)) {
      throw std::logic_error("coloring received infeasible candidate");
    }
    for (int j = i + 1; j < p; ++j) {
      if (state.can_add(candidates[static_cast<std::size_t>(j)])) {
        set_adjacent(result.adjacency, i, j);
      }
    }
    state.undo(candidates[static_cast<std::size_t>(i)], undo);
  }

  std::vector<int> scan_order(static_cast<std::size_t>(p));
  std::iota(scan_order.begin(), scan_order.end(), 0);
  std::vector<int> degree(static_cast<std::size_t>(p), 0);
  for (int i = 0; i < p; ++i) {
    int d = 0;
    for (std::uint64_t word : result.adjacency[static_cast<std::size_t>(i)]) {
      d += static_cast<int>(std::popcount(word));
    }
    degree[static_cast<std::size_t>(i)] = d;
  }
  std::sort(scan_order.begin(), scan_order.end(), [&](int lhs, int rhs) {
    if (degree[static_cast<std::size_t>(lhs)] !=
        degree[static_cast<std::size_t>(rhs)]) {
      return degree[static_cast<std::size_t>(lhs)] >
             degree[static_cast<std::size_t>(rhs)];
    }
    return candidates[static_cast<std::size_t>(lhs)] <
           candidates[static_cast<std::size_t>(rhs)];
  });

  std::vector<unsigned char> remaining(static_cast<std::size_t>(p), 1);
  int left = p;
  int color = 0;
  while (left != 0) {
    ++color;
    std::vector<std::uint64_t> color_class(
        static_cast<std::size_t>(words), 0);
    for (int v : scan_order) {
      if (remaining[static_cast<std::size_t>(v)] == 0) {
        continue;
      }
      bool has_same_color_neighbor = false;
      for (int w = 0; w < words; ++w) {
        if ((result.adjacency[static_cast<std::size_t>(v)]
                             [static_cast<std::size_t>(w)] &
             color_class[static_cast<std::size_t>(w)]) != 0) {
          has_same_color_neighbor = true;
          break;
        }
      }
      if (has_same_color_neighbor) {
        continue;
      }
      remaining[static_cast<std::size_t>(v)] = 0;
      --left;
      color_class[static_cast<std::size_t>(v / 64)] |=
          std::uint64_t{1} << (v % 64);
      result.order.push_back(candidates[static_cast<std::size_t>(v)]);
      result.original_index.push_back(v);
      result.color_bound.push_back(color);
    }
  }
  return result;
}

class SearchWorker {
 public:
  explicit SearchWorker(Shared& shared) : shared_(shared) {}

  void search(State& state, const std::vector<int>& raw_candidates) {
    ++local_nodes_;
    if ((local_nodes_ & 2047U) == 0U) {
      if (shared_.stop.load(std::memory_order_relaxed) ||
          shared_.deadline_reached()) {
        return;
      }
    } else if (shared_.stop.load(std::memory_order_relaxed)) {
      return;
    }

    const int best = shared_.best_size.load(std::memory_order_relaxed);
    std::vector<int> candidates;
    candidates.reserve(raw_candidates.size());
    for (int x : raw_candidates) {
      if (state.can_add(x)) {
        candidates.push_back(x);
      }
    }
    if (state.size() + static_cast<int>(candidates.size()) <= best) {
      return;
    }
    if (extension_upper_bound(state, candidates,
                              static_cast<int>(candidates.size()),
                              static_cast<int>(candidates.size())) <= best) {
      return;
    }

    Coloring coloring = build_coloring(state, candidates);
    for (int i = static_cast<int>(coloring.order.size()) - 1; i >= 0; --i) {
      if (shared_.stop.load(std::memory_order_relaxed)) {
        return;
      }
      const int live_best =
          shared_.best_size.load(std::memory_order_relaxed);
      if (state.size() + coloring.color_bound[static_cast<std::size_t>(i)] <=
          live_best) {
        return;
      }
      if (extension_upper_bound(
              state, coloring.order, i + 1,
              coloring.color_bound[static_cast<std::size_t>(i)]) <= live_best) {
        return;
      }

      const int v = coloring.order[static_cast<std::size_t>(i)];
      const int original_v =
          coloring.original_index[static_cast<std::size_t>(i)];
      std::vector<int> child_candidates;
      child_candidates.reserve(static_cast<std::size_t>(i));
      for (int j = 0; j < i; ++j) {
        const int original_j =
            coloring.original_index[static_cast<std::size_t>(j)];
        if (adjacent(coloring.adjacency, original_v, original_j)) {
          child_candidates.push_back(
              coloring.order[static_cast<std::size_t>(j)]);
        }
      }

      State::Undo undo;
      if (!state.add(v, undo)) {
        shared_.fail("candidate-became-infeasible-without-state-change");
        return;
      }
      shared_.publish(state.chosen());
      if (state.size() + static_cast<int>(child_candidates.size()) >
          shared_.best_size.load(std::memory_order_relaxed)) {
        search(state, child_candidates);
      }
      state.undo(v, undo);
    }
  }

  std::uint64_t take_nodes() {
    const std::uint64_t result = local_nodes_;
    local_nodes_ = 0;
    return result;
  }

 private:
  Shared& shared_;
  std::uint64_t local_nodes_ = 0;
};

void add_or_throw(State& state, int x) {
  State::Undo undo;
  if (!state.add(x, undo)) {
    throw std::logic_error("failed to initialize an admissible state");
  }
}

void run_heuristics(Shared& shared, const Options& options) {
  State singleton(options.n);
  add_or_throw(singleton, 1);
  shared.publish(singleton.chosen());
  if (options.n == 1 || options.heuristic_restarts == 0) {
    return;
  }

  std::mt19937_64 rng(options.seed);
  std::vector<int> all_values;
  for (int x = 2; x <= options.n; ++x) {
    all_values.push_back(x);
  }

  // Deterministic increasing greedy first.
  {
    State state(options.n);
    add_or_throw(state, 1);
    for (int x : all_values) {
      State::Undo undo;
      if (state.add(x, undo)) {
        shared.publish(state.chosen());
      }
    }
  }

  for (int restart = 0; restart < options.heuristic_restarts; ++restart) {
    if ((restart & 255) == 0 && shared.deadline_reached()) {
      return;
    }
    State state(options.n);
    add_or_throw(state, 1);

    if ((restart & 1) == 0) {
      // Reflected-pair construction is only a lower-bound heuristic.  Exact
      // search below does not assume this structure.
      const int center_low = std::max(3, options.n - 8);
      const int center_count = options.n + 2 - center_low;
      const int center = center_low + (restart / 2) % center_count;
      const int mate_of_one = center - 1;
      if (mate_of_one >= 2 && mate_of_one <= options.n) {
        State::Undo undo;
        if (!state.add(mate_of_one, undo)) {
          throw std::logic_error("two-element set rejected");
        }
      }

      std::vector<std::pair<int, int>> pairs;
      for (int x = std::max(2, center - options.n); x < center - x; ++x) {
        const int y = center - x;
        if (y > options.n || y == mate_of_one) {
          continue;
        }
        pairs.emplace_back(x, y);
      }
      std::shuffle(pairs.begin(), pairs.end(), rng);
      for (const auto [x, y] : pairs) {
        State::Undo first;
        if (!state.add(x, first)) {
          continue;
        }
        State::Undo second;
        if (!state.add(y, second)) {
          state.undo(x, first);
        }
      }

      std::vector<unsigned char> selected(
          static_cast<std::size_t>(options.n + 1), 0);
      for (int x : state.chosen()) {
        selected[static_cast<std::size_t>(x)] = 1;
      }
      std::vector<int> leftovers;
      for (int x = 2; x <= options.n; ++x) {
        if (selected[static_cast<std::size_t>(x)] == 0) {
          leftovers.push_back(x);
        }
      }
      std::shuffle(leftovers.begin(), leftovers.end(), rng);
      for (int x : leftovers) {
        State::Undo undo;
        state.add(x, undo);
      }
    } else {
      std::shuffle(all_values.begin(), all_values.end(), rng);
      for (int x : all_values) {
        State::Undo undo;
        state.add(x, undo);
      }
    }
    shared.publish(state.chosen());
  }
}

void print_usage(std::ostream& out) {
  out << "Usage: solve_bnb --n N [--timeout SECONDS] [--threads T] "
         "[--seed S] [--heuristic-restarts R]\n"
         "  stdout is newline-delimited JSON; diagnostics/help use stderr.\n"
         "  timeout 0 means no deadline.  Exit: 0 proof-complete, 2 timeout, "
         "3 internal error.\n";
}

template <typename T>
T parse_number(const std::string& text, const std::string& option) {
  std::istringstream in(text);
  T value{};
  char extra = 0;
  if (!(in >> value) || (in >> extra)) {
    throw std::invalid_argument("invalid value for " + option + ": " + text);
  }
  return value;
}

Options parse_options(int argc, char** argv) {
  Options options;
  const unsigned hardware = std::thread::hardware_concurrency();
  options.threads = std::max(1U, std::min(64U, hardware == 0 ? 1U : hardware));

  for (int i = 1; i < argc; ++i) {
    const std::string arg = argv[i];
    auto require_value = [&](const std::string& name) -> std::string {
      if (++i >= argc) {
        throw std::invalid_argument("missing value for " + name);
      }
      return argv[i];
    };
    if (arg == "--n") {
      options.n = parse_number<int>(require_value(arg), arg);
    } else if (arg == "--timeout") {
      options.timeout_seconds =
          parse_number<double>(require_value(arg), arg);
    } else if (arg == "--threads") {
      options.threads = parse_number<unsigned>(require_value(arg), arg);
    } else if (arg == "--seed") {
      options.seed =
          parse_number<std::uint64_t>(require_value(arg), arg);
    } else if (arg == "--heuristic-restarts") {
      options.heuristic_restarts =
          parse_number<int>(require_value(arg), arg);
    } else if (arg == "--help" || arg == "-h") {
      print_usage(std::cerr);
      std::exit(0);
    } else if (!arg.empty() && arg[0] != '-' && options.n == -1) {
      options.n = parse_number<int>(arg, "N");
    } else {
      throw std::invalid_argument("unknown argument: " + arg);
    }
  }

  if (options.n < 1 || options.n > 10000) {
    throw std::invalid_argument("N must be in [1,10000]");
  }
  if (!(options.timeout_seconds >= 0.0) ||
      !std::isfinite(options.timeout_seconds)) {
    throw std::invalid_argument("timeout must be finite and nonnegative");
  }
  if (options.threads < 1 || options.threads > 64) {
    throw std::invalid_argument("threads must be in [1,64]");
  }
  if (options.heuristic_restarts < 0) {
    throw std::invalid_argument("heuristic-restarts must be nonnegative");
  }
  return options;
}

int run(const Options& options) {
  Shared shared(options.n);
  if (options.timeout_seconds > 0.0) {
    shared.deadline =
        shared.start + std::chrono::duration_cast<Clock::duration>(
                           std::chrono::duration<double>(options.timeout_seconds));
  }

  run_heuristics(shared, options);

  if (!shared.stop.load(std::memory_order_relaxed) && options.n >= 2) {
    std::vector<int> second_elements;
    for (int second = 2; second <= options.n; ++second) {
      second_elements.push_back(second);
    }
    std::atomic<std::size_t> next_task{0};
    const unsigned worker_count =
        std::min<unsigned>(options.threads,
                           static_cast<unsigned>(second_elements.size()));
    std::vector<std::thread> workers;
    workers.reserve(worker_count);
    for (unsigned worker_id = 0; worker_id < worker_count; ++worker_id) {
      workers.emplace_back([&]() {
        SearchWorker worker(shared);
        try {
          while (!shared.stop.load(std::memory_order_relaxed)) {
            const std::size_t task =
                next_task.fetch_add(1, std::memory_order_relaxed);
            if (task >= second_elements.size()) {
              break;
            }
            if (shared.deadline_reached()) {
              break;
            }
            const int second = second_elements[task];
            if (2 + (options.n - second) <=
                shared.best_size.load(std::memory_order_relaxed)) {
              continue;
            }
            State state(options.n);
            add_or_throw(state, 1);
            add_or_throw(state, second);
            shared.publish(state.chosen());
            std::vector<int> candidates;
            for (int x = second + 1; x <= options.n; ++x) {
              candidates.push_back(x);
            }
            worker.search(state, candidates);
          }
        } catch (const std::exception &error) {
          shared.fail(std::string("worker-exception:") + error.what());
        } catch (...) {
          shared.fail("worker-exception:unknown");
        }
        shared.nodes.fetch_add(worker.take_nodes(), std::memory_order_relaxed);
      });
    }
    for (std::thread& worker : workers) {
      worker.join();
    }
  }

  if (!shared.stop.load(std::memory_order_relaxed)) {
    shared.deadline_reached();
  }

  std::vector<int> final_set;
  std::string error_message;
  {
    std::lock_guard<std::mutex> lock(shared.mutex);
    final_set = shared.best_set;
    error_message = shared.error_message;
  }
  const CheckResult checked = check_admissible(final_set, options.n);
  if (!checked.admissible) {
    shared.fail("final-candidate-failed-independent-check:" + checked.error);
    error_message = "final-candidate-failed-independent-check:" + checked.error;
  }

  const bool internal_error =
      shared.internal_error.load(std::memory_order_relaxed);
  const bool timeout = shared.timed_out.load(std::memory_order_relaxed);
  const bool complete = !internal_error && !timeout;
  const int lower_bound = static_cast<int>(final_set.size());
  const int upper_bound =
      complete ? lower_bound : universal_upper_bound(options.n);

  std::lock_guard<std::mutex> lock(shared.mutex);
  std::cout << "{\"type\":\"result\",\"n\":" << options.n
            << ",\"status\":\""
            << (internal_error ? "internal-error"
                               : (timeout ? "timeout" : "proof-complete"))
            << "\",\"lower_bound\":" << lower_bound
            << ",\"upper_bound\":" << upper_bound << ",\"maximum\":";
  if (complete) {
    std::cout << lower_bound;
  } else {
    std::cout << "null";
  }
  std::cout << ",\"set\":" << json_array(final_set)
            << ",\"exceptional_sum\":";
  if (checked.exceptional_sum == -1) {
    std::cout << "null";
  } else {
    std::cout << checked.exceptional_sum;
  }
  std::cout << ",\"exceptional_multiplicity\":"
            << checked.exceptional_multiplicity
            << ",\"verified\":" << (checked.admissible ? "true" : "false")
            << ",\"nodes\":" << shared.nodes.load(std::memory_order_relaxed)
            << ",\"threads\":" << options.threads
            << ",\"elapsed_seconds\":" << std::fixed << std::setprecision(6)
            << shared.elapsed_seconds();
  if (internal_error) {
    std::cout << ",\"error\":\"" << error_message << '"';
  }
  std::cout << "}\n";
  std::cout.flush();

  if (internal_error) {
    return 3;
  }
  return timeout ? 2 : 0;
}

}  // namespace

int main(int argc, char** argv) {
  try {
    return run(parse_options(argc, argv));
  } catch (const std::exception& error) {
    std::cerr << "solve_bnb: " << error.what() << '\n';
    print_usage(std::cerr);
    return 1;
  }
}
