// AUDIT of G8 section 6.2 for k = 6,7 (the report verified only k = 2..5 but states
// the block "for every k >= 3").
// Computes  min over cuts S of  nu(mono(S))  for And(k), exactly.
// nu is computed by exhaustive recursion over the lowest uncovered vertex (own routine).
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cstdint>
using namespace std;

static int n;
static vector<pair<int,int>> E;

static int nbest;
static vector<pair<int,int>> ME;

static void mrec(int idx, uint32_t used, int cur) {
    if (cur + (int)(ME.size() - idx) <= nbest) return;
    if (idx == (int)ME.size()) { if (cur > nbest) nbest = cur; return; }
    int u = ME[idx].first, v = ME[idx].second;
    if (!((used >> u) & 1) && !((used >> v) & 1))
        mrec(idx+1, used | (1u<<u) | (1u<<v), cur+1);
    mrec(idx+1, used, cur);
}

static int matching(vector<pair<int,int>> &mono) {
    ME = mono; nbest = 0; mrec(0, 0u, 0); return nbest;
}

int main(int argc, char **argv) {
    int k = atoi(argv[1]);
    n = 3*k - 1;
    for (int i = 0; i < n; i++)
        for (int j = i+1; j < n; j++) {
            int d = (j - i) % n;
            if (d % 3 == 1 || (n - d) % 3 == 1) E.push_back({i,j});
        }
    printf("And(%d): n=%d |E|=%zu\n", k, n, E.size());
    int best = 1000; uint32_t bestmask = 0;
    for (uint32_t mask = 0; mask < (1u << (n-1)); mask++) {
        int side[32];
        side[0] = 0;
        for (int v = 1; v < n; v++) side[v] = (mask >> (v-1)) & 1;
        vector<pair<int,int>> mono;
        for (auto &e : E) if (side[e.first] == side[e.second]) mono.push_back(e);
        if (mono.empty()) { printf("  BIPARTITE CUT?! mask=%u\n", mask); continue; }
        // cheap greedy lower bound first
        uint32_t used = 0; int g = 0;
        for (auto &e : mono)
            if (!((used>>e.first)&1) && !((used>>e.second)&1)) { used |= (1u<<e.first)|(1u<<e.second); g++; }
        if (g >= best) continue;                 // cannot improve the incumbent
        int nu = matching(mono);
        if (nu < best) { best = nu; bestmask = mask; }
    }
    printf("  min over cuts of nu(mono(S)) = %d   (k-1 = %d)   witness mask=%u\n", best, k-1, bestmask);
    printf("  nu^2 = %d  vs  n^2/25 = %.4f  =>  %s\n", best*best, n*n/25.0,
           (double)(best*best) > n*n/25.0 ? "BLOCKED" : "POSSIBLE");
    return 0;
}
