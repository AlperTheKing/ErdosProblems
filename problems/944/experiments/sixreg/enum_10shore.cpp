// Enumerate candidate 10-vertex shores of a nontrivial 6-edge-cut in a
// 6-regular (4,1)-graph, with the same necessary filters used for 9-shores.
// Feed with: geng -c -D6 10 27:27 | enum_10shore.exe
//
// Filters:
//   B: b(v)=6-deg_A(v) is a valid nonnegative boundary degree, sum 6.
//   C: every proper 3-colouring has boundary vector in the 6-cut row-sum list.
//   T: no comparable non-neighbour forced by a b=0 vertex.
//   L: for every b=0 vertex v, some colouring of A-v has all colours appearing
//      at least twice on N_A(v); otherwise local multiplicity kills the shore.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <functional>
#include <iostream>
#include <string>
using namespace std;

static const int N = 10;
struct G {
  uint32_t adj[N];
  int deg(int u) const { return __builtin_popcount(adj[u]); }
};

static bool g6decode(const string& line, G& g) {
  if (line.empty() || line[0] - 63 != N) return false;
  memset(g.adj, 0, sizeof(g.adj));
  int bit = 0;
  for (int j = 1; j < N; j++) {
    for (int i = 0; i < j; i++) {
      int byte = 1 + bit / 6, off = 5 - bit % 6;
      if ((int)line.size() <= byte) return false;
      if (((line[byte] - 63) >> off) & 1) {
        g.adj[i] |= 1u << j;
        g.adj[j] |= 1u << i;
      }
      bit++;
    }
  }
  return true;
}

static int bnd[N];
static const int ALLOWED[4][3] = {{6,0,0}, {4,1,1}, {3,3,0}, {2,2,2}};

static bool vec_allowed(int s0, int s1, int s2) {
  int v[3] = {s0, s1, s2};
  sort(v, v + 3, greater<int>());
  for (auto& a : ALLOWED)
    if (v[0] == a[0] && v[1] == a[1] && v[2] == a[2]) return true;
  return false;
}

static long long nColGlobal;
static bool colourings_ok(const G& g) {
  int8_t col[N], tryc[N];
  memset(col, -1, sizeof(col));
  memset(tryc, 0, sizeof(tryc));
  int pos = 0;
  long long cnt = 0;
  while (pos >= 0) {
    if (pos == N) {
      cnt++;
      int s[3] = {0, 0, 0};
      for (int v = 0; v < N; v++) s[col[v]] += bnd[v];
      if (!vec_allowed(s[0], s[1], s[2])) {
        nColGlobal = cnt;
        return false;
      }
      pos--;
      continue;
    }
    bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      bool fine = true;
      uint32_t nb = g.adj[pos];
      while (nb) {
        int u = __builtin_ctz(nb);
        nb &= nb - 1;
        if (u < pos && col[u] == c) { fine = false; break; }
      }
      if (fine) {
        col[pos] = c;
        tryc[pos] = c + 1;
        pos++;
        if (pos < N) tryc[pos] = 0;
        adv = true;
        break;
      }
    }
    if (!adv) {
      col[pos] = -1;
      tryc[pos] = 0;
      pos--;
    }
  }
  nColGlobal = cnt;
  return cnt > 0;
}

static bool comparable_ok(const G& g) {
  for (int u = 0; u < N; u++) {
    if (bnd[u] != 0) continue;
    for (int v = 0; v < N; v++) {
      if (u == v || ((g.adj[u] >> v) & 1)) continue;
      uint32_t nu = g.adj[u] & ~(1u << v);
      if ((nu & ~g.adj[v]) == 0) return false;
    }
  }
  return true;
}

static bool local_multiplicity_ok_at(const G& g, int removed) {
  int verts[N - 1], m = 0;
  for (int v = 0; v < N; v++) if (v != removed) verts[m++] = v;
  int8_t col[N];
  memset(col, -1, sizeof(col));

  bool found = false;
  function<void(int)> dfs = [&](int idx) {
    if (found) return;
    if (idx == m) {
      int cnt[3] = {0, 0, 0};
      uint32_t nb = g.adj[removed];
      while (nb) {
        int u = __builtin_ctz(nb);
        nb &= nb - 1;
        cnt[col[u]]++;
      }
      if (cnt[0] >= 2 && cnt[1] >= 2 && cnt[2] >= 2) found = true;
      return;
    }
    int v = verts[idx];
    for (int c = 0; c < 3; c++) {
      bool fine = true;
      uint32_t nb = g.adj[v];
      while (nb) {
        int u = __builtin_ctz(nb);
        nb &= nb - 1;
        if (col[u] == c) { fine = false; break; }
      }
      if (!fine) continue;
      col[v] = c;
      dfs(idx + 1);
      col[v] = -1;
      if (found) return;
    }
  };
  dfs(0);
  return found;
}

static bool local_kill_ok(const G& g) {
  for (int v = 0; v < N; v++) {
    if (bnd[v] == 0 && !local_multiplicity_ok_at(g, v)) return false;
  }
  return true;
}

int main() {
  string line;
  long long total = 0, badB = 0, no3col = 0, badvec = 0, badcomp = 0, badlocal = 0, survive = 0;
  while (getline(cin, line)) {
    while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
    if (line.empty() || line[0] == '>') continue;
    G g;
    if (!g6decode(line, g)) continue;
    total++;
    bool okB = true;
    int sumB = 0;
    for (int v = 0; v < N; v++) {
      bnd[v] = 6 - g.deg(v);
      sumB += bnd[v];
      if (bnd[v] < 0 || bnd[v] > 5) okB = false;
    }
    if (!okB || sumB != 6) { badB++; continue; }
    if (!colourings_ok(g)) {
      if (nColGlobal == 0) no3col++; else badvec++;
      continue;
    }
    if (!comparable_ok(g)) { badcomp++; continue; }
    if (!local_kill_ok(g)) { badlocal++; continue; }
    survive++;
    printf("SURVIVOR: %s  ncol=%lld  b=", line.c_str(), nColGlobal);
    for (int v = 0; v < N; v++) printf("%d", bnd[v]);
    printf("\n");
    fflush(stdout);
    if (total % 10000 == 0) {
      fprintf(stderr, "PROGRESS total=%lld no3col=%lld badvec=%lld badcomp=%lld badlocal=%lld SURVIVORS=%lld\n",
              total, no3col, badvec, badcomp, badlocal, survive);
      fflush(stderr);
    }
  }
  printf("total=%lld badDeficiency=%lld not3col=%lld badBoundaryVec=%lld comparableNonNbr=%lld localMultiplicityKill=%lld SURVIVORS=%lld\n",
         total, badB, no3col, badvec, badcomp, badlocal, survive);
  return 0;
}
