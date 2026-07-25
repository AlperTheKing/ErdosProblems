// AUDIT of G12: EXACT re-verification of "no integrality-gap witness on N <= 11".
// The target established this with a FLOATING-POINT LP (scipy/HiGHS, tolerance 1e-6,
// no exact recheck).  Here the acceptance path is pure integer.
//
// For each connected triangle-free graph:
//   bip  = m - maxcut  (exhaustive over all 2^(n-1) cuts)
//   nu_int = maximum number of pairwise EDGE-DISJOINT odd cycles (exhaustive DFS)
// Since  nu_int <= nu* <= tau* <= bip, the integer identity  nu_int == bip  is an
// EXACT certificate that bip = nu* (no gap) for that graph.  Graphs with
// nu_int < bip are printed as RESIDUE and must then be settled by an exact LP.
#include <cstdio>
#include <cstring>
#include <string>
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int n, m;
vector<unsigned> adj;
vector<pair<int,int>> E;
int eidx[32][32];
vector<unsigned long long> cyc;      // odd cycles as edge bitmasks

void dfs(int root, int cur, unsigned long long used_e, unsigned vis, int len, int first) {
    unsigned x = adj[cur];
    while (x) {
        int w = __builtin_ctz(x); x &= x - 1;
        if (w == root) {
            if (len >= 3 && (len % 2 == 1) && first < cur)   // canonical: first < last
                cyc.push_back(used_e | (1ULL << eidx[cur][root]));
            continue;
        }
        if (w < root || ((vis >> w) & 1)) continue;
        dfs(root, w, used_e | (1ULL << eidx[cur][w]), vis | (1u << w), len + 1,
            (len == 1 ? w : first));
    }
}

int need;
bool search_disjoint(int start, int have, unsigned long long used) {
    if (have == need) return true;
    for (int i = start; i < (int)cyc.size(); i++) {
        if ((int)cyc.size() - i < need - have) break;
        if (cyc[i] & used) continue;
        if (search_disjoint(i + 1, have + 1, used | cyc[i])) return true;
    }
    return false;
}

int main() {
    string line;
    long long cnt = 0, residue = 0;
    while (getline(cin, line)) {
        while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
        if (line.empty()) continue;
        n = line[0] - 63;
        vector<int> bits;
        for (size_t i = 1; i < line.size(); i++) {
            int v = line[i] - 63;
            for (int k = 5; k >= 0; k--) bits.push_back((v >> k) & 1);
        }
        adj.assign(n, 0u); E.clear();
        int p = 0;
        for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
            if (p < (int)bits.size() && bits[p]) {
                adj[i] |= 1u << j; adj[j] |= 1u << i;
                eidx[i][j] = eidx[j][i] = (int)E.size(); E.push_back({i, j});
            }
            p++;
        }
        m = (int)E.size();
        unsigned full = (1u << n) - 1;
        int best = m;
        for (unsigned S = 0; S < (1u << (n - 1)); S++) {
            unsigned T = full ^ S; int cross = 0; unsigned x = S;
            while (x) { int u = __builtin_ctz(x); cross += __builtin_popcount(adj[u] & T); x &= x - 1; }
            if (m - cross < best) { best = m - cross; if (!best) break; }
        }
        cnt++;
        if (best == 0) continue;                  // bipartite: bip = nu* = 0
        cyc.clear();
        for (int r = 0; r < n; r++) dfs(r, r, 0ULL, 1u << r, 1, -1);
        sort(cyc.begin(), cyc.end());
        cyc.erase(unique(cyc.begin(), cyc.end()), cyc.end());
        need = best;
        if (!search_disjoint(0, 0, 0ULL)) {
            residue++;
            if (residue < 100000) printf("RESIDUE %s n=%d m=%d bip=%d ncyc=%d\n",
                                     line.c_str(), n, m, best, (int)cyc.size());
        }
    }
    printf("graphs=%lld  residue(nu_int < bip, need exact LP)=%lld\n", cnt, residue);
    return 0;
}
