// Q2_finite.cpp -- EXACT finite-blow-up mechanism-ceiling search.
//
// For every connected triangle-free pattern H on h vertices, every 2-colouring
// (= part-respecting cut) and every integer weight vector a with sum a_i = N,
// decide which families of max-cut switching inequalities are satisfied, and
// record the largest 25|M|/N^2 that survives each family.
//
// Everything is integer arithmetic (long long).  Blow-up facts used:
//   parts are independent sets, so Delta(S) is MULTILINEAR in s_i = |S cap V_i|;
//   sigma is constant on parts.
//
// families
//   LOC  : sigma_i >= 0  and  switch-star  sigma_i >= sum_{j in N_B(i), sigma_j<=1} a_j (2-sigma_j)
//   STAR : LOC + Delta(N(v) u T) <= 0 for every part i (v in V_i) and every
//          independent union-of-parts T disjoint from N(i)      [family (*)]
//   ALL  : LOC + Delta(S) <= 0 for all 2^h part-subsets S       [<=> maximum cut]
//
// Any (H,col,a) that satisfies a family but has 25|M| > N^2 is an EXACT witness
// that no discharging scheme built from that family can prove the conjecture.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>
#include <thread>
#include <mutex>
using namespace std;
typedef long long ll;

struct Pat { int h; int adj[8][8]; string g6; };

static vector<Pat> pats;

struct Best {
    ll num = 0, den = 1;   // 25M / N^2  as a fraction, stored as (25M, N*N)
    string desc;
    void upd(ll M, ll N, const string& d) {
        ll a = 25 * M, b = N * N;
        if ((__int128)a * den > (__int128)num * b) { num = a; den = b; desc = d; }
    }
};

struct Ctx {
    int h; const int (*adj)[8]; int col[8];
    ll a[8], sig[8], N;
    vector<int> nbrmask, indepSets, starSets;
};

static inline ll deltaS(const Ctx& C, int Smask) {
    ll v = 0;
    for (int i = 0; i < C.h; i++) if (Smask >> i & 1) v -= C.a[i] * C.sig[i];
    for (int i = 0; i < C.h; i++) if (Smask >> i & 1)
        for (int j = i + 1; j < C.h; j++) if ((Smask >> j & 1) && C.adj[i][j])
            v += (C.col[i] == C.col[j] ? -2 : 2) * C.a[i] * C.a[j];
    return v;
}

int main(int argc, char** argv) {
    // ---- read patterns: "h" then h lines of h chars
    FILE* f = fopen(argv[1], "r");
    char buf[256];
    while (fgets(buf, sizeof buf, f)) {
        if (buf[0] == '#') continue;
        Pat p; char g6[64];
        if (sscanf(buf, "%d %s", &p.h, g6) != 2) continue;
        p.g6 = g6;
        memset(p.adj, 0, sizeof p.adj);
        for (int i = 0; i < p.h; i++) {
            if (!fgets(buf, sizeof buf, f)) break;
            for (int j = 0; j < p.h; j++) p.adj[i][j] = (buf[j] == '1');
        }
        pats.push_back(p);
    }
    fclose(f);
    int Nmin = atoi(argv[2]), Nmax = atoi(argv[3]);
    int nth = argc > 4 ? atoi(argv[4]) : 8;
    fprintf(stderr, "patterns=%zu N=%d..%d threads=%d\n", pats.size(), Nmin, Nmax, nth);

    mutex mu;
    Best gLOC, gSTAR, gALL;
    vector<string> witLOC, witSTAR, witALL;

    auto work = [&](int tid) {
        Best bLOC, bSTAR, bALL;
        vector<string> wL, wS, wA;
        for (size_t pi = tid; pi < pats.size(); pi += nth) {
            const Pat& P = pats[pi];
            int h = P.h;
            for (int cm = 0; cm < (1 << (h - 1)); cm++) {
                Ctx C; C.h = h; C.adj = P.adj;
                C.col[0] = 0;
                for (int i = 1; i < h; i++) C.col[i] = (cm >> (i - 1)) & 1;
                // precompute neighbour masks and STAR sets
                int nb[8];
                for (int i = 0; i < h; i++) { nb[i] = 0; for (int j = 0; j < h; j++) if (P.adj[i][j]) nb[i] |= 1 << j; }
                vector<int> starSets;
                for (int i = 0; i < h; i++) {
                    int rest = ((1 << h) - 1) & ~nb[i];
                    for (int sub = rest; ; sub = (sub - 1) & rest) {
                        bool indep = true;
                        for (int x = 0; x < h && indep; x++) if (sub >> x & 1)
                            for (int y = x + 1; y < h; y++) if ((sub >> y & 1) && P.adj[x][y]) { indep = false; break; }
                        if (indep) { int S = nb[i] | sub; if (S && S != (1 << h) - 1) starSets.push_back(S); }
                        if (sub == 0) break;
                    }
                }
                sort(starSets.begin(), starSets.end());
                starSets.erase(unique(starSets.begin(), starSets.end()), starSets.end());

                for (int N = Nmin; N <= Nmax; N++) {
                    // enumerate compositions a_0..a_{h-1} >= 0 summing to N
                    struct Rec {
                        Ctx& C; const Pat& P; const vector<int>& starSets;
                        Best &bLOC, &bSTAR, &bALL; vector<string> &wL, &wS, &wA;
                        int h; ll N;
                        void go(int i, ll rem) {
                            if (i == h - 1) { C.a[i] = rem; eval(); return; }
                            for (ll v = 0; v <= rem; v++) { C.a[i] = v; go(i + 1, rem - v); }
                        }
                        void eval() {
                            // sigma
                            for (int i = 0; i < h; i++) {
                                ll s = 0;
                                for (int j = 0; j < h; j++) if (P.adj[i][j]) s += (C.col[i] == C.col[j] ? -C.a[j] : C.a[j]);
                                C.sig[i] = s;
                                if (C.a[i] > 0 && s < 0) return;
                            }
                            // mono mass
                            ll M = 0;
                            for (int i = 0; i < h; i++) for (int j = i + 1; j < h; j++)
                                if (P.adj[i][j] && C.col[i] == C.col[j]) M += C.a[i] * C.a[j];
                            if (25 * M <= N * N) return;         // only violations are interesting
                            // switch-star
                            for (int i = 0; i < h; i++) {
                                if (!C.a[i]) continue;
                                ll rhs = 0;
                                for (int j = 0; j < h; j++)
                                    if (P.adj[i][j] && C.col[i] != C.col[j] && C.sig[j] <= 1 && C.a[j] > 0)
                                        rhs += C.a[j] * (2 - C.sig[j]);
                                if (C.sig[i] < rhs) return;
                            }
                            char d[256];
                            snprintf(d, sizeof d, "H=%s col=%d%d%d%d%d%d%d a=%lld,%lld,%lld,%lld,%lld,%lld,%lld N=%lld M=%lld",
                                     P.g6.c_str(), C.col[0], C.col[1], C.col[2], C.col[3], C.col[4], C.col[5], C.col[6],
                                     C.a[0], C.a[1], C.a[2], C.a[3], C.a[4], C.a[5], C.a[6], N, M);
                            bLOC.upd(M, N, d); if (wL.size() < 40) wL.push_back(d);
                            // STAR
                            bool ok = true;
                            for (int S : starSets) if (deltaS(C, S) > 0) { ok = false; break; }
                            if (!ok) return;
                            bSTAR.upd(M, N, d); if (wS.size() < 40) wS.push_back(d);
                            // ALL
                            for (int S = 1; S < (1 << h) - 1; S++) if (deltaS(C, S) > 0) return;
                            bALL.upd(M, N, d); if (wA.size() < 40) wA.push_back(d);
                        }
                    } rec{C, P, starSets, bLOC, bSTAR, bALL, wL, wS, wA, h, (ll)N};
                    C.N = N;
                    rec.go(0, N);
                }
            }
        }
        lock_guard<mutex> lk(mu);
        if ((__int128)bLOC.num * gLOC.den > (__int128)gLOC.num * bLOC.den) gLOC = bLOC;
        if ((__int128)bSTAR.num * gSTAR.den > (__int128)gSTAR.num * bSTAR.den) gSTAR = bSTAR;
        if ((__int128)bALL.num * gALL.den > (__int128)gALL.num * bALL.den) gALL = bALL;
        for (auto& s : wL) if (witLOC.size() < 60) witLOC.push_back(s);
        for (auto& s : wS) if (witSTAR.size() < 60) witSTAR.push_back(s);
        for (auto& s : wA) if (witALL.size() < 60) witALL.push_back(s);
    };
    vector<thread> th;
    for (int t = 0; t < nth; t++) th.emplace_back(work, t);
    for (auto& t : th) t.join();

    printf("### LOC  max 25M/N^2 = %lld/%lld   %s\n", gLOC.num, gLOC.den, gLOC.desc.c_str());
    printf("### STAR max 25M/N^2 = %lld/%lld   %s\n", gSTAR.num, gSTAR.den, gSTAR.desc.c_str());
    printf("### ALL  max 25M/N^2 = %lld/%lld   %s\n", gALL.num, gALL.den, gALL.desc.c_str());
    printf("\n-- LOC witnesses (%zu shown)\n", witLOC.size());
    for (auto& s : witLOC) printf("   %s\n", s.c_str());
    printf("\n-- STAR witnesses (%zu shown)\n", witSTAR.size());
    for (auto& s : witSTAR) printf("   %s\n", s.c_str());
    printf("\n-- ALL witnesses (%zu shown)  [these would be COUNTEREXAMPLES]\n", witALL.size());
    for (auto& s : witALL) printf("   %s\n", s.c_str());
    return 0;
}
