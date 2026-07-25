// H2 family: weighted-blow-up search.
//
// For a triangle-free base H on h <= 24 vertices and integer weights n_i >= 0 with
// sum n_i = N, the blow-up G = H[n] is triangle-free on N vertices and
//     bip(G) = min_{S subset V(H)} sum_{ij in E(H), i,j on the same side of S} n_i n_j
// (exact identity: the cut value is affine in each part's split, so a maximum cut is
//  constant on parts; verified independently in h2_blowup_theory.py).
//
// This program reads graph6 bases on stdin and, for each, maximises
//     bip(H[n]) over integer n >= 0 with sum n = N
// by multi-restart steepest-ascent hill climbing with plateau tie-breaking,
// reporting 25*bip/N^2.  Anything > 1 is a counterexample to Erdos #23.
//
// Options:
//   -N <int>      total order N to optimise at (default 100); may be repeated
//   -r <int>      restarts per graph (default 8)
//   -maximal      keep only maximal triangle-free bases
//   -twinfree     keep only bases with no two vertices having equal neighbourhoods
//   -thr <double> only print graphs whose best 25*bip/N^2 >= thr (default 0.99)
//   -v            print the winning weight vector
//
// Exact integer arithmetic throughout (int64).
//
// Build: clang++ -O3 -march=native -std=c++17 -o h2_gmax.exe h2_gmax.cpp

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <iostream>
#include <random>
#include <algorithm>

typedef long long ll;

static int H;                     // base order
static int NE;                    // base edges
static int EU[600], EV[600];      // edge endpoints
static uint32_t ADJ[24];

// per-cut monochromatic edge lists
static std::vector<std::vector<int>> monoE;   // monoE[s] = edge indices monochromatic under cut s
static int NCUT;

static bool decode_g6(const std::string& line, int& n, uint32_t* adj) {
    if (line.empty()) return false;
    const char* p = line.c_str();
    n = (int)p[0] - 63;
    if (n < 1 || n > 24) return false;
    ++p;
    for (int i = 0; i < n; ++i) adj[i] = 0;
    int cur = 0, nbits = 0;
    for (int j = 1; j < n; ++j)
        for (int i = 0; i < j; ++i) {
            if (nbits == 0) { cur = (int)(*p++) - 63; nbits = 6; }
            int bit = (cur >> (nbits - 1)) & 1; --nbits;
            if (bit) { adj[i] |= 1u << j; adj[j] |= 1u << i; }
        }
    return true;
}

static bool triangle_free(int n, const uint32_t* adj) {
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j)
            if ((adj[i] >> j) & 1) if (adj[i] & adj[j]) return false;
    return true;
}

static bool maximal_tf(int n, const uint32_t* adj) {
    // adding any non-edge must create a triangle, i.e. every non-adjacent pair has
    // a common neighbour
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j)
            if (!((adj[i] >> j) & 1))
                if ((adj[i] & adj[j]) == 0) return false;
    return true;
}

static bool twin_free(int n, const uint32_t* adj) {
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j)
            if (adj[i] == adj[j]) return false;
    return true;
}

static void build_cuts(int n, const uint32_t* adj) {
    H = n;
    NE = 0;
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j)
            if ((adj[i] >> j) & 1) { EU[NE] = i; EV[NE] = j; ++NE; }
    NCUT = 1 << (n - 1);            // vertex 0 fixed outside S
    monoE.assign(NCUT, {});
    for (int half = 0; half < NCUT; ++half) {
        uint32_t S = ((uint32_t)half) << 1;
        std::vector<int>& L = monoE[half];
        for (int e = 0; e < NE; ++e)
            if (((S >> EU[e]) & 1) == ((S >> EV[e]) & 1)) L.push_back(e);
    }
}

// evaluate: returns (min, count at min) for weights w
struct Val { ll mn; int cnt; ll mn2; };

static inline Val evaluate(const ll* w) {
    Val v; v.mn = (ll)4e18; v.cnt = 0; v.mn2 = (ll)4e18;
    for (int s = 0; s < NCUT; ++s) {
        ll t = 0;
        for (int e : monoE[s]) t += w[EU[e]] * w[EV[e]];
        if (t < v.mn) { v.mn2 = v.mn; v.mn = t; v.cnt = 1; }
        else if (t == v.mn) ++v.cnt;
        else if (t < v.mn2) v.mn2 = t;
    }
    return v;
}

static inline bool better(const Val& a, const Val& b) {
    if (a.mn != b.mn) return a.mn > b.mn;
    if (a.cnt != b.cnt) return a.cnt < b.cnt;
    return a.mn2 > b.mn2;
}

int main(int argc, char** argv) {
    std::vector<ll> Ns;
    int restarts = 8;
    bool need_max = false, need_tf = false, verbose = false;
    double thr = 0.99;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "-N")) Ns.push_back(atoll(argv[++i]));
        else if (!strcmp(argv[i], "-r")) restarts = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-maximal")) need_max = true;
        else if (!strcmp(argv[i], "-twinfree")) need_tf = true;
        else if (!strcmp(argv[i], "-thr")) thr = atof(argv[++i]);
        else if (!strcmp(argv[i], "-v")) verbose = true;
    }
    if (Ns.empty()) Ns.push_back(100);

    std::mt19937_64 rng(0xC5C5C5ULL);
    std::string line;
    std::ios::sync_with_stdio(false);

    ll seen = 0, kept = 0;
    double globalbest = 0.0;
    std::string globalg6; ll globalN = 0; std::vector<ll> globalw;

    uint32_t adj[24];
    int n;
    ll w[24], bw[24];

    while (std::getline(std::cin, line)) {
        while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
        if (line.empty()) continue;
        if (!decode_g6(line, n, adj)) { fprintf(stderr, "bad g6: %s\n", line.c_str()); continue; }
        ++seen;
        if (!triangle_free(n, adj)) continue;
        if (need_max && !maximal_tf(n, adj)) continue;
        if (need_tf && !twin_free(n, adj)) continue;
        ++kept;
        build_cuts(n, adj);

        for (ll N : Ns) {
            Val best; best.mn = -1; best.cnt = 0; best.mn2 = -1;
            for (int r = 0; r < restarts; ++r) {
                // start: uniform (r==0) else random composition
                if (r == 0) {
                    for (int i = 0; i < n; ++i) w[i] = N / n;
                    for (int i = 0; i < N % n; ++i) w[i] += 1;
                } else {
                    for (int i = 0; i < n; ++i) w[i] = 0;
                    for (ll k = 0; k < N; ++k) w[rng() % n] += 1;
                }
                Val cur = evaluate(w);
                bool improved = true;
                while (improved) {
                    improved = false;
                    // steepest ascent over unit moves i -> j
                    int bi = -1, bj = -1; Val bv = cur;
                    for (int i = 0; i < n; ++i) {
                        if (w[i] == 0) continue;
                        for (int j = 0; j < n; ++j) {
                            if (i == j) continue;
                            w[i] -= 1; w[j] += 1;
                            Val v = evaluate(w);
                            if (better(v, bv)) { bv = v; bi = i; bj = j; }
                            w[i] += 1; w[j] -= 1;
                        }
                    }
                    if (bi >= 0) { w[bi] -= 1; w[bj] += 1; cur = bv; improved = true; }
                }
                if (cur.mn > best.mn) {
                    best = cur;
                    for (int i = 0; i < n; ++i) bw[i] = w[i];
                }
            }
            double ratio = 25.0 * (double)best.mn / ((double)N * (double)N);
            if (ratio > globalbest) {
                globalbest = ratio; globalg6 = line; globalN = N;
                globalw.assign(bw, bw + n);
            }
            if (ratio >= thr) {
                printf("HIT g6=%s h=%d N=%lld bip=%lld 25bip/N2=%.6f", line.c_str(), n, N, best.mn, ratio);
                if (verbose) {
                    printf(" w=[");
                    for (int i = 0; i < n; ++i) printf("%s%lld", i ? "," : "", bw[i]);
                    printf("]");
                }
                if (25 * best.mn > N * N) printf("  *** VIOLATION 25*bip=%lld > N^2=%lld ***", 25 * best.mn, N * N);
                printf("\n");
                fflush(stdout);
            }
        }
    }
    printf("SUMMARY seen=%lld kept=%lld best25bipN2=%.8f at g6=%s N=%lld w=[", seen, kept, globalbest, globalg6.c_str(), globalN);
    for (size_t i = 0; i < globalw.size(); ++i) printf("%s%lld", i ? "," : "", globalw[i]);
    printf("]\n");
    return 0;
}
