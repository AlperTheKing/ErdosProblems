// R8 stability census.  EXACT INTEGER arithmetic throughout.
//
// For a graph H on n vertices and an integer weight vector a >= 0 with sum a = q,
//   M(a) = min over bipartitions S of  sum_{uv in E, u,v on the same side} a_u a_v   (an integer)
// and psi(H, a/q) = M(a)/q^2.  The conjecture says 25*M(a) <= q^2 for every a.
//
// We enumerate ALL compositions of q into n non-negative parts (ZEROS ALLOWED, as required)
// and store M exactly.  Then:
//   * global maximum and its full argmax set;
//   * the QUANTITATIVE STABILITY PROFILE:  BFS distance d(a) (in unit transfers; note
//     ||a-a*||_1 = 2*d) from the argmax set, and  env[d] = max{ M(a) : d(a) = d }.
//     env is the exact "either close to the extremal set, or psi <= env/q^2" curve.
//   * grid-local maxima (no single unit transfer improves) with M > 0.
//
// usage:  R8_stability_census <g6file> <q> [maxargmax] [profile=0/1]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
#include <map>
#include <deque>
using namespace std;

static int n, m;
static int eu[64], ev[64];
static uint64_t adjm[32];

static bool parse_g6(const string &s) {
    n = (int)s[0] - 63;
    if (n < 1 || n > 20) return false;
    vector<int> bits;
    for (size_t i = 1; i < s.size(); i++) {
        int v = (int)s[i] - 63;
        for (int k = 5; k >= 0; k--) bits.push_back((v >> k) & 1);
    }
    for (int i = 0; i < n; i++) adjm[i] = 0;
    m = 0;
    size_t p = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            if (p < bits.size() && bits[p]) {
                eu[m] = i; ev[m] = j; m++;
                adjm[i] |= 1ull << j; adjm[j] |= 1ull << i;
            }
            p++;
        }
    return true;
}
static bool triangle_free() {
    for (int k = 0; k < m; k++) if (adjm[eu[k]] & adjm[ev[k]]) return false;
    return true;
}
static int count_induced_C5() {
    int cnt = 0, vs[5];
    for (vs[0] = 0; vs[0] < n; vs[0]++)
    for (vs[1] = vs[0]+1; vs[1] < n; vs[1]++)
    for (vs[2] = vs[1]+1; vs[2] < n; vs[2]++)
    for (vs[3] = vs[2]+1; vs[3] < n; vs[3]++)
    for (vs[4] = vs[3]+1; vs[4] < n; vs[4]++) {
        int deg[5] = {0,0,0,0,0}, e = 0;
        for (int i = 0; i < 5; i++) for (int j = i+1; j < 5; j++)
            if ((adjm[vs[i]] >> vs[j]) & 1) { deg[i]++; deg[j]++; e++; }
        if (e != 5) continue;
        bool ok = true;
        for (int i = 0; i < 5; i++) if (deg[i] != 2) { ok = false; break; }
        if (ok) cnt++;
    }
    return cnt;
}

static vector<vector<int64_t>> Nc;
static void build_N(int q, int nn) {
    Nc.assign(nn + 1, vector<int64_t>(q + 1, 0));
    for (int r = 0; r <= q; r++) Nc[1][r] = 1;
    for (int k = 2; k <= nn; k++)
        for (int r = 0; r <= q; r++) {
            int64_t s = 0;
            for (int v = 0; v <= r; v++) s += Nc[k - 1][r - v];
            Nc[k][r] = s;
        }
}
static int64_t rank_comp(const int *a, int q, int nn) {
    int64_t idx = 0; int s = 0;
    for (int i = 0; i + 1 < nn; i++) {
        for (int v = 0; v < a[i]; v++) idx += Nc[nn - 1 - i][q - s - v];
        s += a[i];
    }
    return idx;
}
static vector<signed char> COMP;
struct Rec {
    int nn, q; vector<int> *cur; vector<signed char> *out; int64_t idx;
    void go(int i, int rem) {
        if (i == nn - 1) {
            (*cur)[i] = rem;
            for (int t = 0; t < nn; t++) (*out)[(size_t)idx * nn + t] = (signed char)(*cur)[t];
            idx++;
            return;
        }
        for (int v = 0; v <= rem; v++) { (*cur)[i] = v; go(i + 1, rem - v); }
    }
};
static void gen_comps(int q, int nn) {
    COMP.assign((size_t)Nc[nn][q] * nn, 0);
    vector<int> cur(nn, 0);
    Rec rec; rec.nn = nn; rec.q = q; rec.cur = &cur; rec.out = &COMP; rec.idx = 0;
    rec.go(0, q);
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: census <g6file> <q> [maxargmax] [profile]\n"); return 1; }
    FILE *f = fopen(argv[1], "r");
    if (!f) { fprintf(stderr, "cannot open %s\n", argv[1]); return 1; }
    int q = atoi(argv[2]);
    int maxarg = argc > 3 ? atoi(argv[3]) : 8;
    int profile = argc > 4 ? atoi(argv[4]) : 0;
    int doloc = argc > 5 ? atoi(argv[5]) : 1;
    char buf[512];
    int lastn = -1;
    while (fgets(buf, sizeof buf, f)) {
        string s(buf);
        while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back();
        if (s.empty()) continue;
        if (!parse_g6(s)) continue;
        if (!triangle_free()) { fprintf(stderr, "NOT TRIANGLE FREE: %s\n", s.c_str()); continue; }
        int nc5 = count_induced_C5();
        if (n != lastn) { build_N(q, n); gen_comps(q, n); lastn = n; }
        int64_t total = Nc[n][q];

        int ncut = 1 << (n - 1);
        vector<vector<int>> mono(ncut);
        for (int S = 0; S < ncut; S++) {
            int Sm = (S << 1) | 1;
            for (int k = 0; k < m; k++)
                if (((Sm >> eu[k]) & 1) == ((Sm >> ev[k]) & 1)) mono[S].push_back(k);
        }
        vector<int32_t> Mv(total);
        for (int64_t r = 0; r < total; r++) {
            const signed char *a = &COMP[(size_t)r * n];
            int best = INT32_MAX;
            for (int S = 0; S < ncut; S++) {
                int val = 0;
                const vector<int> &mo = mono[S];
                for (size_t t = 0; t < mo.size(); t++) {
                    val += (int)a[eu[mo[t]]] * (int)a[ev[mo[t]]];
                    if (val >= best) break;
                }
                if (val < best) { best = val; if (best == 0) break; }
            }
            Mv[r] = best;
        }

        int32_t best = -1;
        vector<int64_t> argmax;
        for (int64_t r = 0; r < total; r++) {
            if (Mv[r] > best) { best = Mv[r]; argmax.clear(); }
            if (Mv[r] == best) argmax.push_back(r);
        }
        printf("G %s n=%d m=%d nC5=%d q=%d bestM=%d 25M=%d q2=%d nargmax=%d\n",
               s.c_str(), n, m, nc5, q, best, 25 * best, q * q, (int)argmax.size());
        for (size_t i = 0; i < argmax.size() && (int)i < maxarg; i++) {
            const signed char *a = &COMP[(size_t)argmax[i] * n];
            printf("  ARGMAX");
            for (int t = 0; t < n; t++) printf(" %d", (int)a[t]);
            printf("\n");
        }
        if (best <= 0) { fflush(stdout); continue; }

        // grid-local maxima with M > 0 (single unit transfer)
        if (doloc) {
            map<int32_t, int64_t> lv;
            map<int32_t, vector<int64_t>> reps;
            int b2[24];
            for (int64_t r = 0; r < total; r++) {
                if (Mv[r] <= 0) continue;
                const signed char *a = &COMP[(size_t)r * n];
                bool loc = true;
                for (int i = 0; i < n && loc; i++) {
                    if (a[i] == 0) continue;
                    for (int j = 0; j < n; j++) {
                        if (i == j) continue;
                        for (int t = 0; t < n; t++) b2[t] = a[t];
                        b2[i]--; b2[j]++;
                        if (Mv[rank_comp(b2, q, n)] > Mv[r]) { loc = false; break; }
                    }
                }
                if (loc) { lv[Mv[r]]++; if ((int)reps[Mv[r]].size() < 3) reps[Mv[r]].push_back(r); }
            }
            vector<pair<int32_t,int64_t> > vv(lv.begin(), lv.end());
            sort(vv.begin(), vv.end(), [](const pair<int32_t,int64_t>&x, const pair<int32_t,int64_t>&y){ return x.first > y.first; });
            printf("  GRIDLOCMAX");
            for (size_t i = 0; i < vv.size() && i < 10; i++) printf(" %d:%lld", vv[i].first, (long long)vv[i].second);
            printf("\n");
            for (size_t i = 1; i < vv.size() && i < 4; i++)
                for (size_t z = 0; z < reps[vv[i].first].size(); z++) {
                    const signed char *a = &COMP[(size_t)reps[vv[i].first][z] * n];
                    printf("  LOCREP %d :", vv[i].first);
                    for (int t = 0; t < n; t++) printf(" %d", (int)a[t]);
                    printf("\n");
                }
        }

        if (profile) {
            // BFS from argmax over unit-transfer moves; d(a) = ||a-a*||_1 / 2
            vector<int16_t> dist(total, -1);
            deque<int64_t> Qd;
            for (size_t i = 0; i < argmax.size(); i++) { dist[argmax[i]] = 0; Qd.push_back(argmax[i]); }
            int b2[24];
            while (!Qd.empty()) {
                int64_t r = Qd.front(); Qd.pop_front();
                const signed char *a = &COMP[(size_t)r * n];
                for (int i = 0; i < n; i++) {
                    if (a[i] == 0) continue;
                    for (int j = 0; j < n; j++) {
                        if (i == j) continue;
                        for (int t = 0; t < n; t++) b2[t] = a[t];
                        b2[i]--; b2[j]++;
                        int64_t rr = rank_comp(b2, q, n);
                        if (dist[rr] < 0) { dist[rr] = dist[r] + 1; Qd.push_back(rr); }
                    }
                }
            }
            int maxd = 0;
            for (int64_t r = 0; r < total; r++) if (dist[r] > maxd) maxd = dist[r];
            vector<int32_t> env(maxd + 1, -1);
            for (int64_t r = 0; r < total; r++) if (dist[r] >= 0 && Mv[r] > env[dist[r]]) env[dist[r]] = Mv[r];
            printf("  PROFILE maxd=%d :", maxd);
            for (int d = 0; d <= maxd; d++) printf(" %d", env[d]);
            printf("\n");
        }
        fflush(stdout);
    }
    fclose(f);
    return 0;
}
