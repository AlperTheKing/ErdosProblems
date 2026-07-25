// Erdos #23, family F6.  Exhaustive census over triangle-free graphs.
// Input: graph6 lines on stdin (from nauty geng -t).
// For every graph G on N<=16 vertices computes EXACTLY (integers only):
//    m      = |E|
//    bip    = min over all 2^(N-1) cuts of #monochromatic edges
//    Dmax   = max_v sum_{u ~ v} d(u)           (best "neighbourhood cut" bound is m - Dmax)
//    w      = max over independent sets I of sum_{u in I} d(u)  (best independent-set cut bound m - w)
// Reports, per N: max bip and all extremisers (up to a cap), max (m-Dmax), max (m-w),
// and the number of graphs attaining max bip.
//
// build:  clang++ -O3 -march=native -o census.exe census.cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <cstdint>
#include <algorithm>
using namespace std;

static inline int pc(uint32_t x){ return __builtin_popcount(x); }

int main(int argc, char** argv){
    int CAP = 12;                      // how many extremisers to print
    if(argc>1) CAP = atoi(argv[1]);
    char buf[4096];
    int N=-1;
    long long count=0;
    int bestBip=-1; long long bestBipCount=0; vector<string> bestG;
    int bestNbhd=-1; string bestNbhdG;
    int bestIS=-1;   string bestISG;
    int bestCOMB=-1; string bestCOMBG; int bC_m=0,bC_w=0,bC_bip=0;
    // for reporting the (m-w) ratio champion we also keep m,w
    int bestIS_m=0,bestIS_w=0,bestIS_bip=0;
    int bestNb_m=0,bestNb_D=0,bestNb_bip=0;

    vector<int> f;                    // MWIS dp

    while(fgets(buf,sizeof buf,stdin)){
        int L=strlen(buf); while(L&&(buf[L-1]=='\n'||buf[L-1]=='\r')) buf[--L]=0;
        if(L==0) continue;
        const unsigned char* s=(const unsigned char*)buf;
        int n = s[0]-63; int pos=1;
        if(n!=N){ N=n; f.assign(1u<<N,0); }
        uint32_t adj[32]; for(int i=0;i<n;i++) adj[i]=0;
        int bitpos=0; int cur=0, nb=0;
        for(int j=1;j<n;j++) for(int i=0;i<j;i++){
            if(nb==0){ cur = s[pos++]-63; nb=6; }
            int bit = (cur>>(nb-1))&1; nb--;
            if(bit){ adj[i]|=1u<<j; adj[j]|=1u<<i; }
        }
        (void)bitpos;
        int deg[32]; int m=0;
        for(int i=0;i<n;i++){ deg[i]=pc(adj[i]); m+=deg[i]; }
        m/=2;

        // ---- exact bip by Gray-code enumeration of cuts, vertex 0 fixed on side A
        // state: mask = set of vertices on side B (mask has bit0 = 0)
        // mono(mask) = e(B) + e(A)
        uint32_t full = (n==32)?0xffffffffu:((1u<<n)-1);
        int mono=m;                      // mask=0: everything on side A -> mono = m
        int bip=mono;
        uint32_t mask=0;
        long long total = 1LL<<(n-1);
        for(long long g=1; g<total; g++){
            // gray code: bit to flip = index of lowest set bit of g, +1 (vertex 0 fixed)
            int b = __builtin_ctzll(g)+1;
            uint32_t vb = 1u<<b;
            uint32_t B = mask, A = full & ~mask;
            if(mask & vb){ // v currently in B -> move to A
                mono += pc(adj[b]&(A&~vb)) - pc(adj[b]&(B&~vb));
                mask &= ~vb;
            } else {       // v currently in A -> move to B
                mono += pc(adj[b]&(B&~vb)) - pc(adj[b]&(A&~vb));
                mask |= vb;
            }
            if(mono<bip) bip=mono;
        }

        // ---- Dmax
        int Dmax=0;
        for(int v=0;v<n;v++){ int D=0; uint32_t t=adj[v]; while(t){ int u=__builtin_ctz(t); t&=t-1; D+=deg[u]; } if(D>Dmax) Dmax=D; }

        // ---- max weight independent set, weights = degrees
        f[0]=0;
        for(uint32_t S=1;S<=full;S++){
            int v=__builtin_ctz(S);
            int a=f[S&~(1u<<v)];
            int b=deg[v]+f[S&~((1u<<v)|adj[v])];
            f[S]= a>b?a:b;
        }
        int w=f[full];

        count++;
        if(bip>bestBip){ bestBip=bip; bestBipCount=1; bestG.clear(); bestG.push_back(buf); }
        else if(bip==bestBip){ bestBipCount++; if((int)bestG.size()<CAP) bestG.push_back(buf); }
        if(m-Dmax>bestNbhd){ bestNbhd=m-Dmax; bestNbhdG=buf; bestNb_m=m;bestNb_D=Dmax;bestNb_bip=bip; }
        if(m-w>bestIS){ bestIS=m-w; bestISG=buf; bestIS_m=m;bestIS_w=w;bestIS_bip=bip; }
        { int comb = min(m/2, m-w); if(comb>bestCOMB){ bestCOMB=comb; bestCOMBG=buf; bC_m=m;bC_w=w;bC_bip=bip; } }
    }
    printf("N=%d  graphs=%lld\n", N, count);
    printf("  max bip = %d   (N^2/25 = %d/25 = %.6f)   #extremisers=%lld\n", bestBip, N*N, N*N/25.0, bestBipCount);
    printf("  25*bip vs N^2 : 25*%d = %d   %s  N^2 = %d\n", bestBip, 25*bestBip, (25*bestBip<=N*N?"<=":"> "), N*N);
    for(size_t i=0;i<bestG.size();i++) printf("    extremiser: %s\n", bestG[i].c_str());
    printf("  max (m - Dmax) = %d  at %s  (m=%d,Dmax=%d,bip=%d)   25*val=%d vs N^2=%d\n",
        bestNbhd,bestNbhdG.c_str(),bestNb_m,bestNb_D,bestNb_bip,25*bestNbhd,N*N);
    printf("  max (m - w)    = %d  at %s  (m=%d,w=%d,bip=%d)   25*val=%d vs N^2=%d\n",
        bestIS,bestISG.c_str(),bestIS_m,bestIS_w,bestIS_bip,25*bestIS,N*N);
    printf("  max min(floor(m/2), m-w) = %d  at %s  (m=%d,w=%d,bip=%d)   val/N^2=%.6f   25*val=%d vs N^2=%d\n",
      bestCOMB,bestCOMBG.c_str(),bC_m,bC_w,bC_bip,bestCOMB/double(N*N),25*bestCOMB,N*N);
    return 0;
}
