// Verify GPT Pro's 9-vertex support-vs-multiplicity obstruction for #944.
//
// This is not a target graph.  It checks the exact finite claims:
//   * the AB Kempe component through a' is the odd path a'-beta-alpha-b;
//   * it has terminal type (1,1) and e_H(K,C)=7 > 4;
//   * it is boundary-support-critical for L_a and L_b';
//   * H is L_a-critical and L_b'-critical under all one-vertex deletions;
//   * the model fails target-level constraints (6-regularity, comparable pair,
//     and all-six terminal criticality).
#include <array>
#include <algorithm>
#include <cstdint>
#include <functional>
#include <iostream>
#include <queue>
#include <string>
#include <vector>

using namespace std;

static constexpr int N = 9;
static constexpr uint8_t ALL = 0b111;

// Vertex order: a,a',alpha,b,b',beta,c,c',gamma.
static const array<string, N> name = {
    "a", "a'", "alpha", "b", "b'", "beta", "c", "c'", "gamma"};
static const array<int, N> phi = {
    0, 0, 0, 1, 1, 1, 2, 2, 2};  // A=0, B=1, C=2
static const array<int, 6> terminals = {0, 1, 3, 4, 6, 7};

struct Graph {
  array<uint16_t, N> adj{};

  void add(int u, int v) {
    adj[u] |= uint16_t(1u << v);
    adj[v] |= uint16_t(1u << u);
  }

  bool has(int u, int v) const { return (adj[u] >> v) & 1u; }

  int deg(int v, uint16_t mask = (1u << N) - 1) const {
    return __builtin_popcount((unsigned)(adj[v] & mask));
  }
};

static Graph make_graph() {
  Graph g;
  auto e = [&](int u, int v) { g.add(u, v); };
  e(0, 4);  // a b'
  e(0, 6);  // a c
  e(0, 8);  // a gamma
  e(1, 5);  // a' beta
  e(1, 8);  // a' gamma
  e(2, 3);  // alpha b
  e(2, 5);  // alpha beta
  e(2, 6);  // alpha c
  e(3, 6);  // b c
  e(3, 7);  // b c'
  e(3, 8);  // b gamma
  e(4, 7);  // b' c'
  e(4, 8);  // b' gamma
  e(5, 7);  // beta c'
  e(5, 8);  // beta gamma
  return g;
}

static string mask_str(uint16_t mask) {
  string s = "{";
  bool first = true;
  for (int i = 0; i < N; ++i) {
    if (((mask >> i) & 1u) == 0) continue;
    if (!first) s += ",";
    first = false;
    s += name[i];
  }
  s += "}";
  return s;
}

static bool is_terminal(int v) {
  for (int t : terminals) {
    if (t == v) return true;
  }
  return false;
}

static array<uint8_t, N> terminal_lists(int free_terminal) {
  array<uint8_t, N> lists;
  lists.fill(ALL);
  int forbidden = phi[free_terminal];
  for (int t : terminals) {
    if (t == free_terminal) continue;
    lists[t] &= uint8_t(~(1u << forbidden));
  }
  return lists;
}

static bool colourable(const Graph& g, uint16_t mask,
                       const array<uint8_t, N>& lists,
                       array<int, N>* witness = nullptr) {
  array<int, N> col;
  col.fill(-1);
  vector<int> verts;
  for (int v = 0; v < N; ++v) {
    if ((mask >> v) & 1u) verts.push_back(v);
  }
  sort(verts.begin(), verts.end(), [&](int x, int y) {
    int lx = __builtin_popcount((unsigned)lists[x]);
    int ly = __builtin_popcount((unsigned)lists[y]);
    if (lx != ly) return lx < ly;
    int dx = g.deg(x, mask), dy = g.deg(y, mask);
    if (dx != dy) return dx > dy;
    return x < y;
  });

  function<bool(int)> dfs = [&](int pos) {
    if (pos == (int)verts.size()) {
      if (witness) *witness = col;
      return true;
    }
    int v = verts[pos];
    uint8_t avail = lists[v];
    uint16_t nb = g.adj[v] & mask;
    while (nb) {
      int u = __builtin_ctz((unsigned)nb);
      nb &= nb - 1;
      if (col[u] >= 0) avail &= uint8_t(~(1u << col[u]));
    }
    for (int c = 0; c < 3; ++c) {
      if (((avail >> c) & 1u) == 0) continue;
      col[v] = c;
      if (dfs(pos + 1)) return true;
      col[v] = -1;
    }
    return false;
  };
  return dfs(0);
}

static uint16_t kempe_component(const Graph& g, int start, int c1, int c2) {
  uint16_t comp = 0;
  queue<int> q;
  comp |= uint16_t(1u << start);
  q.push(start);
  while (!q.empty()) {
    int v = q.front();
    q.pop();
    uint16_t nb = g.adj[v];
    while (nb) {
      int u = __builtin_ctz((unsigned)nb);
      nb &= nb - 1;
      if ((comp >> u) & 1u) continue;
      if (phi[u] != c1 && phi[u] != c2) continue;
      comp |= uint16_t(1u << u);
      q.push(u);
    }
  }
  return comp;
}

static uint16_t third_support(const Graph& g, uint16_t comp, int third) {
  uint16_t support = 0;
  for (int v = 0; v < N; ++v) {
    if (((comp >> v) & 1u) == 0) continue;
    uint16_t nb = g.adj[v] & ~comp;
    while (nb) {
      int u = __builtin_ctz((unsigned)nb);
      nb &= nb - 1;
      if (phi[u] == third) support |= uint16_t(1u << v);
    }
  }
  return support;
}

static int boundary_to_colour(const Graph& g, uint16_t comp, int colour) {
  int count = 0;
  for (int v = 0; v < N; ++v) {
    if (((comp >> v) & 1u) == 0) continue;
    uint16_t nb = g.adj[v] & ~comp;
    while (nb) {
      int u = __builtin_ctz((unsigned)nb);
      nb &= nb - 1;
      if (phi[u] == colour) ++count;
    }
  }
  return count;
}

static bool support_critical_on_K(const Graph& g, uint16_t comp,
                                  int free_terminal, int third) {
  array<uint8_t, N> lists = terminal_lists(free_terminal);
  uint16_t support = third_support(g, comp, third);
  for (int v = 0; v < N; ++v) {
    if ((support >> v) & 1u) lists[v] &= uint8_t(~(1u << third));
  }
  return !colourable(g, comp, lists);
}

static bool list_critical(const Graph& g, int free_terminal) {
  uint16_t full = (1u << N) - 1;
  auto lists = terminal_lists(free_terminal);
  if (colourable(g, full, lists)) return false;
  for (int y = 0; y < N; ++y) {
    if (!colourable(g, uint16_t(full & ~(1u << y)), lists)) return false;
  }
  return true;
}

int main() {
  Graph g = make_graph();
  uint16_t full = (1u << N) - 1;
  cout << "H degrees:";
  for (int v = 0; v < N; ++v) cout << " " << name[v] << "=" << g.deg(v);
  cout << "\n";

  cout << "After adding v to terminals:";
  for (int x = 0; x < N; ++x) {
    int gd = g.deg(x) + (is_terminal(x) ? 1 : 0);
    cout << " " << name[x] << "=" << gd;
  }
  cout << "\n";

  uint16_t K = kempe_component(g, 1, 0, 1);  // AB component through a'
  cout << "AB Kempe component through a': " << mask_str(K) << "\n";
  cout << "Expected {a',alpha,b,beta}: " << (((K == ((1u << 1) | (1u << 2) | (1u << 3) | (1u << 5))) ? "YES" : "NO")) << "\n";
  cout << "C-support on K: " << mask_str(third_support(g, K, 2)) << "\n";
  cout << "e_H(K,C)=" << boundary_to_colour(g, K, 2) << " (desired type-(1,1) bound would be <=4)\n";
  cout << "support-critical for L_a: " << (support_critical_on_K(g, K, 0, 2) ? "YES" : "NO") << "\n";
  cout << "support-critical for L_b': " << (support_critical_on_K(g, K, 4, 2) ? "YES" : "NO") << "\n";

  cout << "Terminal list-criticalities:\n";
  for (int t : terminals) {
    cout << "  L_" << name[t] << ": " << (list_critical(g, t) ? "CRITICAL" : "not-critical") << "\n";
  }

  cout << "Comparable same-colour nonedge checks:\n";
  for (int x = 0; x < N; ++x) {
    for (int y = x + 1; y < N; ++y) {
      if (phi[x] != phi[y] || g.has(x, y)) continue;
      uint16_t nx = g.adj[x], ny = g.adj[y];
      if ((nx & ~ny) == 0) {
        cout << "  N(" << name[x] << ") subset N(" << name[y] << ")\n";
      }
      if ((ny & ~nx) == 0) {
        cout << "  N(" << name[y] << ") subset N(" << name[x] << ")\n";
      }
    }
  }

  cout << "Proper phi colouring: ";
  bool proper = true;
  for (int i = 0; i < N; ++i) {
    uint16_t nb = g.adj[i];
    while (nb) {
      int j = __builtin_ctz((unsigned)nb);
      nb &= nb - 1;
      if (i < j && phi[i] == phi[j]) proper = false;
    }
  }
  cout << (proper ? "YES" : "NO") << "\n";
  cout << "done\n";
  (void)full;
  return 0;
}
