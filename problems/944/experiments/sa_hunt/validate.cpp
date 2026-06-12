#include <cstdio>
#include <cstdint>
#include <cstring>
static const int MAXN=20;
struct G{int n;uint32_t adj[MAXN];void clear(int n_){n=n_;memset(adj,0,sizeof(adj));}
 bool has(int u,int v)const{return (adj[u]>>v)&1;}void add(int u,int v){adj[u]|=1u<<v;adj[v]|=1u<<u;}
 int deg(int u)const{return __builtin_popcount(adj[u]);}};
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
static void report(const char*name,const G&g){
 bool c3=col3(g,0);int bv=0,ce=0;
 for(int v=0;v<g.n;v++)if(!col3(g,1u<<v))bv++;
 for(int u=0;u<g.n;u++)for(int v=u+1;v<g.n;v++)if(g.has(u,v)&&col3(g,0,u,v))ce++;
 printf("%s: 3col=%d badV=%d critE=%d\n",name,c3,bv,ce);}
int main(){
 G k4;k4.clear(4);for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)k4.add(i,j);
 report("K4(expect 0,0,6)",k4);
 // Grotzsch: vertices 0-4 outer C5, 5-9 inner (i+5 adj to outer i-1,i+1 mod5), 10 hub adj to all inner
 G gz;gz.clear(11);
 for(int i=0;i<5;i++)gz.add(i,(i+1)%5);
 for(int i=0;i<5;i++){gz.add(i+5,(i+4)%5);gz.add(i+5,(i+1)%5);}
 for(int i=0;i<5;i++)gz.add(10,i+5);
 report("Grotzsch(expect 0,0,20)",gz);
 // C5 (3-colorable sanity)
 G c5;c5.clear(5);for(int i=0;i<5;i++)c5.add(i,(i+1)%5);
 report("C5(expect 1,-,-)",c5);
 return 0;}
