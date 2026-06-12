#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
using namespace std;
using u64 = uint64_t;
using u128 = __uint128_t;
using boost::multiprecision::cpp_int;

static mt19937_64 rng(0xE307C0DEULL);
static uint64_t partition_count = 0;
static uint64_t sets_examined = 0;
static uint64_t factored_count = 0;
static chrono::steady_clock::time_point start_time;
static int runtime_limit_sec = 0;

static inline bool timed_out(){
    if(runtime_limit_sec <= 0) return false;
    return chrono::duration_cast<chrono::seconds>(chrono::steady_clock::now()-start_time).count() >= runtime_limit_sec;
}

string u128s(u128 x){ if(!x) return "0"; string s; while(x){ s.push_back(char('0'+x%10)); x/=10; } reverse(s.begin(),s.end()); return s; }
string cppints(const cpp_int& x){ return x.convert_to<string>(); }

u64 mul_mod(u64 a,u64 b,u64 mod){ return (u128)a*b%mod; }
u64 pow_mod(u64 a,u64 d,u64 mod){ u64 r=1; while(d){ if(d&1) r=mul_mod(r,a,mod); a=mul_mod(a,a,mod); d>>=1; } return r; }
bool isPrime64(u64 n){
    if(n<2) return false;
    for(u64 p: {2ULL,3ULL,5ULL,7ULL,11ULL,13ULL,17ULL,19ULL,23ULL,29ULL,31ULL,37ULL}) if(n%p==0) return n==p;
    u64 d=n-1,s=0; while((d&1)==0){d>>=1; s++;}
    for(u64 a: {2ULL,3ULL,5ULL,7ULL,11ULL,13ULL,17ULL,19ULL,23ULL,29ULL,31ULL,37ULL}){
        if(a>=n) continue; u64 x=pow_mod(a,d,n); if(x==1||x==n-1) continue;
        bool comp=true; for(u64 r=1;r<s;r++){ x=mul_mod(x,x,n); if(x==n-1){ comp=false; break; }}
        if(comp) return false;
    }
    return true;
}
u64 pollard(u64 n){
    if(n%2==0) return 2; if(n%3==0) return 3;
    while(true){
        u64 c=uniform_int_distribution<u64>(1,n-1)(rng), x=uniform_int_distribution<u64>(0,n-1)(rng), y=x, d=1;
        auto f=[&](u64 v){ return (mul_mod(v,v,n)+c)%n; };
        for(int it=0; d==1 && it<20000; ++it){ x=f(x); y=f(f(y)); u64 diff=x>y?x-y:y-x; d=gcd(diff,n); }
        if(d>1 && d<n) return d;
    }
}
void factor_rec(u64 n, vector<u64>& fs){ if(n==1) return; if(isPrime64(n)){ fs.push_back(n); return; } u64 d=pollard(n); factor_rec(d,fs); factor_rec(n/d,fs); }

vector<u64> blocks_from_u128(u128 N){
    if(N > numeric_limits<u64>::max()) return {};
    vector<u64> fs; factor_rec((u64)N,fs); sort(fs.begin(),fs.end());
    vector<u64> blocks;
    for(size_t i=0;i<fs.size();){ u64 p=fs[i], pp=1; while(i<fs.size() && fs[i]==p){ if(pp > numeric_limits<u64>::max()/p) return {}; pp*=p; i++; } blocks.push_back(pp); }
    return blocks;
}

bool partition_rec(const vector<u64>& blocks, const vector<u128>& prod, u128 N, u128 target, int unused, u128 acc, vector<u128>& group){
    if(acc > target) return false;
    if(unused == 0) return group.size() >= 2 && acc == target;
    partition_count++;
    u128 mx=0; int mm=unused;
    while(mm){ int l=mm&-mm; int i=__builtin_ctz((unsigned)l); mx += N/blocks[i]; mm ^= l; if(acc + mx >= target && mx > target){} }
    if(acc + mx < target) return false;
    if(acc + N/prod[unused] > target) return false;
    int lsb = unused & -unused, rest = unused ^ lsb;
    vector<pair<u128,int>> opts;
    for(int sub=rest;; sub=(sub-1)&rest){ int g=sub|lsb; opts.push_back({N/prod[g],g}); if(sub==0) break; }
    sort(opts.begin(), opts.end(), [](auto&a, auto&b){ return a.first < b.first; });
    for(auto [contrib,g]: opts){ group.push_back(prod[g]); if(partition_rec(blocks,prod,N,target,unused^g,acc+contrib,group)) return true; group.pop_back(); }
    return false;
}

bool find_partition(u128 N, u128 target, vector<u128>& out){
    factored_count++;
    vector<u64> blocks = blocks_from_u128(N);
    int r=blocks.size();
    if(r<2 || r>26) return false;
    u128 maxnum=0; for(u64 b: blocks) maxnum += N/b;
    if(maxnum < target) return false;
    int full=(1<<r)-1;
    vector<u128> prod(1<<r,1);
    for(int m=1;m<=full;m++){ int l=m&-m; int i=__builtin_ctz((unsigned)l); prod[m]=prod[m^l]*(u128)blocks[i]; }
    vector<u128> group;
    if(partition_rec(blocks,prod,N,target,full,0,group)){ out=group; sort(out.begin(),out.end()); return true; }
    return false;
}

struct Cand{ uint64_t x; vector<int> pf; unsigned long long smallMask; };
vector<int> primes;
unordered_map<int,int> primeIndex;
vector<Cand> cands;

vector<int> pfactors_int(uint64_t n){
    vector<int> out; uint64_t x=n;
    for(int p: primes){ if((uint64_t)p*p>x) break; if(x%p==0){ out.push_back(p); while(x%p==0) x/=p; }}
    if(x>1) out.push_back((int)x);
    return out;
}

void build_cands(int pmax, bool primePowerOnly){
    primes.clear(); primeIndex.clear(); cands.clear();
    vector<bool> iscomp(pmax+1,false);
    for(int i=2;i<=pmax;i++) if(!iscomp[i]){ primeIndex[i]=primes.size(); primes.push_back(i); if((long long)i*i<=pmax) for(long long j=1LL*i*i;j<=pmax;j+=i) iscomp[(int)j]=true; }
    for(int x=2;x<=pmax;x++){
        auto pf=pfactors_int(x);
        if(primePowerOnly && pf.size()!=1) continue;
        unsigned long long sm=0;
        for(int p: pf){ auto it=primeIndex.find(p); if(it!=primeIndex.end() && it->second<64) sm |= 1ULL<<it->second; }
        cands.push_back({(uint64_t)x,pf,sm});
    }
}

bool disjoint_pf(const vector<int>& a, const vector<int>& b){ for(int p:a) for(int q:b) if(p==q) return false; return true; }
bool disjoint_used(const vector<vector<int>>& used, const vector<int>& pf){ for(auto &v: used) if(!disjoint_pf(v,pf)) return false; return true; }

double greedy_ub(int start, unsigned long long smask, vector<vector<int>> usedLarge, int slots, long double product_left){
    double s=0; int got=0;
    for(int j=start;j<(int)cands.size() && got<slots;j++){
        auto &c=cands[j]; if((long double)c.x > product_left) break;
        if((c.smallMask & smask)!=0) continue;
        if(!disjoint_used(usedLarge,c.pf)) continue;
        s += 1.0/(double)c.x; got++; product_left /= c.x; smask |= c.smallMask; usedLarge.push_back(c.pf);
    }
    return s;
}

void print_witness(const vector<uint64_t>& P, u128 D, u128 N, const vector<u128>& Q){
    cout << "WITNESS_FOUND:\nP:"; for(auto x:P) cout << " " << x; cout << "\nDp: " << u128s(D) << "\nNp: " << u128s(N) << "\nQ:"; for(auto q:Q) cout << " " << u128s(q); cout << "\nDq: " << u128s(N) << "\nNq: " << u128s(D) << "\n"; exit(0);
}

void dfsA(int start, unsigned long long smask, vector<vector<int>>& usedLarge, u128 D, u128 N, int size, int sizeMax, long double prodBound, vector<uint64_t>& elems){
    if(timed_out()) return;
    if(size>=2 && N>D){
        sets_examined++;
        vector<u128> Q;
        if(find_partition(N,D,Q)) print_witness(elems,D,N,Q);
    }
    if(size>=sizeMax) return;
    if((long double)N/(long double)D + greedy_ub(start,smask,usedLarge,sizeMax-size,prodBound/(long double)D) <= 1.0L) return;
    for(int j=start;j<(int)cands.size();j++){
        auto &c=cands[j];
        if((long double)D*(long double)c.x > prodBound) break;
        if((c.smallMask & smask)!=0) continue;
        if(!disjoint_used(usedLarge,c.pf)) continue;
        u128 D2=D*(u128)c.x, N2=N*(u128)c.x + D;
        usedLarge.push_back(c.pf); elems.push_back(c.x);
        if((long double)N2/(long double)D2 + greedy_ub(j+1,smask|c.smallMask,usedLarge,sizeMax-size-1,prodBound/(long double)D2) > 1.0L)
            dfsA(j+1,smask|c.smallMask,usedLarge,D2,N2,size+1,sizeMax,prodBound,elems);
        elems.pop_back(); usedLarge.pop_back();
    }
}

void dfsReverse(int start, unsigned long long smask, vector<vector<int>>& usedLarge, u128 D, u128 N, int size, int sizeMax, long double prodBound, vector<uint64_t>& elems){
    if(timed_out()) return;
    if(size>=2 && N<D){
        sets_examined++;
        vector<u128> P;
        if(find_partition(N,D,P)){
            vector<uint64_t> P64; for(auto x:P) P64.push_back((uint64_t)x);
            vector<u128> Q; for(auto x: elems) Q.push_back(x);
            print_witness(P64,N,D,Q);
        }
    }
    if(size>=sizeMax) return;
    for(int j=start;j<(int)cands.size();j++){
        auto &c=cands[j];
        if((long double)D*(long double)c.x > prodBound) break;
        if((c.smallMask & smask)!=0) continue;
        if(!disjoint_used(usedLarge,c.pf)) continue;
        u128 D2=D*(u128)c.x, N2=N*(u128)c.x + D;
        if(N2>=D2) continue;
        usedLarge.push_back(c.pf); elems.push_back(c.x);
        dfsReverse(j+1,smask|c.smallMask,usedLarge,D2,N2,size+1,sizeMax,prodBound,elems);
        elems.pop_back(); usedLarge.pop_back();
    }
}

void run_phase(const string& mode, int pmax, int sizeMax, long double prodBound, bool ppOnly, int seconds){
    start_time=chrono::steady_clock::now(); runtime_limit_sec=seconds;
    sets_examined=partition_count=factored_count=0;
    build_cands(pmax,ppOnly);
    vector<vector<int>> used; vector<uint64_t> elems;
    if(mode=="forward") dfsA(0,0,used,1,0,0,sizeMax,prodBound,elems);
    else dfsReverse(0,0,used,1,0,0,sizeMax,prodBound,elems);
    auto runtime=chrono::duration_cast<chrono::seconds>(chrono::steady_clock::now()-start_time).count();
    cout << "NO_WITNESS_UP_TO:\nphase: " << mode << (ppOnly?"_prime_power":"") << "\nP_max: " << pmax << "\nsize_max: " << sizeMax << "\nproduct_bound: " << fixed << setprecision(0) << (long double)prodBound << "\nsets_examined: " << sets_examined << "\npartition_count: " << partition_count << "\nruntime: " << runtime << "s\nnext_phase: continue\n";
}

int main(int argc, char** argv){
    string mode = argc>1 ? argv[1] : "forward";
    int pmax = argc>2 ? atoi(argv[2]) : 500;
    int sizeMax = argc>3 ? atoi(argv[3]) : 12;
    long double prodBound = argc>4 ? stold(argv[4]) : 1e24L;
    bool ppOnly = argc>5 ? atoi(argv[5])!=0 : false;
    int seconds = argc>6 ? atoi(argv[6]) : 0;
    run_phase(mode,pmax,sizeMax,prodBound,ppOnly,seconds);
}
