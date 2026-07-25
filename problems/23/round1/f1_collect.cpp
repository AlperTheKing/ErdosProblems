// Collect ALL maximal triangle-free graphs on n vertices with bip >= thr.
// build: clang++ -O2 -std=c++17 -o f1_collect.exe f1_collect.cpp
// usage: geng -tcq N | f1_collect N THR
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <iostream>

int main(int argc, char **argv) {
    int n = atoi(argv[1]);
    int thr = atoi(argv[2]);
    std::ios::sync_with_stdio(false);
    std::string line;
    uint32_t adj[32];
    const uint32_t FULL = (1u << n) - 1u;
    long long found = 0;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        for (int i = 0; i < n; i++) adj[i] = 0;
        size_t ci = 1; int cur = 0, have = 0;
        for (int j = 1; j < n; j++)
            for (int i = 0; i < j; i++) {
                if (have == 0) { cur = line[ci++] - 63; have = 6; }
                int b = (cur >> (have - 1)) & 1; have--;
                if (b) { adj[i] |= 1u << j; adj[j] |= 1u << i; }
            }
        bool ok = true;
        for (int i = 0; i < n && ok; i++)
            for (int j = i + 1; j < n; j++)
                if (!((adj[i] >> j) & 1) && (adj[i] & adj[j]) == 0) { ok = false; break; }
        if (!ok) continue;
        int m = 0;
        for (int i = 0; i < n; i++) m += __builtin_popcount(adj[i]);
        m /= 2;
        int bestcut = 0;
        for (uint32_t s = 0; s < (1u << (n - 1)); s++) {
            uint32_t S = (s << 1) | 1u; int cut = 0; uint32_t t = S;
            while (t) { int v = __builtin_ctz(t); t &= t - 1; cut += __builtin_popcount(adj[v] & ~S & FULL); }
            if (cut > bestcut) bestcut = cut;
        }
        if (m - bestcut >= thr) { printf("%s %d %d\n", line.c_str(), m, m - bestcut); ++found; }
    }
    fprintf(stderr, "found %lld\n", found);
    return 0;
}
