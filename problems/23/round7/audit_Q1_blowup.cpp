// audit_Q1_blowup.cpp -- independent exhaustive exact integer-weight blow-up audit.
//
// For a given triangle-free H (graph6) and every integer a >= 0 with sum a = W, Wmin<=W<=Wmax:
//   bip(H[a]) = min over ALL 2^(n-1) cuts S of H of sum_{uv mono} a_u a_v      (base 1)
//   fam(H[a]) = min over the neighbourhood-UNION cuts  union_{v in I} N(v)
// and reports EXACTLY:
//   (1) every a with 25*bip > W^2                      (counterexample to the conjecture)
//   (2) the number of a with 25*bip == W^2             (all maximisers, not just the first)
//   (3) every a with 25*fam  > W^2                     (certificate failures)  -- capped listing
// Soundness of the pruning: the loop exits early only on a cut with 25q < W^2 (case 1/2)
// resp. 25q <= W^2 (case 3); since bip<=q and fam<=q those exits are decisions, not guesses.
//
// build: clang++ -O3 -march=native -std=c++17 audit_Q1_blowup.cpp -o audit_Q1_blowup.exe
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <mutex>
#include <algorithm>

static int NV;
static std::vector<std::pair<int,int>> EDG;
static std::vector<std::vector<std::pair<int,int>>> CUTALL, CUTFAM;

static void parse_g6(const std::string& s, int& n, std::vector<std::pair<int,int>>& E){
    size_t p=0; n=(int)s[p++]-63; int val=0, have=0; E.clear();
    for(int j=1;j<n;j++) for(int i=0;i<j;i++){
        if(have==0){ val=(int)s[p++]-63; have=6; }
        int bit=(val>>(have-1))&1; have--;
        if(bit) E.push_back({i,j});
    }
}

static std::mutex MTX;
static long long TOT_MAXIMISERS=0, TOT_CE=0, TOT_FAMFAIL=0;
static std::vector<std::string> LIST_MAX, LIST_CE, LIST_FAMFAIL;

struct Res { long long nvec=0, nmax=0, nce=0, nfam=0; std::vector<std::string> mx, ce, fm; };

static void run_slice(int W, int lo, int hi, Res* R){
    std::vector<int> a(NV,0);
    long long W2=(long long)W*W;
    // recursive composition
    struct Rec {
        int NV; long long W2; int W; Res* R; std::vector<int>* a; int lo, hi;
        void go(int idx, int left){
            if(idx==NV-1){
                (*a)[idx]=left; R->nvec++;
                // ---- bip
                bool small=false; long long mn=-1;
                for(auto& C : CUTALL){
                    long long q=0; for(auto& e:C) q+=(long long)(*a)[e.first]*(*a)[e.second];
                    if(25*q < W2){ small=true; break; }
                    if(mn<0||q<mn) mn=q;
                }
                if(!small){
                    if(25*mn>W2){ R->nce++; if(R->ce.size()<20){ std::string s="a=["; for(int i=0;i<NV;i++){s+=std::to_string((*a)[i]); if(i+1<NV)s+=",";} s+="] bip="+std::to_string(mn)+" W="+std::to_string(W); R->ce.push_back(s);} }
                    else { R->nmax++; if(R->mx.size()<40){ std::string s="a=["; for(int i=0;i<NV;i++){s+=std::to_string((*a)[i]); if(i+1<NV)s+=",";} s+="] bip="+std::to_string(mn)+" W="+std::to_string(W); R->mx.push_back(s);} }
                }
                // ---- fam
                bool ok=false; long long fm=-1;
                for(auto& C : CUTFAM){
                    long long q=0; for(auto& e:C) q+=(long long)(*a)[e.first]*(*a)[e.second];
                    if(25*q <= W2){ ok=true; break; }
                    if(fm<0||q<fm) fm=q;
                }
                if(!ok){ R->nfam++; if(R->fm.size()<20){ std::string s="a=["; for(int i=0;i<NV;i++){s+=std::to_string((*a)[i]); if(i+1<NV)s+=",";} s+="] fam="+std::to_string(fm)+" W="+std::to_string(W)+" 25fam="+std::to_string(25*fm)+" W^2="+std::to_string(W2); R->fm.push_back(s);} }
                return;
            }
            int l=0,h=left;
            if(idx==0){ l=lo; h=std::min(h,hi); }
            for(int v=l;v<=h;v++){ (*a)[idx]=v; go(idx+1,left-v); }
        }
    } rec{NV,W2,W,R,&a,lo,hi};
    if(lo<=hi) rec.go(0,W);
}

int main(int argc,char**argv){
    if(argc<4){ printf("usage: %s <g6> <Wmin> <Wmax> [threads]\n",argv[0]); return 1; }
    std::string g6=argv[1]; int Wmin=atoi(argv[2]), Wmax=atoi(argv[3]);
    int nt=(argc>4)?atoi(argv[4]):8;
    parse_g6(g6,NV,EDG);
    printf("H=%s n=%d |E|=%zu\n",g6.c_str(),NV,EDG.size());
    std::vector<unsigned> adj(NV,0);
    for(auto&e:EDG){ adj[e.first]|=1u<<e.second; adj[e.second]|=1u<<e.first; }
    // all cuts (bit 0 fixed to 0)
    std::vector<unsigned> all, fam;
    for(unsigned m=0;m<(1u<<(NV-1));m++) all.push_back(m<<1);
    { std::vector<char> seen(1u<<NV,0);
      for(unsigned I=0;I<(1u<<NV);I++){ unsigned S=0; for(int v=0;v<NV;v++) if(I>>v&1) S|=adj[v];
          if(!seen[S]){ seen[S]=1; fam.push_back(S); } } }
    printf("cuts: all=%zu  neighbourhood-union=%zu\n",all.size(),fam.size());
    auto build=[&](std::vector<unsigned>& L, std::vector<std::vector<std::pair<int,int>>>& out){
        std::vector<std::pair<size_t,size_t>> ord; std::vector<std::vector<std::pair<int,int>>> tmp;
        for(unsigned S:L){ std::vector<std::pair<int,int>> l;
            for(auto&e:EDG) if((((S>>e.first)&1)==((S>>e.second)&1))) l.push_back(e);
            ord.push_back({l.size(),tmp.size()}); tmp.push_back(l); }
        std::sort(ord.begin(),ord.end());
        for(auto&o:ord) out.push_back(tmp[o.second]);
    };
    build(all,CUTALL); build(fam,CUTFAM);
    long long gmax=0,gce=0,gfam=0,gvec=0;
    for(int W=Wmin;W<=Wmax;W++){
        std::vector<Res> R(nt); std::vector<std::thread> th;
        int per=(W+1+nt-1)/nt;
        for(int t=0;t<nt;t++){ int lo=t*per, hi=std::min(W,(t+1)*per-1);
            th.emplace_back([W,lo,hi,&R,t](){ run_slice(W,lo,hi,&R[t]); }); }
        for(auto&x:th) x.join();
        long long nv=0,nm=0,nc=0,nf=0;
        for(auto&r:R){ nv+=r.nvec; nm+=r.nmax; nc+=r.nce; nf+=r.nfam;
            for(auto&s:r.mx) if(LIST_MAX.size()<40) LIST_MAX.push_back(s);
            for(auto&s:r.ce) LIST_CE.push_back(s);
            for(auto&s:r.fm) if(LIST_FAMFAIL.size()<40) LIST_FAMFAIL.push_back(s); }
        printf("W=%2d vectors=%12lld  #{25bip==W^2}=%lld  #{25bip>W^2}=%lld  #{25fam>W^2}=%lld\n",
               W,nv,nm,nc,nf); fflush(stdout);
        gvec+=nv; gmax+=nm; gce+=nc; gfam+=nf;
    }
    printf("TOTAL vectors=%lld  maximisers(25bip==W^2)=%lld  counterexamples=%lld  fam-failures=%lld\n",
           gvec,gmax,gce,gfam);
    printf("-- sample maximisers --\n"); for(auto&s:LIST_MAX) printf("   %s\n",s.c_str());
    printf("-- counterexamples --\n"); for(auto&s:LIST_CE) printf("   %s\n",s.c_str());
    printf("-- fam failures --\n"); for(auto&s:LIST_FAMFAIL) printf("   %s\n",s.c_str());
    return 0;
}
