// Enumerate candidate 9-vertex shores of a nontrivial 6-edge-cut in a 6-REGULAR
// (4,1)-graph (target), and filter by local necessary conditions:
//   [S] G[A]: 9 vertices, exactly 24 edges, Delta<=6, connected  (fed by geng)
//   [B] deficiency b(v) = 6 - deg(v) >= 0, sum = 6 (automatic), b(v) <= 5
//   [C] G[A] 3-colourable, and EVERY proper 3-colouring alpha has boundary vector
//       s_i = sum of b(v) over alpha-colour class i, with sorted (s1,s2,s3) in
//       {(6,0,0),(3,3,0),(4,1,1),(2,2,2)}   [Theorem 4.3 row-sum condition]
//   [T] no nonadjacent pair u,v with b(u)=0 and N(u) subseteq N(v)
//       [folklore: vertex-critical graphs have no comparable nonneighbours;
//        b(u)=0 makes N_G(u)=N_A(u) local]
// usage: enum_9shore.exe < g6_lines   (geng -c -D6 9 24:24)
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <iostream>
using namespace std;
static const int N = 9;
struct G { uint32_t adj[N]; int deg(int u) const { return __builtin_popcount(adj[u]); } };
static bool g6decode(const string& line, G& g) {
  if (line.empty() || line[0] - 63 != N) return false;
  memset(g.adj, 0, sizeof(g.adj));
  int bit = 0;
  for (int j = 1; j < N; j++)
    for (int i = 0; i < j; i++) {
      int byte = 1 + bit / 6, off = 5 - bit % 6;
      if ((int)line.size() <= byte) return false;
      if ((line[byte] - 63) >> off & 1) { g.adj[i] |= 1u << j; g.adj[j] |= 1u << i; }
      bit++;
    }
  return true;
}
static int b[N];
static const int ALLOWED[4][3] = {{6,0,0},{4,1,1},{3,3,0},{2,2,2}}; // sorted desc
static bool vec_allowed(int s0, int s1, int s2) {
  int v[3] = {s0, s1, s2};
  if (v[0] < v[1]) swap(v[0], v[1]);
  if (v[1] < v[2]) swap(v[1], v[2]);
  if (v[0] < v[1]) swap(v[0], v[1]);
  for (auto& a : ALLOWED)
    if (v[0]==a[0] && v[1]==a[1] && v[2]==a[2]) return true;
  return false;
}
// enumerate all proper 3-colourings; return false if none exists OR some colouring
// violates the boundary-vector condition; nCol returns count
static long long nColGlobal;
static bool colourings_ok(const G& g) {
  int8_t col[N];
  long long cnt = 0;
  bool ok = true;
  // iterative backtracking
  int pos = 0; int8_t tryc[N]; memset(tryc, 0, sizeof(tryc)); memset(col, -1, sizeof(col));
  while (pos >= 0) {
    if (pos == N) {
      cnt++;
      int s[3] = {0,0,0};
      for (int v = 0; v < N; v++) s[col[v]] += b[v];
      if (!vec_allowed(s[0], s[1], s[2])) { ok = false; break; }
      pos--; continue;
    }
    int v = pos; bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      bool fine = true; uint32_t nb = g.adj[v];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
        if (u < v && col[u] == c) { fine = false; break; } }
      if (fine) { col[v] = c; tryc[pos] = c + 1; pos++; if (pos < N) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { col[v] = -1; tryc[pos] = 0; pos--; }
  }
  nColGlobal = cnt;
  return ok && cnt > 0;
}
static bool twins_ok(const G& g) {
  for (int u = 0; u < N; u++) {
    if (b[u] != 0) continue;
    for (int v = 0; v < N; v++) {
      if (v == u || (g.adj[u] >> v & 1)) continue;
      // N(u) subseteq N(v) ?  (u's neighbourhood, excluding v itself, inside v's)
      uint32_t nu = g.adj[u] & ~(1u << v);
      if ((nu & ~g.adj[v]) == 0) return false; // comparable nonneighbours -> impossible
    }
  }
  return true;
}
int main() {
  string line;
  long long total = 0, badB = 0, no3col = 0, badvec = 0, badtwin = 0, survive = 0;
  while (getline(cin, line)) {
    while (!line.empty() && (line.back()=='\r' || line.back()=='\n')) line.pop_back();
    if (line.empty() || line[0] == '>') continue;
    G g;
    if (!g6decode(line, g)) continue;
    total++;
    bool okB = true;
    for (int v = 0; v < N; v++) { b[v] = 6 - g.deg(v); if (b[v] < 0 || b[v] > 5) okB = false; }
    if (!okB) { badB++; continue; }
    if (!colourings_ok(g)) {
      if (nColGlobal == 0) no3col++; else badvec++;
      continue;
    }
    if (!twins_ok(g)) { badtwin++; continue; }
    survive++;
    printf("SURVIVOR: %s  ncol=%lld  b=", line.c_str(), nColGlobal);
    for (int v = 0; v < N; v++) printf("%d", b[v]);
    printf("\n");
  }
  printf("total=%lld badDeficiency=%lld not3col=%lld badBoundaryVec=%lld comparableNonNbr=%lld SURVIVORS=%lld\n",
         total, badB, no3col, badvec, badtwin, survive);
  return 0;
}
