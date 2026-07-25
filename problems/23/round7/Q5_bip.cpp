// Q5: exact bip(G) = min over cuts of #monochromatic edges, by exhaustive
// enumeration of all 2^(N-1) cuts.  Integer arithmetic only.
// usage: Q5_bip.exe <graph6>            (N <= 34, 8 threads)
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <algorithm>
using namespace std;

int N;
vector<uint64_t> amask;

static void decode(const string &s) {
    vector<int> d;
    for (char c : s) d.push_back((int)c - 63);
    N = d[0];
    vector<int> bits;
    for (size_t i = 1; i < d.size(); i++)
        for (int k = 5; k >= 0; k--) bits.push_back((d[i] >> k) & 1);
    amask.assign(N, 0);
    int idx = 0;
    for (int j = 1; j < N; j++)
        for (int i = 0; i < j; i++) {
            if (bits[idx]) { amask[i] |= 1ULL << j; amask[j] |= 1ULL << i; }
            idx++;
        }
}

int main(int argc, char **argv) {
    if (argc < 2) { printf("need graph6\n"); return 1; }
    decode(argv[1]);
    uint64_t full = (N == 64) ? ~0ULL : ((1ULL << N) - 1);
    long long E = 0;
    for (int v = 0; v < N; v++) E += __builtin_popcountll(amask[v]);
    E /= 2;
    uint64_t total = 1ULL << (N - 1);
    int T = 8;
    vector<int> best(T, 1 << 30);
    vector<uint64_t> bestS(T, 0);
    vector<thread> th;
    for (int t = 0; t < T; t++) {
        th.emplace_back([&, t]() {
            int bb = 1 << 30; uint64_t bs = 0;
            for (uint64_t m = t; m < total; m += T) {
                uint64_t S = m << 1;              // vertex 0 pinned to side 0
                uint64_t C = full ^ S;
                int tot = 0;
                for (int v = 0; v < N; v++) {
                    uint64_t side = ((S >> v) & 1) ? S : C;
                    tot += __builtin_popcountll(amask[v] & side);
                }
                tot >>= 1;
                if (tot < bb) { bb = tot; bs = S; }
            }
            best[t] = bb; bestS[t] = bs;
        });
    }
    for (auto &x : th) x.join();
    int bb = 1 << 30; uint64_t bs = 0;
    for (int t = 0; t < T; t++) if (best[t] < bb) { bb = best[t]; bs = bestS[t]; }
    printf("N=%d E=%lld bip=%d cutmask=%llu\n", N, E, bb, (unsigned long long)bs);
    return 0;
}
