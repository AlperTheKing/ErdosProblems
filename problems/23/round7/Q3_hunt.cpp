// Q3_hunt.cpp -- round 7 label Q3.  Direct hunt for the PERFECT-STABILITY constant.
//
// Pikhurko-Sliacan-Tyros: the problem is perfectly C5-stable iff there is C with
//        dist(G, C5-blow-ups)  <=  C * (deficit) .
// In the psi normalisation, for a pattern H with integer weights w (Q = sum w):
//        d      = dist / Q^2 ,      deficit = 1/25 - bip/Q^2 = (Q^2 - 25 bip)/(25 Q^2)
//        R      = d / deficit      =  25 * dist / (Q^2 - 25*bip)         <-- EXACT INTEGER RATIO
// so perfect stability fails iff R is unbounded.  Q^2 - 25*bip <= 0 with dist > 0 would be a
// COUNTEREXAMPLE to Erdos 23 and is reported as such.
//
// This program does steepest-ascent local search on R (exact rational comparison by cross
// multiplication) over integer weightings, with random restarts, and reports the largest R found.
//
// usage: Q3_hunt <patternfile> <Qlist> <restarts> <threads>

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

struct Eval {
    int n; uint32_t adj[MAXN]; vector<long long> ws, ins;
    void init(const Graph &G){ n=G.n; for(int i=0;i<n;i++) adj[i]=G.adj[i]; ws.assign(1<<n,0); ins.assign(1<<n,0); }
    long long bip(const long long *w){
        int full=(1<<n)-1;
        for(int S=1;S<=full;S++){ int lo=S&(-S); int l=__builtin_ctz(lo); ws[S]=ws[S^lo]+w[l]; }
        for(int S=1;S<=full;S++){ int lo=S&(-S); int l=__builtin_ctz(lo); int rest=S^lo;
            ins[S]=ins[rest]+w[l]*ws[(int)adj[l]&rest]; }
        long long best=-1;
        for(int T=0;T<(1<<(n-1));T++){ int S=(T<<1)|1; long long v=ins[S]+ins[full^S]; if(best<0||v<best) best=v; }
        return best;
    }
};

static mutex mtx;
static long long gbestNum=0, gbestDen=1; static string gbestLine;

int main(int argc,char**argv){
    if(argc<5){ fprintf(stderr,"usage: hunt <patterns> <Qlist> <restarts> <threads>\n"); return 1; }
    vector<string> lines;
    { FILE*f=fopen(argv[1],"r"); if(!f){fprintf(stderr,"no file\n");return 1;} char buf[4096];
      while(fgets(buf,sizeof buf,f)){ string s(buf); while(!s.empty()&&(s.back()=='\n'||s.back()=='\r')) s.pop_back();
        if(!s.empty()) lines.push_back(s.substr(0,s.find_first_of(" \t"))); } fclose(f); }
    vector<int> Qs; { string q(argv[2]); size_t p=0; while(p<q.size()){ size_t c=q.find(',',p);
        string t=(c==string::npos)?q.substr(p):q.substr(p,c-p); Qs.push_back(atoi(t.c_str())); if(c==string::npos)break; p=c+1; } }
    int RESTARTS=atoi(argv[3]); int NTH=atoi(argv[4]);
    printf("g6\tn\tQ\tbip\tdist\tRnum\tRden\tR\tw\n");
    vector<thread> th; size_t total=lines.size();
    for(int t=0;t<NTH;t++){
        th.emplace_back([&,t](){
            mt19937 rng(777+31*t); Graph G; Eval ev; DistSolver DS;
            for(size_t li=t; li<total; li+=NTH){
                if(!parse_g6(lines[li],G)) continue;
                ev.init(G); int n=G.n;
                for(int Q : Qs){
                    long long bnum=0,bden=1; vector<long long> bw; long long bbip=0,bdist=0;
                    for(int r=0;r<RESTARTS;r++){
                        long long w[MAXN]; for(int i=0;i<n;i++) w[i]=0;
                        if(r==0){ for(int i=0;i<Q;i++) w[i%n]++; }
                        else { for(int i=0;i<Q;i++) w[rng()%n]++; }
                        long long cb=ev.bip(w), cd=DS.solve(G,w);
                        long long cnum=25*cd, cden=(long long)Q*Q-25*cb;   // R = cnum/cden
                        bool improved=true;
                        while(improved){
                            improved=false;
                            long long bestnum=cnum,bestden=cden,bb=cb,bd=cd; int bi=-1,bj=-1;
                            for(int i=0;i<n;i++){ if(w[i]==0) continue;
                                for(int j=0;j<n;j++){ if(i==j) continue;
                                    w[i]--; w[j]++;
                                    long long nb=ev.bip(w);
                                    long long nden=(long long)Q*Q-25*nb;
                                    if(nden>0){
                                        long long nd=DS.solve(G,w);
                                        long long nnum=25*nd;
                                        // compare nnum/nden > bestnum/bestden  (all denominators > 0)
                                        if(bestden<=0 || nnum*bestden > bestnum*nden){
                                            bestnum=nnum; bestden=nden; bb=nb; bd=nd; bi=i; bj=j; }
                                    } else {
                                        long long nd=DS.solve(G,w);
                                        lock_guard<mutex> lk(mtx);
                                        printf("*** psi >= 1/25 : %s Q=%d bip=%lld dist=%lld w=",lines[li].c_str(),Q,nb,nd);
                                        for(int k=0;k<n;k++) printf("%s%lld",k?",":"",w[k]);
                                        printf("\n");
                                    }
                                    w[i]++; w[j]--; } }
                            if(bi>=0){ w[bi]--; w[bj]++; cnum=bestnum; cden=bestden; cb=bb; cd=bd; improved=true; }
                        }
                        if(cden>0 && cnum*bden > bnum*cden){ bnum=cnum; bden=cden; bw.assign(w,w+n); bbip=cb; bdist=cd; }
                    }
                    if(!bw.empty()){
                        string ws; for(int i=0;i<n;i++){ if(i)ws+=","; ws+=to_string(bw[i]); }
                        lock_guard<mutex> lk(mtx);
                        printf("%s\t%d\t%d\t%lld\t%lld\t%lld\t%lld\t%.4f\t%s\n",lines[li].c_str(),n,Q,bbip,bdist,
                               bnum,bden,(double)bnum/(double)bden,ws.c_str());
                        if((long long)bnum*gbestDen > (long long)gbestNum*bden){ gbestNum=bnum; gbestDen=bden;
                            gbestLine=lines[li]+" Q="+to_string(Q)+" w="+ws; }
                    }
                }
            }
        });
    }
    for(auto&x:th) x.join();
    fprintf(stderr,"# best R = %lld/%lld = %.6f  at %s\n",gbestNum,gbestDen,(double)gbestNum/(double)gbestDen,gbestLine.c_str());
    return 0;
}
