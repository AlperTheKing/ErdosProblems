// FK-simulation stage 1: robust-internal-unfrozen test (GPT round-2 Sec 3.6,
// audited digest gpt_fk_round2_digest_2026-06-12.md).
//
// A piece Q (b == 0, stubs = 6 - deg at each vertex) is ROBUSTLY INTERNALLY
// UNFROZEN if for EVERY outside stub assignment beta : S -> [3] such that some
// proper 3-colouring phi of Q has phi(a(s)) != beta(s) for all s (outside is
// compatible), and EVERY vertex q of Q, there exists a proper 3-colouring
// phi_q of Q - q with:
//   - phi_q(a(s)) != beta(s) for every stub s not anchored at q,
//   - colour counts of {phi_q(x) : x in N_Q(q)} u {beta(s) : s in S_q}
//     exactly (2,2,2).
// Such a Q can replace any same-Col-state larger piece P in an all-unfrozen
// minimal shore without destroying unfrozenness inside Q (replacement lemma).
//
// usage: fk_sim_check < pieces_file
//   reads STATE lines (from piece_enum), groups by canonical state, and for
//   every cross-size group tests the smallest member; prints per-piece verdict
//   ROBUST g6=... (group sizes) or NOTROBUST g6=... reason=beta,q
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <iostream>
using namespace std;
static const int MAXV = 16;

struct G { int n; uint32_t adj[MAXV]; int deg(int u) const { return __builtin_popcount(adj[u]); } };

static bool g6decode(const string& line, G& g) {
  if (line.empty()) return false;
  g.n = line[0] - 63;
  if (g.n < 1 || g.n > MAXV) return false;
  memset(g.adj, 0, sizeof(g.adj));
  int nbits = g.n*(g.n-1)/2, need = (nbits+5)/6;
  if ((int)line.size() < 1 + need) return false;
  int bit = 0;
  for (int j = 1; j < g.n; j++) for (int i = 0; i < j; i++) {
    int byte = 1 + bit/6, off = 5 - bit%6;
    if ((line[byte]-63) >> off & 1) { g.adj[i] |= 1u<<j; g.adj[j] |= 1u<<i; }
    bit++;
  }
  return true;
}

// stubs: per vertex s(x) = 6 - deg(x); stub list in vertex order
struct Stubs { vector<int> anchor; };   // stub index -> vertex
static Stubs stubsOf(const G& g) {
  Stubs S;
  for (int x = 0; x < g.n; x++) { int s = 6 - g.deg(x); for (int i = 0; i < s; i++) S.anchor.push_back(x); }
  return S;
}
static long long ipow3(int k) { long long r=1; while (k--) r*=3; return r; }

// does Q have a proper colouring with phi(a(s)) != beta(s) for all s in 'req'
// (req: per-stub outside colours; -1 = unconstrained), optionally deleting
// vertex del; if del >= 0 also require counts(N(del) internal phi + etaSum)
// == (2,2,2) where etaCnt[c] = count of outside colours at del's stubs.
static bool existsColouring(const G& g, const Stubs& S, const vector<int>& beta,
                            int del, const int* etaCnt) {
  // forbidden colours per vertex from beta (vertex may have several stubs)
  uint8_t forb[MAXV]; memset(forb, 0, sizeof(forb));     // bitmask of banned colours
  for (size_t s = 0; s < S.anchor.size(); s++) {
    int a = S.anchor[s];
    if (a == del) continue;                              // stubs at deleted vertex: eta, not constraint
    if (beta[s] >= 0) forb[a] |= 1 << beta[s];
  }
  int order[MAXV], m = 0;
  for (int x = 0; x < g.n; x++) if (x != del) order[m++] = x;
  // N(del) first for early count pruning
  if (del >= 0) {
    int front = 0;
    for (int i = 0; i < m; i++) if ((g.adj[del] >> order[i]) & 1) swap(order[front++], order[i]);
  }
  int nDel = del >= 0 ? __builtin_popcount(g.adj[del]) : 0;
  int8_t col[MAXV]; memset(col, -1, sizeof(col));
  int cnt[3] = {0,0,0};
  if (del >= 0) { cnt[0] = etaCnt[0]; cnt[1] = etaCnt[1]; cnt[2] = etaCnt[2]; }
  int pos = 0; int8_t tryc[MAXV]; memset(tryc, 0, sizeof(tryc));
  while (pos >= 0) {
    if (pos == m) return true;
    int x = order[pos]; bool adv = false;
    bool isNbr = del >= 0 && pos < nDel;
    for (int c = tryc[pos]; c < 3; c++) {
      if (forb[x] >> c & 1) continue;
      if (isNbr && cnt[c] >= 2) continue;
      bool ok = true; uint32_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb-1;
        if (u == del) continue;
        if (col[u] == c) { ok = false; break; } }
      if (ok) { col[x] = c; if (isNbr) cnt[c]++;
        tryc[pos] = c+1; pos++; if (pos < m) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { tryc[pos] = 0; pos--;
      if (pos >= 0) { int y = order[pos];
        if (del >= 0 && pos < nDel) cnt[col[y]]--;
        col[y] = -1; } }
  }
  return false;
}

// robust-internal-unfrozen verdict; on failure sets failBeta/failQ
static bool robust(const G& g, const Stubs& S, long long* failBeta, int* failQ) {
  int ns = (int)S.anchor.size();
  long long n3 = ipow3(ns);
  vector<int> beta(ns);
  for (long long bc = 0; bc < n3; bc++) {
    long long t = bc;
    for (int s = 0; s < ns; s++) { beta[s] = t % 3; t /= 3; }
    // outside compatible with Q?
    if (!existsColouring(g, S, beta, -1, nullptr)) continue;
    for (int q = 0; q < g.n; q++) {
      // eta counts from beta at q's stubs
      int etaCnt[3] = {0,0,0}; bool etaBad = false;
      for (int s = 0; s < ns; s++) if (S.anchor[s] == q) { if (++etaCnt[beta[s]] > 2) etaBad = true; }
      bool okq = !etaBad && existsColouring(g, S, beta, q, etaCnt);
      if (!okq) { *failBeta = bc; *failQ = q; return false; }
    }
  }
  return true;
}

int main() {
  // group STATE lines
  map<string, vector<pair<int,string>>> groups;
  string line;
  while (getline(cin, line)) {
    if (line.rfind("STATE ", 0) != 0) continue;
    char ms[64], ht[8192], g6[64]; int n, q;
    if (sscanf(line.c_str(), "STATE %d %d %63s %8191s %63s", &n, &q, ms, ht, g6) != 5) continue;
    groups[string(ms) + "|" + ht].push_back({n, g6});
  }
  long long crossGroups = 0, robustHits = 0, tested = 0;
  set<string> testedQ;   // dedupe identical small pieces across groups
  for (auto& kv : groups) {
    set<int> ns; for (auto& p : kv.second) ns.insert(p.first);
    if (ns.size() < 2) continue;
    crossGroups++;
    int nmin = *ns.begin(), nmax = *ns.rbegin();
    // smallest members
    for (auto& p : kv.second) {
      if (p.first != nmin) continue;
      if (testedQ.count(p.second)) continue;
      testedQ.insert(p.second);
      G g; if (!g6decode(p.second, g)) continue;
      Stubs S = stubsOf(g);
      tested++;
      long long fb; int fq;
      if (robust(g, S, &fb, &fq)) {
        robustHits++;
        printf("ROBUST n=%d g6=%s groupSizes=%d..%d members=%d\n",
               nmin, p.second.c_str(), nmin, nmax, (int)kv.second.size());
        fflush(stdout);
      } else {
        printf("NOTROBUST n=%d g6=%s failBeta=%lld failQ=%d\n", nmin, p.second.c_str(), fb, fq);
      }
      break;   // one smallest member per group is enough for existence
    }
  }
  printf("crossGroups=%lld testedSmallest=%lld ROBUST=%lld\n", crossGroups, tested, robustHits);
  return 0;
}
