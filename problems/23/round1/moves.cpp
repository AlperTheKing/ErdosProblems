// Erdos #23, family F6.  Exact values of
//    F_C(N) = max { |M(A,B)| : G triangle-free on N vertices, (A,B) a cut with
//                              Delta(S) >= 0 for every S in the move class C }
// for several move classes C.  Delta(S) = c(S) - m(S) = sum_{v in S} s(v) - 2(cut_in(S)-mono_in(S))
// is the change in #monochromatic edges when the side of every vertex of S is flipped;
// Delta(S) >= 0 means "flipping S is not an improvement".
//
// Classes:
//   k=1..K : all S with 1 <= |S| <= k
//   NB     : all S = N(v)                       ("neighbourhood moves")
//   NC     : all S = N[v] = {v} u N(v)           ("closed neighbourhood moves")
//   CS     : all S = {v} u N_C(v)                ("cut-star / rotation moves")
//   ALLSTR : union of {|S|<=2}, NB, NC, CS
//
// Everything exact integer.  Input: graph6 on stdin.
// build: clang++ -O3 -march=native -o moves.exe moves.cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <cstdint>
#include <algorithm>
using namespace std;
static inline int pc(uint32_t x){ return __builtin_popcount(x); }

int n;
uint32_t adj[20];
int deg[20];
int s_[20];
uint32_t sideB;                 // bitmask of side B

// Delta(S) for a subset given as bitmask
static inline int Delta(uint32_t S){
    int tot=0, cut_in=0, mono_in=0;
    uint32_t t=S;
    while(t){ int v=__builtin_ctz(t); t&=t-1; tot+=s_[v];
        uint32_t hi = adj[v] & S & ~((2u<<v)-1);      // neighbours of v in S with index > v
        uint32_t sameB = (sideB>>v)&1 ? sideB : (~sideB);
        cut_in  += pc(hi & ~sameB);
        mono_in += pc(hi &  sameB);
    }
    return tot - 2*(cut_in - mono_in);
}

int K;                                   // max size for the "all subsets of size<=k" classes
vector<uint32_t> subsBySize[8];          // subsets of {0..n-1} of each size

// returns the largest k in 0..K such that all S with |S|<=k have Delta>=0  (0 = fails even k=1)
int maxGoodK(){
    for(int k=1;k<=K;k++){
        for(uint32_t S : subsBySize[k]) if(Delta(S)<0) return k-1;
    }
    return K;
}
bool okNB(){ for(int v=0;v<n;v++) if(adj[v] && Delta(adj[v])<0) return false; return true; }
bool okNC(){ for(int v=0;v<n;v++){ uint32_t S=adj[v]|(1u<<v); if(Delta(S)<0) return false;} return true; }
bool okCS(){ for(int v=0;v<n;v++){
        uint32_t sameB = (sideB>>v)&1 ? sideB : (~sideB);
        uint32_t S=(adj[v]&~sameB)|(1u<<v); if(Delta(S)<0) return false;} return true; }
// OPTIMAL star move: min over all S with v in S subset N[v] of Delta(S)
//   Delta({v} u T) = s(v) + sum_{u in T n N_C(v)} (s(u)-2) + sum_{u in T n N_M(v)} (s(u)+2)
// so the minimiser is T = { u in N_C(v) : s(u) < 2 }.  Condition:
//   s(v) >= sum_{u in N_C(v)} (2 - s(u))^+     for every v.
bool okSTAR(){ for(int v=0;v<n;v++){
        uint32_t sameB=(sideB>>v)&1?sideB:(~sideB);
        uint32_t NC = adj[v]&~sameB; int need=0;
        while(NC){ int u=__builtin_ctz(NC); NC&=NC-1; if(s_[u]<2) need += 2-s_[u]; }
        if(s_[v] < need) return false; } return true; }

int main(int argc,char**argv){
    K = argc>1?atoi(argv[1]):5;
    char buf[4096]; int N=-1; long long cnt=0;
    // best[k] = F_k(N); bestNB/NC/CS/ALL
    int best[9]; memset(best,-1,sizeof best);
    string arg[9];
    int bestALL=-1; string argALL;
    int bestNBv=-1,bestNCv=-1,bestCSv=-1,bestSTv=-1; string argNB,argNC,argCS,argST;

    while(fgets(buf,sizeof buf,stdin)){
        int L=strlen(buf); while(L&&(buf[L-1]=='\n'||buf[L-1]=='\r')) buf[--L]=0;
        if(!L) continue;
        const unsigned char* g=(const unsigned char*)buf;
        int nn=g[0]-63; int pos=1;
        if(nn!=N){ N=nn; n=N;
            for(int k=0;k<=K;k++) subsBySize[k].clear();
            for(uint32_t S=1;S<(1u<<n);S++){ int c=pc(S); if(c<=K) subsBySize[c].push_back(S); }
        }
        n=N;
        for(int i=0;i<n;i++) adj[i]=0;
        int cur=0,nb=0;
        for(int j=1;j<n;j++) for(int i=0;i<j;i++){
            if(nb==0){ cur=g[pos++]-63; nb=6; }
            int bit=(cur>>(nb-1))&1; nb--;
            if(bit){ adj[i]|=1u<<j; adj[j]|=1u<<i; }
        }
        int m=0; for(int i=0;i<n;i++){ deg[i]=pc(adj[i]); m+=deg[i]; } m/=2;
        cnt++;
        uint32_t full=(1u<<n)-1;
        // enumerate all cuts (vertex 0 on side A), collect (mono,mask), sort desc
        static vector<pair<int,uint32_t>> cuts; cuts.clear();
        for(uint32_t mask=0; mask<(1u<<(n-1)); mask++){
            uint32_t B=mask<<1; uint32_t A=full&~B;
            int mono=0; for(int v=0;v<n;v++){ uint32_t sm=((B>>v)&1)?B:A; mono+=pc(adj[v]&sm); }
            mono/=2;
            cuts.push_back({mono,B});
        }
        sort(cuts.begin(),cuts.end(),greater<pair<int,uint32_t>>());
        // prune: stop once mono can no longer beat the WEAKEST current record
        // (a class is only improvable while mono exceeds that class's record)
        int needMin;
        auto recomputeMin=[&](){ needMin=best[1]; for(int k=1;k<=K;k++) needMin=min(needMin,best[k]);
            needMin=min(needMin,min(bestALL,min(bestSTv,min(bestNBv,min(bestNCv,bestCSv))))); };
        recomputeMin();
        // flags: which classes already have their per-graph maximum recorded
        int foundK=-1; bool fNB=false,fNC=false,fCS=false,fST=false,fALL=false;
        for(size_t ci=0; ci<cuts.size(); ci++){
            int mono=cuts[ci].first; sideB=cuts[ci].second;
            if(mono<=needMin) break;                 // no class can be improved any more
            for(int v=0;v<n;v++){ uint32_t sm=((sideB>>v)&1)?sideB:(full&~sideB);
                int dm=pc(adj[v]&sm); s_[v]=deg[v]-2*dm; }
            int gk=maxGoodK();
            if(gk>=1){
                if(foundK<0) foundK=gk;
                for(int k=1;k<=gk;k++) if(mono>best[k]){ best[k]=mono; arg[k]=buf; }
                bool a=okNB(),b=okNC(),c=okCS(),d=okSTAR();
                if(a&&!fNB){ fNB=true; if(mono>bestNBv){bestNBv=mono;argNB=buf;} }
                if(b&&!fNC){ fNC=true; if(mono>bestNCv){bestNCv=mono;argNC=buf;} }
                if(c&&!fCS){ fCS=true; if(mono>bestCSv){bestCSv=mono;argCS=buf;} }
                if(d&&!fST){ fST=true; if(mono>bestSTv){bestSTv=mono;argST=buf;} }
                if(gk>=K&&a&&b&&c&&d&&!fALL){ fALL=true; if(mono>bestALL){bestALL=mono;argALL=buf;} }
            }
            recomputeMin();
        }
    }
    printf("N=%d graphs=%lld    (N^2/8=%.3f  N^2/25=%.3f)\n",N,cnt,N*N/8.0,N*N/25.0);
    for(int k=1;k<=K;k++)
        printf("  F_{|S|<=%d}(%d) = %3d   ratio=%.5f   witness %s\n",k,N,best[k],best[k]/double(N*N),arg[k].c_str());
    printf("  F_{N(v) moves}(%d)  = %3d   ratio=%.5f   witness %s\n",N,bestNBv,bestNBv/double(N*N),argNB.c_str());
    printf("  F_{N[v] moves}(%d)  = %3d   ratio=%.5f   witness %s\n",N,bestNCv,bestNCv/double(N*N),argNC.c_str());
    printf("  F_{cut-star}(%d)    = %3d   ratio=%.5f   witness %s\n",N,bestCSv,bestCSv/double(N*N),argCS.c_str());
    printf("  F_{STAR moves}(%d)  = %3d   ratio=%.5f   witness %s\n",N,bestSTv,bestSTv/double(N*N),argST.c_str());
    printf("  F_{|S|<=%d & NB & NC & CS & STAR}(%d)= %3d ratio=%.5f   witness %s\n",K,N,bestALL,bestALL/double(N*N),argALL.c_str());
    return 0;
}
