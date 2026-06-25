// FK-simulation stage 2: Unf-table SUBSET transfer test (corrected sufficient
// condition, PROOF_STATE 2026-06-12 ~22:00; sound by the audited composition
// lemma — no internal-robustness needed).
//
// Replacement P -> Q (|V(Q)| < |V(P)|) preserves "all full vertices unfrozen"
// in any host if, under a stub bijection sigma and colour permutation pi with
//   Col_Q = (sigma,pi) . Col_P            (colour-state alignment)
// it holds that
//   for every q in V(Q) there is p in V(P) with
//     (sigma,pi) . Unf_P(p)  SUBSET-OF  Unf_Q(q).
// (The host-side boundary data realizing p's witness in H is an element of
//  Unf_P(p); under alignment it lies in Unf_Q(q), so it realizes q's witness
//  in H'. Host vertices keep witnesses via Col equality.)
// Pieces P with some empty Unf_P(p) are FrozenFlag pieces: they cannot occur
// in an all-unfrozen host at all (counted separately as HOST-IMPOSSIBLE).
//
// usage: fk_sim2 [maxPerGroup] < pieces_file
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <array>
#include <tuple>
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
static long long ipow3(int k) { long long r=1; while (k--) r*=3; return r; }

struct PieceInfo {
  G g;
  vector<int> anchors, mult;          // anchor vertices, stub multiplicities
  vector<int> stubAnchorIdx;          // stub -> anchor position (anchors order)
  int A, S;
  vector<int> canonAperm;             // anchor pos -> canonical slot
  int canonCperm[3];                  // colour -> canonical colour
};

// anchor-indexed Col table (3^A)
static vector<uint8_t> colAnchors(const G& g, const vector<int>& anchors) {
  int A = (int)anchors.size();
  long long n3 = ipow3(A);
  vector<uint8_t> tab((n3+7)/8, 0);
  int8_t col[MAXV]; memset(col, -1, sizeof(col));
  int pos = 0; int8_t tryc[MAXV]; memset(tryc, 0, sizeof(tryc));
  while (pos >= 0) {
    if (pos == g.n) {
      long long code = 0;
      for (int i = A-1; i >= 0; i--) code = code*3 + col[anchors[i]];
      tab[code>>3] |= 1u << (code&7);
      pos--; col[pos] = -1; continue;
    }
    int x = pos; bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      bool ok = true; uint32_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb-1; if (col[u] == c) { ok = false; break; } }
      if (ok) { col[x] = c; tryc[pos] = c+1; pos++; if (pos < g.n) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { col[x] = -1; tryc[pos] = 0; pos--; if (pos >= 0) { col[pos] = -1; } }
  }
  return tab;
}
static vector<uint8_t> remapAnchorTable(const vector<uint8_t>& tab, int A,
                                        const int* cperm, const vector<int>& aperm) {
  long long n3 = ipow3(A);
  vector<uint8_t> out((n3+7)/8, 0);
  vector<long long> p3(A+1); p3[0]=1; for (int i = 1; i <= A; i++) p3[i] = p3[i-1]*3;
  for (long long c = 0; c < n3; c++) {
    if (!(tab[c>>3] >> (c&7) & 1)) continue;
    long long nc = 0, t = c;
    for (int i = 0; i < A; i++) { int d = t % 3; t /= 3; nc += p3[aperm[i]] * cperm[d]; }
    out[nc>>3] |= 1u << (nc&7);
  }
  return out;
}

// canonicalize: find (aperm, cperm) minimizing remapped table (same algorithm
// as piece_enum: invariant-sorted anchors, permute within tie blocks)
static void canonicalize(PieceInfo& P, const vector<uint8_t>& tab) {
  int A = P.A;
  long long n3A = ipow3(A);
  vector<array<long long,3>> cnt(A, {0,0,0});
  for (long long c = 0; c < n3A; c++) {
    if (!(tab[c>>3] >> (c&7) & 1)) continue;
    long long t = c;
    for (int i = 0; i < A; i++) { cnt[i][t%3]++; t /= 3; }
  }
  vector<array<long long,3>> inv(A);
  for (int i = 0; i < A; i++) { inv[i] = cnt[i]; sort(inv[i].begin(), inv[i].end()); }
  vector<int> idx(A); for (int i = 0; i < A; i++) idx[i] = i;
  auto key = [&](int a) { return make_tuple(P.mult[a], inv[a][0], inv[a][1], inv[a][2]); };
  sort(idx.begin(), idx.end(), [&](int a, int b){ return key(a) < key(b); });
  static const int CP[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
  vector<uint8_t> best;
  vector<int> aperm(A), bestAperm; int bestCp = 0;
  vector<int> cur(idx);
  do {
    bool okp = true;
    for (int i = 0; i+1 < A; i++) if (key(cur[i]) > key(cur[i+1])) { okp = false; break; }
    if (!okp) continue;
    for (int i = 0; i < A; i++) aperm[cur[i]] = i;
    for (int cp = 0; cp < 6; cp++) {
      auto t2 = remapAnchorTable(tab, A, CP[cp], aperm);
      if (best.empty() || t2 < best) { best = t2; bestAperm = aperm; bestCp = cp; }
    }
  } while (next_permutation(cur.begin(), cur.end()));
  P.canonAperm = bestAperm;
  for (int c = 0; c < 3; c++) P.canonCperm[c] = CP[bestCp][c];
}

static bool buildPiece(const string& g6, PieceInfo& P) {
  if (!g6decode(g6, P.g)) return false;
  P.anchors.clear(); P.mult.clear(); P.stubAnchorIdx.clear();
  for (int x = 0; x < P.g.n; x++) {
    int s = 6 - P.g.deg(x);
    if (s < 0) return false;
    if (s > 0) { P.anchors.push_back(x); P.mult.push_back(s); }
  }
  P.A = (int)P.anchors.size();
  for (int i = 0; i < P.A; i++) for (int k = 0; k < P.mult[i]; k++) P.stubAnchorIdx.push_back(i);
  P.S = (int)P.stubAnchorIdx.size();
  auto tab = colAnchors(P.g, P.anchors);
  canonicalize(P, tab);
  return true;
}

// stub-indexed Unf table for vertex v: bitset over 3^S codes; digit of stub s:
// if anchor(s) != v: colour of that anchor; if anchor(s) == v: outside colour eta.
static vector<uint8_t> unfStub(const PieceInfo& P, int v) {
  int S = P.S;
  long long n3 = ipow3(S);
  vector<uint8_t> tab((n3+7)/8, 0);
  vector<int> sv, snv;
  for (int s = 0; s < S; s++) (P.anchors[P.stubAnchorIdx[s]] == v ? sv : snv).push_back(s);
  int kEta = (int)sv.size();
  long long n3eta = ipow3(kEta);
  vector<long long> p3(S+1); p3[0]=1; for (int i = 1; i <= S; i++) p3[i]=p3[i-1]*3;
  const G& g = P.g;
  // enumerate colourings of P - v
  int order[MAXV], m = 0;
  for (int x = 0; x < g.n; x++) if (x != v) order[m++] = x;
  int8_t col[MAXV]; memset(col, -1, sizeof(col));
  int pos = 0; int8_t tryc[MAXV]; memset(tryc, 0, sizeof(tryc));
  while (pos >= 0) {
    if (pos == m) {
      int cnt0[3] = {0,0,0};
      uint32_t nb = g.adj[v];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb-1; cnt0[col[u]]++; }
      for (long long ec = 0; ec < n3eta; ec++) {
        int cnt[3] = {cnt0[0],cnt0[1],cnt0[2]};
        long long t = ec; bool ok = true;
        for (int i = 0; i < kEta; i++) { int c = t%3; t/=3; if (++cnt[c] > 2) { ok=false; break; } }
        if (!ok || cnt[0]!=2 || cnt[1]!=2 || cnt[2]!=2) continue;
        long long code = 0; t = ec;
        for (int i = 0; i < kEta; i++) { code += p3[sv[i]] * (t%3); t/=3; }
        for (int s : snv) code += p3[s] * col[P.anchors[P.stubAnchorIdx[s]]];
        tab[code>>3] |= 1u << (code&7);
      }
      pos--; col[order[pos]] = -1; continue;
    }
    int x = order[pos]; bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      bool ok = true; uint32_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb-1;
        if (u == v) continue;
        if (col[u] == c) { ok = false; break; } }
      if (ok) { col[x] = c; tryc[pos] = c+1; pos++; if (pos < m) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { col[x] = -1; tryc[pos] = 0; pos--; if (pos >= 0) { col[order[pos]] = -1; } }
  }
  return tab;
}

// remap stub table by stub map sm (stub s of P -> stub sm[s] of Q) and colour perm
static vector<uint8_t> remapStubTable(const vector<uint8_t>& tab, int S,
                                      const vector<int>& sm, const int* cperm) {
  long long n3 = ipow3(S);
  vector<uint8_t> out((n3+7)/8, 0);
  vector<long long> p3(S+1); p3[0]=1; for (int i = 1; i <= S; i++) p3[i]=p3[i-1]*3;
  for (long long c = 0; c < n3; c++) {
    if (!(tab[c>>3] >> (c&7) & 1)) continue;
    long long nc = 0, t = c;
    for (int s = 0; s < S; s++) { int d = t%3; t/=3; nc += p3[sm[s]] * cperm[d]; }
    out[nc>>3] |= 1u << (nc&7);
  }
  return out;
}
static bool subsetOf(const vector<uint8_t>& a, const vector<uint8_t>& b) {
  for (size_t i = 0; i < a.size(); i++) if (a[i] & ~b[i]) return false;
  return true;
}
static bool emptyTab(const vector<uint8_t>& a) { for (uint8_t x : a) if (x) return false; return true; }

int main(int argc, char** argv) {
  int maxPerGroup = argc > 1 ? atoi(argv[1]) : 3;
  map<string, vector<pair<int,string>>> groups;
  string line;
  while (getline(cin, line)) {
    if (line.rfind("STATE ", 0) != 0) continue;
    char ms[64], ht[8192], g6[64]; int n, q;
    if (sscanf(line.c_str(), "STATE %d %d %63s %8191s %63s", &n, &q, ms, ht, g6) != 5) continue;
    groups[string(ms) + "|" + ht].push_back({n, g6});
  }
  long long crossGroups = 0, reductions = 0, hostImpossible = 0, pairsTested = 0;
  for (auto& kv : groups) {
    set<int> ns; for (auto& p : kv.second) ns.insert(p.first);
    if (ns.size() < 2) continue;
    crossGroups++;
    int nmin = *ns.begin();
    // build smallest Q
    PieceInfo Q;
    string qg6;
    for (auto& pr : kv.second) if (pr.first == nmin) { qg6 = pr.second; break; }
    if (!buildPiece(qg6, Q)) continue;
    vector<vector<uint8_t>> unfQ(Q.g.n);
    for (int v = 0; v < Q.g.n; v++) unfQ[v] = unfStub(Q, v);
    int testedP = 0;
    for (auto& pr : kv.second) {
      if (pr.first <= nmin || testedP >= maxPerGroup) continue;
      testedP++;
      PieceInfo P;
      if (!buildPiece(pr.second, P)) continue;
      if (P.A != Q.A || P.S != Q.S) continue;
      pairsTested++;
      // alignment: anchor pos i of P -> anchor pos j of Q with canonAperm equal
      vector<int> a2a(P.A, -1);
      vector<int> qslot(Q.A);
      for (int j = 0; j < Q.A; j++) qslot[Q.canonAperm[j]] = j;
      bool okA = true;
      for (int i = 0; i < P.A; i++) {
        int j = qslot[P.canonAperm[i]];
        if (P.mult[i] != Q.mult[j]) { okA = false; break; }
        a2a[i] = j;
      }
      if (!okA) continue;
      // colour perm pi = cpermQ^{-1} o cpermP
      int invQ[3]; for (int c = 0; c < 3; c++) invQ[Q.canonCperm[c]] = c;
      int pi[3]; for (int c = 0; c < 3; c++) pi[c] = invQ[P.canonCperm[c]];
      // stub map: stubs of P at anchor i -> stubs of Q at anchor a2a[i], in order
      vector<vector<int>> qStubsAt(Q.A);
      for (int s = 0; s < Q.S; s++) qStubsAt[Q.stubAnchorIdx[s]].push_back(s);
      vector<int> used(Q.A, 0), sm(P.S);
      for (int s = 0; s < P.S; s++) {
        int j = a2a[P.stubAnchorIdx[s]];
        sm[s] = qStubsAt[j][used[j]++];
      }
      // host-impossible check + cover test
      bool hostImp = false, cover = true;
      vector<vector<uint8_t>> unfPm(P.g.n);
      for (int p = 0; p < P.g.n; p++) {
        auto t = unfStub(P, p);
        if (emptyTab(t)) { hostImp = true; break; }
        unfPm[p] = remapStubTable(t, P.S, sm, pi);
      }
      if (hostImp) { hostImpossible++; continue; }
      for (int q = 0; q < Q.g.n && cover; q++) {
        bool found = false;
        for (int p = 0; p < P.g.n && !found; p++)
          if (subsetOf(unfPm[p], unfQ[q])) found = true;
        if (!found) cover = false;
      }
      if (cover) {
        reductions++;
        printf("REDUCTION P(n=%d)=%s -> Q(n=%d)=%s\n", pr.first, pr.second.c_str(), nmin, qg6.c_str());
        fflush(stdout);
      }
    }
  }
  printf("crossGroups=%lld pairsTested=%lld hostImpossiblePs=%lld REDUCTIONS=%lld\n",
         crossGroups, pairsTested, hostImpossible, reductions);
  return 0;
}
