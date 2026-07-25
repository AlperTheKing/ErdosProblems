// Q2_exhaust.cpp -- exhaustive test on ALL maximal triangle-free graphs, N <= 12.
//
// reads graph6 on stdin (output of geng -t -c n), keeps the MAXIMAL ones
// (every non-adjacent pair has a common neighbour), then for every graph:
//
//  PART A  at every MAXIMUM cut: verify   25|M| <= N^2,  the charge identity
//          sum_v mu(v) = N^2 - 25|M| with mu(v) = N - (25/2)d_M(v)  (doubled to
//          stay integral), and that every family-(*) inequality holds
//              Delta(N(v) u T) <= 0  for all v, all independent T disjoint N(v).
//          Any violation is a genuine failure and is printed with the graph6.
//
//  PART B  over ALL cuts: find those that satisfy
//              (i)  sigma(v) >= 0            (single-vertex switches)
//              (ii) switch-star sigma(v) >= sum_{a in T}(2-sigma(a)), T c N_B(v)
//              (iii) the whole family (*)
//          yet have 25|M| > N^2.  Each such cut is an EXACT witness that the
//          corresponding discharging mechanism cannot prove the conjecture.
//
// All arithmetic is integer.
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;
typedef long long ll;

int N;
int adj[16];          // bitmask adjacency
vector<int> indepSets;

bool decode(const char* s, int& n, int* A) {
    int len = strlen(s);
    while (len && (s[len - 1] == '\n' || s[len - 1] == '\r')) len--;
    if (len <= 0) return false;
    n = s[0] - 63;
    for (int i = 0; i < n; i++) A[i] = 0;
    int idx = 0, bit = 0, pos = 1;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            int b = (s[pos] - 63) >> (5 - bit) & 1;
            if (b) { A[i] |= 1 << j; A[j] |= 1 << i; }
            if (++bit == 6) { bit = 0; pos++; }
        }
    return true;
}

bool isMaximalTF(int n, int* A) {
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            if (!((A[i] >> j) & 1) && (A[i] & A[j]) == 0) return false;
    return true;
}

int main(int argc, char** argv) {
    char line[512];
    ll nGraphs = 0, nMaxCutChecked = 0, failA = 0, witB = 0;
    ll bestNum = 0, bestDen = 1; string bestDesc;
    while (fgets(line, sizeof line, stdin)) {
        int n, A[16];
        if (!decode(line, n, A)) continue;
        if (!isMaximalTF(n, A)) continue;
        nGraphs++;
        N = n;
        memcpy(adj, A, sizeof A);
        string g6(line);
        while (!g6.empty() && (g6.back() == '\n' || g6.back() == '\r')) g6.pop_back();
        int full = (1 << n) - 1;
        // independent sets
        indepSets.clear();
        for (int S = 0; S <= full; S++) {
            bool ok = true;
            for (int i = 0; i < n && ok; i++) if (S >> i & 1) if (adj[i] & S) ok = false;
            if (ok) indepSets.push_back(S);
        }
        // all cuts (vertex 0 fixed on side 0)
        int bestM = 1 << 30;
        vector<int> cuts;
        vector<int> Mv(1 << (n - 1));
        for (int cm = 0; cm < (1 << (n - 1)); cm++) {
            int X = cm << 1;                    // side-1 membership, vertex0 -> side 0
            int M = 0;
            for (int i = 0; i < n; i++)
                for (int j = i + 1; j < n; j++)
                    if ((adj[i] >> j & 1) && (((X >> i) & 1) == ((X >> j) & 1))) M++;
            Mv[cm] = M;
            if (M < bestM) bestM = M;
        }
        for (int cm = 0; cm < (1 << (n - 1)); cm++) {
            int X = cm << 1;
            int M = Mv[cm];
            int sig[16], dM[16], dB[16];
            bool sigok = true;
            for (int i = 0; i < n; i++) {
                int mm = 0, bb = 0;
                for (int j = 0; j < n; j++) if (adj[i] >> j & 1) {
                    if (((X >> i) & 1) == ((X >> j) & 1)) mm++; else bb++;
                }
                dM[i] = mm; dB[i] = bb; sig[i] = bb - mm;
                if (sig[i] < 0) sigok = false;
            }
            bool isMax = (M == bestM);
            if (!isMax && !sigok) continue;
            // --- switch-star (exact best T = all B-neighbours with sigma <= 1)
            bool ssok = true;
            for (int i = 0; i < n && ssok; i++) {
                int rhs = 0;
                for (int j = 0; j < n; j++)
                    if ((adj[i] >> j & 1) && (((X >> i) & 1) != ((X >> j) & 1)) && sig[j] <= 1)
                        rhs += 2 - sig[j];
                if (sig[i] < rhs) ssok = false;
            }
            // --- family (*)  max over v, independent T
            int worstStar = -1073741824; int wv = -1, wT = 0;
            for (int v = 0; v < n; v++) {
                int Nv = adj[v];
                ll base = 0;
                for (int u = 0; u < n; u++) if (Nv >> u & 1) base -= sig[u];
                int w[16];
                for (int u = 0; u < n; u++) {
                    if (Nv >> u & 1) { w[u] = -1048576; continue; }
                    int b = 0, m = 0;
                    for (int t = 0; t < n; t++) if ((adj[u] >> t & 1) && (Nv >> t & 1)) {
                        if (((X >> u) & 1) == ((X >> t) & 1)) m++; else b++;
                    }
                    w[u] = -sig[u] + 2 * b - 2 * m;
                }
                for (int S : indepSets) {
                    if (S & Nv) continue;
                    ll tot = base;
                    for (int u = 0; u < n; u++) if (S >> u & 1) tot += w[u];
                    if (tot > worstStar) { worstStar = (int)tot; wv = v; wT = S; }
                }
            }
            if (isMax) {
                nMaxCutChecked++;
                ll sumMu2 = 0;                       // 2*mu summed = 2N^2 - 50M
                for (int i = 0; i < n; i++) sumMu2 += 2LL * n - 25LL * dM[i];
                bool bad = false;
                if (25LL * M > (ll)n * n) { bad = true; printf("FAIL-A(bound) %s cut=%d M=%d N=%d\n", g6.c_str(), X, M, n); }
                if (sumMu2 != 2LL * n * n - 50LL * M) { bad = true; printf("FAIL-A(charge) %s cut=%d\n", g6.c_str(), X); }
                if (worstStar > 0) { bad = true; printf("FAIL-A(star) %s cut=%d v=%d T=%d Delta=%d\n", g6.c_str(), X, wv, wT, worstStar); }
                if (bad) failA++;
            }
            if (!isMax && sigok && ssok && worstStar <= 0 && 25LL * M > (ll)n * n) {
                witB++;
                printf("WITNESS-B %s N=%d cut=0x%x M=%d 25M-N^2=%lld sigma=[", g6.c_str(), n, X, M, 25LL * M - (ll)n * n);
                for (int i = 0; i < n; i++) printf("%d%s", sig[i], i + 1 < n ? "," : "]\n");
                ll num = 25LL * M, den = (ll)n * n;
                if ((__int128)num * bestDen > (__int128)bestNum * den) {
                    bestNum = num; bestDen = den;
                    char d[256]; snprintf(d, sizeof d, "%s N=%d cut=0x%x M=%d", g6.c_str(), n, X, M);
                    bestDesc = d;
                }
            }
        }
    }
    printf("# maximal-triangle-free graphs processed: %lld\n", nGraphs);
    printf("# maximum cuts checked (PART A): %lld   failures: %lld\n", nMaxCutChecked, failA);
    printf("# PART B witnesses (locally-max + switch-star + family(*) but 25|M| > N^2): %lld\n", witB);
    if (witB) printf("# best PART B ratio 25M/N^2 = %lld/%lld  at  %s\n", bestNum, bestDen, bestDesc.c_str());
    return 0;
}
