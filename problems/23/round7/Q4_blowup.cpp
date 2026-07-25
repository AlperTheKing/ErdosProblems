// Q4: exact integer exhaustive blow-up check of the 1/25 ceiling on a pattern H.
// For every integer weight vector a >= 0 with sum a = N (zeros allowed, per ACCEPTED BASE 2),
// computes bip(H[a]) = min over cuts S of H of sum_{uv mono} a_u a_v  in exact integers,
// and reports max over a of 25*bip - N^2 (>0 would be a counterexample).
// Usage: Q4_blowup <n> <Nmax> with the edge list / cut list compiled in (Gamma_8 by default).
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <array>
#include <thread>
#include <mutex>
#include <algorithm>
using namespace std;

static int n;
static vector<pair<int,int>> E;
static vector<vector<pair<int,int>>> CUTS; // per cut: list of monochromatic edges

static void build_gamma(int m){
    n=m; E.clear();
    for(int i=0;i<m;i++) for(int j=i+1;j<m;j++){ int d=min(j-i,m-(j-i)); if(3*d>m) E.push_back({i,j}); }
}
static void build_cuts(){
    CUTS.clear();
    vector<vector<int>> monosets;
    for(long long mask=0; mask< (1LL<<(n-1)); mask++){
        vector<int> mono;
        for(size_t k=0;k<E.size();k++){
            int u=E[k].first,v=E[k].second;
            int su = u==0?0:int((mask>>(u-1))&1), sv = v==0?0:int((mask>>(v-1))&1);
            if(su==sv) mono.push_back((int)k);
        }
        monosets.push_back(mono);
    }
    // keep inclusion-minimal ones
    for(size_t i=0;i<monosets.size();i++){
        bool dominated=false;
        for(size_t j=0;j<monosets.size() && !dominated;j++){
            if(i==j) continue;
            if(monosets[j].size()>=monosets[i].size()) continue;
            bool sub=true;
            for(int e: monosets[j]) if(!binary_search(monosets[i].begin(),monosets[i].end(),e)){sub=false;break;}
            if(sub) dominated=true;
        }
        if(!dominated){
            vector<pair<int,int>> c;
            for(int e: monosets[i]) c.push_back(E[e]);
            // dedupe identical sets
            bool dup=false;
            for(auto&o:CUTS) if(o==c){dup=true;break;}
            if(!dup) CUTS.push_back(c);
        }
    }
}

struct Best { long long val; array<int,16> a; int N; };
static mutex mtx;
static Best gbest{-1LL<<60,{},0};

static void rec(int idx, int rem, array<int,16>& a, int N){
    if(idx==n-1){
        a[n-1]=rem;
        long long best=-1;
        for(auto& c: CUTS){
            long long s=0;
            for(auto& e: c) s += (long long)a[e.first]*a[e.second];
            if(best<0||s<best) best=s;
            if(best==0) break;
        }
        long long score = 25*best - (long long)N*N;
        if(score>gbest.val){ lock_guard<mutex> g(mtx); if(score>gbest.val){ gbest.val=score; gbest.a=a; gbest.N=N; } }
        return;
    }
    for(int v=0;v<=rem;v++){ a[idx]=v; rec(idx+1,rem-v,a,N); }
    a[idx]=0;
}

int main(int argc,char**argv){
    int m = argc>1?atoi(argv[1]):8;
    int Nmax = argc>2?atoi(argv[2]):30;
    build_gamma(m); build_cuts();
    printf("Gamma_%d: n=%d |E|=%zu non-dominated cuts=%zu\n",m,n,E.size(),CUTS.size());
    for(int N=1;N<=Nmax;N++){
        gbest.val=-1LL<<60;
        // parallelise over a[0]
        vector<thread> th; int nth=8;
        vector<Best> loc(nth);
        for(int t=0;t<nth;t++) th.emplace_back([&,t](){
            array<int,16> a{};
            for(int v0=t; v0<=N; v0+=nth){ a[0]=v0; rec(1,N-v0,a,N); }
        });
        for(auto&x:th) x.join();
        printf("N=%2d  max(25*bip - N^2) = %lld   at a=(",N,gbest.val);
        for(int i=0;i<n;i++) printf("%d%s",gbest.a[i], i+1<n?",":"");
        printf(")\n"); fflush(stdout);
        if(gbest.val>0){ printf("*** COUNTEREXAMPLE ***\n"); return 1; }
    }
    return 0;
}
