// a2_census.cpp -- AUDIT pass 2: independent census driver.
// Reads graph6 lines on stdin.  For each graph computes, in exact integers:
//   bip  = |E| - maxcut, via subset-DP  e[S] = #edges inside S, mono(S) = e[S] + e[~S]
//   fam  = min over ALL sets  U(I) = union_{v in I} N(v),  I ranges over every subset of V
//   also the min over single neighbourhoods, and over odd-BFS-layer sets from every root.
// Reports counts of {fam > bip} and {25*fam > n^2} and {25*bip > n^2}, and the total.
// No Gray code; no floating point.
// build: clang++ -O3 -march=native -std=c++17 a2_census.cpp -o a2_census.exe
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>

static inline int pc(unsigned x){ return __builtin_popcount(x); }

int main(int argc, char** argv){
    bool verbose = (argc > 1 && std::string(argv[1]) == "-v");
    std::vector<int> e, mono;
    std::vector<unsigned> U;
    std::vector<char> seen;
    char line[4096];
    long long total=0, cnt_famgt=0, cnt_fam25=0, cnt_bip25=0, cnt_single25=0, cnt_bfs25=0;
    long long cnt_bfs_not_union=0, cnt_roots=0;
    int lastn = -1;
    while(fgets(line, sizeof(line), stdin)){
        int L = (int)strlen(line);
        while(L>0 && (line[L-1]=='\n' || line[L-1]=='\r')) line[--L]=0;
        if(L==0) continue;
        // ---- graph6 decode (own: explicit column-major double loop) ----
        int n = line[0]-63;
        if(n<1 || n>25){ fprintf(stderr,"bad n\n"); return 1; }
        std::vector<unsigned> adj(n,0);
        {
            int p=1, val=0, have=0;
            for(int j=1;j<n;j++) for(int i=0;i<j;i++){
                if(have==0){ val = line[p++]-63; have=6; }
                int bit = (val >> (have-1)) & 1; have--;
                if(bit){ adj[i] |= 1u<<j; adj[j] |= 1u<<i; }
            }
        }
        int m = 0; for(int v=0;v<n;v++) m += pc(adj[v]); m/=2;
        unsigned full = (n==32)?~0u:((1u<<n)-1);
        if(n != lastn){ e.assign(1u<<n,0); mono.assign(1u<<n,0); U.assign(1u<<n,0); seen.assign(1u<<n,0); lastn=n; }
        // ---- e[S] subset DP ----
        e[0]=0;
        for(unsigned S=1; S<=full; S++){
            int v = __builtin_ctz(S);
            unsigned T = S ^ (1u<<v);
            e[S] = e[T] + pc(adj[v] & T);
        }
        // ---- bip ----
        int bip = 1<<30;
        for(unsigned S=0; S<=full; S++){
            int t = e[S] + e[full^S];
            mono[S] = t;
            if(t < bip) bip = t;
        }
        // ---- neighbourhood-union family over ALL index sets ----
        U[0]=0;
        std::fill(seen.begin(), seen.end(), 0);
        int fam = 1<<30;
        seen[0]=1;                       // I = empty gives S = empty
        if(mono[0] < fam) fam = mono[0];
        for(unsigned I=1; I<=full; I++){
            int v = __builtin_ctz(I);
            U[I] = U[I ^ (1u<<v)] | adj[v];
            unsigned S = U[I];
            if(!seen[S]){ seen[S]=1; if(mono[S] < fam) fam = mono[S]; }
        }
        // ---- single neighbourhoods ----
        int single = 1<<30;
        for(int v=0;v<n;v++) if(mono[adj[v]] < single) single = mono[adj[v]];
        // ---- odd BFS layers from every root ----
        int bfsmin = 1<<30;
        for(int r=0;r<n;r++){
            std::vector<int> dist(n,-1); dist[r]=0;
            std::vector<int> q{r};
            for(size_t h=0; h<q.size(); h++){
                int x=q[h];
                unsigned t = adj[x];
                while(t){ int y=__builtin_ctz(t); t&=t-1; if(dist[y]<0){ dist[y]=dist[x]+1; q.push_back(y);} }
            }
            unsigned S=0;
            for(int v=0;v<n;v++) if(dist[v]>0 && (dist[v]&1)) S |= 1u<<v;
            if(mono[S] < bfsmin) bfsmin = mono[S];
            cnt_roots++;
            if(!seen[S]) cnt_bfs_not_union++;
        }
        total++;
        if(fam > bip) cnt_famgt++;
        if(25*fam > n*n) cnt_fam25++;
        if(25*bip > n*n) cnt_bip25++;
        if(25*single > n*n) cnt_single25++;
        if(25*bfsmin > n*n) cnt_bfs25++;
        if(verbose && (25*fam > n*n || 25*bip > n*n))
            printf("HIT %s  n=%d m=%d bip=%d fam=%d single=%d bfs=%d\n", line, n, m, bip, fam, single, bfsmin);
    }
    printf("total=%lld  #{fam>bip}=%lld  #{25fam>n^2}=%lld  #{25bip>n^2}=%lld  "
           "#{25single>n^2}=%lld  #{25bfsmin>n^2}=%lld  roots=%lld  #{oddlayer not a nbhd-union}=%lld\n",
           total, cnt_famgt, cnt_fam25, cnt_bip25, cnt_single25, cnt_bfs25, cnt_roots, cnt_bfs_not_union);
    return 0;
}
