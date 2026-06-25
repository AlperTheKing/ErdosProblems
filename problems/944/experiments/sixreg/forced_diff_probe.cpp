// Forced-DIFFERENT (forced-rainbow) probe (Erdos #944, 2026-06-13).
// The descent salvage lemma IDENTIFIES a non-adjacent set R such that K/R is
// non-3-colourable; the minimal such R is the rigidity core. K/(z1=z2) is
// non-3-colourable IFF z1,z2 are forced-DIFFERENT (distinct colour in every
// proper 3-colouring of G[K]).  So the descent contracts a forced-different set.
//
// Over shore-shaped graphs (connected, Delta<=6, e=3n-3, sum b=6, 3-colourable,
// every colouring's weighted boundary vector in the 5 allowed types):
//   1. Compute the forced-different relation D (u<>v iff col[u]!=col[v] in EVERY
//      proper 3-colouring).  A forced-different INDEPENDENT set = independent
//      clique of D.  Report max size of an independent forced-different set.
//   2. CRUCIAL minimality test: does there exist a NON-ADJACENT forced-different
//      PAIR?  (If a forced-rainbow triple exists, every pair in it is forced-
//      different; if also non-adjacent it gives a PAIR-merge core, so triple-
//      merge is never minimal.)  We report:
//        - hasNonadjFDpair: some non-adjacent {u,v} with K/(u=v) non-3-col
//        - for each forced-rainbow triple, whether it contains a non-adjacent FD pair
//   3. For non-adjacent FD pairs, the merged degree |N(u) u N(v)| (range check
//      vs the hunted single-merge band 6..10).
//
// usage: geng -c -D6 n <3n-3>:<3n-3> | forced_diff_probe n
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <iostream>
using namespace std;
static int N;
static const int MAXN = 20;
struct G { uint32_t adj[MAXN]; int deg(int u) const { return __builtin_popcount(adj[u]); } };
static int Bdef[MAXN];

static int boundaryType(int w0,int w1,int w2){
  int w[3]={w0,w1,w2}; sort(w,w+3);
  if(w[0]==0&&w[1]==0&&w[2]==6) return 0;
  if(w[0]==0&&w[1]==3&&w[2]==3) return 1;
  if(w[0]==1&&w[1]==1&&w[2]==4) return 2;
  if(w[0]==2&&w[1]==2&&w[2]==2) return 3;
  return -1;
}
struct Stats {
  long long nCol=0;
  uint32_t everSame[MAXN]; // bit j set if exists colouring with col[i]==col[j]
  bool badType=false;
};
static void colStats(const G& g, Stats& st){
  for(int i=0;i<N;i++) st.everSame[i]=0;
  st.nCol=0; st.badType=false;
  int order[MAXN]; for(int i=0;i<N;i++)order[i]=i;
  sort(order,order+N,[&](int a,int b){return g.deg(a)>g.deg(b);});
  int8_t col[MAXN]; memset(col,-1,sizeof(col));
  int8_t tryc[MAXN]; memset(tryc,0,sizeof(tryc));
  int pos=0;
  while(pos>=0){
    if(pos==N){
      st.nCol++;
      int w[3]={0,0,0}; for(int v=0;v<N;v++) w[col[v]]+=Bdef[v];
      if(boundaryType(w[0],w[1],w[2])<0) st.badType=true;
      for(int i=0;i<N;i++) for(int j=i+1;j<N;j++)
        if(col[i]==col[j]){ st.everSame[i]|=1u<<j; st.everSame[j]|=1u<<i; }
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
  string line; long long total=0, cand=0;
  long long histFDset[5]={0}; // max independent forced-different set size: 0,1,2,3,4(impossible)
  long long triplesWithNonadjPair=0, triplesTotal=0;
  long long candNoNonadjPair=0;     // candidates with NO non-adjacent FD pair (would force triple-merge!)
  long long candWithTripleNoPair=0; // candidate has FD triple but NO non-adjacent FD pair
  int dmin=99,dmax=0;               // merged-degree range over non-adjacent FD pairs
  long long du11=0;                 // non-adjacent FD pairs with merged degree >=11
  long long minDuPairDef[6]={0,0,0,0,0,0}; // histogram of min(b(r1),b(r2)) over MINIMAL-deg nonadj FD pair per cand
  long long pairBothDef0=0;         // candidates whose ONLY nonadj FD pairs are both-b=0
  while(getline(cin,line)){
    while(!line.empty()&&(line.back()=='\r'||line.back()=='\n'))line.pop_back();
    if(line.empty()||line[0]=='>')continue;
    G g; if(!g6decode(line,g))continue;
    total++;
    for(int v=0;v<N;v++)Bdef[v]=6-g.deg(v);
    int sb=0; bool baddef=false;
    for(int v=0;v<N;v++){ if(Bdef[v]<0||Bdef[v]>5)baddef=true; sb+=Bdef[v]; }
    if(baddef||sb!=6)continue;
    Stats st; colStats(g,st);
    if(st.nCol==0) continue;
    if(st.badType) continue;
    cand++;
    // forced-different graph FD: edge (i,j) iff never-same (i.e. !everSame bit) and i!=j
    // independent forced-different set = clique in FD that is independent in g.
    // Find max independent FD set (size<=3). Also find non-adjacent FD pair.
    bool hasNonadjPair=false;
    int maxFD=1;
    int bestMinDef=99;            // over nonadj FD pairs, the smallest-merged-degree pair: track its min(b)
    int bestDuForMinDef=99;
    bool anyPairHasDef=false;     // some nonadj FD pair has a deficient (b>=1) member
    // pairs
    for(int i=0;i<N;i++)for(int j=i+1;j<N;j++){
      bool fd = !((st.everSame[i]>>j)&1); // never same => forced different
      bool nonadj = !((g.adj[i]>>j)&1);
      if(fd){ if(maxFD<2)maxFD=2;
        if(nonadj){ hasNonadjPair=true;
          int d=__builtin_popcount((g.adj[i]|g.adj[j]) & ~((1u<<i)|(1u<<j)));
          if(d<dmin)dmin=d; if(d>dmax)dmax=d;
          if(d>=11) du11++;
          int mb=min(Bdef[i],Bdef[j]);
          if(mb>=1) anyPairHasDef=true;
          // track the pair that minimizes merged degree (the natural minimal-quotient choice)
          if(d<bestDuForMinDef){ bestDuForMinDef=d; bestMinDef=mb; }
        } }
    }
    if(hasNonadjPair){ if(bestMinDef<=5) minDuPairDef[bestMinDef]++;
      if(!anyPairHasDef) pairBothDef0++; }
    // triples (all pairwise FD AND pairwise non-adjacent => independent forced-rainbow triple)
    for(int i=0;i<N;i++)for(int j=i+1;j<N;j++)for(int k=j+1;k<N;k++){
      bool fdij=!((st.everSame[i]>>j)&1), fdik=!((st.everSame[i]>>k)&1), fdjk=!((st.everSame[j]>>k)&1);
      bool indij=!((g.adj[i]>>j)&1), indik=!((g.adj[i]>>k)&1), indjk=!((g.adj[j]>>k)&1);
      if(fdij&&fdik&&fdjk&&indij&&indik&&indjk){
        maxFD=3; triplesTotal++;
        // does this triple contain a NON-ADJACENT FD pair? all 3 pairs are FD+nonadj => yes
        triplesWithNonadjPair++;
      }
    }
    histFDset[maxFD]++;
    if(!hasNonadjPair) candNoNonadjPair++;
    if(maxFD==3 && !hasNonadjPair) candWithTripleNoPair++; // should be impossible (triple => its pairs are nonadj FD)
  }
  printf("n=%d candidates=%lld\n",N,cand);
  printf(" maxIndepForcedDiffSet hist:");
  for(int k=0;k<5;k++) if(histFDset[k]) printf(" %d:%lld",k,histFDset[k]);
  printf("\n");
  printf(" candidates with NO non-adjacent forced-diff PAIR = %lld\n", candNoNonadjPair);
  printf(" forced-rainbow independent triples total = %lld (all contain non-adj FD pairs: %lld)\n",
         triplesTotal, triplesWithNonadjPair);
  printf(" candidates having a triple but NO non-adj pair (would force triple-merge) = %lld\n", candWithTripleNoPair);
  if(dmax>0) printf(" non-adjacent FD pair merged-degree range = [%d,%d]\n", dmin, dmax);
  printf(" non-adjacent FD pairs with merged degree >=11 = %lld\n", du11);
  printf(" min-degree nonadj FD pair: min(b) histogram:");
  for(int k=0;k<6;k++) if(minDuPairDef[k]) printf(" b>=%d? bucket%d:%lld",k,k,minDuPairDef[k]);
  printf("\n candidates where EVERY nonadj FD pair is both-b=0 (no deficient member) = %lld\n", pairBothDef0);
  return 0;
}
