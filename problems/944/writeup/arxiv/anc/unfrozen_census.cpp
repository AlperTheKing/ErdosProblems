// Exhaustive deletion-unfrozen census over 6-regular 3-colourable graphs.
// v UNFROZEN <=> G-v has a proper 3-colouring with N(v) colour counts (2,2,2).
// Feeds the (FK) frozen-kernel frontier: any graph with ALL vertices unfrozen
// refutes the reduced kernel.
// usage: unfrozen_census.exe N < g6_lines     (geng -d6 -D6 N output)
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
// does G-v admit a proper 3-colouring with N(v) colour counts exactly (2,2,2)?
// backtracking with N(v) first; prune any colour used >2 times on N(v);
// symmetry: first vertex fixed to colour 0.
static bool unfrozen(const G& g, int v) {
  int idx[MAXN], m = 0;
  uint32_t nbv = g.adj[v];
  while (nbv) { int u = __builtin_ctz(nbv); nbv &= nbv - 1; idx[m++] = u; }
  int nN = m;                       // 6 neighbours first
  for (int u = 0; u < N; u++) if (u != v && !((g.adj[v] >> u) & 1)) idx[m++] = u;
  // sort the non-neighbour tail by degree desc (helps pruning)
  for (int i = nN + 1; i < m; i++) { int k = idx[i], j = i - 1;
    while (j >= nN && g.deg(idx[j]) < g.deg(k)) { idx[j+1] = idx[j]; j--; } idx[j+1] = k; }
  int8_t color[MAXN]; memset(color, -1, sizeof(color));
  int cnt[3] = {0, 0, 0};
  int pos = 0; int8_t tryc[MAXN]; memset(tryc, 0, sizeof(tryc));
  while (pos >= 0) {
    if (pos == m) return true;      // all 6 nbrs placed with cnt<=2 each => (2,2,2)
    int x = idx[pos]; bool adv = false;
    int cmax = (pos == 0) ? 1 : 3;  // symmetry: first vertex colour 0 only
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
  long long total = 0, threecol = 0, badline = 0, fully = 0;
  long long hist[MAXN + 1]; memset(hist, 0, sizeof(hist));
  int maxUnfrozen = 0;
  while (getline(cin, line)) {
    while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
    if (line.empty() || line[0] == '>') continue;
    G g;
    if (!g6decode(line, g)) { badline++; continue; }
    total++;
    bool oddnbhd = false;           // wheel => chi >= 4 => not 3-colourable
    for (int v = 0; v < N && !oddnbhd; v++)
      if (!induced_bipartite(g, g.adj[v])) oddnbhd = true;
    if (oddnbhd) continue;
    if (!col3(g, 0)) continue;
    threecol++;
    int k = 0; uint32_t uset = 0;
    for (int v = 0; v < N; v++)
      if (unfrozen(g, v)) { k++; uset |= 1u << v; }
    hist[k]++;
    if (k > maxUnfrozen) maxUnfrozen = k;
    if (k == N) { fully++; printf("FULLY_UNFROZEN_G6: %s\n", line.c_str()); fflush(stdout); }
    else if (k >= 3) { printf("HIGH_UNFROZEN_G6: %s k=%d set=%u\n", line.c_str(), k, uset); fflush(stdout); }
  }
  printf("total=%lld threecol=%lld maxUnfrozen=%d fullyUnfrozen=%lld badline=%lld hist:", total, threecol, maxUnfrozen, fully, badline);
  for (int i = 0; i <= N; i++) if (hist[i]) printf(" %d:%lld", i, hist[i]);
  printf("\n");
  return 0;
}
