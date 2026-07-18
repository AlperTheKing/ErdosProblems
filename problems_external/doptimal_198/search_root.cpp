#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <mutex>
#include <numeric>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {
using Bits = std::vector<unsigned char>;
long long sq(long long x) { return x * x; }

struct Options {
  int v=87, r=38, s=36, lambda=31, runs=64, threads=64;
  std::uint64_t steps=2000000, seed=19899, audit_period=100000;
  double t0=3.0, t1=0.08;
  std::uint64_t epoch=100000;
  bool stop_first=false;
  std::string output;
};

template<class T> T parse(const std::string& flag,const char* text) {
  std::istringstream in(text); T x{}; in>>x;
  if(!in||!in.eof()) throw std::runtime_error("bad "+flag); return x;
}
Options options(int argc,char**argv) {
  Options o;
  for(int i=1;i<argc;++i){std::string a=argv[i];
    auto next=[&](){if(++i>=argc)throw std::runtime_error("missing "+a);return argv[i];};
    if(a=="--v")o.v=parse<int>(a,next()); else if(a=="--r")o.r=parse<int>(a,next());
    else if(a=="--s")o.s=parse<int>(a,next()); else if(a=="--lambda")o.lambda=parse<int>(a,next());
    else if(a=="--runs")o.runs=parse<int>(a,next()); else if(a=="--threads")o.threads=parse<int>(a,next());
    else if(a=="--steps")o.steps=parse<std::uint64_t>(a,next()); else if(a=="--seed")o.seed=parse<std::uint64_t>(a,next());
    else if(a=="--audit-period")o.audit_period=parse<std::uint64_t>(a,next());
    else if(a=="--epoch")o.epoch=parse<std::uint64_t>(a,next());
    else if(a=="--t0")o.t0=parse<double>(a,next()); else if(a=="--t1")o.t1=parse<double>(a,next());
    else if(a=="--stop-first")o.stop_first=true; else if(a=="--output")o.output=next();
    else throw std::runtime_error("unknown option "+a);
  }
  return o;
}

std::uint64_t mix(std::uint64_t x){x+=0x9e3779b97f4a7c15ULL;x=(x^(x>>30))*0xbf58476d1ce4e5b9ULL;x=(x^(x>>27))*0x94d049bb133111ebULL;return x^(x>>31);}
int card(const Bits&x){return std::accumulate(x.begin(),x.end(),0);}
std::vector<int> raw_counts(const Bits&x){int v=x.size(),m=(v-1)/2;std::vector<int>n(m+1);for(int d=1;d<=m;++d)for(int a=0;a<v;++a)n[d]+=x[a]&&x[(a+d)%v];return n;}

struct State {
  int v,m,lambda; Bits x,y; std::vector<int> nx,ny; long long energy=0;
  State(Bits xx,Bits yy,int l):v(xx.size()),m((v-1)/2),lambda(l),x(std::move(xx)),y(std::move(yy)),nx(raw_counts(x)),ny(raw_counts(y)){
    for(int d=1;d<=m;++d)energy+=sq(nx[d]+ny[d]-lambda);
  }
  void toggle(bool first,int p){Bits&z=first?x:y;auto&n=first?nx:ny;int sign=z[p]?-1:1;
    for(int d=1;d<=m;++d){int old=nx[d]+ny[d]-lambda;int delta=sign*((int)z[(p+d)%v]+(int)z[(p-d+v)%v]);n[d]+=delta;energy+=sq(old+delta)-sq(old);}z[p]^=1;}
  int max_defect()const{int z=0;for(int d=1;d<=m;++d)z=std::max(z,std::abs(nx[d]+ny[d]-lambda));return z;}
};

bool audit(const State&s,int r,int t,std::string&why){auto a=raw_counts(s.x),b=raw_counts(s.y);long long e=0;
  if(card(s.x)!=r||card(s.y)!=t){why="weight";return false;}for(int d=1;d<=s.m;++d){if(a[d]!=s.nx[d]||b[d]!=s.ny[d]){why="count d="+std::to_string(d);return false;}e+=sq(a[d]+b[d]-s.lambda);}if(e!=s.energy){why="energy";return false;}return true;}

Bits random_bits(int v,int k,std::mt19937_64&g){if(k<1||k>v)throw std::runtime_error("bad weight");Bits z(v);z[0]=1;std::vector<int>p(v-1);std::iota(p.begin(),p.end(),1);std::shuffle(p.begin(),p.end(),g);for(int i=0;i<k-1;++i)z[p[i]]=1;return z;}
int pick(std::mt19937_64&g,int hi){return std::uniform_int_distribution<int>(1,hi)(g);}
std::pair<int,int> move(const Bits&z,std::mt19937_64&g){int out,in;do out=pick(g,z.size()-1);while(!z[out]);do in=pick(g,z.size()-1);while(z[in]);return {out,in};}
void apply_swap(State&s,bool first,std::pair<int,int>p){s.toggle(first,p.first);s.toggle(first,p.second);}
void undo_swap(State&s,bool first,std::pair<int,int>p){s.toggle(first,p.second);s.toggle(first,p.first);}
std::string set_text(const Bits&z){std::ostringstream o;o<<'[';bool f=true;for(int i=0;i<(int)z.size();++i)if(z[i]){if(!f)o<<',';o<<i;f=false;}return o.str()+"]";}

struct Result {bool solved=false,audit_ok=false;long long best=std::numeric_limits<long long>::max();std::uint64_t step=0;Bits x,y;};
Result one_run(const Options&o,int run,std::atomic<bool>&global_stop){std::mt19937_64 g(mix(o.seed+run));State s(random_bits(o.v,o.r,g),random_bits(o.v,o.s,g),o.lambda);Result z;z.best=s.energy;z.x=s.x;z.y=s.y;
  std::uniform_real_distribution<double>u(0,1);std::uint64_t stale=0;
  for(std::uint64_t step=1;step<=o.steps&&!(o.stop_first&&global_stop);++step){
    bool first=(g()&1);auto p=move(first?s.x:s.y,g);long long old=s.energy;apply_swap(s,first,p);long long delta=s.energy-old;
    std::uint64_t pos=(step-1)%o.epoch;double frac=(double)pos/std::max<std::uint64_t>(1,o.epoch-1);double temp=o.t0*std::pow(o.t1/o.t0,frac);
    if(delta>0&&u(g)>=std::exp(-(double)delta/temp))undo_swap(s,first,p);
    if(s.energy<z.best){z.best=s.energy;z.step=step;z.x=s.x;z.y=s.y;stale=0;}else ++stale;
    if(o.audit_period&&step%o.audit_period==0){std::string why;if(!audit(s,o.r,o.s,why))throw std::runtime_error("incremental audit "+why);}
    if(s.energy==0){std::string why;z.solved=audit(s,o.r,o.s,why);z.audit_ok=z.solved;z.best=0;z.step=step;z.x=s.x;z.y=s.y;if(!z.solved)throw std::runtime_error("zero audit "+why);global_stop=true;return z;}
    if(stale>4*o.epoch){for(int k=0;k<4;++k){bool f=(g()&1);apply_swap(s,f,move(f?s.x:s.y,g));}stale=0;}
  }
  State best(z.x,z.y,o.lambda);std::string why;z.audit_ok=audit(best,o.r,o.s,why)&&best.energy==z.best;if(!z.audit_ok)throw std::runtime_error("best audit "+why);return z;}

void write_cert(const std::string&path,const Options&o,const Result&z){std::ofstream f(path);if(!f)throw std::runtime_error("cannot write "+path);f<<"{\n  \"v\": "<<o.v<<", \"r\": "<<o.r<<", \"s\": "<<o.s<<", \"lambda\": "<<o.lambda<<",\n  \"X\": "<<set_text(z.x)<<",\n  \"Y\": "<<set_text(z.y)<<"\n}\n";}

int run(const Options&o){if(o.v%2!=1||o.r<1||o.s<1||o.r>=o.v||o.s>=o.v)throw std::runtime_error("bad parameters");if(1LL*o.r*(o.r-1)+1LL*o.s*(o.s-1)!=1LL*o.lambda*(o.v-1))throw std::runtime_error("parameter equation");
  std::cout<<"SEARCH v="<<o.v<<" params=("<<o.r<<','<<o.s<<';'<<o.lambda<<") runs="<<o.runs<<" steps="<<o.steps<<" threads="<<std::min(o.runs,o.threads)<<"\n";
  std::atomic<int>next{0},success{0};std::atomic<bool>stop{false};std::mutex lock;Result overall;std::vector<Result>all(o.runs);auto start=std::chrono::steady_clock::now();
  auto worker=[&]{for(;;){int i=next++;if(i>=o.runs||(o.stop_first&&stop))return;Result z=one_run(o,i,stop);all[i]=z;if(z.solved){++success;std::lock_guard<std::mutex>g(lock);overall=z;std::cout<<"ZERO run="<<i<<" step="<<z.step<<" X="<<set_text(z.x)<<" Y="<<set_text(z.y)<<"\n";}}};
  int nw=std::min(o.runs,o.threads);std::vector<std::thread>w;for(int i=0;i<nw;++i)w.emplace_back(worker);for(auto&t:w)t.join();
  long long best=std::numeric_limits<long long>::max();int bi=-1;for(int i=0;i<o.runs;++i)if(all[i].audit_ok&&all[i].best<best){best=all[i].best;bi=i;if(all[i].solved)overall=all[i];}
  double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();std::cout<<std::fixed<<std::setprecision(3)<<"DONE seconds="<<sec<<" successes="<<success<<'/'<<o.runs<<" best="<<best<<" best_run="<<bi<<" audited="<<std::count_if(all.begin(),all.end(),[](auto&z){return z.audit_ok;})<<'/'<<o.runs<<"\n";
  if(!o.output.empty()&&success){write_cert(o.output,o,overall);std::cout<<"WROTE "<<o.output<<"\n";}return 0;}
}
int main(int argc,char**argv){try{return run(options(argc,argv));}catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<'\n';return 2;}}
