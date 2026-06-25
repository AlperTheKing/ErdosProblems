// CRITICAL D-test on the danger family's purest member: incidence graph of
// PG(2,5) — 31 points + 31 lines, 6-regular bipartite, girth 6, vertex- and
// (self-dual) flag-transitive. One vertex's verdict decides all 62.
// unfrozen(v) <=> exists proper 3-colouring of G-v with N(v) counts (2,2,2).
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <vector>
using namespace std;
static const int N = 62;
static uint64_t adj[N];
int main() {
  // points: normalized (x:y:z) over F5: z=1 (25), z=0,y=1 (5), z=0,y=0,x=1 (1)
  int P[31][3], np = 0;
  for (int x = 0; x < 5; x++) for (int y = 0; y < 5; y++) { P[np][0]=x; P[np][1]=y; P[np][2]=1; np++; }
  for (int x = 0; x < 5; x++) { P[np][0]=x; P[np][1]=1; P[np][2]=0; np++; }
  P[np][0]=1; P[np][1]=0; P[np][2]=0; np++;
  // lines: same normalized triples (a:b:c); incidence ax+by+cz=0 mod 5
  memset(adj, 0, sizeof(adj));
  int edges = 0;
  for (int p = 0; p < 31; p++) for (int l = 0; l < 31; l++) {
    int s = (P[p][0]*P[l][0] + P[p][1]*P[l][1] + P[p][2]*P[l][2]) % 5;
    if (s == 0) { adj[p] |= 1ull << (31+l); adj[31+l] |= 1ull << p; edges++; }
  }
  // sanity: 6-regular, 186 edges
  for (int v = 0; v < N; v++) if (__builtin_popcountll(adj[v]) != 6) { printf("DEGREE FAIL v=%d d=%d\n", v, __builtin_popcountll(adj[v])); return 1; }
  printf("PG(2,5) incidence built: %d edges (expect 186)\n", edges);
  // unfrozen test for v=0 (a point; transitivity + self-duality covers all)
  int v = 0;
  int order[N]; int m = 0;
  // N(v) first, then BFS from N(v)
  uint64_t nv = adj[v];
  bool inOrd[N]; memset(inOrd, 0, sizeof(inOrd));
  for (int u = 0; u < N; u++) if (nv >> u & 1) { order[m++] = u; inOrd[u] = true; }
  // BFS layers
  for (int head = 0; head < m; head++) {
    uint64_t nb = adj[order[head]];
    for (int u = 0; u < N; u++) if ((nb >> u & 1) && u != v && !inOrd[u]) { order[m++] = u; inOrd[u] = true; }
  }
  printf("order built m=%d (expect 61)\n", m);
  int8_t col[N]; memset(col, -1, sizeof(col));
  int cnt[3] = {0,0,0};
  long long nodes = 0;
  int8_t tryc[N]; memset(tryc, 0, sizeof(tryc));
  int pos = 0;
  while (pos >= 0) {
    if (pos == m) { printf("UNFROZEN: witness found after %lld nodes\n", nodes); return 0; }
    int x = order[pos]; bool adv = false;
    bool isNbr = pos < 6;
    for (int c = tryc[pos]; c < 3; c++) {
      if (isNbr && cnt[c] >= 2) continue;
      bool ok = true; uint64_t nb = adj[x];
      while (nb) { int u = __builtin_ctzll(nb); nb &= nb-1;
        if (u == v) continue;
        if (col[u] == c) { ok = false; break; } }
      if (ok) { col[x] = c; if (isNbr) cnt[c]++; nodes++;
        tryc[pos] = c+1; pos++; if (pos < m) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { tryc[pos] = 0; pos--;
      if (pos >= 0) { int y = order[pos]; if (pos < 6) cnt[col[y]]--; col[y] = -1; } }
    if (nodes % 500000000 == 0 && nodes) { printf("... %lld nodes\n", nodes); fflush(stdout); }
  }
  printf("FROZEN: exhausted after %lld nodes — no (2,2,2) witness for v=0\n", nodes);
  return 0;
}
