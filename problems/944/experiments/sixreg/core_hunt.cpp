// Descent-core hunt, profile 1 (2026-06-13): M = apex(8) over base L, target
// M-profile {8, 5, 5, 6^11} on n=14 — candidate 4-vertex-critical quotient cores
// of hypothetical trace-hypo-rigid shores (see PROOF_STATE 00:55/01:18).
// Base class: n=13, degrees {5^10, 6^3} (forced by d5:D6 e=34), 41,386,386 graphs.
// For each base L (g6 on stdin) and each S = 8 of the ten degree-5 vertices
// (C(10,8)=45): M = L + apex u adjacent to S. Tests in order:
//   P1: L[S] bipartite (4-VC => every neighbourhood induces bipartite; N(u)=S)
//   P2: chi(M) >= 4 (no proper 3-colouring; MRV+FC exhaustive)
//   P3: criticality: for every x, M - x is 3-colourable
// Survivors of P2 are logged (RARE); P3 survivors = DESCENT-CORE CANDIDATES.
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
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
  int nbits = n * (n - 1) / 2, bit = 0;
  for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
    int byte = 1 + bit / 6, off = 5 - bit % 6;
    if (((s[byte] - 63) >> off) & 1) g.addEdge(i, j);
    bit++;
  }
  (void)nbits;
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

// MRV+FC: exists proper 3-colouring of g minus del (-1 = none)?
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

static long long nL = 0, nRead = 0, nApex = 0, p1 = 0, p2cnt = 0, p3 = 0;

static void testApex(const char* line, const G& L, uint16_t S) {
  nApex++;
  if (!bipartiteSubset(L, S)) return;
  p1++;
  G M = L; M.n = 14;
  uint16_t SS = S;
  while (SS) { int v = __builtin_ctz(SS); SS &= SS - 1; M.addEdge(13, v); }
  if (threeColourable(M, -1)) return;
  p2cnt++;
  for (int x = 0; x < 14; x++)
    if (!threeColourable(M, x)) {
      printf("CHI4-NONCRIT %s S=%04x\n", line, S);
      return;
    }
  p3++;
  printf("** DESCENT-CORE CANDIDATE ** %s S=%04x\n", line, S);
  fflush(stdout);
}

int main(int argc, char** argv) {
  bool prof2 = argc > 1 && string(argv[1]) == "p2";
  int argcMode = (argc > 1 && string(argv[1]) == "p2b") ? 3
               : (argc > 1 && string(argv[1]) == "p3") ? 10
               : (argc > 1 && string(argv[1]) == "p7") ? 7
               : (argc > 1 && string(argv[1]) == "p9") ? 9 : 0;
  char line[64];
  while (fgets(line, sizeof(line), stdin)) {
    if (line[0] == '>' || line[0] == '\n') continue;
    line[strcspn(line, "\r\n")] = 0;
    G L;
    if (!g6decode(line, L, 13)) continue;
    nRead++;
    if (prof2) {
      // profile 2a: base {4, 5^8, 6^4}; S forced = the eight degree-5 vertices
      int c4 = 0, c5 = 0, c6 = 0; uint16_t S = 0;
      for (int x = 0; x < 13; x++) { int d = L.deg(x);
        if (d == 4) c4++; else if (d == 5) { c5++; S |= 1 << x; } else if (d == 6) c6++; }
      if (c4 != 1 || c5 != 8 || c6 != 4) continue;
      nL++;
      testApex(line, L, S);
    } else if (argcMode == 3) {
      // profile 2b: base {3, 5^7, 6^5}; S forced = the deg-3 vertex + seven deg-5's
      int c3 = 0, c5 = 0, c6 = 0; uint16_t S = 0;
      for (int x = 0; x < 13; x++) { int d = L.deg(x);
        if (d == 3) { c3++; S |= 1 << x; }
        else if (d == 5) { c5++; S |= 1 << x; }
        else if (d == 6) c6++; }
      if (c3 != 1 || c5 != 7 || c6 != 5) continue;
      nL++;
      testApex(line, L, S);
    } else if (argcMode == 7) {
      // profile d_u=7 ({7,5,6^12}, base e=35):
      // case A base {5^8,6^5}: S = 7 of the eight 5's (8 ways)
      // case B base {4,5^6,6^6}: S = the 4 + all six 5's (forced)
      int c4 = 0, c5 = 0, c6 = 0; int v5[13], n5i = 0; int v4 = -1;
      for (int x = 0; x < 13; x++) { int d = L.deg(x);
        if (d == 4) { c4++; v4 = x; }
        else if (d == 5) { c5++; v5[n5i++] = x; }
        else if (d == 6) c6++; }
      if (c4 == 0 && c5 == 8 && c6 == 5) {
        nL++;
        for (int omit = 0; omit < 8; omit++) {
          uint16_t S = 0;
          for (int k = 0; k < 8; k++) if (k != omit) S |= 1 << v5[k];
          testApex(line, L, S);
        }
      } else if (c4 == 1 && c5 == 6 && c6 == 6) {
        nL++;
        uint16_t S = 1 << v4;
        for (int k = 0; k < 6; k++) S |= 1 << v5[k];
        testApex(line, L, S);
      }
    } else if (argcMode == 9) {
      // profile d_u=9 (base e=33), residual deficiency 3 on the quotient:
      // M-profiles {9,5^3,6^10} / {9,4,5,6^10}(n=14:1+1+1+11? recount below) / {9,3,6^11}
      // S = N(u), |S| = 9; deg-6 base vertices cannot be in S... M-deg of S-members
      // <= 6 => deg_L <= 5 inside S; outside S deg_M = deg_L. Enumerate S over
      // subsets of {deg<=5 vertices} of size 9 and accept iff resulting M-profile
      // has one 9, rest {5,6} or {4,5,6}/{3,6} with total deficiency 3.
      int low[13], nlow = 0; uint16_t six = 0;
      bool bad = false;
      for (int x = 0; x < 13; x++) { int d = L.deg(x);
        if (d >= 3 && d <= 5) low[nlow++] = x;
        else if (d == 6) six |= 1 << x;
        else { bad = true; break; } }
      if (bad || nlow < 9) continue;
      nL++;
      // choose 9 of the nlow low vertices for S (nlow <= 13; C(nlow,9) small)
      int idx[9];
      for (int i = 0; i < 9; i++) idx[i] = i;
      for (;;) {
        uint16_t S = 0;
        for (int i = 0; i < 9; i++) S |= 1 << low[idx[i]];
        // M-profile check: deficiency of M = sum over x != u of (6 - deg_M(x)) == 3
        int defM = 0; bool ok = true;
        for (int x = 0; x < 13 && ok; x++) {
          int dM = L.deg(x) + ((S >> x & 1) ? 1 : 0);
          if (dM > 6) ok = false; else defM += 6 - dM;
        }
        if (ok && defM == 3) testApex(line, L, S);
        // next combination
        int i = 8;
        while (i >= 0 && idx[i] == nlow - 9 + i) i--;
        if (i < 0) break;
        idx[i]++;
        for (int j = i + 1; j < 9; j++) idx[j] = idx[j-1] + 1;
      }
    } else if (argcMode == 10) {
      // profile 3 ({10,5^4,6^9}, apex degree 10, base e=32): every deg-6 base
      // vertex must be OUTSIDE S (else deg 7); non-S = the deg-6 set + enough
      // deg-5 vertices to make 3; S = the rest (deg-4's all inside).
      int c4 = 0, c5 = 0, c6 = 0; int v5[13], n5i = 0; uint16_t six = 0, all = (1 << 13) - 1;
      for (int x = 0; x < 13; x++) { int d = L.deg(x);
        if (d == 4) c4++;
        else if (d == 5) { c5++; v5[n5i++] = x; }
        else if (d == 6) { c6++; six |= 1 << x; }
        else { c4 = -99; break; } }                      // deg<4 impossible (d4 bound) but guard
      if (c4 < 0 || c6 > 3 || c4 + c5 + c6 != 13) continue;
      nL++;
      int need5out = 3 - c6;
      if (need5out < 0 || need5out > c5) continue;
      // choose need5out of the deg-5 vertices to sit outside S
      if (need5out == 0) testApex(line, L, all & ~six);
      else if (need5out == 1) {
        for (int i = 0; i < n5i; i++) testApex(line, L, all & ~six & ~(1 << v5[i]));
      } else if (need5out == 2) {
        for (int i = 0; i < n5i; i++) for (int j = i + 1; j < n5i; j++)
          testApex(line, L, all & ~six & ~(1 << v5[i]) & ~(1 << v5[j]));
      } else {
        for (int i = 0; i < n5i; i++) for (int j = i + 1; j < n5i; j++) for (int k = j + 1; k < n5i; k++)
          testApex(line, L, all & ~six & ~(1 << v5[i]) & ~(1 << v5[j]) & ~(1 << v5[k]));
      }
    } else {
      // profile 1: base {5^10, 6^3}; S = 8 of the ten degree-5 vertices (45 ways)
      nL++;
      int d5[10], n5 = 0;
      for (int x = 0; x < 13; x++) if (L.deg(x) == 5) { if (n5 < 10) d5[n5] = x; n5++; }
      if (n5 != 10) continue;
      for (int i = 0; i < 10; i++) for (int j = i + 1; j < 10; j++) {
        uint16_t S = 0;
        for (int k = 0; k < 10; k++) if (k != i && k != j) S |= 1 << d5[k];
        testApex(line, L, S);
      }
    }
  }
  fprintf(stderr, "read=%lld bases=%lld apexings=%lld P1pass=%lld P2pass=%lld P3pass=%lld\n",
          nRead, nL, nApex, p1, p2cnt, p3);
  return 0;
}
