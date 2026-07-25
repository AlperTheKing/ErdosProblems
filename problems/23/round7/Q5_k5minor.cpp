// Q5: decide whether a graph has a K5 minor, and whether it has an ODD-K5 minor
// (all-negative signature), by exhaustive enumeration of branch-set assignments.
//   usage: Q5_k5minor.exe <graph6>          (N <= 14 practical)
// Assignment: every vertex -> one of 5 branch sets or 5 = unused.
// Symmetry reduction: the branch sets are required to appear in order of their
// smallest vertex.
// For the ODD test we enumerate, per branch set, all 2-colourings p of the set
// whose bichromatic edges span it connectedly (= proper 2-colourings of some
// spanning tree), and all choices of linking edges; the contracted signed K5 has
// sigma'(ij) = (-1)^(1 + p(u) + p(v)) on a linking edge uv, and it is an ODD-K5
// iff every triangle has product -1.
#include <cstdio>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

int N;
vector<uint32_t> A;                 // adjacency bitmasks

static void decode(const string &s) {
    vector<int> d;
    for (char c : s) d.push_back((int)c - 63);
    N = d[0];
    vector<int> bits;
    for (size_t i = 1; i < d.size(); i++)
        for (int k = 5; k >= 0; k--) bits.push_back((d[i] >> k) & 1);
    A.assign(N, 0);
    int idx = 0;
    for (int j = 1; j < N; j++)
        for (int i = 0; i < j; i++) {
            if (bits[idx]) { A[i] |= 1u << j; A[j] |= 1u << i; }
            idx++;
        }
}

static bool connectedMask(uint32_t m) {
    if (!m) return false;
    int s = __builtin_ctz(m);
    uint32_t seen = 1u << s, frontier = 1u << s;
    while (frontier) {
        uint32_t nxt = 0;
        uint32_t f = frontier;
        while (f) { int v = __builtin_ctz(f); f &= f - 1; nxt |= A[v] & m & ~seen; }
        seen |= nxt;
        frontier = nxt;
    }
    return seen == m;
}

// all 2-colourings p of branch set m (as bitmask of the "p=1" vertices) such
// that the bichromatic edges of m span m connectedly
static void colourings(uint32_t m, vector<uint32_t> &out) {
    out.clear();
    vector<int> vs;
    uint32_t t = m;
    while (t) { vs.push_back(__builtin_ctz(t)); t &= t - 1; }
    int k = vs.size();
    for (int c = 0; c < (1 << k); c++) {
        uint32_t p = 0;
        for (int i = 0; i < k; i++) if (c >> i & 1) p |= 1u << vs[i];
        // connectivity of the bichromatic subgraph on m
        int s = vs[0];
        uint32_t seen = 1u << s, frontier = 1u << s;
        while (frontier) {
            uint32_t nxt = 0, f = frontier;
            while (f) {
                int v = __builtin_ctz(f); f &= f - 1;
                uint32_t cand = A[v] & m & ~seen;
                uint32_t opp = ((p >> v) & 1) ? (m & ~p) : p;   // opposite colour
                nxt |= cand & opp;
            }
            seen |= nxt; frontier = nxt;
        }
        if (seen == m) out.push_back(p);
    }
}

int main(int argc, char **argv) {
    if (argc < 2) { printf("need graph6\n"); return 1; }
    decode(argv[1]);
    long long E = 0;
    for (int v = 0; v < N; v++) E += __builtin_popcountll(A[v]);
    E /= 2;
    printf("N=%d E=%lld\n", N, E);

    long long total = 1; for (int i = 0; i < N; i++) total *= 6;
    vector<int> asg(N, 5);
    bool foundK5 = false, foundOdd = false;
    vector<uint32_t> B(5);
    long long checked = 0;

    // iterate assignments in base 6 with the canonical-order restriction
    bool early = (argc > 2 && string(argv[2]) == "-e");
    for (long long code = 0; code < total; code++) {
        if (early && foundOdd) break;
        long long c = code;
        for (int i = 0; i < N; i++) { asg[i] = c % 6; c /= 6; }
        // canonical: first occurrence order of labels 0..4 is increasing
        int nextlab = 0; bool okc = true;
        for (int i = 0; i < N && okc; i++)
            if (asg[i] != 5) {
                if (asg[i] > nextlab) okc = false;
                else if (asg[i] == nextlab) nextlab++;
            }
        if (!okc || nextlab < 5) continue;
        for (int i = 0; i < 5; i++) B[i] = 0;
        for (int i = 0; i < N; i++) if (asg[i] != 5) B[asg[i]] |= 1u << i;
        bool ok = true;
        for (int i = 0; i < 5 && ok; i++) if (!connectedMask(B[i])) ok = false;
        if (!ok) continue;
        // pairwise adjacency; collect linking edges
        vector<vector<pair<int,int>>> links(10);
        int idx = 0;
        for (int i = 0; i < 5 && ok; i++)
            for (int j = i + 1; j < 5 && ok; j++) {
                uint32_t bi = B[i];
                bool any = false;
                while (bi) {
                    int u = __builtin_ctz(bi); bi &= bi - 1;
                    uint32_t nb = A[u] & B[j];
                    while (nb) { int v = __builtin_ctz(nb); nb &= nb - 1;
                                 links[idx].push_back({u, v}); any = true; }
                }
                if (!any) ok = false;
                idx++;
            }
        if (!ok) continue;
        checked++;
        if (!foundK5) {
            foundK5 = true;
            printf("K5 minor: ");
            for (int i = 0; i < 5; i++) {
                printf("B%d={", i + 1);
                uint32_t b = B[i];
                while (b) { printf("%d%s", __builtin_ctz(b), (b & (b - 1)) ? "," : ""); b &= b - 1; }
                printf("} ");
            }
            printf("\n");
        }
        if (foundOdd) continue;
        // odd test: enumerate colourings of each branch set and linking choices
        vector<vector<uint32_t>> cols(5);
        for (int i = 0; i < 5; i++) colourings(B[i], cols[i]);
        vector<int> ci(5, 0);
        bool done = false;
        while (!done) {
            uint32_t P = 0;
            for (int i = 0; i < 5; i++) P |= cols[i][ci[i]];
            // for each pair choose a linking edge; the sign is
            // (-1)^(1+p(u)+p(v)); try all combinations (bounded, small)
            vector<int> li(10, 0);
            bool d2 = false;
            while (!d2) {
                int sg[5][5];
                int t = 0;
                for (int i = 0; i < 5; i++)
                    for (int j = i + 1; j < 5; j++) {
                        auto e = links[t][li[t]];
                        int s = 1 + ((P >> e.first) & 1) + ((P >> e.second) & 1);
                        sg[i][j] = sg[j][i] = (s % 2) ? -1 : 1;
                        t++;
                    }
                bool allodd = true;
                for (int i = 0; i < 5 && allodd; i++)
                    for (int j = i + 1; j < 5 && allodd; j++)
                        for (int k = j + 1; k < 5 && allodd; k++)
                            if (sg[i][j] * sg[j][k] * sg[i][k] != -1) allodd = false;
                if (allodd) {
                    foundOdd = true;
                    printf("ODD-K5 minor FOUND: branch sets ");
                    for (int i = 0; i < 5; i++) {
                        printf("B%d={", i + 1);
                        uint32_t b = B[i];
                        while (b) { printf("%d%s", __builtin_ctz(b), (b & (b - 1)) ? "," : ""); b &= b - 1; }
                        printf("} ");
                    }
                    printf(" p-mask=%u\n", P);
                    d2 = true; done = true; break;
                }
                // advance li
                int q = 0;
                while (q < 10) {
                    li[q]++;
                    if (li[q] < (int)links[q].size()) break;
                    li[q] = 0; q++;
                }
                if (q == 10) d2 = true;
            }
            if (done) break;
            int q = 0;
            while (q < 5) {
                ci[q]++;
                if (ci[q] < (int)cols[q].size()) break;
                ci[q] = 0; q++;
            }
            if (q == 5) done = true;
        }
    }
    printf("branch-set configurations checked: %lld\n", checked);
    printf("K5 minor: %s\n", foundK5 ? "YES" : "NO");
    printf("ODD-K5 minor: %s\n", foundOdd ? "YES" : "NO");
    return 0;
}
