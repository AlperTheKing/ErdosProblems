// Random local-target search for the #944 domination/synchronisation lemma.
//
// We fix one deleted vertex v and a 3-colouring of H=G-v.  The model enforces
// the local target-level constraints visible from v:
//   * H is tripartite with colour classes A,B,C.
//   * two terminals in each colour class are neighbours of v.
//   * terminals have degree 5 in H, nonterminals degree 6 in H
//     (so G would be 6-regular at these vertices after adding v).
//   * all six terminal list assignments L_x are globally one-deletion critical.
//   * no same-colour comparable open-neighbourhood pair in G=H+v.
//
// It then looks for a high-multiplicity support-critical mate Kempe component:
//   * type (1,1) with e_H(K,third) >= 5, support-critical for both opposite
//     terminal assignments;
//   * type (2,2) with e_H(K,third) >= 3, support-critical for all four
//     terminal assignments.
//
// Such a hit would refute the proposed local domination lemma.  Absence of a
// hit is only T0 evidence.
#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <functional>
#include <iostream>
#include <mutex>
#include <numeric>
#include <queue>
#include <random>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

using namespace std;

static constexpr int MAXN = 24;
static constexpr uint8_t ALL = 0b111;

struct Model {
  int m = 0;
  int n = 0;
  uint32_t adj[MAXN]{};
  int colour[MAXN]{};
  int terminal[6]{};
};

static int cls_start(int c, int m) { return c * m; }
static int cls_end(int c, int m) { return (c + 1) * m; }
static int first_terminal(int c, int m) { return c * m; }
static int second_terminal(int c, int m) { return c * m + 1; }
static int other_terminal(int v, int m) {
  int c = v / m;
  int a = first_terminal(c, m), b = second_terminal(c, m);
  return v == a ? b : a;
}
static bool is_terminal_vertex(int v, int m) { return (v % m) < 2; }

static int pop(uint32_t x) { return __builtin_popcount(x); }

static bool has_edge(const Model& g, int u, int v) {
  return (g.adj[u] >> v) & 1u;
}

static void add_edge(Model& g, int u, int v) {
  g.adj[u] |= 1u << v;
  g.adj[v] |= 1u << u;
}

static void remove_edge(Model& g, int u, int v) {
  g.adj[u] &= ~(1u << v);
  g.adj[v] &= ~(1u << u);
}

static bool build_random_model(int m, mt19937_64& rng, Model& g) {
  g = Model{};
  g.m = m;
  g.n = 3 * m;
  for (int c = 0; c < 3; ++c) {
    for (int v = cls_start(c, m); v < cls_end(c, m); ++v) g.colour[v] = c;
    g.terminal[2 * c] = first_terminal(c, m);
    g.terminal[2 * c + 1] = second_terminal(c, m);
  }

  // Start from complete tripartite graph.
  for (int u = 0; u < g.n; ++u) {
    for (int v = u + 1; v < g.n; ++v) {
      if (g.colour[u] != g.colour[v]) add_edge(g, u, v);
    }
  }

  // Remove edges to reach H-degrees: terminals 5, nonterminals 6.
  vector<int> deficit(g.n);
  for (int v = 0; v < g.n; ++v) {
    int target = is_terminal_vertex(v, m) ? 5 : 6;
    deficit[v] = 2 * m - target;
    if (deficit[v] < 0) return false;
  }

  vector<pair<int, int>> candidates;
  candidates.reserve(3 * m * m);
  for (int u = 0; u < g.n; ++u) {
    for (int v = u + 1; v < g.n; ++v) {
      if (g.colour[u] != g.colour[v]) candidates.emplace_back(u, v);
    }
  }

  for (int attempt = 0; attempt < 2000; ++attempt) {
    Model h = g;
    vector<int> d = deficit;
    int remaining = accumulate(d.begin(), d.end(), 0);
    bool ok = true;
    while (remaining > 0) {
      vector<int> positive;
      for (int i = 0; i < h.n; ++i) {
        if (d[i] > 0) positive.push_back(i);
      }
      if (positive.empty()) break;
      int max_def = 0;
      for (int v : positive) max_def = max(max_def, d[v]);
      vector<int> max_positive;
      for (int v : positive) {
        if (d[v] == max_def) max_positive.push_back(v);
      }
      int u = max_positive[uniform_int_distribution<int>(
          0, (int)max_positive.size() - 1)(rng)];
      vector<int> nbrs;
      for (int v = 0; v < h.n; ++v) {
        if (u == v || h.colour[u] == h.colour[v]) continue;
        if (d[v] <= 0 || !has_edge(h, u, v)) continue;
        nbrs.push_back(v);
      }
      if (nbrs.empty()) {
        ok = false;
        break;
      }
      shuffle(nbrs.begin(), nbrs.end(), rng);
      int v = nbrs.front();
      remove_edge(h, u, v);
      --d[u];
      --d[v];
      remaining -= 2;
    }
    if (!ok) continue;
    if (all_of(d.begin(), d.end(), [](int x) { return x == 0; })) {
      g = h;
      return true;
    }
  }
  return false;
}

static bool colourable_with_lists(const Model& g, uint32_t mask,
                                  const vector<uint8_t>& lists) {
  vector<int> verts;
  for (int v = 0; v < g.n; ++v) {
    if ((mask >> v) & 1u) verts.push_back(v);
  }
  sort(verts.begin(), verts.end(), [&](int a, int b) {
    int la = pop(lists[a]), lb = pop(lists[b]);
    if (la != lb) return la < lb;
    int da = pop(g.adj[a] & mask), db = pop(g.adj[b] & mask);
    if (da != db) return da > db;
    return a < b;
  });
  int colour[MAXN];
  fill(begin(colour), end(colour), -1);
  function<bool(int)> dfs = [&](int pos) -> bool {
    if (pos == (int)verts.size()) return true;
    int v = verts[pos];
    uint8_t avail = lists[v];
    uint32_t nb = g.adj[v] & mask;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if (colour[u] >= 0) avail &= (uint8_t)~(1u << colour[u]);
    }
    for (int c = 0; c < 3; ++c) {
      if (((avail >> c) & 1u) == 0) continue;
      colour[v] = c;
      if (dfs(pos + 1)) return true;
      colour[v] = -1;
    }
    return false;
  };
  return dfs(0);
}

static vector<uint8_t> terminal_lists(const Model& g, int free_terminal) {
  vector<uint8_t> lists(g.n, ALL);
  int forbidden = g.colour[free_terminal];
  for (int t : g.terminal) {
    if (t == free_terminal) continue;
    lists[t] &= (uint8_t)~(1u << forbidden);
  }
  return lists;
}

static bool terminal_list_critical(const Model& g, int free_terminal) {
  uint32_t full = (g.n == 32) ? ~0u : ((1u << g.n) - 1u);
  auto lists = terminal_lists(g, free_terminal);
  if (colourable_with_lists(g, full, lists)) return false;
  for (int y = 0; y < g.n; ++y) {
    if (!colourable_with_lists(g, full & ~(1u << y), lists)) return false;
  }
  return true;
}

static bool all_six_terminal_critical(const Model& g) {
  for (int t : g.terminal) {
    if (!terminal_list_critical(g, t)) return false;
  }
  return true;
}

static bool no_comparable_same_colour_pair_in_G(const Model& g) {
  uint32_t vbit = 1u << g.n;  // virtual deleted vertex v, only for comparison.
  uint32_t gnb[MAXN];
  for (int x = 0; x < g.n; ++x) {
    gnb[x] = g.adj[x];
    if (is_terminal_vertex(x, g.m)) gnb[x] |= vbit;
  }
  for (int x = 0; x < g.n; ++x) {
    for (int y = x + 1; y < g.n; ++y) {
      if (g.colour[x] != g.colour[y]) continue;
      if ((gnb[x] & ~gnb[y]) == 0) return false;
      if ((gnb[y] & ~gnb[x]) == 0) return false;
    }
  }
  return true;
}

static uint32_t kempe_component(const Model& g, int start, int c1, int c2) {
  uint32_t comp = 0;
  queue<int> q;
  comp |= 1u << start;
  q.push(start);
  while (!q.empty()) {
    int v = q.front();
    q.pop();
    uint32_t nb = g.adj[v];
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if ((comp >> u) & 1u) continue;
      if (g.colour[u] != c1 && g.colour[u] != c2) continue;
      comp |= 1u << u;
      q.push(u);
    }
  }
  return comp;
}

static int boundary_to_colour(const Model& g, uint32_t comp, int third) {
  int count = 0;
  for (int v = 0; v < g.n; ++v) {
    if (((comp >> v) & 1u) == 0) continue;
    uint32_t nb = g.adj[v] & ~comp;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if (g.colour[u] == third) ++count;
    }
  }
  return count;
}

static uint32_t third_support(const Model& g, uint32_t comp, int third) {
  uint32_t support = 0;
  for (int v = 0; v < g.n; ++v) {
    if (((comp >> v) & 1u) == 0) continue;
    uint32_t nb = g.adj[v] & ~comp;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if (g.colour[u] == third) support |= 1u << v;
    }
  }
  return support;
}

static bool support_critical(const Model& g, uint32_t comp, int free_terminal,
                             int third) {
  auto lists = terminal_lists(g, free_terminal);
  uint32_t support = third_support(g, comp, third);
  for (int v = 0; v < g.n; ++v) {
    if ((support >> v) & 1u) lists[v] &= (uint8_t)~(1u << third);
  }
  return !colourable_with_lists(g, comp, lists);
}

static int terminal_count_in_comp(const Model& g, uint32_t comp, int colour) {
  int count = 0;
  for (int k = 0; k < 2; ++k) {
    int t = colour * g.m + k;
    if ((comp >> t) & 1u) ++count;
  }
  return count;
}

static string model_edges(const Model& g) {
  ostringstream out;
  out << "m=" << g.m << " n=" << g.n << "\n";
  for (int u = 0; u < g.n; ++u) {
    for (int v = u + 1; v < g.n; ++v) {
      if (has_edge(g, u, v)) out << u << " " << v << "\n";
    }
  }
  return out.str();
}

static bool has_high_support_critical_component(const Model& g, string& why) {
  for (int c1 = 0; c1 < 3; ++c1) {
    for (int c2 = c1 + 1; c2 < 3; ++c2) {
      int third = 3 - c1 - c2;
      uint32_t seen = 0;
      for (int start = 0; start < g.n; ++start) {
        if (g.colour[start] != c1 && g.colour[start] != c2) continue;
        if ((seen >> start) & 1u) continue;
        uint32_t comp = kempe_component(g, start, c1, c2);
        seen |= comp;
        int tc1 = terminal_count_in_comp(g, comp, c1);
        int tc2 = terminal_count_in_comp(g, comp, c2);
        int e3 = boundary_to_colour(g, comp, third);
        if (tc1 == 1 && tc2 == 1 && e3 >= 5) {
          int contained1 = -1, contained2 = -1;
          for (int k = 0; k < 2; ++k) {
            int t1 = c1 * g.m + k, t2 = c2 * g.m + k;
            if ((comp >> t1) & 1u) contained1 = t1;
            if ((comp >> t2) & 1u) contained2 = t2;
          }
          int free1 = other_terminal(contained1, g.m);
          int free2 = other_terminal(contained2, g.m);
          if (support_critical(g, comp, free1, third) &&
              support_critical(g, comp, free2, third)) {
            why = "type(1,1) pair=" + to_string(c1) + to_string(c2) +
                  " e3=" + to_string(e3);
            return true;
          }
        }
        if (tc1 == 2 && tc2 == 2 && e3 >= 3) {
          bool ok = true;
          for (int k = 0; k < 2; ++k) {
            ok = ok && support_critical(g, comp, c1 * g.m + k, third);
            ok = ok && support_critical(g, comp, c2 * g.m + k, third);
          }
          if (ok) {
            why = "type(2,2) pair=" + to_string(c1) + to_string(c2) +
                  " e3=" + to_string(e3);
            return true;
          }
        }
      }
    }
  }
  return false;
}

int main(int argc, char** argv) {
  int m = 4;
  int seconds = 120;
  int threads = 96;
  if (argc > 1) m = stoi(argv[1]);
  if (argc > 2) seconds = stoi(argv[2]);
  if (argc > 3) threads = stoi(argv[3]);
  threads = max(1, threads);

  atomic<uint64_t> generated{0}, degree_ok{0}, allcrit{0}, nocomp{0}, hits{0};
  atomic<bool> stop{false};
  mutex hit_mu;
  string hit_text;
  auto deadline = chrono::steady_clock::now() + chrono::seconds(seconds);

  auto worker = [&](int tid) {
    mt19937_64 rng(0x944D0AULL + tid * 0x9e3779b97f4a7c15ULL +
                   chrono::high_resolution_clock::now().time_since_epoch().count());
    while (!stop.load(memory_order_relaxed)) {
      if (chrono::steady_clock::now() >= deadline) {
        stop.store(true);
        break;
      }
      Model g;
      if (!build_random_model(m, rng, g)) continue;
      ++generated;
      ++degree_ok;
      if (!all_six_terminal_critical(g)) continue;
      ++allcrit;
      if (!no_comparable_same_colour_pair_in_G(g)) continue;
      ++nocomp;
      string why;
      if (has_high_support_critical_component(g, why)) {
        ++hits;
        lock_guard<mutex> lock(hit_mu);
        if (hit_text.empty()) {
          hit_text = "HIT " + why + "\n" + model_edges(g);
          stop.store(true);
        }
      }
    }
  };

  vector<thread> pool;
  for (int t = 0; t < threads; ++t) pool.emplace_back(worker, t);

  auto start = chrono::steady_clock::now();
  while (!stop.load(memory_order_relaxed)) {
    this_thread::sleep_for(chrono::seconds(5));
    auto now = chrono::steady_clock::now();
    double elapsed = chrono::duration<double>(now - start).count();
    cerr << "progress elapsed=" << elapsed
         << " generated=" << generated.load()
         << " allSixCritical=" << allcrit.load()
         << " noComparable=" << nocomp.load()
         << " hits=" << hits.load() << "\n";
    if (now >= deadline) stop.store(true);
  }

  for (auto& th : pool) th.join();
  cout << "SUMMARY m=" << m << " seconds=" << seconds << " threads=" << threads
       << " generated=" << generated.load()
       << " allSixCritical=" << allcrit.load()
       << " noComparable=" << nocomp.load()
       << " hits=" << hits.load() << "\n";
  if (!hit_text.empty()) cout << hit_text;
  return hit_text.empty() ? 0 : 2;
}
