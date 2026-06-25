// Diagnostic for the (FK) route: on every 3-colourable 6-regular graph, compare
// the cheap local necessary condition (filter 5: complement of H[N(v)] has a
// perfect matching) with true unfrozenness (exists 3-colouring of G-v with N(v)
// counts (2,2,2)). High f5-pass rate + tiny unfrozen rate => the binding
// constraint is GLOBAL extension, not local neighbourhood structure.
// Also exhaustively re-verifies: unfrozen => f5 (any violation printed).
// usage: pm_stats.exe N < g6_lines
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <iostream>
using namespace std;
static int N;
static const int MAXN = 32;
struct G {
  uint32_t adj[MAXN];
  void add(int u, int v) { adj[u] |= 1u << v; adj[v] |= 1u << u; }
  int deg(int u) const { return __builtin_popcount(adj[u]); }
};
static bool col3(const G& g, uint32_t rm) {
  int idx[MAXN], m = 0;
  for (int v = 0; v < N; v++) if (!((rm >> v) & 1)) idx[m++] = v;
  for (int i = 1; i < m; i++) { int k = idx[i], j = i - 1;
    while (j >= 0 && g.deg(idx[j]) < g.deg(k)) { idx[j+1] = idx[j]; j--; } idx[j+1] = k; }
  int8_t color[MAXN]; memset(color, -1, sizeof(color));
  int pos = 0; int8_t tryc[MAXN]; memset(tryc, 0, sizeof(tryc));
  while (pos >= 0) {
    if (pos == m) return true;
    int v = idx[pos]; bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      bool ok = true; uint32_t nb = g.adj[v];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
        if ((rm >> u) & 1) continue;
        if (color[u] == c) { ok = false; break; } }
      if (ok) { color[v] = c; tryc[pos] = c + 1; pos++; if (pos < m) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { color[v] = -1; tryc[pos] = 0; pos--; }
  }
  return false;
}
static bool induced_bipartite(const G& g, uint32_t mask) {
  int8_t side[MAXN]; uint32_t left = mask;
  while (left) {
    int s = __builtin_ctz(left);
    side[s] = 0; uint32_t qmask = 1u << s; left &= ~(1u << s);
    uint32_t stack = 1u << s;
    while (stack) {
      int x = __builtin_ctz(stack); stack &= stack - 1;
      uint32_t nb = g.adj[x] & mask;
      while (nb) {
        int y = __builtin_ctz(nb); nb &= nb - 1;
        if (qmask >> y & 1) { if (side[y] == side[x]) return false; }
        else { side[y] = 1 - side[x]; qmask |= 1u << y; stack |= 1u << y; left &= ~(1u << y); }
      }
    }
  }
  return true;
}
static bool unfrozen(const G& g, int v) {
  int idx[MAXN], m = 0;
  uint32_t nbv = g.adj[v];
  while (nbv) { int u = __builtin_ctz(nbv); nbv &= nbv - 1; idx[m++] = u; }
  int nN = m;
  for (int u = 0; u < N; u++) if (u != v && !((g.adj[v] >> u) & 1)) idx[m++] = u;
  for (int i = nN + 1; i < m; i++) { int k = idx[i], j = i - 1;
    while (j >= nN && g.deg(idx[j]) < g.deg(k)) { idx[j+1] = idx[j]; j--; } idx[j+1] = k; }
  int8_t color[MAXN]; memset(color, -1, sizeof(color));
  int cnt[3] = {0, 0, 0};
  int pos = 0; int8_t tryc[MAXN]; memset(tryc, 0, sizeof(tryc));
  while (pos >= 0) {
    if (pos == m) return true;
    int x = idx[pos]; bool adv = false;
    int cmax = (pos == 0) ? 1 : 3;
    for (int c = tryc[pos]; c < cmax; c++) {
      if (pos < nN && cnt[c] >= 2) continue;
      bool ok = true; uint32_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
        if (u == v) continue;
        if (color[u] == c) { ok = false; break; } }
      if (ok) { color[x] = c; if (pos < nN) cnt[c]++;
        tryc[pos] = c + 1; pos++; if (pos < m) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { color[x] = -1; tryc[pos] = 0; pos--;
      if (pos >= 0) { int y = idx[pos]; if (pos < nN) cnt[color[y]]--; color[y] = -1; } }
  }
  return false;
}
// complement of induced N(v) (6 vertices) has a perfect matching?
static bool f5(const G& g, int v) {
  int nv[6], k = 0;
  uint32_t nb = g.adj[v];
  while (nb) { nv[k++] = __builtin_ctz(nb); nb &= nb - 1; }
  // brute force over the 15 pairings of 6 elements
  static const int P[15][6] = {
    {0,1,2,3,4,5},{0,1,2,4,3,5},{0,1,2,5,3,4},
    {0,2,1,3,4,5},{0,2,1,4,3,5},{0,2,1,5,3,4},
    {0,3,1,2,4,5},{0,3,1,4,2,5},{0,3,1,5,2,4},
    {0,4,1,2,3,5},{0,4,1,3,2,5},{0,4,1,5,2,3},
    {0,5,1,2,3,4},{0,5,1,3,2,4},{0,5,1,4,2,3}};
  for (int p = 0; p < 15; p++) {
    bool ok = true;
    for (int q = 0; q < 6 && ok; q += 2) {
      int a = nv[P[p][q]], b = nv[P[p][q+1]];
      if ((g.adj[a] >> b) & 1) ok = false;
    }
    if (ok) return true;
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
  for (int j = 1; j < n; j++)
    for (int i = 0; i < j; i++) {
      int byte = 1 + bit / 6, off = 5 - bit % 6;
      if ((line[byte] - 63) >> off & 1) g.add(i, j);
      bit++;
    }
  return true;
}
int main(int argc, char** argv) {
  N = argc > 1 ? atoi(argv[1]) : 14;
  string line;
  long long total = 0, threecol = 0, badline = 0;
  long long vTotal = 0, vF5 = 0, vUnf = 0, viol = 0;
  long long allF5 = 0;   // graphs where EVERY vertex passes filter 5
  while (getline(cin, line)) {
    while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
    if (line.empty() || line[0] == '>') continue;
    G g;
    if (!g6decode(line, g)) { badline++; continue; }
    total++;
    bool oddnbhd = false;
    for (int v = 0; v < N && !oddnbhd; v++)
      if (!induced_bipartite(g, g.adj[v])) oddnbhd = true;
    if (oddnbhd) continue;
    if (!col3(g, 0)) continue;
    threecol++;
    int f5cnt = 0;
    for (int v = 0; v < N; v++) {
      vTotal++;
      bool p5 = f5(g, v);
      bool unf = unfrozen(g, v);
      if (p5) { vF5++; f5cnt++; }
      if (unf) { vUnf++;
        if (!p5) { viol++; printf("I4_VIOLATION_G6: %s v=%d\n", line.c_str(), v); fflush(stdout); } }
    }
    if (f5cnt == N) allF5++;
  }
  printf("total=%lld threecol=%lld verts=%lld f5pass=%lld unfrozen=%lld I4viol=%lld allF5graphs=%lld badline=%lld\n",
         total, threecol, vTotal, vF5, vUnf, viol, allF5, badline);
  return 0;
}
