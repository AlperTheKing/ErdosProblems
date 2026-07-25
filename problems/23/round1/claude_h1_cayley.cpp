// H1: exhaustive sweep of triangle-free Cayley graphs over arbitrary finite groups.
//
// For each group G (Cayley table read from file) enumerate every connection set S with
//   * S = S^{-1},  e not in S                        (undirected simple Cayley graph)
//   * for all s,t in S: s^{-1} t not in S            (<=> Cay(G,S) triangle-free)
//   * <S> = G                                        (connected; a disconnected Cayley graph is a
//                                                     disjoint union of Cayley graphs of a proper
//                                                     subgroup, which is swept at that order, and
//                                                     k copies of a graph with bip <= m^2/25 have
//                                                     bip <= k m^2/25 < (km)^2/25)
//   * 25|S| > 4n  and  5|S| <= 2n                    (degree window, see below)
//
// Degree window (both directions sound):
//   maxcut >= |E|/2 always, so bip <= |E|/2 = n d /4; to beat n^2/25 we need 25 d > 4 n.
//   Andrasfai-Erdos-Sos (1974): a triangle-free graph with min degree > 2n/5 is bipartite
//   (bip = 0), so a d-regular non-bipartite triangle-free graph has 5d <= 2n.
//
// Bipartite-subtree prune: Cay(G,S) is bipartite iff some homomorphism phi: G -> Z_2 is
//   identically 1 on S.  Classes are ordered so that phi-odd classes come last; when phi is 1
//   on the current S and on every remaining class the entire subtree has bip = 0 and is cut.
//
// Screening is SOUND-BY-CONSTRUCTION: a heuristic cut is a *lower* bound on maxcut, hence
//   bip_ub := |E| - maxcut_heur   is an UPPER bound on bip.
// Any S with bip_ub < target cannot violate.  Only survivors get an exact maxcut.
//
// Exact maxcut: n <= 30 -> Gray-code enumeration of all 2^(n-1) bipartitions (integers only).
//               n >  30 -> branch & bound on min #monochromatic edges with the disjoint
//                          placed-to-unplaced lower bound; node cap -> UNRESOLVED, graph dumped
//                          for exact CP-SAT verification.
//
// usage: claude_h1_cayley groups_<n>.txt [--top K] [--restarts R] [--exact-top E]
//                                        [--dump FILE] [--dumptop M] [--cap NODES] [--threads T]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
#include <thread>
#include <atomic>
#include <mutex>
using namespace std;

static int n;
static vector<int> Tab;      // n*n multiplication table, element 0 = identity
static vector<int> invv;
static vector<vector<int>> classes;         // inverse-closed classes {s} or {s,s^-1}
static vector<vector<char>> homs;           // nontrivial homomorphisms G -> Z_2
static vector<vector<char>> suffix_all1;
static int dmax, target;
static int RESTARTS = 6;
static int STORE_K = 3000;

// ---------------------------------------------------------------- exact maxcut, n<=30
static long long exhaustive_maxcut(int nn, const vector<uint32_t>& amask) {
    vector<int> deg(nn);
    for (int i = 0; i < nn; i++) deg[i] = __builtin_popcount(amask[i]);
    uint32_t S = 1u;
    long long cut = deg[0], best = cut;
    uint64_t lim = 1ull << (nn - 1);
    for (uint64_t k = 1; k < lim; k++) {
        int v = __builtin_ctzll(k) + 1;              // gray-code flip position (vertex 0 fixed)
        int a = __builtin_popcount(amask[v] & S);
        if (S >> v & 1) { cut += 2 * a - deg[v]; S &= ~(1u << v); }
        else            { cut += deg[v] - 2 * a; S |= (1u << v); }
        if (cut > best) best = cut;
    }
    return best;
}

// ---------------------------------------------------------------- exact min-mono BnB
struct BnB {
    int nn;
    const vector<vector<int>>* adj;
    vector<int> ord, pos;
    vector<int> c0, c1;
    int best;
    long long nodes, cap;
    bool capped;

    int run(int nn_, const vector<vector<int>>& adj_, int ub, long long cap_) {
        nn = nn_; adj = &adj_; best = ub; cap = cap_; nodes = 0; capped = false;
        ord.assign(nn, -1); pos.assign(nn, -1); c0.assign(nn, 0); c1.assign(nn, 0);
        vector<char> used(nn, 0); vector<int> cnt(nn, 0);
        for (int k = 0; k < nn; k++) {
            int bv = -1, bc = -1;
            for (int v = 0; v < nn; v++) if (!used[v] && cnt[v] > bc) { bc = cnt[v]; bv = v; }
            used[bv] = 1; ord[k] = bv; pos[bv] = k;
            for (int u : adj_[bv]) if (!used[u]) cnt[u]++;
        }
        for (int u : adj_[ord[0]]) c0[u]++;
        rec(1, 0);
        return best;
    }
    void rec(int k, int cur) {
        if (++nodes > cap) { capped = true; return; }
        if (k == nn) { if (cur < best) best = cur; return; }
        int lb = cur;
        for (int j = k; j < nn; j++) { int v = ord[j]; lb += (c0[v] < c1[v] ? c0[v] : c1[v]); }
        if (lb >= best) return;
        int v = ord[k];
        int first = (c0[v] <= c1[v]) ? 0 : 1;
        for (int t = 0; t < 2; t++) {
            int c = first ^ t;
            int add = c ? c1[v] : c0[v];
            if (cur + add >= best) continue;
            for (int u : (*adj)[v]) if (pos[u] > k) { if (c) c1[u]++; else c0[u]++; }
            rec(k + 1, cur + add);
            for (int u : (*adj)[v]) if (pos[u] > k) { if (c) c1[u]--; else c0[u]--; }
            if (capped) return;
        }
    }
};

// ---------------------------------------------------------------- heuristic maxcut (lower bd)
static long long heur_maxcut(int nn, int d, const vector<vector<int>>& adj, int restarts,
                             uint64_t& seed, vector<int>& col, vector<int>& same) {
    long long best = 0;
    auto rnd = [&]() { seed ^= seed << 13; seed ^= seed >> 7; seed ^= seed << 17; return seed; };
    long long E = (long long)nn * d / 2;
    for (int r = 0; r < restarts; r++) {
        for (int i = 0; i < nn; i++) col[i] = (int)(rnd() & 1);
        for (int i = 0; i < nn; i++) { int s = 0; for (int u : adj[i]) if (col[u] == col[i]) s++; same[i] = s; }
        for (int kick = 0; kick < 3; kick++) {
            bool improved = true;
            while (improved) {
                improved = false;
                for (int i = 0; i < nn; i++) if (2 * same[i] > d) {
                    col[i] ^= 1;
                    int s = 0;
                    for (int u : adj[i]) { if (col[u] == col[i]) { s++; same[u]++; } else same[u]--; }
                    same[i] = s; improved = true;
                }
            }
            long long mono = 0;
            for (int i = 0; i < nn; i++) mono += same[i];
            mono /= 2;
            if (E - mono > best) best = E - mono;
            if (kick == 2) break;
            for (int t = 0; t < 1 + nn / 8; t++) {
                int i = (int)(rnd() % nn);
                col[i] ^= 1;
                int s = 0;
                for (int u : adj[i]) { if (col[u] == col[i]) { s++; same[u]++; } else same[u]--; }
                same[i] = s;
            }
        }
    }
    return best;
}

// ---------------------------------------------------------------- worker
struct Cand { int bipub; vector<int> S; };

struct Worker {
    vector<int> curS; vector<char> inS;
    vector<Cand> store; int store_floor = 0; int runmax = -1000; bool trimmed = false;
    long long n_sets = 0, n_eval = 0;
    uint64_t seed;
    vector<vector<int>> adj;
    vector<int> col, same;
    vector<char> vis;

    void init(uint64_t s) {
        inS.assign(n, 0); curS.clear(); seed = s ? s : 0x9E3779B97F4A7C15ull;
        col.assign(n, 0); same.assign(n, 0); vis.assign(n, 0);
        adj.assign(n, vector<int>());
    }
    bool triangle_free() {
        for (size_t a = 0; a < curS.size(); a++)
            for (size_t b = 0; b < curS.size(); b++) {
                int x = Tab[(size_t)invv[curS[a]] * n + curS[b]];
                if (x != 0 && inS[x]) return false;
            }
        return true;
    }
    bool generates() {
        fill(vis.begin(), vis.end(), 0);
        vis[0] = 1; int cnt = 1;
        vector<int> st; st.push_back(0);
        while (!st.empty()) {
            int a = st.back(); st.pop_back();
            for (int s : curS) { int b = Tab[(size_t)a * n + s]; if (!vis[b]) { vis[b] = 1; cnt++; st.push_back(b); } }
        }
        return cnt == n;
    }
    bool subtree_all_bipartite(size_t ci) {
        for (size_t h = 0; h < homs.size(); h++) {
            if (!suffix_all1[h][ci]) continue;
            bool ok = true;
            for (int s : curS) if (!homs[h][s]) { ok = false; break; }
            if (ok) return true;
        }
        return false;
    }
    void push_cand(int bipub) {
        if (bipub < store_floor) return;
        store.push_back({bipub, curS});
        if ((int)store.size() >= 2 * STORE_K) {
            nth_element(store.begin(), store.begin() + STORE_K, store.end(),
                        [](const Cand& a, const Cand& b) { return a.bipub > b.bipub; });
            store_floor = store[STORE_K].bipub;
            store.resize(STORE_K); trimmed = true;
        }
    }
    // bip(G) is monotone non-decreasing under edge addition (|E| grows by 1, maxcut by <=1),
    // so only connection sets MAXIMAL among triangle-free symmetric sets can be optimal.
    bool maximal() {
        for (size_t i = 0; i < classes.size(); i++) {
            if (inS[classes[i][0]]) continue;
            for (int s : classes[i]) { curS.push_back(s); inS[s] = 1; }
            bool tf = triangle_free();
            for (int s : classes[i]) { inS[s] = 0; curS.pop_back(); }
            if (tf) return false;
        }
        return true;
    }
    void evaluate() {
        int d = (int)curS.size();
        if (!maximal()) return;
        if (!generates()) return;
        n_eval++;
        for (int i = 0; i < n; i++) {
            adj[i].resize(d);
            for (int k = 0; k < d; k++) adj[i][k] = Tab[(size_t)i * n + curS[k]];
        }
        long long E = (long long)n * d / 2;
        long long mc = heur_maxcut(n, d, adj, RESTARTS, seed, col, same);
        int bipub = (int)(E - mc);
        if (bipub >= runmax && bipub >= store_floor) {
            long long mc2 = heur_maxcut(n, d, adj, 12 * RESTARTS, seed, col, same);
            if (mc2 > mc) bipub = (int)(E - mc2);
        }
        if (bipub > runmax) runmax = bipub;
        push_cand(bipub);
    }
    void dfs(size_t ci, int sz) {
        if (!homs.empty() && subtree_all_bipartite(ci)) return;
        bool anychild = false;
        for (size_t i = ci; i < classes.size(); i++) {
            int add = (int)classes[i].size();
            if (sz + add > dmax) continue;
            for (int s : classes[i]) { curS.push_back(s); inS[s] = 1; }
            if (triangle_free()) { anychild = true; n_sets++; dfs(i + 1, sz + add); }
            for (int s : classes[i]) { inS[s] = 0; curS.pop_back(); }
        }
        // some class with index >= ci is addable  =>  curS is not maximal  =>  by monotonicity
        // of bip it cannot be optimal; only leaves of the search tree are candidates, and
        // evaluate() re-verifies full maximality (classes with index < ci included).
        if (sz > 0 && !anychild) evaluate();
    }
};

// ---------------------------------------------------------------- helpers
static void compute_homs() {
    homs.clear();
    vector<int> gens;
    {
        vector<char> cur(n, 0); cur[0] = 1; int cnt = 1;
        while (cnt < n) {
            int pick = -1;
            for (int g = 1; g < n; g++) if (!cur[g]) { pick = g; break; }
            gens.push_back(pick);
            vector<char> visl(n, 0); visl[0] = 1; vector<int> st{0}; cnt = 1;
            while (!st.empty()) {
                int a = st.back(); st.pop_back();
                for (int s : gens) { int b = Tab[(size_t)a * n + s]; if (!visl[b]) { visl[b] = 1; cnt++; st.push_back(b); } }
            }
            cur = visl;
        }
    }
    int k = (int)gens.size();
    if (k > 20) return;
    vector<vector<int>> word(n);
    { vector<char> visl(n, 0); visl[0] = 1; vector<int> fr{0};
      while (!fr.empty()) { vector<int> nf;
        for (int a : fr) for (int t = 0; t < k; t++) { int b = Tab[(size_t)a * n + gens[t]];
            if (!visl[b]) { visl[b] = 1; word[b] = word[a]; word[b].push_back(t); nf.push_back(b); } }
        fr = nf; } }
    for (int mask = 1; mask < (1 << k); mask++) {
        vector<char> phi(n, 0);
        for (int g = 0; g < n; g++) { int v = 0; for (int t : word[g]) v ^= (mask >> t) & 1; phi[g] = (char)v; }
        bool ok = true;
        for (int a = 0; a < n && ok; a++)
            for (int b = 0; b < n; b++)
                if (phi[Tab[(size_t)a * n + b]] != (phi[a] ^ phi[b])) { ok = false; break; }
        if (ok) homs.push_back(phi);
    }
}

static string g6_of(const vector<int>& S) {
    string out; out += (char)(n + 63);
    vector<vector<char>> A(n, vector<char>(n, 0));
    for (int i = 0; i < n; i++) for (int s : S) A[i][Tab[(size_t)i * n + s]] = 1;
    int cur = 0, nb = 0;
    for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
        cur = (cur << 1) | A[i][j];
        if (++nb == 6) { out += (char)(cur + 63); cur = nb = 0; }
    }
    if (nb) out += (char)((cur << (6 - nb)) + 63);
    return out;
}

int main(int argc, char** argv) {
    const char* path = argv[1];
    const char* dumppath = nullptr;
    int EXACT_TOP = 400, DUMPTOP = 0;
    long long BNB_CAP = 40000000LL;
    int NTH = (int)thread::hardware_concurrency();
    if (NTH <= 0) NTH = 8;
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--top")) STORE_K = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--restarts")) RESTARTS = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--exact-top")) EXACT_TOP = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--dump")) dumppath = argv[++i];
        else if (!strcmp(argv[i], "--dumptop")) DUMPTOP = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--cap")) BNB_CAP = atoll(argv[++i]);
        else if (!strcmp(argv[i], "--threads")) NTH = atoi(argv[++i]);
    }
    FILE* f = fopen(path, "r");
    if (!f) { fprintf(stderr, "cannot open %s\n", path); return 1; }
    int ngroups, ord;
    if (fscanf(f, "%d %d", &ngroups, &ord) != 2) return 1;
    n = ord;
    dmax = (2 * n) / 5;
    target = (n * n) / 25 + 1;
    printf("order n=%d  groups=%d  threads=%d  degree window: %d <= d <= %d   need bip >= %d  (n^2/25 = %.2f)\n",
           n, ngroups, NTH, (4 * n) / 25 + 1, dmax, target, n * n / 25.0);

    int gbest = -1; vector<int> gbestS; string gbestname; int gtopub = -1;
    for (int gi = 0; gi < ngroups; gi++) {
        char name[256];
        if (fscanf(f, "%255s", name) != 1) return 1;
        Tab.assign((size_t)n * n, 0);
        for (size_t i = 0; i < (size_t)n * n; i++) { int v; if (fscanf(f, "%d", &v) != 1) return 1; Tab[i] = v; }
        invv.assign(n, 0);
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (Tab[(size_t)i * n + j] == 0) { invv[i] = j; break; }
        classes.clear();
        { vector<char> used(n, 0);
          for (int s = 1; s < n; s++) { if (used[s]) continue; used[s] = 1;
            if (invv[s] == s) classes.push_back({s});
            else { used[invv[s]] = 1; classes.push_back({s, invv[s]}); } } }
        compute_homs();
        {   vector<pair<unsigned long long, int>> key(classes.size());
            for (size_t i = 0; i < classes.size(); i++) {
                unsigned long long m = 0;
                for (size_t h = 0; h < homs.size() && h < 64; h++) if (homs[h][classes[i][0]]) m |= 1ull << h;
                key[i] = {m, (int)i};
            }
            sort(key.begin(), key.end());
            vector<vector<int>> nc(classes.size());
            for (size_t i = 0; i < key.size(); i++) nc[i] = classes[key[i].second];
            classes = nc;
            suffix_all1.assign(homs.size(), vector<char>(classes.size() + 1, 1));
            for (size_t h = 0; h < homs.size(); h++)
                for (int i = (int)classes.size() - 1; i >= 0; i--)
                    suffix_all1[h][i] = (char)(suffix_all1[h][i + 1] && homs[h][classes[i][0]]);
        }

        // ---- parallel enumeration: one task per choice of the first class
        int NC = (int)classes.size();
        vector<Worker> W(NTH);
        atomic<int> next_task(0);
        atomic<int> shared_runmax(-1000);
        vector<thread> th;
        for (int t = 0; t < NTH; t++) th.emplace_back([&, t]() {
            W[t].init(0x9E3779B97F4A7C15ull ^ (0x1234567ull * (t + 1)));
            for (;;) {
                int i = next_task.fetch_add(1);
                if (i >= NC) break;
                int rm = shared_runmax.load();
                if (rm > W[t].runmax) W[t].runmax = rm;
                int add = (int)classes[i].size();
                if (add > dmax) continue;
                for (int s : classes[i]) { W[t].curS.push_back(s); W[t].inS[s] = 1; }
                if (W[t].triangle_free()) { W[t].n_sets++; W[t].dfs(i + 1, add); }
                for (int s : classes[i]) { W[t].inS[s] = 0; W[t].curS.pop_back(); }
                int cur = shared_runmax.load();
                while (W[t].runmax > cur && !shared_runmax.compare_exchange_weak(cur, W[t].runmax)) {}
            }
        });
        for (auto& x : th) x.join();

        vector<Cand> store;
        bool trimmed = false;
        long long n_sets = 0, n_eval = 0;
        for (int t = 0; t < NTH; t++) {
            n_sets += W[t].n_sets; n_eval += W[t].n_eval; trimmed |= W[t].trimmed;
            for (auto& c : W[t].store) store.push_back(move(c));
            W[t].store.clear(); W[t].store.shrink_to_fit();
        }
        sort(store.begin(), store.end(), [](const Cand& a, const Cand& b) { return a.bipub > b.bipub; });
        if ((int)store.size() > STORE_K) { store.resize(STORE_K); trimmed = true; }
        int topub = store.empty() ? -1 : store[0].bipub;

        // ---- exact stage (parallel over the head of the list)
        int bestexact = -1; vector<int> bestS; atomic<int> unresolved(0);
        int lim = min((int)store.size(), EXACT_TOP);
        {
            vector<int> res(lim, -1);
            atomic<int> nxt(0), gb(-1);
            vector<thread> th2;
            for (int t = 0; t < NTH; t++) th2.emplace_back([&]() {
                for (;;) {
                    int i = nxt.fetch_add(1);
                    if (i >= lim) break;
                    if (store[i].bipub <= gb.load()) { res[i] = -2; continue; }  // dominated
                    const vector<int>& S = store[i].S;
                    int d = (int)S.size();
                    long long E = (long long)n * d / 2;
                    if (n <= 30) {
                        vector<uint32_t> am(n, 0);
                        for (int v = 0; v < n; v++) for (int s : S) am[v] |= 1u << Tab[(size_t)v * n + s];
                        res[i] = (int)(E - exhaustive_maxcut(n, am));
                    } else {
                        vector<vector<int>> adj(n, vector<int>(d));
                        for (int v = 0; v < n; v++) for (int k = 0; k < d; k++) adj[v][k] = Tab[(size_t)v * n + S[k]];
                        BnB b; int r = b.run(n, adj, store[i].bipub + 1, BNB_CAP);
                        if (b.capped) { unresolved.fetch_add(1); res[i] = -1; }
                        else res[i] = r;
                    }
                    int c = gb.load();
                    while (res[i] > c && !gb.compare_exchange_weak(c, res[i])) {}
                }
            });
            for (auto& x : th2) x.join();
            for (int i = 0; i < lim; i++) if (res[i] > bestexact) { bestexact = res[i]; bestS = store[i].S; }
        }
        bool proven = !trimmed && unresolved.load() == 0 &&
                      (lim == (int)store.size() || store[lim - 1].bipub <= bestexact);
        printf("  %-24s maxTF=%-9lld eval=%-8lld bip_ub_max=%-5d EXACT bip=%-5d d=%-3d %-20s%s%s\n",
               name, n_sets, n_eval, topub, bestexact, (int)bestS.size(),
               proven ? "[PROVEN family max]" : "[lower bd only]",
               (bestexact >= target || topub >= target) ? " *** CHECK ***" : "",
               unresolved.load() ? " [UNRESOLVED BnB]" : "");
        fflush(stdout);
        if (bestexact > gbest) { gbest = bestexact; gbestS = bestS; gbestname = name; }
        if (topub > gtopub) gtopub = topub;
        if (dumppath) {
            FILE* df = fopen(dumppath, "a");
            for (int m = 0; m < DUMPTOP && m < (int)store.size(); m++) {
                fprintf(df, "CAND %d %s d=%d bipub=%d %s S=", n, name,
                        (int)store[m].S.size(), store[m].bipub, g6_of(store[m].S).c_str());
                for (int s : store[m].S) fprintf(df, "%d,", s);
                fprintf(df, "\n");
            }
            if (!bestS.empty())
                fprintf(df, "BEST %d %s d=%d bip=%d %s\n", n, name, (int)bestS.size(), bestexact, g6_of(bestS).c_str());
            fclose(df);
        }
    }
    printf("ORDER %d BEST: exact bip=%d group=%s ratio=%.6f | max bip_ub over family = %d (need %d) -> %s\n",
           n, gbest, gbestname.c_str(), (double)gbest / (n * (double)n), gtopub, target,
           gtopub >= target ? "*** CANDIDATE SURVIVES SCREEN ***" : "NO VIOLATION (screen is an upper bound)");
    fclose(f);
    return 0;
}
