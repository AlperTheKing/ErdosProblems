// robust-(FK) test on H* = PG(2,5) incidence minus edges (0,32),(7,41),(15,33).
// (2026-06-12; round-2 digest formalism, piece P=(V,E,S,a,b) with b=0, |S|=6,
// anchors = the six degree-5 vertices.)
//
// gamma in [3]^6 = colours of the OUTSIDE stub endpoints.
//  - gamma COMPATIBLE  <=> exists proper 3-col tau of H* with tau(anchor_s) != gamma_s for all s.
//  - full v SERVED for gamma <=> exists proper 3-col of H*-v with exactly (2,2,2)
//    on N(v) and anchor colours avoiding gamma componentwise.
// H* ROBUSTLY INTERNALLY UNFROZEN <=> every compatible gamma serves every full v.
// A starved (gamma, v) = a completion-class in which v is frozen => robust-(FK) lives.
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
static int ANCH[6];                              // sorted degree-5 vertices
static int DEG[N];

enum R { FOUND, NONE, CAPPED };

// proper 3-col of H* minus del (-1 = none); forbid[x] = bitmask of banned colours;
// if del>=0, require exactly (2,2,2) on N(del). Node cap.
static R search(int del, const uint8_t* forbid, uint64_t cap) {
  vector<int> order;
  uint64_t seen = 0, nbv = 0;
  if (del >= 0) {
    seen = 1ull << del; nbv = ADJ[del];
    for (int x = 0; x < N; x++) if (nbv >> x & 1) { order.push_back(x); seen |= 1ull << x; }
  }
  for (int s = 0; s < 6; s++)                    // anchors early: forbid-pruning bites first
    if (!(seen >> ANCH[s] & 1)) { order.push_back(ANCH[s]); seen |= 1ull << ANCH[s]; }
  for (size_t h = 0; h < order.size(); h++) {
    uint64_t nb = ADJ[order[h]] & ~seen;
    while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1; order.push_back(u); seen |= 1ull << u; }
  }
  for (int x = 0; x < N; x++) if (!(seen >> x & 1)) order.push_back(x);
  int m = (int)order.size();
  int8_t col[N]; memset(col, -1, sizeof(col));
  int8_t tryc[N]; memset(tryc, 0, sizeof(tryc));
  int cnt[3] = {0,0,0};
  uint64_t nodes = 0;
  int pos = 0;
  while (pos >= 0) {
    if (pos == m) return FOUND;
    if (++nodes > cap) return CAPPED;
    int x = order[pos];
    bool onN = del >= 0 && (nbv >> x & 1);
    bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      if (forbid[x] >> c & 1) continue;
      if (onN && cnt[c] == 2) continue;
      bool ok = true;
      uint64_t nb = ADJ[x];
      while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1;
        if (u != del && col[u] == c) { ok = false; break; } }
      if (!ok) continue;
      col[x] = c; if (onN) cnt[c]++;
      tryc[pos] = c + 1;
      pos++; if (pos < m) tryc[pos] = 0;
      adv = true; break;
    }
    if (!adv) {
      tryc[pos] = 0; pos--;
      if (pos >= 0) { int y = order[pos]; if (del >= 0 && (nbv >> y & 1)) cnt[col[y]]--; col[y] = -1; }
    }
  }
  return NONE;
}

int main(int argc, char** argv) {
  int gLo = 0, gHi = 729;                        // optional gamma chunk [gLo,gHi)
  if (argc >= 3) { gLo = atoi(argv[1]); gHi = atoi(argv[2]); }
  // build H*
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
  printf("anchors:"); for (int s = 0; s < 6; s++) printf(" %d", ANCH[s]); printf(" (na=%d)\n", na);

  static const int POW3[7] = {1,3,9,27,81,243,729};
  // phase A: compatibility of each gamma
  vector<int8_t> compat(729, -1);
  {
    atomic<int> next(0);
    auto wk = [&]() {
      for (;;) { int g = next.fetch_add(1); if (g >= 729) break;
        uint8_t forbid[N]; memset(forbid, 0, sizeof(forbid));
        for (int s = 0; s < 6; s++) forbid[ANCH[s]] = 1 << (g / POW3[s] % 3);
        R r = search(-1, forbid, 1ull << 33);
        compat[g] = r == FOUND ? 1 : (r == NONE ? 0 : 2);
      }
    };
    vector<thread> th; for (int i = 0; i < 64; i++) th.emplace_back(wk);
    for (auto& t : th) t.join();
  }
  int nC = 0, nI = 0, nCap = 0;
  for (int g = 0; g < 729; g++) { if (compat[g] == 1) nC++; else if (compat[g] == 0) nI++; else nCap++; }
  printf("phase A: compatible=%d incompatible=%d capped=%d / 729\n", nC, nI, nCap);
  fflush(stdout);

  // phase B: for each compatible gamma x full v, witness avoiding gamma
  vector<int> fulls;
  for (int x = 0; x < N; x++) if (DEG[x] == 6) fulls.push_back(x);
  int NF = (int)fulls.size();
  printf("full vertices: %d => %d (gamma,v) searches\n", NF, nC * NF);
  fflush(stdout);
  atomic<long long> nServed(0), nStarved(0), nCap2(0);
  mutex mu; string starvedList, capList;
  {
    atomic<int> next(gLo * NF), done(0);
    auto wk = [&]() {
      for (;;) { int idx = next.fetch_add(1); if (idx >= gHi * NF) break;
        int g = idx / NF, v = fulls[idx % NF];
        if (compat[g] != 1) continue;
        uint8_t forbid[N]; memset(forbid, 0, sizeof(forbid));
        for (int s = 0; s < 6; s++) forbid[ANCH[s]] = 1 << (g / POW3[s] % 3);
        R r = search(v, forbid, 1ull << 28);
        if (r == FOUND) nServed++;
        else if (r == NONE) { nStarved++; lock_guard<mutex> lk(mu);
          starvedList += " (" + to_string(g) + "," + to_string(v) + ")"; }
        else { nCap2++; lock_guard<mutex> lk(mu);
          capList += " (" + to_string(g) + "," + to_string(v) + ")"; }
        int d = done.fetch_add(1) + 1;
        if (d % 2048 == 0) { printf("  ...%d/%d\n", d, (gHi - gLo) * NF); fflush(stdout); }
      }
    };
    vector<thread> th; for (int i = 0; i < 64; i++) th.emplace_back(wk);
    for (auto& t : th) t.join();
  }
  printf("gamma chunk [%d,%d)\n", gLo, gHi);
  printf("phase B: served=%lld starved=%lld capped=%lld\n",
         nServed.load(), nStarved.load(), nCap2.load());
  if (nStarved) printf("STARVED pairs:%s\n", starvedList.c_str());
  if (nCap2) printf("CAPPED pairs:%s\n", capList.c_str());
  printf("VERDICT: %s\n",
         nStarved == 0 && nCap2 == 0 && nCap == 0
           ? "H* ROBUSTLY INTERNALLY UNFROZEN — freezing mechanism can NEVER kill this shore"
           : (nStarved > 0 ? "NOT robust — starved (gamma,v) pairs exist => robust-(FK) lives"
                           : "INCONCLUSIVE (caps hit)"));
  return 0;
}
