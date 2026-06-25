// Parametric H2 counterexample search at N=5n (default n=4, N=20), native MT.
// H2: every triangle-free G on 5n vtx admits a 5-set S with beta(G)-beta(G-S) <= 2n-1.
// Counterexample = triangle-free, beta in (2n-1, n^2], with min over all C(N,5) 5-sets
// of [beta(G)-beta(G-S)] > 2n-1.  beta = E - MaxCut (exact brute, fix vtx0).
// Generators: all C5-blowup compositions of N into 5 parts; random-maximal triangle-free;
// perturbation hill-climb; Petersen[2] (N=20 non-C5-hom hard core) + its perturbs.
// Build: clang++ -O3 -std=c++17 -pthread h2_ce_search_param.cpp -o h2_ce_search_param.exe
// Usage: ./h2_ce_search_param.exe N threads nrand_per_thr nhard_per_thr
#include <cstdio>
#include <cstdint>
#include <vector>
#include <random>
#include <thread>
#include <algorithm>

static int N;            // vertex count = 5n
static int TARGET;       // 2n-1
static int BAND_LO;      // 2n  (nontrivial band lower bound, since beta<=2n-1 is trivial)

typedef uint32_t Mask;
struct Graph { std::vector<Mask> adj; Graph():adj(32,0){} };

static inline int popc(uint32_t x){ return __builtin_popcount(x); }
static inline bool addSafe(Graph&g,int u,int v){ if(u==v)return false; if(g.adj[u]&(1u<<v))return false; if(g.adj[u]&g.adj[v])return false; g.adj[u]|=(1u<<v);g.adj[v]|=(1u<<u);return true; }
static inline void delE(Graph&g,int u,int v){ g.adj[u]&=~(1u<<v); g.adj[v]&=~(1u<<u); }
static bool triFree(const Graph&g){ for(int u=0;u<N;u++){ Mask a=g.adj[u]&(~((1u<<(u+1))-1)); while(a){int v=__builtin_ctz(a);a&=a-1; if(g.adj[u]&g.adj[v])return false;} } return true; }

static long maxcut(const Graph&g,const int*verts,int m,long&Eout){
    if(m<=1){Eout=0;return 0;}
    static thread_local int idx[32];
    for(int i=0;i<N;i++) idx[i]=-1; for(int i=0;i<m;i++) idx[verts[i]]=i;
    Mask b[32]={0}; long E=0;
    for(int i=0;i<m;i++){int v=verts[i];Mask a=g.adj[v]; while(a){int w=__builtin_ctz(a);a&=a-1; if(idx[w]>=0&&w>v){b[idx[w]]|=(1u<<i);b[i]|=(1u<<idx[w]);E++;}}}
    Eout=E; long best=0; long lim=1L<<(m-1);
    for(long h=0;h<lim;h++){ Mask s1=(Mask)(h<<1); long cut=0; Mask x=s1; while(x){int v=__builtin_ctz(x);x&=x-1; cut+=popc(b[v]&~s1);} if(cut>best)best=cut; }
    return best;
}
static long betaFull(const Graph&g){ static thread_local std::vector<int> v; v.resize(N); for(int i=0;i<N;i++)v[i]=i; long E; long mc=maxcut(g,v.data(),N,E); return E-mc; }
static long betaMinus5(const Graph&g,const int*S){ static thread_local std::vector<int> r; r.clear(); int si=0; for(int i=0;i<N;i++){ if(si<5&&i==S[si]){si++;continue;} r.push_back(i);} long E; long mc=maxcut(g,r.data(),N-5,E); return E-mc; }

static long min5drop(const Graph&g,long bG){
    long mn=1L<<30; int S[5];
    for(S[0]=0;S[0]<N;S[0]++)for(S[1]=S[0]+1;S[1]<N;S[1]++)for(S[2]=S[1]+1;S[2]<N;S[2]++)
    for(S[3]=S[2]+1;S[3]<N;S[3]++)for(S[4]=S[3]+1;S[4]<N;S[4]++){
        long d=bG-betaMinus5(g,S); if(d<mn){mn=d; if(mn<=TARGET) return mn;} }
    return mn;
}

static Graph blowup(const std::vector<int>&parts){ Graph g; std::vector<std::vector<int>> grp(5); int idx=0; for(int p=0;p<5;p++){for(int j=0;j<parts[p];j++)grp[p].push_back(idx++);} for(int p=0;p<5;p++){int q=(p+1)%5; for(int u:grp[p])for(int v:grp[q]){g.adj[u]|=(1u<<v);g.adj[v]|=(1u<<u);}} return g; }
static Graph randMax(std::mt19937&rng){ Graph g; std::vector<std::pair<int,int>> pr; for(int u=0;u<N;u++)for(int v=u+1;v<N;v++)pr.push_back({u,v}); std::shuffle(pr.begin(),pr.end(),rng); for(auto&p:pr)addSafe(g,p.first,p.second); return g; }
static Graph perturb(Graph g,std::mt19937&rng,int steps){ long cur=betaFull(g); std::uniform_int_distribution<int> vd(0,N-1); for(int s=0;s<steps;s++){int u=vd(rng),v=vd(rng); if(u==v)continue; if(g.adj[u]&(1u<<v)){delE(g,u,v); long nb=betaFull(g); if(nb>=cur)cur=nb; else{g.adj[u]|=(1u<<v);g.adj[v]|=(1u<<u);}} else{ if(g.adj[u]&g.adj[v])continue; g.adj[u]|=(1u<<v);g.adj[v]|=(1u<<u); long nb=betaFull(g); if(nb>=cur)cur=nb; else delE(g,u,v);} } return g; }

// Petersen[2] on 20 vtx (the agent's non-C5-hom hard core), as a fixed seed for perturbs.
static Graph petersen2(){ Graph g; int E[][2]={{0,2},{0,3},{1,2},{1,3},{2,4},{2,5},{3,4},{3,5},{4,6},{4,7},{5,6},{5,7},{6,8},{6,9},{7,8},{7,9},{8,0},{8,1},{9,0},{9,1},{10,14},{10,15},{11,14},{11,15},{14,18},{14,19},{15,18},{15,19},{18,12},{18,13},{19,12},{19,13},{12,16},{12,17},{13,16},{13,17},{16,10},{16,11},{17,10},{17,11},{0,10},{0,11},{1,10},{1,11},{2,12},{2,13},{3,12},{3,13},{4,14},{4,15},{5,14},{5,15},{6,16},{6,17},{7,16},{7,17},{8,18},{8,19},{9,18},{9,19}}; for(auto&e:E){g.adj[e[0]]|=(1u<<e[1]);g.adj[e[1]]|=(1u<<e[0]);} return g; }

struct Res{ long tested=0; long worst=-99; long viol=0; std::vector<Graph> viols; long bh[40]={0}; };
static void consider(const Graph&g,Res&r){ if(!triFree(g))return; long bG=betaFull(g); if(bG<BAND_LO)return; long mn=min5drop(g,bG); r.tested++; if(bG<40)r.bh[bG]++; long m=mn-TARGET; if(m>r.worst)r.worst=m; if(m>0){r.viol++; if(r.viols.size()<10)r.viols.push_back(g);} }
static void worker(int tid,long nrand,long nhard,Res&out){ std::mt19937 rng(20260620u+tid*7919u); Res r;
    for(long i=0;i<nrand;i++){ Graph g=randMax(rng); consider(g,r); if(i%4==0)consider(perturb(g,rng,150),r);}
    if(N==20){ for(long i=0;i<nhard;i++){ consider(perturb(petersen2(),rng,150),r);} }
    out=r; }
static void printG(const Graph&g){ long b=betaFull(g); printf("    beta=%ld edges:",b); for(int u=0;u<N;u++){Mask a=g.adj[u]&(~((1u<<(u+1))-1)); while(a){int v=__builtin_ctz(a);a&=a-1; printf(" %d-%d",u,v);}} printf("\n"); }

int main(int argc,char**argv){
    N=argc>1?atoi(argv[1]):20; int nt=argc>2?atoi(argv[2]):16; long nr=argc>3?atol(argv[3]):8000; long nh=argc>4?atol(argv[4]):3000;
    int n=N/5; TARGET=2*n-1; BAND_LO=2*n;
    printf("H2 search N=%d (n=%d) target 2n-1=%d band_lo=%d threads=%d nrand/thr=%ld nhard/thr=%ld\n",N,n,TARGET,BAND_LO,nt,nr,nh); fflush(stdout);
    Res master;
    // blowup compositions of N into 5 parts
    for(int a=1;a<=N-4;a++)for(int b=1;b<=N-4;b++)for(int c=1;c<=N-4;c++)for(int d=1;d<=N-4;d++){ int e=N-a-b-c-d; if(e<1)continue; if(a+b+c+d+e!=N)continue; std::vector<int> p={a,b,c,d,e}; consider(blowup(p),master);}
    printf("blowups done: tested=%ld worstMargin=%ld\n",master.tested,master.worst); fflush(stdout);
    std::vector<Res> outs(nt); std::vector<std::thread> th; for(int t=0;t<nt;t++)th.emplace_back(worker,t,nr,nh,std::ref(outs[t])); for(auto&x:th)x.join();
    for(auto&r:outs){ master.tested+=r.tested; for(int i=0;i<40;i++)master.bh[i]+=r.bh[i]; if(r.worst>master.worst)master.worst=r.worst; master.viol+=r.viol; for(auto&g:r.viols)if(master.viols.size()<10)master.viols.push_back(g);}
    printf("\n==== H2 N=%d search complete ====\n",N);
    printf("tested (beta>=%d): %ld\n",BAND_LO,master.tested);
    printf("beta histogram:"); for(int i=BAND_LO;i<40;i++)if(master.bh[i])printf(" b%d=%ld",i,master.bh[i]); printf("\n");
    printf("worst margin (min_drop - %d): %ld  (>0 = H2 VIOLATION)\n",TARGET,master.worst);
    printf("# H2 violations: %ld\n",master.viol);
    for(auto&g:master.viols){ printf("  VIOLATION:\n"); printG(g);}
    return 0;
}
