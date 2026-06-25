// PC1/PC2 verification (deficiency-0 variant) on full 6-regular stock.
// For every graph G (g6, 6-regular, n<=13), every v, every proper 3-colouring
// psi of G-v with N(v) colour counts (2,2,2):
//   per k: q_k=|X_k|, pair graph P_k=G[(V\{v})\X_k]; components -> s,t,W,R
//   PC1 claim (b=0): W_1=W_2=W_3=0 impossible for n>=8  -> count violations
//   PC2 claim (b=0): 11 q_k + 5 W_k - 8 R_k >= 5n-13    -> count violations
// usage: pc_check <n> <file> [nthreads]
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <mutex>
#include <algorithm>
using namespace std;
static int N;

struct G { uint16_t adj[13]; };

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

static atomic<long long> nGraphs(0), nWitness(0), pc1Viol(0), pc2Viol(0);
static atomic<long long> minSlack(1u<<30);
static mutex outMu;

static void checkWitness(const G& g, int v, const int* col, const string& line) {
  // colour counts in N(v) already verified (2,2,2)
  int q[3] = {0,0,0};
  for (int u = 0; u < N; u++) if (u != v) q[col[u]]++;
  for (int k = 0; k < 3; k++) {
    // component scan of P_k = induced on {u != v : col[u] != k}
    int compW = 0, compR = 0;
    uint16_t inP = 0;
    for (int u = 0; u < N; u++) if (u != v && col[u] != k) inP |= 1u<<u;
    uint16_t seen = 0;
    int W = 0, R = 0;
    for (int u = 0; u < N; u++) {
      if (!((inP >> u) & 1) || ((seen >> u) & 1)) continue;
      // BFS
      uint16_t comp = 1u<<u, frontier = 1u<<u;
      while (frontier) {
        uint16_t next = 0;
        for (int x = 0; x < N; x++) if ((frontier >> x) & 1)
          next |= (uint16_t)(g.adj[x] & inP & ~comp);
        comp |= next; frontier = next;
      }
      seen |= comp;
      int sz = __builtin_popcount(comp);
      if (sz >= 3) { W += sz; R++; }
    }
    compW = W; compR = R;
    long long lhs = 11LL*q[k] + 5LL*compW - 8LL*compR, rhs = 5LL*N - 13;
    long long slack = lhs - rhs;
    long long cur = minSlack.load();
    while (slack < cur && !minSlack.compare_exchange_weak(cur, slack)) {}
    if (slack < 0) {
      pc2Viol++;
      lock_guard<mutex> lk(outMu);
      printf("PC2-VIOLATION %s v=%d k=%d q=%d W=%d R=%d\n", line.c_str(), v, k, q[k], compW, compR);
    }
    if (k == 0) {
      // PC1 needs all three W to be 0; collect via flag trick below
    }
  }
  // PC1: recompute all three W quickly
  bool allSmall = true;
  for (int k = 0; k < 3 && allSmall; k++) {
    uint16_t inP = 0;
    for (int u = 0; u < N; u++) if (u != v && col[u] != k) inP |= 1u<<u;
    uint16_t seen = 0;
    for (int u = 0; u < N && allSmall; u++) {
      if (!((inP >> u) & 1) || ((seen >> u) & 1)) continue;
      uint16_t comp = 1u<<u, frontier = 1u<<u;
      while (frontier) {
        uint16_t next = 0;
        for (int x = 0; x < N; x++) if ((frontier >> x) & 1)
          next |= (uint16_t)(g.adj[x] & inP & ~comp);
        comp |= next; frontier = next;
      }
      seen |= comp;
      if (__builtin_popcount(comp) >= 3) allSmall = false;
    }
  }
  if (allSmall) {
    pc1Viol++;
    lock_guard<mutex> lk(outMu);
    printf("PC1-INSTANCE %s v=%d (all components <=2!)\n", line.c_str(), v);
  }
  nWitness++;
}

static void enumColourings(const G& g, int v, const string& line) {
  // backtracking over vertices != v in index order
  int order[13], m = 0;
  for (int u = 0; u < N; u++) if (u != v) order[m++] = u;
  int col[13]; memset(col, -1, sizeof(col));
  // iterative DFS
  int pos = 0, choice[13]; memset(choice, 0, sizeof(choice));
  while (pos >= 0) {
    if (pos == m) {
      // full colouring; check N(v) counts
      int cnt[3] = {0,0,0};
      for (int u = 0; u < N; u++) if ((g.adj[v] >> u) & 1) cnt[col[u]]++;
      if (cnt[0] == 2 && cnt[1] == 2 && cnt[2] == 2) checkWitness(g, v, col, line);
      pos--; continue;
    }
    int u = order[pos];
    bool advanced = false;
    for (int c = choice[pos]; c < 3; c++) {
      bool ok = true;
      for (int x = 0; x < N && ok; x++)
        if (((g.adj[u] >> x) & 1) && x != v && col[x] == c) ok = false;
      if (ok) { col[u] = c; choice[pos] = c + 1; pos++; if (pos <= m) choice[pos] = 0; advanced = true; break; }
    }
    if (!advanced) { col[u] = -1; choice[pos] = 0; pos--; if (pos >= 0) { col[order[pos]] = -1; choice[pos] = choice[pos]; } }
  }
}

int main(int argc, char** argv) {
  if (argc < 3) { fprintf(stderr, "usage: pc_check <n> <file> [nthreads]\n"); return 1; }
  N = atoi(argv[1]);
  int nt = (argc > 3) ? atoi(argv[3]) : 8;
  FILE* f = fopen(argv[2], "r");
  if (!f) { fprintf(stderr, "cannot open %s\n", argv[2]); return 1; }
  vector<string> lines;
  char buf[256];
  while (fgets(buf, sizeof buf, f)) {
    size_t l = strcspn(buf, "\r\n"); buf[l] = 0;
    if (buf[0] && buf[0] != '>') lines.push_back(buf);
  }
  fclose(f);
  atomic<size_t> idx(0);
  vector<thread> th;
  for (int t = 0; t < nt; t++) th.emplace_back([&]{
    size_t i;
    while ((i = idx.fetch_add(1)) < lines.size()) {
      G g;
      if (!g6decode(lines[i], g)) continue;
      nGraphs++;
      for (int v = 0; v < N; v++) enumColourings(g, v, lines[i]);
    }
  });
  for (auto& x : th) x.join();
  printf("n=%d graphs=%lld witnesses=%lld PC1instances=%lld PC2violations=%lld minPC2slack=%lld\n",
         N, nGraphs.load(), nWitness.load(), pc1Viol.load(), pc2Viol.load(),
         (long long)minSlack.load());
  return 0;
}
