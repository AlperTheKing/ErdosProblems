// audit_P3_arcexact.cpp -- INDEPENDENT adversarial test of P3.md's ARC-EXACTNESS claim
//   "ARCBOUND(mu) = psi(mu) exactly on the circle graphs, not just >=".
//
// P3 tested only the Andrasfai circles Gamma_i = Gamma(3i-1), i = 2..8 (m = 5,8,11,14,17,20,23),
// with integer weightings up to a small q.  That is one residue class of m mod 3 and only seven
// circle sizes.  This program tests the STRUCTURAL statement instead:
//
//   a measure on the circle supported on s atoms is, combinatorially, s points in cyclic order
//   with gaps d_0..d_{s-1} summing to m, and u ~ v iff 3*circdist(u,v) > m.  The trace of a
//   cyclic arc of the circle on the support is exactly a cyclic interval of the s atoms.
//   So: enumerate EVERY circular-threshold adjacency pattern reachable with m <= MMAX,
//   and for each one every positive integer weighting with total <= QMAX, and compare
//        arcmin = min over the s(s-1)+2 cyclic intervals
//   against
//        bip    = min over all 2^(s-1) cuts.
//   A single arcmin > bip refutes exactness.
//
// This covers every rational atom configuration of denominator <= MMAX, i.e. every induced
// subgraph of every Gamma(m), m <= MMAX -- all three residue classes of m mod 3.
//
// usage: audit_P3_arcexact <smin> <smax> <mmax> <qmax> [threads]
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <set>
#include <map>
#include <algorithm>
#include <thread>
#include <atomic>
#include <mutex>
#include <string>
using namespace std;

static int SMIN, SMAX, MMAX, QMAX, NTH;
static int CONTROL_HALF = 0;
static mutex OUTM;
static atomic<long long> G_configs(0), G_fail(0), G_patterns(0);

// adjacency of s points with given gaps, as an s x s bit matrix packed into uint16 rows
struct Pat { int s; uint16_t row[16]; int m; vector<int> gaps; };

static uint64_t keyOf(int s, const uint16_t* row) {
    // canonical key under rotation and reflection of the cyclic order
    uint64_t best = ~0ULL;
    for (int r = 0; r < s; r++) for (int refl = 0; refl < 2; refl++) {
        uint64_t k = 0; int bit = 0;
        for (int i = 0; i < s; i++) for (int j = i + 1; j < s; j++) {
            int a = refl ? (r - i + 2 * s) % s : (r + i) % s;
            int b = refl ? (r - j + 2 * s) % s : (r + j) % s;
            if ((row[a] >> b) & 1) k |= (1ULL << bit);
            bit++;
        }
        if (k < best) best = k;
    }
    return best;
}

int main(int argc, char** argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s smin smax mmax qmax [threads]\n", argv[0]); return 1; }
    SMIN = atoi(argv[1]); SMAX = atoi(argv[2]); MMAX = atoi(argv[3]); QMAX = atoi(argv[4]);
    NTH = argc > 5 ? atoi(argv[5]) : 8;
    CONTROL_HALF = (argc > 6 && string(argv[6]) == "HALF") ? 1 : 0;
    if (CONTROL_HALF) printf("### CONTROL MODE: half-arcs only -- falsifiers are EXPECTED ###\n");

    for (int s = SMIN; s <= SMAX; s++) {
        // ---- enumerate every circular-threshold pattern on s atoms with m <= MMAX
        map<uint64_t, Pat> pats;
        vector<int> d(s);
        // iterate gap vectors with sum m, m from s to MMAX
        // simple odometer over compositions
        for (int m = s; m <= MMAX; m++) {
            // compositions of m into s positive parts
            vector<int> c(s, 1); c[s - 1] = m - (s - 1);
            while (true) {
                int pos[16]; pos[0] = 0;
                for (int k = 1; k < s; k++) pos[k] = pos[k - 1] + c[k - 1];
                uint16_t row[16]; for (int k = 0; k < s; k++) row[k] = 0;
                for (int i = 0; i < s; i++) for (int j = i + 1; j < s; j++) {
                    int dd = pos[j] - pos[i]; int cd = min(dd, m - dd);
                    if (3 * cd > m) { row[i] |= (uint16_t)(1u << j); row[j] |= (uint16_t)(1u << i); }
                }
                uint64_t k = keyOf(s, row);
                if (!pats.count(k)) { Pat P; P.s = s; P.m = m; for (int t = 0; t < s; t++) P.row[t] = row[t];
                                      P.gaps.assign(c.begin(), c.end()); pats[k] = P; }
                // next composition of m into s positive parts (lexicographic)
                int i = s - 2;
                while (i >= 0 && c[i] == m - (s - 1)) i--;
                if (i < 0) break;
                bool adv = false;
                for (int t = s - 2; t >= 0; t--) {
                    if (c[t] < m - (s - 1)) {
                        int used = 0; for (int r = 0; r < t; r++) used += c[r];
                        if (used + c[t] + 1 + (s - 1 - t) <= m) { c[t]++; for (int r = t + 1; r < s - 1; r++) c[r] = 1;
                            int u2 = 0; for (int r = 0; r < s - 1; r++) u2 += c[r]; c[s - 1] = m - u2; adv = true; break; }
                    }
                }
                if (!adv) break;
            }
        }
        vector<Pat> P; for (map<uint64_t, Pat>::iterator it = pats.begin(); it != pats.end(); ++it) P.push_back(it->second);
        G_patterns += (long long)P.size();
        printf("s=%2d  distinct circular-threshold patterns (m<=%d): %zu\n", s, MMAX, P.size());
        fflush(stdout);

        // ---- arc masks: cyclic intervals of {0..s-1}
        //      CONTROL mode "HALF": only the half-arcs, which round 5 already refuted, so the
        //      detector MUST fire; this validates that a failure would be seen.
        vector<uint32_t> arcs;
        for (int st = 0; st < s; st++) for (int len = 0; len <= s; len++) {
            if (CONTROL_HALF && len != s / 2 && len != (s + 1) / 2) continue;
            uint32_t A = 0; for (int t = 0; t < len; t++) A |= 1u << ((st + t) % s);
            arcs.push_back(A);
        }
        sort(arcs.begin(), arcs.end()); arcs.erase(unique(arcs.begin(), arcs.end()), arcs.end());

        atomic<size_t> next(0);
        vector<thread> th;
        for (int t = 0; t < NTH; t++) th.push_back(thread([&]() {
            long long loc = 0, locf = 0;
            vector<int> a(s);
            for (;;) {
                size_t pi = next.fetch_add(1); if (pi >= P.size()) break;
                const Pat& pp = P[pi];
                // edge list
                int eu[128], ev[128], ne = 0;
                for (int i = 0; i < s; i++) for (int j = i + 1; j < s; j++) if ((pp.row[i] >> j) & 1) { eu[ne] = i; ev[ne] = j; ne++; }
                if (ne == 0) continue;
                // precompute mono edge lists for all 2^(s-1) cuts and for arcs
                int nc = 1 << (s - 1);
                vector<vector<pair<int,int> > > mono(nc);
                for (int mask = 0; mask < nc; mask++)
                    for (int t2 = 0; t2 < ne; t2++)
                        if (((mask >> eu[t2]) & 1) == ((mask >> ev[t2]) & 1)) mono[mask].push_back(make_pair(eu[t2], ev[t2]));
                vector<int> arcidx;
                for (size_t k = 0; k < arcs.size(); k++) {
                    uint32_t A = arcs[k];
                    if ((A >> (s - 1)) & 1u) A = (~A) & ((1u << s) - 1);   // normalise top bit = 0
                    arcidx.push_back((int)A);
                }
                sort(arcidx.begin(), arcidx.end()); arcidx.erase(unique(arcidx.begin(), arcidx.end()), arcidx.end());
                // weightings
                for (int q = s; q <= QMAX; q++) {
                    for (int k = 0; k < s; k++) a[k] = 1;
                    a[s - 1] = q - (s - 1);
                    while (true) {
                        long long arcmin = -1;
                        for (size_t k = 0; k < arcidx.size(); k++) {
                            long long v = 0; const vector<pair<int,int> >& M = mono[arcidx[k]];
                            for (size_t t2 = 0; t2 < M.size(); t2++) v += (long long)a[M[t2].first] * a[M[t2].second];
                            if (arcmin < 0 || v < arcmin) arcmin = v;
                        }
                        long long bip = arcmin;
                        for (int mask = 0; mask < nc; mask++) {
                            long long v = 0; const vector<pair<int,int> >& M = mono[mask];
                            for (size_t t2 = 0; t2 < M.size(); t2++) { v += (long long)a[M[t2].first] * a[M[t2].second]; if (v >= bip) break; }
                            if (v < bip) bip = v;
                        }
                        loc++;
                        if (arcmin > bip) {
                            locf++;
                            lock_guard<mutex> lk(OUTM);
                            printf("*** ARC-EXACTNESS FALSIFIER  s=%d m=%d gaps=", s, pp.m);
                            for (int k = 0; k < s; k++) printf("%d%s", pp.gaps[k], k + 1 < s ? "," : "");
                            printf("  a="); for (int k = 0; k < s; k++) printf("%d%s", a[k], k + 1 < s ? "," : "");
                            printf("  arcmin=%lld  bip=%lld  q=%d\n", arcmin, bip, q);
                            fflush(stdout);
                        }
                        // next positive composition of q into s parts
                        int i = s - 2;
                        while (i >= 0 && a[i] >= q - (s - 1)) i--;
                        if (i < 0) break;
                        bool adv = false;
                        for (int t2 = s - 2; t2 >= 0; t2--) {
                            int used = 0; for (int r = 0; r < t2; r++) used += a[r];
                            if (used + a[t2] + 1 + (s - 1 - t2) <= q) { a[t2]++; for (int r = t2 + 1; r < s - 1; r++) a[r] = 1;
                                int u2 = 0; for (int r = 0; r < s - 1; r++) u2 += a[r]; a[s - 1] = q - u2; adv = true; break; }
                        }
                        if (!adv) break;
                    }
                }
            }
            G_configs += loc; G_fail += locf;
        }));
        for (int t = 0; t < NTH; t++) th[t].join();
        printf("s=%2d  done.  cumulative configs=%lld  cumulative falsifiers=%lld\n",
               s, (long long)G_configs, (long long)G_fail);
        fflush(stdout);
    }
    printf("TOTAL patterns=%lld  configs=%lld  ARC-EXACTNESS FALSIFIERS=%lld\n",
           (long long)G_patterns, (long long)G_configs, (long long)G_fail);
    return 0;
}
