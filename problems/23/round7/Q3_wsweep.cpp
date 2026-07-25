// Q3_wsweep.cpp -- round 7 label Q3.  Weighted sweep: for each pattern H and each total weight Q,
// steepest-ascent maximisation of  bip(H[w]) = min over cuts of sum_{mono} w_u w_v  over integer
// weight vectors w >= 0 with sum w = Q (ZERO WEIGHTS ALLOWED, as base (2) requires), then the exact
// distance d(H,w) to the C5-blow-up family at every local optimum found.
//
// Output TSV: g6  n  Q  bip  dist  weights  phi
// All arithmetic is exact 64-bit integer.  Randomness only chooses starting points.
//
// usage:  Q3_wsweep <patternfile> <Qlist,comma> <restarts> <threads>

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
#include <random>
#include <thread>
#include <mutex>
#include <iostream>

using namespace std;
static const int MAXN = 18;

struct Graph { int n; uint32_t adj[MAXN]; };

static bool parse_g6(const string &s, Graph &G) {
    if (s.empty()) return false;
    size_t p = 0; int n = (int)(s[0] - 63); p = 1;
    if (n == 63) { n = (((int)(s[1]-63))<<12)|(((int)(s[2]-63))<<6)|((int)(s[3]-63)); p = 4; }
    if (n <= 0 || n > MAXN) return false;
    G.n = n; for (int i=0;i<n;i++) G.adj[i]=0;
    int need = n*(n-1)/2; vector<int> bits; bits.reserve(need+6);
    for (size_t i=p;i<s.size() && (int)bits.size()<need;i++){ int c=(int)(s[i]-63); if(c<0||c>63) return false;
        for(int k=5;k>=0;k--) bits.push_back((c>>k)&1); }
    if ((int)bits.size()<need) return false;
    int idx=0; for(int j=1;j<n;j++) for(int i=0;i<j;i++){ if(bits[idx]){G.adj[i]|=1u<<j;G.adj[j]|=1u<<i;} idx++; }
    return true;
}

struct Eval {
    int n; uint32_t adj[MAXN];
    vector<long long> ws, ins;
    void init(const Graph &G){ n=G.n; for(int i=0;i<n;i++) adj[i]=G.adj[i]; ws.assign(1<<n,0); ins.assign(1<<n,0); }
    long long bip(const long long *w){
        int full=(1<<n)-1;
        ws[0]=0; ins[0]=0;
        for(int S=1;S<=full;S++){ int lo=S&(-S); int l=__builtin_ctz(lo); ws[S]=ws[S^lo]+w[l]; }
        for(int S=1;S<=full;S++){ int lo=S&(-S); int l=__builtin_ctz(lo); int rest=S^lo;
            ins[S]=ins[rest]+w[l]*ws[(int)adj[l]&rest]; }
        long long best=-1;
        for(int T=0;T<(1<<(n-1));T++){ int S=(T<<1)|1; long long v=ins[S]+ins[full^S]; if(best<0||v<best) best=v; }
        return best;
    }
};

struct DistSolver {
    int n; long long w[MAXN]; bool E[MAXN][MAXN]; int ord[MAXN];
    long long best; int phi[MAXN], bestphi[MAXN]; long long P[MAXN][5];
    static inline bool req(int a,int b){ int d=a-b; if(d<0)d=-d; return d==1||d==4; }
    inline long long pcost(int u,int v,int a,int b) const { bool need=req(a,b); return (E[u][v]!=need)? w[u]*w[v] : 0LL; }
    void greedy(){
        for(int i=0;i<n;i++) phi[ord[i]]=0;
        for(int i=0;i<n;i++){ int u=ord[i]; long long bc=-1; int ba=0;
            for(int a=0;a<5;a++){ long long c=0; for(int j=0;j<i;j++){int v=ord[j]; c+=pcost(u,v,a,phi[v]);} if(bc<0||c<bc){bc=c;ba=a;} }
            phi[u]=ba; }
        bool imp=true;
        while(imp){ imp=false;
            for(int u=0;u<n;u++){ long long bc=-1; int ba=phi[u];
                for(int a=0;a<5;a++){ long long c=0; for(int v=0;v<n;v++) if(v!=u) c+=pcost(u,v,a,phi[v]); if(bc<0||c<bc){bc=c;ba=a;} }
                if(ba!=phi[u]){phi[u]=ba;imp=true;} } }
        long long tot=0; for(int u=0;u<n;u++) for(int v=u+1;v<n;v++) tot+=pcost(u,v,phi[u],phi[v]);
        best=tot; for(int u=0;u<n;u++) bestphi[u]=phi[u];
    }
    void dfs(int depth,long long cost,bool rf){
        if(depth==n){ if(cost<best){best=cost; for(int u=0;u<n;u++) bestphi[u]=phi[u];} return; }
        long long lb=0;
        for(int j=depth;j<n;j++){ int u=ord[j]; long long m=P[u][0]; for(int a=1;a<5;a++) if(P[u][a]<m)m=P[u][a]; lb+=m; }
        if(cost+lb>=best) return;
        int u=ord[depth];
        int order[5]={0,1,2,3,4};
        for(int i=1;i<5;i++){int t=order[i];int j=i-1;while(j>=0&&P[u][order[j]]>P[u][t]){order[j+1]=order[j];j--;}order[j+1]=t;}
        for(int oi=0;oi<5;oi++){
            int a=order[oi];
            if(depth==0&&a!=0) continue;
            bool nrf=rf; if(!rf&&a!=0){ if(a==3||a==4) continue; nrf=true; }
            long long nc=cost+P[u][a]; if(nc>=best) continue;
            phi[u]=a;
            for(int j=depth+1;j<n;j++){int v=ord[j]; for(int b=0;b<5;b++) P[v][b]+=pcost(v,u,b,a);}
            dfs(depth+1,nc,nrf);
            for(int j=depth+1;j<n;j++){int v=ord[j]; for(int b=0;b<5;b++) P[v][b]-=pcost(v,u,b,a);}
        }
    }
    long long solve(const Graph &G,const long long *ww){
        n=G.n; for(int i=0;i<n;i++) w[i]=ww[i];
        for(int i=0;i<n;i++) for(int j=0;j<n;j++) E[i][j]=(i!=j)&&((G.adj[i]>>j)&1);
        vector<pair<long long,int>> d;
        for(int i=0;i<n;i++){ long long deg=0; for(int j=0;j<n;j++) if(E[i][j]) deg+=w[j]; d.push_back({-(deg*(w[i]+1)),i}); }
        sort(d.begin(),d.end()); for(int i=0;i<n;i++) ord[i]=d[i].second;
        greedy();
        for(int i=0;i<n;i++) for(int a=0;a<5;a++) P[i][a]=0;
        for(int i=0;i<n;i++) phi[i]=0;
        dfs(0,0,false);
        return best;
    }
};

static mutex outmtx;

int main(int argc,char**argv){
    if(argc<5){ fprintf(stderr,"usage: wsweep <patterns> <Qlist> <restarts> <threads>\n"); return 1; }
    vector<string> lines;
    { FILE*f=fopen(argv[1],"r"); if(!f){fprintf(stderr,"no file\n");return 1;} char buf[4096];
      while(fgets(buf,sizeof buf,f)){ string s(buf); while(!s.empty()&&(s.back()=='\n'||s.back()=='\r')) s.pop_back();
        if(!s.empty()) lines.push_back(s.substr(0,s.find_first_of(" \t"))); } fclose(f); }
    vector<int> Qs; { string q(argv[2]); size_t p=0; while(p<q.size()){ size_t c=q.find(',',p);
        string t=(c==string::npos)?q.substr(p):q.substr(p,c-p); Qs.push_back(atoi(t.c_str())); if(c==string::npos)break; p=c+1; } }
    int RESTARTS=atoi(argv[3]); int NTH=atoi(argv[4]);
    printf("g6\tn\tQ\tbip\tdist\tw\tphi\n");
    vector<thread> th;
    size_t total=lines.size();
    for(int t=0;t<NTH;t++){
        th.emplace_back([&,t](){
            mt19937 rng(12345+1000*t);
            Graph G; Eval ev; DistSolver DS;
            for(size_t li=t; li<total; li+=NTH){
                if(!parse_g6(lines[li],G)) continue;
                ev.init(G);
                int n=G.n;
                for(int Q : Qs){
                    // collect distinct local optima
                    vector<pair<long long,vector<long long>>> found;
                    for(int r=0;r<RESTARTS;r++){
                        long long w[MAXN]; for(int i=0;i<n;i++) w[i]=0;
                        if(r==0){ for(int i=0;i<Q;i++) w[i%n]++; }
                        else { for(int i=0;i<Q;i++) w[rng()%n]++; }
                        long long cur=ev.bip(w);
                        bool improved=true;
                        while(improved){
                            improved=false; long long bestv=cur; int bi=-1,bj=-1;
                            for(int i=0;i<n;i++){ if(w[i]==0) continue;
                                for(int j=0;j<n;j++){ if(i==j) continue;
                                    w[i]--; w[j]++;
                                    long long v=ev.bip(w);
                                    w[i]++; w[j]--;
                                    if(v>bestv){ bestv=v; bi=i; bj=j; } } }
                            if(bi>=0){ w[bi]--; w[bj]++; cur=bestv; improved=true; }
                        }
                        vector<long long> wv(w,w+n);
                        bool dup=false;
                        for(auto&f:found) if(f.first==cur&&f.second==wv){dup=true;break;}
                        if(!dup) found.push_back({cur,wv});
                    }
                    for(auto&f:found){
                        long long w[MAXN]; for(int i=0;i<n;i++) w[i]=f.second[i];
                        long long dd=DS.solve(G,w);
                        string ws,ps;
                        for(int i=0;i<n;i++){ if(i)ws+=","; ws+=to_string(w[i]); }
                        for(int i=0;i<n;i++) ps+=(char)('0'+DS.bestphi[i]);
                        lock_guard<mutex> lk(outmtx);
                        printf("%s\t%d\t%d\t%lld\t%lld\t%s\t%s\n",lines[li].c_str(),n,Q,f.first,dd,ws.c_str(),ps.c_str());
                    }
                }
            }
        });
    }
    for(auto&x:th) x.join();
    return 0;
}
