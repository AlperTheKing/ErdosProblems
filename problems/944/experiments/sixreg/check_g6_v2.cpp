// v2 graph6 classifier for the 6-regular (4,1)-graph hunt, with the
// neighbourhood-bipartiteness prefilter:
//   In a 4-vertex-critical graph on n >= 8 vertices, every induced neighbourhood
//   G[N(v)] is bipartite (an odd cycle C in N(v) gives the 4-chromatic wheel
//   v+C on <= 7 vertices; any u outside it has chi(G-u) >= 4, contradicting
//   vertex-criticality). Graphs failing the test are notVC; they are also never
//   3-colourable-misclassified (a wheel forces chi >= 4), so counters remain
//   comparable with check_g6.cpp.
// usage: check_g6_v2.exe N < g6_lines
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
static bool col3(const G& g, uint32_t rm, int eu = -1, int ev = -1) {
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
        if (eu >= 0 && ((u == eu && v == ev) || (u == ev && v == eu))) continue;
        if (color[u] == c) { ok = false; break; } }
      if (ok) { color[v] = c; tryc[pos] = c + 1; pos++; if (pos < m) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { color[v] = -1; tryc[pos] = 0; pos--; }
  }
  return false;
}
// is the induced graph on vertex set 'mask' bipartite? (mask has <= 8 bits here)
static bool induced_bipartite(const G& g, uint32_t mask) {
  int8_t side[MAXN]; uint32_t left = mask;
  while (left) {
    int s = __builtin_ctz(left);
    // BFS from s
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
  N = argc > 1 ? atoi(argv[1]) : 15;
  string line;
  long long total = 0, prefilt = 0, c3 = 0, notvc = 0, vccrit = 0, target = 0, badline = 0;
  while (getline(cin, line)) {
    while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
    if (line.empty() || line[0] == '>') continue;
    G g;
    if (!g6decode(line, g)) { badline++; continue; }
    total++;
    if (total % 1000000 == 0) {
      fprintf(stderr, "PROGRESS total=%lld nbhdOdd=%lld threecol=%lld notVC=%lld vcWithCritEdge=%lld TARGET=%lld\n",
              total, prefilt, c3, notvc, vccrit, target);
      fflush(stderr);
    }
    bool oddnbhd = false;
    for (int v = 0; v < N && !oddnbhd; v++)
      if (!induced_bipartite(g, g.adj[v])) oddnbhd = true;
    if (oddnbhd) { prefilt++; continue; }   // notVC (wheel); counted separately
    if (col3(g, 0)) { c3++; continue; }
    bool vc = true;
    for (int v = 0; v < N && vc; v++) if (!col3(g, 1u << v)) vc = false;
    if (!vc) { notvc++; continue; }
    bool crit = false;
    for (int u = 0; u < N && !crit; u++) { uint32_t nb = g.adj[u];
      while (nb) { int v = __builtin_ctz(nb); nb &= nb - 1; if (v < u) continue;
        if (col3(g, 0, u, v)) { crit = true; break; } } }
    if (crit) { vccrit++; printf("VC_WITH_CRIT_G6: %s\n", line.c_str()); fflush(stdout); }
    else { target++; printf("TARGET_G6: %s\n", line.c_str()); fflush(stdout); }
  }
  printf("total=%lld nbhdOdd=%lld threecol=%lld notVC=%lld vcWithCritEdge=%lld TARGET=%lld badline=%lld\n",
         total, prefilt, c3, notvc, vccrit, target, badline);
  return 0;
}
