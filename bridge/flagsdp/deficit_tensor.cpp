// Multithreaded deficit-tensor precompute for higher-k profile cuts (matches flag_cutgen.precompute_type).
// For each order-N triangle-free graph and rooted type sigma=(k,Asig): accumulate
//   Sraw = #ordered k-tuples R inducing sigma,
//   Eraw[a][b] = # (inducing R, non-root edge pair u<v with profile classes {a<=b}).
// Python normalizes: E = Eraw/(nk*Cnmk2), S = Sraw/nk.  Incremental induce-check prunes the k-tuple tree.
// I/O: binary stdin-> compute -> binary file. Parallel over graphs via std::thread (<=64).
#include <cstdio>
#include <cstdint>
#include <vector>
#include <thread>
#include <cstring>
#include <algorithm>
#ifdef _WIN32
#include <io.h>
#include <fcntl.h>
#endif
using namespace std;

static int N, K, NC, NG, NTH;
static vector<vector<uint32_t>> ADJ;     // ADJ[g][u] = neighbor bitmask
static uint32_t ASIG[16];                // root-root adjacency (ASIG[a] bit b = edge a-b)
static vector<int> PROFMAP;              // [1<<K] -> class index (-1 if none)
static vector<double> Eall;              // NG * NC*NC
static vector<double> Sall;              // NG

static void rec(const vector<uint32_t>& adj, int depth, int* R, uint32_t used, double* E, double& S) {
    if (depth == K) {
        int cls[32], nr[32], m = 0;
        for (int w = 0; w < N; w++) {
            if ((used >> w) & 1) continue;
            uint32_t prof = 0;
            uint32_t aw = adj[w];
            for (int i = 0; i < K; i++) if ((aw >> R[i]) & 1) prof |= (1u << i);
            nr[m] = w; cls[m] = PROFMAP[prof]; m++;
        }
        S += 1.0;
        for (int ui = 0; ui < m; ui++) {
            uint32_t au = adj[nr[ui]]; int cu = cls[ui];
            for (int vi = ui + 1; vi < m; vi++) {
                if ((au >> nr[vi]) & 1) {
                    int a = cu, b = cls[vi];
                    if (a > b) { int t = a; a = b; b = t; }
                    E[a * NC + b] += 1.0;
                }
            }
        }
        return;
    }
    for (int v = 0; v < N; v++) {
        if ((used >> v) & 1) continue;
        uint32_t av = adj[v];
        bool ok = true;
        uint32_t want = ASIG[depth];
        for (int a = 0; a < depth; a++) {
            int w = (want >> a) & 1;
            int h = (av >> R[a]) & 1;
            if (w != h) { ok = false; break; }
        }
        if (!ok) continue;
        R[depth] = v;
        rec(adj, depth + 1, R, used | (1u << v), E, S);
    }
}

static void worker(int g0, int g1) {
    int R[32];
    for (int g = g0; g < g1; g++) {
        double* E = &Eall[(size_t)g * NC * NC];
        double S = 0.0;
        rec(ADJ[g], 0, R, 0u, E, S);
        Sall[g] = S;
    }
}

int main(int argc, char** argv) {
#ifdef _WIN32
    _setmode(_fileno(stdin), _O_BINARY);
#endif
    const char* outf = argv[1];
    NTH = argc > 2 ? atoi(argv[2]) : 32;
    // read binary from stdin: N K NC NG (int32 each), then ASIG[K] (uint32), classmasks[NC] (uint32),
    //   then NG graphs each N uint32 adjacency rows.
    if (fread(&N, 4, 1, stdin) != 1) return 1;
    fread(&K, 4, 1, stdin); fread(&NC, 4, 1, stdin); fread(&NG, 4, 1, stdin);
    fread(ASIG, 4, K, stdin);
    vector<uint32_t> cmask(NC);
    fread(cmask.data(), 4, NC, stdin);
    PROFMAP.assign((size_t)1 << K, -1);
    for (int c = 0; c < NC; c++) PROFMAP[cmask[c]] = c;
    ADJ.assign(NG, vector<uint32_t>(N));
    for (int g = 0; g < NG; g++) fread(ADJ[g].data(), 4, N, stdin);
    Eall.assign((size_t)NG * NC * NC, 0.0);
    Sall.assign(NG, 0.0);
    int nth = min(NTH, max(1, NG));
    vector<thread> th;
    int chunk = (NG + nth - 1) / nth;
    for (int t = 0; t < nth; t++) {
        int a = t * chunk, b = min(NG, a + chunk);
        if (a < b) th.emplace_back(worker, a, b);
    }
    for (auto& x : th) x.join();
    FILE* f = fopen(outf, "wb");
    fwrite(Sall.data(), 8, NG, f);
    fwrite(Eall.data(), 8, (size_t)NG * NC * NC, f);
    fclose(f);
    return 0;
}
