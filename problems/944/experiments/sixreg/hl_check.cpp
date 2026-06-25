// HL-law falsification check (2026-06-12). Law (empirical, m<=13, kappa<=20):
// connected bipartite Delta<=6 piece with locked=0 satisfies e <= 2m.
// Candidate refutation: bridged K44 blocks (e = 2m + #bridges, kappa > 20).
// locked(v) per piece_hunt.cpp locked mode: NO proper 3-colouring of C-v has
// every colour count <= 2 on N_C(v).
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <vector>
#include <string>
using namespace std;

struct G {
  int n = 0;
  unsigned adj[32] = {};
  void addEdge(int a, int b) { adj[a] |= 1u << b; adj[b] |= 1u << a; }
  int deg(int x) const { return __builtin_popcount(adj[x]); }
};

// proper 3-colourings of G minus del; stop when cb true.
static bool forEachCol(const G& g, int del, int8_t* col, int pos, const vector<int>& order,
                       unsigned nbv, const int* cnt0, bool (*final)(const int*, int), int dv) {
  if (pos == (int)order.size()) return true;
  int x = order[pos];
  for (int c = 0; c < 3; c++) {
    bool ok = true;
    unsigned nb = g.adj[x];
    while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
      if (u != del && col[u] == c) { ok = false; break; } }
    if (!ok) continue;
    col[x] = c;
    if (forEachCol(g, del, col, pos + 1, order, nbv, cnt0, final, dv)) { col[x] = -1; return true; }
    col[x] = -1;
  }
  return false;
}

// unlockable(v): exists proper 3-col of G-v with each colour <=2 on N(v).
// prune: colour N(v) first; abort branch when some colour exceeds 2 on N(v).
static bool unlockable(const G& g, int v) {
  vector<int> order;
  unsigned nbv = g.adj[v];
  for (int x = 0; x < g.n; x++) if (x != v && (nbv >> x & 1)) order.push_back(x);
  for (int x = 0; x < g.n; x++) if (x != v && !(nbv >> x & 1)) order.push_back(x);
  int8_t col[32]; memset(col, -1, sizeof(col));
  // recursive with count pruning on N(v)
  struct R {
    const G& g; int v; unsigned nbv; const vector<int>& order;
    int8_t* col; int cnt[3] = {0,0,0};
    R(const G& gg, int vv, unsigned nb, const vector<int>& o, int8_t* c)
        : g(gg), v(vv), nbv(nb), order(o), col(c) {}
    bool go(int pos) {
      if (pos == (int)order.size()) return true;
      int x = order[pos];
      bool onN = nbv >> x & 1;
      for (int c = 0; c < 3; c++) {
        if (onN && cnt[c] == 2) continue;
        bool ok = true;
        unsigned nb = g.adj[x];
        while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
          if (u != v && col[u] == c) { ok = false; break; } }
        if (!ok) continue;
        col[x] = c; if (onN) cnt[c]++;
        if (go(pos + 1)) { col[x] = -1; if (onN) cnt[c]--; return true; }
        col[x] = -1; if (onN) cnt[c]--;
      }
      return false;
    }
  } r(g, v, nbv, order, col);
  return r.go(0);
}

static bool bipartite(const G& g) {
  int side[32]; memset(side, -1, sizeof(side));
  for (int s = 0; s < g.n; s++) {
    if (side[s] >= 0) continue;
    side[s] = 0;
    vector<int> st = {s};
    while (!st.empty()) {
      int x = st.back(); st.pop_back();
      unsigned nb = g.adj[x];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
        if (side[u] < 0) { side[u] = side[x] ^ 1; st.push_back(u); }
        else if (side[u] == side[x]) return false; }
    }
  }
  return true;
}

static void addK44(G& g, int base) {           // sides {base..base+3},{base+4..base+7}
  for (int a = 0; a < 4; a++) for (int b = 0; b < 4; b++) g.addEdge(base + a, base + 4 + b);
}

static void report(const char* name, const G& g) {
  int e = 0;
  for (int x = 0; x < g.n; x++) e += g.deg(x);
  e /= 2;
  int maxd = 0;
  for (int x = 0; x < g.n; x++) if (g.deg(x) > maxd) maxd = g.deg(x);
  int locked = 0;
  string lockedList;
  for (int v = 0; v < g.n; v++)
    if (!unlockable(g, v)) { locked++; lockedList += " " + to_string(v); }
  printf("%s: m=%d e=%d 2m=%d kappa=%d Delta=%d bipartite=%d connected_check_by_construction locked=%d%s%s\n",
         name, g.n, e, 2 * g.n, 6 * g.n - 2 * e, maxd, bipartite(g) ? 1 : 0, locked,
         locked ? " lockedV:" : "", lockedList.c_str());
  printf("  -> HL law (locked=0 => e<=2m): %s\n",
         (locked == 0 && e > 2 * g.n) ? "VIOLATED (counterexample)" : "consistent");
}

int main() {
  { G g; g.n = 8; addK44(g, 0); report("K44 (control, expect locked=0, e=2m)", g); }
  { G g; g.n = 16; addK44(g, 0); addK44(g, 8);
    g.addEdge(0, 8);                            // bridge A-side block1 -> A-side block2 (parts swap)
    report("2xK44 + bridge (m=16, e=33)", g); }
  { G g; g.n = 24; addK44(g, 0); addK44(g, 8); addK44(g, 16);
    g.addEdge(0, 8); g.addEdge(12, 16);         // chain of 3
    report("3xK44 chain (m=24, e=50)", g); }
  { G g; g.n = 16; addK44(g, 0); addK44(g, 8);
    g.addEdge(0, 8); g.addEdge(1, 9);           // TWO bridges: e=34=2m+2
    report("2xK44 + 2 bridges (m=16, e=34)", g); }
  { G g; g.n = 16; addK44(g, 0); addK44(g, 8);  // FOUR distinct-endpoint bridges:
    for (int i = 0; i < 4; i++) g.addEdge(i, 8 + i);   // e=36=2m+4, kappa=24
    report("2xK44 + 4 bridges (m=16, e=36, kappa=24)", g); }
  { G g; g.n = 16; addK44(g, 0); addK44(g, 8);  // saturating 2-regular bridge set:
    for (int i = 0; i < 4; i++) { g.addEdge(i, 8 + i); g.addEdge(i, 8 + (i + 1) % 4); }
    report("2xK44 + 8 bridges (m=16, e=40, kappa=16; expect LOCKED)", g); }
  return 0;
}
