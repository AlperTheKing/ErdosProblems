// Terminal list-critical blocker diagnostics for Erdos #944.
//
// Given a small 6-regular no-critical-edge seed, inspect every 3-colourable
// vertex deletion G-v.  For each colour-pair {a,a'} in N(v) and terminal a,
// build GPT Pro's list assignment L_a on H = G-v:
//   L_a(a) = all colours,
//   L_a(x) = colours except A for x in N(v) \ {a},
//   L_a(x) = all colours otherwise.
// Then find minimum induced L_a-uncolourable blockers in H.
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using namespace std;

static constexpr int MAXN = 32;
static constexpr uint8_t ALL = 0b111;

struct Graph {
  int n = 0;
  uint32_t adj[MAXN]{};

  void add_edge(int u, int v) {
    if (u == v) return;
    n = max(n, max(u, v) + 1);
    adj[u] |= 1u << v;
    adj[v] |= 1u << u;
  }

  bool has_edge(int u, int v) const { return (adj[u] >> v) & 1u; }
  int deg_in(int v, uint32_t mask) const { return __builtin_popcount(adj[v] & mask); }
};

static Graph parse_graph(const string& path) {
  ifstream in(path);
  if (!in) throw runtime_error("cannot open " + path);
  string text((istreambuf_iterator<char>(in)), istreambuf_iterator<char>());
  size_t g6pos = text.find("G6:");
  if (g6pos != string::npos) text = text.substr(g6pos + 3);
  size_t first = text.find_first_not_of(" \t\r\n");
  if (first == string::npos) throw runtime_error("empty input");

  Graph g;
  if (text[first] != '[' && text[first] != '(' && !isdigit((unsigned char)text[first])) {
    string line = text.substr(first);
    size_t end = line.find_first_of("\r\n \t");
    if (end != string::npos) line = line.substr(0, end);
    int n = line[0] - 63;
    if (n <= 0 || n > MAXN) throw runtime_error("unsupported graph6 order");
    g.n = n;
    int nbits = n * (n - 1) / 2;
    int need = (nbits + 5) / 6;
    if ((int)line.size() < 1 + need) throw runtime_error("truncated graph6");
    int bit = 0;
    for (int j = 1; j < n; j++) {
      for (int i = 0; i < j; i++) {
        int byte = 1 + bit / 6, off = 5 - bit % 6;
        if (((line[byte] - 63) >> off) & 1) g.add_edge(i, j);
        bit++;
      }
    }
    return g;
  }

  vector<int> vals;
  for (size_t i = 0; i < text.size();) {
    if (!isdigit((unsigned char)text[i])) {
      i++;
      continue;
    }
    int x = 0;
    while (i < text.size() && isdigit((unsigned char)text[i])) {
      x = 10 * x + (text[i] - '0');
      i++;
    }
    vals.push_back(x);
  }
  if (vals.size() % 2 != 0) throw runtime_error("odd number of integers");
  for (size_t i = 0; i < vals.size(); i += 2) g.add_edge(vals[i], vals[i + 1]);
  return g;
}

static string mask_vertices(uint32_t mask) {
  string s = "{";
  bool first = true;
  for (int v = 0; v < MAXN; v++) {
    if (((mask >> v) & 1u) == 0) continue;
    if (!first) s += ",";
    first = false;
    s += to_string(v);
  }
  s += "}";
  return s;
}

static int edge_count(const Graph& g, uint32_t mask) {
  int e = 0;
  for (int v = 0; v < g.n; v++) {
    if ((mask >> v) & 1u) e += __builtin_popcount(g.adj[v] & mask);
  }
  return e / 2;
}

static int boundary_count(const Graph& g, uint32_t mask, uint32_t full) {
  int b = 0;
  for (int v = 0; v < g.n; v++) {
    if ((mask >> v) & 1u) b += __builtin_popcount(g.adj[v] & (full & ~mask));
  }
  return b;
}

static string degree_sequence(const Graph& g, uint32_t mask) {
  vector<int> ds;
  for (int v = 0; v < g.n; v++) {
    if ((mask >> v) & 1u) ds.push_back(g.deg_in(v, mask));
  }
  sort(ds.begin(), ds.end());
  string s;
  for (size_t i = 0; i < ds.size(); i++) {
    if (i) s += ",";
    s += to_string(ds[i]);
  }
  return s;
}

static string induced_graph6(const Graph& g, uint32_t mask) {
  vector<int> verts;
  for (int v = 0; v < g.n; v++) {
    if ((mask >> v) & 1u) verts.push_back(v);
  }
  int n = (int)verts.size();
  if (n > 62) return "";
  vector<int> bits;
  for (int j = 1; j < n; j++) {
    for (int i = 0; i < j; i++) bits.push_back(g.has_edge(verts[i], verts[j]) ? 1 : 0);
  }
  while (bits.size() % 6 != 0) bits.push_back(0);
  string s;
  s.push_back(char(n + 63));
  for (size_t i = 0; i < bits.size(); i += 6) {
    int x = 0;
    for (int k = 0; k < 6; k++) x = (x << 1) | bits[i + k];
    s.push_back(char(x + 63));
  }
  return s;
}

static bool colourable_with_lists(const Graph& g, uint32_t mask,
                                  const array<uint8_t, MAXN>& lists,
                                  array<int8_t, MAXN>* witness = nullptr) {
  vector<int> verts;
  for (int v = 0; v < g.n; v++) {
    if ((mask >> v) & 1u) verts.push_back(v);
  }
  sort(verts.begin(), verts.end(), [&](int a, int b) {
    int la = __builtin_popcount((int)lists[a]), lb = __builtin_popcount((int)lists[b]);
    if (la != lb) return la < lb;
    int da = g.deg_in(a, mask), db = g.deg_in(b, mask);
    if (da != db) return da > db;
    return a < b;
  });

  array<int8_t, MAXN> colour;
  colour.fill(-1);
  function<bool(int)> dfs = [&](int pos) -> bool {
    if (pos == (int)verts.size()) {
      if (witness) *witness = colour;
      return true;
    }
    int v = verts[pos];
    uint8_t avail = lists[v];
    uint32_t nb = g.adj[v] & mask;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if (colour[u] >= 0) avail &= (uint8_t)~(1u << colour[u]);
    }
    for (int c = 0; c < 3; c++) {
      if (((avail >> c) & 1u) == 0) continue;
      colour[v] = (int8_t)c;
      if (dfs(pos + 1)) return true;
      colour[v] = -1;
    }
    return false;
  };
  return dfs(0);
}

static bool three_colourable(const Graph& g, uint32_t mask,
                             array<int8_t, MAXN>* witness = nullptr) {
  array<uint8_t, MAXN> lists;
  lists.fill(ALL);
  return colourable_with_lists(g, mask, lists, witness);
}

static void enumerate_three_colourings(const Graph& g, uint32_t mask,
                                       vector<array<int8_t, MAXN>>& out,
                                       int limit = 200000) {
  vector<int> verts;
  for (int v = 0; v < g.n; v++) {
    if ((mask >> v) & 1u) verts.push_back(v);
  }
  sort(verts.begin(), verts.end(), [&](int a, int b) {
    int da = g.deg_in(a, mask), db = g.deg_in(b, mask);
    if (da != db) return da > db;
    return a < b;
  });

  array<int8_t, MAXN> colour;
  colour.fill(-1);
  function<void(int)> dfs = [&](int pos) {
    if ((int)out.size() >= limit) return;
    if (pos == (int)verts.size()) {
      out.push_back(colour);
      return;
    }
    int v = verts[pos];
    bool used[3] = {false, false, false};
    uint32_t nb = g.adj[v] & mask;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if (colour[u] >= 0) used[colour[u]] = true;
    }
    for (int c = 0; c < 3; c++) {
      if (used[c]) continue;
      colour[v] = (int8_t)c;
      dfs(pos + 1);
      colour[v] = -1;
    }
  };
  dfs(0);
}

static vector<uint32_t> minimum_blockers(const Graph& g, uint32_t H,
                                         const array<uint8_t, MAXN>& lists) {
  int hsize = __builtin_popcount(H);
  vector<uint32_t> blockers;
  for (int sz = 1; sz <= hsize; sz++) {
    for (uint32_t sub = H; sub; sub = (sub - 1) & H) {
      if (__builtin_popcount(sub) != sz) continue;
      if (!colourable_with_lists(g, sub, lists)) blockers.push_back(sub);
    }
    if (!blockers.empty()) return blockers;
  }
  return blockers;
}

static bool inclusion_minimal_blocker(const Graph& g, uint32_t blocker,
                                      const array<uint8_t, MAXN>& lists) {
  if (colourable_with_lists(g, blocker, lists)) return false;
  uint32_t tmp = blocker;
  while (tmp) {
    int v = __builtin_ctz(tmp);
    tmp &= tmp - 1;
    if (!colourable_with_lists(g, blocker & ~(1u << v), lists)) return false;
  }
  return true;
}

static string colour_classes_key(const array<int8_t, MAXN>& colour, uint32_t mask) {
  vector<string> classes;
  for (int c = 0; c < 3; c++) {
    uint32_t cm = 0;
    for (int v = 0; v < MAXN; v++) {
      if (((mask >> v) & 1u) && colour[v] == c) cm |= 1u << v;
    }
    classes.push_back(mask_vertices(cm));
  }
  sort(classes.begin(), classes.end());
  return classes[0] + "|" + classes[1] + "|" + classes[2];
}

int main(int argc, char** argv) {
  if (argc < 2) {
    cerr << "usage: terminal_blockers.exe graph-file [max-print-per-case]\n";
    return 2;
  }
  int max_print = argc >= 3 ? stoi(argv[2]) : 6;
  Graph g = parse_graph(argv[1]);
  uint32_t full = g.n == 32 ? 0xffffffffu : ((1u << g.n) - 1u);

  cout << "GRAPH " << argv[1] << "\n";
  cout << "n=" << g.n << " m=" << edge_count(g, full) << "\n";
  cout << "degrees";
  for (int v = 0; v < g.n; v++) cout << " " << g.deg_in(v, full);
  cout << "\n";

  int deletion_colourable = 0;
  int cases = 0, h_not_l = 0, h_minus_a_l = 0, min_blocker_cases = 0;
  map<int, int> min_size_hist;
  set<tuple<int, uint32_t, int>> seen_case;

  for (int v = 0; v < g.n; v++) {
    uint32_t H = full & ~(1u << v);
    vector<array<int8_t, MAXN>> colourings;
    enumerate_three_colourings(g, H, colourings);
    if (colourings.empty()) continue;
    deletion_colourable++;
    set<string> partitions;
    for (const auto& col : colourings) partitions.insert(colour_classes_key(col, H));
    cout << "DELETE v=" << v << " colourings=" << colourings.size()
         << " partitions_mod_colour=" << partitions.size() << "\n";

    for (const auto& col : colourings) {
      for (int A = 0; A < 3; A++) {
        uint32_t pair = 0;
        uint32_t nb = g.adj[v] & H;
        while (nb) {
          int x = __builtin_ctz(nb);
          nb &= nb - 1;
          if (col[x] == A) pair |= 1u << x;
        }
        if (__builtin_popcount(pair) != 2) continue;
        uint32_t tmp = pair;
        while (tmp) {
          int a = __builtin_ctz(tmp);
          tmp &= tmp - 1;
          int mate = __builtin_ctz(pair & ~(1u << a));
          auto key = make_tuple(v, pair, a);
          if (!seen_case.insert(key).second) continue;

          array<uint8_t, MAXN> lists;
          lists.fill(ALL);
          for (int x = 0; x < g.n; x++) {
            if (x == v) {
              lists[x] = 0;
            } else if (x == a) {
              lists[x] = ALL;
            } else if (g.has_edge(v, x)) {
              lists[x] = (uint8_t)(ALL & ~(1u << A));
            } else {
              lists[x] = ALL;
            }
          }

          cases++;
          bool Hcol = colourable_with_lists(g, H, lists);
          bool HminusAcol = colourable_with_lists(g, H & ~(1u << a), lists);
          if (!Hcol) h_not_l++;
          if (HminusAcol) h_minus_a_l++;

          vector<uint32_t> blockers;
          if (!Hcol) blockers = minimum_blockers(g, H, lists);
          if (!blockers.empty()) {
            min_blocker_cases++;
            min_size_hist[__builtin_popcount(blockers[0])]++;
          }

          int all_contains_terminal = 0;
          int all_contains_mate = 0;
          int all_ordinary3 = 0;
          int all_inclusion_minimal = 0;
          map<int, int> all_boundary_hist;
          for (uint32_t b : blockers) {
            if ((b >> a) & 1u) all_contains_terminal++;
            if ((b >> mate) & 1u) all_contains_mate++;
            if (three_colourable(g, b)) all_ordinary3++;
            if (inclusion_minimal_blocker(g, b, lists)) all_inclusion_minimal++;
            all_boundary_hist[boundary_count(g, b, full)]++;
          }

          cout << "CASE v=" << v << " pair=" << mask_vertices(pair)
               << " terminal=" << a << " mate=" << mate
               << " H_not_L=" << (!Hcol ? 1 : 0)
               << " H_minus_terminal_L=" << (HminusAcol ? 1 : 0);
          if (!blockers.empty()) {
            cout << " minBlockerSize=" << __builtin_popcount(blockers[0])
                 << " minBlockerCount=" << blockers.size()
                 << " blockersContainTerminal=" << all_contains_terminal
                 << " blockersContainMate=" << all_contains_mate
                 << " blockersOrdinary3=" << all_ordinary3
                 << " blockersInclMinimal=" << all_inclusion_minimal
                 << " blockerBoundaryHist=";
            bool first_hist = true;
            for (auto [bb, cnt] : all_boundary_hist) {
              if (!first_hist) cout << ",";
              first_hist = false;
              cout << bb << ":" << cnt;
            }
          }
          cout << "\n";

          int printed = 0;
          for (uint32_t b : blockers) {
            if (printed++ >= max_print) break;
            bool ordinary3 = three_colourable(g, b);
            bool incl = inclusion_minimal_blocker(g, b, lists);
            uint32_t restricted = 0;
            uint32_t free_vertices = 0;
            for (int z = 0; z < g.n; z++) {
              if (((b >> z) & 1u) == 0) continue;
              if (lists[z] == ALL) free_vertices |= 1u << z;
              else restricted |= 1u << z;
            }
            cout << "  BLOCKER " << mask_vertices(b)
                 << " containsTerminal=" << (((b >> a) & 1u) ? 1 : 0)
                 << " containsMate=" << (((b >> mate) & 1u) ? 1 : 0)
                 << " restricted=" << mask_vertices(restricted)
                 << " free=" << mask_vertices(free_vertices)
                 << " ordinary3=" << (ordinary3 ? 1 : 0)
                 << " inclusionMinimal=" << (incl ? 1 : 0)
                 << " edges=" << edge_count(g, b)
                 << " boundary=" << boundary_count(g, b, full)
                 << " degseq=" << degree_sequence(g, b)
                 << " g6=" << induced_graph6(g, b) << "\n";
          }
        }
      }
    }
  }

  cout << "SUMMARY deletion_colourable_vertices=" << deletion_colourable
       << " cases=" << cases
       << " H_not_L=" << h_not_l
       << " H_minus_terminal_L=" << h_minus_a_l
       << " min_blocker_cases=" << min_blocker_cases << "\n";
  cout << "min_blocker_size_hist";
  for (auto [k, v] : min_size_hist) cout << " [" << k << "]=" << v;
  cout << "\n";
  return 0;
}
