// exact minimum edit distance from a graph to the C5-blow-up family on the same vertex set
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
using namespace std;
int n, m; uint32_t adj[32]; int cls[32]; int bestd; int bestc[32];
// cost contributed by pairs (i,j) with i<j once both assigned
static inline int paircost(int i, int j) {
    bool e = (adj[i] >> j) & 1;
    int dd = (cls[i] - cls[j] + 5) % 5;
    bool b = (dd == 1 || dd == 4);
    return e != b;
}
void dfs(int v, int cost) {
    if (cost >= bestd) return;
    if (v == n) { bestd = cost; memcpy(bestc, cls, sizeof cls); return; }
    int lim = (v == 0) ? 1 : 5;
    for (int c = 0; c < lim; c++) {
        cls[v] = c;
        int add = 0;
        for (int u = 0; u < v; u++) add += paircost(u, v);
        dfs(v + 1, cost + add);
    }
}
int main(int argc, char **argv) {
    string s = argv[1];
    n = (int)s[0] - 63;
    vector<int> bits;
    for (size_t i = 1; i < s.size(); i++) { int v = (int)s[i] - 63; for (int k = 5; k >= 0; k--) bits.push_back((v >> k) & 1); }
    memset(adj, 0, sizeof adj); m = 0; size_t p = 0;
    for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) { if (p < bits.size() && bits[p]) { adj[i] |= 1u << j; adj[j] |= 1u << i; m++; } p++; }
    bestd = 1 << 30;
    dfs(0, 0);
    printf("n=%d |E|=%d  min edit distance to a C5 blow-up = %d\n  classes:", n, m, bestd);
    for (int i = 0; i < n; i++) printf(" %d", bestc[i]);
    printf("\n");
    int sz[5] = {0,0,0,0,0};
    for (int i = 0; i < n; i++) sz[bestc[i]]++;
    printf("  nearest blow-up sizes: %d %d %d %d %d  (its bip = min_i n_i n_{i+1} = ", sz[0],sz[1],sz[2],sz[3],sz[4]);
    int mn = 1<<30; for (int i=0;i<5;i++){ int t=sz[i]*sz[(i+1)%5]; if(t<mn) mn=t; }
    printf("%d)\n", mn);
    return 0;
}
