// Descent-core hunt 3 (2026-06-13): GENERALIZED merge count. Quotient size B+1 from a
// k-merge of a size-(B+k) shore (forced-equal class of size k contracted to one apex vertex).
// Completes the feasible descent census across merge counts: quotient sizes 12,11,10,9
// (base B = 11,10,9,8) on top of single-merge n=14 (B=13) and triple-merge n=13 (B=12).
//   Base L' = quotient minus apex: B-vertex graph, Delta<=6, g6 on stdin (geng -c -D6 B).
//   apex u = vertex B, adjacent to S subset of {deg<=5 base vertices}, |S| = apex degree.
//   Accept iff base vertices stay <=6 and residual base deficiency D' in [DMIN,DMAX].
//   P1: L'[S] bipartite; P2: chi>=4; P3: every (quotient)-x 3-colourable. P3 hits = candidates.
// Usage: core_hunt3 <baseSize B> <apexDeg 7..B | all> [DMAX=8] [DMIN=0]
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
using namespace std;

static const int MAXN = 14;

struct G {
  int n = 0;
  uint16_t adj[MAXN] = {};
  void addEdge(int a, int b) { adj[a] |= 1 << b; adj[b] |= 1 << a; }
  int deg(int x) const { return __builtin_popcount(adj[x]); }
};

static bool g6decode(const char* s, G& g, int expectN) {
  int n = s[0] - 63;
  if (n != expectN) return false;
  g = G(); g.n = n;
  int bit = 0;
  for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
    int byte = 1 + bit / 6, off = 5 - bit % 6;
    if (((s[byte] - 63) >> off) & 1) g.addEdge(i, j);
    bit++;
  }
  return true;
}

static bool bipartiteSubset(const G& g, uint16_t S) {
  int side[MAXN]; memset(side, -1, sizeof(side));
  for (int s0 = 0; s0 < g.n; s0++) {
    if (!(S >> s0 & 1) || side[s0] >= 0) continue;
    side[s0] = 0;
    int st[MAXN], sp = 0; st[sp++] = s0;
    while (sp) { int x = st[--sp];
      uint16_t nb = g.adj[x] & S;
      while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
        if (side[u] < 0) { side[u] = side[x] ^ 1; st[sp++] = u; }
        else if (side[u] == side[x]) return false; } }
  }
  return true;
}

struct Solver {
  const G* g; int del;
  uint8_t dom[MAXN]; int8_t col[MAXN];
  pair<int,uint8_t> trail[MAXN * 12]; int tp = 0;
  bool shrink(int u, uint8_t bit) {
    if (!(dom[u] & bit)) return true;
    trail[tp++] = {u, dom[u]};
    dom[u] &= ~bit;
    return dom[u] != 0;
  }
  bool solve() {
    int x = -1, best = 4;
    for (int u = 0; u < g->n; u++)
      if (u != del && col[u] < 0) { int p = __builtin_popcount(dom[u]);
        if (p < best) { best = p; x = u; if (p <= 1) break; } }
    if (x < 0) return true;
    for (int c = 0; c < 3; c++) {
      if (!(dom[x] >> c & 1)) continue;
      bool ok = true;
      int mark = tp;
      col[x] = c;
      uint16_t nb = g->adj[x];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
        if (u != del && col[u] < 0 && !shrink(u, 1 << c)) { ok = false; break; } }
      if (ok && solve()) return true;
      while (tp > mark) { dom[trail[tp-1].first] = trail[tp-1].second; tp--; }
      col[x] = -1;
    }
    return false;
  }
};

static bool threeColourable(const G& g, int del) {
  Solver s; s.g = &g; s.del = del; s.tp = 0;
  memset(s.col, -1, sizeof(s.col));
  for (int u = 0; u < g.n; u++) s.dom[u] = 7;
  return s.solve();
}

static long long nRead = 0, nL = 0, nApex = 0, p1 = 0, p2cnt = 0, p3 = 0;
static int BASE = 0, APEXDEG = 0, DMAX = 8, DMIN = 0;

static void testApex(const char* line, const G& L, uint16_t S) {
  nApex++;
  if (!bipartiteSubset(L, S)) return;
  p1++;
  G M = L; M.n = BASE + 1;
  uint16_t SS = S;
  while (SS) { int v = __builtin_ctz(SS); SS &= SS - 1; M.addEdge(BASE, v); }
  if (threeColourable(M, -1)) return;
  p2cnt++;
  for (int x = 0; x <= BASE; x++)
    if (!threeColourable(M, x)) {
      printf("CHI4-NONCRIT %s S=%04x\n", line, S);
      return;
    }
  p3++;
  printf("** MERGE DESCENT-CORE CANDIDATE ** base=%d %s deg=%d S=%04x\n", BASE, line, APEXDEG, S);
  fflush(stdout);
}

int idx[16];
static void enumerate(const char* line, const G& L, const int* low, int nlow) {
  for (int i = 0; i < APEXDEG; i++) idx[i] = i;
  for (;;) {
    uint16_t S = 0;
    for (int i = 0; i < APEXDEG; i++) S |= 1 << low[idx[i]];
    int defM = 0; bool ok = true;
    for (int x = 0; x < BASE && ok; x++) {
      int dM = L.deg(x) + ((S >> x & 1) ? 1 : 0);
      if (dM > 6) ok = false; else defM += 6 - dM;
    }
    if (ok && defM >= DMIN && defM <= DMAX) testApex(line, L, S);
    int i = APEXDEG - 1;
    while (i >= 0 && idx[i] == nlow - APEXDEG + i) i--;
    if (i < 0) break;
    idx[i]++;
    for (int j = i + 1; j < APEXDEG; j++) idx[j] = idx[j-1] + 1;
  }
}

int main(int argc, char** argv) {
  if (argc < 3) { fprintf(stderr, "usage: core_hunt3 <baseSize> <apexDeg|all> [DMAX=8] [DMIN=0]\n"); return 1; }
  BASE = atoi(argv[1]);
  bool allMode = string(argv[2]) == "all";
  if (!allMode) APEXDEG = atoi(argv[2]);
  if (argc > 3) DMAX = atoi(argv[3]);
  if (argc > 4) DMIN = atoi(argv[4]);
  char line[64];
  while (fgets(line, sizeof(line), stdin)) {
    if (line[0] == '>' || line[0] == '\n') continue;
    line[strcspn(line, "\r\n")] = 0;
    G L;
    if (!g6decode(line, L, BASE)) continue;
    nRead++;
    int low[14], nlow = 0; bool bad = false;
    for (int x = 0; x < BASE; x++) { int d = L.deg(x);
      if (d > 6) { bad = true; break; }
      if (d <= 5) low[nlow++] = x; }
    if (bad) continue;
    if (allMode) {
      bool used = false;
      for (int N = 7; N <= BASE && N <= nlow; N++) { APEXDEG = N; used = true; enumerate(line, L, low, nlow); }
      if (used) nL++;
    } else {
      if (nlow < APEXDEG) continue;
      nL++;
      enumerate(line, L, low, nlow);
    }
  }
  fprintf(stderr, "base=%d read=%lld bases=%lld apexings=%lld P1pass=%lld P2pass=%lld P3pass=%lld\n",
          BASE, nRead, nL, nApex, p1, p2cnt, p3);
  return 0;
}
