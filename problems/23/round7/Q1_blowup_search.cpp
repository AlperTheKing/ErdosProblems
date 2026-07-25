// Q1_blowup_search.cpp -- exhaustive EXACT integer-weight search for a counterexample
// among blow-ups H[a] of a given triangle-free H.
//
// Base 1 (accepted): bip(H[a]) = min over cuts S of H of sum_{uv monochromatic} a_u a_v.
// Base 2 (accepted): zero weights MUST be allowed.
// A counterexample is a vector a >= 0 (integers, sum = W) with 25 * bip(H[a]) > W^2.
//
// All arithmetic is exact 64-bit integer arithmetic; no floating point anywhere.
//
// usage: Q1_blowup_search.exe <graph6> <Wmin> <Wmax> [threads]
// build : clang++ -O3 -march=native -std=c++17 Q1_blowup_search.cpp -o Q1_blowup_search.exe
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <algorithm>

static int N;                       // |V(H)|
static std::vector<std::pair<int,int>> EDG;
static std::vector<std::vector<std::pair<int,int>>> MONO;   // per cut: monochromatic edge list

static bool parse_g6(const std::string& s, int& n, std::vector<std::pair<int,int>>& E){
    size_t p = 0;
    n = (int)s[p++] - 63;
    int need = n*(n-1)/2;
    int val = 0, have = 0;
    E.clear();
    for(int k=0;k<need;k++){
        if(have==0){ val = (int)s[p++]-63; have = 6; }
        int bit = (val >> (have-1)) & 1; have--;
        if(bit){
            int j = 1, base = 0;
            while(base + j <= k){ base += j; j++; }
            int i = k - base;
            E.push_back({i,j});
        }
    }
    return true;
}

// ---- search state -------------------------------------------------------
static std::atomic<long long> g_count(0);
static std::atomic<long long> g_found(0);
static std::vector<std::vector<int>> g_witness;

// evaluate: return true iff  25 * min_S q_S(a)  >  W^2   (i.e. a is a counterexample)
static inline bool is_counterexample(const int* a, long long W, long long& outmin){
    long long target = W*W;                      // need 25*q > W^2 for EVERY cut
    long long best = -1;
    for(size_t c=0;c<MONO.size();c++){
        long long q = 0;
        for(const auto& e : MONO[c]) q += (long long)a[e.first]*a[e.second];
        if(25*q <= target){ outmin = q; return false; }   // early exit
        if(best < 0 || q < best) best = q;
    }
    outmin = best;
    return true;
}

struct Searcher {
    long long W;
    int a[32];
    long long bestratio_num, bestratio_den;      // best 25*min/W^2 seen (as a fraction)
    std::vector<int> bestvec;
    int startlo, starthi;                        // slice of a[0] handled by this thread
    long long count;

    void rec(int idx, long long left){
        if(idx == N-1){
            a[idx] = (int)left;
            count++;
            long long mn;
            if(is_counterexample(a, W, mn)){
                g_found++;
                std::vector<int> v(a, a+N);
                g_witness.push_back(v);
                printf("COUNTEREXAMPLE  W=%lld  a=[", W);
                for(int i=0;i<N;i++) printf("%d%s", a[i], i+1<N?",":"");
                printf("]  bip=%lld  25*bip=%lld > W^2=%lld\n", mn, 25*mn, W*W);
                fflush(stdout);
            } else {
                // mn is the value of the first cut that failed, hence an UPPER bound on bip.
                // Only when that upper bound is already near-extremal do we pay for the true min.
                if(25*mn*10 > 9*W*W){
                    long long tru = -1;
                    for(size_t c=0;c<MONO.size();c++){
                        long long q = 0;
                        for(const auto& e : MONO[c]) q += (long long)a[e.first]*a[e.second];
                        if(tru < 0 || q < tru) tru = q;
                    }
                    if(tru*bestratio_den*25 > bestratio_num*W*W){
                        bestratio_num = 25*tru; bestratio_den = W*W;
                        bestvec.assign(a, a+N);
                    }
                }
            }
            return;
        }
        int lo = 0, hi = (int)left;
        if(idx == 0){ lo = startlo; hi = std::min<int>(hi, starthi); }
        for(int v=lo; v<=hi; v++){
            a[idx] = v;
            rec(idx+1, left - v);
        }
    }
};

int main(int argc, char** argv){
    if(argc < 4){ printf("usage: %s <graph6> <Wmin> <Wmax> [threads]\n", argv[0]); return 1; }
    std::string g6 = argv[1];
    int Wmin = atoi(argv[2]), Wmax = atoi(argv[3]);
    int nthreads = (argc>4)? atoi(argv[4]) : 8;

    parse_g6(g6, N, EDG);
    printf("H = %s   n=%d  |E|=%zu\n", g6.c_str(), N, EDG.size());

    bool nbhd_only = (argc>5 && std::string(argv[5])=="nbhd");
    // optional restriction: cuts of the form  union of N(v), v in I   (I an arbitrary index set)
    std::vector<unsigned> cutlist;
    if(nbhd_only){
        std::vector<unsigned> adj(N,0);
        for(auto& e : EDG){ adj[e.first] |= 1u<<e.second; adj[e.second] |= 1u<<e.first; }
        std::vector<char> seen(1u<<N, 0);
        for(unsigned I=0; I<(1u<<N); I++){
            unsigned S=0;
            for(int v=0;v<N;v++) if(I>>v&1) S |= adj[v];
            if(!seen[S]){ seen[S]=1; cutlist.push_back(S); }
        }
        printf("neighbourhood-union cuts: %zu distinct sets\n", cutlist.size());
    } else {
        for(unsigned mask=0; mask < (1u<<(N-1)); mask++) cutlist.push_back(mask<<1);
    }

    // build monochromatic edge lists for every cut
    std::vector<std::pair<long long,int>> order;
    std::vector<std::vector<std::pair<int,int>>> tmp;
    for(unsigned S : cutlist){
        std::vector<std::pair<int,int>> lst;
        for(auto& e : EDG){
            int bu = (S>>e.first)&1, bv = (S>>e.second)&1;
            if(bu==bv) lst.push_back(e);
        }
        order.push_back({(long long)lst.size(), (int)tmp.size()});
        tmp.push_back(lst);
    }
    std::sort(order.begin(), order.end());        // fewest monochromatic edges first
    for(auto& o : order) MONO.push_back(tmp[o.second]);
    printf("cuts considered: %zu (fewest-mono-first ordering)\n", MONO.size());

    for(int W=Wmin; W<=Wmax; W++){
        std::vector<Searcher> S(nthreads);
        std::vector<std::thread> th;
        int per = (W+1 + nthreads-1)/nthreads;
        for(int t=0;t<nthreads;t++){
            S[t].W = W; S[t].count = 0;
            S[t].bestratio_num = 0; S[t].bestratio_den = 1;
            S[t].startlo = t*per; S[t].starthi = std::min(W, (t+1)*per-1);
            if(S[t].startlo > W) { S[t].starthi = -1; }
        }
        for(int t=0;t<nthreads;t++)
            th.emplace_back([&S,t](){ if(S[t].startlo<=S[t].starthi) S[t].rec(0, S[t].W); });
        for(auto& x : th) x.join();
        long long tot=0; long long bn=0, bd=1; std::vector<int> bv;
        for(int t=0;t<nthreads;t++){
            tot += S[t].count;
            if(S[t].bestratio_num*bd > bn*S[t].bestratio_den){ bn=S[t].bestratio_num; bd=S[t].bestratio_den; bv=S[t].bestvec; }
        }
        printf("W=%2d  vectors=%12lld  best 25*bip/W^2 = %lld/%lld", W, tot, bn, bd);
        if(!bv.empty()){ printf("  at a=["); for(size_t i=0;i<bv.size();i++) printf("%d%s", bv[i], i+1<bv.size()?",":""); printf("]"); }
        printf("   counterexamples so far: %lld\n", (long long)g_found);
        fflush(stdout);
    }
    printf("TOTAL counterexamples: %lld\n", (long long)g_found);
    return 0;
}
