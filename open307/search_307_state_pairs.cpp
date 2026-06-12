#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
using namespace std;
using u64 = uint64_t;
using u128 = __uint128_t;
using boost::multiprecision::cpp_int;

struct PairKey { u64 a, b; };
struct PairHash {
  size_t operator()(PairKey const& k) const noexcept {
    u64 x = k.a + 0x9e3779b97f4a7c15ULL;
    x ^= k.b + 0xbf58476d1ce4e5b9ULL + (x << 6) + (x >> 2);
    x ^= x >> 30; x *= 0xbf58476d1ce4e5b9ULL;
    x ^= x >> 27; x *= 0x94d049bb133111ebULL;
    x ^= x >> 31;
    return (size_t)x;
  }
};
struct PairEq { bool operator()(PairKey const& x, PairKey const& y) const noexcept { return x.a==y.a && x.b==y.b; } };
struct StateVal { uint32_t offset; uint16_t len; };

static vector<vector<u64>> storedSets;
static uint64_t states_generated = 0;
static uint64_t reciprocal_hits = 0;
static chrono::steady_clock::time_point start_time;
static int time_limit_sec = 0;

static inline bool timeout(){
  return time_limit_sec > 0 && chrono::duration_cast<chrono::seconds>(chrono::steady_clock::now()-start_time).count() >= time_limit_sec;
}
string u64s(u64 x){ return to_string(x); }
string u128s(u128 x){ if(!x) return "0"; string s; while(x){ s.push_back(char('0'+x%10)); x/=10; } reverse(s.begin(),s.end()); return s; }

vector<int> spf;
void build_spf(int n){
  spf.assign(n+1,0);
  for(int i=2;i<=n;i++) if(!spf[i]){ spf[i]=i; if((int64_t)i*i<=n) for(int64_t j=(int64_t)i*i;j<=n;j+=i) if(!spf[(int)j]) spf[(int)j]=i; }
}

vector<u64> pp_blocks_u64(u64 n){
  vector<u64> b;
  while(n>1){
    u64 p = (n < spf.size() ? spf[(size_t)n] : 0);
    if(p==0) p=n;
    u64 pp=1;
    while(n%p==0){ pp*=p; n/=p; }
    b.push_back(pp);
  }
  return b;
}

void emit_witness(vector<u64> const& P, vector<u64> const& Q){
  auto calcD=[&](vector<u64> const& S){ u128 D=1; for(u64 x:S) D*=x; return D; };
  auto calcN=[&](vector<u64> const& S){ u128 D=calcD(S), N=0; for(u64 x:S) N += D/x; return N; };
  cout << "WITNESS_FOUND:\nP:"; for(auto x:P) cout << " " << x;
  cout << "\nDp: " << u128s(calcD(P)) << "\nNp: " << u128s(calcN(P));
  cout << "\nQ:"; for(auto x:Q) cout << " " << x;
  cout << "\nDq: " << u128s(calcD(Q)) << "\nNq: " << u128s(calcN(Q)) << "\n";
  exit(0);
}

bool pairwise_coprime(vector<u64> const& S){
  for(size_t i=0;i<S.size();i++) for(size_t j=i+1;j<S.size();j++) if(std::gcd(S[i],S[j])!=1) return false;
  return true;
}

void process_partition(vector<u64> const& denoms, u64 D, unordered_map<PairKey, StateVal, PairHash, PairEq>& mp){
  if(denoms.size()<2) return;
  u128 N128=0;
  for(u64 s: denoms) N128 += (u128)D / s;
  if(N128 <= 1 || N128 > numeric_limits<u64>::max()) return;
  u64 N=(u64)N128;
  if(std::gcd(D,N)!=1) return;
  states_generated++;
  PairKey recip{N,D};
  auto it=mp.find(recip);
  if(it!=mp.end()){
    reciprocal_hits++;
    vector<u64> P=denoms;
    vector<u64> Q=storedSets[it->second.offset];
    if(P.size()>1 && Q.size()>1 && pairwise_coprime(P) && pairwise_coprime(Q)){
      u128 Dp=1,Np=0,Dq=1,Nq=0;
      for(u64 x:P) Dp*=x; for(u64 x:P) Np+=Dp/x;
      for(u64 x:Q) Dq*=x; for(u64 x:Q) Nq+=Dq/x;
      if(Dp==Nq && Dq==Np) emit_witness(P,Q);
    }
  }
  PairKey key{D,N};
  if(mp.find(key)==mp.end()){
    uint32_t off=(uint32_t)storedSets.size();
    storedSets.push_back(denoms);
    mp.emplace(key, StateVal{off,(uint16_t)denoms.size()});
  }
}

void gen_partitions_rec(int idx, vector<u64> const& blocks, vector<u64>& groups, u64 D, unordered_map<PairKey, StateVal, PairHash, PairEq>& mp){
  if(idx==(int)blocks.size()){
    process_partition(groups,D,mp);
    return;
  }
  u64 b=blocks[idx];
  for(size_t i=0;i<groups.size();i++){
    groups[i]*=b;
    gen_partitions_rec(idx+1,blocks,groups,D,mp);
    groups[i]/=b;
    if(timeout()) return;
  }
  groups.push_back(b);
  gen_partitions_rec(idx+1,blocks,groups,D,mp);
  groups.pop_back();
}

void process_D(u64 D, unordered_map<PairKey, StateVal, PairHash, PairEq>& mp){
  auto blocks=pp_blocks_u64(D);
  if(blocks.size()<2) return;
  vector<u64> groups;
  groups.reserve(blocks.size());
  gen_partitions_rec(0,blocks,groups,D,mp);
}

void phase_all(uint64_t DMAX, int seconds){
  start_time=chrono::steady_clock::now(); time_limit_sec=seconds;
  build_spf((int)DMAX);
  unordered_map<PairKey, StateVal, PairHash, PairEq> mp;
  mp.reserve(5000000);
  storedSets.reserve(5000000);
  uint64_t done=0;
  for(u64 D=2; D<=DMAX && !timeout(); D++){
    process_D(D,mp); done=D;
  }
  cout << "NO_WITNESS_UP_TO:\nmethod: state-pair D/N search\nD_MAX: " << done << "\nstates_generated: " << states_generated << "\nreciprocal_hits: " << reciprocal_hits << "\nnext_phase: prioritized many-prime-factor D search\n";
}

vector<int> primes_up_to(int n){
  vector<int> ps; vector<bool> comp(n+1,false);
  for(int i=2;i<=n;i++) if(!comp[i]){ ps.push_back(i); if((int64_t)i*i<=n) for(int64_t j=(int64_t)i*i;j<=n;j+=i) comp[(int)j]=true; }
  return ps;
}

void gen_block_products_rec(vector<u64> const& blocks, int idx, int rmax, u128 prod, u128 bound, vector<u64>& chosen, unordered_map<PairKey, StateVal, PairHash, PairEq>& mp){
  if(timeout()) return;
  if(chosen.size()>=3){
    if(prod <= numeric_limits<u64>::max()){
      vector<u64> groups;
      gen_partitions_rec(0, chosen, groups, (u64)prod, mp);
    }
  }
  if((int)chosen.size()>=rmax) return;
  for(int i=idx;i<(int)blocks.size();i++){
    u128 p2=prod*blocks[i];
    if(p2>bound) continue;
    chosen.push_back(blocks[i]);
    gen_block_products_rec(blocks,i+1,rmax,p2,bound,chosen,mp);
    chosen.pop_back();
  }
}

void phase_blocks(int primeMax, int rmax, string boundStr, int seconds){
  start_time=chrono::steady_clock::now(); time_limit_sec=seconds;
  vector<int> ps=primes_up_to(primeMax);
  vector<u64> blocks;
  for(int p:ps){
    u128 pp=p;
    while(pp <= numeric_limits<u64>::max() && pp <= (u128)1000000000000ULL){ blocks.push_back((u64)pp); pp*=p; }
  }
  sort(blocks.begin(),blocks.end());
  cpp_int bigBound(boundStr);
  u128 bound=0;
  string bs=bigBound.convert_to<string>();
  for(char c:bs){ bound=bound*10+(c-'0'); if(bound>numeric_limits<u64>::max()) { bound=numeric_limits<u64>::max(); break; } }
  unordered_map<PairKey, StateVal, PairHash, PairEq> mp;
  mp.reserve(10000000); storedSets.reserve(10000000);
  vector<u64> chosen;
  gen_block_products_rec(blocks,0,rmax,1,bound,chosen,mp);
  cout << "NO_WITNESS_UP_TO:\nmethod: state-pair D/N search\nD_MAX: block_product_bound_" << boundStr << "\nstates_generated: " << states_generated << "\nreciprocal_hits: " << reciprocal_hits << "\nnext_phase: random sampled many-block D search\n";
}

int main(int argc, char** argv){
  string mode = argc>1 ? argv[1] : "all";
  if(mode=="all"){
    uint64_t DMAX = argc>2 ? strtoull(argv[2],nullptr,10) : 10000000ULL;
    int seconds = argc>3 ? atoi(argv[3]) : 0;
    phase_all(DMAX,seconds);
  } else if(mode=="blocks"){
    int primeMax = argc>2 ? atoi(argv[2]) : 100;
    int rmax = argc>3 ? atoi(argv[3]) : 14;
    string bound = argc>4 ? argv[4] : "1000000000000000000";
    int seconds = argc>5 ? atoi(argv[5]) : 0;
    phase_blocks(primeMax,rmax,bound,seconds);
  }
}
