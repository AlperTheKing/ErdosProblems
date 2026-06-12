// Structural diagnostics for small 6-regular no-critical-edge seeds.
//
// For each vertex deletion, report whether the remaining graph is
// 3-colourable. If not, find minimum-cardinality induced subgraphs in G-v
// that are still not 3-colourable, and mark which of those are vertex-critical
// as induced subgraphs.
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

static constexpr int MAXN = 32;

struct Graph {
  int n = 0;
  uint32_t adj[MAXN]{};

  void add_edge(int u, int v) {
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

static bool three_colourable(const Graph& g, uint32_t mask, array<int8_t, MAXN>* witness = nullptr) {
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
  function<bool(int)> dfs = [&](int pos) -> bool {
    if (pos == (int)verts.size()) {
      if (witness) *witness = colour;
      return true;
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
      if (dfs(pos + 1)) return true;
      colour[v] = -1;
    }
    return false;
  };
  return dfs(0);
}

static bool vertex_critical_on_mask(const Graph& g, uint32_t mask) {
  if (three_colourable(g, mask)) return false;
  uint32_t tmp = mask;
  while (tmp) {
    int v = __builtin_ctz(tmp);
    tmp &= tmp - 1;
    if (!three_colourable(g, mask & ~(1u << v))) return false;
  }
  return true;
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
    if (((mask >> v) & 1u) == 0) continue;
    e += __builtin_popcount(g.adj[v] & mask);
  }
  return e / 2;
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

static string pair_list(const Graph& g, uint32_t mask, bool want_edges) {
  string s = "{";
  bool first = true;
  for (int u = 0; u < g.n; u++) {
    if (((mask >> u) & 1u) == 0) continue;
    for (int v = u + 1; v < g.n; v++) {
      if (((mask >> v) & 1u) == 0) continue;
      if (g.has_edge(u, v) != want_edges) continue;
      if (!first) s += ",";
      first = false;
      s += "(" + to_string(u) + "," + to_string(v) + ")";
    }
  }
  s += "}";
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
    for (int i = 0; i < j; i++) {
      bits.push_back(g.has_edge(verts[i], verts[j]) ? 1 : 0);
    }
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

int main(int argc, char** argv) {
  if (argc < 2) {
    cerr << "usage: seed_structure.exe graph-file\n";
    return 2;
  }
  Graph g = parse_graph(argv[1]);
  uint32_t full = (g.n == 32 ? 0xffffffffu : ((1u << g.n) - 1u));

  cout << "n=" << g.n << " m=" << edge_count(g, full) << "\n";
  cout << "degrees";
  for (int v = 0; v < g.n; v++) cout << " " << g.deg_in(v, full);
  cout << "\n";

  for (int removed = 0; removed < g.n; removed++) {
    uint32_t base = full & ~(1u << removed);
    array<int8_t, MAXN> colour;
    if (three_colourable(g, base, &colour)) {
      cout << "delete " << removed << ": 3-colourable";
      cout << " colouring";
      for (int v = 0; v < g.n; v++) {
        if (v != removed) cout << " " << v << ":" << int(colour[v]);
      }
      cout << "\n";
      continue;
    }

    cout << "delete " << removed << ": NOT 3-colourable\n";
    int base_size = __builtin_popcount(base);
    int found_size = -1;
    vector<uint32_t> cores;
    for (int sz = 4; sz <= base_size && found_size < 0; sz++) {
      for (uint32_t sub = base; sub; sub = (sub - 1) & base) {
        if (__builtin_popcount(sub) != sz) continue;
        if (!three_colourable(g, sub)) cores.push_back(sub);
      }
      if (!cores.empty()) found_size = sz;
    }
    cout << "  min_non3_size=" << found_size << " count=" << cores.size() << "\n";
    int shown = 0;
    for (uint32_t core : cores) {
      bool vc = vertex_critical_on_mask(g, core);
      cout << "  core " << mask_vertices(core)
           << " g6=" << induced_graph6(g, core)
           << " edges=" << edge_count(g, core)
           << " degseq=" << degree_sequence(g, core)
           << " vertexCritical=" << (vc ? 1 : 0)
           << " edgeList=" << pair_list(g, core, true)
           << " nonEdgeList=" << pair_list(g, core, false) << "\n";
      if (++shown >= 12) {
        if ((int)cores.size() > shown) cout << "  ...\n";
        break;
      }
    }
  }
  return 0;
}
