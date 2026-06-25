// Multithreaded moment-block precompute M^sigma(H) for k-root types with s=2 free flag vertices
// (flags on k+2 vertices). Matches flag_sdp.P_sigma. M[i][j] = #{ordered R inducing sigma, disjoint
// 2-subsets S1,S2 : flag(R,S1)=i, flag(R,S2)=j}. Flag index via a 15-bit canonical key (roots fixed,
// 2 free verts in min order) -> index map passed from Python. Parallel over graphs (std::thread).
#include <cstdio>
#include <cstdint>
#include <vector>
#include <thread>
#include <algorithm>
#ifdef _WIN32
#include <io.h>
#include <fcntl.h>
#endif
using namespace std;

static int N, K, TT, NG, NTH, KEYBITS;
static vector<vector<uint32_t>> ADJ;     // ADJ[g][u] neighbor bitmask
static uint32_t ASIG[16];
static vector<int> KEYMAP;               // [1<<KEYBITS] -> flag index (-1)
static vector<double> Mall;              // NG * TT*TT

// 6-vertex (k+2) canonical key for flag (R[0..K-1], f0, f1): roots fixed positions 0..K-1, free 4,5.
// pairs ordered (i<j) over the M=K+2 positions. Try (f0,f1) and (f1,f0), take min key.
static inline int flagkey(const vector<uint32_t>& adj, const int* R, int f0, int f1) {
    int M = K + 2;
    int verts0[16], verts1[16];
    for (int i = 0; i < K; i++) { verts0[i] = R[i]; verts1[i] = R[i]; }
    verts0[K] = f0; verts0[K + 1] = f1;
    verts1[K] = f1; verts1[K + 1] = f0;
    int key0 = 0, key1 = 0, bit = 0;
    for (int i = 0; i < M; i++)
        for (int j = i + 1; j < M; j++) {
            if ((adj[verts0[i]] >> verts0[j]) & 1) key0 |= (1 << bit);
            if ((adj[verts1[i]] >> verts1[j]) & 1) key1 |= (1 << bit);
            bit++;
        }
    int key = key0 < key1 ? key0 : key1;
    return KEYMAP[key];
}

static void rec(const vector<uint32_t>& adj, int depth, int* R, uint32_t used, double* Mx) {
    if (depth == K) {
        int rest[16], m = 0;
        for (int w = 0; w < N; w++) if (!((used >> w) & 1)) rest[m++] = w;
        // flag index for each 2-subset of rest
        int nsub = m * (m - 1) / 2;
        static thread_local vector<int> idx; idx.assign(nsub, 0);
        static thread_local vector<int> sa, sb; sa.assign(nsub, 0); sb.assign(nsub, 0);
        int c = 0;
        for (int i = 0; i < m; i++)
            for (int j = i + 1; j < m; j++) {
                idx[c] = flagkey(adj, R, rest[i], rest[j]); sa[c] = i; sb[c] = j; c++;
            }
        for (int a = 0; a < nsub; a++) {
            int ia = idx[a]; if (ia < 0) continue;
            for (int b = 0; b < nsub; b++) {
                int ib = idx[b]; if (ib < 0) continue;
                // S1, S2 must be disjoint (no shared vertex)
                if (sa[a] == sa[b] || sa[a] == sb[b] || sb[a] == sa[b] || sb[a] == sb[b]) continue;
                Mx[ia * TT + ib] += 1.0;
            }
        }
        return;
    }
    for (int v = 0; v < N; v++) {
        if ((used >> v) & 1) continue;
        uint32_t av = adj[v];
        bool ok = true; uint32_t want = ASIG[depth];
        for (int a = 0; a < depth; a++) { if (((want >> a) & 1) != ((av >> R[a]) & 1)) { ok = false; break; } }
        if (!ok) continue;
        R[depth] = v; rec(adj, depth + 1, R, used | (1u << v), Mx);
    }
}

static void worker(int g0, int g1) {
    int R[16];
    for (int g = g0; g < g1; g++) rec(ADJ[g], 0, R, 0u, &Mall[(size_t)g * TT * TT]);
}

int main(int argc, char** argv) {
#ifdef _WIN32
    _setmode(_fileno(stdin), _O_BINARY);
#endif
    const char* outf = argv[1]; NTH = argc > 2 ? atoi(argv[2]) : 32;
    fread(&N, 4, 1, stdin); fread(&K, 4, 1, stdin); fread(&TT, 4, 1, stdin); fread(&NG, 4, 1, stdin);
    KEYBITS = (K + 2) * (K + 1) / 2;
    fread(ASIG, 4, K, stdin);
    KEYMAP.assign((size_t)1 << KEYBITS, -1);
    fread(KEYMAP.data(), 4, (size_t)1 << KEYBITS, stdin);
    ADJ.assign(NG, vector<uint32_t>(N));
    for (int g = 0; g < NG; g++) fread(ADJ[g].data(), 4, N, stdin);
    Mall.assign((size_t)NG * TT * TT, 0.0);
    int nth = min(NTH, max(1, NG)); vector<thread> th; int chunk = (NG + nth - 1) / nth;
    for (int t = 0; t < nth; t++) { int a = t * chunk, b = min(NG, a + chunk); if (a < b) th.emplace_back(worker, a, b); }
    for (auto& x : th) x.join();
    // chunked write: a single fwrite > 2GB is truncated on Windows CRT, so write in <512MB blocks
    FILE* f = fopen(outf, "wb");
    size_t total = (size_t)NG * TT * TT;          // number of doubles
    size_t pos = 0; const size_t BLK = 1u << 26;  // 2^26 doubles = 512MB per call
    while (pos < total) {
        size_t cnt = (total - pos < BLK) ? (total - pos) : BLK;
        size_t w = fwrite(Mall.data() + pos, 8, cnt, f);
        if (w != cnt) { fclose(f); return 2; }    // signal short write
        pos += cnt;
    }
    fclose(f);
    return 0;
}
