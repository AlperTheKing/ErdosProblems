// Diagonal-partner probe: among shore-shaped graphs (connected, Delta<=6,
// e=3n-3, sum b=6, 3-colourable), which are ALWAYS-BALANCED — every proper
// 3-colouring has deficiency-weighted colour vector exactly (2,2,2)?
// (These are the only possible partner shores B of a diagonal 3+3 shore A.)
// Reports: count; deficiency profile multiset; whether [T] holds.
// usage: geng -c -D6 n <e>:<e> | always_balanced n
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
static int B[MAXN];
// enumerate ALL proper 3-colourings; check every one gives weighted (2,2,2).
static bool alwaysBalanced(const G& g) {
  int order[MAXN];
  for (int i = 0; i < N; i++) order[i] = i;
  sort(order, order+N, [&](int a, int b){ return g.deg(a) > g.deg(b); });
  int8_t col[MAXN]; memset(col, -1, sizeof(col));
  int8_t tryc[MAXN]; memset(tryc, 0, sizeof(tryc));
  int pos = 0;
  bool any = false;
  while (pos >= 0) {
    if (pos == N) {
      int w[3] = {0,0,0};
      for (int v = 0; v < N; v++) w[col[v]] += B[v];
      if (!(w[0]==2 && w[1]==2 && w[2]==2)) return false;   // a non-(2,2,2) colouring
      any = true;
      pos--; { int y = order[pos]; col[y] = -1; }
      continue;
    }
    int x = order[pos]; bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      bool ok = true; uint32_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb-1; if (col[u]==c) { ok=false; break; } }
      if (ok) { col[x]=c; tryc[pos]=c+1; pos++; if (pos<N) tryc[pos]=0; adv=true; break; }
    }
    if (!adv) { tryc[pos]=0; pos--; if (pos>=0){ int y=order[pos]; col[y]=-1; } }
  }
  return any;   // 3-colourable AND every colouring balanced
}
static bool g6decode(const string& line, G& g) {
  if (line.empty()) return false;
  int n = line[0]-63; if (n != N) return false;
  memset(g.adj, 0, sizeof(g.adj));
  int nbits=n*(n-1)/2, need=(nbits+5)/6;
  if ((int)line.size()<1+need) return false;
  int bit=0;
  for (int j=1;j<n;j++) for (int i=0;i<j;i++){ int byte=1+bit/6,off=5-bit%6;
    if ((line[byte]-63)>>off&1){g.adj[i]|=1u<<j;g.adj[j]|=1u<<i;} bit++; }
  return true;
}
int main(int argc, char** argv){
  N = argc>1?atoi(argv[1]):9;
  string line; long long total=0, ab=0;
  while (getline(cin,line)){
    while(!line.empty()&&(line.back()=='\r'||line.back()=='\n'))line.pop_back();
    if(line.empty()||line[0]=='>')continue;
    G g; if(!g6decode(line,g))continue;
    total++;
    for(int v=0;v<N;v++)B[v]=6-g.deg(v);
    int sb=0; for(int v=0;v<N;v++)sb+=B[v]; if(sb!=6)continue;
    bool bad=false; for(int v=0;v<N;v++) if(B[v]>=3){bad=true;break;} // always-bal needs parts<=2
    if(bad){ /* still test: parts>=3 can't be always-balanced, skip */ }
    if(alwaysBalanced(g)){
      ab++;
      vector<int> prof; for(int v=0;v<N;v++) if(B[v])prof.push_back(B[v]);
      sort(prof.begin(),prof.end());
      string ps; for(int x:prof)ps+=('0'+x);
      printf("ALWAYS_BAL g6=%s profile=%s\n", line.c_str(), ps.c_str());
    }
  }
  printf("n=%d total=%lld alwaysBalanced=%lld\n", N, total, ab);
  return 0;
}
