// FrozenFlag scan over the full q<=8 piece inventory: which pieces contain a
// vertex with EMPTY Unf table (certified frozen in EVERY completion)?
// Output: per (n,q) counts; prints every NOT-certified piece (survivor).
// usage: ff_scan < pieces_chunk > out
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <map>
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
// does vertex v have ANY deletion witness (some colouring of G-v, some eta at
// v's stubs, counts (2,2,2))? early-exit existence version.
static bool hasWitness(const G& g, int v) {
  int sv = 6 - g.deg(v);              // stubs at v (eta slots)
  int order[MAXV], m = 0;
  for (int x = 0; x < g.n; x++) if (x != v) order[m++] = x;
  int front = 0;
  for (int i = 0; i < m; i++) if ((g.adj[v] >> order[i]) & 1) { int t=order[front]; order[front]=order[i]; order[i]=t; front++; }
  int nDel = front;
  int8_t col[MAXV]; memset(col, -1, sizeof(col));
  int cnt[3] = {0,0,0};
  int pos = 0; int8_t tryc[MAXV]; memset(tryc, 0, sizeof(tryc));
  while (pos >= 0) {
    if (pos == m) {
      // internal nbr counts in cnt; need exists eta multiset of size sv with
      // cnt[c]+eta[c] == 2 for all c  <=> all cnt[c] <= 2 and sum(2-cnt)==sv
      if (cnt[0]<=2 && cnt[1]<=2 && cnt[2]<=2 && (6-cnt[0]-cnt[1]-cnt[2]) == sv) return true;
      pos--;
      if (pos >= 0) { int y = order[pos]; if (pos < nDel) cnt[col[y]]--; col[y] = -1; }
      continue;
    }
    int x = order[pos]; bool adv = false;
    bool isNbr = pos < nDel;
    for (int c = tryc[pos]; c < 3; c++) {
      if (isNbr && cnt[c] >= 2) continue;
      bool ok = true; uint32_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb-1;
        if (u == v) continue;
        if (col[u] == c) { ok = false; break; } }
      if (ok) { col[x] = c; if (isNbr) cnt[c]++;
        tryc[pos] = c+1; pos++; if (pos < m) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { tryc[pos] = 0; pos--;
      if (pos >= 0) { int y = order[pos]; if (pos < nDel) cnt[col[y]]--; col[y] = -1; } }
  }
  return false;
}
int main() {
  string line;
  map<pair<int,int>, pair<long long,long long>> stat;  // (n,q) -> (frozenCert, survivors)
  while (getline(cin, line)) {
    if (line.rfind("STATE ", 0) != 0) continue;
    char ms[64], ht[8192], g6s[64]; int n, q;
    if (sscanf(line.c_str(), "STATE %d %d %63s %8191s %63s", &n, &q, ms, ht, g6s) != 5) continue;
    G g; if (!g6decode(string(g6s), g)) continue;
    bool cert = false;
    for (int v = 0; v < g.n && !cert; v++)
      if (!hasWitness(g, v)) cert = true;
    if (cert) stat[{n,q}].first++;
    else { stat[{n,q}].second++; printf("SURVIVOR n=%d q=%d g6=%s\n", n, q, g6s); }
  }
  for (auto& kv : stat)
    printf("STAT n=%d q=%d frozenCert=%lld survivors=%lld\n",
           kv.first.first, kv.first.second, kv.second.first, kv.second.second);
  return 0;
}
