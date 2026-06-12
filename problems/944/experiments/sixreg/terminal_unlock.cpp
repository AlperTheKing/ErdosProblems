// Terminal list-colouring unlock diagnostics for Erdos #944.
//
// For each 3-colourable deletion H = G-v and each terminal list assignment
// L_a, report which single-vertex deletions H-y become L_a-colourable and
// where y sits relative to the original Kempe components containing the mate
// terminal a'.  In a genuine target, global terminal-list-criticality forces
// every proper H-y to unlock; small no-critical-edge seeds show what fails.
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
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
  int deg_in(int v, uint32_t mask) const {
    return __builtin_popcount(adj[v] & mask);
  }
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
  if (text[first] != '[' && text[first] != '(' &&
      !isdigit((unsigned char)text[first])) {
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

static string vertices(uint32_t mask) {
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

static int boundary_count(const Graph& g, uint32_t mask, uint32_t full) {
  int b = 0;
  for (int v = 0; v < g.n; v++) {
    if ((mask >> v) & 1u) b += __builtin_popcount(g.adj[v] & (full & ~mask));
  }
  return b;
}

static bool colourable_with_lists(const Graph& g, uint32_t mask,
                                  const array<uint8_t, MAXN>& lists,
                                  array<int8_t, MAXN>* witness = nullptr) {
  vector<int> verts;
  for (int v = 0; v < g.n; v++) {
    if ((mask >> v) & 1u) verts.push_back(v);
  }
  sort(verts.begin(), verts.end(), [&](int a, int b) {
    int la = __builtin_popcount((int)lists[a]);
    int lb = __builtin_popcount((int)lists[b]);
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
    uint8_t avail = ALL;
    uint32_t nb = g.adj[v] & mask;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if (colour[u] >= 0) avail &= (uint8_t)~(1u << colour[u]);
    }
    for (int c = 0; c < 3; c++) {
      if (((avail >> c) & 1u) == 0) continue;
      colour[v] = (int8_t)c;
      dfs(pos + 1);
      colour[v] = -1;
    }
  };
  dfs(0);
}

static string partition_key(const array<int8_t, MAXN>& col, uint32_t mask) {
  vector<uint32_t> cls(3, 0);
  for (int v = 0; v < MAXN; v++) {
    if (((mask >> v) & 1u) && col[v] >= 0) cls[col[v]] |= 1u << v;
  }
  sort(cls.begin(), cls.end());
  string s;
  for (uint32_t x : cls) {
    s += to_string(x);
    s += "|";
  }
  return s;
}

static uint32_t kempe_component(const Graph& g, uint32_t mask,
                                const array<int8_t, MAXN>& col, int start,
                                int c1, int c2) {
  if (((mask >> start) & 1u) == 0) return 0;
  if (col[start] != c1 && col[start] != c2) return 0;
  uint32_t comp = 0;
  queue<int> q;
  comp |= 1u << start;
  q.push(start);
  while (!q.empty()) {
    int v = q.front();
    q.pop();
    uint32_t nb = g.adj[v] & mask;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if ((comp >> u) & 1u) continue;
      if (col[u] != c1 && col[u] != c2) continue;
      comp |= 1u << u;
      q.push(u);
    }
  }
  return comp;
}

static array<int, 3> terminal_counts(const Graph& g, int v,
                                     const array<int8_t, MAXN>& col,
                                     uint32_t present) {
  array<int, 3> cnt{0, 0, 0};
  uint32_t nb = g.adj[v] & present;
  while (nb) {
    int u = __builtin_ctz(nb);
    nb &= nb - 1;
    if (col[u] >= 0) cnt[col[u]]++;
  }
  return cnt;
}

static string colour_name(int c) {
  static const char* names[] = {"A", "B", "C"};
  return names[c];
}

static uint32_t third_colour_support(const Graph& g, uint32_t hmask,
                                     const array<int8_t, MAXN>& col,
                                     uint32_t comp, int third) {
  uint32_t third_outside = 0;
  for (int v = 0; v < g.n; v++) {
    if (((hmask >> v) & 1u) && ((comp >> v) & 1u) == 0 && col[v] == third) {
      third_outside |= 1u << v;
    }
  }
  uint32_t support = 0;
  uint32_t m = comp;
  while (m) {
    int x = __builtin_ctz(m);
    m &= m - 1;
    if (g.adj[x] & third_outside) support |= 1u << x;
  }
  return support;
}

static bool component_M_colourable(const Graph& g, uint32_t comp,
                                   const array<uint8_t, MAXN>& lists,
                                   uint32_t support, int third) {
  array<uint8_t, MAXN> mlist = lists;
  uint32_t s = support;
  while (s) {
    int x = __builtin_ctz(s);
    s &= s - 1;
    mlist[x] &= (uint8_t)~(1u << third);
  }
  return colourable_with_lists(g, comp, mlist, nullptr);
}

static bool satisfies_lists_and_proper(const Graph& g, uint32_t mask,
                                       const array<int8_t, MAXN>& col,
                                       const array<uint8_t, MAXN>& lists) {
  for (int v = 0; v < g.n; v++) {
    if (((mask >> v) & 1u) == 0) continue;
    if (col[v] < 0 || (((lists[v] >> col[v]) & 1u) == 0)) return false;
    uint32_t nb = g.adj[v] & mask;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if (u > v && col[u] == col[v]) return false;
    }
  }
  return true;
}

static bool single_kempe_swap_unlocks(const Graph& g, uint32_t mask,
                                      const array<int8_t, MAXN>& phi,
                                      const array<uint8_t, MAXN>& lists) {
  if (satisfies_lists_and_proper(g, mask, phi, lists)) return true;
  for (int c1 = 0; c1 < 3; c1++) {
    for (int c2 = c1 + 1; c2 < 3; c2++) {
      uint32_t seen = 0;
      for (int start = 0; start < g.n; start++) {
        if (((mask >> start) & 1u) == 0 || ((seen >> start) & 1u)) continue;
        if (phi[start] != c1 && phi[start] != c2) continue;
        uint32_t comp = kempe_component(g, mask, phi, start, c1, c2);
        seen |= comp;
        array<int8_t, MAXN> swapped = phi;
        uint32_t m = comp;
        while (m) {
          int x = __builtin_ctz(m);
          m &= m - 1;
          if (swapped[x] == c1) swapped[x] = c2;
          else if (swapped[x] == c2) swapped[x] = c1;
        }
        if (satisfies_lists_and_proper(g, mask, swapped, lists)) return true;
      }
    }
  }
  return false;
}

int main(int argc, char** argv) {
  if (argc < 2) {
    cerr << "usage: terminal_unlock <graph-file>\n";
    return 2;
  }
  Graph g = parse_graph(argv[1]);
  uint32_t full = (g.n == 32) ? 0xffffffffu : ((1u << g.n) - 1u);
  cout << "GRAPH " << argv[1] << "\n";
  cout << "n=" << g.n << "\n";

  for (int v = 0; v < g.n; v++) {
    uint32_t hmask = full & ~(1u << v);
    vector<array<int8_t, MAXN>> colourings;
    enumerate_three_colourings(g, hmask, colourings);
    if (colourings.empty()) continue;
    set<string> seen;
    int partition_index = 0;
    for (const auto& phi : colourings) {
      string key = partition_key(phi, hmask);
      if (!seen.insert(key).second) continue;
      partition_index++;
      auto cnt = terminal_counts(g, v, phi, hmask);
      if (cnt != array<int, 3>{2, 2, 2}) continue;

      cout << "DELETE v=" << v << " partition=" << partition_index
           << " terminal_counts=2,2,2\n";
      for (int A = 0; A < 3; A++) {
        vector<int> aterms;
        uint32_t nb = g.adj[v] & hmask;
        while (nb) {
          int u = __builtin_ctz(nb);
          nb &= nb - 1;
          if (phi[u] == A) aterms.push_back(u);
        }
        if (aterms.size() != 2) continue;
        for (int ti = 0; ti < 2; ti++) {
          int a = aterms[ti], mate = aterms[1 - ti];
          array<uint8_t, MAXN> lists;
          lists.fill(ALL);
          uint32_t nbh = g.adj[v] & hmask;
          while (nbh) {
            int x = __builtin_ctz(nbh);
            nbh &= nbh - 1;
            if (x != a) lists[x] &= (uint8_t)~(1u << A);
          }
          bool h_col = colourable_with_lists(g, hmask, lists, nullptr);

          int B = (A + 1) % 3;
          int C = (A + 2) % 3;
          uint32_t compAB = kempe_component(g, hmask, phi, mate, A, B);
          uint32_t compAC = kempe_component(g, hmask, phi, mate, A, C);
          int bdAB = boundary_count(g, compAB, full);
          int bdAC = boundary_count(g, compAC, full);
          uint32_t suppAB = third_colour_support(g, hmask, phi, compAB, C);
          uint32_t suppAC = third_colour_support(g, hmask, phi, compAC, B);
          bool mAB = component_M_colourable(g, compAB, lists, suppAB, C);
          bool mAC = component_M_colourable(g, compAC, lists, suppAC, B);

          map<string, int> bucket;
          vector<string> examples;
          int unlocks = 0;
          int already_ok = 0;
          int single_swap = 0;
          for (int y = 0; y < g.n; y++) {
            if (((hmask >> y) & 1u) == 0) continue;
            uint32_t ymask = hmask & ~(1u << y);
            bool phi_ok = satisfies_lists_and_proper(g, ymask, phi, lists);
            if (phi_ok) already_ok++;
            array<int8_t, MAXN> psi;
            bool ok = colourable_with_lists(g, ymask, lists, &psi);
            if (!ok) continue;
            unlocks++;
            bool one_swap = single_kempe_swap_unlocks(g, ymask, phi, lists);
            if (one_swap) single_swap++;
            auto tc = terminal_counts(g, v, psi, ymask);
            string b;
            b += "ycol=" + colour_name(phi[y]);
            b += ((compAB >> y) & 1u) ? " inMateAB" : " outMateAB";
            b += ((compAC >> y) & 1u) ? " inMateAC" : " outMateAC";
            b += " termAafter=" + to_string(tc[A]);
            if (phi_ok) b += " phiOK";
            else if (one_swap) b += " oneSwap";
            bucket[b]++;
            if (examples.size() < 6) {
              examples.push_back("y=" + to_string(y) + " " + b);
            }
          }

          cout << "  L_" << a << " colour=" << colour_name(A)
               << " mate=" << mate
               << " H_L_colourable=" << (h_col ? 1 : 0)
               << " unlocks=" << unlocks << "/" << __builtin_popcount(hmask)
               << " phiOK=" << already_ok
               << " oneSwapUnlocks=" << single_swap
               << " mateAB_size=" << __builtin_popcount(compAB)
               << " mateAB_bd=" << bdAB
               << " mateAB_support=" << __builtin_popcount(suppAB)
               << " mateAB_M_colourable=" << (mAB ? 1 : 0)
               << " mateAC_size=" << __builtin_popcount(compAC)
               << " mateAC_bd=" << bdAC
               << " mateAC_support=" << __builtin_popcount(suppAC)
               << " mateAC_M_colourable=" << (mAC ? 1 : 0) << "\n";
          cout << "    mateAB=" << vertices(compAB)
               << " supportAB=" << vertices(suppAB)
               << " mateAC=" << vertices(compAC)
               << " supportAC=" << vertices(suppAC) << "\n";
          for (const auto& [k, c] : bucket) {
            cout << "    bucket " << c << " " << k << "\n";
          }
          for (const auto& ex : examples) cout << "    ex " << ex << "\n";
        }
      }
    }
  }
}
