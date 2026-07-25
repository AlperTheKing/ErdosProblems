// Erdos #23, family F4.  Exhaustive census of the ONE-VERTEX DELETION STEP.
//
// For every connected triangle-free graph G on N<=13 vertices (graph6 on stdin,
// from nauty geng -t -c) compute exactly, with integers only:
//     bip(G)          = |E| - maxcut(G)
//     drop(v)         = bip(G) - bip(G-v)
//     rho(G)          = min_v drop(v)
// The naive induction step "exists v with bip(G)-bip(G-v) <= (2N-1)/25"
// holds for G iff 25*rho(G) <= 2N-1.
// Reports per N: max rho, witnesses, and the count of graphs whose every vertex
// fails the step (i.e. 25*rho(G) > 2N-1).
//
// build: clang++ -O3 -march=native -o f4_step.exe f4_step.cpp
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <cstdint>
using namespace std;

int main(int argc, char** argv){
    int CAP = 8; if(argc>1) CAP = atoi(argv[1]);
    char buf[4096];
    int N=-1; long long count=0;
    int bestRho=-1; long long bestRhoCount=0; vector<string> bestG;
    long long failAll=0;                 // graphs where every vertex fails the step
    vector<string> failEx;
    static int f[1<<14];                 // f[S] = #edges inside S
    int adj[16];

    while(fgets(buf,sizeof buf,stdin)){
        int L=strlen(buf); while(L&&(buf[L-1]=='\n'||buf[L-1]=='\r')) buf[--L]=0;
        if(L==0) continue;
        string g6(buf);
        int n = buf[0]-63;
        if(n!=N){
            if(N>0){
                printf("N=%d graphs=%lld maxrho=%d budget=(2N-1)/25=%d/25 stepfails=%lld",
                       N,count,bestRho,2*N-1,failAll);
                for(size_t i=0;i<bestG.size();i++) printf(" %s",bestG[i].c_str());
                printf("\n"); fflush(stdout);
            }
            N=n; count=0; bestRho=-1; bestRhoCount=0; bestG.clear(); failAll=0; failEx.clear();
        }
        // decode graph6
        for(int i=0;i<n;i++) adj[i]=0;
        {
            int k=0; const char* p=buf+1;
            for(int j=1;j<n;j++) for(int i=0;i<j;i++){
                int c = p[k/6]-63;
                if((c >> (5-(k%6))) & 1){ adj[i]|=1<<j; adj[j]|=1<<i; }
                k++;
            }
        }
        count++;
        int full=(1<<n)-1;
        f[0]=0;
        for(int S=1;S<=full;S++){
            int v=__builtin_ctz(S);
            f[S]=f[S^(1<<v)]+__builtin_popcount(adj[v]&(S^(1<<v)));
        }
        int bip=1<<30;
        for(int S=0;S<=full;S++){ int c=f[S]+f[full^S]; if(c<bip) bip=c; }
        if(bip==0){ continue; }              // bipartite: rho=0, step holds trivially
        int best[16]; for(int v=0;v<n;v++) best[v]=1<<30;
        for(int S=0;S<=full;S++){
            int T=full^S, fs=f[S], t=T;
            while(t){ int v=__builtin_ctz(t); t&=t-1;
                int c=fs+f[T^(1<<v)]; if(c<best[v]) best[v]=c; }
        }
        int rho=1<<30;
        for(int v=0;v<n;v++){ int d=bip-best[v]; if(d<rho) rho=d; }
        if(25*rho > 2*N-1){ failAll++; if((int)failEx.size()<CAP) failEx.push_back(g6); }
        if(rho>bestRho){ bestRho=rho; bestRhoCount=1; bestG.clear(); bestG.push_back(g6); }
        else if(rho==bestRho){ bestRhoCount++; if((int)bestG.size()<CAP) bestG.push_back(g6); }
    }
    if(N>0){
        printf("N=%d graphs=%lld maxrho=%d budget=(2N-1)/25=%d/25 stepfails=%lld",
               N,count,bestRho,2*N-1,failAll);
        for(size_t i=0;i<bestG.size();i++) printf(" %s",bestG[i].c_str());
        printf("\n");
    }
    return 0;
}
