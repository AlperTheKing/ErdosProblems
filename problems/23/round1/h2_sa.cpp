// H2: simulated annealing over triangle-free BASES with co-evolving blow-up weights.
//
// State = (triangle-free graph H on h vertices, integer weights w with sum w = N).
// Objective = bip(H[w]) = min_{S subset V(H)} sum_{ij in E(H) monochromatic} w_i w_j,
// evaluated EXACTLY by enumerating all 2^(h-1) cuts of the base (integer arithmetic).
// Reported score = 25*bip/N^2; anything > 1 is a counterexample to Erdos #23.
//
// This searches the same space as a direct search over N-vertex graphs, but with only
// h << N free vertices, so it reaches orders N that a direct search cannot touch.
// bip is monotone under adding edges, so the graph moves always re-saturate H to a
// MAXIMAL triangle-free graph.
//
// Build: clang++ -O3 -march=native -std=c++17 -o h2_sa.exe h2_sa.cpp
// Usage: h2_sa.exe -h 16 -N 100 -iters 200000 -seed 1 [-start <g6>]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <random>
#include <algorithm>
#include <cmath>

typedef long long ll;
int CLIMB = 12;
static const int MAXH = 22;

static int h, NCUT;
static ll N;
static uint32_t adj[MAXH];
static std::vector<uint32_t> sideBits;      // sideBits[s]
static std::vector<uint32_t> monoAdj;       // monoAdj[s*h+i]
static std::vector<ll> q;                   // q[s]
static std::vector<ll> W;                   // W[s*h+i]
static ll w[MAXH];
static std::mt19937_64 rng;

static void buildSides() {
    NCUT = 1 << (h - 1);
    sideBits.assign(NCUT, 0);
    for (int s = 0; s < NCUT; ++s) sideBits[s] = ((uint32_t)s) << 1;
    monoAdj.assign((size_t)NCUT * h, 0);
    q.assign(NCUT, 0);
    W.assign((size_t)NCUT * h, 0);
}

static void refreshMono() {
    uint32_t full = (1u << h) - 1;
    for (int s = 0; s < NCUT; ++s) {
        uint32_t sd = sideBits[s];
        uint32_t nsd = (~sd) & full;
        for (int i = 0; i < h; ++i)
            monoAdj[(size_t)s * h + i] = adj[i] & (((sd >> i) & 1) ? sd : nsd);
    }
}

static void refreshQ() {
    for (int s = 0; s < NCUT; ++s) {
        ll t = 0;
        for (int i = 0; i < h; ++i) {
            uint32_t m = monoAdj[(size_t)s * h + i];
            ll acc = 0;
            while (m) { int j = __builtin_ctz(m); m &= m - 1; acc += w[j]; }
            W[(size_t)s * h + i] = acc;
            t += w[i] * acc;
        }
        q[s] = t / 2;
    }
}

struct Val { ll mn; int cnt; ll mn2; };
static inline bool better(const Val& a, const Val& b) {
    if (a.mn != b.mn) return a.mn > b.mn;
    if (a.cnt != b.cnt) return a.cnt < b.cnt;
    return a.mn2 > b.mn2;
}
static Val curVal;

static Val recompute() {
    Val v; v.mn = (ll)4e18; v.cnt = 0; v.mn2 = (ll)4e18;
    for (int s = 0; s < NCUT; ++s) {
        ll t = q[s];
        if (t < v.mn) { v.mn2 = v.mn; v.mn = t; v.cnt = 1; }
        else if (t == v.mn) ++v.cnt;
        else if (t < v.mn2) v.mn2 = t;
    }
    return v;
}

static Val trial(int i, int j) {
    Val v; v.mn = (ll)4e18; v.cnt = 0; v.mn2 = (ll)4e18;
    bool ij = (adj[i] >> j) & 1;
    for (int s = 0; s < NCUT; ++s) {
        ll t = q[s] + W[(size_t)s * h + j] - W[(size_t)s * h + i];
        if (ij) { uint32_t sd = sideBits[s]; if ((((sd >> i) ^ (sd >> j)) & 1u) == 0) t -= 1; }
        if (t < v.mn) { v.mn2 = v.mn; v.mn = t; v.cnt = 1; }
        else if (t == v.mn) ++v.cnt;
        else if (t < v.mn2) v.mn2 = t;
    }
    return v;
}

static void commit(int i, int j) {
    bool ij = (adj[i] >> j) & 1;
    for (int s = 0; s < NCUT; ++s) {
        ll* Wp = &W[(size_t)s * h];
        ll t = q[s] + Wp[j] - Wp[i];
        if (ij) { uint32_t sd = sideBits[s]; if ((((sd >> i) ^ (sd >> j)) & 1u) == 0) t -= 1; }
        q[s] = t;
        uint32_t m = monoAdj[(size_t)s * h + i];
        while (m) { int k = __builtin_ctz(m); m &= m - 1; Wp[k] -= 1; }
        m = monoAdj[(size_t)s * h + j];
        while (m) { int k = __builtin_ctz(m); m &= m - 1; Wp[k] += 1; }
    }
    w[i] -= 1; w[j] += 1;
    curVal = recompute();
}

static void climb(int maxsteps) {
    for (int st = 0; st < maxsteps; ++st) {
        int bi = -1, bj = -1; Val bv = curVal;
        for (int i = 0; i < h; ++i) {
            if (w[i] == 0) continue;
            for (int j = 0; j < h; ++j) {
                if (i == j) continue;
                Val v = trial(i, j);
                if (better(v, bv)) { bv = v; bi = i; bj = j; }
            }
        }
        if (bi < 0) return;
        commit(bi, bj);
    }
}

// ---- graph moves ----
static bool triangleFreeAdd(int i, int j) { return (adj[i] & adj[j]) == 0; }

static void saturate() {
    // add random non-edges while triangle-free (result is maximal triangle-free)
    int pairs[MAXH * MAXH][2]; int np = 0;
    for (int i = 0; i < h; ++i) for (int j = i + 1; j < h; ++j) { pairs[np][0] = i; pairs[np][1] = j; ++np; }
    for (int k = np - 1; k > 0; --k) { int r = rng() % (k + 1); std::swap(pairs[k], pairs[r]); }
    bool changed = true;
    while (changed) {
        changed = false;
        for (int k = 0; k < np; ++k) {
            int i = pairs[k][0], j = pairs[k][1];
            if ((adj[i] >> j) & 1) continue;
            if (triangleFreeAdd(i, j)) { adj[i] |= 1u << j; adj[j] |= 1u << i; changed = true; }
        }
    }
}

static void randomStart() {
    for (int i = 0; i < h; ++i) adj[i] = 0;
    saturate();
}

int main(int argc, char** argv) {
    h = 16; N = 100; ll iters = 200000; unsigned long long seed = 1;
    const char* startg6 = 0; extern int CLIMB;
    double T0 = 0.02, T1 = 0.0008;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "-h")) h = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-N")) N = atoll(argv[++i]);
        else if (!strcmp(argv[i], "-iters")) iters = atoll(argv[++i]);
        else if (!strcmp(argv[i], "-seed")) seed = strtoull(argv[++i], 0, 0);
        else if (!strcmp(argv[i], "-start")) startg6 = argv[++i];
        else if (!strcmp(argv[i], "-climb")) CLIMB = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-T0")) T0 = atof(argv[++i]);
        else if (!strcmp(argv[i], "-T1")) T1 = atof(argv[++i]);
    }
    if (h > MAXH) { fprintf(stderr, "h too large\n"); return 2; }
    rng.seed(seed);
    buildSides();

    if (startg6) {
        const char* p = startg6; int n = (int)p[0] - 63; ++p;
        if (n != h) { fprintf(stderr, "start order mismatch\n"); return 2; }
        for (int i = 0; i < h; ++i) adj[i] = 0;
        int cur = 0, nb = 0;
        for (int j = 1; j < h; ++j) for (int i = 0; i < j; ++i) {
            if (nb == 0) { cur = (int)(*p++) - 63; nb = 6; }
            int bit = (cur >> (nb - 1)) & 1; --nb;
            if (bit) { adj[i] |= 1u << j; adj[j] |= 1u << i; }
        }
    } else randomStart();

    for (int i = 0; i < h; ++i) w[i] = N / h;
    for (int i = 0; i < N % h; ++i) w[i] += 1;
    refreshMono(); refreshQ(); curVal = recompute();
    climb(400);

    ll best = curVal.mn; uint32_t badj[MAXH]; ll bw[MAXH];
    for (int i = 0; i < h; ++i) { badj[i] = adj[i]; bw[i] = w[i]; }

    uint32_t sadj[MAXH]; ll sw[MAXH];
    for (ll it = 0; it < iters; ++it) {
        double frac = (double)it / (double)iters;
        double T = T0 * std::pow(T1 / T0, frac);
        for (int i = 0; i < h; ++i) { sadj[i] = adj[i]; sw[i] = w[i]; }
        ll before = curVal.mn;
        // graph move: delete 1..3 random edges then re-saturate
        int ndel = 1 + (int)(rng() % 3);
        for (int d = 0; d < ndel; ++d) {
            int tries = 0;
            while (tries++ < 50) {
                int i = rng() % h, j = rng() % h;
                if (i == j) continue;
                if (!((adj[i] >> j) & 1)) continue;
                adj[i] &= ~(1u << j); adj[j] &= ~(1u << i); break;
            }
        }
        saturate();
        refreshMono(); refreshQ(); curVal = recompute();
        climb(CLIMB);
        ll after = curVal.mn;
        double d = 25.0 * (double)(after - before) / ((double)N * N);
        bool accept = (after >= before) ||
                      (std::exp(d / T) > (double)(rng() % 1000000) / 1e6);
        if (!accept) {
            for (int i = 0; i < h; ++i) { adj[i] = sadj[i]; w[i] = sw[i]; }
            refreshMono(); refreshQ(); curVal = recompute();
        } else if (curVal.mn > best) {
            best = curVal.mn;
            for (int i = 0; i < h; ++i) { badj[i] = adj[i]; bw[i] = w[i]; }
            printf("NEW h=%d N=%lld bip=%lld 25bip/N2=%.8f w=[", h, N, best,
                   25.0 * (double)best / ((double)N * N));
            for (int i = 0; i < h; ++i) printf("%s%lld", i ? "," : "", bw[i]);
            printf("] g6=");
            { // emit graph6
                std::string bits;
                for (int j = 1; j < h; ++j) for (int i = 0; i < j; ++i)
                    bits += ((badj[i] >> j) & 1) ? '1' : '0';
                while (bits.size() % 6) bits += '0';
                std::string g; g += (char)(h + 63);
                for (size_t k = 0; k < bits.size(); k += 6) {
                    int v = 0; for (int t = 0; t < 6; ++t) v = (v << 1) | (bits[k + t] - '0');
                    g += (char)(v + 63);
                }
                printf("%s", g.c_str());
            }
            if (25 * best > N * N) printf("  *** VIOLATION ***");
            printf("\n"); fflush(stdout);
        }
    }
    printf("SA_DONE h=%d N=%lld best=%lld 25bip/N2=%.8f\n", h, N, best,
           25.0 * (double)best / ((double)N * N));
    return 0;
}
