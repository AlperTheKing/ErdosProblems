// Independent re-verification of item 3's exhaustive claim:
//    25 * ARCBOUND(mu) <= (sum x)^2   for every integer weighting of a circle graph.
// Pure integer arithmetic: with integer weights w summing to q, mono(S)*q^2 is the integer
// M(S) = sum_{u<v adjacent, same side} w_u w_v, and the claim is  25 * min_S M(S) <= q^2 .
// Enumerates ALL weightings (zeros allowed) of Gamma_m with total weight exactly q.
//
// build: C:\msys64\mingw64\bin\clang++.exe -O3 -march=native -std=c++17 P4_arcexhaust.cpp -o P4_arcexhaust.exe
// run:   P4_arcexhaust.exe m q
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cstdint>
using namespace std;

int m, q;
vector<vector<int>> adj;      // adjacency of Gamma_m
long long w[64];

// returns 25 * min over arcs of M(S)   and   q*q, so caller compares
long long arcbound_times25(long long &best_out) {
    long long Wtot = 0;
    long long d[64];
    for (int i = 0; i < m; i++) {
        d[i] = 0;
        for (int j = 0; j < m; j++) if (adj[i][j]) d[i] += w[j];
        Wtot += w[i] * d[i];
    }
    Wtot /= 2;                       // total adjacent-pair weight
    long long best = Wtot;           // empty arc: mono = Wtot
    for (int st = 0; st < m; st++) {
        long long cross = 0;
        long long s[64];
        for (int j = 0; j < m; j++) s[j] = 0;
        for (int L = 1; L <= m; L++) {
            int j = (st + L - 1) % m;
            cross += w[j] * d[j] - 2 * w[j] * s[j];
            for (int v = 0; v < m; v++) if (adj[j][v]) s[v] += w[j];
            long long mono = Wtot - cross;
            if (mono < best) best = mono;
        }
    }
    best_out = best;
    return 25 * best;
}

long long worst_num = -1, worst_den = 1;
vector<long long> worst_w;
long long violations = 0, tested = 0, equality = 0;
vector<long long> eq_example;
int eq_atoms = -1;

void rec(int i, int rem) {
    if (i == m - 1) {
        w[i] = rem;
        long long best;
        long long lhs = arcbound_times25(best);
        long long rhs = (long long)q * q;
        tested++;
        if (lhs > rhs) {
            violations++;
            if (violations <= 5) {
                printf("  *** VIOLATION 25*ARCBOUND=%lld > q^2=%lld  w =", lhs, rhs);
                for (int t = 0; t < m; t++) printf(" %lld", w[t]);
                printf("\n");
            }
        }
        if (lhs == rhs) {
            equality++;
            if (getenv("DUMP_EQ")) {
                printf("EQ");
                for (int t = 0; t < m; t++) printf(" %lld", w[t]);
                printf("\n");
            }
            int atoms = 0;
            for (int t = 0; t < m; t++) if (w[t]) atoms++;
            if (eq_atoms < 0 || atoms != eq_atoms) {
                if (eq_atoms < 0) { eq_atoms = atoms; eq_example.assign(w, w + m); }
                else if (atoms != eq_atoms) {
                    printf("  equality with a DIFFERENT atom count %d (first was %d):", atoms, eq_atoms);
                    for (int t = 0; t < m; t++) printf(" %lld", w[t]);
                    printf("\n");
                    eq_atoms = -2;   // stop reporting
                }
            }
        }
        // track the largest 25*ARCBOUND / q^2
        if (worst_num < 0 || lhs * worst_den > worst_num * rhs) {
            worst_num = lhs; worst_den = rhs;
            worst_w.assign(w, w + m);
        }
        return;
    }
    for (int t = 0; t <= rem; t++) { w[i] = t; rec(i + 1, rem - t); }
}

int main(int argc, char **argv) {
    m = atoi(argv[1]); q = atoi(argv[2]);
    adj.assign(m, vector<int>(m, 0));
    for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) {
        int dd = abs(i - j); dd = min(dd, m - dd);
        adj[i][j] = (i != j && 3 * dd > m);
    }
    rec(0, q);
    printf("Gamma_%d, all %lld weightings of total q=%d: violations of 25*ARCBOUND <= q^2 : %lld\n",
           m, tested, q, violations);
    printf("   max 25*ARCBOUND/q^2 = %lld/%lld = %.8f   at w =", worst_num, worst_den,
           (double)worst_num / (double)worst_den);
    for (int t = 0; t < m; t++) printf(" %lld", worst_w[t]);
    printf("\n   equality cases: %lld", equality);
    if (eq_atoms >= 0) printf("   (all with %d atoms)", eq_atoms);
    else if (eq_atoms == -2) printf("   (MIXED atom counts - see above)");
    printf("\n");
    return 0;
}
