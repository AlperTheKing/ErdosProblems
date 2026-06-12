// Stream-check SMS graph lines: classify 3col / not-vertex-critical / vc-with-critical-edge / TARGET
// usage: check_stream.exe N < sms_output.txt
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <iostream>
using namespace std;
static int N;
static const int MAXN=32;
struct G{uint32_t adj[MAXN];
 bool has(int u,int v)const{return (adj[u]>>v)&1;}void add(int u,int v){adj[u]|=1u<<v;adj[v]|=1u<<u;}
 int deg(int u)const{return __builtin_popcount(adj[u]);}};
static bool col3(const G&g,uint32_t rm,int eu=-1,int ev=-1){
 int idx[MAXN],m=0;for(int v=0;v<N;v++)if(!((rm>>v)&1))idx[m++]=v;
 for(int i=1;i<m;i++){int k=idx[i],j=i-1;while(j>=0&&g.deg(idx[j])<g.deg(k)){idx[j+1]=idx[j];j--;}idx[j+1]=k;}
 int8_t color[MAXN];memset(color,-1,sizeof(color));int pos=0;int8_t tryc[MAXN];memset(tryc,0,sizeof(tryc));
 while(pos>=0){if(pos==m)return true;int v=idx[pos];bool adv=false;
  for(int c=tryc[pos];c<3;c++){bool ok=true;uint32_t nb=g.adj[v];
   while(nb){int u=__builtin_ctz(nb);nb&=nb-1;if((rm>>u)&1)continue;
    if(eu>=0&&((u==eu&&v==ev)||(u==ev&&v==eu)))continue;if(color[u]==c){ok=false;break;}}
   if(ok){color[v]=c;tryc[pos]=c+1;pos++;if(pos<m)tryc[pos]=0;adv=true;break;}}
  if(!adv){color[v]=-1;tryc[pos]=0;pos--;}}
 return false;}
int main(int argc,char**argv){
 N=argc>1?atoi(argv[1]):12;
 string line; long long total=0,c3=0,notvc=0,vccrit=0,target=0;
  while(getline(cin,line)){
  if(line.size()<3||line[0]!='[') continue;
  G g; memset(g.adj,0,sizeof(g.adj));
  // parse (a,b) pairs
  const char*s=line.c_str();
  while(*s){
   if(*s=='('){int a=0,b=0; s++; while(*s>='0'&&*s<='9'){a=a*10+(*s-'0');s++;} s++; while(*s>='0'&&*s<='9'){b=b*10+(*s-'0');s++;}
    g.add(a,b);} else s++;
  }
  total++;
  if(total % 10000 == 0){
   fprintf(stderr,
    "PROGRESS total=%lld threecol=%lld notVC=%lld vcWithCritEdge=%lld TARGET=%lld\n",
    total,c3,notvc,vccrit,target);
   fflush(stderr);
  }
  if(col3(g,0)){c3++;continue;}
  bool vc=true;
  for(int v=0;v<N&&vc;v++) if(!col3(g,1u<<v)) vc=false;
  if(!vc){notvc++;continue;}
  bool crit=false;
  for(int u=0;u<N&&!crit;u++){uint32_t nb=g.adj[u];
   while(nb){int v=__builtin_ctz(nb);nb&=nb-1;if(v<u)continue;
    if(col3(g,0,u,v)){crit=true;break;}}}
  if(crit){vccrit++; printf("VC_WITH_CRIT: %s\n", line.c_str()); fflush(stdout);
   continue;}
  target++;
  printf("TARGET: %s\n", line.c_str()); fflush(stdout);
 }
 printf("total=%lld threecol=%lld notVC=%lld vcWithCritEdge=%lld TARGET=%lld\n",total,c3,notvc,vccrit,target);
 return 0;}
