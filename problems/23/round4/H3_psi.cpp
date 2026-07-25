// H3_psi.cpp -- exact integer-weight search for max_x psi(H,x) lower bounds.
//
//   psi(H,x) = min over cuts S of sum_{uv in E, u,v same side} x_u x_v.
//   For integer a >= 0 with sum a = q,  psi(H, a/q) = bip(H[a]) / q^2,
//   where bip(H[a]) = min_S sum_{uv mono} a_u a_v   (accepted fact 1).
//
// Everything is exact 64-bit integer arithmetic.  We enumerate every a >= 0 with sum a = q
// (ZEROS ALLOWED), with a branch-and-bound prune based on a set of "cheap" cuts.
//
// Prune validity:  at a node with assigned prefix, remaining vertex set R and budget r,
//   q_S^final = P_S + sum_{v in R} a_v nb_S(v) + sum_{uv mono, u,v in R} a_u a_v
//             <= P_S + r * max_{v in R} nb_S(v) + floor(r^2/4) * [mono edge inside R]
// (the last term by Motzkin-Straus: the mono graph is triangle-free so clique number <= 2).
// bip <= min over cheap S of q_S^final <= min_S B_S, so we may prune when min_S B_S <= best.
//
// Usage: H3_psi <graph6> <q> [threads] [ncheap]
// Output: exact max of bip(H[a]) over all a, one maximiser, and 25*bip vs q^2.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
#include <atomic>
#include <thread>
#include <mutex>

using namespace std;
typedef long long ll;

int n;                       // number of vertices
vector<vector<int>> adj;     // adjacency lists
vector<pair<int,int>> edges; // edge list
vector<uint32_t> adjmask;

// ---- graph6 decoding -------------------------------------------------------
static void readg6(const string& s) {
    int p = 0;
    if ((unsigned char)s[0] == 126) { // n >= 63
        n = ((s[1]-63)<<12) | ((s[2]-63)<<6) | (s[3]-63);
        p = 4;
    } else { n = s[0]-63; p = 1; }
    adj.assign(n, {}); adjmask.assign(n, 0);
    int bit = 0; int cur = 0; int k = 0;
    vector<int> bits;
    for (size_t t = p; t < s.size(); ++t) {
        int v = s[t]-63;
        for (int b = 5; b >= 0; --b) bits.push_back((v>>b)&1);
    }
    (void)bit; (void)cur; (void)k;
    int idx = 0;
    for (int j = 1; j < n; ++j)
        for (int i = 0; i < j; ++i) {
            if (idx < (int)bits.size() && bits[idx]) {
                adj[i].push_back(j); adj[j].push_back(i);
                adjmask[i] |= 1u<<j; adjmask[j] |= 1u<<i;
                edges.push_back({i,j});
            }
            ++idx;
        }
}

// ---- cheap cuts ------------------------------------------------------------
struct Cut {
    vector<pair<int,int>> mono;         // mono edges
    vector<vector<int>> monoNb;         // monoNb[v] = mono-neighbours of v
    uint32_t mask;                      // side-1 set
};
vector<Cut> cheap;

static void buildCheapCuts(int ncheap) {
    ll total = 1LL << (n-1);
    vector<pair<int,uint32_t>> all;
    all.reserve(total);
    for (ll S = 0; S < total; ++S) {
        uint32_t m = (uint32_t)S;    // vertex 0 always side 0
        int c = 0;
        for (auto&e : edges) if ((((m>>e.first)&1u) == ((m>>e.second)&1u))) ++c;
        all.push_back({c, m});
    }
    sort(all.begin(), all.end());
    if ((int)all.size() > ncheap) all.resize(ncheap);
    cheap.clear();
    for (auto& pr : all) {
        Cut C; C.mask = pr.second;
        C.monoNb.assign(n, {});
        for (auto& e : edges)
            if ((((C.mask>>e.first)&1u) == ((C.mask>>e.second)&1u))) {
                C.mono.push_back(e);
                C.monoNb[e.first].push_back(e.second);
                C.monoNb[e.second].push_back(e.first);
            }
        cheap.push_back(C);
    }
}

// ---- exact bip over ALL cuts ----------------------------------------------
static ll bipFull(const vector<ll>& a) {
    ll total = 1LL << (n-1);
    ll best = -1;
    for (ll S = 0; S < total; ++S) {
        uint32_t m = (uint32_t)S;
        ll v = 0;
        for (auto& e : edges)
            if ((((m>>e.first)&1u) == ((m>>e.second)&1u))) v += a[e.first]*a[e.second];
        if (best < 0 || v < best) { best = v; if (best == 0) break; }
    }
    return best;
}

// ---- search ----------------------------------------------------------------
int Q;
int NC;
std::atomic<ll> gBest(0);
vector<ll> gArg;
mutex gMut;

struct Worker {
    vector<ll> a;
    vector<vector<ll>> P;       // P[depth][cut]
    vector<vector<ll>> NB;      // NB[depth][cut*n+v]
    vector<vector<char>> HASMONO; // HASMONO[depth][cut] : mono edge fully inside remaining set
    ll localBest; vector<ll> localArg;

    void init() {
        a.assign(n, 0);
        P.assign(n+1, vector<ll>(NC, 0));
        NB.assign(n+1, vector<ll>((size_t)NC*n, 0));
        localBest = 0; localArg.assign(n,0);
    }

    // returns true if pruned
    bool prune(int d, ll r) {
        ll cur = gBest.load(memory_order_relaxed);
        if (localBest > cur) cur = localBest;
        ll quad = (r*r)/4;
        for (int c = 0; c < NC; ++c) {
            ll M = 0;
            const ll* nb = &NB[d][(size_t)c*n];
            for (int v = d; v < n; ++v) if (nb[v] > M) M = nb[v];
            ll extra = 0;
            for (auto& e : cheap[c].mono)
                if (e.first >= d && e.second >= d) { extra = quad; break; }
            if (P[d][c] + r*M + extra <= cur) return true;
        }
        return false;
    }

    void rec(int d, ll r) {
        if (d == n) {
            if (r != 0) return;
            ll v = LLONG_MAX;
            for (int c = 0; c < NC; ++c) v = min(v, P[n][c]);
            ll cur = max(localBest, gBest.load(memory_order_relaxed));
            if (v > cur) {
                ll b = bipFull(a);
                if (b > cur) {
                    localBest = b; localArg = a;
                    ll old = gBest.load();
                    while (b > old && !gBest.compare_exchange_weak(old, b)) {}
                    lock_guard<mutex> lk(gMut);
                    if (b >= gBest.load()) gArg = a;
                }
            }
            return;
        }
        if (d == n-1) {           // last vertex takes the whole remaining budget
            a[d] = r;
            step(d, r);
            rec(d+1, 0);
            a[d] = 0;
            return;
        }
        if (prune(d, r)) return;
        for (ll t = r; t >= 0; --t) {
            a[d] = t;
            step(d, t);
            rec(d+1, r-t);
        }
        a[d] = 0;
    }

    // apply a[d] = t : write P[d+1], NB[d+1] from P[d], NB[d]
    void step(int d, ll t) {
        for (int c = 0; c < NC; ++c) {
            const ll* nb = &NB[d][(size_t)c*n];
            ll* nb2 = &NB[d+1][(size_t)c*n];
            memcpy(nb2, nb, sizeof(ll)*n);
            P[d+1][c] = P[d][c] + t*nb[d];
            if (t) for (int u : cheap[c].monoNb[d]) if (u > d) nb2[u] += t;
        }
    }
};

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: H3_psi <graph6> <q> [threads] [ncheap]\n"); return 1; }
    string g6 = argv[1];
    Q = atoi(argv[2]);
    int nthreads = argc > 3 ? atoi(argv[3]) : 8;
    int ncheap = argc > 4 ? atoi(argv[4]) : 256;
    readg6(g6);
    fprintf(stderr, "n=%d m=%d q=%d\n", n, (int)edges.size(), Q);
    buildCheapCuts(ncheap);
    NC = (int)cheap.size();
    fprintf(stderr, "cheap cuts: %d  (mono counts %d .. %d)\n", NC,
            (int)cheap.front().mono.size(), (int)cheap.back().mono.size());

    // seed gBest with the floor of q^2/25 - 1 so that the prune is immediately strong,
    // but never above a value we have actually realised: use q^2/25 - 1 only as a *search*
    // threshold; the reported maximum is then "max(bip) if it exceeds that, else <= that".
    // For an honest exact maximum we start from 0.
    gBest.store(0);
    gArg.assign(n, 0);

    // parallelise over the value of a[0]
    vector<thread> th;
    std::atomic<int> next(0);
    for (int t = 0; t < nthreads; ++t)
        th.emplace_back([&]() {
            Worker W; W.init();
            for (;;) {
                int t0 = next.fetch_add(1);
                if (t0 > Q) break;
                W.a.assign(n, 0);
                W.a[0] = t0;
                for (int c = 0; c < NC; ++c) {
                    memset(&W.NB[0][(size_t)c*n], 0, sizeof(ll)*n);
                    W.P[0][c] = 0;
                }
                W.step(0, t0);
                W.rec(1, Q - t0);
            }
        });
    for (auto& x : th) x.join();

    ll best = gBest.load();
    printf("q=%d  maxbip=%lld  25*maxbip=%lld  q^2=%lld  ratio=%.10f  1/25=%.10f\n",
           Q, best, 25*best, (ll)Q*Q, (double)best/((double)Q*Q), 0.04);
    printf("argmax=");
    for (int v = 0; v < n; ++v) printf("%lld ", gArg[v]);
    printf("\n");
    printf("VERDICT: %s\n", (25*best > (ll)Q*Q) ? "REFUTES 1/25" : "<= 1/25");
    fflush(stdout);
    return 0;
}
