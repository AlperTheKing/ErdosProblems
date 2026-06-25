// robust-(FK) test on H*, engine v2: MRV + forward checking + colour-orbit dedup.
// Semantics identical to robust_fk.cpp:
//   gamma in [3]^6 (outside stub-endpoint colours), anchors = degree-5 vertices.
//   compat(gamma): exists proper 3-col of H* with anchor colours avoiding gamma.
//   served(gamma,v): exists proper 3-col of H*-v, exactly (2,2,2) on N(v),
//                    anchor colours avoiding gamma.
// Both predicates are invariant under simultaneous colour permutation of gamma,
// so only canonical gammas (min over the 6 perms) are solved; verdicts lift to orbits.
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <array>
#include <thread>
#include <atomic>
#include <mutex>
using namespace std;

static const int N = 62;
static uint64_t ADJ[N];
static int ANCH[6], DEG[N];

enum R { FOUND, NONE, CAPPED };

struct Solver {
  int del; uint64_t nbv;
  uint8_t dom[N]; int8_t col[N];
  int cnt[3];
  vector<pair<int,uint8_t>> trail;               // (vertex, previous dom)
  uint64_t nodes = 0, cap;

  bool shrink(int u, uint8_t bit) {              // remove colours `bit` from dom[u]
    if (!(dom[u] & bit)) return true;
    trail.push_back({u, dom[u]});
    dom[u] &= ~bit;
    return dom[u] != 0;
  }
  R solve() {
    if (++nodes > cap) return CAPPED;
    // MRV
    int x = -1, best = 4;
    for (int u = 0; u < N; u++)
      if (u != del && col[u] < 0) {
        int p = __builtin_popcount(dom[u]);
        if (p < best) { best = p; x = u; if (p <= 1) break; }
      }
    if (x < 0) return FOUND;                     // all coloured
    size_t mark0 = trail.size();
    for (int c = 0; c < 3; c++) {
      if (!(dom[x] >> c & 1)) continue;
      bool ok = true;
      size_t mark = trail.size();
      col[x] = c;
      bool onN = del >= 0 && (nbv >> x & 1);
      if (onN) {
        cnt[c]++;
        if (cnt[c] == 2) {                       // colour saturated on N(del)
          uint64_t nb = nbv;
          while (nb) { int w = __builtin_ctzll(nb); nb &= nb - 1;
            if (w != x && col[w] < 0 && !shrink(w, 1 << c)) { ok = false; break; } }
        }
      }
      if (ok) {
        uint64_t nb = ADJ[x];
        while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1;
          if (u != del && col[u] < 0 && !shrink(u, 1 << c)) { ok = false; break; } }
      }
      if (ok) {
        R r = solve();
        if (r != NONE) { return r; }             // FOUND or CAPPED propagate up
      }
      // undo
      while (trail.size() > mark) { dom[trail.back().first] = trail.back().second; trail.pop_back(); }
      if (onN) cnt[c]--;
      col[x] = -1;
    }
    (void)mark0;
    return NONE;
  }
};

static R query(int del, int gamma, uint64_t cap) {
  static const int POW3[7] = {1,3,9,27,81,243,729};
  Solver s; s.del = del; s.nbv = del >= 0 ? ADJ[del] : 0; s.cap = cap;
  s.cnt[0] = s.cnt[1] = s.cnt[2] = 0;
  memset(s.col, -1, sizeof(s.col));
  for (int u = 0; u < N; u++) s.dom[u] = 7;
  for (int sIdx = 0; sIdx < 6; sIdx++) {
    int banned = gamma / POW3[sIdx] % 3;
    s.dom[ANCH[sIdx]] &= ~(1 << banned);
  }
  if (del >= 0) s.col[del] = 3;                  // mark as handled (never selected: col>=0)
  return s.solve();
}

static int canonical(int g) {                    // min over simultaneous colour perms
  static const int P[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
  static const int POW3[7] = {1,3,9,27,81,243,729};
  int best = 99999;
  for (auto& p : P) {
    int h = 0, t = g;
    for (int s = 0; s < 6; s++) { h += p[t % 3] * POW3[s]; t /= 3; }
    if (h < best) best = h;
  }
  return best;
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
  printf("anchors:"); for (int s = 0; s < 6; s++) printf(" %d", ANCH[s]); printf("\n");

  vector<int> canon;
  for (int g = 0; g < 729; g++) if (canonical(g) == g) canon.push_back(g);
  printf("canonical gammas: %d / 729\n", (int)canon.size());

  vector<int> fulls;
  for (int x = 0; x < N; x++) if (DEG[x] == 6) fulls.push_back(x);
  int NF = (int)fulls.size(), NG = (int)canon.size();

  // phase A
  vector<int8_t> compat(NG, -1);
  {
    atomic<int> next(0);
    auto wk = [&]() { for (;;) { int i = next.fetch_add(1); if (i >= NG) break;
      R r = query(-1, canon[i], 200000000ull);
      compat[i] = r == FOUND ? 1 : (r == NONE ? 0 : 2); } };
    vector<thread> th; for (int i = 0; i < 64; i++) th.emplace_back(wk);
    for (auto& t : th) t.join();
  }
  int nC = 0;
  for (int i = 0; i < NG; i++) if (compat[i] == 1) nC++;
  printf("phase A: compatible=%d / %d canonical (others:", nC, NG);
  for (int i = 0; i < NG; i++) if (compat[i] != 1) printf(" g%d=%s", canon[i], compat[i] == 0 ? "INC" : "CAP");
  printf(")\n"); fflush(stdout);

  // phase B
  atomic<long long> nServed(0), nStarved(0), nCap(0);
  atomic<int> done(0);
  mutex mu; string starved, capped;
  {
    atomic<int> next(0);
    auto wk = [&]() { for (;;) { int idx = next.fetch_add(1); if (idx >= NG * NF) break;
      int gi = idx / NF, v = fulls[idx % NF];
      if (compat[gi] != 1) continue;
      R r = query(v, canon[gi], 200000000ull);
      if (r == FOUND) nServed++;
      else if (r == NONE) { nStarved++; lock_guard<mutex> lk(mu);
        starved += " (" + to_string(canon[gi]) + "," + to_string(v) + ")"; }
      else { nCap++; lock_guard<mutex> lk(mu);
        capped += " (" + to_string(canon[gi]) + "," + to_string(v) + ")"; }
      int d = done.fetch_add(1) + 1;
      if (d % 1024 == 0) { printf("  ...%d/%d\n", d, nC * NF); fflush(stdout); } } };
    vector<thread> th; for (int i = 0; i < 64; i++) th.emplace_back(wk);
    for (auto& t : th) t.join();
  }
  printf("phase B (canonical): served=%lld starved=%lld capped=%lld\n",
         nServed.load(), nStarved.load(), nCap.load());
  if (nStarved) printf("STARVED:%s\n", starved.c_str());
  if (nCap) printf("CAPPED:%s\n", capped.c_str());
  printf("VERDICT: %s\n",
         nStarved == 0 && nCap == 0
           ? "H* ROBUSTLY INTERNALLY UNFROZEN (freezing can never kill this shore)"
           : (nStarved ? "NOT robust — robust-(FK) lives" : "INCONCLUSIVE (caps)"));
  return 0;
}
