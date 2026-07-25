// h6_gscan.cpp -- H6 family, Erdos #23.
//
// THEORY.  For a triangle-free template G on n vertices and integer class sizes
// t_1..t_n, the blow-up G[t] is triangle-free on N = sum t_i vertices and
//
//     bip(G[t]) = min_{cuts (S,S^c) of G}  sum_{ij in E(G), i,j same side} t_i t_j.
//
// (The count of same-side edges of a blow-up depends only on how many copies of
// each class lie on each side; the resulting function is multilinear in the
// fractions alpha_i = s_i/t_i, hence minimised at a 0/1 vertex, i.e. at a cut of G.)
//
// Therefore, with x = t/N in the simplex,
//
//     bip(G[t]) / N^2 = min_S  sum_{ij same side} x_i x_j =: F_G(x),
//     g(G) := max_{x in simplex} F_G(x),
//
// and sup_N a(N)/N^2 = sup over all triangle-free templates G of g(G).
// The Erdos conjecture is exactly:  g(G) <= 1/25 for every triangle-free G.
// C5 with uniform x gives g(C5) = 1/25.
//
// This program scans templates and maximises F_G by exponentiated-gradient
// ascent on a soft-min surrogate (multi-restart), then reports the EXACT value
// min_S Q_S(x) at the returned point (a rigorous lower bound on g(G)).
//
// Modes:
//   scan   : read graph6 on stdin, print worst-case / top templates
//   polish : read graph6 on stdin, integer-weight hill climb at given orders N,
//            exact int64 arithmetic, flags 25*bip > N*N.
//
// Build: clang++ -O3 -march=native -std=c++17 h6_gscan.cpp -o h6_gscan.exe

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <cstdint>
#include <climits>
#include <array>
#include <string>
#include <vector>
#include <algorithm>
#include <thread>
#include <mutex>
#include <random>
#include <iostream>

using namespace std;

struct Graph {
    int n = 0;
    vector<pair<int,int>> E;
    string g6;
};

static bool parse_g6(const string& s, Graph& G) {
    if (s.empty()) return false;
    size_t p = 0;
    int n = (int)(unsigned char)s[p++] - 63;
    if (n < 0 || n > 20) return false;           // this tool: n <= 20
    G.n = n; G.E.clear(); G.g6 = s;
    int need = n * (n - 1) / 2;
    int bit = 0;
    int cur = 0, have = 0;
    for (int j = 1; j < n; j++) {
        for (int i = 0; i < j; i++) {
            if (have == 0) {
                if (p >= s.size()) return false;
                cur = (int)(unsigned char)s[p++] - 63;
                have = 6;
            }
            int b = (cur >> (have - 1)) & 1;
            have--;
            if (b) G.E.push_back({i, j});
            bit++;
        }
    }
    return bit == need;
}

static bool triangle_free(const Graph& G) {
    vector<uint32_t> adj(G.n, 0);
    for (auto& e : G.E) { adj[e.first] |= 1u << e.second; adj[e.second] |= 1u << e.first; }
    for (auto& e : G.E) if (adj[e.first] & adj[e.second]) return false;
    return true;
}

// A vertex v is DOMINATED if N(v) subset of N(u) for some u != v.  Then v -> u is a
// retraction G -> G-v, and g is monotone under homomorphism (if G -> H then
// g(G) <= g(H)), so such a template is subsumed by a smaller one.  Skipping these
// leaves exactly the hom-irreducible ("point-determining") templates.
static bool has_dominated_vertex(const Graph& G) {
    int n = G.n;
    vector<uint32_t> adj(n, 0);
    for (auto& e : G.E) { adj[e.first] |= 1u << e.second; adj[e.second] |= 1u << e.first; }
    for (int v = 0; v < n; v++)
        for (int u = 0; u < n; u++)
            if (u != v && (adj[v] & ~adj[u]) == 0) return true;
    return false;
}

static bool bipartite(const Graph& G) {
    vector<int> col(G.n, -1);
    vector<vector<int>> ad(G.n);
    for (auto& e : G.E) { ad[e.first].push_back(e.second); ad[e.second].push_back(e.first); }
    for (int s = 0; s < G.n; s++) {
        if (col[s] != -1) continue;
        col[s] = 0; vector<int> st{s};
        while (!st.empty()) {
            int v = st.back(); st.pop_back();
            for (int u : ad[v]) {
                if (col[u] == -1) { col[u] = col[v] ^ 1; st.push_back(u); }
                else if (col[u] == col[v]) return false;
            }
        }
    }
    return true;
}

// ---- per-template cut structure ----------------------------------------
struct Cuts {
    int n, m, ncuts;
    vector<int> off;   // ncuts+1
    vector<int> eu, ev; // flattened same-side endpoint pairs
};

// Only the INCLUSION-MINIMAL same-side edge sets matter: if E_S subset of E_T then
// Q_S(x) <= Q_T(x) for every x >= 0, so cut T can never attain the minimum.
// This typically collapses 2^(n-1) cuts to a few dozen (e.g. C5: 16 -> 5).
static void build_cuts(const Graph& G, Cuts& C) {
    C.n = G.n; C.m = (int)G.E.size();
    int ncuts = 1 << (G.n - 1);
    vector<uint64_t> masks;
    if (C.m <= 64) {
        masks.reserve(ncuts);
        for (int S = 0; S < ncuts; S++) {
            int mask = S << 1;             // vertex 0 always on side 0
            uint64_t bm = 0;
            for (int k = 0; k < C.m; k++) {
                int a = (mask >> G.E[k].first) & 1, b = (mask >> G.E[k].second) & 1;
                if (a == b) bm |= 1ULL << k;
            }
            masks.push_back(bm);
        }
        sort(masks.begin(), masks.end());
        masks.erase(unique(masks.begin(), masks.end()), masks.end());
        // keep inclusion-minimal masks (ascending popcount, reject supersets)
        stable_sort(masks.begin(), masks.end(),
                    [](uint64_t a, uint64_t b){ return __builtin_popcountll(a) < __builtin_popcountll(b); });
        vector<uint64_t> keep;
        for (uint64_t bm : masks) {
            bool red = false;
            for (uint64_t k : keep) if ((k & ~bm) == 0) { red = true; break; }
            if (!red) keep.push_back(bm);
        }
        masks.swap(keep);
    } else {                                // m > 64: no bitmask pruning, use all cuts
        C.ncuts = ncuts;
        C.off.assign(ncuts + 1, 0);
        C.eu.clear(); C.ev.clear();
        for (int S = 0; S < ncuts; S++) {
            int mask = S << 1;
            C.off[S] = (int)C.eu.size();
            for (auto& e : G.E) {
                int a = (mask >> e.first) & 1, b = (mask >> e.second) & 1;
                if (a == b) { C.eu.push_back(e.first); C.ev.push_back(e.second); }
            }
        }
        C.off[ncuts] = (int)C.eu.size();
        return;
    }
    C.ncuts = (int)masks.size();
    C.off.assign(C.ncuts + 1, 0);
    C.eu.clear(); C.ev.clear();
    for (int i = 0; i < C.ncuts; i++) {
        C.off[i] = (int)C.eu.size();
        uint64_t bm = masks[i];
        while (bm) {
            int k = __builtin_ctzll(bm); bm &= bm - 1;
            C.eu.push_back(G.E[k].first); C.ev.push_back(G.E[k].second);
        }
    }
    C.off[C.ncuts] = (int)C.eu.size();
}

// exact objective F(x) = min_S sum_{same side} x_i x_j  (double)
static double Fmin(const Cuts& C, const double* x) {
    double best = 1e300;
    for (int S = 0; S < C.ncuts; S++) {
        double q = 0.0;
        for (int k = C.off[S]; k < C.off[S + 1]; k++) q += x[C.eu[k]] * x[C.ev[k]];
        if (q < best) best = q;
        if (best == 0.0) break;
    }
    return best;
}

// Every triangle-free graph containing an INDUCED C5 has g(G) >= g(C5) = 1/25:
// put weight 1/5 on each C5 vertex; only the 5 C5 edges lie inside the support, and
// every cut of G restricts to a cut of C5, so F = min_i x_i x_{i+1} = 1/25.
// So 1/25 is a huge plateau; the real question is whether it can be beaten LOCALLY.
// We therefore seed the ascent at each induced C5 (up to a cap).
static vector<array<int,5>> induced_C5s(const Graph& G, int cap) {
    int n = G.n;
    vector<uint32_t> adj(n, 0);
    for (auto& e : G.E) { adj[e.first] |= 1u << e.second; adj[e.second] |= 1u << e.first; }
    vector<array<int,5>> out;
    for (int a = 0; a < n && (int)out.size() < cap; a++)
    for (int b = a+1; b < n && (int)out.size() < cap; b++)
    for (int c = b+1; c < n && (int)out.size() < cap; c++)
    for (int d = c+1; d < n && (int)out.size() < cap; d++)
    for (int e = d+1; e < n && (int)out.size() < cap; e++) {
        int v[5] = {a,b,c,d,e};
        uint32_t S = (1u<<a)|(1u<<b)|(1u<<c)|(1u<<d)|(1u<<e);
        int deg[5], tot = 0; bool ok = true;
        for (int i = 0; i < 5; i++) { deg[i] = __builtin_popcount(adj[v[i]] & S); tot += deg[i];
                                     if (deg[i] != 2) { ok = false; break; } }
        if (!ok || tot != 10) continue;
        // degrees all 2 and 5 edges => disjoint cycles covering 5 vertices => a single C5
        // order them along the cycle
        array<int,5> cyc; cyc[0] = v[0];
        int prev = -1, cur = v[0];
        for (int i = 1; i < 5; i++) {
            uint32_t nb = adj[cur] & S;
            int nx = -1;
            for (int j = 0; j < 5; j++) if ((nb >> v[j]) & 1) { if (v[j] != prev) { nx = v[j]; break; } }
            if (nx < 0) { ok = false; break; }
            prev = cur; cur = nx; cyc[i] = cur;
        }
        if (ok) out.push_back(cyc);
    }
    return out;
}

// exponentiated-gradient ascent on soft-min surrogate
static double optimize(const Cuts& C, double* xbest, int restarts, int iters, uint64_t seed,
                       const vector<array<int,5>>* seeds = nullptr) {
    int n = C.n;
    vector<double> x(n), q(C.ncuts), w(C.ncuts), gr(n);
    mt19937_64 rng(seed);
    double gbest = -1.0;
    for (int i = 0; i < n; i++) xbest[i] = 1.0 / n;
    for (int r = 0; r < restarts; r++) {
        int nseed = seeds ? (int)seeds->size() : 0;
        if (r < nseed) {                       // seed on an induced C5 (the 1/25 plateau)
            double s = 0;
            for (int i = 0; i < n; i++) { x[i] = 1e-4 * ((rng() % 1000) / 1000.0 + 0.5); s += x[i]; }
            for (int k = 0; k < 5; k++) { x[(*seeds)[r][k]] += 0.2; s += 0.2; }
            for (int i = 0; i < n; i++) x[i] /= s;
        }
        else if (r == nseed) { for (int i = 0; i < n; i++) x[i] = 1.0 / n; }
        else {
            double s = 0;
            for (int i = 0; i < n; i++) { x[i] = -log((rng() % 1000000 + 1) / 1000001.0); s += x[i]; }
            for (int i = 0; i < n; i++) x[i] /= s;
        }
        for (int it = 0; it < iters; it++) {
            double frac = (double)it / iters;
            // seeded restarts start ON the 1/25 plateau: use a gentle local schedule so
            // the ascent probes for a genuine local improvement instead of jumping away
            double tau0 = (r < nseed) ? 2e-3 : 3e-2;
            double eta0 = (r < nseed) ? 0.3  : 3.0;
            double tau = tau0 * pow(1e-4, frac);
            double eta = eta0 * pow(3e-5, frac);

            double mn = 1e300;
            for (int S = 0; S < C.ncuts; S++) {
                double v = 0.0;
                for (int k = C.off[S]; k < C.off[S + 1]; k++) v += x[C.eu[k]] * x[C.ev[k]];
                q[S] = v; if (v < mn) mn = v;
            }
            // mn == F(x) exactly: track the best iterate seen (free)
            if (mn > gbest) { gbest = mn; for (int i = 0; i < n; i++) xbest[i] = x[i]; }
            double Z = 0.0, cutoff = 30.0 * tau;   // exp() dominates; skip negligible cuts
            for (int S = 0; S < C.ncuts; S++) {
                double d = q[S] - mn;
                w[S] = (d > cutoff) ? 0.0 : exp(-d / tau);
                Z += w[S];
            }
            for (int i = 0; i < n; i++) gr[i] = 0.0;
            for (int S = 0; S < C.ncuts; S++) {
                double ws = w[S] / Z;
                if (ws < 1e-12) continue;
                for (int k = C.off[S]; k < C.off[S + 1]; k++) {
                    gr[C.eu[k]] += ws * x[C.ev[k]];
                    gr[C.ev[k]] += ws * x[C.eu[k]];
                }
            }
            double gmax = 0.0;
            for (int i = 0; i < n; i++) gmax = max(gmax, fabs(gr[i]));
            if (gmax < 1e-15) break;
            double Zx = 0.0;
            for (int i = 0; i < n; i++) { x[i] *= exp(eta * gr[i] / gmax); Zx += x[i]; }
            for (int i = 0; i < n; i++) x[i] /= Zx;
        }
        double v = Fmin(C, x.data());
        if (v > gbest) { gbest = v; for (int i = 0; i < n; i++) xbest[i] = x[i]; }
    }
    return gbest;   // rigorous lower bound on g(G): F(xbest) evaluated exactly
}

// ---- exact integer blow-up optimisation at a fixed order N -------------
static long long int_min(const Cuts& C, const long long* t) {
    long long best = LLONG_MAX;
    for (int S = 0; S < C.ncuts; S++) {
        long long q = 0;
        for (int k = C.off[S]; k < C.off[S + 1]; k++) q += t[C.eu[k]] * t[C.ev[k]];
        if (q < best) best = q;
        if (best == 0) break;
    }
    return best;
}

static long long int_polish(const Cuts& C, long long N, const double* x0, vector<long long>& tout) {
    int n = C.n;
    vector<long long> t(n, 0);
    // largest-remainder rounding of N*x0
    {
        vector<pair<double,int>> rem(n);
        long long used = 0;
        for (int i = 0; i < n; i++) {
            double v = N * x0[i];
            t[i] = (long long)floor(v);
            rem[i] = {v - t[i], i};
            used += t[i];
        }
        sort(rem.begin(), rem.end(), [](auto&a, auto&b){ return a.first > b.first; });
        for (int k = 0; used < N; k++, used++) t[rem[k % n].second]++;
    }
    long long cur = int_min(C, t.data());
    for (long long step = max(1LL, N / 4); ; step = step / 2) {
        bool improved = true;
        while (improved) {
            improved = false;
            for (int a = 0; a < n; a++) {
                if (t[a] < step) continue;
                for (int b = 0; b < n; b++) {
                    if (a == b) continue;
                    t[a] -= step; t[b] += step;
                    long long v = int_min(C, t.data());
                    if (v > cur) { cur = v; improved = true; }
                    else { t[a] += step; t[b] -= step; }
                }
            }
        }
        if (step == 1) break;
    }
    // second-order neighbourhood: two simultaneous unit transfers (needed because
    // e.g. for C5 the single-transfer neighbourhood has spurious local maxima)
    bool improved = (n <= 11);   // O(n^4 * ncuts): only affordable for small templates
    while (improved) {
        improved = false;
        for (int a = 0; a < n && !improved; a++) for (int b = 0; b < n && !improved; b++) {
            if (a == b || t[a] < 1) continue;
            for (int c = 0; c < n && !improved; c++) for (int d = 0; d < n && !improved; d++) {
                if (c == d) continue;
                t[a]--; t[b]++;
                if (t[c] < 1) { t[a]++; t[b]--; continue; }
                t[c]--; t[d]++;
                long long v = int_min(C, t.data());
                if (v > cur) { cur = v; improved = true; }
                else { t[a]++; t[b]--; t[c]++; t[d]--; }
            }
        }
        // re-run single-transfer descent after any pair improvement
        if (improved) {
            bool imp2 = true;
            while (imp2) {
                imp2 = false;
                for (int a = 0; a < n; a++) { if (t[a] < 1) continue;
                    for (int b = 0; b < n; b++) { if (a == b) continue;
                        t[a]--; t[b]++;
                        long long v = int_min(C, t.data());
                        if (v > cur) { cur = v; imp2 = true; }
                        else { t[a]++; t[b]--; }
                    } }
            }
        }
    }
    tout = t;
    return cur;
}

// ------------------------------------------------------------------------
struct Hit { double g; string g6; vector<double> x; };

int main(int argc, char** argv) {
    string mode = argc > 1 ? argv[1] : "scan";
    int restarts = 6, iters = 250, nthreads = 32, topk = 40;
    vector<long long> orders;
    for (int i = 2; i < argc; i++) {
        string a = argv[i];
        if (a == "-r") restarts = atoi(argv[++i]);
        else if (a == "-i") iters = atoi(argv[++i]);
        else if (a == "-t") nthreads = atoi(argv[++i]);
        else if (a == "-k") topk = atoi(argv[++i]);
        else if (a == "-N") orders.push_back(atoll(argv[++i]));
    }
    if (orders.empty()) orders.push_back(100000);

    if (mode == "filter") {
        // streaming: keep only non-bipartite, hom-irreducible templates
        ios::sync_with_stdio(false);
        string s; Graph G; long long in = 0, out = 0;
        while (getline(cin, s)) {
            while (!s.empty() && (s.back()=='\n'||s.back()=='\r')) s.pop_back();
            if (s.empty()) continue;
            in++;
            if (!parse_g6(s, G)) continue;
            if (bipartite(G) || has_dominated_vertex(G)) continue;
            out++;
            fwrite(s.data(), 1, s.size(), stdout); fputc('\n', stdout);
        }
        fprintf(stderr, "# filter: in=%lld kept=%lld\n", in, out);
        return 0;
    }

    vector<string> lines;
    { string s; while (getline(cin, s)) { while (!s.empty() && (s.back()=='\n'||s.back()=='\r')) s.pop_back(); if (!s.empty()) lines.push_back(s); } }

    if (mode == "polish") {
        for (auto& s : lines) {
            Graph G;
            if (!parse_g6(s, G)) { fprintf(stderr, "bad g6 %s\n", s.c_str()); continue; }
            if (!triangle_free(G)) { printf("%s HAS_TRIANGLE\n", s.c_str()); continue; }
            Cuts C; build_cuts(G, C);
            vector<array<int,5>> sd = induced_C5s(G, 40);
            vector<double> x(G.n);
            double g = optimize(C, x.data(), restarts + (int)sd.size(), iters, 12345, &sd);
            printf("%s n=%d m=%zu g~%.9f  x=[", s.c_str(), G.n, G.E.size(), g);
            for (int i = 0; i < G.n; i++) printf("%s%.5f", i?",":"", x[i]);
            printf("]\n");
            for (long long N : orders) {
                vector<long long> t;
                long long b = int_polish(C, N, x.data(), t);
                bool viol = (25 * b > N * N);
                printf("   N=%-7lld bip=%-14lld 25*bip=%-16lld N^2=%-16lld ratio=%.9f floor(N^2/25)=%lld %s t=[",
                       N, b, 25 * b, N * N, (double)b / ((double)N * N), (N * N) / 25, viol ? "*** VIOLATION ***" : "ok");
                for (size_t i = 0; i < t.size(); i++) printf("%s%lld", i?",":"", t[i]);
                printf("]\n");
            }
        }
        return 0;
    }

    // scan mode
    size_t n = lines.size();
    vector<Hit> hits(nthreads);
    vector<vector<Hit>> tops(nthreads);
    vector<size_t> counted(nthreads, 0), skipped(nthreads, 0);
    mutex mu;
    auto work = [&](int tid) {
        for (size_t idx = tid; idx < n; idx += nthreads) {
            Graph G;
            if (!parse_g6(lines[idx], G)) continue;
            if (bipartite(G) || has_dominated_vertex(G)) { skipped[tid]++; continue; }
            Cuts C; build_cuts(G, C);
            vector<array<int,5>> sd = induced_C5s(G, 24);
            vector<double> x(G.n);
            double g = optimize(C, x.data(), restarts + (int)sd.size(), iters,
                                0x9E3779B97F4A7C15ULL * (idx + 1), &sd);
            counted[tid]++;
            tops[tid].push_back({g, lines[idx], x});
            if (tops[tid].size() > (size_t)topk * 4) {
                sort(tops[tid].begin(), tops[tid].end(), [](const Hit&a, const Hit&b){ return a.g > b.g; });
                tops[tid].resize(topk);
            }
        }
    };
    vector<thread> th;
    for (int i = 0; i < nthreads; i++) th.emplace_back(work, i);
    for (auto& t : th) t.join();

    vector<Hit> all;
    for (auto& v : tops) for (auto& h : v) all.push_back(h);
    sort(all.begin(), all.end(), [](const Hit&a, const Hit&b){ return a.g > b.g; });
    size_t tot = 0, skp = 0;
    for (int i = 0; i < nthreads; i++) { tot += counted[i]; skp += skipped[i]; }
    printf("# templates read=%zu evaluated=%zu bipartite_skipped=%zu\n", n, tot, skp);
    int shown = 0;
    for (auto& h : all) {
        if (shown++ >= topk) break;
        printf("%.10f  %s  25g=%.9f %s  x=[", h.g, h.g6.c_str(), 25.0 * h.g, (h.g > 0.04 + 1e-9) ? "*** OVER 1/25 ***" : "");
        for (size_t i = 0; i < h.x.size(); i++) printf("%s%.5f", i?",":"", h.x[i]);
        printf("]\n");
    }
    return 0;
}
