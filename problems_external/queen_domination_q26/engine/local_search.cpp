#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <mutex>
#include <random>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace {

enum class Strategy { Sampled, TargetMinConflicts };

struct Options {
  int n = 26;
  int k = 13;
  int threads = 1;
  int seconds = 60;
  int samples = 48;
  std::uint64_t seed = 1;
  bool balanced_parity = false;
  bool audit_deltas = false;
  Strategy strategy = Strategy::Sampled;
};

const char* strategy_name(Strategy strategy) {
  return strategy == Strategy::Sampled ? "sampled" : "target-minconflicts";
}


struct Board {
  int n;
  int n2;
  std::vector<std::vector<int>> cover;
  std::vector<std::uint8_t> cover_mask;

  explicit Board(int side) : n(side), n2(side * side), cover(n2),
                             cover_mask(static_cast<std::size_t>(n2) * n2, 0) {
    for (int q = 0; q < n2; ++q) {
      const int qr = q / n;
      const int qc = q % n;
      for (int s = 0; s < n2; ++s) {
        const int sr = s / n;
        const int sc = s % n;
        if (qr == sr || qc == sc || qr - qc == sr - sc || qr + qc == sr + sc) {
          cover[q].push_back(s);
          cover_mask[static_cast<std::size_t>(q) * n2 + s] = 1;
        }
      }
    }
  }

  bool covers(int q, int s) const {
    return cover_mask[static_cast<std::size_t>(q) * n2 + s] != 0;
  }
};

int square_parity(const Board& board, int q) {
  return (q / board.n + q % board.n) & 1;
}

int parity_zero_count(const Board& board, const std::vector<int>& selected) {
  return static_cast<int>(std::count_if(
      selected.begin(), selected.end(),
      [&](int q) { return square_parity(board, q) == 0; }));
}

bool has_balanced_parity(const Board& board, const std::vector<int>& selected) {
  const int zero = parity_zero_count(board, selected);
  return std::abs(2 * zero - static_cast<int>(selected.size())) <= 1;
}

struct State {
  std::vector<int> selected;
  std::vector<std::uint8_t> in_set;
  std::vector<std::uint8_t> count;
  std::vector<int> weight;
  int uncovered = 0;
  long long weighted = 0;
};

struct Shared {
  std::atomic<bool> found{false};
  std::atomic<int> best_uncovered{std::numeric_limits<int>::max()};
  std::atomic<std::uint64_t> iterations{0};
  std::mutex best_mutex;
  std::vector<int> best_selected;
  int winning_worker = -1;
  double winning_seconds = 0.0;
};

Options parse_options(int argc, char** argv) {
  Options o;
  const unsigned hw = std::thread::hardware_concurrency();
  o.threads = std::max(1u, std::min(64u, hw == 0 ? 1u : hw));
  for (int i = 1; i < argc; ++i) {
    const std::string arg = argv[i];
    auto need = [&](const char* name) -> std::string {
      if (++i >= argc) {
        std::cerr << "missing value for " << name << "\n";
        std::exit(64);
      }
      return argv[i];
    };
    if (arg == "--n") o.n = std::stoi(need("--n"));
    else if (arg == "--k") o.k = std::stoi(need("--k"));
    else if (arg == "--threads") o.threads = std::stoi(need("--threads"));
    else if (arg == "--seconds") o.seconds = std::stoi(need("--seconds"));
    else if (arg == "--samples") o.samples = std::stoi(need("--samples"));
    else if (arg == "--seed") o.seed = std::stoull(need("--seed"));
    else if (arg == "--balanced-parity") o.balanced_parity = true;
    else if (arg == "--audit-deltas") o.audit_deltas = true;
    else if (arg == "--strategy") {
      const std::string value = need("--strategy");
      if (value == "sampled") o.strategy = Strategy::Sampled;
      else if (value == "target-minconflicts") {
        o.strategy = Strategy::TargetMinConflicts;
      } else {
        std::cerr << "unknown strategy: " << value << "\n";
        std::exit(64);
      }
    }
    else if (arg == "--help") {
      std::cout << "local_search --n N --k K --threads T --seconds S --samples M --seed X "
                   "[--balanced-parity] [--audit-deltas] "
                   "[--strategy sampled|target-minconflicts]\n";
      std::exit(0);
    } else {
      std::cerr << "unknown option: " << arg << "\n";
      std::exit(64);
    }
  }
  if (o.n <= 0 || o.k <= 0 || o.k > o.n * o.n || o.threads <= 0 ||
      o.threads > 64 || o.seconds <= 0 || o.samples <= 0) {
    std::cerr << "invalid options\n";
    std::exit(64);
  }
  if (o.balanced_parity &&
      ((o.k % 2 != 0 && o.threads < 2) ||
       (o.k + 1) / 2 > (o.n * o.n) / 2)) {
    std::cerr << "balanced parity requires both orientations to fit and, for odd k, at least two threads\n";
    std::exit(64);
  }
  return o;
}

template <class Rng>
State greedy_state(const Board& board, int k, int target_parity_zero, Rng& rng) {
  State st;
  st.selected.reserve(k);
  st.in_set.assign(board.n2, 0);
  st.count.assign(board.n2, 0);
  st.weight.assign(board.n2, 1);
  int selected_parity_zero = 0;

  for (int slot = 0; slot < k; ++slot) {
    std::vector<std::pair<int, int>> ranked;
    ranked.reserve(board.n2 - slot);
    for (int q = 0; q < board.n2; ++q) {
      if (st.in_set[q]) continue;
      if (target_parity_zero >= 0) {
        const bool parity_zero = square_parity(board, q) == 0;
        const int selected_parity_one = slot - selected_parity_zero;
        if ((parity_zero && selected_parity_zero >= target_parity_zero) ||
            (!parity_zero &&
             selected_parity_one >= k - target_parity_zero)) {
          continue;
        }
      }
      int gain = 0;
      for (const int s : board.cover[q]) gain += (st.count[s] == 0);
      ranked.emplace_back(gain, q);
    }
    std::sort(ranked.begin(), ranked.end(), [](const auto& a, const auto& b) {
      if (a.first != b.first) return a.first > b.first;
      return a.second < b.second;
    });
    const int rcl = std::min<int>(slot == 0 ? 64 : 12, ranked.size());
    const int pick = static_cast<int>(rng() % static_cast<std::uint64_t>(rcl));
    const int q = ranked[pick].second;
    st.selected.push_back(q);
    st.in_set[q] = 1;
    for (const int s : board.cover[q]) ++st.count[s];
    selected_parity_zero += square_parity(board, q) == 0;
  }
  for (int s = 0; s < board.n2; ++s) {
    if (st.count[s] == 0) {
      ++st.uncovered;
      st.weighted += st.weight[s];
    }
  }
  return st;
}

bool verify(const Board& board, const std::vector<int>& selected, int k) {
  if (static_cast<int>(selected.size()) != k) return false;
  std::vector<std::uint8_t> seen(board.n2, 0);
  std::vector<std::uint8_t> covered(board.n2, 0);
  for (const int q : selected) {
    if (q < 0 || q >= board.n2 || seen[q]) return false;
    seen[q] = 1;
    for (const int s : board.cover[q]) covered[s] = 1;
  }
  return std::all_of(covered.begin(), covered.end(), [](std::uint8_t x) { return x != 0; });
}

[[noreturn]] void audit_fail(const char* message) {
  std::cerr << "delta audit failed: " << message << "\n";
  std::abort();
}

void audit_state(const Board& board, const State& st, int k,
                 int target_parity_zero) {
  if (static_cast<int>(st.selected.size()) != k) audit_fail("selected size");
  if (static_cast<int>(st.in_set.size()) != board.n2 ||
      static_cast<int>(st.count.size()) != board.n2 ||
      static_cast<int>(st.weight.size()) != board.n2) {
    audit_fail("state vector size");
  }
  std::vector<std::uint8_t> expected_in(board.n2, 0);
  std::vector<std::uint8_t> expected_count(board.n2, 0);
  for (const int q : st.selected) {
    if (q < 0 || q >= board.n2 || expected_in[q]) {
      audit_fail("selected range or duplicate");
    }
    expected_in[q] = 1;
    for (const int s : board.cover[q]) ++expected_count[s];
  }
  int expected_uncovered = 0;
  long long expected_weighted = 0;
  for (int s = 0; s < board.n2; ++s) {
    if (st.in_set[s] != expected_in[s]) audit_fail("in_set mismatch");
    if (st.count[s] != expected_count[s]) audit_fail("coverage count mismatch");
    if (st.count[s] == 0) {
      ++expected_uncovered;
      expected_weighted += st.weight[s];
    }
  }
  if (st.uncovered != expected_uncovered) audit_fail("uncovered mismatch");
  if (st.weighted != expected_weighted) audit_fail("weighted mismatch");
  if (target_parity_zero >= 0 &&
      parity_zero_count(board, st.selected) != target_parity_zero) {
    audit_fail("parity mismatch");
  }
}

void publish_best(Shared& shared, const State& st, int worker,
                  double elapsed, bool winning) {
  int prior = shared.best_uncovered.load(std::memory_order_relaxed);
  while (st.uncovered < prior &&
         !shared.best_uncovered.compare_exchange_weak(prior, st.uncovered,
                                                       std::memory_order_relaxed)) {}
  if (st.uncovered <= shared.best_uncovered.load(std::memory_order_relaxed)) {
    std::lock_guard<std::mutex> lock(shared.best_mutex);
    if (st.uncovered <= shared.best_uncovered.load(std::memory_order_relaxed)) {
      shared.best_selected = st.selected;
      if (winning) {
        shared.winning_worker = worker;
        shared.winning_seconds = elapsed;
      }
    }
  }
}

void worker_loop(const Board& board, const Options& opt, int worker,
                 const std::chrono::steady_clock::time_point deadline,
                 const std::chrono::steady_clock::time_point start,
                 Shared& shared) {
  std::seed_seq seq{static_cast<std::uint32_t>(opt.seed),
                    static_cast<std::uint32_t>(opt.seed >> 32),
                    static_cast<std::uint32_t>(worker), 0x9e3779b9u};
  std::mt19937_64 rng(seq);
  const int target_parity_zero = opt.balanced_parity
      ? opt.k / 2 + ((opt.k % 2 != 0 && worker % 2 != 0) ? 1 : 0)
      : -1;
  State st = greedy_state(board, opt.k, target_parity_zero, rng);
  if (opt.audit_deltas) audit_state(board, st, opt.k, target_parity_zero);
  publish_best(shared, st, worker, 0.0, false);
  std::uint64_t local_iterations = 0;
  std::uint64_t since_restart_best = 0;
  int restart_best = st.uncovered;

  struct Move { int old_index = -1; int add = -1; int du = 0; long long dw = 0; };
  struct Move2 {
    int old_index1 = -1;
    int old_index2 = -1;
    int add1 = -1;
    int add2 = -1;
    int du = 0;
    long long dw = 0;
  };

  while (!shared.found.load(std::memory_order_relaxed) &&
         std::chrono::steady_clock::now() < deadline) {
    if (st.uncovered == 0) {
      const double elapsed = std::chrono::duration<double>(
          std::chrono::steady_clock::now() - start).count();
      if (verify(board, st.selected, opt.k) &&
          (!opt.balanced_parity ||
           parity_zero_count(board, st.selected) == target_parity_zero)) {
        publish_best(shared, st, worker, elapsed, true);
        shared.found.store(true, std::memory_order_relaxed);
        break;
      }
    }

    int target = -1;
    if (opt.strategy == Strategy::TargetMinConflicts) {
      int best_weight = -1;
      std::uint64_t ties = 0;
      for (int s = 0; s < board.n2; ++s) {
        if (st.count[s] != 0) continue;
        if (st.weight[s] > best_weight) {
          best_weight = st.weight[s];
          target = s;
          ties = 1;
        } else if (st.weight[s] == best_weight) {
          ++ties;
          if (rng() % ties == 0) target = s;
        }
      }
    } else {
    for (int tries = 0; tries < 64; ++tries) {
      const int s = static_cast<int>(rng() % static_cast<std::uint64_t>(board.n2));
      if (st.count[s] == 0 && (target < 0 || st.weight[s] > st.weight[target])) target = s;
    }
    if (target < 0) {
      const int begin = static_cast<int>(rng() % static_cast<std::uint64_t>(board.n2));
      for (int j = 0; j < board.n2; ++j) {
        const int s = (begin + j) % board.n2;
        if (st.count[s] == 0) { target = s; break; }
      }
    }
    }

    if (opt.strategy == Strategy::Sampled && opt.k >= 2 &&
        st.uncovered <= 3 && local_iterations % 8 == 0 &&
        target >= 0) {
      Move2 best2;
      best2.dw = std::numeric_limits<long long>::max();
      best2.du = std::numeric_limits<int>::max();
      for (int sample = 0; sample < opt.samples; ++sample) {
        const int oi1 = static_cast<int>(rng() % static_cast<std::uint64_t>(opt.k));
        int oi2 = static_cast<int>(rng() % static_cast<std::uint64_t>(opt.k - 1));
        if (oi2 >= oi1) ++oi2;
        const int old1 = st.selected[oi1];
        const int old2 = st.selected[oi2];
        const auto& first_candidates = board.cover[target];
        const int add1 = first_candidates[rng() % first_candidates.size()];
        int add2 = static_cast<int>(rng() % static_cast<std::uint64_t>(board.n2));
        if (st.in_set[add1] || st.in_set[add2] || add1 == add2) continue;
        if (opt.balanced_parity &&
            square_parity(board, old1) + square_parity(board, old2) !=
                square_parity(board, add1) + square_parity(board, add2)) {
          continue;
        }

        int du = 0;
        long long dw = 0;
        for (int s = 0; s < board.n2; ++s) {
          const int after = st.count[s] - (board.covers(old1, s) ? 1 : 0)
              - (board.covers(old2, s) ? 1 : 0) + (board.covers(add1, s) ? 1 : 0)
              + (board.covers(add2, s) ? 1 : 0);
          const bool before_uncovered = st.count[s] == 0;
          const bool after_uncovered = after == 0;
          if (before_uncovered != after_uncovered) {
            const int sign = after_uncovered ? 1 : -1;
            du += sign;
            dw += static_cast<long long>(sign) * st.weight[s];
          }
        }
        if (dw < best2.dw || (dw == best2.dw && du < best2.du)) {
          best2 = Move2{oi1, oi2, add1, add2, du, dw};
        }
      }
      if (best2.old_index1 >= 0) {
        const double temperature2 = 0.8 + std::min(6.0, st.uncovered / 3.0);
        const bool accept2 = best2.dw <= 0 ||
            std::generate_canonical<double, 53>(rng) < std::exp(-best2.dw / temperature2);
        if (accept2) {
          const int old1 = st.selected[best2.old_index1];
          const int old2 = st.selected[best2.old_index2];
          for (const int s : board.cover[old1]) --st.count[s];
          for (const int s : board.cover[old2]) --st.count[s];
          st.in_set[old1] = 0;
          st.in_set[old2] = 0;
          st.selected[best2.old_index1] = best2.add1;
          st.selected[best2.old_index2] = best2.add2;
          st.in_set[best2.add1] = 1;
          st.in_set[best2.add2] = 1;
          for (const int s : board.cover[best2.add1]) ++st.count[s];
          for (const int s : board.cover[best2.add2]) ++st.count[s];
          st.uncovered += best2.du;
          st.weighted += best2.dw;
          if (opt.audit_deltas) {
            audit_state(board, st, opt.k, target_parity_zero);
          }
          if (st.uncovered == 0) {
            const double elapsed = std::chrono::duration<double>(
                std::chrono::steady_clock::now() - start).count();
            if (verify(board, st.selected, opt.k) &&
                (!opt.balanced_parity ||
                 parity_zero_count(board, st.selected) == target_parity_zero)) {
              publish_best(shared, st, worker, elapsed, true);
              shared.found.store(true, std::memory_order_relaxed);
              break;
            }
          }
        }
      }
    }

    Move best;
    best.dw = std::numeric_limits<long long>::max();
    best.du = std::numeric_limits<int>::max();
    if (opt.strategy == Strategy::TargetMinConflicts && target >= 0) {
      std::uint64_t ties = 0;
      for (int old_index = 0; old_index < opt.k; ++old_index) {
        const int old_q = st.selected[old_index];
        int loss_u = 0;
        long long loss_w = 0;
        for (const int s : board.cover[old_q]) {
          if (st.count[s] == 1) { ++loss_u; loss_w += st.weight[s]; }
        }
        for (const int add_q : board.cover[target]) {
          if (st.in_set[add_q]) continue;
          if (opt.balanced_parity &&
              square_parity(board, old_q) != square_parity(board, add_q)) {
            continue;
          }
          int gain_u = 0;
          long long gain_w = 0;
          for (const int s : board.cover[add_q]) {
            const int after_remove = st.count[s] -
                (board.covers(old_q, s) ? 1 : 0);
            if (after_remove == 0) {
              ++gain_u;
              gain_w += st.weight[s];
            }
          }
          const int du = loss_u - gain_u;
          const long long dw = loss_w - gain_w;
          if (dw < best.dw || (dw == best.dw && du < best.du)) {
            best = Move{old_index, add_q, du, dw};
            ties = 1;
          } else if (dw == best.dw && du == best.du) {
            ++ties;
            if (rng() % ties == 0) {
              best = Move{old_index, add_q, du, dw};
            }
          }
        }
      }
    } else {
      for (int sample = 0; sample < opt.samples; ++sample) {
      const int old_index = static_cast<int>(rng() % static_cast<std::uint64_t>(opt.k));
      const int old_q = st.selected[old_index];
      int add_q;
      if (target >= 0 && sample * 5 < opt.samples * 4) {
        const auto& candidates = board.cover[target];
        add_q = candidates[rng() % candidates.size()];
      } else {
        add_q = static_cast<int>(rng() % static_cast<std::uint64_t>(board.n2));
      }
      if (st.in_set[add_q]) continue;

      if (opt.balanced_parity &&
          square_parity(board, old_q) != square_parity(board, add_q)) {
        continue;
      }
      int du = 0;
      long long dw = 0;
      for (const int s : board.cover[old_q]) {
        if (st.count[s] == 1) { ++du; dw += st.weight[s]; }
      }
      for (const int s : board.cover[add_q]) {
        const int after_remove = st.count[s] - (board.covers(old_q, s) ? 1 : 0);
        if (after_remove == 0) { --du; dw -= st.weight[s]; }
      }
      if (dw < best.dw || (dw == best.dw && du < best.du)) {
        best = Move{old_index, add_q, du, dw};
      }
    }
    }

    if (best.old_index >= 0) {
      const double temperature = 0.35 + std::min(4.0, st.uncovered / 8.0);
      const bool accept = opt.strategy == Strategy::TargetMinConflicts ||
          best.dw <= 0 ||
          std::generate_canonical<double, 53>(rng) < std::exp(-best.dw / temperature);
      if (accept) {
        const int old_q = st.selected[best.old_index];
        for (const int s : board.cover[old_q]) --st.count[s];
        st.in_set[old_q] = 0;
        st.selected[best.old_index] = best.add;
        st.in_set[best.add] = 1;
        for (const int s : board.cover[best.add]) ++st.count[s];
        st.uncovered += best.du;
        st.weighted += best.dw;
        if (opt.audit_deltas) {
          audit_state(board, st, opt.k, target_parity_zero);
        }
        if (st.uncovered == 0) {
          const double elapsed = std::chrono::duration<double>(
              std::chrono::steady_clock::now() - start).count();
          if (verify(board, st.selected, opt.k) &&
              (!opt.balanced_parity ||
               parity_zero_count(board, st.selected) == target_parity_zero)) {
            publish_best(shared, st, worker, elapsed, true);
            shared.found.store(true, std::memory_order_relaxed);
            break;
          }
        }
      }
    }

    ++local_iterations;
    ++since_restart_best;
    if (st.uncovered < restart_best) {
      restart_best = st.uncovered;
      since_restart_best = 0;
      const double elapsed = std::chrono::duration<double>(
          std::chrono::steady_clock::now() - start).count();
      publish_best(shared, st, worker, elapsed, false);
    }
    if (local_iterations % 2000 == 0) {
      for (int s = 0; s < board.n2; ++s) {
        if (st.count[s] == 0) { ++st.weight[s]; ++st.weighted; }
      }
      if (opt.audit_deltas) audit_state(board, st, opt.k, target_parity_zero);
    }
    if (since_restart_best >= 200000) {
      st = greedy_state(board, opt.k, target_parity_zero, rng);
      if (opt.audit_deltas) audit_state(board, st, opt.k, target_parity_zero);
      restart_best = st.uncovered;
      since_restart_best = 0;
      publish_best(shared, st, worker, 0.0, false);
    }
  }
  shared.iterations.fetch_add(local_iterations, std::memory_order_relaxed);
}

void print_queens(const std::vector<int>& selected, int n) {
  std::vector<int> sorted = selected;
  std::sort(sorted.begin(), sorted.end());
  std::cout << "[";
  for (std::size_t i = 0; i < sorted.size(); ++i) {
    if (i) std::cout << ",";
    std::cout << "[" << sorted[i] / n << "," << sorted[i] % n << "]";
  }
  std::cout << "]";
}

}  // namespace

int main(int argc, char** argv) {
  const Options opt = parse_options(argc, argv);
  const Board board(opt.n);
  const auto start = std::chrono::steady_clock::now();
  const auto deadline = start + std::chrono::seconds(opt.seconds);
  Shared shared;
  std::vector<std::thread> workers;
  workers.reserve(opt.threads);
  for (int w = 0; w < opt.threads; ++w) {
    workers.emplace_back(worker_loop, std::cref(board), std::cref(opt), w,
                         deadline, start, std::ref(shared));
  }
  for (auto& thread : workers) thread.join();
  const double elapsed = std::chrono::duration<double>(
      std::chrono::steady_clock::now() - start).count();

  std::lock_guard<std::mutex> lock(shared.best_mutex);
  const bool sat = shared.found.load() &&
      verify(board, shared.best_selected, opt.k) &&
      (!opt.balanced_parity || has_balanced_parity(board, shared.best_selected));
  std::cout << std::fixed << std::setprecision(6)
            << "{\"n\":" << opt.n << ",\"k\":" << opt.k
            << ",\"status\":\"" << (sat ? "SAT" : "NO_HIT") << "\""
            << ",\"best_uncovered\":" << shared.best_uncovered.load()
            << ",\"threads\":" << opt.threads
            << ",\"iterations\":" << shared.iterations.load()
            << ",\"elapsed_seconds\":" << elapsed
            << ",\"seed\":" << opt.seed
            << ",\"strategy\":\"" << strategy_name(opt.strategy) << "\""
            << ",\"audit_deltas\":" << (opt.audit_deltas ? "true" : "false");
  if (opt.balanced_parity) {
    const int parity_zero = parity_zero_count(board, shared.best_selected);
    std::cout << ",\"balanced_parity\":true,\"parity_counts\":["
              << parity_zero << "," << opt.k - parity_zero << "]";
  }
  if (!shared.best_selected.empty()) {
    std::cout << ",\"coordinates\":";
    print_queens(shared.best_selected, opt.n);
  }
  if (sat) std::cout << ",\"worker\":" << shared.winning_worker;
  std::cout << "}\n";
  return sat ? 0 : 2;
}
