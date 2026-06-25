// Self-pairing experiment for H* = PG(2,5) - 3 disjoint edges (2026-06-12).
// G(pi) = H1* u H2* + 6 cut edges (a, pi(a)) anchor-to-anchor => 6-regular, 124 vtcs.
//
// Tables on H* (exact anchor traces tau in [3]^6, anchors sorted {0,7,15,32,33,41}):
//  Col          = { tau : some proper 3-col of H* has anchor trace tau }
//  UnfTrace(v)  = { tau : some proper 3-col of H*-v with exactly (2,2,2) on N(v) has trace tau }   (v full)
//  AnchorWit(a) = { (tau5, j) : some proper 3-col of H*-a with counts (2,2,2)-e_j on N(a)
//                   has trace tau5 on the OTHER 5 anchors }                                          (a anchor)
// All predicates are equivariant under simultaneous colour permutation => solve canonical
// representatives, close orbits.
//
// Matching scan, for each pi of 720:
//  G(pi) 3-colourable        <=> exists tau in Col, gamma in Col: tau_s != gamma_{pi(s)} all s
//  interior v in H1 served    <=> exists tau in UnfTrace(v), gamma in Col: tau perp_pi gamma
//  anchor a in H1 served      <=> exists (tau5,j) in AnchorWit(a), gamma in Col:
//                                  gamma_{pi(a)} = j and tau5_s != gamma_{pi(s)} for s != a
//  (H2 symmetric: same tables with pi^{-1}; checked explicitly.)
// CANDIDATE criticality screen: NOT 3-colourable AND all 124 vertices served.
//
// Internal consistency assertion: phase-B verdicts of robust_fk2 re-derived from
// UnfTrace tables for sampled (gamma, v): served <=> exists tau in UnfTrace(v) avoiding gamma.
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <array>
#include <thread>
#include <atomic>
#include <mutex>
#include <bitset>
#include <algorithm>
using namespace std;

static const int N = 62, NTAU = 729;
static uint64_t ADJ[N];
static int ANCH[6], DEG[N];
static const int POW3[7] = {1,3,9,27,81,243,729};

struct Solver {
  int del; uint64_t nbv;
  uint8_t dom[N]; int8_t col[N];
  int cnt[3]; int capv[3];
  vector<pair<int,uint8_t>> trail;
  uint64_t nodes = 0, cap;
  bool shrink(int u, uint8_t bit) {
    if (!(dom[u] & bit)) return true;
    trail.push_back({u, dom[u]});
    dom[u] &= ~bit;
    return dom[u] != 0;
  }
  int solve() {                                  // 1 found, 0 none, 2 capped
    if (++nodes > cap) return 2;
    int x = -1, best = 4;
    for (int u = 0; u < N; u++)
      if (col[u] < 0) { int p = __builtin_popcount(dom[u]);
        if (p < best) { best = p; x = u; if (p <= 1) break; } }
    if (x < 0) return 1;
    for (int c = 0; c < 3; c++) {
      if (!(dom[x] >> c & 1)) continue;
      bool ok = true;
      size_t mark = trail.size();
      col[x] = c;
      bool onN = del >= 0 && (nbv >> x & 1);
      if (onN) {
        cnt[c]++;
        if (cnt[c] == capv[c]) {
          uint64_t nb = nbv;
          while (nb) { int w = __builtin_ctzll(nb); nb &= nb - 1;
            if (w != x && col[w] < 0 && !shrink(w, 1 << c)) { ok = false; break; } }
        } else if (cnt[c] > capv[c]) ok = false;
      }
      if (ok) {
        uint64_t nb = ADJ[x];
        while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1;
          if (col[u] < 0 && !shrink(u, 1 << c)) { ok = false; break; } }
      }
      if (ok) { int r = solve(); if (r) return r; }
      while (trail.size() > mark) { dom[trail.back().first] = trail.back().second; trail.pop_back(); }
      if (onN) cnt[c]--;
      col[x] = -1;
    }
    return 0;
  }
};

// query: del=-1 plain / del=v full / del=a anchor; fixTrace: anchor s -> colour or -1 (skip);
// caps = per-colour count caps on N(del)
static int query(int del, const int* fixTrace, const int* caps) {
  Solver s; s.del = del; s.nbv = del >= 0 ? ADJ[del] : 0; s.cap = 400000000ull;
  for (int c = 0; c < 3; c++) { s.cnt[c] = 0; s.capv[c] = caps ? caps[c] : 3; }
  memset(s.col, -1, sizeof(s.col));
  for (int u = 0; u < N; u++) s.dom[u] = 7;
  for (int i = 0; i < 6; i++)
    if (fixTrace[i] >= 0 && ANCH[i] != del) s.dom[ANCH[i]] = 1 << fixTrace[i];
  if (del >= 0) s.col[del] = 3;
  return s.solve();
}

static int canon6(int g) {
  static const int P[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
  int best = 99999;
  for (auto& p : P) { int h = 0, t = g;
    for (int s = 0; s < 6; s++) { h += p[t % 3] * POW3[s]; t /= 3; }
    if (h < best) best = h; }
  return best;
}
static void orbit6(int g, vector<int>& out) {
  static const int P[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
  out.clear();
  for (auto& p : P) { int h = 0, t = g;
    for (int s = 0; s < 6; s++) { h += p[t % 3] * POW3[s]; t /= 3; }
    out.push_back(h); }
}
// joint canonical for (tau5, j): encode as tau5 + j*243
static int canon53(int code) {
  static const int P[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
  int best = 99999;
  for (auto& p : P) { int t = code % 243, h = p[code / 243] * 243;
    for (int s = 0; s < 5; s++) { h += p[t % 3] * POW3[s]; t /= 3; }
    if (h < best) best = h; }
  return best;
}
static void orbit53(int code, vector<int>& out) {
  static const int P[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
  out.clear();
  for (auto& p : P) { int t = code % 243, h = p[code / 243] * 243;
    for (int s = 0; s < 5; s++) { h += p[t % 3] * POW3[s]; t /= 3; }
    out.push_back(h); }
}

int main() {
  vector<array<int,3>> reps;
  for (int a = 0; a < 5; a++) for (int b = 0; b < 5; b++) for (int c = 0; c < 5; c++) {
    if (!a && !b && !c) continue;
    if ((a && a != 1) || (!a && b && b != 1) || (!a && !b && c != 1)) continue;
    reps.push_back({a, b, c});
  }
  memset(ADJ, 0, sizeof(ADJ));
  for (int i = 0; i < 31; i++) for (int j = 0; j < 31; j++) {
    int dot = reps[i][0]*reps[j][0] + reps[i][1]*reps[j][1] + reps[i][2]*reps[j][2];
    if (dot % 5 == 0) { ADJ[i] |= 1ull << (31 + j); ADJ[31 + j] |= 1ull << i; }
  }
  int dels[3][2] = {{0,32},{7,41},{15,33}};
  for (auto& d : dels) { ADJ[d[0]] &= ~(1ull << d[1]); ADJ[d[1]] &= ~(1ull << d[0]); }
  int na = 0;
  for (int x = 0; x < N; x++) { DEG[x] = __builtin_popcountll(ADJ[x]); if (DEG[x] == 5) ANCH[na++] = x; }
  vector<int> fulls;
  for (int x = 0; x < N; x++) if (DEG[x] == 6) fulls.push_back(x);
  int NF = (int)fulls.size();

  // ---------------- build tables (canonical solve + orbit closure) ----------
  static bitset<NTAU> Col;
  static bitset<NTAU> Unf[56];
  static bitset<729 * 3> AWit[6];                // code = tau5 + 243*j
  long long nQ = 0, nCap = 0;

  vector<int> canonTau;
  for (int t = 0; t < NTAU; t++) if (canon6(t) == t) canonTau.push_back(t);
  vector<int> canon53s;
  for (int c = 0; c < 729; c++) if (canon53(c) == c) canon53s.push_back(c);
  // jobs: (kind, idx, code) kind0=Col, kind1=Unf(fulls[idx]), kind2=AWit(idx anchor)
  struct Job { int kind, idx, code; };
  vector<Job> jobs;
  for (int t : canonTau) jobs.push_back({0, 0, t});
  for (int i = 0; i < NF; i++) for (int t : canonTau) jobs.push_back({1, i, t});
  for (int a = 0; a < 6; a++) for (int c : canon53s) jobs.push_back({2, a, c});
  printf("jobs: %d (Col %d + Unf %d + AWit %d)\n", (int)jobs.size(),
         (int)canonTau.size(), NF * (int)canonTau.size(), 6 * (int)canon53s.size());
  fflush(stdout);

  mutex mu;
  atomic<int> next(0), done(0);
  atomic<long long> caps(0);
  auto wk = [&]() {
    vector<int> orb;
    for (;;) {
      int i = next.fetch_add(1); if (i >= (int)jobs.size()) break;
      Job& J = jobs[i];
      int fix[6], capsArr[3] = {2,2,2}, r;
      if (J.kind == 0) {
        int t = J.code;
        for (int s = 0; s < 6; s++) { fix[s] = t % 3; t /= 3; }
        r = query(-1, fix, nullptr);
        if (r == 1) { orbit6(J.code, orb); lock_guard<mutex> lk(mu); for (int o : orb) Col.set(o); }
      } else if (J.kind == 1) {
        int t = J.code;
        for (int s = 0; s < 6; s++) { fix[s] = t % 3; t /= 3; }
        r = query(fulls[J.idx], fix, capsArr);
        if (r == 1) { orbit6(J.code, orb); lock_guard<mutex> lk(mu); for (int o : orb) Unf[J.idx].set(o); }
      } else {
        int a = J.idx, t5 = J.code % 243, j = J.code / 243, k = 0;
        int c2[3] = {2,2,2}; c2[j] = 1;
        for (int s = 0; s < 6; s++) {
          if (s == a) { fix[s] = -1; continue; }
          fix[s] = (t5 / POW3[k]) % 3; k++;
        }
        r = query(ANCH[a], fix, c2);
        if (r == 1) { orbit53(J.code, orb); lock_guard<mutex> lk(mu); for (int o : orb) AWit[a].set(o); }
      }
      if (r == 2) caps++;
      int d = done.fetch_add(1) + 1;
      if (d % 2048 == 0) { printf("  ...%d/%d\n", d, (int)jobs.size()); fflush(stdout); }
    }
  };
  { vector<thread> th; for (int i = 0; i < 64; i++) th.emplace_back(wk);
    for (auto& t : th) t.join(); }
  nQ = jobs.size(); nCap = caps.load();
  printf("tables built: |Col|=%d, capped=%lld/%lld\n", (int)Col.count(), nCap, nQ);
  for (int i = 0; i < NF; i++) if (Unf[i].none()) printf("  WARNING Unf empty v=%d\n", fulls[i]);
  for (int a = 0; a < 6; a++) printf("  |AWit(%d)|=%d", ANCH[a], (int)AWit[a].count());
  printf("\n"); fflush(stdout);

  // -------- Avoid-coverage: which gamma are avoided by SOME tau in Col? ------
  // If Avoid(Col) = all 729 (for every matching-relabelling), then ANY partner
  // shore K with nonempty Col gives a 3-colourable pairing under every matching
  // => H* can never be a shore of a 4-critical graph at all.
  {
    static bitset<NTAU> av;                      // identity labelling
    for (int t = 0; t < NTAU; t++) {
      if (!Col[t]) continue;
      int ch[6][2];
      for (int s = 0; s < 6; s++) { int c = (t / POW3[s]) % 3, k = 0;
        for (int x = 0; x < 3; x++) if (x != c) ch[s][k++] = x; }
      for (int msk = 0; msk < 64; msk++) { int g = 0;
        for (int s = 0; s < 6; s++) g += ch[s][msk >> s & 1] * POW3[s];
        av.set(g); }
    }
    printf("Avoid(Col) coverage (identity labelling): %d/729%s\n", (int)av.count(),
           av.count() == NTAU ? " — FULL: H* can NEVER be a critical-graph shore (any partner, any matching)" : "");
    if (av.count() != NTAU) { printf("  uncovered gammas:");
      for (int g = 0; g < NTAU; g++) if (!av[g]) printf(" %d", g); printf("\n"); }
  }
  // -------- consistency check vs robust_fk2 phase B (sampled) ---------------
  // served(gamma,v) <=> exists tau in Unf(v) with tau_s != gamma_s for all s
  auto servedAvoid = [&](int gamma, int vi) {
    for (int t = 0; t < NTAU; t++) {
      if (!Unf[vi][t]) continue;
      int a = t, b = gamma; bool ok = true;
      for (int s = 0; s < 6; s++) { if (a % 3 == b % 3) { ok = false; break; } a /= 3; b /= 3; }
      if (ok) return true;
    }
    return false;
  };
  int vi31 = -1, vi1 = -1;
  for (int i = 0; i < NF; i++) { if (fulls[i] == 31) vi31 = i; if (fulls[i] == 1) vi1 = i; }
  printf("consistency: (5,31) starved? %s (expect yes) | (5,1) served? %s (expect yes) | (0,1) served? %s (expect yes)\n",
         servedAvoid(5, vi31) ? "NO-MISMATCH!" : "yes", servedAvoid(5, vi1) ? "yes" : "NO-MISMATCH!",
         servedAvoid(0, vi1) ? "yes" : "NO-MISMATCH!");
  fflush(stdout);

  // ---------------- matching scan -------------------------------------------
  // pi: H1 stub s -> H2 stub pi[s]. gammaP = gamma re-indexed: gammaP_s = gamma_{pi(s)}.
  int perm[6] = {0,1,2,3,4,5};
  vector<int> ColList;
  for (int t = 0; t < NTAU; t++) if (Col[t]) ColList.push_back(t);
  int nAlive = 0, n3col = 0, bestUnserved = 999; string bestDesc;
  vector<int> digits(6);
  do {
    // TauOK[t] = exists gammaP differing everywhere
    static bitset<NTAU> TauOK; TauOK.reset();
    static bitset<729 * 3> Tau5OK[6];
    for (int a = 0; a < 6; a++) Tau5OK[a].reset();
    for (int g : ColList) {
      int gp = 0;
      for (int s = 0; s < 6; s++) gp += ((g / POW3[perm[s]]) % 3) * POW3[s];
      // mark all tau differing from gp everywhere: product of 2 choices per coord
      int ch[6][2];
      for (int s = 0; s < 6; s++) { int c = (gp / POW3[s]) % 3, k = 0;
        for (int x = 0; x < 3; x++) if (x != c) ch[s][k++] = x; }
      for (int msk = 0; msk < 64; msk++) {
        int t = 0;
        for (int s = 0; s < 6; s++) t += ch[s][msk >> s & 1] * POW3[s];
        TauOK.set(t);
      }
      // anchor variant: for anchor a: gammaP_a = j fixed = (gp/POW3[a])%3; tau5 over s!=a
      for (int a = 0; a < 6; a++) {
        int j = (gp / POW3[a]) % 3;
        for (int msk = 0; msk < 32; msk++) {
          int t5 = 0, k = 0, mb = 0;
          for (int s = 0; s < 6; s++) { if (s == a) continue;
            t5 += ch[s][msk >> mb & 1] * POW3[k]; k++; mb++; }
          Tau5OK[a].set(t5 + 243 * j);
        }
      }
    }
    bool g3 = false;
    for (int t : ColList) if (TauOK[t]) { g3 = true; break; }
    int unserved = 0; string who;
    for (int i = 0; i < NF; i++) {                       // H1 interior (H2 symmetric by pi^-1; tables equal)
      if ((Unf[i] & TauOK).none()) { unserved++; who += " v" + to_string(fulls[i]); }
    }
    for (int a = 0; a < 6; a++)
      if ((AWit[a] & Tau5OK[a]).none()) { unserved++; who += " a" + to_string(ANCH[a]); }
    // H2 side: pi^{-1}: by symmetry of construction (same tables), repeat with inverse perm
    int iperm[6]; for (int s = 0; s < 6; s++) iperm[perm[s]] = s;
    static bitset<NTAU> TauOK2; TauOK2.reset();
    static bitset<729 * 3> Tau5OK2[6];
    for (int a = 0; a < 6; a++) Tau5OK2[a].reset();
    for (int g : ColList) {
      int gp = 0;
      for (int s = 0; s < 6; s++) gp += ((g / POW3[iperm[s]]) % 3) * POW3[s];
      int ch[6][2];
      for (int s = 0; s < 6; s++) { int c = (gp / POW3[s]) % 3, k = 0;
        for (int x = 0; x < 3; x++) if (x != c) ch[s][k++] = x; }
      for (int msk = 0; msk < 64; msk++) { int t = 0;
        for (int s = 0; s < 6; s++) t += ch[s][msk >> s & 1] * POW3[s];
        TauOK2.set(t); }
      for (int a = 0; a < 6; a++) {
        int j = (gp / POW3[a]) % 3;
        for (int msk = 0; msk < 32; msk++) { int t5 = 0, k = 0, mb = 0;
          for (int s = 0; s < 6; s++) { if (s == a) continue;
            t5 += ch[s][msk >> mb & 1] * POW3[k]; k++; mb++; }
          Tau5OK2[a].set(t5 + 243 * j); }
      }
    }
    for (int i = 0; i < NF; i++)
      if ((Unf[i] & TauOK2).none()) { unserved++; who += " V" + to_string(fulls[i]); }
    for (int a = 0; a < 6; a++)
      if ((AWit[a] & Tau5OK2[a]).none()) { unserved++; who += " A" + to_string(ANCH[a]); }

    if (g3) n3col++;
    if (!g3 && unserved == 0) {
      nAlive++;
      printf("!! ALIVE NON-3COL MATCHING: pi = %d%d%d%d%d%d\n",
             perm[0], perm[1], perm[2], perm[3], perm[4], perm[5]);
    }
    if (unserved < bestUnserved) { bestUnserved = unserved;
      char buf[32]; snprintf(buf, 32, "%d%d%d%d%d%d", perm[0],perm[1],perm[2],perm[3],perm[4],perm[5]);
      bestDesc = string(buf) + " g3=" + (g3 ? "Y" : "N") + " unserved=" + to_string(unserved) + who.substr(0, 200); }
  } while (next_permutation(perm, perm + 6));
  printf("matching scan: 720 pi's | 3-colourable: %d | alive-non-3col (candidate): %d\n", n3col, nAlive);
  printf("best (fewest unserved): %s\n", bestDesc.c_str());
  printf("VERDICT: %s\n", nAlive
    ? "CANDIDATE FOUND — escalate to 4-VC screens"
    : (n3col == 720 ? "all pairings 3-colourable => self-pairing cannot be critical (Col too rich)"
                    : "no candidate: every non-3col pairing has an unserved (frozen) vertex => robust-(FK) evidence"));
  return 0;
}
