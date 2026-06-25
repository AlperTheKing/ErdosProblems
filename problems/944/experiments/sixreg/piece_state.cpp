// Boundary-piece state tables for the (FK) certificate programme (GPT round-2
// formalism, audited 2026-06-12, gpt_fk_round2_digest_2026-06-12.md Sec Q3).
//
// A piece P = (V, E, S, a, b): simple graph (V,E), stubs S anchored by a:S->V,
// intrinsic deficiency b:V->{0..6}, with d(x) + #stubs(x) + b(x) = 6 for all x.
//
// Col(P)   subset [3]^S : anchor-consistent stub colourings extendable to a
//                         proper 3-colouring of P.
// Unf(P,v) subset [3]^S (v full, b(v)=0, here also no stub at v unless stated):
//          for stubs not at v: colour of the anchor; for stubs at v: colour of
//          the OUTSIDE endpoint. Member iff exists proper 3-colouring of P-v
//          matching the non-v stub colours whose N(v)-counts (internal nbrs +
//          outside-endpoint colours at v-stubs) are exactly (2,2,2).
// FrozenFlag(P): some full v with Unf(P,v) empty  =>  v frozen in EVERY
//          completion of P (sound certificate).
//
// SELF-TEST MODE (validation against exhaustive census data):
//   piece_state.exe validate N <g6file>
//   For each 6-regular 3-colourable graph H in the file and each vertex set Y
//   (BFS balls of radius 1 around each vertex, plus random connected sets),
//   cut P = H[Y] with stubs = edges(Y, V\Y), b=0. Then for every full vertex
//   v in Y (all nbrs inside Y or anchoring stubs):
//     FrozenFlag certifies v frozen  ==>  v must NOT be unfrozen in H.
//   Any violation falsifies the implementation (or the soundness argument).
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <set>
#include <random>
#include <iostream>
using namespace std;

static const int MAXV = 32;

struct Piece {
  int nv;                       // vertices 0..nv-1
  uint32_t adj[MAXV];           // internal adjacency
  vector<int> stubAnchor;       // stub s -> anchor vertex
  int b[MAXV];                  // intrinsic deficiency
  int deg(int x) const { return __builtin_popcount(adj[x]); }
  int stubsAt(int x) const { int c=0; for (int a : stubAnchor) if (a==x) c++; return c; }
  bool wellFormed() const {
    for (int x = 0; x < nv; x++)
      if (deg(x) + stubsAt(x) + b[x] != 6) return false;
    return true;
  }
};

// enumerate proper 3-colourings of P (optionally minus vertex 'del'), calling
// cb(colors). Returns early if cb returns true (existence queries).
template <class CB>
static bool forEachColouring(const Piece& P, int del, CB cb) {
  int order[MAXV], m = 0;
  for (int x = 0; x < P.nv; x++) if (x != del) order[m++] = x;
  // degree-descending static order
  for (int i = 1; i < m; i++) { int k = order[i], j = i-1;
    while (j >= 0 && P.deg(order[j]) < P.deg(k)) { order[j+1] = order[j]; j--; } order[j+1] = k; }
  int8_t col[MAXV]; memset(col, -1, sizeof(col));
  int pos = 0; int8_t tryc[MAXV]; memset(tryc, 0, sizeof(tryc));
  while (pos >= 0) {
    if (pos == m) {
      if (cb(col)) return true;
      pos--; if (pos >= 0) { col[order[pos]] = -1; continue; }
      break;
    }
    int x = order[pos]; bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      bool ok = true; uint32_t nb = P.adj[x];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb-1;
        if (u == del) continue;
        if (col[u] == c) { ok = false; break; } }
      if (ok) { col[x] = c; tryc[pos] = c+1; pos++; if (pos < m) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { col[x] = -1; tryc[pos] = 0; pos--;
      if (pos >= 0) { col[order[pos]] = -1; } }
  }
  return false;
}

static long long ipow3(int k) { long long r = 1; while (k--) r *= 3; return r; }

// Col(P) as a bitset over 3^|S| stub-colour codes (stub s least significant).
static vector<uint8_t> colTable(const Piece& P) {
  int S = (int)P.stubAnchor.size();
  long long n3 = ipow3(S);
  vector<uint8_t> tab((n3 + 7) / 8, 0);
  forEachColouring(P, -1, [&](const int8_t* col) {
    // all anchor-consistent codes for this colouring: each stub takes its
    // anchor's colour (anchor-consistency forces exactly one code)
    long long code = 0, mul = 1;
    for (int s = 0; s < S; s++) { code += mul * col[P.stubAnchor[s]]; mul *= 3; }
    tab[code >> 3] |= 1u << (code & 7);
    return false;                 // enumerate all
  });
  return tab;
}

// Unf(P,v): bitset over 3^|S| codes; stubs at v carry OUTSIDE colours (eta),
// other stubs carry anchor colours. v must be full (b(v)==0).
static vector<uint8_t> unfTable(const Piece& P, int v) {
  int S = (int)P.stubAnchor.size();
  long long n3 = ipow3(S);
  vector<uint8_t> tab((n3 + 7) / 8, 0);
  // stubs at v
  vector<int> sv, snv;
  for (int s = 0; s < S; s++) (P.stubAnchor[s] == v ? sv : snv).push_back(s);
  int kEta = (int)sv.size();
  long long n3eta = ipow3(kEta);
  forEachColouring(P, v, [&](const int8_t* col) {
    // internal neighbour colour counts
    int cnt0[3] = {0,0,0};
    uint32_t nb = P.adj[v];
    while (nb) { int u = __builtin_ctz(nb); nb &= nb-1; cnt0[col[u]]++; }
    // try every eta assignment on v-stubs; need final counts (2,2,2)
    for (long long ec = 0; ec < n3eta; ec++) {
      int cnt[3] = {cnt0[0], cnt0[1], cnt0[2]};
      long long t = ec; bool ok = true;
      for (int i = 0; i < kEta; i++) { int c = t % 3; t /= 3; if (++cnt[c] > 2) { ok = false; break; } }
      if (!ok) continue;
      if (cnt[0] == 2 && cnt[1] == 2 && cnt[2] == 2) {
        long long code = 0;
        // build full code: non-v stubs from colouring, v-stubs from ec
        long long t2 = ec;
        long long mul = 1;
        int ei = 0;
        for (int s = 0; s < S; s++) {
          int c;
          if (P.stubAnchor[s] == v) { c = (int)((ec / ipow3(ei)) % 3); ei++; }
          else c = col[P.stubAnchor[s]];
          code += mul * c; mul *= 3;
        }
        (void)t2;
        tab[code >> 3] |= 1u << (code & 7);
      }
    }
    return false;
  });
  return tab;
}

static bool tableEmpty(const vector<uint8_t>& t) {
  for (uint8_t x : t) if (x) return false;
  return true;
}

// ---------- graph6 + whole-graph unfrozen (reference, from unfrozen_census) ----
static int N;
struct G { uint32_t adj[MAXV]; int deg(int u) const { return __builtin_popcount(adj[u]); } };
static bool g6decode(const string& line, G& g) {
  if (line.empty()) return false;
  int n = line[0] - 63; if (n != N) return false;
  memset(g.adj, 0, sizeof(g.adj));
  int nbits = n*(n-1)/2, need = (nbits+5)/6;
  if ((int)line.size() < 1 + need) return false;
  int bit = 0;
  for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
    int byte = 1 + bit/6, off = 5 - bit%6;
    if ((line[byte]-63) >> off & 1) { g.adj[i] |= 1u<<j; g.adj[j] |= 1u<<i; }
    bit++;
  }
  return true;
}
static bool unfrozenWhole(const G& g, int v) {
  Piece P; P.nv = N; for (int x = 0; x < N; x++) { P.adj[x] = g.adj[x]; P.b[x] = 0; }
  // whole graph: no stubs
  int S = 0; (void)S;
  bool found = false;
  forEachColouring(P, v, [&](const int8_t* col) {
    int cnt[3] = {0,0,0};
    uint32_t nb = g.adj[v];
    while (nb) { int u = __builtin_ctz(nb); nb &= nb-1; if (++cnt[col[u]] > 2) return false; }
    if (cnt[0]==2 && cnt[1]==2 && cnt[2]==2) { found = true; return true; }
    return false;
  });
  return found;
}

int main(int argc, char** argv) {
  if (argc >= 2 && string(argv[1]) == "validate") {
    N = atoi(argv[2]);
    FILE* f = fopen(argv[3], "r");
    if (!f) { fprintf(stderr, "no file\n"); return 1; }
    char buf[256];
    long long graphs = 0, pieces = 0, certFrozen = 0, violations = 0, agree = 0;
    mt19937 rng(944);
    while (fgets(buf, sizeof(buf), f)) {
      string line(buf);
      while (!line.empty() && (line.back()=='\n'||line.back()=='\r')) line.pop_back();
      // accept "HIGH_UNFROZEN_G6: <g6> ..." or raw g6
      size_t sp = line.find(' ');
      if (line.rfind("HIGH_UNFROZEN_G6:", 0) == 0) { line = line.substr(18); sp = line.find(' '); }
      if (sp != string::npos) line = line.substr(0, sp);
      G g; if (!g6decode(line, g)) continue;
      graphs++;
      // pieces: ALL subsets of size 2..8 whose stub count (= 6|Y| - 2 e(Y) for
      // 6-regular) is at most 12 — every testable piece, no sampling
      vector<uint32_t> sets;
      for (uint32_t Y = 1; Y < (1u << N); Y++) {
        int sz = __builtin_popcount(Y);
        if (sz < 2 || sz > 8) continue;
        int eY = 0;
        uint32_t t = Y;
        while (t) { int x = __builtin_ctz(t); t &= t-1; eY += __builtin_popcount(g.adj[x] & Y); }
        eY /= 2;
        if (6*sz - 2*eY <= 12) sets.push_back(Y);
      }
      for (uint32_t Y : sets) {
        int sz = __builtin_popcount(Y);
        if (sz < 2 || sz > N-2) continue;
        // build piece
        Piece P; P.nv = 0;
        int map_[MAXV]; memset(map_, -1, sizeof(map_));
        for (int x = 0; x < N; x++) if ((Y>>x)&1) map_[x] = P.nv++;
        memset(P.adj, 0, sizeof(P.adj));
        P.stubAnchor.clear();
        for (int x = 0; x < N; x++) if ((Y>>x)&1) {
          P.b[map_[x]] = 0;
          uint32_t nb = g.adj[x];
          while (nb) { int u = __builtin_ctz(nb); nb &= nb-1;
            if ((Y>>u)&1) { if (u > x) { P.adj[map_[x]] |= 1u<<map_[u]; P.adj[map_[u]] |= 1u<<map_[x]; } }
            else P.stubAnchor.push_back(map_[x]); }
        }
        if ((int)P.stubAnchor.size() > 12) continue;   // 3^12 tables = 66KB; fine
        if (!P.wellFormed()) { fprintf(stderr, "BAD PIECE\n"); return 2; }
        pieces++;
        for (int x = 0; x < N; x++) {
          if (!((Y>>x)&1)) continue;
          int v = map_[x];
          auto t = unfTable(P, v);
          if (tableEmpty(t)) {
            certFrozen++;
            if (unfrozenWhole(g, x)) {
              violations++;
              printf("VIOLATION g6=%s Y=%u v=%d\n", line.c_str(), Y, x);
            }
          } else agree++;
        }
      }
    }
    fclose(f);
    printf("graphs=%lld pieces=%lld certFrozen=%lld nonCert=%lld VIOLATIONS=%lld\n",
           graphs, pieces, certFrozen, agree, violations);
    return 0;
  }
  fprintf(stderr, "usage: piece_state validate N <g6file>\n");
  return 1;
}
