// audit_Q2_v2_d.cpp -- AUDITOR's independent re-implementation of the round7/Q2.md
// section-4 mechanism-ceiling search.  Written from the definitions, not from
// Q2_finite.cpp: own graph6 decoder, own composition enumerator (lexicographic
// "next composition" loop, not recursion), own exact fraction comparison.
//
// families
//   LOC  : sigma_i >= 0 on every part with a_i>0, and the switch-star
//          sigma_i >= sum_{j adj i, col_j != col_i, sigma_j <= 1} a_j (2 - sigma_j)
//   STAR : LOC + Delta(N(v) u T) <= 0, T an independent union of parts, T disj N(v)
//   ALL  : LOC + Delta(S) <= 0 for every part-subset S  (= maximum cut, by multilinearity)
//
// usage: audit_Q2_v2_d.exe <g6file> <N> [threads]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <algorithm>
using namespace std;
typedef long long ll;
typedef __int128 lll;

struct G { int h; unsigned char A[9][9]; string s; };

static bool decode(const string& s, G& g) {
    int n = (int)s[0] - 63;
    if (n < 1 || n > 8) return false;
    g.h = n; g.s = s;
    memset(g.A, 0, sizeof g.A);
    int need = n * (n - 1) / 2, got = 0;
    vector<int> bits;
    for (size_t k = 1; k < s.size(); k++) {
        int v = (int)s[k] - 63;
        for (int b = 5; b >= 0; b--) bits.push_back((v >> b) & 1);
    }
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            int b = bits[got++];
            g.A[i][j] = g.A[j][i] = (unsigned char)b;
        }
    (void)need;
    return true;
}

struct Frac {            // 25M / N^2 kept as (num, den), compared exactly
    ll num = 0, den = 1;
    string w;
    bool better(ll a, ll b) const { return (lll)a * den > (lll)num * b; }
    void upd(ll M, ll N, const string& d) {
        ll a = 25 * M, b = N * N;
        if (better(a, b)) { num = a; den = b; w = d; }
    }
};

int main(int argc, char** argv) {
    FILE* f = fopen(argv[1], "r");
    if (!f) { fprintf(stderr, "no file\n"); return 1; }
    vector<G> gs; char buf[128];
    while (fscanf(f, "%127s", buf) == 1) { G g; if (decode(buf, g)) gs.push_back(g); }
    fclose(f);
    int N = atoi(argv[2]);
    int nth = argc > 3 ? atoi(argv[3]) : 8;
    fprintf(stderr, "patterns=%zu N=%d threads=%d\n", gs.size(), N, nth);

    mutex mu;
    Frac gLOC, gSTAR, gALL;
    ll cLOC = 0, cSTAR = 0, cALL = 0;

    auto work = [&](int tid) {
        Frac bLOC, bSTAR, bALL;
        ll nL = 0, nS = 0, nA = 0;
        for (size_t gi = tid; gi < gs.size(); gi += nth) {
            const G& g = gs[gi];
            int h = g.h;
            // independent part-subsets, precomputed
            vector<int> indep;
            for (int m = 0; m < (1 << h); m++) {
                bool ok = true;
                for (int i = 0; i < h && ok; i++) if (m >> i & 1)
                    for (int j = i + 1; j < h; j++) if ((m >> j & 1) && g.A[i][j]) { ok = false; break; }
                if (ok) indep.push_back(m);
            }
            int nb[9];
            for (int i = 0; i < h; i++) { nb[i] = 0; for (int j = 0; j < h; j++) if (g.A[i][j]) nb[i] |= 1 << j; }
            for (int cm = 0; cm < (1 << (h - 1)); cm++) {
                int col[9]; col[0] = 0;
                for (int i = 1; i < h; i++) col[i] = (cm >> (i - 1)) & 1;
                // STAR set list
                vector<int> Sstar;
                for (int i = 0; i < h; i++)
                    for (int T : indep)
                        if ((T & nb[i]) == 0) {
                            int S = nb[i] | T;
                            if (S && S != (1 << h) - 1) Sstar.push_back(S);
                        }
                sort(Sstar.begin(), Sstar.end());
                Sstar.erase(unique(Sstar.begin(), Sstar.end()), Sstar.end());

                // lexicographic enumeration of compositions a_0..a_{h-1} >= 0, sum = N
                vector<ll> a(h, 0); a[h - 1] = N;
                while (true) {
                    // ---- evaluate
                    ll sig[9], M = 0;
                    bool ok = true;
                    for (int i = 0; i < h; i++) {
                        ll s = 0;
                        for (int j = 0; j < h; j++) if (g.A[i][j]) s += (col[i] == col[j] ? -a[j] : a[j]);
                        sig[i] = s;
                        if (a[i] > 0 && s < 0) ok = false;
                    }
                    if (ok) {
                        for (int i = 0; i < h; i++) for (int j = i + 1; j < h; j++)
                            if (g.A[i][j] && col[i] == col[j]) M += a[i] * a[j];
                        if (25 * M > (ll)N * N) {
                            for (int i = 0; i < h && ok; i++) {
                                if (!a[i]) continue;
                                ll rhs = 0;
                                for (int j = 0; j < h; j++)
                                    if (g.A[i][j] && col[i] != col[j] && a[j] > 0 && sig[j] <= 1)
                                        rhs += a[j] * (2 - sig[j]);
                                if (sig[i] < rhs) ok = false;
                            }
                            if (ok) {
                                char d[256]; int p = snprintf(d, sizeof d, "H=%s col=", g.s.c_str());
                                for (int i = 0; i < h; i++) p += snprintf(d + p, sizeof d - p, "%d", col[i]);
                                p += snprintf(d + p, sizeof d - p, " a=");
                                for (int i = 0; i < h; i++) p += snprintf(d + p, sizeof d - p, "%lld%s", a[i], i + 1 < h ? "," : "");
                                snprintf(d + p, sizeof d - p, " N=%d M=%lld", N, M);
                                bLOC.upd(M, N, d); nL++;
                                bool st = true;
                                for (int S : Sstar) {
                                    ll v = 0;
                                    for (int i = 0; i < h; i++) if (S >> i & 1) v -= a[i] * sig[i];
                                    for (int i = 0; i < h; i++) if (S >> i & 1)
                                        for (int j = i + 1; j < h; j++) if ((S >> j & 1) && g.A[i][j])
                                            v += (col[i] == col[j] ? -2 : 2) * a[i] * a[j];
                                    if (v > 0) { st = false; break; }
                                }
                                if (st) {
                                    bSTAR.upd(M, N, d); nS++;
                                    bool al = true;
                                    for (int S = 1; S < (1 << h) - 1 && al; S++) {
                                        ll v = 0;
                                        for (int i = 0; i < h; i++) if (S >> i & 1) v -= a[i] * sig[i];
                                        for (int i = 0; i < h; i++) if (S >> i & 1)
                                            for (int j = i + 1; j < h; j++) if ((S >> j & 1) && g.A[i][j])
                                                v += (col[i] == col[j] ? -2 : 2) * a[i] * a[j];
                                        if (v > 0) al = false;
                                    }
                                    if (al) { bALL.upd(M, N, d); nA++; if (nA < 20) fprintf(stderr, "ALL-WITNESS %s\n", d); }
                                }
                            }
                        }
                    }
                    // ---- next composition (lexicographic on a_0..a_{h-2})
                    int i = h - 2;
                    while (i >= 0 && a[h - 1] == 0) { a[h - 1] += a[i]; a[i] = 0; i--; }
                    if (i < 0) break;
                    a[i]++; a[h - 1]--;
                }
            }
        }
        lock_guard<mutex> lk(mu);
        if (gLOC.better(bLOC.num, bLOC.den)) {} // no-op to keep symmetry
        if ((lll)bLOC.num * gLOC.den > (lll)gLOC.num * bLOC.den) gLOC = bLOC;
        if ((lll)bSTAR.num * gSTAR.den > (lll)gSTAR.num * bSTAR.den) gSTAR = bSTAR;
        if ((lll)bALL.num * gALL.den > (lll)gALL.num * bALL.den) gALL = bALL;
        cLOC += nL; cSTAR += nS; cALL += nA;
    };
    vector<thread> th;
    for (int t = 0; t < nth; t++) th.emplace_back(work, t);
    for (auto& t : th) t.join();
    printf("N=%d  LOC  max 25M/N^2 = %lld/%lld  count=%lld  %s\n", N, gLOC.num, gLOC.den, cLOC, gLOC.w.c_str());
    printf("N=%d  STAR max 25M/N^2 = %lld/%lld  count=%lld  %s\n", N, gSTAR.num, gSTAR.den, cSTAR, gSTAR.w.c_str());
    printf("N=%d  ALL  max 25M/N^2 = %lld/%lld  count=%lld  %s\n", N, gALL.num, gALL.den, cALL, gALL.w.c_str());
    return 0;
}
