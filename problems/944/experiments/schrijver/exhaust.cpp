#include <cstdio>
#include <cstdint>
#include <cstring>
#include <thread>
#include <atomic>
#include <vector>
#include <mutex>
using namespace std;
#include "data.h"
static const int N=25;
struct G{uint32_t adj[N];
 bool has(int u,int v)const{return (adj[u]>>v)&1;}void add(int u,int v){adj[u]|=1u<<v;adj[v]|=1u<<u;}
 int deg(int u)const{return __builtin_popcount(adj[u]);}};
static bool col3(const G&g,uint32_t rm,int eu=-1,int ev=-1){
 int idx[N],m=0;for(int v=0;v<N;v++)if(!((rm>>v)&1))idx[m++]=v;
 for(int i=1;i<m;i++){int k=idx[i],j=i-1;while(j>=0&&g.deg(idx[j])<g.deg(k)){idx[j+1]=idx[j];j--;}idx[j+1]=k;}
 int8_t color[N];memset(color,-1,sizeof(color));int pos=0;int8_t tryc[N];memset(tryc,0,sizeof(tryc));
 while(pos>=0){if(pos==m)return true;int v=idx[pos];bool adv=false;
  for(int c=tryc[pos];c<3;c++){bool ok=true;uint32_t nb=g.adj[v];
   while(nb){int u=__builtin_ctz(nb);nb&=nb-1;if((rm>>u)&1)continue;
    if(eu>=0&&((u==eu&&v==ev)||(u==ev&&v==eu)))continue;if(color[u]==c){ok=false;break;}}
   if(ok){color[v]=c;tryc[pos]=c+1;pos++;if(pos<m)tryc[pos]=0;adv=true;break;}}
  if(!adv){color[v]=-1;tryc[pos]=0;pos--;}}
 return false;}
static mutex mx; static atomic<long long> tested(0), passdeg(0);
static void run(uint32_t lo, uint32_t hi){
 for(uint32_t s=lo;s<hi;s++){
  G g; memset(g.adj,0,sizeof(g.adj));
  for(int e=0;e<NSGE;e++) g.add(SGE[e][0],SGE[e][1]);
  for(int o=0;o<NORB;o++) if((s>>o)&1)
   for(int t=0;t<ORBLEN[o];t++) g.add(ORB[o][t][0],ORB[o][t][1]);
  tested++;
  bool degok=true; for(int v=0;v<N;v++) if(g.deg(v)<6){degok=false;break;}
  if(!degok) continue;
  passdeg++;
  if(col3(g,0)) continue;             // must stay 4-chromatic (it will, but cheap check)
  bool vcrit=true;
  for(int v=0;v<N&&vcrit;v++) if(!col3(g,1u<<v)) vcrit=false;
  if(!vcrit) continue;
  bool nocrit=true;
  for(int u=0;u<N&&nocrit;u++){uint32_t nb=g.adj[u];
   while(nb){int v=__builtin_ctz(nb);nb&=nb-1;if(v<u)continue;
    if(col3(g,0,u,v)){nocrit=false;break;}}}
  if(nocrit){ lock_guard<mutex>lk(mx);
   printf("*** FOUND subset=0x%x\n", s);
   for(int u=0;u<N;u++)for(int v=u+1;v<N;v++)if(g.has(u,v))printf("%d-%d ",u,v);
   printf("\n"); fflush(stdout); }
 }
}
int main(){
 const uint32_t TOT=1u<<NORB;
 int T=40; vector<thread> ts;
 for(int i=0;i<T;i++){uint32_t lo=(uint64_t)TOT*i/T, hi=(uint64_t)TOT*(i+1)/T; ts.emplace_back(run,lo,hi);}
 for(auto&t:ts)t.join();
 printf("done. tested=%lld degree-pass=%lld\n",(long long)tested,(long long)passdeg);
 return 0;}
