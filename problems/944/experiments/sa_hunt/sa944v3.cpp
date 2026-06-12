// v3: sample random 4-edge-critical H, then SA over extra-edge sets S only.
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <random>
#include <thread>
#include <atomic>
#include <vector>
#include <mutex>
#include <algorithm>
#include <cmath>
using namespace std;
static const int MAXN=32;
struct G{int n;uint32_t adj[MAXN];void clear(int n_){n=n_;memset(adj,0,sizeof(adj));}
 bool has(int u,int v)const{return (adj[u]>>v)&1;}void add(int u,int v){adj[u]|=1u<<v;adj[v]|=1u<<u;}
 void del(int u,int v){adj[u]&=~(1u<<v);adj[v]&=~(1u<<u);}int deg(int u)const{return __builtin_popcount(adj[u]);}};
static bool col3(const G&g,uint32_t rm,int eu=-1,int ev=-1){
 int idx[MAXN],m=0;for(int v=0;v<g.n;v++)if(!((rm>>v)&1))idx[m++]=v;
 for(int i=1;i<m;i++){int k=idx[i],j=i-1;while(j>=0&&g.deg(idx[j])<g.deg(k)){idx[j+1]=idx[j];j--;}idx[j+1]=k;}
 int8_t color[MAXN];memset(color,-1,sizeof(color));int pos=0;int8_t tryc[MAXN];memset(tryc,0,sizeof(tryc));
 while(pos>=0){if(pos==m)return true;int v=idx[pos];bool adv=false;
  for(int c=tryc[pos];c<3;c++){bool ok=true;uint32_t nb=g.adj[v];
   while(nb){int u=__builtin_ctz(nb);nb&=nb-1;if((rm>>u)&1)continue;
    if(eu>=0&&((u==eu&&v==ev)||(u==ev&&v==eu)))continue;if(color[u]==c){ok=false;break;}}
   if(ok){color[v]=c;tryc[pos]=c+1;pos++;if(pos<m)tryc[pos]=0;adv=true;break;}}
  if(!adv){color[v]=-1;tryc[pos]=0;pos--;}}
 return false;}
static mutex outmx; static atomic<bool> found(false);
// generate a random 4-edge-critical H on n vertices
static bool gen4critical(G&h,int n,mt19937&rng,double p){
 for(int tries=0;tries<200;tries++){
  h.clear(n);
  for(int u=0;u<n;u++)for(int v=u+1;v<n;v++) if(uniform_real_distribution<double>(0,1)(rng)<p) h.add(u,v);
  if(col3(h,0)) continue; // need 4-chromatic (assume <=4 since random dense-ish; we only need NOT 3-col)
  // delete non-critical edges greedily (random order) until edge-critical
  bool changed=true;
  while(changed){ changed=false;
   vector<pair<int,int>> es;
   for(int u=0;u<n;u++)for(int v=u+1;v<n;v++)if(h.has(u,v))es.push_back({u,v});
   shuffle(es.begin(),es.end(),rng);
   for(auto&e:es){ // e non-critical iff H-e still not 3-colorable
    if(!col3(h,0,e.first,e.second)){ h.del(e.first,e.second); changed=true; }
   }
  }
  // H now edge-critical 4-chromatic (every edge critical). check spanning/connected-ish: isolated vertices?
  bool iso=false; for(int v=0;v<n;v++) if(h.deg(v)==0) iso=true;
  if(iso) continue;
  return true;
 }
 return false;
}
static void worker(int n,unsigned seed){
 mt19937 rng(seed);
 while(!found.load()){
  G h; if(!gen4critical(h,n,rng,0.35+0.05*(seed%3))) continue;
  // SA over S subset of co-edges
  vector<pair<int,int>> co;
  for(int u=0;u<n;u++)for(int v=u+1;v<n;v++) if(!h.has(u,v)) co.push_back({u,v});
  if(co.empty()) continue;
  G g=h;
  auto obj=[&](int&ce,int&bv)->long long{
   bv=0; for(int v=0;v<n;v++) if(!col3(g,1u<<v)) bv++;
   ce=0; for(int u=0;u<n;u++)for(int v=u+1;v<n;v++) if(g.has(u,v)&&col3(g,0,u,v)) ce++;
   return (long long)bv*50+ce; };
  int ce,bv; long long cur=obj(ce,bv); long long best=cur;
  double T=6.0;
  for(int it=0; it<400000 && !found.load(); it++){
   if((it&511)==0){T*=0.997; if(T<0.05)T=6.0;}
   auto&e=co[rng()%co.size()];
   bool had=g.has(e.first,e.second);
   if(had) g.del(e.first,e.second); else g.add(e.first,e.second);
   int ce2,bv2; long long nxt=obj(ce2,bv2);
   if(nxt<=cur||exp((cur-nxt)/T)>uniform_real_distribution<double>(0,1)(rng)){
    cur=nxt; ce=ce2; bv=bv2; if(cur<best)best=cur;
    if(cur==0){ found.store(true); lock_guard<mutex>lk(outmx);
     printf("FOUND n=%d seed=%u\nedges:",n,seed);
     for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)if(g.has(a,b))printf(" %d-%d",a,b);
     printf("\n");fflush(stdout); return; }
   } else { if(had) g.add(e.first,e.second); else g.del(e.first,e.second); }
  }
  { lock_guard<mutex>lk(outmx);
    printf("n=%d seed=%u H-round best=%lld (last ce=%d bv=%d)\n",n,seed,best,ce,bv); fflush(stdout);}
 }
}
int main(int argc,char**argv){
 int nlo=argc>1?atoi(argv[1]):11, nhi=argc>2?atoi(argv[2]):18, threads=argc>3?atoi(argv[3]):36;
 vector<thread> ts; int per=threads/(nhi-nlo+1)+1; unsigned s0=777;
 for(int n=nlo;n<=nhi;n++)for(int i=0;i<per;i++) ts.emplace_back(worker,n,s0+n*100+i);
 for(auto&t:ts)t.join(); return 0;
}
