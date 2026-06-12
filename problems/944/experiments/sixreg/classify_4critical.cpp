// Classify small graph6 streams by 4-criticality.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <functional>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using namespace std;

static constexpr int MAXN = 32;
static int N;

struct G {
  uint32_t adj[MAXN]{};
  void add(int u, int v) { adj[u] |= 1u << v; adj[v] |= 1u << u; }
  int deg_in(int u, uint32_t mask) const { return __builtin_popcount(adj[u] & mask); }
};

static bool decode(const string& line, G& g) {
  if (line.empty() || line[0] == '>') return false;
  int n = line[0] - 63;
  if (n <= 0 || n > MAXN) return false;
  N = n;
  memset(g.adj, 0, sizeof(g.adj));
  int nbits = n * (n - 1) / 2, need = (nbits + 5) / 6;
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
  for (int v = 0; v < N; v++) if ((mask >> v) & 1u) verts.push_back(v);
  sort(verts.begin(), verts.end(), [&](int a, int b) {
    return g.deg_in(a, mask) > g.deg_in(b, mask);
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

static string degree_sequence(const G& g, uint32_t mask) {
  vector<int> ds;
  for (int v = 0; v < N; v++) if ((mask >> v) & 1u) ds.push_back(g.deg_in(v, mask));
  sort(ds.begin(), ds.end());
  string s;
  for (size_t i = 0; i < ds.size(); i++) {
    if (i) s += ",";
    s += to_string(ds[i]);
  }
  return s;
}

int main() {
  string line;
  long long total = 0, crit4 = 0;
  map<string, long long> by_sig;
  while (getline(cin, line)) {
    while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
    G g;
    if (!decode(line, g)) continue;
    total++;
    uint32_t full = (N == 32 ? 0xffffffffu : ((1u << N) - 1u));
    if (col3(g, full)) continue;
    bool vc = true;
    for (int v = 0; v < N; v++) {
      if (!col3(g, full & ~(1u << v))) {
        vc = false;
        break;
      }
    }
    if (!vc) continue;
    int m = 0;
    for (int v = 0; v < N; v++) m += __builtin_popcount(g.adj[v]);
    m /= 2;
    string sig = "m=" + to_string(m) + " deg=" + degree_sequence(g, full);
    by_sig[sig]++;
    crit4++;
    cout << "FOUR_CRITICAL " << sig << " G6: " << line << "\n";
  }
  cout << "total=" << total << " fourCritical=" << crit4 << "\n";
  cout << "signatures";
  for (auto& [sig, c] : by_sig) cout << " [" << sig << "]=" << c;
  cout << "\n";
  return 0;
}
