// H2 family: weighted-blow-up optimiser (fast, incremental).
//
// Exact identity used throughout (verified in h2_blowup_theory.py):
//   for triangle-free base H on h vertices and integer weights n_i >= 0,
//   the blow-up H[n] is triangle-free on N = sum n_i vertices and
//       bip(H[n]) = min_{S subset V(H)} sum_{ij in E(H) monochromatic under S} n_i n_j.
//
// We maximise that quantity over integer weight vectors with a fixed total N,
// by coarse-to-fine steepest-ascent hill climbing with random restarts.
// 25*bip/N^2 > 1 would be a counterexample to Erdos #23.
//
// Build: clang++ -O3 -march=native -std=c++17 -o h2_opt.exe h2_opt.cpp
// Usage: h2_opt.exe [-Nmax 960] [-Nfix 24] [-r 16] [-thr 0.99] [-v] < bases.g6

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
static const int MAXH = 20;

struct Base {
    int h, ne;
    uint32_t adj[MAXH];
    int eu[MAXH * MAXH / 2], ev[MAXH * MAXH / 2];
    int ncut;
    std::vector<uint32_t> side;     // side[s]: bit i = side of vertex i (vertex 0 always 0)
    std::vector<uint32_t> monoAdj;  // monoAdj[s*h+i] = bitmask of mono-neighbours of i under s
};

static bool decode_g6(const std::string& line, Base& B) {
    if (line.empty()) return false;
    const char* p = line.c_str();
    int n = (int)p[0] - 63;
    if (n < 1 || n > MAXH) return false;
    ++p;
    B.h = n;
    for (int i = 0; i < n; ++i) B.adj[i] = 0;
    int cur = 0, nbits = 0;
    for (int j = 1; j < n; ++j)
        for (int i = 0; i < j; ++i) {
            if (nbits == 0) { cur = (int)(*p++) - 63; nbits = 6; }
            int bit = (cur >> (nbits - 1)) & 1; --nbits;
            if (bit) { B.adj[i] |= 1u << j; B.adj[j] |= 1u << i; }
        }
    B.ne = 0;
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j)
            if ((B.adj[i] >> j) & 1) { B.eu[B.ne] = i; B.ev[B.ne] = j; ++B.ne; }
    return true;
}

static bool triangle_free(const Base& B) {
    for (int i = 0; i < B.h; ++i)
        for (int j = i + 1; j < B.h; ++j)
            if ((B.adj[i] >> j) & 1) if (B.adj[i] & B.adj[j]) return false;
    return true;
}

static void build(Base& B) {
    int h = B.h;
    B.ncut = 1 << (h - 1);
    B.side.assign(B.ncut, 0);
    B.monoAdj.assign((size_t)B.ncut * h, 0);
    for (int s = 0; s < B.ncut; ++s) {
        uint32_t sd = ((uint32_t)s) << 1;
        B.side[s] = sd;
        for (int i = 0; i < h; ++i) {
            uint32_t same = ((sd >> i) & 1) ? sd : (~sd) & ((1u << h) - 1);
            B.monoAdj[(size_t)s * h + i] = B.adj[i] & same;
        }
    }
}

struct Val { ll mn; int cnt; ll mn2; };
static inline bool better(const Val& a, const Val& b) {
    if (a.mn != b.mn) return a.mn > b.mn;
    if (a.cnt != b.cnt) return a.cnt < b.cnt;
    return a.mn2 > b.mn2;
}

struct State {
    const Base* B;
    std::vector<ll> q;      // q[s]
    std::vector<ll> W;      // W[s*h+i] = sum of weights of mono-neighbours of i under s
    ll w[MAXH];
    Val val;

    void init(const Base& b, const ll* wt) {
        B = &b;
        int h = B->h, nc = B->ncut;
        q.assign(nc, 0);
        W.assign((size_t)nc * h, 0);
        for (int i = 0; i < h; ++i) w[i] = wt[i];
        for (int s = 0; s < nc; ++s) {
            ll t = 0;
            for (int i = 0; i < h; ++i) {
                uint32_t m = B->monoAdj[(size_t)s * h + i];
                ll acc = 0;
                uint32_t mm = m;
                while (mm) { int j = __builtin_ctz(mm); mm &= mm - 1; acc += w[j]; }
                W[(size_t)s * h + i] = acc;
                t += w[i] * acc;
            }
            q[s] = t / 2;
        }
        val = recompute();
    }
    Val recompute() const {
        Val v; v.mn = (ll)4e18; v.cnt = 0; v.mn2 = (ll)4e18;
        for (int s = 0; s < B->ncut; ++s) {
            ll t = q[s];
            if (t < v.mn) { v.mn2 = v.mn; v.mn = t; v.cnt = 1; }
            else if (t == v.mn) ++v.cnt;
            else if (t < v.mn2) v.mn2 = t;
        }
        return v;
    }
    // value after moving d units from i to j (no commit)
    Val trial(int i, int j, ll d) const {
        int h = B->h, nc = B->ncut;
        Val v; v.mn = (ll)4e18; v.cnt = 0; v.mn2 = (ll)4e18;
        bool ij = (B->adj[i] >> j) & 1;
        const ll* Wp = W.data();
        ll dd = d * d;
        for (int s = 0; s < nc; ++s) {
            ll t = q[s] + d * (Wp[(size_t)s * h + j] - Wp[(size_t)s * h + i]);
            if (ij) {
                uint32_t sd = B->side[s];
                if ((((sd >> i) ^ (sd >> j)) & 1u) == 0) t -= dd;
            }
            if (t < v.mn) { v.mn2 = v.mn; v.mn = t; v.cnt = 1; }
            else if (t == v.mn) ++v.cnt;
            else if (t < v.mn2) v.mn2 = t;
        }
        return v;
    }
    void commit(int i, int j, ll d) {
        int h = B->h, nc = B->ncut;
        bool ij = (B->adj[i] >> j) & 1;
        ll dd = d * d;
        for (int s = 0; s < nc; ++s) {
            ll* Wp = &W[(size_t)s * h];
            ll t = q[s] + d * (Wp[j] - Wp[i]);
            if (ij) {
                uint32_t sd = B->side[s];
                if ((((sd >> i) ^ (sd >> j)) & 1u) == 0) t -= dd;
            }
            q[s] = t;
            uint32_t mi = B->monoAdj[(size_t)s * h + i];
            uint32_t mj = B->monoAdj[(size_t)s * h + j];
            uint32_t mm = mi;
            while (mm) { int k = __builtin_ctz(mm); mm &= mm - 1; Wp[k] -= d; }
            mm = mj;
            while (mm) { int k = __builtin_ctz(mm); mm &= mm - 1; Wp[k] += d; }
        }
        w[i] -= d; w[j] += d;
        val = recompute();
    }
};

// Steepest ascent over MULTI-UNIT transfers i -> j of size d in {1,2,4,...,w_i} u {w_i}.
// Single-unit moves alone cannot drive a weight to zero (every intermediate state is
// worse), which made the previous version miss the C5 collapse on e.g. the Petersen graph.
static void climb(State& st) {
    int h = st.B->h;
    for (;;) {
        int bi = -1, bj = -1; ll bd = 0; Val bv = st.val;
        for (int i = 0; i < h; ++i) {
            if (st.w[i] == 0) continue;
            for (int j = 0; j < h; ++j) {
                if (i == j) continue;
                for (ll d = 1;; d = (d * 2 <= st.w[i] ? d * 2 : st.w[i])) {
                    Val v = st.trial(i, j, d);
                    if (better(v, bv)) { bv = v; bi = i; bj = j; bd = d; }
                    if (d >= st.w[i]) break;
                }
            }
        }
        if (bi < 0) break;
        st.commit(bi, bj, bd);
    }
}

int main(int argc, char** argv) {
    ll Nmax = 960, Nfix = 0, N0 = 0;
    int restarts = 16;
    double thr = 0.99;
    bool verbose = false, plain = false;
    for (int i = 1; i < argc; ++i) if (!strcmp(argv[i], "-plain")) plain = true;
    unsigned long long seed = 0xC5C5C5ULL;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "-Nmax")) Nmax = atoll(argv[++i]);
        else if (!strcmp(argv[i], "-Nfix")) Nfix = atoll(argv[++i]);
        else if (!strcmp(argv[i], "-N0")) N0 = atoll(argv[++i]);
        else if (!strcmp(argv[i], "-r")) restarts = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-thr")) thr = atof(argv[++i]);
        else if (!strcmp(argv[i], "-seed")) seed = strtoull(argv[++i], 0, 0);
        else if (!strcmp(argv[i], "-v")) verbose = true;
    }
    std::mt19937_64 rng(seed);
    std::ios::sync_with_stdio(false);
    std::string line;
    double gbest = 0; std::string gg6; ll gN = 0; std::vector<ll> gw;
    ll count = 0;

    while (std::getline(std::cin, line)) {
        while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
        if (line.empty()) continue;
        Base B;
        if (!decode_g6(line, B)) { fprintf(stderr, "bad g6 %s\n", line.c_str()); continue; }
        if (!triangle_free(B)) continue;
        build(B);
        ++count;
        int h = B.h;
        ll bestbip = -1, bestN = 0; std::vector<ll> bestw(h, 0);
        double bestratio = 0;

        ll wtmp[MAXH];
        if (plain) {
            for (int i = 0; i < h; ++i) wtmp[i] = 1;
            State st; st.init(B, wtmp);
            ll N = h;
            printf("PLAIN g6=%s h=%d m=%d bip=%lld 25bip/N2=%.8f\n",
                   line.c_str(), h, B.ne, st.val.mn, 25.0 * (double)st.val.mn / ((double)N * N));
            fflush(stdout);
            continue;
        }
        for (int r = 0; r < restarts; ++r) {
            ll N = Nfix ? Nfix : (N0 ? N0 : (ll)h * 2);
            if (Nfix) {
                if (r == 0) { for (int i = 0; i < h; ++i) wtmp[i] = N / h;
                              for (int i = 0; i < N % h; ++i) wtmp[i] += 1; }
                else { // random restart on a random SUPPORT of size 5..h
                       int idx[MAXH]; for (int i = 0; i < h; ++i) idx[i] = i;
                       for (int k = h - 1; k > 0; --k) { int t = rng() % (k + 1); std::swap(idx[k], idx[t]); }
                       int sup = 5 + (int)(rng() % (h - 4 > 0 ? h - 4 : 1));
                       if (sup > h) sup = h;
                       for (int i = 0; i < h; ++i) wtmp[i] = 0;
                       for (ll k = 0; k < N; ++k) wtmp[idx[rng() % sup]] += 1; }
                State st; st.init(B, wtmp); climb(st);
                double ratio = 25.0 * (double)st.val.mn / ((double)N * (double)N);
                if (ratio > bestratio) { bestratio = ratio; bestbip = st.val.mn; bestN = N;
                                          for (int i = 0; i < h; ++i) bestw[i] = st.w[i]; }
            } else {
                if (r == 0) { for (int i = 0; i < h; ++i) wtmp[i] = N / h;
                              for (int i = 0; i < N % h; ++i) wtmp[i] += 1; }
                else { // random restart on a random SUPPORT of size 5..h
                       int idx[MAXH]; for (int i = 0; i < h; ++i) idx[i] = i;
                       for (int k = h - 1; k > 0; --k) { int t = rng() % (k + 1); std::swap(idx[k], idx[t]); }
                       int sup = 5 + (int)(rng() % (h - 4 > 0 ? h - 4 : 1));
                       if (sup > h) sup = h;
                       for (int i = 0; i < h; ++i) wtmp[i] = 0;
                       for (ll k = 0; k < N; ++k) wtmp[idx[rng() % sup]] += 1; }
                State st; st.init(B, wtmp); climb(st);
                while (N < Nmax) {
                    N *= 2;
                    for (int i = 0; i < h; ++i) wtmp[i] = st.w[i] * 2;
                    st.init(B, wtmp); climb(st);
                    double ratio = 25.0 * (double)st.val.mn / ((double)N * (double)N);
                    if (ratio > bestratio) { bestratio = ratio; bestbip = st.val.mn; bestN = N;
                                              for (int i = 0; i < h; ++i) bestw[i] = st.w[i]; }
                }
            }
        }
        if (bestratio > gbest) { gbest = bestratio; gg6 = line; gN = bestN; gw = bestw; }
        if (bestratio >= thr) {
            printf("HIT g6=%s h=%d N=%lld bip=%lld 25bip/N2=%.8f", line.c_str(), h, bestN, bestbip, bestratio);
            if (verbose) { printf(" w=["); for (int i = 0; i < h; ++i) printf("%s%lld", i ? "," : "", bestw[i]); printf("]"); }
            if (25 * bestbip > bestN * bestN) printf("  *** VIOLATION ***");
            printf("\n"); fflush(stdout);
        }
    }
    printf("SUMMARY bases=%lld best=%.8f g6=%s N=%lld w=[", count, gbest, gg6.c_str(), gN);
    for (size_t i = 0; i < gw.size(); ++i) printf("%s%lld", i ? "," : "", gw[i]);
    printf("]\n");
    return 0;
}
