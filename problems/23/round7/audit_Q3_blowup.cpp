// audit_Q3_blowup.cpp -- exact-integer upper bounds for dist(G[t]) (blow-up invariance audit).
// Any value printed is the cost of an EXPLICIT template phi, hence an exact upper bound
// for dist(G[t]).  If it is < t^2 * dist(G) the "R is blow-up invariant" claim is refuted.
// usage: audit_Q3_blowup <g6> <t> <restarts>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

static int CONS[5][5];

int main(int argc, char **argv) {
    string s = argv[1];
    int T = atoi(argv[2]);
    long long restarts = atoll(argv[3]);
    // graph6 decode
    vector<int> b; for (char c : s) b.push_back((int)(unsigned char)c - 63);
    int n = b[0]; size_t p = 1;
    vector<vector<char>> A(n, vector<char>(n, 0));
    long long idx = 0;
    for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
        int bit = 0; long long by = idx / 6, bi = idx % 6;
        if (p + by < b.size()) bit = (b[p + by] >> (5 - bi)) & 1;
        if (bit) { A[i][j] = A[j][i] = 1; }
        idx++;
    }
    int N = n * T;
    vector<vector<char>> B(N, vector<char>(N, 0));
    for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (A[u][v])
        for (int a = 0; a < T; a++) for (int c = 0; c < T; c++)
            B[u * T + a][v * T + c] = 1;
    for (int a = 0; a < 5; a++) for (int c = 0; c < 5; c++) { int d = ((a - c) % 5 + 5) % 5; CONS[a][c] = (d == 1 || d == 4); }
    auto cost = [&](vector<int> &col) {
        long long tot = 0;
        for (int u = 0; u < N; u++) for (int v = u + 1; v < N; v++)
            if ((int)B[u][v] != CONS[col[u]][col[v]]) tot++;
        return tot;
    };
    long long best = -1; vector<int> bestcol;
    if (n <= 13) {   // exact dist(G) by own exhaustive 5^(n-1), plus the pulled-back template
        vector<int> c(n, 0); long long tot5 = 1; for (int i = 1; i < n; i++) tot5 *= 5;
        long long bb = -1; vector<int> bc;
        for (long long code = 0; code < tot5; code++) {
            long long x = code; for (int i = 1; i < n; i++) { c[i] = x % 5; x /= 5; }
            long long q = 0;
            for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++)
                if ((int)A[u][v] != CONS[c[u]][c[v]]) q++;
            if (bb < 0 || q < bb) { bb = q; bc = c; }
        }
        printf("exact dist(G) = %lld (own exhaustive 5^%d)\n", bb, n - 1);
        vector<int> col(N);
        for (int u = 0; u < n; u++) for (int a = 0; a < T; a++) col[u * T + a] = bc[u];
        long long q = cost(col);
        printf("pulled-back template on G[%d] costs %lld  (t^2*dist(G) = %lld)\n", T, q, bb * (long long)T * T);
        best = q; bestcol = col;
    }
    unsigned long long seed = 987654321ULL;
    auto rnd = [&]() { seed ^= seed << 13; seed ^= seed >> 7; seed ^= seed << 17; return seed; };
    vector<int> col(N);
    for (long long r = 0; r < restarts; r++) {
        for (int v = 0; v < N; v++) col[v] = rnd() % 5;
        bool improved = true;
        while (improved) {
            improved = false;
            for (int v = 0; v < N; v++) {
                int bc = 1 << 29, ba = col[v];
                for (int a = 0; a < 5; a++) {
                    int q = 0;
                    for (int u = 0; u < N; u++) if (u != v) if ((int)B[u][v] != CONS[col[u]][a]) q++;
                    if (q < bc) { bc = q; ba = a; }
                }
                if (ba != col[v]) { col[v] = ba; improved = true; }
            }
        }
        long long q = cost(col);
        if (best < 0 || q < best) { best = q; bestcol = col; printf("new best %lld at restart %lld\n", best, r); fflush(stdout); }
    }
    printf("BEST UPPER BOUND dist(G[%d]) <= %lld\n", T, best);
    printf("template:");
    for (int v = 0; v < N; v++) printf(" %d", bestcol[v]);
    printf("\n");
    return 0;
}
