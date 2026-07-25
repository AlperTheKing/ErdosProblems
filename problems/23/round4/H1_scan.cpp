// H1_scan.cpp -- exhaustive EXACT integer scan of the arc-cut / W-square
// conjectures on Gamma_m (m equally spaced points, x~y iff 3*circdist > 1 ).
//
// A measure is an integer weight vector w[0..m-1] >= 0 with sum q (zeros allowed,
// so every n-atom circular configuration realisable on the grid is covered).
// With mass w_i/q:
//     W  = E / q^2      where E   = sum_{i<j, adj} w_i w_j            (integer)
//     ARCBOUND = A / q^2 where A  = min over cyclic intervals of the
//                        monochromatic weighted edge count            (integer)
// Conjectures, in pure integer form:
//     ARC-CUT :  25 * A <= q^2
//     W-SQUARE:  A * q^2 <= E^2
// Rotation+reflection canonical enumeration.
//
// build: clang++ -O3 -march=native -std=c++17 H1_scan.cpp -o H1_scan.exe
// usage: H1_scan.exe m qmax
#include <cstdio>
#include <cstdint>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

typedef long long ll;
typedef __int128 lll;

int m, q;
bool adjm[32][32];
int w[32];

ll bestArcRatioNum = 0, bestArcRatioDen = 1;   // max of 25*A/q^2
ll bestWsqNum = 0, bestWsqDen = 1;             // max of A*q^2 / E^2
int bestArcW[32], bestWsqW[32];
ll violArc = 0, violWsq = 0, violWsqQ = 0;
ll bestQnum=0,bestQden=1; int bestQw[32];
ll count_vec = 0;
// regime W > 1/5  <=> 5E > q^2 : record max A there
ll bigWbestA = -1; int bigWbestW[32]; ll bigWbestE = 0, bigWbestQ = 0;

static inline bool canonical() {
    // lexicographically minimal among all rotations and reflections
    for (int r = 0; r < m; r++) {
        for (int refl = 0; refl < 2; refl++) {
            if (r == 0 && refl == 0) continue;
            int c = 0;
            for (int i = 0; i < m; i++) {
                int j = refl ? ((r - i) % m + m) % m : (r + i) % m;
                if (w[j] != w[i]) { c = (w[j] < w[i]) ? -1 : 1; break; }
            }
            if (c < 0) return false;
        }
    }
    return true;
}

static void evaluate() {
    ll E = 0;
    for (int i = 0; i < m; i++) if (w[i])
        for (int j = i + 1; j < m; j++) if (w[j] && adjm[i][j]) E += (ll)w[i] * w[j];
    // min over cyclic intervals of monochromatic weight
    ll A = E;                    // empty interval
    for (int s = 0; s < m; s++) {
        bool in[32]; memset(in, 0, sizeof(in));
        ll cut = 0;
        for (int L = 1; L <= m; L++) {
            int k = (s + L - 1) % m;
            if (w[k]) {
                ll d = 0;
                for (int j = 0; j < m; j++) {
                    if (j == k || !w[j] || !adjm[k][j]) continue;
                    if (in[j]) d -= (ll)w[k] * w[j]; else d += (ll)w[k] * w[j];
                }
                cut += d;
            }
            in[k] = true;
            ll mono = E - cut;
            if (mono < A) A = mono;
        }
    }
    count_vec++;
    ll qq = (ll)q * q;
    // arc-cut : 25*A <= q^2
    if ((lll)25 * A > (lll)qq) { violArc++;
        printf("ARC-CUT VIOLATION m=%d q=%d A=%lld E=%lld w=", m, q, A, E);
        for (int i = 0; i < m; i++) printf("%d%s", w[i], i + 1 < m ? "," : "\n");
    }
    if ((lll)A * qq * bestArcRatioDen > (lll)bestArcRatioNum * qq * 0 + (lll)bestArcRatioNum * 1 * qq) {}
    // track max A/q^2
    if ((lll)A * bestArcRatioDen > (lll)bestArcRatioNum * qq) {
        bestArcRatioNum = A; bestArcRatioDen = qq; memcpy(bestArcW, w, sizeof(w));
    }
    // W-square : A*q^2 <= E^2
    if ((lll)A * qq > (lll)E * E) { violWsq++; violWsqQ++;
        if (violWsqQ <= 2) {
            printf("W-SQUARE VIOLATION m=%d q=%d A=%lld E=%lld w=", m, q, A, E);
            for (int i = 0; i < m; i++) printf("%d%s", w[i], i + 1 < m ? "," : "\n");
        }
    }
    if (E > 0 && (lll)A * qq * bestWsqDen > (lll)bestWsqNum * (lll)E * E) {
        bestWsqNum = A * qq; bestWsqDen = E * E; memcpy(bestWsqW, w, sizeof(w));
    }
    if (E > 0 && (lll)A * qq * bestQden > (lll)bestQnum * (lll)E * E) {
        bestQnum = A * qq; bestQden = E * E; memcpy(bestQw, w, sizeof(w));
    }
    // regime W > 1/5
    if ((lll)5 * E > (lll)qq) {
        if (A > 0 && (bigWbestA < 0 || (lll)A * bigWbestQ * bigWbestQ > (lll)bigWbestA * qq)) {
            bigWbestA = A; bigWbestE = E; bigWbestQ = q; memcpy(bigWbestW, w, sizeof(w));
        }
    }
}

static void rec(int i, int rem) {
    if (i == m - 1) { w[i] = rem; if (canonical()) evaluate(); return; }
    for (int v = 0; v <= rem; v++) { w[i] = v; rec(i + 1, rem - v); }
}

int main(int argc, char** argv) {
    int mm = atoi(argv[1]);
    int qmax = atoi(argv[2]);
    m = mm;
    for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) {
        int d = abs(i - j); d = min(d, m - d);
        adjm[i][j] = (3 * d > m);
    }
    for (q = 1; q <= qmax; q++) {
        violWsqQ = 0; bestQnum = 0; bestQden = 1;
        rec(0, q);
        printf("  [m=%d q=%d] wsq_violations=%lld  maxratio=%.6f\n", m, q, violWsqQ,
               bestQden ? (double)bestQnum/(double)bestQden : 0.0);
    }
    printf("m=%d qmax=%d vectors=%lld  ARC-CUT violations=%lld  W-SQUARE violations=%lld\n",
           m, qmax, count_vec, violArc, violWsq);
    printf("  max ARCBOUND = %lld/%lld = %.8f   at w=", bestArcRatioNum, bestArcRatioDen,
           (double)bestArcRatioNum / (double)bestArcRatioDen);
    for (int i = 0; i < m; i++) printf("%d%s", bestArcW[i], i + 1 < m ? "," : "\n");
    printf("  max ARCBOUND/W^2 = %lld/%lld = %.8f   at w=", bestWsqNum, bestWsqDen,
           (double)bestWsqNum / (double)bestWsqDen);
    for (int i = 0; i < m; i++) printf("%d%s", bestWsqW[i], i + 1 < m ? "," : "\n");
    if (bigWbestA >= 0) {
        printf("  regime W>1/5: max ARCBOUND = %lld/%lld = %.8f  E=%lld q=%lld  at w=",
               bigWbestA, bigWbestQ * bigWbestQ, (double)bigWbestA / (double)(bigWbestQ * bigWbestQ),
               bigWbestE, bigWbestQ);
        for (int i = 0; i < m; i++) printf("%d%s", bigWbestW[i], i + 1 < m ? "," : "\n");
    } else printf("  regime W>1/5: no vector with ARCBOUND>0\n");
    return 0;
}
