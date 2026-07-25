// Q1_indcut.cpp -- exact integer test of the "neighbourhood-of-an-independent-set" cut family.
//
// Reads graph6 lines on stdin (from nauty geng -t ...), n <= 16.
// For every graph computes, in exact integers:
//   bip(G)      = |E| - maxcut(G)                       (brute force over all 2^(n-1) cuts, Gray code)
//   fam(G)      = min over independent sets I of  mono( N(I) )   (N(I) = union of neighbourhoods)
//   c5(G)       = number of 5-cycles = tr(A^5)/10        (valid because G is triangle-free)
// and reports
//   (A) graphs with fam(G) > bip(G)                      -- family is not always optimal
//   (B) graphs with 25*fam(G) > n*n                      -- family fails the 1/25 target
//   (C) max of 25*bip/n^2 and max of bip^5/c5^2
//
// Build: clang++ -O3 -march=native -std=c++17 Q1_indcut.cpp -o Q1_indcut.exe
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <algorithm>
#include <cmath>

static inline int pc(uint32_t x){ return __builtin_popcount(x); }

struct Graph {
    int n;
    uint32_t adj[16];
    int deg[16];
    int m;
};

static bool parse_g6(const std::string& s, Graph& g){
    if(s.empty()) return false;
    size_t p = 0;
    int n = (int)s[p++] - 63;
    if(n < 0 || n > 16) return false;
    g.n = n;
    for(int i=0;i<16;i++){ g.adj[i]=0; g.deg[i]=0; }
    int bitpos = 0;
    int need = n*(n-1)/2;
    int val = 0, have = 0;
    for(int k=0;k<need;k++){
        if(have==0){ if(p>=s.size()) return false; val = (int)s[p++]-63; have = 6; }
        int bit = (val >> (have-1)) & 1;
        have--;
        if(bit){
            // k-th bit is edge (i,j) with j>i, column-major order: for j=1..n-1, i=0..j-1
            // recover i,j from k
            int j = 1; int base = 0;
            while(base + j <= k){ base += j; j++; }
            int i = k - base;
            g.adj[i] |= (1u<<j);
            g.adj[j] |= (1u<<i);
        }
        (void)bitpos;
    }
    g.m = 0;
    for(int i=0;i<n;i++){ g.deg[i] = pc(g.adj[i]); g.m += g.deg[i]; }
    g.m /= 2;
    return true;
}

// exact bip via Gray-code over subsets containing vertex 0 in the complement
static int bip_exact(const Graph& g){
    int n = g.n;
    uint32_t total = 1u << (n-1);           // subsets of {1..n-1}
    int cut = 0;                            // cut(S) for current S
    int best = g.m;                         // S = empty -> cut 0 -> mono = m
    uint32_t S = 0;
    for(uint32_t i=1;i<total;i++){
        uint32_t gray = i ^ (i>>1);
        uint32_t prev = (i-1) ^ ((i-1)>>1);
        uint32_t diff = gray ^ prev;
        int v = __builtin_ctz(diff) + 1;    // vertices 1..n-1
        if(gray & diff){                    // adding v
            cut += g.deg[v] - 2*pc(g.adj[v] & S);
            S |= (1u<<v);
        } else {                            // removing v
            S &= ~(1u<<v);
            cut -= g.deg[v] - 2*pc(g.adj[v] & S);
        }
        int mono = g.m - cut;
        if(mono < best) best = mono;
    }
    return best;
}

static inline int mono_of_cut(const Graph& g, uint32_t A){
    // mono = m - cut(A)
    int cut = 0;
    uint32_t B = (~A) & ((1u<<g.n)-1);
    uint32_t t = A;
    while(t){ int v = __builtin_ctz(t); t &= t-1; cut += pc(g.adj[v] & B); }
    return g.m - cut;
}

// enumerate independent sets, track min mono(N(I))
static void rec_ind(const Graph& g, int v, uint32_t I, uint32_t nb, uint32_t allowed, int& best){
    if(v == g.n){
        int mo = mono_of_cut(g, nb);
        if(mo < best) best = mo;
        return;
    }
    // skip v
    rec_ind(g, v+1, I, nb, allowed, best);
    // take v if allowed
    if(allowed & (1u<<v)){
        rec_ind(g, v+1, I|(1u<<v), nb | g.adj[v], allowed & ~g.adj[v], best);
    }
}

static int fam_exact(const Graph& g){
    int best = g.m; // I = empty -> N(I) = empty -> mono = m
    uint32_t all = (1u<<g.n)-1;
    rec_ind(g, 0, 0, 0, all, best);
    return best;
}

// number of 5-cycles = tr(A^5)/10 for triangle-free graphs
static long long c5_count(const Graph& g){
    int n = g.n;
    long long A2[16][16]; long long A3[16][16];
    for(int i=0;i<n;i++) for(int j=0;j<n;j++){
        long long s=0; uint32_t t = g.adj[i];
        while(t){ int k=__builtin_ctz(t); t&=t-1; if(g.adj[k]>>j & 1u) s++; }
        A2[i][j]=s;
    }
    for(int i=0;i<n;i++) for(int j=0;j<n;j++){
        long long s=0;
        for(int k=0;k<n;k++) if(A2[i][k]) { if(g.adj[k]>>j & 1u) s += A2[i][k]; }
        A3[i][j]=s;
    }
    long long tr=0;
    for(int i=0;i<n;i++) for(int j=0;j<n;j++) tr += A3[i][j]*A2[j][i];
    return tr/10;
}

int main(int argc, char** argv){
    std::ios::sync_with_stdio(false);
    long long nread=0, nA=0, nB=0;
    double maxratio = 0.0; std::string argmaxratio;
    double maxpent = 0.0; std::string argmaxpent;
    std::string line;
    std::vector<std::string> exA, exB;
    while(std::getline(std::cin, line)){
        if(!line.empty() && (line.back()=='\n'||line.back()=='\r')) line.pop_back();
        if(line.empty()) continue;
        Graph g;
        if(!parse_g6(line,g)) continue;
        nread++;
        int b = bip_exact(g);
        int f = fam_exact(g);
        int n = g.n;
        if(f > b){ nA++; if(exA.size()<20) exA.push_back(line + "  bip=" + std::to_string(b) + " fam=" + std::to_string(f)); }
        if(25*f > n*n){ nB++; if(exB.size()<20) exB.push_back(line + "  bip=" + std::to_string(b) + " fam=" + std::to_string(f) + " n=" + std::to_string(n)); }
        double r = 25.0*b/(double)(n*n);
        if(r > maxratio){ maxratio = r; argmaxratio = line + "  bip=" + std::to_string(b) + " n=" + std::to_string(n); }
        long long c5 = c5_count(g);
        if(c5 > 0 && b > 0){
            double pr = std::pow((double)b, 2.5)/(double)c5;
            if(pr > maxpent){ maxpent = pr; argmaxpent = line + "  bip=" + std::to_string(b) + " c5=" + std::to_string(c5) + " n=" + std::to_string(n); }
        }
    }
    printf("graphs read      : %lld\n", nread);
    printf("fam > bip        : %lld\n", nA);
    for(auto&s:exA) printf("   A %s\n", s.c_str());
    printf("25*fam > n^2     : %lld\n", nB);
    for(auto&s:exB) printf("   B %s\n", s.c_str());
    printf("max 25*bip/n^2   : %.6f   at %s\n", maxratio, argmaxratio.c_str());
    printf("max bip^2.5/c5   : %.6f   at %s\n", maxpent, argmaxpent.c_str());
    return 0;
}
