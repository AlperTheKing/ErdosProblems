// FK-simulator hunt v1 (certificate programme step 3).
// Enumerate connected pieces with b == 0, augmented boundary q = sum(6-d(x))
// = 6n - 2e <= QMAX (so e >= (6n-QMAX)/2: DENSE graphs — small space).
// State v1 = Col table over ANCHOR colourings (anchor-consistency makes stub
// colours = anchor colours, so Col depends only on the anchor vector), plus
// the anchor stub-multiplicity signature. Canonical form: minimize table bytes
// over colour permutations (6) x permutations of anchors with equal stub
// multiplicity. Two pieces with SAME canonical state and DIFFERENT vertex
// counts = candidate FK-simulator pair (colour-simulation part).
// usage: geng -c -D6 <n> <emin>:<emax> | piece_enum <n> <QMAX> >> pieces.txt
//        piece_enum report < pieces.txt     (group + find cross-n collisions)
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <array>
#include <tuple>
#include <iostream>
using namespace std;
static const int MAXV = 16;
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

static long long ipow3(int k) { long long r=1; while (k--) r*=3; return r; }

// Col over anchor colourings: anchors = vertices with deficit > 0, in given order.
// tab bit c set iff anchor colouring code c extends to proper 3-colouring of G.
static vector<uint8_t> colAnchors(const G& g, const vector<int>& anchors) {
  int A = (int)anchors.size();
  long long n3 = ipow3(A);
  vector<uint8_t> tab((n3+7)/8, 0);
  int aidx[MAXV]; memset(aidx, -1, sizeof(aidx));
  for (int i = 0; i < A; i++) aidx[anchors[i]] = i;
  // enumerate all proper 3-colourings, record anchor codes
  int order[MAXV];
  for (int i = 0; i < N; i++) order[i] = i;
  // anchors first improves nothing for full enumeration; plain order fine
  int8_t col[MAXV]; memset(col, -1, sizeof(col));
  int pos = 0; int8_t tryc[MAXV]; memset(tryc, 0, sizeof(tryc));
  while (pos >= 0) {
    if (pos == N) {
      long long code = 0;
      for (int i = A-1; i >= 0; i--) code = code*3 + col[anchors[i]];
      tab[code>>3] |= 1u << (code&7);
      pos--; col[order[pos]] = -1; continue;
    }
    int x = order[pos]; bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      bool ok = true; uint32_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb-1; if (col[u] == c) { ok = false; break; } }
      if (ok) { col[x] = c; tryc[pos] = c+1; pos++; if (pos < N) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { col[x] = -1; tryc[pos] = 0; pos--; if (pos >= 0) { col[order[pos]] = -1; } }
  }
  return tab;
}

static bool tabEmpty(const vector<uint8_t>& t) { for (uint8_t x : t) if (x) return false; return true; }

// permute colours / anchors of a table
static vector<uint8_t> remapTable(const vector<uint8_t>& tab, int A,
                                  const int* cperm, const vector<int>& aperm) {
  long long n3 = ipow3(A);
  vector<uint8_t> out((n3+7)/8, 0);
  vector<long long> p3(A); for (int i = 0; i < A; i++) p3[i] = ipow3(i);
  for (long long c = 0; c < n3; c++) {
    if (!(tab[c>>3] >> (c&7) & 1)) continue;
    // digit i (anchor i) colour
    long long nc = 0; long long t = c;
    for (int i = 0; i < A; i++) { int d = t % 3; t /= 3; nc += p3[aperm[i]] * cperm[d]; }
    out[nc>>3] |= 1u << (nc&7);
  }
  return out;
}

int main(int argc, char** argv) {
  if (argc >= 2 && string(argv[1]) == "report") {
    // lines: STATE <n> <q> <multsig> <hextable> <g6>
    map<string, vector<pair<int,string>>> groups;   // key=multsig|hextable -> [(n,g6)]
    string w, line;
    while (getline(cin, line)) {
      if (line.rfind("STATE ", 0) != 0) continue;
      char ms[64], ht[4096], g6[64]; int n, q;
      if (sscanf(line.c_str(), "STATE %d %d %63s %4095s %63s", &n, &q, ms, ht, g6) != 5) continue;
      groups[string(ms) + "|" + ht].push_back({n, g6});
    }
    long long total = 0, crossPairs = 0;
    for (auto& kv : groups) {
      total++;
      set<int> ns; for (auto& p : kv.second) ns.insert(p.first);
      if (ns.size() >= 2) {
        crossPairs++;
        printf("SIMULATOR_CANDIDATE sizes={");
        for (int n : ns) printf("%d,", n);
        printf("} members=%d examples:", (int)kv.second.size());
        int shown = 0;
        for (auto& p : kv.second) { if (shown++ >= 4) break; printf(" n%d:%s", p.first, p.second.c_str()); }
        printf("\n");
      }
    }
    printf("stateGroups=%lld crossSizeGroups=%lld\n", total, crossPairs);
    return 0;
  }
  N = atoi(argv[1]);
  int QMAX = argc > 2 ? atoi(argv[2]) : 8;
  string line;
  long long total = 0, kept = 0;
  while (getline(cin, line)) {
    while (!line.empty() && (line.back()=='\r'||line.back()=='\n')) line.pop_back();
    if (line.empty() || line[0] == '>') continue;
    G g; if (!g6decode(line, g)) continue;
    total++;
    int q = 0; vector<int> anchors; vector<int> mult;
    bool ok = true;
    for (int x = 0; x < N; x++) {
      int d = g.deg(x);
      if (d > 6) { ok = false; break; }
      int s = 6 - d;
      q += s;
      if (s > 0) { anchors.push_back(x); mult.push_back(s); }
    }
    if (!ok || q > QMAX || q < 1) continue;
    auto tab = colAnchors(g, anchors);
    if (tabEmpty(tab)) continue;            // not 3-colourable: cannot sit in shore
    int A = (int)anchors.size();
    // canonical: min over 6 colour perms x anchor perms preserving multiplicity
    static const int CP[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
    // per-anchor colour-perm-invariant: sorted counts of valid codes per colour
    long long n3A = ipow3(A);
    vector<array<long long,3>> cnt(A, {0,0,0});
    for (long long c = 0; c < n3A; c++) {
      if (!(tab[c>>3] >> (c&7) & 1)) continue;
      long long t = c;
      for (int i = 0; i < A; i++) { cnt[i][t%3]++; t /= 3; }
    }
    vector<array<long long,3>> inv(A);
    for (int i = 0; i < A; i++) { inv[i] = cnt[i]; sort(inv[i].begin(), inv[i].end()); }
    // order anchors by (mult, invariant); permute only within tie blocks
    vector<int> idx(A); for (int i = 0; i < A; i++) idx[i] = i;
    auto key = [&](int a) { return make_tuple(mult[a], inv[a][0], inv[a][1], inv[a][2]); };
    sort(idx.begin(), idx.end(), [&](int a, int b){ return key(a) < key(b); });
    vector<uint8_t> best;
    vector<int> aperm(A);
    vector<int> cur(idx);
    do {
      bool okp = true;
      for (int i = 0; i+1 < A; i++)
        if (key(cur[i]) > key(cur[i+1])) { okp = false; break; }
      if (!okp) continue;
      for (int i = 0; i < A; i++) aperm[cur[i]] = i;
      for (int cp = 0; cp < 6; cp++) {
        auto t2 = remapTable(tab, A, CP[cp], aperm);
        if (best.empty() || t2 < best) best = t2;
      }
    } while (next_permutation(cur.begin(), cur.end()));
    // multiplicity signature (sorted)
    vector<int> ms(mult); sort(ms.begin(), ms.end());
    string msig;
    for (int m : ms) msig += ('0'+m);
    string hex;
    for (uint8_t b : best) { char buf[3]; snprintf(buf, 3, "%02x", b); hex += buf; }
    printf("STATE %d %d %s %s %s\n", N, q, msig.c_str(), hex.c_str(), line.c_str());
    kept++;
  }
  fprintf(stderr, "n=%d total=%lld kept=%lld\n", N, total, kept);
  return 0;
}
