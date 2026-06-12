// General candidate-shore filter for nontrivial 6-edge-cut shores of size A_SIZE in a
// 6-REGULAR (4,1)-graph. Feed geng -c -D6 <a> E:E where E = 3a-3.
// Filters (all NECESSARY conditions for being a shore of a target):
//   [B]  b(v) = 6 - deg(v) in [0,5], sum b = 6 (automatic from edge count)
//   [C]  3-colourable AND every proper 3-colouring has boundary deficiency-vector
//        (sum of b over colour classes, sorted desc) in {(6,0,0),(4,1,1),(3,3,0),(2,2,2)}
//   [T]  no nonadjacent pair u,v with b(u)=0 and N(u) subseteq N(v)  [folklore]
//   [K]  for EVERY vertex v: there EXISTS a proper 3-colouring psi of H-v with
//        sum_i max(0, 2 - cnt_i) <= b(v), where cnt_i = # colour-i vertices in N_A(v).
//        (In a target chi(G-v)=3 gives such a psi: every colour needs >= 2 in N_G(v)
//         [Lemma 1.1 + no-critical-edge], and at most b(v) of those can be cut-neighbours.)
// usage: enum_shore.exe A_SIZE < g6_lines
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <iostream>
using namespace std;
static int N;
static const int MAXN = 16;
struct G { uint32_t adj[MAXN]; int deg(int u) const { return __builtin_popcount(adj[u]); } };
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
static int b[MAXN];
static const int ALLOWED[4][3] = {{6,0,0},{4,1,1},{3,3,0},{2,2,2}};
static bool vec_allowed(int v0, int v1, int v2) {
  int v[3] = {v0,v1,v2};
  if (v[0]<v[1]) swap(v[0],v[1]);
  if (v[1]<v[2]) swap(v[1],v[2]);
  if (v[0]<v[1]) swap(v[0],v[1]);
  for (auto& a : ALLOWED) if (v[0]==a[0] && v[1]==a[1] && v[2]==a[2]) return true;
  return false;
}
// enumerate proper 3-colourings of the graph restricted to vertices != skip (skip=-1: all);
// callback per colouring via lambda-ish: we inline the two uses instead.
static long long nCol;
// use: mode 0 = check boundary vectors on full graph (returns false on violation or no colouring)
static bool check_colourings_full(const G& g) {
  int8_t col[MAXN]; memset(col, -1, sizeof(col));
  int8_t tryc[MAXN]; memset(tryc, 0, sizeof(tryc));
  long long cnt = 0; int pos = 0; bool ok = true;
  while (pos >= 0) {
    if (pos == N) {
      cnt++;
      int s[3] = {0,0,0};
      for (int v = 0; v < N; v++) s[col[v]] += b[v];
      if (!vec_allowed(s[0],s[1],s[2])) { ok = false; break; }
      pos--; continue;
    }
    int v = pos; bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      bool fine = true; uint32_t nb = g.adj[v];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb-1; if (u < v && col[u]==c) { fine=false; break; } }
      if (fine) { col[v]=c; tryc[pos]=c+1; pos++; if (pos<N) tryc[pos]=0; adv=true; break; }
    }
    if (!adv) { col[v]=-1; tryc[pos]=0; pos--; }
  }
  nCol = cnt;
  return ok && cnt > 0;
}
// mode 1: does H-skip admit a proper colouring with deficiency on N(skip) <= b(skip)?
static bool exists_good_colouring_minus(const G& g, int skip) {
  int verts[MAXN], m = 0;
  for (int v = 0; v < N; v++) if (v != skip) verts[m++] = v;
  int8_t col[MAXN]; memset(col, -1, sizeof(col));
  int8_t tryc[MAXN]; memset(tryc, 0, sizeof(tryc));
  int pos = 0;
  while (pos >= 0) {
    if (pos == m) {
      int cnt[3] = {0,0,0};
      uint32_t nb = g.adj[skip];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb-1; cnt[col[u]]++; }
      int defc = 0;
      for (int i = 0; i < 3; i++) if (cnt[i] < 2) defc += 2 - cnt[i];
      if (defc <= b[skip]) return true;
      pos--; continue;
    }
    int v = verts[pos]; bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      bool fine = true; uint32_t nb = g.adj[v];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb-1;
        if (u == skip || col[u] != c) continue; fine = false; break; }
      if (fine) { col[v]=c; tryc[pos]=c+1; pos++; if (pos<m) tryc[pos]=0; adv=true; break; }
    }
    if (!adv) { col[v]=-1; tryc[pos]=0; pos--; }
  }
  return false;
}
static bool twins_ok(const G& g) {
  for (int u = 0; u < N; u++) {
    if (b[u] != 0) continue;
    for (int v = 0; v < N; v++) {
      if (v == u || (g.adj[u] >> v & 1)) continue;
      uint32_t nu = g.adj[u] & ~(1u << v);
      if ((nu & ~g.adj[v]) == 0) return false;
    }
  }
  return true;
}
int main(int argc, char** argv) {
  N = argc > 1 ? atoi(argv[1]) : 10;
  bool certs = argc > 2 && string(argv[2]) == "certs";
  string line;
  long long total=0, badB=0, no3col=0, badvec=0, badtwin=0, killed=0, survive=0;
  while (getline(cin, line)) {
    while (!line.empty() && (line.back()=='\r'||line.back()=='\n')) line.pop_back();
    if (line.empty() || line[0] == '>') continue;
    G g;
    if (!g6decode(line, g)) continue;
    total++;
    bool okB = true;
    for (int v = 0; v < N; v++) { b[v] = 6 - g.deg(v); if (b[v] < 0 || b[v] > 5) okB = false; }
    if (!okB) { badB++; continue; }
    if (!check_colourings_full(g)) { if (nCol == 0) no3col++; else badvec++; continue; }
    if (!twins_ok(g)) {
      badtwin++;
      if (certs) printf("CERT %s fate=twins ncol=%lld\n", line.c_str(), nCol);
      continue;
    }
    bool dead = false;
    int killv = -1;
    for (int v = 0; v < N && !dead; v++)
      if (!exists_good_colouring_minus(g, v)) { dead = true; killv = v; }
    if (dead) {
      killed++;
      if (certs) printf("CERT %s fate=kill:v%d b%d ncol=%lld\n", line.c_str(), killv, b[killv], nCol);
      continue;
    }
    survive++;
    printf("SURVIVOR: %s  ncol=%lld  b=", line.c_str(), nCol);
    for (int v = 0; v < N; v++) printf("%d", b[v]);
    printf("\n");
  }
  printf("total=%lld badDeficiency=%lld not3col=%lld badBoundaryVec=%lld comparableNonNbr=%lld localKill=%lld SURVIVORS=%lld\n",
         total, badB, no3col, badvec, badtwin, killed, survive);
  return 0;
}
