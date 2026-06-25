// Diagonal-partner criticality-feasibility, C++ port (split-INDEPENDENT form).
// unlock(w): B-w has a proper 3-colouring with some colour absent from the six
// cut units (units on deleted w removed). [T_p u T_l = all 6 units, split-free.]
// B criticality-feasible <=> every vertex w unlocks. Count feasible always-bal B.
// usage: geng -c -D6 n e:e | diag_unlock n
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <iostream>
using namespace std;
static int N;
static const int MAXN = 32;
struct G { uint32_t adj[MAXN]; int deg(int u) const { return __builtin_popcount(adj[u]); } };
static int Bdef[MAXN];

// enumerate proper 3-colourings of G minus 'skip' (skip<0 = none); callback cb(col[]).
// cb returns true to stop early.
template<class CB>
static bool eachCol(const G& g, int skip, CB cb) {
  int order[MAXN], m = 0;
  for (int v = 0; v < N; v++) if (v != skip) order[m++] = v;
  for (int i = 1; i < m; i++){int k=order[i],j=i-1;while(j>=0&&g.deg(order[j])<g.deg(k)){order[j+1]=order[j];j--;}order[j+1]=k;}
  int8_t col[MAXN]; memset(col,-1,sizeof(col));
  int8_t tryc[MAXN]; memset(tryc,0,sizeof(tryc));
  int pos=0;
  while(pos>=0){
    if(pos==m){ if(cb(col)) return true; pos--; if(pos>=0)col[order[pos]]=-1; continue; }
    int x=order[pos]; bool adv=false;
    for(int c=tryc[pos];c<3;c++){
      bool ok=true; uint32_t nb=g.adj[x];
      while(nb){int u=__builtin_ctz(nb);nb&=nb-1; if(u==skip)continue; if(col[u]==c){ok=false;break;}}
      if(ok){col[x]=c;tryc[pos]=c+1;pos++;if(pos<m)tryc[pos]=0;adv=true;break;}
    }
    if(!adv){col[x]=-1;tryc[pos]=0;pos--;if(pos>=0)col[order[pos]]=-1;}
  }
  return false;
}
static bool alwaysBalanced(const G& g){
  bool any=false;
  bool bad = eachCol(g,-1,[&](const int8_t*col){
    int w[3]={0,0,0}; for(int v=0;v<N;v++) w[col[v]]+=Bdef[v];
    any=true;
    return !(w[0]==2&&w[1]==2&&w[2]==2);   // stop (true) if a colouring is unbalanced
  });
  return any && !bad;
}
// w unlocks: some colouring of g-w has a colour absent from the 6 units (minus w's units)
static bool unlocks(const G& g, int w, const vector<int>& units){
  return eachCol(g,w,[&](const int8_t*col){
    int present[3]={0,0,0};
    for(int v:units){ if(v==w)continue; present[col[v]]=1; }
    return !(present[0]&&present[1]&&present[2]);  // stop(true) if some colour missing
  });
}
static bool g6decode(const string& line, G& g){
  if(line.empty())return false; int n=line[0]-63; if(n!=N)return false;
  memset(g.adj,0,sizeof(g.adj));
  int nbits=n*(n-1)/2,need=(nbits+5)/6; if((int)line.size()<1+need)return false;
  int bit=0;
  for(int j=1;j<n;j++)for(int i=0;i<j;i++){int byte=1+bit/6,off=5-bit%6;
    if((line[byte]-63)>>off&1){g.adj[i]|=1u<<j;g.adj[j]|=1u<<i;}bit++;}
  return true;
}
int main(int argc,char**argv){
  N=argc>1?atoi(argv[1]):12;
  string line; long long total=0,ab=0,feasible=0;
  while(getline(cin,line)){
    while(!line.empty()&&(line.back()=='\r'||line.back()=='\n'))line.pop_back();
    if(line.empty()||line[0]=='>')continue;
    G g; if(!g6decode(line,g))continue;
    total++;
    int sb=0; for(int v=0;v<N;v++){Bdef[v]=6-g.deg(v);sb+=Bdef[v];} if(sb!=6)continue;
    if(!alwaysBalanced(g))continue;
    ab++;
    vector<int> units; for(int v=0;v<N;v++) for(int k=0;k<Bdef[v];k++) units.push_back(v);
    bool allUnlock=true;
    for(int w=0;w<N;w++){ if(!unlocks(g,w,units)){allUnlock=false;break;} }
    if(allUnlock){ feasible++; printf("FEASIBLE g6=%s\n",line.c_str()); }
  }
  printf("n=%d total=%lld alwaysBalanced=%lld criticalityFeasible=%lld\n",N,total,ab,feasible);
  return 0;
}
