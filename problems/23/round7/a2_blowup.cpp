// a2_blowup.cpp -- AUDIT pass 2: exhaustive EXACT integer-weight blow-up search on a
// given triangle-free H.  Counts, for each total weight W:
//   * counterexamples          25*bip(H[a]) >  W^2
//   * maximisers               25*bip(H[a]) == W^2          <-- the E3 claim
//   * neighbourhood-family failures  25*fam(H[a]) > W^2
// Zero weights are allowed (accepted base 2).  All arithmetic is 64-bit integer.
// usage: a2_blowup.exe <graph6> <Wmin> <Wmax> [threads] [--dumpmax W]
// build: clang++ -O3 -march=native -std=c++17 a2_blowup.cpp -o a2_blowup.exe
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <algorithm>

static int N;
static std::vector<std::pair<int,int>> EDG;
static std::vector<std::vector<std::pair<int,int>>> CUTS;   // all cuts, mono edge lists
static std::vector<std::vector<std::pair<int,int>>> FCUTS;  // neighbourhood-union cuts

static void parse_g6(const std::string& s, int& n, std::vector<std::pair<int,int>>& E){
    n = (int)s[0] - 63;
    int p = 1, val = 0, have = 0;
    E.clear();
    for(int j=1;j<n;j++) for(int i=0;i<j;i++){
        if(have==0){ val = (int)s[p++]-63; have=6; }
        int bit = (val >> (have-1)) & 1; have--;
        if(bit) E.push_back({i,j});
    }
}

static std::atomic<long long> g_ce(0), g_max(0), g_famfail(0), g_cnt(0);
static std::vector<std::vector<int>> g_maxvec, g_famvec;


struct Th {
    long long W, T;                 // T = W*W
    int a[32];
    long long ce=0, mx=0, ff=0, cnt=0;
    int lo0, hi0;
    bool dump;
    std::vector<std::vector<int>> mxvec, ffvec;

    void leaf(){
        cnt++;
        // ---- true min over all cuts, with early exit at 25q < W^2 ----
        long long best = -1;
        bool alive = true;
        for(const auto& L : CUTS){
            long long q = 0;
            for(const auto& e : L) q += (long long)a[e.first]*a[e.second];
            if(25*q < T){ alive = false; break; }
            if(best < 0 || q < best) best = q;
        }
        if(alive){
            if(25*best > T){ ce++; }
            else { mx++; if(dump && mxvec.size()<2000) mxvec.push_back(std::vector<int>(a,a+N)); }
        }
        // ---- neighbourhood-union family, early exit at 25q <= W^2 ----
        bool fail = true;
        for(const auto& L : FCUTS){
            long long q = 0;
            for(const auto& e : L) q += (long long)a[e.first]*a[e.second];
            if(25*q <= T){ fail = false; break; }
        }
        if(fail){ ff++; if(ffvec.size()<200) ffvec.push_back(std::vector<int>(a,a+N)); }
    }
    void rec(int idx, long long left){
        if(idx == N-1){ a[idx] = (int)left; leaf(); return; }
        int lo = 0, hi = (int)left;
        if(idx == 0){ lo = lo0; hi = std::min<int>(hi, hi0); }
        for(int v=lo; v<=hi; v++){ a[idx]=v; rec(idx+1, left-v); }
    }
};

int main(int argc, char** argv){
    if(argc < 4){ printf("usage: %s <graph6> <Wmin> <Wmax> [threads] [dumpW]\n", argv[0]); return 1; }
    std::string g6 = argv[1];
    int Wmin = atoi(argv[2]), Wmax = atoi(argv[3]);
    int nth = (argc>4)? atoi(argv[4]) : 8;
    int dumpW = (argc>5)? atoi(argv[5]) : -1;
    parse_g6(g6, N, EDG);
    printf("H = %s  n=%d |E|=%zu\n", g6.c_str(), N, EDG.size());

    std::vector<unsigned> adj(N,0);
    for(auto& e : EDG){ adj[e.first] |= 1u<<e.second; adj[e.second] |= 1u<<e.first; }

    auto monolist = [&](unsigned S){
        std::vector<std::pair<int,int>> L;
        for(auto& e : EDG) if((((S>>e.first)&1) == ((S>>e.second)&1))) L.push_back(e);
        return L;
    };
    // all cuts (S and complement give the same mono set; keep S with bit0 = 0)
    std::vector<std::pair<size_t,std::vector<std::pair<int,int>>>> tmp;
    for(unsigned S=0; S<(1u<<(N-1)); S++){ auto L = monolist(S<<1); tmp.push_back({L.size(), L}); }
    std::sort(tmp.begin(), tmp.end(), [](auto&x, auto&y){ return x.first < y.first; });
    for(auto& t : tmp) CUTS.push_back(t.second);
    // neighbourhood-union cuts
    std::vector<char> seen(1u<<N, 0);
    std::vector<unsigned> U(1u<<N, 0);
    std::vector<std::pair<size_t,std::vector<std::pair<int,int>>>> tf;
    seen[0]=1; { auto L = monolist(0u); tf.push_back({L.size(), L}); }
    for(unsigned I=1; I<(1u<<N); I++){
        int v = __builtin_ctz(I);
        U[I] = U[I ^ (1u<<v)] | adj[v];
        if(!seen[U[I]]){ seen[U[I]]=1; auto L = monolist(U[I]); tf.push_back({L.size(), L}); }
    }
    std::sort(tf.begin(), tf.end(), [](auto&x, auto&y){ return x.first < y.first; });
    for(auto& t : tf) FCUTS.push_back(t.second);
    printf("cuts=%zu  neighbourhood-union cuts=%zu\n", CUTS.size(), FCUTS.size());

    for(int W=Wmin; W<=Wmax; W++){
        std::vector<Th> S(nth);
        std::vector<std::thread> th;
        int per = (W+1 + nth-1)/nth;
        for(int t=0;t<nth;t++){
            S[t].W=W; S[t].T=(long long)W*W; S[t].lo0=t*per; S[t].hi0=std::min(W,(t+1)*per-1);
            S[t].dump = (W==dumpW);
        }
        for(int t=0;t<nth;t++) th.emplace_back([&S,t](){ if(S[t].lo0<=S[t].hi0) S[t].rec(0,S[t].W); });
        for(auto& x : th) x.join();
        long long ce=0,mx=0,ff=0,cnt=0;
        std::vector<std::vector<int>> mv, fv;
        for(int t=0;t<nth;t++){ ce+=S[t].ce; mx+=S[t].mx; ff+=S[t].ff; cnt+=S[t].cnt;
            for(auto& v : S[t].mxvec) mv.push_back(v);
            for(auto& v : S[t].ffvec) fv.push_back(v); }
        printf("W=%2d vectors=%12lld  counterexamples=%lld  maximisers(25bip==W^2)=%lld  "
               "family-failures(25fam>W^2)=%lld\n", W, cnt, ce, mx, ff);
        for(size_t i=0;i<fv.size() && i<10;i++){
            printf("     famfail a=["); for(int k=0;k<N;k++) printf("%d%s", fv[i][k], k+1<N?",":""); printf("]\n");
        }
        if(W==dumpW) for(size_t i=0;i<mv.size() && i<12;i++){
            printf("     maximiser a=["); for(int k=0;k<N;k++) printf("%d%s", mv[i][k], k+1<N?",":""); printf("]\n");
        }
        fflush(stdout);
    }
    return 0;
}
