#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
using namespace std;
using boost::multiprecision::cpp_int;
using u64 = uint64_t;

struct Den { u64 v; int p; double inv; bool even; };
struct Counters { uint64_t states=0, smooth=0, parts=0, hits=0; long double best=1e100L; string best_desc="none"; } C;
static mt19937_64 rng(0x307F17A1ULL);
static chrono::steady_clock::time_point T0, lastLog;
static int totalSeconds = 0;

string s(const cpp_int& x){ return x.convert_to<string>(); }
cpp_int gcd_big(cpp_int a, cpp_int b){ while(b != 0){ cpp_int r = a % b; a = b; b = r; } return a < 0 ? -a : a; }
long double to_ld(const cpp_int& x){ return x.convert_to<long double>(); }
bool timed_out(){ return totalSeconds > 0 && chrono::duration_cast<chrono::seconds>(chrono::steady_clock::now()-T0).count() >= totalSeconds; }
void progress(const string& phase, const string& next){
  auto now=chrono::steady_clock::now();
  if(chrono::duration_cast<chrono::seconds>(now-lastLog).count() >= 600){
    cout << "SEARCH:\nphase: " << phase << "\nstates_generated: " << C.states << "\nsmooth_survivors: " << C.smooth << "\npartitions_checked: " << C.parts << "\nbest_near_miss: " << C.best_desc << "\nnext_action: " << next << "\n" << flush;
    lastLog=now;
  }
}

vector<int> primes_up_to(int n){ vector<int> p; vector<char> comp(n+1); for(int i=2;i<=n;i++) if(!comp[i]){ p.push_back(i); if(1LL*i*i<=n) for(long long j=1LL*i*i;j<=n;j+=i) comp[(int)j]=1; } return p; }
vector<Den> make_pool(int maxv, bool oddOnly=false){
  vector<Den> out; auto ps=primes_up_to(maxv);
  for(int p: ps){ u64 pp=p; while(pp <= (u64)maxv){ if(!(oddOnly && pp%2==0)) out.push_back({pp,p,1.0L/(long double)pp,(pp%2==0)}); if(pp > (u64)maxv/(u64)p) break; pp *= (u64)p; } }
  sort(out.begin(), out.end(), [](auto&a, auto&b){ return a.v < b.v; });
  return out;
}

struct State { vector<u64> den; vector<int> primes; cpp_int D=1, N=0; long double sum=0; bool uniqueEven=false, allOdd=true; };
State build_state(const vector<Den>& ds){
  State st; st.den.reserve(ds.size()); st.primes.reserve(ds.size()); st.D=1; st.sum=0; int ev=0;
  for(auto &d: ds){ st.den.push_back(d.v); st.primes.push_back(d.p); st.D *= d.v; st.sum += d.inv; if(d.even) ev++; }
  st.N=0; for(auto v: st.den) st.N += st.D / v;
  st.uniqueEven = (ev==1); st.allOdd = (ev==0); sort(st.den.begin(), st.den.end()); sort(st.primes.begin(), st.primes.end()); return st;
}

bool smooth_factor(cpp_int n, int B, vector<cpp_int>& blocks){
  blocks.clear(); auto ps=primes_up_to(B);
  for(int p: ps){ if(n % p == 0){ cpp_int pp=1; while(n % p == 0){ n /= p; pp *= p; } blocks.push_back(pp); } }
  return n == 1;
}

struct PartCtx { vector<cpp_int> prod, contrib; cpp_int N, target; int full=0; int minGroups=0, maxGroups=100, parity=-1; bool wantEvenGroup=false; int twoIndex=-1; vector<cpp_int> answer; };

bool part_rec(PartCtx& ctx, int unused, cpp_int acc, vector<cpp_int>& groups){
  if(timed_out()) return false;
  C.parts++;
  if(acc > ctx.target) return false;
  if(unused == 0){
    int g=(int)groups.size();
    if(g < ctx.minGroups || g > ctx.maxGroups) return false;
    if(ctx.parity != -1 && (g&1) != ctx.parity) return false;
    if(acc == ctx.target){ ctx.answer=groups; return true; }
    return false;
  }
  cpp_int mx=0; int mm=unused;
  while(mm){ int l=mm&-mm; mx += ctx.contrib[l]; mm ^= l; }
  if(acc + mx < ctx.target) return false;
  if(acc + ctx.contrib[unused] > ctx.target) return false;
  int lsb=unused&-unused, rest=unused^lsb;
  vector<pair<cpp_int,int>> opts;
  for(int sub=rest;; sub=(sub-1)&rest){ int g=sub|lsb; opts.push_back({ctx.contrib[g],g}); if(sub==0) break; }
  sort(opts.begin(), opts.end(), [](auto&a, auto&b){ return a.first < b.first; });
  for(auto &op: opts){ int gmask=op.second; groups.push_back(ctx.prod[gmask]); if(part_rec(ctx, unused^gmask, acc+ctx.contrib[gmask], groups)) return true; groups.pop_back(); }
  return false;
}

bool enumerate_partition(const vector<cpp_int>& blocks, const cpp_int& N, const cpp_int& target, int minGroups, int maxGroups, int parity, vector<cpp_int>& out){
  int r=(int)blocks.size(); if(r < minGroups || r > 18) return false;
  PartCtx ctx; ctx.N=N; ctx.target=target; ctx.minGroups=minGroups; ctx.maxGroups=maxGroups; ctx.parity=parity; ctx.full=(1<<r)-1; ctx.prod.assign(1<<r,1); ctx.contrib.assign(1<<r,0);
  for(int m=1;m<=ctx.full;m++){ int l=m&-m; int i=__builtin_ctz((unsigned)l); ctx.prod[m]=ctx.prod[m^l]*blocks[i]; }
  for(int m=1;m<=ctx.full;m++) ctx.contrib[m]=N/ctx.prod[m];
  cpp_int maxSplit=0; for(int i=0;i<r;i++) maxSplit += ctx.contrib[1<<i];
  if(maxSplit < target) return false;
  if(ctx.contrib[ctx.full] > target) return false;
  vector<cpp_int> groups;
  if(part_rec(ctx, ctx.full, 0, groups)){ out=ctx.answer; return true; }
  return false;
}

void emit_witness(const vector<u64>& P, const vector<cpp_int>& Qbig){
  auto Dnat=[&](const vector<u64>& S){ cpp_int D=1; for(auto x:S) D*=x; return D; };
  auto Nnat=[&](const vector<u64>& S){ cpp_int D=Dnat(S), N=0; for(auto x:S) N += D/x; return N; };
  cpp_int Dq=1; for(auto &x:Qbig) Dq*=x; cpp_int Nq=0; for(auto &x:Qbig) Nq += Dq/x;
  cout << "WITNESS_FOUND:\nP:"; for(auto x:P) cout << " " << x;
  cout << "\nDp: " << s(Dnat(P)) << "\nNp: " << s(Nnat(P)) << "\nQ:"; for(auto &x:Qbig) cout << " " << s(x);
  cout << "\nDq: " << s(Dq) << "\nNq: " << s(Nq) << "\n" << flush;
  exit(0);
}
void emit_witness2(const vector<cpp_int>& Pbig, const vector<u64>& Q){
  vector<u64> P; for(auto &x:Pbig){ if(x > numeric_limits<u64>::max()) return; P.push_back(x.convert_to<u64>()); }
  vector<cpp_int> Qb; for(auto x:Q) Qb.push_back(x); emit_witness(P,Qb);
}


vector<Den> random_unique_even_set(const vector<Den>& pool, int minSz, int maxSz, long double low, long double high, bool avoidSmall){
  vector<Den> evens, odds; for(auto &d: pool){ if(d.even) evens.push_back(d); else odds.push_back(d); }
  vector<Den> chosen; unordered_set<int> used;
  size_t ecap=min<size_t>(evens.size(), (size_t)8);
  Den e = evens[(size_t)(rng()%ecap)]; chosen.push_back(e); used.insert(e.p); long double sum=e.inv;
  vector<pair<long double,Den>> scored; scored.reserve(odds.size());
  for(auto &d: odds){
    long double w=d.inv;
    if(avoidSmall && (d.p==3||d.p==5||d.p==7||d.p==11)) w*=0.05L;
    long double noise=0.35L + (long double)(rng()%1000000)/500000.0L;
    scored.push_back({w*noise,d});
  }
  sort(scored.begin(), scored.end(), [](auto&a, auto&b){ return a.first > b.first; });
  for(auto &sd: scored){ auto d=sd.second; if((int)chosen.size()>=maxSz) break; if(used.count(d.p)) continue; if(sum + d.inv > high && (int)chosen.size()>=minSz) continue; chosen.push_back(d); used.insert(d.p); sum += d.inv; if(sum>low && (int)chosen.size()>=minSz && (rng()%3==0)) break; }
  if(!(sum>low && sum<high && (int)chosen.size()>=minSz)) chosen.clear(); return chosen;
}
vector<Den> random_all_odd_set(const vector<Den>& pool, int minSz, int maxSz, long double low, long double high){
  vector<pair<long double,Den>> scored;
  for(auto &d: pool) if(!d.even){ long double noise=0.35L + (long double)(rng()%1000000)/500000.0L; scored.push_back({d.inv*noise,d}); }
  sort(scored.begin(), scored.end(), [](auto&a, auto&b){ return a.first > b.first; });
  vector<Den> chosen; unordered_set<int> used; long double sum=0;
  for(auto &sd: scored){ auto d=sd.second; if((int)chosen.size()>=maxSz) break; if(used.count(d.p)) continue; if(sum+d.inv>high && (int)chosen.size()>=minSz) continue; chosen.push_back(d); used.insert(d.p); sum+=d.inv; if(sum>low && (int)chosen.size()>=minSz && chosen.size()%2==0 && (rng()%3==0)) break; }
  if(!(sum>low && sum<high && (int)chosen.size()>=minSz && chosen.size()%2==0)) chosen.clear(); return chosen;
}

void update_best(long double v, const string& desc){ if(v < C.best){ C.best=v; C.best_desc=desc; } }

void modeA(const string& phase, int poolMax, int B, int minSz, int maxSz, int seconds){
  auto pool=make_pool(poolMax,false); auto end=chrono::steady_clock::now()+chrono::seconds(seconds);
  while(chrono::steady_clock::now()<end && !timed_out()){
    auto ds=random_unique_even_set(pool,minSz,maxSz,1.0L,1.25L,true); if(ds.empty()) continue;
    State P=build_state(ds); C.states++;
    update_best(fabsl(P.sum-1.0L), phase+" sumP="+to_string((double)P.sum)+" size="+to_string(P.den.size()));
    vector<cpp_int> blocks; if(!smooth_factor(P.N,B,blocks)) { progress(phase,"smooth sieve"); continue; }
    C.smooth++; if(blocks.size()<4 || blocks.size()>18) continue;
    vector<cpp_int> Q; if(enumerate_partition(blocks,P.N,P.D,4,16,0,Q)) emit_witness(P.den,Q);
    progress(phase,"partition smooth numerator");
  }
}

void modeB(const string& phase, int poolMax, int B, int minSz, int maxSz, int seconds){
  auto pool=make_pool(poolMax,true); auto end=chrono::steady_clock::now()+chrono::seconds(seconds);
  while(chrono::steady_clock::now()<end && !timed_out()){
    auto ds=random_all_odd_set(pool,minSz,maxSz,0.75L,0.99L); if(ds.empty()) continue;
    State Q=build_state(ds); C.states++;
    update_best(fabsl(Q.sum-0.9L), phase+" sumQ="+to_string((double)Q.sum)+" size="+to_string(Q.den.size()));
    if(Q.N % 2 != 0) continue;
    vector<cpp_int> blocks; if(!smooth_factor(Q.N,B,blocks)) { progress(phase,"smooth sieve"); continue; }
    C.smooth++; if(blocks.size()<3 || blocks.size()>18) continue;
    vector<cpp_int> P; if(enumerate_partition(blocks,Q.N,Q.D,3,25,-1,P)) emit_witness2(P,Q.den);
    progress(phase,"partition reverse numerator");
  }
}

void modeC(const string& phase, int poolMax, int B, int seconds){
  auto pool=make_pool(poolMax,false); unordered_map<string, vector<u64>> uniq, odd; auto end=chrono::steady_clock::now()+chrono::seconds(seconds);
  while(chrono::steady_clock::now()<end && !timed_out()){
    bool makeOdd = (rng()%2==0); vector<Den> ds = makeOdd ? random_all_odd_set(pool,5,16,0.75L,1.25L) : random_unique_even_set(pool,8,25,1.0L,1.25L,false); if(ds.empty()) continue;
    State S=build_state(ds); C.states++;
    vector<cpp_int> blocks; if(!smooth_factor(S.N,B,blocks)) { progress(phase,"reciprocal hash smooth states"); continue; }
    C.smooth++;
    string k=s(S.D)+"#"+s(S.N), rk=s(S.N)+"#"+s(S.D);
    if(S.uniqueEven){ auto it=odd.find(rk); if(it!=odd.end()){ vector<cpp_int> Q; for(auto x:it->second) Q.push_back(x); emit_witness(S.den,Q); } uniq.emplace(k,S.den); }
    if(S.allOdd){ auto it=uniq.find(rk); if(it!=uniq.end()){ vector<cpp_int> Q; for(auto x:S.den) Q.push_back(x); emit_witness(it->second,Q); } odd.emplace(k,S.den); }
    progress(phase,"reciprocal state hash");
  }
}

int main(int argc, char** argv){
  int s1=argc>1?atoi(argv[1]):600, s2=argc>2?atoi(argv[2]):600, s3=argc>3?atoi(argv[3]):1200;
  totalSeconds=s1+s2+s3+60; T0=chrono::steady_clock::now(); lastLog=T0;
  modeA("phase1_A_pool200_B100",200,100,10,18,s1/3);
  modeB("phase1_B_pool200_B100",200,100,4,12,s1/3);
  modeC("phase1_C_pool200_B100",200,100,s1 - 2*(s1/3));
  modeA("phase2_A_pool1000_B300",1000,300,10,25,s2/3);
  modeB("phase2_B_pool1000_B300",1000,300,4,16,s2/3);
  modeC("phase2_C_pool1000_B300",1000,300,s2 - 2*(s2/3));
  modeA("phase3_A_random_B500",1000,500,10,25,s3/3);
  modeB("phase3_B_random_B500",1000,500,4,16,s3/3);
  modeC("phase3_C_random_hash_B500",1000,500,s3 - 2*(s3/3));
  cout << "NO_WITNESS_FINAL_PHASE:\nmethod: smooth numerator + reciprocal-state search\nstates_generated: " << C.states << "\nsmooth_survivors: " << C.smooth << "\npartitions_checked: " << C.parts << "\nbest_near_miss: " << C.best_desc << "\nrecommendation: park Erdos307 and request next open target\n";
}

