// Exact local/Kempe diagnostics for candidate 6-regular 4-critical graphs.
//
// Input: a text file containing edge pairs such as [(0,7),(0,8),...].
// Usage:
//   g++ -O3 -std=c++20 kempe_balance.cpp -o kempe_balance.exe
//   kempe_balance.exe unique_6reg_4vc_n13.txt
//
// This is not a target searcher. It measures which local constraints fail or
// hold in a concrete graph, especially the vertex-form Kempe-balance condition.
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

using namespace std;

static constexpr int MAXN = 62;

struct Graph {
  int n = 0;
  uint64_t adj[MAXN]{};

  void add_edge(int u, int v) {
    n = max(n, max(u, v) + 1);
    adj[u] |= 1ull << v;
    adj[v] |= 1ull << u;
  }

  int deg(int v) const { return __builtin_popcountll(adj[v]); }
  bool has_edge(int u, int v) const { return (adj[u] >> v) & 1ull; }
};

static vector<pair<int, int>> parse_edges(const string& path) {
  ifstream in(path);
  if (!in) throw runtime_error("cannot open input file: " + path);
  string text((istreambuf_iterator<char>(in)), istreambuf_iterator<char>());
  size_t g6pos = text.find("G6:");
  if (g6pos != string::npos) text = text.substr(g6pos + 3);
  size_t first = text.find_first_not_of(" \t\r\n");
  if (first != string::npos && text[first] != '[' && text[first] != '(') {
    string line = text.substr(first);
    size_t end = line.find_first_of("\r\n \t");
    if (end != string::npos) line = line.substr(0, end);
    int n = line[0] - 63;
    if (n < 0 || n > 62) throw runtime_error("unsupported graph6 order");
    int nbits = n * (n - 1) / 2;
    int need = (nbits + 5) / 6;
    if ((int)line.size() < 1 + need) throw runtime_error("truncated graph6 line");
    vector<pair<int, int>> edges;
    int bit = 0;
    for (int j = 1; j < n; j++) {
      for (int i = 0; i < j; i++) {
        int byte = 1 + bit / 6, off = 5 - bit % 6;
        if (((line[byte] - 63) >> off) & 1) edges.push_back({i, j});
        bit++;
      }
    }
    return edges;
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
  if (vals.size() % 2 != 0) throw runtime_error("odd number of integers in edge file");
  vector<pair<int, int>> edges;
  for (size_t i = 0; i < vals.size(); i += 2) {
    if (vals[i] == vals[i + 1]) throw runtime_error("loop in edge file");
    edges.push_back({vals[i], vals[i + 1]});
  }
  sort(edges.begin(), edges.end());
  edges.erase(unique(edges.begin(), edges.end()), edges.end());
  return edges;
}

static bool is_three_colourable(const Graph& g, uint64_t removed_vertices = 0,
                                int rem_u = -1, int rem_v = -1) {
  vector<int> verts;
  for (int v = 0; v < g.n; v++) {
    if (((removed_vertices >> v) & 1ull) == 0) verts.push_back(v);
  }
  sort(verts.begin(), verts.end(), [&](int a, int b) { return g.deg(a) > g.deg(b); });

  array<int8_t, MAXN> colour;
  colour.fill(-1);

  function<bool(int)> dfs = [&](int pos) -> bool {
    if (pos == (int)verts.size()) return true;
    int v = verts[pos];
    bool used[3] = {false, false, false};
    uint64_t nb = g.adj[v] & ~removed_vertices;
    while (nb) {
      int u = __builtin_ctzll(nb);
      nb &= nb - 1;
      if ((u == rem_u && v == rem_v) || (u == rem_v && v == rem_u)) continue;
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

struct ColourStats {
  long long total = 0;
  long long local222 = 0;
  long long has_empty = 0;
  long long has_singleton = 0;
  long long unbalanced_pair_components = 0;
  long long edge_split_predictors = 0;
  long long edge_split_false_positives = 0;
  long long accounting_failures = 0;
  long long touched_components = 0;
  long long touched_non_singleton_components = 0;
  long long touched_non_singleton_delta6 = 0;
  map<string, long long> size_patterns;
  map<string, long long> kempe_patterns;
  map<int, long long> touched_delta_hist;
};

static string pattern_key(vector<int> xs) {
  sort(xs.begin(), xs.end());
  string s;
  for (size_t i = 0; i < xs.size(); i++) {
    if (i) s += ",";
    s += to_string(xs[i]);
  }
  return s;
}

static void analyse_colouring(const Graph& g, int removed, const array<int8_t, MAXN>& col,
                              ColourStats& stats) {
  stats.total++;

  vector<int> cls[3];
  uint64_t nb = g.adj[removed];
  while (nb) {
    int u = __builtin_ctzll(nb);
    nb &= nb - 1;
    cls[col[u]].push_back(u);
  }

  vector<int> sizes = {(int)cls[0].size(), (int)cls[1].size(), (int)cls[2].size()};
  int class_size[3] = {0, 0, 0};
  for (int u = 0; u < g.n; u++) {
    if (u == removed) continue;
    class_size[col[u]]++;
  }
  stats.size_patterns[pattern_key(sizes)]++;
  if (*min_element(sizes.begin(), sizes.end()) == 0) stats.has_empty++;
  if (find(sizes.begin(), sizes.end(), 1) != sizes.end()) stats.has_singleton++;
  if (pattern_key(sizes) != "2,2,2") return;

  stats.local222++;
  for (int a = 0; a < 3; a++) {
    for (int b = a + 1; b < 3; b++) {
      bool seen[MAXN]{};
      int delta_sum = 0;
      int opposite = 3 - a - b;
      vector<pair<int, int>> boundary_counts;
      for (int start = 0; start < g.n; start++) {
        if (start == removed || seen[start]) continue;
        if (col[start] != a && col[start] != b) continue;
        int ca = 0, cb = 0;
        vector<int> stack = {start};
        seen[start] = true;
        for (size_t sp = 0; sp < stack.size(); sp++) {
          int x = stack[sp];
          if (g.has_edge(removed, x)) {
            if (col[x] == a) ca++;
            if (col[x] == b) cb++;
          }
          uint64_t nn = g.adj[x];
          while (nn) {
            int y = __builtin_ctzll(nn);
            nn &= nn - 1;
            if (y == removed || seen[y]) continue;
            if (col[y] != a && col[y] != b) continue;
            seen[y] = true;
            stack.push_back(y);
          }
        }
        bool in_comp[MAXN]{};
        for (int z : stack) in_comp[z] = true;
        int delta = 0;
        for (int z : stack) {
          uint64_t nn = g.adj[z];
          while (nn) {
            int w = __builtin_ctzll(nn);
            nn &= nn - 1;
            if (!in_comp[w]) delta++;
          }
        }
        delta_sum += delta;
        if (ca || cb) {
          stats.touched_components++;
          stats.touched_delta_hist[delta]++;
          if ((int)stack.size() >= 2) {
            stats.touched_non_singleton_components++;
            if (delta == 6) stats.touched_non_singleton_delta6++;
          }
          boundary_counts.push_back({ca, cb});
          if (ca != cb) stats.unbalanced_pair_components++;
        }
      }
      int expected_delta_sum = 6 * class_size[opposite] + 2;
      if (delta_sum != expected_delta_sum) stats.accounting_failures++;
      sort(boundary_counts.begin(), boundary_counts.end());
      string key = to_string(a) + to_string(b) + ":";
      for (auto [ca, cb] : boundary_counts) key += "(" + to_string(ca) + "," + to_string(cb) + ")";
      stats.kempe_patterns[key]++;
    }
  }

  for (int x = 0; x < g.n; x++) {
    if (x == removed) continue;
    uint64_t nb = g.adj[x] & ~(1ull << removed);
    while (nb) {
      int y = __builtin_ctzll(nb);
      nb &= nb - 1;
      if (y <= x || y == removed) continue;
      int a = col[x], b = col[y];
      if (a == b) continue;

      bool seen[MAXN]{};
      for (int start = 0; start < g.n; start++) {
        if (start == removed || seen[start]) continue;
        if (col[start] != a && col[start] != b) continue;
        int ca = 0, cb = 0;
        vector<int> stack = {start};
        seen[start] = true;
        for (size_t sp = 0; sp < stack.size(); sp++) {
          int z = stack[sp];
          if (g.has_edge(removed, z)) {
            if (col[z] == a) ca++;
            if (col[z] == b) cb++;
          }
          uint64_t nn = g.adj[z];
          while (nn) {
            int w = __builtin_ctzll(nn);
            nn &= nn - 1;
            if (w == removed || seen[w]) continue;
            if ((z == x && w == y) || (z == y && w == x)) continue;
            if (col[w] != a && col[w] != b) continue;
            seen[w] = true;
            stack.push_back(w);
          }
        }
        if ((ca == 2 && cb == 0) || (ca == 0 && cb == 2)) {
          stats.edge_split_predictors++;
          if (!is_three_colourable(g, 0, x, y)) stats.edge_split_false_positives++;
        }
      }
    }
  }
}

static ColourStats enumerate_deleted_colourings(const Graph& g) {
  ColourStats stats;
  for (int removed = 0; removed < g.n; removed++) {
    vector<int> verts;
    for (int v = 0; v < g.n; v++) {
      if (v != removed) verts.push_back(v);
    }
    sort(verts.begin(), verts.end(), [&](int a, int b) { return g.deg(a) > g.deg(b); });

    array<int8_t, MAXN> col;
    col.fill(-1);
    function<void(int)> dfs = [&](int pos) {
      if (pos == (int)verts.size()) {
        analyse_colouring(g, removed, col, stats);
        return;
      }
      int v = verts[pos];
      bool used[3] = {false, false, false};
      uint64_t nb = g.adj[v] & ~(1ull << removed);
      while (nb) {
        int u = __builtin_ctzll(nb);
        nb &= nb - 1;
        if (col[u] >= 0) used[col[u]] = true;
      }
      for (int c = 0; c < 3; c++) {
        if (used[c]) continue;
        col[v] = (int8_t)c;
        dfs(pos + 1);
        col[v] = -1;
      }
    };
    dfs(0);
  }
  return stats;
}

static void cut_and_triangle_report(const Graph& g, const vector<pair<int, int>>& edges) {
  int min_cut = 1'000'000;
  long long nontriv_6cuts = 0;
  uint64_t full = (g.n == 64 ? ~0ull : ((1ull << g.n) - 1));
  for (uint64_t s = 1; s < full; s++) {
    if ((s & 1ull) == 0) continue;  // count each cut once via vertex 0 side
    int side = __builtin_popcountll(s);
    int cut = 0;
    for (auto [u, v] : edges) {
      if (((s >> u) & 1ull) != ((s >> v) & 1ull)) cut++;
    }
    min_cut = min(min_cut, cut);
    if (cut == 6 && side > 1 && side < g.n - 1) nontriv_6cuts++;
  }

  map<int, int> triangle_hist;
  int max_tri = 0;
  for (auto [u, v] : edges) {
    int t = __builtin_popcountll(g.adj[u] & g.adj[v]);
    triangle_hist[t]++;
    max_tri = max(max_tri, t);
  }

  cout << "edge_connectivity=" << min_cut << "\n";
  cout << "nontrivial_6cuts=" << nontriv_6cuts << "\n";
  cout << "max_triangle_count=" << max_tri << "\n";
  cout << "triangle_hist";
  for (auto [t, c] : triangle_hist) cout << " " << t << ":" << c;
  cout << "\n";
}

static void clique4_report(const Graph& g) {
  long long k4 = 0;
  vector<int> deletion_leaves_k4(g.n, 0);
  for (int a = 0; a < g.n; a++) {
    for (int b = a + 1; b < g.n; b++) {
      if (!g.has_edge(a, b)) continue;
      for (int c = b + 1; c < g.n; c++) {
        if (!g.has_edge(a, c) || !g.has_edge(b, c)) continue;
        for (int d = c + 1; d < g.n; d++) {
          if (!g.has_edge(a, d) || !g.has_edge(b, d) || !g.has_edge(c, d)) continue;
          k4++;
          for (int x = 0; x < g.n; x++) {
            if (x != a && x != b && x != c && x != d) deletion_leaves_k4[x] = 1;
          }
        }
      }
    }
  }
  int del_bad = accumulate(deletion_leaves_k4.begin(), deletion_leaves_k4.end(), 0);
  cout << "k4_count=" << k4 << "\n";
  cout << "vertex_deletions_leaving_k4=" << del_bad;
  for (int v = 0; v < g.n; v++) {
    if (deletion_leaves_k4[v]) cout << " " << v;
  }
  cout << "\n";
}

int main(int argc, char** argv) {
  if (argc < 2) {
    cerr << "usage: kempe_balance.exe edge-file.txt\n";
    return 2;
  }

  vector<pair<int, int>> edges = parse_edges(argv[1]);
  Graph g;
  for (auto [u, v] : edges) g.add_edge(u, v);

  cout << "n=" << g.n << " m=" << edges.size() << "\n";
  cout << "degrees";
  for (int v = 0; v < g.n; v++) cout << " " << g.deg(v);
  cout << "\n";

  cout << "three_colourable=" << (is_three_colourable(g) ? 1 : 0) << "\n";
  int vertex_critical_failures = 0;
  for (int v = 0; v < g.n; v++) {
    if (!is_three_colourable(g, 1ull << v)) vertex_critical_failures++;
  }
  cout << "vertex_deleted_not_three_colourable=" << vertex_critical_failures << "\n";

  int critical_edges = 0;
  for (auto [u, v] : edges) {
    if (is_three_colourable(g, 0, u, v)) critical_edges++;
  }
  cout << "critical_edges=" << critical_edges << "\n";

  cut_and_triangle_report(g, edges);
  clique4_report(g);

  ColourStats stats = enumerate_deleted_colourings(g);
  cout << "deleted_colourings=" << stats.total << "\n";
  cout << "local_222_colourings=" << stats.local222 << "\n";
  cout << "colourings_with_empty_neighbour_colour=" << stats.has_empty << "\n";
  cout << "colourings_with_singleton_neighbour_colour=" << stats.has_singleton << "\n";
  cout << "unbalanced_kempe_boundary_components=" << stats.unbalanced_pair_components << "\n";
  cout << "kempe_accounting_failures=" << stats.accounting_failures << "\n";
  cout << "touched_kempe_components=" << stats.touched_components << "\n";
  cout << "touched_non_singleton_components=" << stats.touched_non_singleton_components << "\n";
  cout << "touched_non_singleton_delta6=" << stats.touched_non_singleton_delta6 << "\n";
  cout << "edge_split_predictors=" << stats.edge_split_predictors << "\n";
  cout << "edge_split_false_positives=" << stats.edge_split_false_positives << "\n";
  cout << "neighbour_size_patterns";
  for (auto& [k, v] : stats.size_patterns) cout << " [" << k << "]=" << v;
  cout << "\n";
  cout << "kempe_boundary_patterns";
  for (auto& [k, v] : stats.kempe_patterns) cout << " [" << k << "]=" << v;
  cout << "\n";
  cout << "touched_delta_hist";
  for (auto& [k, v] : stats.touched_delta_hist) cout << " [" << k << "]=" << v;
  cout << "\n";
  return 0;
}
