// Classify graph6 streams by 3-colourability, no-critical-edge property, and
// vertex-critical failures. Useful for finding construction seeds that already
// satisfy "no critical edge" but fail vertex-criticality.
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <map>
#include <string>
using namespace std;

static int N;
static constexpr int MAXN = 32;

struct G {
  uint32_t adj[MAXN]{};
  void add(int u, int v) { adj[u] |= 1u << v; adj[v] |= 1u << u; }
  int deg(int u) const { return __builtin_popcount(adj[u]); }
};

static bool col3(const G& g, uint32_t rm, int eu = -1, int ev = -1) {
  int idx[MAXN], m = 0;
  for (int v = 0; v < N; v++) if (!((rm >> v) & 1u)) idx[m++] = v;
  for (int i = 1; i < m; i++) {
    int k = idx[i], j = i - 1;
    while (j >= 0 && g.deg(idx[j]) < g.deg(k)) { idx[j + 1] = idx[j]; j--; }
    idx[j + 1] = k;
  }
  int8_t color[MAXN];
  int8_t tryc[MAXN];
  memset(color, -1, sizeof(color));
  memset(tryc, 0, sizeof(tryc));
  int pos = 0;
  while (pos >= 0) {
    if (pos == m) return true;
    int v = idx[pos];
    bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      bool ok = true;
      uint32_t nb = g.adj[v];
      while (nb) {
        int u = __builtin_ctz(nb);
        nb &= nb - 1;
        if ((rm >> u) & 1u) continue;
        if (eu >= 0 && ((u == eu && v == ev) || (u == ev && v == eu))) continue;
        if (color[u] == c) { ok = false; break; }
      }
      if (ok) {
        color[v] = (int8_t)c;
        tryc[pos] = (int8_t)(c + 1);
        pos++;
        if (pos < m) tryc[pos] = 0;
        adv = true;
        break;
      }
    }
    if (!adv) {
      color[v] = -1;
      tryc[pos] = 0;
      pos--;
    }
  }
  return false;
}

static bool g6decode(const string& line, G& g) {
  if (line.empty()) return false;
  int n = line[0] - 63;
  if (n != N) return false;
  memset(g.adj, 0, sizeof(g.adj));
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

int main(int argc, char** argv) {
  N = argc > 1 ? atoi(argv[1]) : 10;
  string line;
  long long total = 0, badline = 0, three = 0, four = 0, noCrit = 0, vcNoCrit = 0;
  map<int, long long> noCritByVertexFailures;
  while (getline(cin, line)) {
    while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
    if (line.empty() || line[0] == '>') continue;
    G g;
    if (!g6decode(line, g)) { badline++; continue; }
    total++;
    if (col3(g, 0)) { three++; continue; }
    four++;
    bool crit = false;
    for (int u = 0; u < N && !crit; u++) {
      uint32_t nb = g.adj[u];
      while (nb) {
        int v = __builtin_ctz(nb);
        nb &= nb - 1;
        if (v < u) continue;
        if (col3(g, 0, u, v)) { crit = true; break; }
      }
    }
    if (crit) continue;
    noCrit++;
    int vc_fail = 0;
    for (int v = 0; v < N; v++) if (!col3(g, 1u << v)) vc_fail++;
    noCritByVertexFailures[vc_fail]++;
    if (vc_fail == 0) {
      vcNoCrit++;
      cout << "TARGET_G6: " << line << "\n";
    } else {
      cout << "NOCRIT_NOTVC failures=" << vc_fail << " G6: " << line << "\n";
    }
  }
  cout << "total=" << total << " threecol=" << three << " fourchrom=" << four
       << " noCriticalEdge=" << noCrit << " vcNoCrit=" << vcNoCrit
       << " badline=" << badline << "\n";
  cout << "noCrit_vertex_failure_hist";
  for (auto [k, v] : noCritByVertexFailures) cout << " [" << k << "]=" << v;
  cout << "\n";
  return 0;
}
