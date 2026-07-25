// Q3 PASS 2 -- how far from a C5-blow-up can a triangle-free graph on N=5n
// vertices be while still having bip = n^2 - 1 ?
//
// At a sharp size N = 5n one has  R = 25*dist/(N^2 - 25*bip) = dist  exactly when
// bip = n^2 - 1.  So  sup R = sup dist over that class, and PERFECT STABILITY
// (Pikhurko-Sliacan-Tyros) fails iff that supremum is infinite.
// Complete enumeration gives  max dist = 10 (N=10, Petersen) and 19 (N=15).
// This program searches N = 20 (and any N) by simulated annealing; every record
// is re-verified exactly (bip by full 2^(N-1) cut enumeration, dist by
// branch and bound) in Python afterwards.
//
// build: clang++ -O3 -march=native -std=c++17 Q3_pass2_n20.cpp -o Q3_pass2_n20.exe
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <random>
#include <vector>
#include <string>
#include <thread>
#include <mutex>
#include <algorithm>
using namespace std;

static int N = 20;          // vertices
static int TARGET = 15;     // required bip
static uint32_t FULL;

struct G {
    uint32_t adj[32];
    G() { memset(adj, 0, sizeof(adj)); }
    bool has(int u, int v) const { return (adj[u] >> v) & 1u; }
    void add(int u, int v) { adj[u] |= 1u << v; adj[v] |= 1u << u; }
    void del(int u, int v) { adj[u] &= ~(1u << v); adj[v] &= ~(1u << u); }
    int edges() const { int s = 0; for (int v = 0; v < N; v++) s += __builtin_popcount(adj[v]); return s / 2; }
    bool trianglefree() const {
        for (int u = 0; u < N; u++)
            for (int v = u + 1; v < N; v++)
                if (has(u, v) && (adj[u] & adj[v])) return false;
        return true;
    }
};

// exact bip by Gray-code enumeration of all 2^(N-1) cuts (vertex 0 fixed outside).
// if `floorv >= 0`, abort as soon as some cut has mono < floorv and return -1.
static int bip(const G& g, int floorv) {
    int cur = g.edges();                 // S = empty : every edge monochromatic
    uint32_t S = 0;
    int best = cur;
    if (floorv >= 0 && cur < floorv) return -1;
    uint64_t lim = 1ull << (N - 1);
    for (uint64_t i = 1; i < lim; i++) {
        int b = __builtin_ctzll(i);      // gray code: flip bit b (vertices 1..N-1)
        int v = b + 1;
        uint32_t bv = 1u << v;
        if (S & bv) {                    // v leaves S
            uint32_t Sm = S & ~bv;
            cur += __builtin_popcount(g.adj[v] & (FULL & ~S)) - __builtin_popcount(g.adj[v] & Sm);
            S = Sm;
        } else {                         // v enters S
            cur += __builtin_popcount(g.adj[v] & S) - __builtin_popcount(g.adj[v] & (FULL & ~S & ~bv));
            S |= bv;
        }
        if (cur < best) {
            best = cur;
            if (floorv >= 0 && best < floorv) return -1;
        }
    }
    return best;
}

static inline bool tmpl(int a, int b) { int d = (a - b + 5) % 5; return d == 1 || d == 4; }

// edit distance to the C5-blow-up family, by multi-restart local search (upper bound).
static int distub(const G& g, mt19937& rng, int restarts) {
    static int T[5][5];
    static bool init = false;
    if (!init) { for (int a = 0; a < 5; a++) for (int b = 0; b < 5; b++) T[a][b] = tmpl(a, b); init = true; }
    int best = 1 << 30;
    int phi[32];
    for (int r = 0; r < restarts; r++) {
        for (int v = 0; v < N; v++) phi[v] = rng() % 5;
        bool imp = true;
        while (imp) {
            imp = false;
            for (int v = 0; v < N; v++) {
                int bc = 1 << 30, ba = phi[v];
                for (int a = 0; a < 5; a++) {
                    int c = 0;
                    for (int u = 0; u < N; u++) {
                        if (u == v) continue;
                        int e = g.has(u, v) ? 1 : 0;
                        if (e != T[phi[u]][a]) c++;
                    }
                    if (c < bc) { bc = c; ba = a; }
                }
                if (ba != phi[v]) { phi[v] = ba; imp = true; }
            }
        }
        int tot = 0;
        for (int u = 0; u < N; u++)
            for (int v = u + 1; v < N; v++) {
                int e = g.has(u, v) ? 1 : 0;
                if (e != T[phi[u]][phi[v]]) tot++;
            }
        if (tot < best) best = tot;
    }
    return best;
}

static string g6(const G& g) {
    string bits;
    for (int j = 1; j < N; j++) for (int i = 0; i < j; i++) bits += (g.has(i, j) ? '1' : '0');
    while (bits.size() % 6) bits += '0';
    string out; out += char(N + 63);
    for (size_t k = 0; k < bits.size(); k += 6) {
        int v = 0; for (int t = 0; t < 6; t++) v = (v << 1) | (bits[k + t] - '0');
        out += char(v + 63);
    }
    return out;
}

static G seed_blowup(mt19937& rng) {
    G g; int k = N / 5;
    for (int i = 0; i < 5; i++) for (int a = 0; a < k; a++)
        for (int b = 0; b < k; b++) g.add(i * k + a, ((i + 1) % 5) * k + b);
    // delete one matching edge per consecutive pair -> bip = k^2 - 1
    for (int i = 0; i < 5; i++) g.del(i * k, ((i + 1) % 5) * k);
    (void)rng;
    return g;
}

// add edges in random order until no non-edge can be added (maximal triangle free).
static void maximalize(G& g, mt19937& rng) {
    vector<pair<int,int>> p;
    for (int u = 0; u < N; u++) for (int v = u + 1; v < N; v++) p.push_back({u, v});
    shuffle(p.begin(), p.end(), rng);
    for (auto& e : p)
        if (!g.has(e.first, e.second) && !(g.adj[e.first] & g.adj[e.second]))
            g.add(e.first, e.second);
}

static G seed_random(mt19937& rng) { G g; maximalize(g, rng); return g; }

// remove r random edges, then re-maximalize: a move inside the maximal-triangle-free world.
static G kick(const G& g, mt19937& rng, int r) {
    G h = g;
    vector<pair<int,int>> es;
    for (int u = 0; u < N; u++) for (int v = u + 1; v < N; v++) if (h.has(u, v)) es.push_back({u, v});
    shuffle(es.begin(), es.end(), rng);
    for (int i = 0; i < r && i < (int)es.size(); i++) h.del(es[i].first, es[i].second);
    maximalize(h, rng);
    return h;
}

static mutex mtx;
static int gbest = -1;
static string gbestg6;

// ---- the useful formulation: maximise bip INSIDE the region {dist >= DMIN}. ----
// {dist >= DMIN} is a huge region (a random maximal triangle-free graph is far
// from every blow-up), while {bip >= TARGET} is tiny, so this is the direction
// that can be searched.  DMIN is swept upward from the outside.
static int DMIN = 0;

static void worker2(int seed, int iters) {
    mt19937 rng(seed);
    G g = seed_random(rng);
    int cd = distub(g, rng, 6);
    while (cd < DMIN) { g = seed_random(rng); cd = distub(g, rng, 6); }
    int cb = bip(g, -1);
    double T0 = 2.5;
    int stall = 0;
    for (int it = 0; it < iters; it++) {
        double T = T0 * (1.0 - double(it % 6000) / 6000.0) + 0.10;
        G h;
        if (rng() % 4) h = kick(g, rng, 1 + (int)(rng() % 4));
        else {
            h = g; int u = rng() % N, v = rng() % N;
            if (u == v) continue;
            if (h.has(u, v)) h.del(u, v);
            else { if (h.adj[u] & h.adj[v]) continue; h.add(u, v); }
        }
        int nd = distub(h, rng, 4);
        if (nd < DMIN) { stall++; continue; }            // stay in the far region
        int nb = bip(h, -1);
        int delta = nb - cb;
        if (delta >= 0 || exp(delta / T) > double(rng()) / 4294967296.0) {
            g = h; cb = nb; cd = nd;
            if (cb >= TARGET) {
                int dd = distub(g, rng, 80);
                if (dd >= DMIN) {
                    lock_guard<mutex> lk(mtx);
                    if (dd > gbest) {
                        gbest = dd; gbestg6 = g6(g);
                        printf("N=%d bip=%d distUB=%d |E|=%d %s\n", N, cb, dd, g.edges(), gbestg6.c_str());
                        fflush(stdout);
                    }
                }
            }
            stall = 0;
        } else stall++;
        if (stall > 4000) {
            stall = 0;
            do { g = seed_random(rng); cd = distub(g, rng, 6); } while (cd < DMIN);
            cb = bip(g, -1);
        }
    }
}

// score = 1000*min(bip,TARGET) + dist : climb bip first, then push distance.
static int score_of(const G& g, mt19937& rng, int restarts, int* bipout, int* dout) {
    int b = bip(g, -1);
    int d = distub(g, rng, restarts);
    if (bipout) *bipout = b;
    if (dout) *dout = d;
    return 1000 * min(b, TARGET) + d;
}

static void worker(int seed, int iters) {
    mt19937 rng(seed);
    G g = seed_blowup(rng);
    maximalize(g, rng);
    int cb, cd;
    int cur = score_of(g, rng, 4, &cb, &cd);
    double Temp0 = 260.0;
    int stall = 0;
    for (int it = 0; it < iters; it++) {
        double Temp = Temp0 * (1.0 - double(it % 8000) / 8000.0) + 12.0;
        G h;
        if (rng() % 4) h = kick(g, rng, 1 + (int)(rng() % 4));
        else {                                        // single toggle
            h = g; int u = rng() % N, v = rng() % N;
            if (u == v) continue;
            if (h.has(u, v)) h.del(u, v);
            else { if (h.adj[u] & h.adj[v]) continue; h.add(u, v); }
        }
        int nb, nd;
        int ns = score_of(h, rng, 3, &nb, &nd);
        int delta = ns - cur;
        if (delta >= 0 || exp(delta / Temp) > double(rng()) / 4294967296.0) {
            g = h; cur = ns; cb = nb; cd = nd;
            if (cb >= TARGET) {
                int dd = distub(g, rng, 60);
                if (dd > gbest) {
                    lock_guard<mutex> lk(mtx);
                    if (dd > gbest) {
                        gbest = dd; gbestg6 = g6(g);
                        printf("N=%d bip=%d distUB=%d |E|=%d %s\n", N, cb, dd, g.edges(), gbestg6.c_str());
                        fflush(stdout);
                    }
                }
                stall = 0;
            } else stall++;
        } else stall++;
        if (stall > 6000) {
            stall = 0;
            g = (rng() % 2) ? seed_random(rng) : seed_blowup(rng);
            maximalize(g, rng);
            cur = score_of(g, rng, 4, &cb, &cd);
        }
    }
}

int main(int argc, char** argv) {
    if (argc > 1) N = atoi(argv[1]);
    if (argc > 2) TARGET = atoi(argv[2]);
    int iters = (argc > 3) ? atoi(argv[3]) : 20000;
    int nthr = (argc > 4) ? atoi(argv[4]) : 8;
    DMIN = (argc > 5) ? atoi(argv[5]) : 0;
    FULL = (N == 32) ? 0xffffffffu : ((1u << N) - 1u);
    printf("# N=%d TARGET bip>=%d iters=%d threads=%d DMIN=%d\n", N, TARGET, iters, nthr, DMIN);
    vector<thread> th;
    for (int t = 0; t < nthr; t++)
        th.emplace_back(DMIN > 0 ? worker2 : worker, 1234 + 7919 * t, iters);
    for (auto& x : th) x.join();
    printf("# BEST dist=%d %s\n", gbest, gbestg6.c_str());
    return 0;
}
