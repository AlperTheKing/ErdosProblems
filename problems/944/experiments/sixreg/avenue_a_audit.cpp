// avenue_a_audit.cpp (2026-06-12): QUANTITATIVE AUDIT OF PROOF-AVENUE (A)
// ("forced-equal-pair leak") for conjecture (R3-prime), on the 12 deterministic
// PG(2,5)+diamond-gadget instances of rainbow_r3_128.cpp (identical RNG seed and
// construction order => identical graphs; cross-check stub lists + locked sets
// against mass_sweep_r3.txt).
//
// Definitions (v full, H := K - v, N := N_K(v), |N| = 6):
//   eqAch(x,y)   : exists proper 3-col psi of H with psi(x) = psi(y)
//   diffAch(x,y) : exists psi with psi(x) != psi(y)
//   forced-equal pair  : diffAch = 0;  forced-diff pair : eqAch = 0 (incl. edges).
// Avenue-(A) certificate levels (THEOREM, easy: F1 => F2 => v frozen):
//   F1: some forced-equality class meets N in >= 3 vertices.
//   F2: no perfect matching M of N (3 pairs) such that every forced-equal pair
//       is an M-pair and no M-pair is forced-diff.  [(2,2,2) pattern needs such M]
// AUDIT QUESTION: does ANY full vertex in ANY rainbow-rigid instance carry an
// F1/F2 certificate?  (Frozen vertices without F2 = pairwise-invisible freezing.)
// Extra: global forced relations of K itself (inst < 4); achievable trace-shape
// census per full vertex (inst 0).
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <array>
#include <set>
#include <functional>
#include <thread>
#include <atomic>
#include <mutex>
#include <algorithm>
using namespace std;

static const int MAXN = 128, NTAU = 729;
static const int POW3[7] = {1,3,9,27,81,243,729};

struct BS {
  uint64_t w[2] = {0, 0};
  void set(int i) { w[i >> 6] |= 1ull << (i & 63); }
  void clr(int i) { w[i >> 6] &= ~(1ull << (i & 63)); }
  bool test(int i) const { return w[i >> 6] >> (i & 63) & 1; }
  int count() const { return __builtin_popcountll(w[0]) + __builtin_popcountll(w[1]); }
};

struct BG {
  int n = 0;
  BS adj[MAXN];
  void addEdge(int a, int b) { adj[a].set(b); adj[b].set(a); }
  void delEdge(int a, int b) { adj[a].clr(b); adj[b].clr(a); }
  int deg(int x) const { return adj[x].count(); }
};

template <class F>
static void forNbr(const BG& g, int x, F f) {
  for (int wd = 0; wd < 2; wd++) {
    uint64_t nb = g.adj[x].w[wd];
    while (nb) { int u = 64 * wd + __builtin_ctzll(nb); nb &= nb - 1; if (!f(u)) return; }
  }
}

static bool connectedG(const BG& g) {
  BS seen; seen.set(0); vector<int> st = {0};
  while (!st.empty()) { int x = st.back(); st.pop_back();
    forNbr(g, x, [&](int u) { if (!seen.test(u)) { seen.set(u); st.push_back(u); } return true; }); }
  return seen.count() == g.n;
}

struct Solver {
  const BG* g; int del; bool useTrace; BS nbv;
  uint8_t dom[MAXN]; int8_t col[MAXN];
  int cnt[3];
  vector<pair<int,uint8_t>> trail;
  uint64_t nodes = 0, cap = 200000000ull;
  bool shrink(int u, uint8_t bit) {
    if (!(dom[u] & bit)) return true;
    trail.push_back({u, dom[u]});
    dom[u] &= ~bit;
    return dom[u] != 0;
  }
  int solve() {
    if (++nodes > cap) return 2;
    int x = -1, best = 4;
    for (int u = 0; u < g->n; u++)
      if (col[u] < 0) { int p = __builtin_popcount(dom[u]);
        if (p < best) { best = p; x = u; if (p <= 1) break; } }
    if (x < 0) return 1;
    for (int c = 0; c < 3; c++) {
      if (!(dom[x] >> c & 1)) continue;
      bool ok = true;
      size_t mark = trail.size();
      col[x] = c;
      bool onN = useTrace && del >= 0 && nbv.test(x);
      if (onN) {
        cnt[c]++;
        if (cnt[c] == 2) {
          for (int wd = 0; wd < 2 && ok; wd++) {
            uint64_t nb = nbv.w[wd];
            while (nb) { int v2 = 64 * wd + __builtin_ctzll(nb); nb &= nb - 1;
              if (v2 != x && col[v2] < 0 && !shrink(v2, 1 << c)) { ok = false; break; } }
          }
        }
      }
      if (ok) {
        for (int wd = 0; wd < 2 && ok; wd++) {
          uint64_t nb = g->adj[x].w[wd];
          while (nb) { int u = 64 * wd + __builtin_ctzll(nb); nb &= nb - 1;
            if (u != del && col[u] < 0 && !shrink(u, 1 << c)) { ok = false; break; } }
        }
      }
      if (ok) { int r = solve(); if (r) return r; }
      while (trail.size() > mark) { dom[trail.back().first] = trail.back().second; trail.pop_back(); }
      if (onN) cnt[c]--;
      col[x] = -1;
    }
    return 0;
  }
};

// general query: delete `del` (or -1), optional (2,2,2)-trace cap at del,
// fix colours of arbitrary vertices. returns 0 unsat / 1 sat / 2 cap-out.
static int queryGen(const BG& g, int del, bool useTrace,
                    const vector<pair<int,int>>& fixes) {
  Solver s; s.g = &g; s.del = del; s.useTrace = useTrace;
  if (del >= 0) s.nbv = g.adj[del];
  s.cnt[0] = s.cnt[1] = s.cnt[2] = 0;
  memset(s.col, -1, sizeof(s.col));
  for (int u = 0; u < g.n; u++) s.dom[u] = 7;
  for (auto& f : fixes) {
    uint8_t bit = 1 << f.second;
    if (!(s.dom[f.first] & bit)) return 0;
    s.dom[f.first] = bit;
  }
  if (del >= 0) s.col[del] = 3;
  return s.solve();
}

static int canon6(int t0) {
  static const int P[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
  int best = 99999;
  for (auto& p : P) { int h = 0, t = t0;
    for (int s = 0; s < 6; s++) { h += p[t % 3] * POW3[s]; t /= 3; }
    if (h < best) best = h; }
  return best;
}

static uint64_t RNG = 0xABCDEF9876543210ull;   // SAME seed as rainbow_r3_128.cpp
static uint64_t rnd() { RNG ^= RNG << 13; RNG ^= RNG >> 7; RNG ^= RNG << 17; return RNG; }

// all 15 perfect matchings of {0..5}; partner[i] = matched element
static vector<array<int,6>> allPMs() {
  vector<array<int,6>> out;
  array<int,6> partner; partner.fill(-1);
  struct Rec { vector<array<int,6>>& out; array<int,6>& p;
    void go() {
      int i = 0; while (i < 6 && p[i] >= 0) i++;
      if (i == 6) { out.push_back(p); return; }
      for (int j = i + 1; j < 6; j++) if (p[j] < 0) {
        p[i] = j; p[j] = i; go(); p[i] = -1; p[j] = -1; }
    } } rec{out, partner};
  rec.go();
  return out;
}

int main(int argc, char** argv) {
  int instLimit = argc > 1 ? atoi(argv[1]) : 12;
  int nThreads = 64;
  auto PMs = allPMs();
  static const int PI[15][2] = {{0,1},{0,2},{0,3},{0,4},{0,5},{1,2},{1,3},{1,4},{1,5},
                                {2,3},{2,4},{2,5},{3,4},{3,5},{4,5}};
  // PG(2,5) incidence on 0..61
  vector<array<int,3>> reps;
  for (int a = 0; a < 5; a++) for (int b = 0; b < 5; b++) for (int c = 0; c < 5; c++) {
    if (!a && !b && !c) continue;
    if ((a && a != 1) || (!a && b && b != 1) || (!a && !b && c != 1)) continue;
    reps.push_back({a, b, c});
  }
  for (int inst = 0; inst < 12; inst++) {
    BG g; g.n = 68;
    for (int i = 0; i < 31; i++) for (int j = 0; j < 31; j++) {
      int dot = reps[i][0]*reps[j][0] + reps[i][1]*reps[j][1] + reps[i][2]*reps[j][2];
      if (dot % 5 == 0) g.addEdge(i, 31 + j);
    }
    int A = 62, B = 63, U = 64, T = 65, V = 66, W = 67;
    g.addEdge(A, B);
    g.addEdge(A, U); g.addEdge(B, U);
    g.addEdge(A, T); g.addEdge(B, T);
    g.addEdge(U, V); g.addEdge(V, W); g.addEdge(T, W);
    vector<int> capv;
    {
      BS used; int got = 0;
      for (int tries = 0; tries < 20000 && got < 10; tries++) {
        int x = rnd() % 62;
        if (used.test(x)) continue;
        vector<int> cand;
        forNbr(g, x, [&](int u) { if (u < 62 && !used.test(u)) cand.push_back(u); return true; });
        if (cand.empty()) continue;
        int y = cand[rnd() % cand.size()];
        BG h = g; h.delEdge(x, y);
        BS seen; seen.set(0); vector<int> st = {0};
        while (!st.empty()) { int z = st.back(); st.pop_back();
          forNbr(h, z, [&](int q) { if (q < 62 && !seen.test(q)) { seen.set(q); st.push_back(q); } return true; }); }
        int cc = 0; for (int q = 0; q < 62; q++) if (seen.test(q)) cc++;
        if (cc != 62) continue;
        g = h; used.set(x); used.set(y);
        capv.push_back(x); capv.push_back(y); got++;
      }
      if (got < 10) { printf("inst %d: capacity fail\n", inst); continue; }
    }
    for (int i = (int)capv.size() - 1; i > 0; i--) { int j = rnd() % (i + 1); swap(capv[i], capv[j]); }
    {
      int padNeed[6] = {3, 3, 2, 3, 3, 3};       // A B U T V W
      int gvs[6] = {A, B, U, T, V, W};
      int idx = 0;
      for (int k = 0; k < 6; k++)
        for (int p = 0; p < padNeed[k]; p++) g.addEdge(gvs[k], capv[idx++]);
    }
    if (!connectedG(g)) { printf("inst %d: disconnected\n", inst); continue; }
    if (inst >= instLimit) continue;   // construction consumed RNG; skip analysis only
    int stubV[6] = {U, V, W, capv[17], capv[18], capv[19]};
    int sumb = 0, maxd = 0;
    for (int x = 0; x < g.n; x++) { sumb += 6 - g.deg(x); if (g.deg(x) > maxd) maxd = g.deg(x); }
    printf("inst %d: m=%d sum_b=%d Delta=%d stubs {%d,%d,%d,%d,%d,%d}\n",
           inst, g.n, sumb, maxd, stubV[0], stubV[1], stubV[2], stubV[3], stubV[4], stubV[5]);
    if (sumb != 6 || maxd > 6) { printf("inst %d: INVALID, skip\n", inst); continue; }
    if (queryGen(g, -1, false, {}) != 1) { printf("inst %d: NOT 3-colourable?!\n", inst); continue; }
    { // dump edge list for offline structural analysis
      char fn[64]; snprintf(fn, sizeof fn, "avenue_a_graph_inst%d.txt", inst);
      FILE* fp = fopen(fn, "w");
      for (int x = 0; x < g.n; x++) for (int y = x + 1; y < g.n; y++)
        if (g.adj[x].test(y)) fprintf(fp, "%d %d\n", x, y);
      fclose(fp);
    }

    vector<int> fulls;
    for (int x = 0; x < g.n; x++) if (g.deg(x) == 6) fulls.push_back(x);
    int nf = (int)fulls.size();
    vector<array<int,6>> nbOf(nf);
    for (int i = 0; i < nf; i++) {
      int k = 0; forNbr(g, fulls[i], [&](int u) { nbOf[i][k++] = u; return true; });
    }
    // ---- Stage L: locked set (with (2,2,2)-trace constraint) ----
    vector<int> lockedFlag(nf, 0);
    {
      atomic<int> next(0);
      vector<thread> th;
      for (int i = 0; i < nThreads; i++) th.emplace_back([&]() {
        for (;;) { int i2 = next.fetch_add(1); if (i2 >= nf) break;
          lockedFlag[i2] = (queryGen(g, fulls[i2], true, {}) == 0) ? 1 : 0; } });
      for (auto& t : th) t.join();
    }
    {
      string s; int cnt = 0;
      for (int i = 0; i < nf; i++) if (lockedFlag[i]) { cnt++; s += " " + to_string(fulls[i]); }
      printf("inst %d: fulls=%d lockedFull=%d at:%s\n", inst, nf, cnt, s.c_str());
      fflush(stdout);
    }
    // ---- Stage P: pairwise relations on N(v) in K-v, all full v ----
    // res[vi][p][0] = eqAch, [1] = diffAch
    vector<array<array<int8_t,2>,15>> res(nf);
    {
      atomic<int> next(0);
      int total = nf * 15 * 2;
      vector<thread> th;
      for (int i = 0; i < nThreads; i++) th.emplace_back([&]() {
        for (;;) { int id = next.fetch_add(1); if (id >= total) break;
          int vi = id / 30, rem = id % 30, p = rem / 2, ty = rem % 2;
          int v = fulls[vi];
          int x = nbOf[vi][PI[p][0]], y = nbOf[vi][PI[p][1]];
          int r = queryGen(g, v, false, {{x, 0}, {y, ty ? 1 : 0}});
          res[vi][p][ty] = (int8_t)r; } });
      for (auto& t : th) t.join();
    }
    // ---- evaluate certificates ----
    int unknownCalls = 0, badPairs = 0;
    int nEqAny = 0, nEqAnyLocked = 0, nNonedgeDiff = 0, nNonedgeDiffLocked = 0;
    int nF1 = 0, nF2 = 0, nF2locked = 0, nF2unlocked = 0;
    for (int vi = 0; vi < nf; vi++) {
      int v = fulls[vi];
      int rel[6][6]; memset(rel, 0, sizeof(rel));   // 0 free, 1 forcedEq, 2 forcedDiff, 3 unknown
      bool anyEq = false, anyNonedgeDiff = false, anyUnknown = false;
      string detail;
      for (int p = 0; p < 15; p++) {
        int i = PI[p][0], j = PI[p][1];
        int eq = res[vi][p][0], df = res[vi][p][1];
        if (eq == 2 || df == 2) { rel[i][j] = rel[j][i] = 3; anyUnknown = true; unknownCalls++; continue; }
        if (!eq && !df) { badPairs++; printf("inst %d v=%d PAIR(%d,%d) BOTH-UNSAT — BUG\n", inst, v, nbOf[vi][i], nbOf[vi][j]); }
        if (!df) { rel[i][j] = rel[j][i] = 1; anyEq = true;
          detail += " EQ{" + to_string(nbOf[vi][i]) + "," + to_string(nbOf[vi][j]) + "}"; }
        else if (!eq) { rel[i][j] = rel[j][i] = 2;
          bool isEdge = g.adj[nbOf[vi][i]].test(nbOf[vi][j]);
          if (!isEdge) { anyNonedgeDiff = true;
            detail += " DF{" + to_string(nbOf[vi][i]) + "," + to_string(nbOf[vi][j]) + "}"; } }
      }
      // F1: union-find on forcedEq pairs
      int par[6]; for (int i = 0; i < 6; i++) par[i] = i;
      function<int(int)> find = [&](int x) { return par[x] == x ? x : par[x] = find(par[x]); };
      for (int i = 0; i < 6; i++) for (int j = i + 1; j < 6; j++)
        if (rel[i][j] == 1) par[find(i)] = find(j);
      int csz[6] = {0,0,0,0,0,0};
      for (int i = 0; i < 6; i++) csz[find(i)]++;
      bool f1 = false; for (int i = 0; i < 6; i++) if (csz[i] >= 3) f1 = true;
      // F2: exists PM containing all forcedEq pairs, avoiding all forcedDiff pairs
      bool anyPM = false;
      for (auto& pm : PMs) {
        bool ok = true;
        for (int i = 0; i < 6 && ok; i++) for (int j = i + 1; j < 6 && ok; j++) {
          if (rel[i][j] == 1 && pm[i] != j) ok = false;            // forced-eq must be matched
          if (pm[i] == j && rel[i][j] == 2) ok = false;            // matched pair must not be forced-diff
        }
        if (ok) { anyPM = true; break; }
      }
      bool f2 = !anyPM;
      if (anyEq) { nEqAny++; if (lockedFlag[vi]) nEqAnyLocked++; }
      if (anyNonedgeDiff) { nNonedgeDiff++; if (lockedFlag[vi]) nNonedgeDiffLocked++; }
      if (f1) nF1++;
      if (f2) { nF2++; if (lockedFlag[vi]) nF2locked++; else nF2unlocked++; }
      if (anyEq || anyNonedgeDiff || f1 || f2 || anyUnknown)
        printf("inst %d v=%d locked=%d F1=%d F2=%d unknown=%d rel:%s\n",
               inst, v, lockedFlag[vi], f1 ? 1 : 0, f2 ? 1 : 0, anyUnknown ? 1 : 0, detail.c_str());
    }
    printf("inst %d AUDIT: fulls=%d | withForcedEqPairInN=%d (locked:%d) | withNonedgeForcedDiff=%d (locked:%d) | F1=%d F2=%d (F2locked=%d F2unlocked=%d) | unknownPairs=%d badPairs=%d\n",
           inst, nf, nEqAny, nEqAnyLocked, nNonedgeDiff, nNonedgeDiffLocked,
           nF1, nF2, nF2locked, nF2unlocked, unknownCalls, badPairs);
    fflush(stdout);
    // ---- Stage G (inst < 4): global forced relations in K itself ----
    if (inst < 4) {
      vector<pair<int,int>> nonadj;
      for (int x = 0; x < g.n; x++) for (int y = x + 1; y < g.n; y++)
        if (!g.adj[x].test(y)) nonadj.push_back({x, y});
      int np = (int)nonadj.size();
      vector<array<int8_t,2>> gres(np);
      atomic<int> next(0);
      int total = np * 2;
      vector<thread> th;
      for (int i = 0; i < nThreads; i++) th.emplace_back([&]() {
        for (;;) { int id = next.fetch_add(1); if (id >= total) break;
          int pi2 = id / 2, ty = id % 2;
          int x = nonadj[pi2].first, y = nonadj[pi2].second;
          gres[pi2][ty] = (int8_t)queryGen(g, -1, false, {{x, 0}, {y, ty ? 1 : 0}}); } });
      for (auto& t : th) t.join();
      int gEq = 0, gDf = 0, gUnk = 0;
      string eqList, dfList;
      for (int pi2 = 0; pi2 < np; pi2++) {
        int eq = gres[pi2][0], df = gres[pi2][1];
        if (eq == 2 || df == 2) { gUnk++; continue; }
        if (!df) { gEq++; eqList += " {" + to_string(nonadj[pi2].first) + "," + to_string(nonadj[pi2].second) + "}"; }
        else if (!eq) { gDf++; dfList += " {" + to_string(nonadj[pi2].first) + "," + to_string(nonadj[pi2].second) + "}"; }
      }
      printf("inst %d GLOBAL-K relations (nonadj pairs=%d): forcedEq=%d:%s | nonedgeForcedDiff=%d:%s | unknown=%d\n",
             inst, np, gEq, eqList.c_str(), gDf, dfList.c_str(), gUnk);
      fflush(stdout);
    }
    // ---- Stage S (inst 0): achievable trace-shape census per full v ----
    if (inst == 0) {
      vector<int> canonTau;
      for (int t = 0; t < NTAU; t++) if (canon6(t) == t) canonTau.push_back(t);
      int nc = (int)canonTau.size();
      vector<set<string>> shapes(nf);
      vector<mutex> mus(nf);
      atomic<int> next(0);
      int total = nf * nc;
      vector<thread> th;
      for (int i = 0; i < nThreads; i++) th.emplace_back([&]() {
        for (;;) { int id = next.fetch_add(1); if (id >= total) break;
          int vi = id / nc, ci = id % nc;
          int t = canonTau[ci], dig[6], tt = t;
          for (int s2 = 0; s2 < 6; s2++) { dig[s2] = tt % 3; tt /= 3; }
          vector<pair<int,int>> fixes;
          for (int s2 = 0; s2 < 6; s2++) fixes.push_back({nbOf[vi][s2], dig[s2]});
          if (queryGen(g, fulls[vi], false, fixes) == 1) {
            int cnt3[3] = {0,0,0};
            for (int s2 = 0; s2 < 6; s2++) cnt3[dig[s2]]++;
            sort(cnt3, cnt3 + 3, greater<int>());
            string sh;
            for (int c = 0; c < 3; c++) if (cnt3[c]) sh += ('0' + cnt3[c]);
            lock_guard<mutex> lk(mus[vi]);
            shapes[vi].insert(sh);
          } } });
      for (auto& t : th) t.join();
      // aggregate: locked vs unlocked shape-set histogram
      for (int vi = 0; vi < nf; vi++) {
        string s;
        for (auto& sh : shapes[vi]) s += " " + sh;
        printf("inst 0 SHAPES v=%d locked=%d :%s\n", fulls[vi], lockedFlag[vi], s.c_str());
      }
      fflush(stdout);
    }
  }
  return 0;
}
