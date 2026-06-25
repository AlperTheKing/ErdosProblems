// Flexible H2 verifier for an explicit graph given as an edge list.
// Input file format:
//   line 1:  N            (number of vertices; must be 5n)
//   following lines: "u v"  (0-indexed edge)
// Reports: triangle-free?, e, MaxCut, beta, and min over all C(N,5) 5-sets of
//   [beta(G)-beta(G-S)], plus H2 verdict (drop_min <= 2n-1 ?).
// Exact brute-force MaxCut (2^(N-1) and 2^(N-6)); fine for N<=22.
//
// Build: clang++ -O3 -std=c++17 h2_check_edgelist.cpp -o h2_check_edgelist.exe
// Usage: ./h2_check_edgelist.exe graph.txt
#include <cstdio>
#include <cstdint>
#include <vector>
#include <cstdlib>
#include <algorithm>

static int N;
static std::vector<uint32_t> adj;   // adjacency bitmask per vertex (N<=32)

static inline int popc(uint32_t x){ return __builtin_popcount(x); }

// exact MaxCut on induced subgraph given by compact vertex list
static long maxcut_induced(const std::vector<int>&verts, long&Eout){
    int m=verts.size(); if(m<=1){ Eout=0; return 0; }
    std::vector<int> idx(N,-1); for(int i=0;i<m;i++) idx[verts[i]]=i;
    std::vector<uint32_t> b(m,0); long E=0;
    for(int i=0;i<m;i++){ int v=verts[i]; uint32_t a=adj[v];
        while(a){ int w=__builtin_ctz(a); a&=a-1; if(idx[w]>=0 && w>v){ b[idx[w]]|=(1u<<i); b[i]|=(1u<<idx[w]); E++; } } }
    Eout=E; long best=0; long lim=1L<<(m-1);
    for(long half=0; half<lim; half++){ uint32_t side1=(uint32_t)(half<<1); long cut=0; uint32_t x=side1;
        while(x){ int v=__builtin_ctz(x); x&=x-1; cut+=popc(b[v]&~side1); } if(cut>best) best=cut; }
    return best;
}
static long beta_of(const std::vector<int>&verts){ long E; long mc=maxcut_induced(verts,E); return E-mc; }

int main(int argc,char**argv){
    if(argc<2){ fprintf(stderr,"usage: %s graph.txt\n",argv[0]); return 2; }
    FILE*f=fopen(argv[1],"r"); if(!f){ perror("open"); return 2; }
    if(fscanf(f,"%d",&N)!=1){ fprintf(stderr,"bad N\n"); return 2; }
    if(N%5!=0){ fprintf(stderr,"N=%d not a multiple of 5\n",N); }
    adj.assign(N,0);
    int u,v; long m=0; bool tri=false;
    while(fscanf(f,"%d %d",&u,&v)==2){ if(u<0||v<0||u>=N||v>=N||u==v) continue; if(adj[u]&(1u<<v)) continue; adj[u]|=(1u<<v); adj[v]|=(1u<<u); m++; }
    fclose(f);
    // triangle check
    for(int a=0;a<N&&!tri;a++){ uint32_t na=adj[a]; while(na){ int w=__builtin_ctz(na); na&=na-1; if(w>a && (adj[a]&adj[w])) { tri=true; break; } } }
    int n=N/5; int target=2*n-1;
    std::vector<int> all(N); for(int i=0;i<N;i++) all[i]=i;
    long Efull; long mcfull=maxcut_induced(all,Efull); long bG=Efull-mcfull;
    printf("N=%d n=%d  e=%ld  MaxCut=%ld  beta=%ld  triangle_free=%s  (n^2=%d, target 2n-1=%d)\n",
           N,n,m,mcfull,bG,tri?"NO":"YES",n*n,target);
    if(tri){ printf("  NOT triangle-free -> not a valid #23 instance.\n"); return 0; }
    if(bG<=target){ printf("  beta<=2n-1: H2 trivially satisfiable (any 5-set). drop_min not computed.\n"); return 0; }
    // min 5-set drop (full, exact -- report true minimum)
    long mn=1L<<30; std::vector<int> S(5), rem; rem.reserve(N-5);
    for(S[0]=0;S[0]<N;S[0]++)for(S[1]=S[0]+1;S[1]<N;S[1]++)for(S[2]=S[1]+1;S[2]<N;S[2]++)
    for(S[3]=S[2]+1;S[3]<N;S[3]++)for(S[4]=S[3]+1;S[4]<N;S[4]++){
        rem.clear(); int si=0;
        for(int i=0;i<N;i++){ if(si<5 && i==S[si]){ si++; continue; } rem.push_back(i); }
        long d=bG-beta_of(rem); if(d<mn) mn=d;
    }
    printf("  min 5-set drop = %ld   target 2n-1 = %d\n",mn,target);
    if(mn>target) printf("  *** H2 VIOLATION *** min drop %ld > %d : this graph BREAKS H2 at n=%d\n",mn,target,n);
    else          printf("  H2 OK: a 5-set with drop=%ld<=%d exists.\n",mn,target);
    return 0;
}
