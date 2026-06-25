// Search for triangle-free graphs on N=20 with beta close to 16 that are NOT C5[4],
// then verify H2 (min 5-set drop <= 7). Generators: C5[4] perturbations, unbalanced
// C5 blow-ups of 20, random-maximal hill-climbs. Flags any min_drop>7.
// Build: clang++ -O3 -std=c++17 -pthread rt2_highbeta20.cpp -o rt2_highbeta20.exe
#include <cstdio>
#include <cstdint>
#include <vector>
#include <array>
#include <random>
#include <thread>
#include <algorithm>
static const int N=20; static const int TARGET=7; static const int BAND_LO=11;
typedef uint32_t Mask;
static inline int popc(unsigned x){return __builtin_popcount(x);}
struct Graph{ std::array<Mask,20> adj{}; };
static bool triFree(const Graph&g){ for(int u=0;u<N;u++){Mask a=g.adj[u]&(~((1u<<(u+1))-1)); while(a){int v=__builtin_ctz(a);a&=a-1; if(g.adj[u]&g.adj[v])return false;}} return true;}
static inline bool addSafe(Graph&g,int u,int v){ if(u==v)return false; if(g.adj[u]&(1u<<v))return false; if(g.adj[u]&g.adj[v])return false; g.adj[u]|=(1u<<v);g.adj[v]|=(1u<<u);return true;}
static inline void del(Graph&g,int u,int v){g.adj[u]&=~(1u<<v);g.adj[v]&=~(1u<<u);}
static int maxcut(const Graph&g,const int*verts,int m,int&Eout){ if(m<=1){Eout=0;return 0;} int idx[20];for(int i=0;i<20;i++)idx[i]=-1; for(int i=0;i<m;i++)idx[verts[i]]=i; uint32_t badj[20]={0};int E=0; for(int i=0;i<m;i++){int v=verts[i];Mask a=g.adj[v];while(a){int w=__builtin_ctz(a);a&=a-1;if(idx[w]>=0&&w>v){badj[idx[w]]|=(1u<<i);badj[i]|=(1u<<idx[w]);E++;}}} Eout=E; int best=0;long lim=1L<<(m-1); for(long h=0;h<lim;h++){uint32_t s1=(uint32_t)(h<<1);int cut=0;uint32_t x=s1;while(x){int v=__builtin_ctz(x);x&=x-1;cut+=popc(badj[v]&~s1);} if(cut>best)best=cut;} return best;}
static int betaFull(const Graph&g){int v[20];for(int i=0;i<20;i++)v[i]=i;int E;int mc=maxcut(g,v,20,E);return E-mc;}
static int betaMinus5(const Graph&g,const std::array<int,5>&S){int v[15];int k=0;bool in[20]={false};for(int i=0;i<5;i++)in[S[i]]=true;for(int i=0;i<20;i++)if(!in[i])v[k++]=i;int E;int mc=maxcut(g,v,15,E);return E-mc;}
static int min5drop(const Graph&g,int bG){int mn=999;std::array<int,5>S;
 for(S[0]=0;S[0]<N;S[0]++)for(S[1]=S[0]+1;S[1]<N;S[1]++)for(S[2]=S[1]+1;S[2]<N;S[2]++)for(S[3]=S[2]+1;S[3]<N;S[3]++)for(S[4]=S[3]+1;S[4]<N;S[4]++){int d=bG-betaMinus5(g,S);if(d<mn){mn=d;if(mn<=TARGET)return mn;}} return mn;}
static Graph blow5(std::array<int,5>p){Graph g;int grp[5][16];int idx=0;for(int q=0;q<5;q++)for(int j=0;j<p[q];j++)grp[q][j]=idx++;for(int q=0;q<5;q++){int r=(q+1)%5;for(int a=0;a<p[q];a++)for(int b=0;b<p[r];b++){int u=grp[q][a],v=grp[r][b];g.adj[u]|=(1u<<v);g.adj[v]|=(1u<<u);}}return g;}
static Graph randMax(std::mt19937&rng){Graph g;std::vector<std::pair<int,int>>pr;for(int u=0;u<N;u++)for(int v=u+1;v<N;v++)pr.push_back({u,v});std::shuffle(pr.begin(),pr.end(),rng);for(auto&e:pr)addSafe(g,e.first,e.second);return g;}
static Graph perturb(Graph g,std::mt19937&rng,int steps){int cur=betaFull(g);std::uniform_int_distribution<int>vd(0,N-1);for(int s=0;s<steps;s++){int u=vd(rng),v=vd(rng);if(u==v)continue;if(g.adj[u]&(1u<<v)){del(g,u,v);int nb=betaFull(g);if(nb>=cur)cur=nb;else{g.adj[u]|=(1u<<v);g.adj[v]|=(1u<<u);}}else{if(g.adj[u]&g.adj[v])continue;g.adj[u]|=(1u<<v);g.adj[v]|=(1u<<u);int nb=betaFull(g);if(nb>=cur)cur=nb;else del(g,u,v);}}return g;}
struct Res{long tested=0;int worst=-99;Graph wG;long viol=0;int hist[25]={0};int maxbeta=0;Graph maxbG;int maxbDrop=0;};
static void consider(const Graph&g,Res&r){ if(!triFree(g))return; int bG=betaFull(g); if(bG<BAND_LO)return; int mn=min5drop(g,bG); r.tested++; if(bG<25)r.hist[bG]++; if(bG>r.maxbeta){r.maxbeta=bG;r.maxbG=g;r.maxbDrop=mn;} int m=mn-TARGET; if(m>r.worst){r.worst=m;r.wG=g;} if(m>0)r.viol++; }
static void worker(int tid,long nrand,Res&out){ std::mt19937 rng(20260620u+tid*7919u); Res r;
 // unbalanced blowups of 20
 for(int a=1;a<=16;a++)for(int b=1;b<=16;b++)for(int c=1;c<=16;c++)for(int d=1;d<=16;d++){int e=20-a-b-c-d;if(e<1||e>16)continue; if(((a+b+c+d+e)%5)!=tid%5)continue; consider(blow5({a,b,c,d,e}),r);}
 for(long i=0;i<nrand;i++){ Graph g=randMax(rng); consider(g,r); Graph p=perturb(g,rng,200); consider(p,r); if(i%3==0){ Graph p2=perturb(blow5({4,4,4,4,4}),rng,200); consider(p2,r);} }
 out=r;}
int main(int argc,char**argv){int nthreads=argc>1?atoi(argv[1]):16;long nrand=argc>2?atol(argv[2]):6000;
 printf("HIGH-BETA N=20 search: threads=%d nrand/thr=%ld (band beta>=%d, target=%d)\n",nthreads,nrand,BAND_LO,TARGET);fflush(stdout);
 std::vector<Res>outs(nthreads);std::vector<std::thread>th;for(int t=0;t<nthreads;t++)th.emplace_back(worker,t,nrand,std::ref(outs[t]));for(auto&x:th)x.join();
 Res M;for(auto&r:outs){M.tested+=r.tested;for(int i=0;i<25;i++)M.hist[i]+=r.hist[i];if(r.worst>M.worst){M.worst=r.worst;M.wG=r.wG;}M.viol+=r.viol;if(r.maxbeta>M.maxbeta){M.maxbeta=r.maxbeta;M.maxbG=r.maxbG;M.maxbDrop=r.maxbDrop;}}
 printf("tested(beta>=%d): %ld\n",BAND_LO,M.tested);
 printf("beta histogram:");for(int i=BAND_LO;i<25;i++)if(M.hist[i])printf(" b%d=%d",i,M.hist[i]);printf("\n");
 printf("MAX beta found: %d  (its min5drop=%d, target=%d, margin=%+d)\n",M.maxbeta,M.maxbDrop,TARGET,M.maxbDrop-TARGET);
 printf("worst margin (min_drop-%d): %d   (>0 = H2 VIOLATION)\n",TARGET,M.worst);
 printf("# H2 violations: %ld\n",M.viol);
 // print worst graph edges
 printf("worst graph edges:");for(int u=0;u<N;u++){Mask a=M.wG.adj[u]&(~((1u<<(u+1))-1));while(a){int v=__builtin_ctz(a);a&=a-1;printf(" %d-%d",u,v);}}printf("\n");
 return 0;}
