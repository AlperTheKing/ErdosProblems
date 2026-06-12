// Verify GPT Pro's 22-vertex diagnostic graph G0 for #944.
//
// Vertex order:
//   A: a,a',alpha,A1,A2,A3,A4          indices 0..6
//   B: b,b',beta,B1,B2,B3,B4           indices 7..13
//   C: c,c',gamma,C1,C2,C3,C4          indices 14..20
//   v                                  index 21
//
// The deleted graph H0=G0-v is tripartite in A/B/C.
#include <algorithm>
#include <array>
#include <cstdint>
#include <functional>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

static constexpr int N = 22;
static constexpr int VERT_V = 21;
static constexpr uint8_t ALL = 0b111;
static const string G6 =
    "U@`d`z{A?C@O???FoIo?o?F`?BzGSa?uaSCWuo??";
static const array<string, N> names = {
    "a",  "a'", "alpha", "A1", "A2", "A3", "A4",
    "b",  "b'", "beta",  "B1", "B2", "B3", "B4",
    "c",  "c'", "gamma", "C1", "C2", "C3", "C4",
    "v"};
static const array<int, 6> terminals = {0, 1, 7, 8, 14, 15};

struct Graph {
  int n = 0;
  array<uint32_t, N> adj{};
  bool has(int u, int v) const { return (adj[u] >> v) & 1u; }
  void add(int u, int v) {
    adj[u] |= 1u << v;
    adj[v] |= 1u << u;
  }
  int deg(int v, uint32_t mask = (N == 32 ? ~0u : ((1u << N) - 1u))) const {
    return __builtin_popcount(adj[v] & mask);
  }
};

static int colour_of(int v) {
  if (0 <= v && v <= 6) return 0;
  if (7 <= v && v <= 13) return 1;
  if (14 <= v && v <= 20) return 2;
  return 3;
}

static bool is_terminal(int v) {
  for (int t : terminals) {
    if (t == v) return true;
  }
  return false;
}

static Graph parse_g6(const string& s) {
  if (s.empty() || s[0] < 63 || s[0] > 126) throw runtime_error("bad graph6");
  int n = s[0] - 63;
  if (n != N) throw runtime_error("unexpected n");
  int nbits = n * (n - 1) / 2;
  int need = (nbits + 5) / 6;
  if ((int)s.size() < 1 + need) throw runtime_error("truncated graph6");
  Graph g;
  g.n = n;
  int bit = 0;
  for (int j = 1; j < n; ++j) {
    for (int i = 0; i < j; ++i) {
      int byte = 1 + bit / 6;
      int off = 5 - bit % 6;
      if (((s[byte] - 63) >> off) & 1) g.add(i, j);
      ++bit;
    }
  }
  return g;
}

static bool colourable_with_lists(const Graph& g, uint32_t mask,
                                  const vector<uint8_t>& lists) {
  vector<int> verts;
  for (int v = 0; v < g.n; ++v) {
    if ((mask >> v) & 1u) verts.push_back(v);
  }
  sort(verts.begin(), verts.end(), [&](int a, int b) {
    int la = __builtin_popcount((unsigned)lists[a]);
    int lb = __builtin_popcount((unsigned)lists[b]);
    if (la != lb) return la < lb;
    int da = g.deg(a, mask), db = g.deg(b, mask);
    if (da != db) return da > db;
    return a < b;
  });
  array<int8_t, N> col;
  col.fill(-1);
  function<bool(int)> dfs = [&](int pos) -> bool {
    if (pos == (int)verts.size()) return true;
    int v = verts[pos];
    uint8_t avail = lists[v];
    uint32_t nb = g.adj[v] & mask;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if (col[u] >= 0) avail &= (uint8_t)~(1u << col[u]);
    }
    for (int c = 0; c < 3; ++c) {
      if (((avail >> c) & 1u) == 0) continue;
      col[v] = (int8_t)c;
      if (dfs(pos + 1)) return true;
      col[v] = -1;
    }
    return false;
  };
  return dfs(0);
}

static bool three_colourable(const Graph& g, uint32_t mask) {
  return colourable_with_lists(g, mask, vector<uint8_t>(g.n, ALL));
}

static vector<uint8_t> terminal_lists(const Graph& g, int free_terminal) {
  vector<uint8_t> lists(g.n, ALL);
  int forbidden = colour_of(free_terminal);
  for (int t : terminals) {
    if (t == free_terminal) continue;
    lists[t] &= (uint8_t)~(1u << forbidden);
  }
  return lists;
}

static int deletion_count_for_list(const Graph& g, int free_terminal) {
  uint32_t H = ((1u << N) - 1u) & ~(1u << VERT_V);
  auto lists = terminal_lists(g, free_terminal);
  int count = 0;
  for (int y = 0; y < N; ++y) {
    if (y == VERT_V) continue;
    if (colourable_with_lists(g, H & ~(1u << y), lists)) ++count;
  }
  return count;
}

static uint32_t kempe_component(const Graph& g, int start, int c1, int c2) {
  uint32_t H = ((1u << N) - 1u) & ~(1u << VERT_V);
  uint32_t comp = 0;
  queue<int> q;
  comp |= 1u << start;
  q.push(start);
  while (!q.empty()) {
    int v = q.front();
    q.pop();
    uint32_t nb = g.adj[v] & H;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if ((comp >> u) & 1u) continue;
      int cu = colour_of(u);
      if (cu != c1 && cu != c2) continue;
      comp |= 1u << u;
      q.push(u);
    }
  }
  return comp;
}

static string mask_names(uint32_t mask) {
  string s = "{";
  bool first = true;
  for (int v = 0; v < N; ++v) {
    if (((mask >> v) & 1u) == 0) continue;
    if (!first) s += ",";
    first = false;
    s += names[v];
  }
  s += "}";
  return s;
}

static int boundary_to_colour(const Graph& g, uint32_t comp, int colour) {
  int count = 0;
  uint32_t H = ((1u << N) - 1u) & ~(1u << VERT_V);
  for (int v = 0; v < N; ++v) {
    if (((comp >> v) & 1u) == 0) continue;
    uint32_t nb = g.adj[v] & H & ~comp;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if (colour_of(u) == colour) ++count;
    }
  }
  return count;
}

static uint32_t third_support(const Graph& g, uint32_t comp, int third) {
  uint32_t support = 0;
  uint32_t H = ((1u << N) - 1u) & ~(1u << VERT_V);
  for (int v = 0; v < N; ++v) {
    if (((comp >> v) & 1u) == 0) continue;
    uint32_t nb = g.adj[v] & H & ~comp;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if (colour_of(u) == third) support |= 1u << v;
    }
  }
  return support;
}

static bool support_critical(const Graph& g, uint32_t comp, int free_terminal,
                             int third) {
  auto lists = terminal_lists(g, free_terminal);
  uint32_t support = third_support(g, comp, third);
  for (int v = 0; v < N; ++v) {
    if ((support >> v) & 1u) lists[v] &= (uint8_t)~(1u << third);
  }
  return !colourable_with_lists(g, comp, lists);
}

static bool no_same_colour_comparable_in_G(const Graph& g) {
  for (int x = 0; x < VERT_V; ++x) {
    for (int y = x + 1; y < VERT_V; ++y) {
      if (colour_of(x) != colour_of(y)) continue;
      uint32_t nx = g.adj[x], ny = g.adj[y];
      if ((nx & ~ny) == 0 || (ny & ~nx) == 0) return false;
    }
  }
  return true;
}

int main() {
  Graph g = parse_g6(G6);
  uint32_t full = (1u << N) - 1u;
  uint32_t H = full & ~(1u << VERT_V);

  cout << "n=" << g.n << "\n";
  cout << "degrees:";
  bool regular = true;
  for (int v = 0; v < g.n; ++v) {
    int d = g.deg(v);
    cout << " " << names[v] << "=" << d;
    regular = regular && (d == 6);
  }
  cout << "\n6regular=" << (regular ? "YES" : "NO") << "\n";

  bool H_tripartite = true;
  for (int u = 0; u < VERT_V; ++u) {
    for (int v = u + 1; v < VERT_V; ++v) {
      if (colour_of(u) == colour_of(v) && g.has(u, v)) H_tripartite = false;
    }
  }
  cout << "H_tripartite_under_displayed_colouring="
       << (H_tripartite ? "YES" : "NO") << "\n";
  cout << "G_three_colourable=" << (three_colourable(g, full) ? "YES" : "NO")
       << "\n";
  cout << "H_three_colourable=" << (three_colourable(g, H) ? "YES" : "NO")
       << "\n";

  int edge_count = 0, g_minus_edge_threecol = 0;
  for (int u = 0; u < g.n; ++u) {
    for (int v = u + 1; v < g.n; ++v) {
      if (!g.has(u, v)) continue;
      ++edge_count;
      Graph h = g;
      h.adj[u] &= ~(1u << v);
      h.adj[v] &= ~(1u << u);
      if (three_colourable(h, full)) ++g_minus_edge_threecol;
    }
  }
  cout << "edges=" << edge_count
       << " G_minus_edge_three_colourable_count=" << g_minus_edge_threecol
       << "\n";

  int vertex_deletion_threecol = 0;
  cout << "three_colourable_vertex_deletions:";
  for (int y = 0; y < g.n; ++y) {
    if (three_colourable(g, full & ~(1u << y))) {
      ++vertex_deletion_threecol;
      cout << " " << names[y];
    }
  }
  cout << "\nvertex_deletion_threecol_count=" << vertex_deletion_threecol
       << "\n";

  cout << "no_same_colour_comparable_in_G="
       << (no_same_colour_comparable_in_G(g) ? "YES" : "NO") << "\n";

  cout << "terminal list deletion counts:\n";
  for (int t : terminals) {
    auto lists = terminal_lists(g, t);
    cout << "  L_" << names[t]
         << " H_colourable=" << (colourable_with_lists(g, H, lists) ? "YES" : "NO")
         << " H-y_count=" << deletion_count_for_list(g, t) << "/21\n";
  }

  uint32_t KAB = kempe_component(g, 1, 0, 1);
  cout << "KAB_through_a'=" << mask_names(KAB) << "\n";
  cout << "KAB_e_to_C=" << boundary_to_colour(g, KAB, 2) << "\n";
  cout << "KAB_support_L_a=" << (support_critical(g, KAB, 0, 2) ? "YES" : "NO")
       << " L_b'=" << (support_critical(g, KAB, 8, 2) ? "YES" : "NO")
       << "\n";

  uint32_t KAC = kempe_component(g, 0, 0, 2);
  cout << "KAC_through_a=" << mask_names(KAC) << "\n";
  cout << "KAC_e_to_B=" << boundary_to_colour(g, KAC, 1) << "\n";
  cout << "KAC_support_L_a=" << (support_critical(g, KAC, 0, 1) ? "YES" : "NO")
       << " L_a'=" << (support_critical(g, KAC, 1, 1) ? "YES" : "NO")
       << " L_c=" << (support_critical(g, KAC, 14, 1) ? "YES" : "NO")
       << " L_c'=" << (support_critical(g, KAC, 15, 1) ? "YES" : "NO")
       << "\n";
  return 0;
}
