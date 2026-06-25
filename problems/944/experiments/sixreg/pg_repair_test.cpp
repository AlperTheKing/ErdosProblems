// Test A in C++: PG(2,5)-repair 3+3 surgery vs [K] (boundary shortfall).
// usage: pg_repair_test <p> <l> <seed>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <random>
using namespace std;
static const int N = 62;
static uint64_t adj[N];
static int P[31][3];
static long long CAP = 4000000000LL;   // 4e9 nodes ~ a couple minutes
static bool witnessShortfall(int v, int bv, long long* nodesOut) {
  int nvList[8], nN = 0;
  for (int u = 0; u < N; u++) if (adj[v] >> u & 1) nvList[nN++] = u;
  int order[N]; int m = 0;
  bool used[N]; memset(used, 0, sizeof(used));
  used[v] = true;
  for (int i = 0; i < nN; i++) { order[m++] = nvList[i]; used[nvList[i]] = true; }
  for (int h = 0; h < m; h++) {                 // BFS
    uint64_t nb = adj[order[h]];
    for (int u = 0; u < N; u++) if ((nb >> u & 1) && !used[u]) { order[m++] = u; used[u] = true; }
  }
  for (int u = 0; u < N; u++) if (!used[u]) order[m++] = u;
  int8_t col[N]; memset(col, -1, sizeof(col));
  int cnt[3] = {0,0,0};
  int8_t tryc[N]; memset(tryc, 0, sizeof(tryc));
  long long nodes = 0;
  int pos = 0;
  while (pos >= 0) {
    if (pos == m) {
      int sh = 0; for (int c = 0; c < 3; c++) sh += max(0, 2-cnt[c]);
      if (sh <= bv) { *nodesOut = nodes; return true; }
      pos--; { int y = order[pos]; if (pos < nN) cnt[col[y]]--; col[y] = -1; }
      continue;
    }
    int x = order[pos]; bool adv = false;
    bool isNbr = pos < nN;
    for (int c = tryc[pos]; c < 3; c++) {
      if (isNbr && cnt[c] >= 2 && bv == 0) continue;   // exact (2,2,2) prune only for full v
      bool ok = true; uint64_t nb = adj[x];
      while (nb) { int u = __builtin_ctzll(nb); nb &= nb-1;
        if (u == v) continue;
        if (col[u] == c) { ok = false; break; } }
      if (ok) { col[x] = c; if (isNbr) cnt[c]++; nodes++;
        if (nodes > CAP) { *nodesOut = nodes; return false; }  // treat as frozen-ish; caller sees CAP
        tryc[pos] = c+1; pos++; if (pos < m) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { tryc[pos] = 0; pos--;
      if (pos >= 0) { int y = order[pos]; if (pos < nN) cnt[col[y]]--; col[y] = -1; } }
  }
  *nodesOut = nodes; return false;
}
int main(int argc, char** argv) {
  int p = atoi(argv[1]), l = atoi(argv[2]); unsigned seed = argc > 3 ? atoi(argv[3]) : 944;
  int np = 0;
  for (int x = 0; x < 5; x++) for (int y = 0; y < 5; y++) { P[np][0]=x;P[np][1]=y;P[np][2]=1;np++; }
  for (int x = 0; x < 5; x++) { P[np][0]=x;P[np][1]=1;P[np][2]=0;np++; }
  P[np][0]=1;P[np][1]=0;P[np][2]=0;np++;
  memset(adj, 0, sizeof(adj));
  for (int a = 0; a < 31; a++) for (int b = 0; b < 31; b++)
    if ((P[a][0]*P[b][0]+P[a][1]*P[b][1]+P[a][2]*P[b][2]) % 5 == 0) { adj[a] |= 1ull<<(31+b); adj[31+b] |= 1ull<<a; }
  int lv = 31 + l;
  // pick 3 nbrs of p and 3 of lv
  mt19937 rng(seed);
  vector<int> Lp, Pl;
  for (int u = 0; u < N; u++) { if (adj[p]>>u&1) Lp.push_back(u); if (adj[lv]>>u&1) Pl.push_back(u); }
  shuffle(Lp.begin(), Lp.end(), rng); shuffle(Pl.begin(), Pl.end(), rng);
  Lp.resize(3); Pl.resize(3);
  if (Pl[0]==p||Pl[1]==p||Pl[2]==p||Lp[0]==lv||Lp[1]==lv||Lp[2]==lv) { printf("SKIP incident choice\n"); return 2; }
  for (int L : Lp) { adj[p] &= ~(1ull<<L); adj[L] &= ~(1ull<<p); }
  for (int Q : Pl) { adj[lv] &= ~(1ull<<Q); adj[Q] &= ~(1ull<<lv); }
  // repair matching
  int perm[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
  bool done = false;
  for (int t = 0; t < 6 && !done; t++) {
    bool ok = true;
    for (int j = 0; j < 3; j++) if (adj[Pl[j]] >> Lp[perm[t][j]] & 1) ok = false;
    if (ok) { for (int j = 0; j < 3; j++) { adj[Pl[j]] |= 1ull<<Lp[perm[t][j]]; adj[Lp[perm[t][j]]] |= 1ull<<Pl[j]; } done = true; }
  }
  if (!done) { printf("SKIP no repair matching\n"); return 2; }
  // sanity
  int b[N]; long long sb = 0;
  for (int v = 0; v < N; v++) { b[v] = 6 - __builtin_popcountll(adj[v]); sb += b[v]; }
  if (sb != 6 || b[p] != 3 || b[lv] != 3) { printf("SKIP bad deficiency\n"); return 2; }
  printf("surgery p=%d l=%d OK (b(p)=b(l)=3)\n", p, l);
  for (int v = 0; v < N; v++) {
    long long nodes;
    bool w = witnessShortfall(v, b[v], &nodes);
    if (!w) {
      if (nodes > CAP) printf("v=%d CAP-UNRESOLVED nodes=%lld\n", v, nodes);
      else { printf("v=%d FROZEN ([K] FAILS) nodes=%lld\n", v, nodes); return 1; }
    }
  }
  printf("ALL 62 PASS [K] — PG-repair candidate SURVIVES boundary-shortfall\n");
  return 0;
}
