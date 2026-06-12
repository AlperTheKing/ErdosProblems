// Census obstruction cores inside 6-regular no-critical-edge seeds.
//
// Input is the output of classify_no_crit.cpp. For each NOCRIT_NOTVC graph,
// inspect the vertex deletions that are not 3-colourable and record the
// minimum induced non-3-colourable cores. This is a diagnostic, not a proof.
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
using namespace std;

static constexpr int MAXN = 32;

struct G {
  int n = 0;
  uint32_t adj[MAXN]{};
  void add(int u, int v) { adj[u] |= 1u << v; adj[v] |= 1u << u; }
  bool edge(int u, int v) const { return (adj[u] >> v) & 1u; }
  int deg_in(int u, uint32_t mask) const { return __builtin_popcount(adj[u] & mask); }
};

static bool decode_g6(const string& line, G& g) {
  if (line.empty()) return false;
  int n = line[0] - 63;
  if (n <= 0 || n > MAXN) return false;
  g = G{};
  g.n = n;
  int nbits = n * (n - 1) / 2;
  int need = (nbits + 5) / 6;
  if ((int)line.size() < 1 + need) return false;
  int bit = 0;
  for (int j = 1; j < n; j++) {
    for (int i = 0; i < j; i++) {
      int byte = 1 + bit / 6, off = 5 - bit % 6;
      if (((line[byte] - 63) >> off) & 1) g.add(i, j);
      bit++;
    }
  }
  return true;
}

static bool col3(const G& g, uint32_t mask) {
  vector<int> verts;
  for (int v = 0; v < g.n; v++) {
    if ((mask >> v) & 1u) verts.push_back(v);
  }
  sort(verts.begin(), verts.end(), [&](int a, int b) {
    int da = g.deg_in(a, mask), db = g.deg_in(b, mask);
    if (da != db) return da > db;
    return a < b;
  });
  int8_t colour[MAXN];
  memset(colour, -1, sizeof(colour));
  function<bool(int)> dfs = [&](int pos) -> bool {
    if (pos == (int)verts.size()) return true;
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

static int edges(const G& g, uint32_t mask) {
  int e = 0;
  for (int v = 0; v < g.n; v++) {
    if ((mask >> v) & 1u) e += __builtin_popcount(g.adj[v] & mask);
  }
  return e / 2;
}

static string degseq(const G& g, uint32_t mask) {
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

static string graph6_from_matrix(const vector<vector<int>>& a) {
  int n = (int)a.size();
  vector<int> bits;
  for (int j = 1; j < n; j++) {
    for (int i = 0; i < j; i++) bits.push_back(a[i][j]);
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

static string canonical_g6_small(const G& g, uint32_t mask) {
  vector<int> verts;
  for (int v = 0; v < g.n; v++) {
    if ((mask >> v) & 1u) verts.push_back(v);
  }
  int n = (int)verts.size();
  if (n > 8) return "";
  vector<int> p(n);
  for (int i = 0; i < n; i++) p[i] = i;
  string best;
  do {
    vector<vector<int>> a(n, vector<int>(n));
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        int u = verts[p[i]], v = verts[p[j]];
        a[i][j] = a[j][i] = g.edge(u, v);
      }
    }
    string s = graph6_from_matrix(a);
    if (best.empty() || s < best) best = s;
  } while (next_permutation(p.begin(), p.end()));
  return best;
}

static bool vertex_critical_core(const G& g, uint32_t mask) {
  if (col3(g, mask)) return false;
  uint32_t tmp = mask;
  while (tmp) {
    int v = __builtin_ctz(tmp);
    tmp &= tmp - 1;
    if (!col3(g, mask & ~(1u << v))) return false;
  }
  return true;
}

static string extract_g6(const string& line) {
  size_t p = line.find("G6:");
  if (p == string::npos) return "";
  p += 3;
  while (p < line.size() && isspace((unsigned char)line[p])) p++;
  size_t q = p;
  while (q < line.size() && !isspace((unsigned char)line[q])) q++;
  return line.substr(p, q - p);
}

int main() {
  string line;
  long long graphs = 0, failed_deletions = 0, total_min_cores = 0;
  map<int, long long> failed_vertices_by_graph;
  map<int, long long> min_size_hist;
  map<string, long long> core_sig_hist;
  map<string, set<string>> examples;

  while (getline(cin, line)) {
    if (line.rfind("NOCRIT_NOTVC", 0) != 0 && line.rfind("TARGET_G6", 0) != 0) continue;
    string g6 = extract_g6(line);
    if (g6.empty() && line.rfind("TARGET_G6:", 0) == 0) {
      size_t p = line.find(':');
      g6 = line.substr(p + 1);
      while (!g6.empty() && isspace((unsigned char)g6.front())) g6.erase(g6.begin());
    }
    G g;
    if (!decode_g6(g6, g)) continue;
    graphs++;
    uint32_t full = (g.n == 32 ? 0xffffffffu : ((1u << g.n) - 1u));
    int graph_failures = 0;
    for (int removed = 0; removed < g.n; removed++) {
      uint32_t base = full & ~(1u << removed);
      if (col3(g, base)) continue;
      graph_failures++;
      failed_deletions++;
      int base_sz = __builtin_popcount(base);
      vector<uint32_t> cores;
      int found = -1;
      for (int sz = 4; sz <= base_sz && found < 0; sz++) {
        for (uint32_t sub = base; sub; sub = (sub - 1) & base) {
          if (__builtin_popcount(sub) != sz) continue;
          if (!col3(g, sub)) cores.push_back(sub);
        }
        if (!cores.empty()) found = sz;
      }
      min_size_hist[found]++;
      total_min_cores += (long long)cores.size();
      for (uint32_t core : cores) {
        string canon = canonical_g6_small(g, core);
        string sig = "size=" + to_string(found) + " m=" + to_string(edges(g, core)) +
                     " deg=" + degseq(g, core) + " vc=" +
                     (vertex_critical_core(g, core) ? "1" : "0");
        if (!canon.empty()) sig += " canon=" + canon;
        core_sig_hist[sig]++;
        if (examples[sig].size() < 3) examples[sig].insert(g6);
      }
    }
    failed_vertices_by_graph[graph_failures]++;
    if (graphs % 1000 == 0) {
      cerr << "processed " << graphs << " graphs, failed_deletions="
           << failed_deletions << "\n";
    }
  }

  cout << "graphs=" << graphs << "\n";
  cout << "failed_vertices_by_graph";
  for (auto [k, v] : failed_vertices_by_graph) cout << " [" << k << "]=" << v;
  cout << "\n";
  cout << "failed_deletions=" << failed_deletions << "\n";
  cout << "min_size_hist";
  for (auto [k, v] : min_size_hist) cout << " [" << k << "]=" << v;
  cout << "\n";
  cout << "total_min_cores=" << total_min_cores << "\n";
  cout << "core_signature_hist\n";
  for (auto& [sig, c] : core_sig_hist) {
    cout << c << " :: " << sig << " examples";
    for (auto& ex : examples[sig]) cout << " " << ex;
    cout << "\n";
  }
  return 0;
}
