// AUDIT: exhaustive exact-integer blow-up test of the 1/25 ceiling for a given pattern.
// Own code, 64-bit integers only (no floating point anywhere).
//
//   bip(H[a]) = min over the 2^(n-1) cuts S of H of sum over monochromatic uv of a_u a_v
//
// For every composition a of N into n nonnegative parts (ZERO WEIGHTS INCLUDED) we report
//   max over a of ( 25*bip(H[a]) - N^2 )
// A positive value at any N would REFUTE the conjecture for this pattern.
//
// usage: audit_Q4_blowup <pattern> <Nmax> [dumpN]
//   pattern in {g8, g11, g14, petersen}
//   dumpN: if given, print every maximiser (25*bip == N^2) at that N.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <thread>
#include <mutex>
#include <algorithm>
using namespace std;

static int n_;
static vector<pair<int,int>> E_;
static vector<vector<pair<int,int>>> cutmono_;   // per cut: list of monochromatic edges

static void build(const string& pat){
    if(pat=="petersen"){
        vector<pair<int,int>> V;
        for(int i=0;i<5;i++) for(int j=i+1;j<5;j++) V.push_back({i,j});
        n_=10;
        for(int i=0;i<10;i++) for(int j=i+1;j<10;j++){
            int a=V[i].first,b=V[i].second,c=V[j].first,d=V[j].second;
            if(a!=c&&a!=d&&b!=c&&b!=d) E_.push_back({i,j});
        }
    } else {
        int m = atoi(pat.c_str()+1);
        n_=m;
        for(int i=0;i<m;i++) for(int j=i+1;j<m;j++){
            int dd = min(j-i, m-(j-i));
            if(3*dd > m) E_.push_back({i,j});
        }
    }
    cutmono_.resize(1u<<(n_-1));
    for(unsigned mask=0; mask < (1u<<(n_-1)); mask++){
        vector<int> side(n_,0);
        for(int v=1;v<n_;v++) side[v]=(mask>>(v-1))&1;
        for(auto&e:E_) if(side[e.first]==side[e.second]) cutmono_[mask].push_back(e);
    }
}

struct Res{ long long best; vector<vector<int>> arg; };

static void work(int N, int lo, int hi, Res* out, bool dump){
    // enumerate compositions with a[0] in [lo,hi)
    vector<int> a(n_,0);
    long long best = LLONG_MIN;
    vector<vector<int>> arg;
    // recursive enumeration
    struct Rec{
        int n; long long N; vector<int>& a; long long& best; vector<vector<int>>& arg; bool dump;
        void go(int i, int rem){
            if(i==n-1){ a[i]=rem; eval(); return; }
            for(int v=0; v<=rem; v++){ a[i]=v; go(i+1, rem-v); }
            a[i]=0;
        }
        void eval(){
            long long thr = N*N;           // we compare 25*bip against N^2
            long long bip = LLONG_MAX;
            for(size_t c=0;c<cutmono_.size();c++){
                long long s=0; bool over=false;
                for(auto&e:cutmono_[c]){
                    s += (long long)a[e.first]*a[e.second];
                    if(s>=bip){ over=true; break; }          // valid prune: terms are nonnegative
                }
                if(!over && s<bip) bip=s;
                if(bip==0) break;
            }
            long long val = 25*bip - thr;
            if(val>best){ best=val; arg.clear(); }
            if(val==best && dump && arg.size()<200) arg.push_back(a);
        }
    } r{n_, (long long)N, a, best, arg, dump};
    for(int v=lo; v<hi && v<=N; v++){ a[0]=v; r.go(1, N-v); }
    out->best=best; out->arg=arg;
}

int main(int argc,char**argv){
    string pat = argc>1?argv[1]:"g8";
    int Nmax = argc>2?atoi(argv[2]):30;
    int dumpN = argc>3?atoi(argv[3]):-1;
    build(pat);
    printf("pattern %s: n=%d |E|=%zu cuts=%zu\n", pat.c_str(), n_, E_.size(), cutmono_.size());
    for(int N=1;N<=Nmax;N++){
        int T = min(8, N+1);
        vector<thread> th; vector<Res> res(T);
        int per = (N+1+T-1)/T;
        for(int t=0;t<T;t++){
            int lo=t*per, hi=min(N+1,(t+1)*per);
            th.emplace_back([=,&res]{ if(lo<hi) work(N,lo,hi,&res[t], N==dumpN); else res[t].best=LLONG_MIN; });
        }
        for(auto&x:th) x.join();
        long long best=LLONG_MIN; vector<vector<int>> arg;
        for(auto&x:res){ if(x.best>best){best=x.best; arg=x.arg;} else if(x.best==best){ for(auto&v:x.arg) arg.push_back(v);} }
        printf("N=%3d  max(25*bip - N^2) = %lld %s\n", N, best, best>0?"  *** CONJECTURE VIOLATED ***":(best==0?"  (tight)":""));
        if(N==dumpN){
            printf("  maximisers (%zu shown):\n", arg.size());
            for(auto&v:arg){ printf("   ["); for(int i=0;i<n_;i++) printf("%d%s", v[i], i+1<n_?",":""); printf("]\n"); }
        }
        fflush(stdout);
    }
    return 0;
}
