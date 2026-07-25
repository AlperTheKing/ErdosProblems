// h4_maxtf.cpp -- read graph6 from stdin, keep MAXIMAL triangle-free graphs,
// compute bip = |E| - maxcut EXACTLY by Gray-code enumeration of all 2^(n-1) cuts.
//
// Sound because bip is monotone under triangle-free edge addition (lemma L1):
//   maxcut(G+e) <= maxcut(G)+1  =>  bip(G+e) >= bip(G),
// so max bip over triangle-free graphs on n vertices is attained at a maximal one.
//
// build: clang++ -O3 -march=native -std=c++17 h4_maxtf.cpp -o h4_maxtf.exe
// usage: geng -t -c 13 | h4_maxtf.exe [minbip_to_print]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>

static inline int popc(uint32_t x) { return __builtin_popcount(x); }

int n;
uint32_t adj[32];

static bool decode(const char* s) {
    int len = (int)strlen(s);
    while (len && (s[len-1]=='\n' || s[len-1]=='\r')) len--;
    if (len <= 0) return false;
    n = s[0] - 63;
    if (n < 1 || n > 30) return false;
    for (int i = 0; i < n; i++) adj[i] = 0;
    int p = 1, bit = 0; unsigned cur = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            if (bit == 0) { if (p >= len) return false; cur = (unsigned)(s[p++] - 63); bit = 6; }
            bit--;
            if ((cur >> bit) & 1u) { adj[i] |= 1u<<j; adj[j] |= 1u<<i; }
        }
    return true;
}

static bool triangle_free() {
    for (int i = 0; i < n; i++) {
        uint32_t a = adj[i] & ~((1u<<(i+1))-1u);
        while (a) { int j = __builtin_ctz(a); a &= a-1; if (adj[i] & adj[j]) return false; }
    }
    return true;
}

static bool maximal() {
    for (int i = 0; i < n; i++)
        for (int j = i+1; j < n; j++)
            if (!((adj[i]>>j)&1u) && !(adj[i] & adj[j])) return false;
    return true;
}

static int maxcut_exact() {
    int deg[32];
    for (int i = 0; i < n; i++) deg[i] = popc(adj[i]);
    uint32_t S = 0; int cut = 0, best = 0;
    uint32_t lim = 1u << (n-1);
    for (uint32_t k = 1; k < lim; k++) {
        int v = __builtin_ctz(k) + 1;
        int a = popc(adj[v] & S);
        if ((S>>v)&1u) { cut += 2*a - deg[v]; S &= ~(1u<<v); }
        else           { cut += deg[v] - 2*a; S |=  (1u<<v); }
        if (cut > best) best = cut;
    }
    return best;
}

int main(int argc, char** argv) {
    int printmin = (argc > 1) ? atoi(argv[1]) : 1000000;
    const char* dumpf = (argc > 2) ? argv[2] : nullptr;
    FILE* fd = dumpf ? fopen(dumpf, "w") : nullptr;
    int mindeg = (argc > 3) ? atoi(argv[3]) : 0;
    char buf[512];
    uint64_t total = 0, nmax = 0;
    int best = -1;
    std::vector<std::string> bestg;
    while (fgets(buf, sizeof buf, stdin)) {
        if (buf[0] == '\0' || buf[0] == '>') continue;
        if (!decode(buf)) continue;
        total++;
        if (!triangle_free()) continue;
        if (!maximal()) continue;
        {int md=99; for(int i=0;i<n;i++){int d=popc(adj[i]); if(d<md) md=d;} if(md<mindeg) continue;}
        nmax++;
        if (fd) { std::string s2(buf); while(!s2.empty()&&(s2.back()=='\n'||s2.back()=='\r')) s2.pop_back(); fprintf(fd, "%s\n", s2.c_str()); }
        int m = 0; for (int i = 0; i < n; i++) m += popc(adj[i]); m /= 2;
        int b = m - maxcut_exact();
        if (b > best) { best = b; bestg.clear(); }
        if (b == best) { if (bestg.size() < 40) { std::string s(buf); while(!s.empty()&&(s.back()=='\n'||s.back()=='\r')) s.pop_back(); bestg.push_back(s); } }
        if (b >= printmin) {
            std::string s(buf); while(!s.empty()&&(s.back()=='\n'||s.back()=='\r')) s.pop_back();
            printf("HIT bip=%d m=%d g6=%s\n", b, m, s.c_str());
        }
    }
    printf("n=%d read=%llu maximal_tf=%llu max_bip=%d\n", n,
           (unsigned long long)total, (unsigned long long)nmax, best);
    for (auto& s : bestg) printf("  extremal %s\n", s.c_str());
    if (fd) fclose(fd);
    return 0;
}
