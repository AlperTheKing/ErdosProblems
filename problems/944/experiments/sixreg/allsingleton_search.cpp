// G3 finite search: the all-singleton extreme of the zero-budget theorem.
// Candidate counterexample shape: H = C + v where C is a connected bipartite
// graph with balanced parts (q,q), Delta<=6, 6q-6 cross edges (kappa(C)=12),
// and apex v adjacent to 4 A-vertices and 2 B-vertices, each with cross-
// deficiency >= 1 (so Delta(H)<=6; final deficiency 2 on A, 4 on B, total 6).
// H is 3-colourable automatically (bipartite + apex).
// (FK) predicts: H always has a FROZEN full vertex. A candidate counterexample
// must have EVERY full (degree-6) vertex deletion-unfrozen ((2,2,2) witness).
// usage: allsingleton_search.exe q [nthreads] < pieces_bipk12_m{2q}.g6
//   reports survivors (g6 + apex sets); prints summary.
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <thread>
#include <atomic>
#include <mutex>
using namespace std;

static const int MAXV = 20;

struct G {
  int n;
  uint32_t adj[MAXV];
  void add(int u, int v) { adj[u] |= 1u << v; adj[v] |= 1u << u; }
  int deg(int u) const { return __builtin_popcount(adj[u]); }
};

static bool g6decode(const string& line, G& g) {
  if (line.empty()) return false;
  g.n = line[0] - 63;
  if (g.n < 1 || g.n > MAXV) return false;
  memset(g.adj, 0, sizeof(g.adj));
  int nbits = g.n * (g.n - 1) / 2, need = (nbits + 5) / 6;
  if ((int)line.size() < 1 + need) return false;
  int bit = 0;
  for (int j = 1; j < g.n; j++) for (int i = 0; i < j; i++) {
    int byte = 1 + bit / 6, off = 5 - bit % 6;
    if ((line[byte] - 63) >> off & 1) g.add(i, j);
    bit++;
  }
  return true;
}

// unique bipartition of a connected bipartite graph; false if not bipartite.
static bool bipartition(const G& g, uint32_t& sideA) {
  int8_t side[MAXV]; memset(side, -1, sizeof(side));
  side[0] = 0;
  uint32_t stack = 1, seen = 1;
  sideA = 1;
  while (stack) {
    int x = __builtin_ctz(stack); stack &= stack - 1;
    uint32_t nb = g.adj[x];
    while (nb) {
      int y = __builtin_ctz(nb); nb &= nb - 1;
      if (side[y] < 0) {
        side[y] = 1 - side[x];
        if (side[y] == 0) sideA |= 1u << y;
        seen |= 1u << y; stack |= 1u << y;
      } else if (side[y] == side[x]) return false;
    }
  }
  return seen == (1u << g.n) - 1;   // connected
}

// does H-v admit a proper 3-colouring with N(v) colour counts exactly (2,2,2)?
// (port of unfrozen_census.cpp::unfrozen, validated against the n<=14 census)
static bool unfrozen(const G& g, int v) {
  int N = g.n;
  int idx[MAXV], m = 0;
  uint32_t nbv = g.adj[v];
  while (nbv) { int u = __builtin_ctz(nbv); nbv &= nbv - 1; idx[m++] = u; }
  int nN = m;
  for (int u = 0; u < N; u++) if (u != v && !((g.adj[v] >> u) & 1)) idx[m++] = u;
  for (int i = nN + 1; i < m; i++) { int k = idx[i], j = i - 1;
    while (j >= nN && g.deg(idx[j]) < g.deg(k)) { idx[j+1] = idx[j]; j--; } idx[j+1] = k; }
  int8_t color[MAXV]; memset(color, -1, sizeof(color));
  int cnt[3] = {0, 0, 0};
  int pos = 0; int8_t tryc[MAXV]; memset(tryc, 0, sizeof(tryc));
  while (pos >= 0) {
    if (pos == m) return true;
    int x = idx[pos]; bool adv = false;
    int cmax = (pos == 0) ? 1 : 3;
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

int main(int argc, char** argv) {
  int q = argc > 1 ? atoi(argv[1]) : 5;
  int nthreads = argc > 2 ? atoi(argv[2]) : 1;
  vector<string> lines;
  { string line;
    while (getline(cin, line)) {
      while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
      if (!line.empty() && line[0] != '>') lines.push_back(line);
    } }
  atomic<long long> idx(0), graphs(0), balanced(0), apexings(0), survivors(0);
  atomic<long long> killV(0), killFourAdj(0), killFourNon(0), killTwoAdj(0), killTwoNon(0);
  mutex outMtx;
  auto worker = [&]() {
    for (;;) {
      long long i = idx.fetch_add(1);
      if (i >= (long long)lines.size()) break;
      const string& line = lines[i];
      G c;
      if (!g6decode(line, c) || c.n != 2 * q) continue;
      graphs++;
      uint32_t sideA;
      if (!bipartition(c, sideA)) continue;       // disconnected or odd cycle
      int szA = __builtin_popcount(sideA);
      if (szA != q) continue;                     // need balanced parts
      balanced++;
      // deficiency-positive vertices per side
      vector<int> defA, defB;
      for (int x = 0; x < c.n; x++) {
        if (c.deg(x) >= 6) continue;              // d = 6 - deg >= 1 required
        if ((sideA >> x) & 1) defA.push_back(x); else defB.push_back(x);
      }
      // both orientations: apex 4 on A & 2 on B, and apex 4 on B & 2 on A
      for (int orient = 0; orient < 2; orient++) {
        const vector<int>& four = orient == 0 ? defA : defB;
        const vector<int>& two  = orient == 0 ? defB : defA;
        int nf = (int)four.size(), nt = (int)two.size();
        if (nf < 4 || nt < 2) continue;
        for (int a1 = 0; a1 < nf; a1++) for (int a2 = a1+1; a2 < nf; a2++)
        for (int a3 = a2+1; a3 < nf; a3++) for (int a4 = a3+1; a4 < nf; a4++)
        for (int b1 = 0; b1 < nt; b1++) for (int b2 = b1+1; b2 < nt; b2++) {
          apexings++;
          G h = c; h.n = c.n + 1;
          int v = c.n;
          h.adj[v] = 0;
          h.add(v, four[a1]); h.add(v, four[a2]); h.add(v, four[a3]); h.add(v, four[a4]);
          h.add(v, two[b1]);  h.add(v, two[b2]);
          // every full vertex must be unfrozen; v (always full) first, cheap kill
          bool allUnfrozen = unfrozen(h, v);
          if (!allUnfrozen) killV++;
          for (int x = 0; x < h.n - 1 && allUnfrozen; x++) {
            if (h.deg(x) != 6) continue;
            if (!unfrozen(h, x)) {
              allUnfrozen = false;
              bool inA = (sideA >> x) & 1, adjV = (h.adj[v] >> x) & 1;
              // classify relative to the 4-side ("A" of this orientation)
              bool inFour = orient == 0 ? inA : !inA;
              (inFour ? (adjV ? killFourAdj : killFourNon)
                      : (adjV ? killTwoAdj : killTwoNon))++;
            }
          }
          if (allUnfrozen) {
            survivors++;
            lock_guard<mutex> lk(outMtx);
            printf("SURVIVOR g6=%s apexA={%d,%d,%d,%d} apexB={%d,%d} orient=%d\n",
                   line.c_str(), four[a1], four[a2], four[a3], four[a4],
                   two[b1], two[b2], orient);
            fflush(stdout);
          }
        }
      }
    }
  };
  vector<thread> th;
  for (int t = 0; t < nthreads; t++) th.emplace_back(worker);
  for (auto& t : th) t.join();
  printf("q=%d graphs=%lld balanced=%lld apexings=%lld SURVIVORS=%lld\n",
         q, graphs.load(), balanced.load(), apexings.load(), survivors.load());
  printf("kills: v=%lld fourSideAdjV=%lld fourSideNonAdj=%lld twoSideAdjV=%lld twoSideNonAdj=%lld\n",
         killV.load(), killFourAdj.load(), killFourNon.load(),
         killTwoAdj.load(), killTwoNon.load());
  return 0;
}
