// Q3_exhaust.cpp -- round 7 label Q3.
// EXHAUSTIVE exact enumeration of ALL integer weightings w >= 0 with sum w = Q on a fixed pattern H
// (zero weights allowed, as base (2) requires), computing for each
//      bip(H[w]) = min over cuts of sum_{mono} w_u w_v          (exact integer)
//      dist(H,w) = min over phi:V->Z5 of the weighted edit distance to the C5-blow-up family
// and returning the exact PARETO FRONTIER  D -> max{ bip : dist = D },
// i.e. the exact empirical trade-off curve for that pattern at that total weight.
//
// dist is only computed when bip already exceeds a threshold (num/den of Q^2), because only the
// upper envelope matters; everything below the threshold cannot affect the frontier above it.
//
// usage: Q3_exhaust <g6> <Q> <num> <den> <threads>
//        e.g.  Q3_exhaust GCrb`o 24 3 100 8      (Wagner graph, Q=24, only bip >= 0.03*Q^2)

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
#include <thread>
#include <mutex>

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
        int u=ord[depth]; int order[5]={0,1,2,3,4};
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

struct Worker {
    Graph G; int n; int Q; long long num, den;
    vector<long long> ws, ins;
    vector<long long> pareto;          // pareto[D] = max bip among weightings with dist == D
    vector<vector<long long>> witness; // witness weighting for that D
    long long bestbip = -1; vector<long long> bestw;
    long long bestfull = -1; vector<long long> bestfullw;   // best over FULL-support weightings
    DistSolver DS;
    long long w[MAXN];

    void init(const Graph &g,int q,long long nu,long long de){
        G=g; n=g.n; Q=q; num=nu; den=de;
        ws.assign(1<<n,0); ins.assign(1<<n,0);
        pareto.assign((size_t)Q*Q+1,-1); witness.assign((size_t)Q*Q+1,{});
    }
    long long bip(){
        int full=(1<<n)-1;
        for(int S=1;S<=full;S++){ int lo=S&(-S); int l=__builtin_ctz(lo); ws[S]=ws[S^lo]+w[l]; }
        for(int S=1;S<=full;S++){ int lo=S&(-S); int l=__builtin_ctz(lo); int rest=S^lo;
            ins[S]=ins[rest]+w[l]*ws[(int)G.adj[l]&rest]; }
        long long best=-1;
        for(int T=0;T<(1<<(n-1));T++){ int S=(T<<1)|1; long long v=ins[S]+ins[full^S]; if(best<0||v<best) best=v; }
        return best;
    }
    void consider(){
        long long b=bip();
        bool full=true; for(int i=0;i<n;i++) if(w[i]==0) full=false;
        if(b>bestbip){ bestbip=b; bestw.assign(w,w+n); }
        if(full && b>bestfull){ bestfull=b; bestfullw.assign(w,w+n); }
        if(b*den < num*(long long)Q*Q) return;
        long long D=DS.solve(G,w);
        if(D>=0 && D<=(long long)Q*Q){
            if(b>pareto[D]){ pareto[D]=b; witness[D].assign(w,w+n); }
        }
    }
    void rec(int i,int rem){
        if(i==n-1){ w[i]=rem; consider(); return; }
        for(int v=rem; v>=0; v--){ w[i]=v; rec(i+1,rem-v); }
    }
};

int main(int argc,char**argv){
    if(argc<6){ fprintf(stderr,"usage: exhaust <g6> <Q> <num> <den> <threads>\n"); return 1; }
    Graph G; if(!parse_g6(argv[1],G)){ fprintf(stderr,"parse fail\n"); return 1; }
    int Q=atoi(argv[2]); long long num=atoll(argv[3]), den=atoll(argv[4]); int NT=atoi(argv[5]);
    int n=G.n;
    vector<Worker> W(NT);
    for(int t=0;t<NT;t++) W[t].init(G,Q,num,den);
    vector<thread> th;
    for(int t=0;t<NT;t++){
        th.emplace_back([&,t](){
            Worker &w=W[t];
            for(int v0=Q-t; v0>=0; v0-=NT){    // split on the first coordinate
                w.w[0]=v0; w.rec(1,Q-v0);
            }
        });
    }
    for(auto&x:th) x.join();
    // merge
    Worker M; M.init(G,Q,num,den);
    for(int t=0;t<NT;t++){
        for(size_t D=0;D<M.pareto.size();D++)
            if(W[t].pareto[D]>M.pareto[D]){ M.pareto[D]=W[t].pareto[D]; M.witness[D]=W[t].witness[D]; }
        if(W[t].bestbip>M.bestbip){ M.bestbip=W[t].bestbip; M.bestw=W[t].bestw; }
        if(W[t].bestfull>M.bestfull){ M.bestfull=W[t].bestfull; M.bestfullw=W[t].bestfullw; }
    }
    printf("# pattern %s n=%d Q=%d  (bip and dist are exact integers; psi=bip/Q^2, d=dist/Q^2)\n",argv[1],n,Q);
    printf("# best bip overall = %lld  (psi = %lld/%d)  w =",M.bestbip,M.bestbip,Q*Q);
    for(size_t i=0;i<M.bestw.size();i++) printf("%s%lld",i?",":" ",M.bestw[i]); printf("\n");
    printf("# best bip full support = %lld  (psi = %lld/%d)  w =",M.bestfull,M.bestfull,Q*Q);
    for(size_t i=0;i<M.bestfullw.size();i++) printf("%s%lld",i?",":" ",M.bestfullw[i]); printf("\n");
    printf("dist\tmaxbip\tw\n");
    // report the monotone upper envelope: for each D, max over dist >= D
    long long run=-1; vector<long long> runw;
    for(int D=(int)M.pareto.size()-1; D>=0; D--){
        if(M.pareto[D]>run){ run=M.pareto[D]; runw=M.witness[D]; }
        if(M.pareto[D]>=0){
            printf("%d\t%lld\t",D,M.pareto[D]);
            for(size_t i=0;i<M.witness[D].size();i++) printf("%s%lld",i?",":"",M.witness[D][i]);
            printf("\n");
        }
    }
    return 0;
}
