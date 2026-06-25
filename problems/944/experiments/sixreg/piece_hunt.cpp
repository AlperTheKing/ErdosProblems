// FK-simulator hunt over kappa=8 boundary pieces (GPT round-2 Q3 programme,
// gpt_fk_round2_digest_2026-06-12.md). A piece here = connected graph on m
// vertices, Delta<=6, e = 3m-4 (so kappa = 6m-2e = 8), b=0: every vertex x
// carries 6-d(x) stubs, |S|=8.
//
// scan mode:   piece_hunt.exe scan <g6file> <outfile> [nthreads]
//   For each graph: skip non-3-colourable (Col empty). Compute
//   Col(P) subset 3^8 (stub colours = anchor colours), canonicalize under all
//   8! stub permutations (colour-permutation closure is automatic: the S3
//   action on proper colourings closes Col), FrozenFlag (exists full v with
//   Unf(P,v) empty; emptiness needs no eta loop: v full => eta deficits always
//   fill, so Unf nonempty <=> exists colouring of P-v with internal N(v)
//   counts all <=2). Emit: g6 m |T| frozen hash128(canonical table).
// match mode:  piece_hunt.exe match <rec1> <rec2> ...
//   Cross-size collisions of canonical-table hashes = FK-simulator candidates.
// robust mode: piece_hunt.exe robust <g6>
//   Robustly-internally-unfrozen test: for every outside colouring gamma
//   compatible with Col, every full v has an Unf element matching gamma
//   (inequality on live stubs, equality on deleted-v stubs).
// exact mode:  piece_hunt.exe exact <g6a> <g6b>
//   Recompute both canonical tables exactly and compare (confirm a hash hit).
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <array>
#include <map>
#include <algorithm>
#include <thread>
#include <atomic>
#include <mutex>
using namespace std;

static const int MAXV = 24;
static const int NSTUB = 8;
static const int N3S = 6561;          // 3^8

struct Piece {
  int nv;
  uint32_t adj[MAXV];
  vector<int> stubAnchor;             // stub s -> anchor vertex, |S|=8
  int deg(int x) const { return __builtin_popcount(adj[x]); }
};

static bool g6decodeAny(const string& line, int& n, uint32_t adj[MAXV]) {
  if (line.empty()) return false;
  n = line[0] - 63;
  if (n < 1 || n > MAXV) return false;
  memset(adj, 0, sizeof(uint32_t) * MAXV);
  int nbits = n * (n - 1) / 2, need = (nbits + 5) / 6;
  if ((int)line.size() < 1 + need) return false;
  int bit = 0;
  for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
    int byte = 1 + bit / 6, off = 5 - bit % 6;
    if ((line[byte] - 63) >> off & 1) { adj[i] |= 1u << j; adj[j] |= 1u << i; }
    bit++;
  }
  return true;
}

static bool buildPiece(const string& g6, Piece& P) {
  if (!g6decodeAny(g6, P.nv, P.adj)) return false;
  P.stubAnchor.clear();
  for (int x = 0; x < P.nv; x++) {
    int k = 6 - P.deg(x);
    if (k < 0) return false;
    for (int i = 0; i < k; i++) P.stubAnchor.push_back(x);
  }
  return (int)P.stubAnchor.size() <= 16;   // scan/robust/exact modes require ==NSTUB
}

// enumerate proper 3-colourings of P minus 'del' (-1 = none); cb returns true to stop.
template <class CB>
static bool forEachColouring(const Piece& P, int del, CB cb) {
  int order[MAXV], m = 0;
  for (int x = 0; x < P.nv; x++) if (x != del) order[m++] = x;
  for (int i = 1; i < m; i++) { int k = order[i], j = i - 1;
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
      while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
        if (u == del) continue;
        if (col[u] == c) { ok = false; break; } }
      if (ok) { col[x] = c; tryc[pos] = c + 1; pos++; if (pos < m) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { col[x] = -1; tryc[pos] = 0; pos--;
      if (pos >= 0) col[order[pos]] = -1; }
  }
  return false;
}

// Col(P) as sorted unique codes over 3^8 (stub s = digit s, value = anchor colour).
static vector<uint16_t> colCodes(const Piece& P) {
  vector<uint8_t> seen(N3S, 0);
  static const int POW3[9] = {1,3,9,27,81,243,729,2187,6561};
  forEachColouring(P, -1, [&](const int8_t* col) {
    int code = 0;
    for (int s = 0; s < NSTUB; s++) code += POW3[s] * col[P.stubAnchor[s]];
    seen[code] = 1;
    return false;
  });
  vector<uint16_t> out;
  for (int c = 0; c < N3S; c++) if (seen[c]) out.push_back((uint16_t)c);
  return out;
}

// Unf(P,v) emptiness: v full by construction; nonempty <=> exists proper
// colouring of P-v with every colour used <=2 times on internal N(v).
static bool unfNonempty(const Piece& P, int v) {
  return forEachColouring(P, v, [&](const int8_t* col) {
    int cnt[3] = {0,0,0};
    uint32_t nb = P.adj[v];
    while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
      if (++cnt[col[u]] > 2) return false; }
    return true;
  });
}

static bool frozenFlag(const Piece& P) {
  for (int v = 0; v < P.nv; v++)
    if (!unfNonempty(P, v)) return true;
  return false;
}

// ---------------- canonicalization under stub permutations -----------------
static vector<array<uint8_t, 8>> ALLPERMS;
static void initPerms() {
  array<uint8_t, 8> p = {0,1,2,3,4,5,6,7};
  do ALLPERMS.push_back(p); while (next_permutation(p.begin(), p.end()));
}

static void codeDigits(uint16_t code, uint8_t d[8]) {
  for (int s = 0; s < 8; s++) { d[s] = code % 3; code /= 3; }
}

// canonical sorted table = min over stub perms of remapped sorted code list.
// P_eq pair-equality matrix prunes the 8! perms first.
static vector<uint16_t> canonicalTable(const vector<uint16_t>& T) {
  int nT = (int)T.size();
  vector<array<uint8_t, 8>> digs(nT);
  for (int i = 0; i < nT; i++) codeDigits(T[i], digs[i].data());
  uint16_t peq[8][8]; memset(peq, 0, sizeof(peq));
  for (int i = 0; i < nT; i++)
    for (int s = 0; s < 8; s++) for (int t = s + 1; t < 8; t++)
      if (digs[i][s] == digs[i][t]) { peq[s][t]++; }
  // min P_eq key + survivors
  vector<const array<uint8_t,8>*> survivors;
  uint16_t bestKey[28]; bool first = true;
  for (const auto& sg : ALLPERMS) {
    uint16_t key[28]; int k = 0;
    for (int i = 0; i < 8; i++) for (int j = i + 1; j < 8; j++) {
      int a = sg[i], b = sg[j];
      key[k++] = (a < b) ? peq[a][b] : peq[b][a];
    }
    int cmp = first ? -1 : memcmp(key, bestKey, sizeof(key));
    if (cmp < 0) { memcpy(bestKey, key, sizeof(key)); survivors.clear(); survivors.push_back(&sg); first = false; }
    else if (cmp == 0) survivors.push_back(&sg);
  }
  static const int POW3[9] = {1,3,9,27,81,243,729,2187,6561};
  vector<uint16_t> best, cur(nT);
  for (auto* sgp : survivors) {
    const auto& sg = *sgp;
    for (int i = 0; i < nT; i++) {
      int code = 0;
      for (int j = 0; j < 8; j++) code += POW3[j] * digs[i][sg[j]];
      cur[i] = (uint16_t)code;
    }
    sort(cur.begin(), cur.end());
    if (best.empty() || cur < best) best = cur;
  }
  return best;
}

static void hash128(const vector<uint16_t>& v, uint64_t& h1, uint64_t& h2) {
  h1 = 1469598103934665603ULL; h2 = 14695981039346656037ULL;
  for (uint16_t x : v) {
    h1 = (h1 ^ x) * 1099511628211ULL;
    h2 = (h2 ^ (x * 2654435761ULL)) * 1099511628211ULL;
    h1 = (h1 ^ (h1 >> 29)) * 0x9E3779B97F4A7C15ULL;
  }
  if (v.empty()) { h1 = 0; h2 = 0; }
}

// ---------------- robust internal unfrozenness ------------------------------
// full Unf(P,v) codes: non-v stubs carry anchor colour, v-stubs carry eta.
static vector<uint8_t> unfBitset(const Piece& P, int v) {
  vector<uint8_t> tab((N3S + 7) / 8, 0);
  static const int POW3[9] = {1,3,9,27,81,243,729,2187,6561};
  vector<int> sv;
  for (int s = 0; s < NSTUB; s++) if (P.stubAnchor[s] == v) sv.push_back(s);
  int kEta = (int)sv.size();
  int n3eta = 1; for (int i = 0; i < kEta; i++) n3eta *= 3;
  forEachColouring(P, v, [&](const int8_t* col) {
    int cnt0[3] = {0,0,0};
    uint32_t nb = P.adj[v];
    while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1; cnt0[col[u]]++; }
    for (int ec = 0; ec < n3eta; ec++) {
      int cnt[3] = {cnt0[0], cnt0[1], cnt0[2]};
      int t = ec; bool ok = true;
      for (int i = 0; i < kEta; i++) { int c = t % 3; t /= 3; if (++cnt[c] > 2) { ok = false; break; } }
      if (!ok || cnt[0] != 2 || cnt[1] != 2 || cnt[2] != 2) continue;
      int code = 0, ei = 0; t = ec;
      for (int s = 0; s < NSTUB; s++) {
        int c;
        if (P.stubAnchor[s] == v) { c = t % 3; if (++ei) t /= 3; }
        else c = col[P.stubAnchor[s]];
        code += POW3[s] * c;
      }
      tab[code >> 3] |= 1u << (code & 7);
    }
    return false;
  });
  return tab;
}

static bool robustlyUnfrozen(const Piece& P, int& failGamma, int& failV) {
  vector<uint16_t> T = colCodes(P);
  if (T.empty()) { failGamma = -1; failV = -1; return false; }  // not 3-col
  vector<array<uint8_t,8>> tDigs(T.size());
  for (size_t i = 0; i < T.size(); i++) codeDigits(T[i], tDigs[i].data());
  vector<vector<uint16_t>> unfCodes(P.nv);
  for (int v = 0; v < P.nv; v++) {
    auto bs = unfBitset(P, v);
    for (int c = 0; c < N3S; c++) if (bs[c >> 3] >> (c & 7) & 1) unfCodes[v].push_back((uint16_t)c);
  }
  uint8_t isVStub[MAXV][8];
  for (int v = 0; v < P.nv; v++)
    for (int s = 0; s < 8; s++) isVStub[v][s] = (P.stubAnchor[s] == v);
  for (int gamma = 0; gamma < N3S; gamma++) {
    uint8_t gd[8]; codeDigits((uint16_t)gamma, gd);
    bool compatible = false;
    for (auto& td : tDigs) {
      bool ok = true;
      for (int s = 0; s < 8; s++) if (td[s] == gd[s]) { ok = false; break; }
      if (ok) { compatible = true; break; }
    }
    if (!compatible) continue;
    for (int v = 0; v < P.nv; v++) {
      bool found = false;
      for (uint16_t uc : unfCodes[v]) {
        uint8_t ud[8]; codeDigits(uc, ud);
        bool ok = true;
        for (int s = 0; s < 8; s++) {
          if (isVStub[v][s]) { if (ud[s] != gd[s]) { ok = false; break; } }
          else               { if (ud[s] == gd[s]) { ok = false; break; } }
        }
        if (ok) { found = true; break; }
      }
      if (!found) { failGamma = gamma; failV = v; return false; }
    }
  }
  return true;
}

// ---------------- modes -----------------------------------------------------
static bool isBipartite(const Piece& P) {
  int8_t side[MAXV]; memset(side, -1, sizeof(side));
  for (int s = 0; s < P.nv; s++) {
    if (side[s] >= 0) continue;
    side[s] = 0;
    vector<int> st = {s};
    while (!st.empty()) {
      int x = st.back(); st.pop_back();
      uint32_t nb = P.adj[x];
      while (nb) { int y = __builtin_ctz(nb); nb &= nb - 1;
        if (side[y] < 0) { side[y] = 1 - side[x]; st.push_back(y); }
        else if (side[y] == side[x]) return false; }
    }
  }
  return true;
}

// locked mode: per 3-colourable piece, count locked vertices (Unf(P,v) empty).
// Lockedness is independent of stub/b designations at other vertices, so
// minLocked >= s+1 extends FrozenFlag to every deficiency assignment with
// at most s deficient vertices (Sigma b <= s covers B_k = 6 - Sigma b cases).
static int doLocked(const char* infile, const char* outfile, int nthreads) {
  FILE* f = fopen(infile, "r");
  if (!f) { fprintf(stderr, "no input %s\n", infile); return 1; }
  vector<string> lines;
  { char buf[256];
    while (fgets(buf, sizeof(buf), f)) {
      string s(buf);
      while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back();
      if (!s.empty() && s[0] != '>') lines.push_back(s);
    } }
  fclose(f);
  atomic<long long> idx(0), n3col(0);
  vector<string> results(lines.size());
  atomic<long long> histArr[17];
  for (auto& h : histArr) h = 0;
  auto worker = [&]() {
    for (;;) {
      long long i = idx.fetch_add(1);
      if (i >= (long long)lines.size()) break;
      Piece P;
      if (!buildPiece(lines[i], P)) continue;
      // locked mode is stub-count-free (any kappa): plain 3-colourability gate
      if (!forEachColouring(P, -1, [](const int8_t*) { return true; })) continue;
      n3col++;
      int locked = 0; uint32_t lset = 0;
      for (int v = 0; v < P.nv; v++)
        if (!unfNonempty(P, v)) { locked++; lset |= 1u << v; }
      histArr[locked > 16 ? 16 : locked]++;
      int bip = isBipartite(P) ? 1 : 0;
      char buf[160];
      snprintf(buf, sizeof(buf), "%s %d %d %d %d %u\n",
               lines[i].c_str(), P.nv, (int)P.stubAnchor.size(), locked, bip, lset);
      results[i] = buf;
    }
  };
  vector<thread> th;
  for (int t = 0; t < nthreads; t++) th.emplace_back(worker);
  for (auto& t : th) t.join();
  FILE* g = fopen(outfile, "w");
  for (auto& r : results) if (!r.empty()) fputs(r.c_str(), g);
  fclose(g);
  printf("threecol=%lld lockedHist:", n3col.load());
  for (int i = 0; i <= 16; i++) if (histArr[i].load()) printf(" %d:%lld", i, histArr[i].load());
  printf("\n");
  return 0;
}

static int doScan(const char* infile, const char* outfile, int nthreads) {
  FILE* f = fopen(infile, "r");
  if (!f) { fprintf(stderr, "no input %s\n", infile); return 1; }
  vector<string> lines;
  { char buf[256];
    while (fgets(buf, sizeof(buf), f)) {
      string s(buf);
      while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back();
      if (!s.empty() && s[0] != '>') lines.push_back(s);
    } }
  fclose(f);
  atomic<long long> idx(0), nPieces(0), n3col(0), nFrozen(0), nBad(0);
  vector<string> results(lines.size());
  auto worker = [&]() {
    for (;;) {
      long long i = idx.fetch_add(1);
      if (i >= (long long)lines.size()) break;
      Piece P;
      if (!buildPiece(lines[i], P) || (int)P.stubAnchor.size() != NSTUB) { nBad++; continue; }
      nPieces++;
      vector<uint16_t> T = colCodes(P);
      if (T.empty()) continue;       // not 3-colourable: Col empty, irrelevant
      n3col++;
      bool fr = frozenFlag(P);
      if (fr) nFrozen++;
      vector<uint16_t> canon = canonicalTable(T);
      uint64_t h1, h2; hash128(canon, h1, h2);
      char buf[160];
      snprintf(buf, sizeof(buf), "%s %d %d %d %016llx%016llx\n",
               lines[i].c_str(), P.nv, (int)T.size(), fr ? 1 : 0,
               (unsigned long long)h1, (unsigned long long)h2);
      results[i] = buf;
    }
  };
  vector<thread> th;
  for (int t = 0; t < nthreads; t++) th.emplace_back(worker);
  for (auto& t : th) t.join();
  FILE* g = fopen(outfile, "w");
  if (!g) { fprintf(stderr, "no output %s\n", outfile); return 1; }
  for (auto& r : results) if (!r.empty()) fputs(r.c_str(), g);
  fclose(g);
  printf("scanned=%lld pieces=%lld threecol=%lld frozen=%lld bad=%lld -> %s\n",
         (long long)lines.size(), nPieces.load(), n3col.load(), nFrozen.load(),
         nBad.load(), outfile);
  return 0;
}

static int doMatch(int nfiles, char** files) {
  // hash -> (m -> first g6, count), plus total per hash
  struct Ent { map<int, pair<string, long long>> byM; };
  map<string, Ent> H;
  for (int i = 0; i < nfiles; i++) {
    FILE* f = fopen(files[i], "r");
    if (!f) { fprintf(stderr, "no file %s\n", files[i]); return 1; }
    char buf[256];
    while (fgets(buf, sizeof(buf), f)) {
      char g6[64], hash[40]; int m, tsz, fr;
      if (sscanf(buf, "%63s %d %d %d %39s", g6, &m, &tsz, &fr, hash) != 5) continue;
      auto& e = H[hash].byM[m];
      if (e.second == 0) e.first = g6;
      e.second++;
    }
    fclose(f);
  }
  long long crossPairs = 0, sameDup = 0;
  for (auto& kv : H) {
    if (kv.second.byM.size() >= 2) {
      crossPairs++;
      printf("CROSS-SIZE hash=%s :", kv.first.c_str());
      for (auto& me : kv.second.byM)
        printf(" m=%d cnt=%lld g6=%s", me.first, me.second.second, me.second.first.c_str());
      printf("\n");
    } else {
      for (auto& me : kv.second.byM) if (me.second.second > 1) sameDup++;
    }
  }
  printf("hashes=%zu crossSizeCollisions=%lld sameSizeDuplicatedStates=%lld\n",
         H.size(), crossPairs, sameDup);
  return 0;
}

int main(int argc, char** argv) {
  initPerms();
  if (argc >= 4 && string(argv[1]) == "scan")
    return doScan(argv[2], argv[3], argc >= 5 ? atoi(argv[4]) : 32);
  if (argc >= 3 && string(argv[1]) == "match")
    return doMatch(argc - 2, argv + 2);
  if (argc >= 4 && string(argv[1]) == "locked")
    return doLocked(argv[2], argv[3], argc >= 5 ? atoi(argv[4]) : 32);
  if (argc >= 3 && string(argv[1]) == "robust") {
    Piece P;
    if (!buildPiece(argv[2], P)) { fprintf(stderr, "bad piece g6\n"); return 1; }
    int fg, fv;
    bool r = robustlyUnfrozen(P, fg, fv);
    printf("robust=%d failGamma=%d failV=%d\n", r ? 1 : 0, fg, fv);
    return 0;
  }
  if (argc >= 4 && string(argv[1]) == "exact") {
    Piece A, B;
    if (!buildPiece(argv[2], A) || !buildPiece(argv[3], B)) { fprintf(stderr, "bad g6\n"); return 1; }
    auto ca = canonicalTable(colCodes(A)), cb = canonicalTable(colCodes(B));
    printf("equal=%d |A|=%zu |B|=%zu\n", ca == cb ? 1 : 0, ca.size(), cb.size());
    return 0;
  }
  fprintf(stderr, "usage: piece_hunt scan <g6file> <out> [threads] | match <rec...> | robust <g6> | exact <g6a> <g6b>\n");
  return 1;
}
