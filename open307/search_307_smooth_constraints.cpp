#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
using namespace std;
using boost::multiprecision::cpp_int;
using Clock = chrono::steady_clock;

struct Den { uint64_t v; vector<int> pf; double inv; bool even; };
struct Block { cpp_int val; int p; bool even; };
struct Counters { uint64_t states=0, smooth=0, partNodes=0, partCalls=0; long double best=1e100L; string bestDesc="none"; } C;
static mt19937_64 rng(0x307C0DECULL);
static Clock::time_point T0,lastLog,deadline;
static bool useDeadline=false;

bool timed_out(){ return useDeadline && Clock::now() >= deadline; }
string sBig(const cpp_int& x){ return x.convert_to<string>(); }
cpp_int gcd_big(cpp_int a, cpp_int b){ while(b!=0){ cpp_int r=a%b; a=b; b=r; } return a<0 ? -a : a; }
long double ldBig(const cpp_int& x){ return x.convert_to<long double>(); }

void progress(const string& phase, const string& next){
  auto now=Clock::now();
  if(chrono::duration_cast<chrono::seconds>(now-lastLog).count() >= 600){
    cout << "SEARCH:\nphase: " << phase << "\nstates_generated: " << C.states
         << "\nsmooth_survivors: " << C.smooth << "\npartitions_checked: " << C.partNodes
         << "\nbest_near_miss: " << C.bestDesc << "\nnext_action: " << next << "\n" << flush;
    lastLog=now;
  }
}
void best(long double v, const string& d){ if(v<C.best){ C.best=v; C.bestDesc=d; } }

vector<int> primes_up_to(int n){ vector<int> p; vector<char> c(n+1); for(int i=2;i<=n;i++) if(!c[i]){ p.push_back(i); if(1LL*i*i<=n) for(long long j=1LL*i*i;j<=n;j+=i) c[(int)j]=1; } return p; }
vector<int> pfactors(int n, const vector<int>& primes){ vector<int> out; int x=n; for(int p: primes){ if(1LL*p*p>x) break; if(x%p==0){ out.push_back(p); while(x%p==0) x/=p; } } if(x>1) out.push_back(x); return out; }
vector<Den> make_pool(int maxv, bool oddOnly){
  auto ps=primes_up_to(maxv); vector<Den> out;
  for(int x=2;x<=maxv;x++){
    if(oddOnly && x%2==0) continue;
    auto pf=pfactors(x,ps);
    out.push_back({(uint64_t)x,pf,1.0/(double)x,(x%2==0)});
  }
  sort(out.begin(), out.end(), [](auto&a, auto&b){ return a.v < b.v; });
  return out;
}
bool disjoint(const vector<int>& a, const vector<int>& b){ for(int x:a) for(int y:b) if(x==y) return false; return true; }
bool can_add(const vector<int>& used, const Den& d){ for(int p:d.pf) if(p<(int)used.size() && used[p]) return false; return true; }
void add_den(vector<int>& used, const Den& d, int delta){ for(int p:d.pf) if(p<(int)used.size()) used[p]+=delta; }

double greedy_max(const vector<Den>& pool, int start, vector<int> used, int slots){
  double sum=0; int got=0;
  for(int i=start;i<(int)pool.size() && got<slots;i++){
    if(!can_add(used,pool[i])) continue;
    sum += pool[i].inv; add_den(used,pool[i],1); got++;
  }
  return sum;
}

struct State { vector<uint64_t> den; vector<int> primes; cpp_int D=1,N=0; long double sum=0; };
State state_from(const vector<Den>& ds){
  State st; st.D=1; st.sum=0;
  for(auto &d:ds){ st.den.push_back(d.v); st.D *= d.v; st.sum += d.inv; for(int p:d.pf) st.primes.push_back(p); }
  st.N=0; for(auto x:st.den) st.N += st.D / x;
  sort(st.den.begin(), st.den.end()); sort(st.primes.begin(), st.primes.end()); return st;
}

bool smooth_factor(cpp_int n, int B, vector<Block>& blocks){
  blocks.clear(); auto ps=primes_up_to(B);
  for(int p: ps){ if(n % p == 0){ cpp_int pp=1; while(n % p == 0){ n/=p; pp*=p; } blocks.push_back({pp,p,p==2}); } }
  return n==1;
}

struct PartCtx { vector<cpp_int> prod, contrib; vector<int> evenMask; cpp_int N,target; int full=0,minG=0,maxG=99,parity=-1; bool requireEvenGroup=false; vector<cpp_int> ans; };
int popc(int x){ return __builtin_popcount((unsigned)x); }
bool part_rec(PartCtx& ctx, int unused, cpp_int acc, vector<cpp_int>& groups, int evenGroups){
  if(timed_out()) return false;
  C.partNodes++;
  if(acc > ctx.target) return false;
  int gcur=(int)groups.size();
  if(gcur > ctx.maxG) return false;
  if(gcur + popc(unused) < ctx.minG) return false;
  if(unused==0){
    if(gcur<ctx.minG || gcur>ctx.maxG) return false;
    if(ctx.parity!=-1 && (gcur&1)!=ctx.parity) return false;
    if(ctx.requireEvenGroup && evenGroups!=1) return false;
    if(acc==ctx.target){ ctx.ans=groups; return true; }
    return false;
  }
  cpp_int mx=0; int mm=unused; while(mm){ int l=mm&-mm; mx += ctx.contrib[l]; mm ^= l; }
  if(acc + mx < ctx.target) return false;
  if(acc + ctx.contrib[unused] > ctx.target) return false;
  int lsb=unused&-unused, rest=unused^lsb;
  vector<pair<cpp_int,int>> opts;
  for(int sub=rest;; sub=(sub-1)&rest){ int g=sub|lsb; opts.push_back({ctx.contrib[g],g}); if(sub==0) break; }
  sort(opts.begin(), opts.end(), [](auto&a, auto&b){ return a.first < b.first; });
  for(auto &op: opts){ int gmask=op.second; int ev = ctx.evenMask[gmask]; groups.push_back(ctx.prod[gmask]); if(part_rec(ctx, unused^gmask, acc+ctx.contrib[gmask], groups, evenGroups+ev)) return true; groups.pop_back(); }
  return false;
}

bool enumerate_partition(const vector<Block>& blocks, const cpp_int& N, const cpp_int& target, int minG, int maxG, int parity, bool requireOneEven, vector<cpp_int>& out){
  int r=(int)blocks.size(); if(r<minG || r>20) return false;
  C.partCalls++;
  PartCtx ctx; ctx.N=N; ctx.target=target; ctx.minG=minG; ctx.maxG=maxG; ctx.parity=parity; ctx.requireEvenGroup=requireOneEven; ctx.full=(1<<r)-1;
  ctx.prod.assign(1<<r,1); ctx.contrib.assign(1<<r,0); ctx.evenMask.assign(1<<r,0);
  for(int m=1;m<=ctx.full;m++){ int l=m&-m; int i=__builtin_ctz((unsigned)l); ctx.prod[m]=ctx.prod[m^l]*blocks[i].val; ctx.evenMask[m]=ctx.evenMask[m^l]+(blocks[i].even?1:0); }
  for(int m=1;m<=ctx.full;m++) ctx.contrib[m]=N/ctx.prod[m];
  cpp_int maxSplit=0; for(int i=0;i<r;i++) maxSplit += ctx.contrib[1<<i];
  if(maxSplit < target || ctx.contrib[ctx.full] > target) return false;
  vector<cpp_int> groups;
  if(part_rec(ctx,ctx.full,0,groups,0)){ out=ctx.ans; return true; }
  return false;
}

void emit_witness(const vector<uint64_t>& P, const vector<cpp_int>& Q){
  auto Dnat=[](const vector<uint64_t>& S){ cpp_int D=1; for(auto x:S) D*=x; return D; };
  auto Nnat=[&](const vector<uint64_t>& S){ cpp_int D=Dnat(S), N=0; for(auto x:S) N += D/x; return N; };
  cpp_int Dq=1; for(auto &x:Q) Dq*=x; cpp_int Nq=0; for(auto &x:Q) Nq += Dq/x;
  cout << "WITNESS_FOUND:\nP:"; for(auto x:P) cout << " " << x;
  cout << "\nQ:"; for(auto &x:Q) cout << " " << sBig(x);
  cout << "\ncheck:\n  sumP: " << sBig(Nnat(P)) << "/" << sBig(Dnat(P))
       << "\n  sumQ: " << sBig(Nq) << "/" << sBig(Dq)
       << "\n  product: 1\n" << flush;
  exit(0);
}
void emit_witness2(const vector<cpp_int>& Pbig, const vector<uint64_t>& Qsmall){ vector<uint64_t> P; for(auto &x:Pbig){ if(x>numeric_limits<uint64_t>::max()) return; P.push_back(x.convert_to<uint64_t>()); } vector<cpp_int> Q; for(auto x:Qsmall) Q.push_back(x); emit_witness(P,Q); }

void processP(const vector<Den>& ds, int B, int qMax, const string& phase){
  State P=state_from(ds); C.states++; best(fabsl(P.sum-1.0L), phase+" sumP="+to_string((double)P.sum)+" size="+to_string(P.den.size()));
  if(P.N % 2 == 0) return;
  if(gcd_big(P.N,P.D)!=1) return;
  vector<Block> blocks; if(!smooth_factor(P.N,B,blocks)) return;
  C.smooth++; if(blocks.size()<4) return;
  vector<cpp_int> Q; if(enumerate_partition(blocks,P.N,P.D,4,qMax,0,false,Q)) emit_witness(P.den,Q);
}
void processQ(const vector<Den>& ds, int B, int pMax, const string& phase){
  State Q=state_from(ds); C.states++; best(fabsl(Q.sum-0.9L), phase+" sumQ="+to_string((double)Q.sum)+" size="+to_string(Q.den.size()));
  if(Q.N % 2 != 0) return;
  if(gcd_big(Q.N,Q.D)!=1) return;
  vector<Block> blocks; if(!smooth_factor(Q.N,B,blocks)) return;
  C.smooth++; if(blocks.size()<3) return;
  vector<cpp_int> P; if(enumerate_partition(blocks,Q.N,Q.D,3,pMax,-1,true,P)) emit_witness2(P,Q.den);
}

void seedP(int B, int qMax){
  vector<vector<int>> seeds={{2,3,5},{2,3,5,7},{2,3,5,7,11},{2,3,5,7,13},{2,3,5,11,13},{2,13,17},{2,13,17,19},{2,13,17,19,23},{2,17,19,23,29},{2,13,17,19,23,29}};
  auto ps=primes_up_to(1000);
  for(auto &v: seeds){ vector<Den> ds; bool ok=true; set<int> used; for(int x:v){ auto pf=pfactors(x,ps); for(int p:pf){ if(used.count(p)) ok=false; used.insert(p); } ds.push_back({(uint64_t)x,pf,1.0/(double)x,(x%2==0)}); } if(ok) processP(ds,B,qMax,"seeds"); }
}

void dfsP(const vector<Den>& pool, int start, vector<int>& used, vector<Den>& chosen, cpp_int D, cpp_int N, double sum, int minSz, int maxSz, int B, int qMax, const string& phase){
  if(timed_out()) return;
  int sz=(int)chosen.size();
  if(sz>=minSz && sum>1.0 && sum<1.25) processP(chosen,B,qMax,phase);
  progress(phase,"P-first smooth numerator sieve");
  if(sz>=maxSz || sum>=1.25) return;
  if(sum + greedy_max(pool,start,used,maxSz-sz) <= 1.0) return;
  for(int i=start;i<(int)pool.size();i++){
    if(!can_add(used,pool[i])) continue;
    double s2=sum+pool[i].inv; if(s2>=1.25 && sz+1>=minSz) continue;
    add_den(used,pool[i],1); chosen.push_back(pool[i]);
    dfsP(pool,i+1,used,chosen,D*pool[i].v,N*pool[i].v+D,s2,minSz,maxSz,B,qMax,phase);
    chosen.pop_back(); add_den(used,pool[i],-1);
    if(timed_out()) return;
  }
}
void runPFirst(int poolMax, int minSz, int maxSz, const vector<int>& Bs, int qMax, int seconds, const string& label){
  auto pool0=make_pool(poolMax,false); vector<Den> odds; for(auto &d:pool0) if(!d.even) odds.push_back(d);
  sort(odds.begin(), odds.end(), [](auto&a, auto&b){
    auto score=[](const Den& d){ double w=d.inv; if(d.pf.size()==1 && (d.pf[0]==3||d.pf[0]==5||d.pf[0]==7||d.pf[0]==11)) w*=0.25; return w; };
    return score(a)>score(b);
  });
  auto end=Clock::now()+chrono::seconds(seconds);
  auto ps=primes_up_to(max(1000,poolMax));
  for(int B: Bs){ if(Clock::now()>=end) break; seedP(B,qMax); vector<int> used(max(1001,poolMax+1),0); vector<Den> chosen; Den two{2,{2},0.5,true}; chosen.push_back(two); used[2]=1; deadline=end; useDeadline=true; dfsP(odds,0,used,chosen,2,1,0.5,minSz,maxSz,B,qMax,label+"_B"+to_string(B)); }
}

void dfsQ(const vector<Den>& pool, int start, vector<int>& used, vector<Den>& chosen, double sum, int maxSz, int B, int pMax, const string& phase){
  if(timed_out()) return;
  int sz=(int)chosen.size();
  if(sz>=4 && (sz%2==0) && sum>0.8 && sum<1.0) processQ(chosen,B,pMax,phase);
  progress(phase,"Q-first reverse smooth sieve");
  if(sz>=maxSz || sum>=1.0) return;
  if(sum + greedy_max(pool,start,used,maxSz-sz) <= 0.8) return;
  for(int i=start;i<(int)pool.size();i++){
    if(!can_add(used,pool[i])) continue;
    double s2=sum+pool[i].inv; if(s2>=1.0 && sz+1>=4) continue;
    add_den(used,pool[i],1); chosen.push_back(pool[i]);
    dfsQ(pool,i+1,used,chosen,s2,maxSz,B,pMax,phase);
    chosen.pop_back(); add_den(used,pool[i],-1);
    if(timed_out()) return;
  }
}
void runQFirst(int poolMax, int maxSz, const vector<int>& Bs, int pMax, int seconds, const string& label){
  auto pool=make_pool(poolMax,true);
  sort(pool.begin(), pool.end(), [](auto&a, auto&b){ return a.inv > b.inv; });
  auto end=Clock::now()+chrono::seconds(seconds);
  for(int B: Bs){ if(Clock::now()>=end) break; vector<int> used(max(1001,poolMax+1),0); vector<Den> chosen; deadline=end; useDeadline=true; dfsQ(pool,0,used,chosen,0.0,maxSz,B,pMax,label+"_B"+to_string(B)); }
}

vector<Den> randomP(const vector<Den>& pool, int maxSz){
  vector<Den> odds; for(auto &d:pool) if(!d.even) odds.push_back(d);
  vector<pair<double,Den>> scored; for(auto &d:odds){ double w=d.inv; if(d.pf.size()==1 && (d.pf[0]==3||d.pf[0]==5||d.pf[0]==7||d.pf[0]==11)) w*=0.15; w *= 0.3 + (rng()%1000000)/500000.0; scored.push_back({w,d}); }
  sort(scored.begin(), scored.end(), [](auto&a, auto&b){return a.first>b.first;});
  vector<int> used(2000); vector<Den> ch{{2,{2},0.5,true}}; used[2]=1; double sum=0.5;
  for(auto &sd:scored){ auto d=sd.second; if((int)ch.size()>=maxSz) break; if(!can_add(used,d)) continue; if(sum+d.inv>=1.25 && ch.size()>=3) continue; ch.push_back(d); add_den(used,d,1); sum+=d.inv; if(sum>1.0 && ch.size()>=3 && (rng()%4==0)) break; }
  if(!(sum>1.0 && sum<1.25 && ch.size()>=3)) ch.clear(); return ch;
}
vector<Den> randomQ(const vector<Den>& pool, int maxSz){
  vector<pair<double,Den>> scored; for(auto &d:pool) if(!d.even){ double w=d.inv*(0.3+(rng()%1000000)/500000.0); scored.push_back({w,d}); }
  sort(scored.begin(), scored.end(), [](auto&a, auto&b){return a.first>b.first;});
  vector<int> used(2000); vector<Den> ch; double sum=0;
  for(auto &sd:scored){ auto d=sd.second; if((int)ch.size()>=maxSz) break; if(!can_add(used,d)) continue; if(sum+d.inv>=1.0 && ch.size()>=4) continue; ch.push_back(d); add_den(used,d,1); sum+=d.inv; if(sum>0.8 && ch.size()>=4 && ch.size()%2==0 && (rng()%4==0)) break; }
  if(!(sum>0.8 && sum<1.0 && ch.size()>=4 && ch.size()%2==0)) ch.clear(); return ch;
}
void runRandom(int poolMax, int seconds){
  auto pool=make_pool(poolMax,false); auto end=Clock::now()+chrono::seconds(seconds); vector<int> Bs={60,100,200,500,1000}; int bi=0;
  while(Clock::now()<end){ int B=Bs[bi++%Bs.size()]; if(rng()%2){ auto ds=randomP(pool,14); if(!ds.empty()) processP(ds,B,16,"phase3_random_P_B"+to_string(B)); } else { auto ds=randomQ(pool,12); if(!ds.empty()) processQ(ds,B,25,"phase3_random_Q_B"+to_string(B)); } progress("phase3_random_smooth_state","sample constrained states"); }
}

int main(int argc, char** argv){
  int phase1=argc>1?atoi(argv[1]):900, phase2=argc>2?atoi(argv[2]):900, phase3=argc>3?atoi(argv[3]):1200;
  T0=Clock::now(); lastLog=T0;
  runPFirst(200,3,8,{60,100,200},12,phase1/2,"phase1_P_pool200");
  runQFirst(200,10,{60,100,200},8,phase1-phase1/2,"phase1_Q_pool200");
  runPFirst(1000,3,12,{60,100,200,500},16,phase2/2,"phase2_P_pool1000");
  runQFirst(1000,12,{60,100,200,500},12,phase2-phase2/2,"phase2_Q_pool1000");
  useDeadline=false;
  runRandom(1000,phase3);
  cout << "NO_WITNESS_FINAL_PHASE:\nmethod: smooth numerator + reciprocal-state search\nstates_generated: " << C.states << "\nsmooth_survivors: " << C.smooth << "\npartitions_checked: " << C.partNodes << "\nbest_near_miss: " << C.bestDesc << "\nrecommendation: park Erdos307 and request next open target\n";
}
