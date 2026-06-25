// Descent-core hunt 2 (2026-06-13): TRIPLE-CONTRACTION (two-merge) quotients on
// n=13 -- the multi-merge gap flagged by the coverage audit (PROOF_STATE ~07:05).
// A size-15 trace-hypo-rigid shore whose partner forces a 3-vertex colour class
// contracts a non-adjacent TRIPLE (15->14->13) to a 13-vertex 4-critical quotient
// with ONE merged (apex) vertex of degree d_u' and all other vertices <=6.
// This tool enumerates the NEAR-REGULAR sub-family (residual base deficiency D'<=DMAX),
// which is feasible and mirrors the validated single-merge core_hunt.cpp battery.
//   Base L' = M'-u: 12-vertex graph, Delta<=6, read as g6 on stdin (geng -c -D6 12).
//   apex u = vertex 12, adjacent to S subset of {deg<=5 base vertices}, |S| = d_u'.
//   Accept M' iff every base vertex stays <=6 and base deficiency D' = sum(6-deg_M') <= DMAX.
//   P1: L'[S] bipartite (4-VC => N(u) induces bipartite).
//   P2: chi(M') >= 4 (MRV+FC).
//   P3: criticality: for every x, M'-x is 3-colourable.  P3 survivors = CANDIDATES.
// Usage: core_hunt2 <apexDeg 7..11> [DMAX=4]
// HIGH-deficiency interior-triple profiles are NOT covered here (infeasible blanket;
// pending the GPT-pinned correspondence). Report covers exactly the enumerated profiles.
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
using namespace std;

static const int MAXN = 13;

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
static int APEXDEG = 0, DMAX = 4, DMIN = 0;

static void testApex(const char* line, const G& L, uint16_t S) {
  nApex++;
  if (!bipartiteSubset(L, S)) return;
  p1++;
  G M = L; M.n = 13;
  uint16_t SS = S;
  while (SS) { int v = __builtin_ctz(SS); SS &= SS - 1; M.addEdge(12, v); }
  if (threeColourable(M, -1)) return;
  p2cnt++;
  for (int x = 0; x < 13; x++)
    if (!threeColourable(M, x)) {
      printf("CHI4-NONCRIT %s S=%04x\n", line, S);
      return;
    }
  p3++;
  printf("** TRIPLE-MERGE DESCENT-CORE CANDIDATE ** %s deg=%d S=%04x\n", line, APEXDEG, S);
  fflush(stdout);
}

int idx[16];
static void enumerate(const char* line, const G& L, const int* low, int nlow) {
  // choose APEXDEG of the nlow low (deg<=5) vertices for S; require base def(M') <= DMAX
  for (int i = 0; i < APEXDEG; i++) idx[i] = i;
  for (;;) {
    uint16_t S = 0;
    for (int i = 0; i < APEXDEG; i++) S |= 1 << low[idx[i]];
    int defM = 0; bool ok = true;
    for (int x = 0; x < 12 && ok; x++) {
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
  if (argc < 2) { fprintf(stderr, "usage: core_hunt2 <apexDeg 7..11 | all> [DMAX=4] [DMIN=0]\n"); return 1; }
  bool allMode = string(argv[1]) == "all";
  if (!allMode) APEXDEG = atoi(argv[1]);
  if (argc > 2) DMAX = atoi(argv[2]);
  if (argc > 3) DMIN = atoi(argv[3]);
  char line[64];
  while (fgets(line, sizeof(line), stdin)) {
    if (line[0] == '>' || line[0] == '\n') continue;
    line[strcspn(line, "\r\n")] = 0;
    G L;
    if (!g6decode(line, L, 12)) continue;
    nRead++;
    int low[12], nlow = 0; bool bad = false;
    for (int x = 0; x < 12; x++) { int d = L.deg(x);
      if (d > 6) { bad = true; break; }
      if (d <= 5) low[nlow++] = x; }
    if (bad) continue;
    if (allMode) {
      bool used = false;
      for (int N = 7; N <= 11 && N <= nlow; N++) { APEXDEG = N; used = true; enumerate(line, L, low, nlow); }
      if (used) nL++;
    } else {
      if (nlow < APEXDEG) continue;
      nL++;
      enumerate(line, L, low, nlow);
    }
  }
  fprintf(stderr, "read=%lld bases=%lld apexings=%lld P1pass=%lld P2pass=%lld P3pass=%lld\n",
          nRead, nL, nApex, p1, p2cnt, p3);
  return 0;
}
