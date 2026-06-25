// Forced-equal-class probe (Erdos #944, 2026-06-13).
// Over shore-shaped graphs (connected, Delta<=6, e=3n-3, sum b=6, 3-colourable),
// compute, for the union of ALL proper 3-colourings, the "forced-equal" relation:
//   u ~ v  iff  in EVERY proper 3-colouring phi, phi(u) == phi(v).
// A forced-equal class = an equivalence class of ~ of size >= 2.
// We also compute the "forced-different" relation:
//   u <> v iff in EVERY proper 3-colouring phi, phi(u) != phi(v)
// and the max clique in <> (a forced-rainbow set; size <=3 trivially).
//
// For each graph we report the largest forced-equal class, the deficiency
// b-multiset of its members, and the boundary-vector type (the deficiency-
// weighted colour multiset of any colouring; we record the SET of types seen).
//
// We additionally apply the [B][C] necessary shore filters (deficiency in
// [0,5]; every colouring's weighted boundary vector in the 5 allowed types)
// to mirror the published shore enumeration. (We do NOT apply [T]/[K] here;
// the point is to find forced-equal classes among CANDIDATE shores.)
//
// usage: geng -c -D6 n <3n-3>:<3n-3> | forced_equal_probe n
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <functional>
#include <iostream>
using namespace std;
static int N;
static const int MAXN = 20;
struct G { uint32_t adj[MAXN]; int deg(int u) const { return __builtin_popcount(adj[u]); } };
static int Bdef[MAXN];

// Enumerate all proper 3-colourings; accumulate per-pair "ever-equal" and
// "ever-different" bitsets. Also collect the set of boundary-vector types.
// Returns number of colourings (0 if not 3-colourable). pairEq[i] has bit j set
// if some colouring gives col[i]==col[j]; pairDiff[i] bit j if some gives !=.
struct ColStats {
  long long nCol = 0;
  uint32_t everEq[MAXN];   // bit j set if exists a colouring with col[i]==col[j]
  uint32_t everDiff[MAXN]; // bit j set if exists a colouring with col[i]!=col[j]
  int typeMask = 0;        // bits for which of the 5 types appeared
  bool badType = false;
};
// classify weighted boundary vector (sorted desc) into one of 5 types; -1 bad
static int boundaryType(int w0,int w1,int w2){
  int w[3]={w0,w1,w2}; sort(w,w+3); // ascending
  // sorted ascending: compare to sorted forms of the 5 types
  // (6,0,0)->0,0,6 ; (3,3,0)->0,3,3 ; (4,1,1)->1,1,4 ; (2,2,2)->2,2,2
  if(w[0]==0&&w[1]==0&&w[2]==6) return 0;
  if(w[0]==0&&w[1]==3&&w[2]==3) return 1;
  if(w[0]==1&&w[1]==1&&w[2]==4) return 2;
  if(w[0]==2&&w[1]==2&&w[2]==2) return 3;
  return -1;
}
static void colStats(const G& g, ColStats& st){
  for(int i=0;i<N;i++){st.everEq[i]=0;st.everDiff[i]=0;}
  st.nCol=0; st.typeMask=0; st.badType=false;
  int order[MAXN]; for(int i=0;i<N;i++)order[i]=i;
  sort(order,order+N,[&](int a,int b){return g.deg(a)>g.deg(b);});
  int8_t col[MAXN]; memset(col,-1,sizeof(col));
  int8_t tryc[MAXN]; memset(tryc,0,sizeof(tryc));
  int pos=0;
  while(pos>=0){
    if(pos==N){
      st.nCol++;
      int w[3]={0,0,0};
      for(int v=0;v<N;v++) w[col[v]]+=Bdef[v];
      int t=boundaryType(w[0],w[1],w[2]);
      if(t<0) st.badType=true; else st.typeMask|=(1<<t);
      for(int i=0;i<N;i++) for(int j=i+1;j<N;j++){
        if(col[i]==col[j]){ st.everEq[i]|=1u<<j; st.everEq[j]|=1u<<i; }
        else { st.everDiff[i]|=1u<<j; st.everDiff[j]|=1u<<i; }
      }
      pos--; { int y=order[pos]; col[y]=-1; }
      continue;
    }
    int x=order[pos]; bool adv=false;
    for(int c=tryc[pos];c<3;c++){
      bool ok=true; uint32_t nb=g.adj[x];
      while(nb){int u=__builtin_ctz(nb);nb&=nb-1;if(col[u]==c){ok=false;break;}}
      if(ok){col[x]=c;tryc[pos]=c+1;pos++;if(pos<N)tryc[pos]=0;adv=true;break;}
    }
    if(!adv){tryc[pos]=0;pos--;if(pos>=0){int y=order[pos];col[y]=-1;}}
  }
}
static bool g6decode(const string& line, G& g){
  if(line.empty())return false;
  int n=line[0]-63; if(n!=N)return false;
  memset(g.adj,0,sizeof(g.adj));
  int nbits=n*(n-1)/2, need=(nbits+5)/6;
  if((int)line.size()<1+need)return false;
  int bit=0;
  for(int j=1;j<n;j++)for(int i=0;i<j;i++){int byte=1+bit/6,off=5-bit%6;
    if((line[byte]-63)>>off&1){g.adj[i]|=1u<<j;g.adj[j]|=1u<<i;} bit++;}
  return true;
}
int main(int argc,char**argv){
  N=argc>1?atoi(argv[1]):9;
  bool filterType = !(argc>2 && string(argv[2])=="notype"); // default: require all colourings valid-type
  string line; long long total=0, cand=0;
  // histograms
  long long histMaxEq[MAXN+1]={0};   // by max forced-equal class size
  long long sz3plus=0;
  while(getline(cin,line)){
    while(!line.empty()&&(line.back()=='\r'||line.back()=='\n'))line.pop_back();
    if(line.empty()||line[0]=='>')continue;
    G g; if(!g6decode(line,g))continue;
    total++;
    for(int v=0;v<N;v++)Bdef[v]=6-g.deg(v);
    int sb=0; bool baddef=false;
    for(int v=0;v<N;v++){ if(Bdef[v]<0||Bdef[v]>5)baddef=true; sb+=Bdef[v]; }
    if(baddef||sb!=6)continue;
    ColStats st; colStats(g,st);
    if(st.nCol==0) continue;          // not 3-colourable
    if(filterType && st.badType) continue; // [C] boundary-vector filter
    cand++;
    // forced-equal: u~v iff NOT everDiff (i.e. equal in every colouring) and u!=v
    // build classes by union-find over the "forced-equal" graph (edge iff !everDiff bit)
    int par[MAXN]; for(int i=0;i<N;i++)par[i]=i;
    function<int(int)> find=[&](int x){while(par[x]!=x){par[x]=par[par[x]];x=par[x];}return x;};
    for(int i=0;i<N;i++)for(int j=i+1;j<N;j++){
      bool forcedEq = !((st.everDiff[i]>>j)&1); // never different => always equal
      if(forcedEq){int a=find(i),b=find(j);if(a!=b)par[a]=b;}
    }
    int csz[MAXN]={0}; for(int i=0;i<N;i++)csz[find(i)]++;
    int maxEq=0,argMax=-1; for(int i=0;i<N;i++) if(csz[i]>maxEq){maxEq=csz[i];argMax=i;}
    histMaxEq[maxEq]++;
    if(maxEq>=3){
      sz3plus++;
      // report it
      vector<int> members; for(int i=0;i<N;i++) if(find(i)==argMax) members.push_back(i);
      string prof; for(int v: members){ prof+=('0'+Bdef[v]); }
      string tmask; for(int t=0;t<4;t++) if(st.typeMask&(1<<t)) tmask+=("ABCD"[t]); // A=(6,0,0)B=(3,3,0)C=(4,1,1)D=(2,2,2)
      printf("FE3+ g6=%s size=%d bdef={%s} types={%s} ncol=%lld\n",
             line.c_str(), maxEq, prof.c_str(), tmask.c_str(), st.nCol);
    }
  }
  printf("n=%d candidates=%lld (filterType=%d) maxEq-hist:", N, cand, (int)filterType);
  for(int k=1;k<=N;k++) if(histMaxEq[k]) printf(" %d:%lld", k, histMaxEq[k]);
  printf("\n forced-equal class size>=3 count=%lld\n", sz3plus);
  return 0;
}
