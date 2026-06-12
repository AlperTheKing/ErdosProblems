#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
using namespace std;
using boost::multiprecision::cpp_int;
struct Item{int x; vector<int> pf; double inv;};
vector<int> primes; vector<Item> items;
mt19937_64 rng(307307);
vector<int> pfactors(int n){ vector<int> r; int x=n; for(int p:primes){ if(p*p>x) break; if(x%p==0){ r.push_back(p); while(x%p==0)x/=p; }} if(x>1) r.push_back(x); return r; }
bool disjoint(const vector<int>&a,const vector<int>&b){ for(int x:a) for(int y:b) if(x==y) return false; return true; }
struct State{ vector<int> idx; double sum=0; };
bool ok_add(const State& s,int id){ for(int j:s.idx) if(!disjoint(items[j].pf,items[id].pf)) return false; return true; }
cpp_int prod_set(const State&s){ cpp_int D=1; for(int id:s.idx) D*=items[id].x; return D; }
cpp_int num_set(const State&s){ cpp_int D=prod_set(s), N=0; for(int id:s.idx) N += D / items[id].x; return N; }
bool exact(const State& P,const State& Q){ if(P.idx.size()<2||Q.idx.size()<2) return false; cpp_int Dp=prod_set(P), Np=num_set(P), Dq=prod_set(Q), Nq=num_set(Q); return Np==Dq && Nq==Dp; }
void print_state(const char* name,const State&s){ cout<<name<<":"; vector<int> xs; for(int id:s.idx) xs.push_back(items[id].x); sort(xs.begin(),xs.end()); for(int x:xs) cout<<" "<<x; cout<<"\n"; }
int main(int argc,char**argv){ int maxEl=argc>1?atoi(argv[1]):1000000; int seconds=argc>2?atoi(argv[2]):600; vector<bool> comp(maxEl+1); for(int i=2;i<=maxEl;i++) if(!comp[i]){ primes.push_back(i); if((long long)i*i<=maxEl) for(long long j=1LL*i*i;j<=maxEl;j+=i) comp[j]=true; }
 for(int x=2;x<=maxEl;x++){ auto pf=pfactors(x); if(pf.size()<=2) items.push_back({x,pf,1.0/x}); }
 auto start=chrono::steady_clock::now(); uint64_t steps=0, exacts=0; double best=1e9;
 uniform_int_distribution<int> distItem(0,(int)items.size()-1);
 while(chrono::duration_cast<chrono::seconds>(chrono::steady_clock::now()-start).count()<seconds){
   State P,Q;
   for(int t=0;t<20;t++){ int id=distItem(rng); if(ok_add(P,id) && P.idx.size()<20){ P.idx.push_back(id); P.sum+=items[id].inv; } id=distItem(rng); if(ok_add(Q,id) && Q.idx.size()<20){ Q.idx.push_back(id); Q.sum+=items[id].inv; }}
   double temp=0.05;
   for(int it=0;it<2000;it++,steps++){
     State *S = (rng()&1)?&P:&Q; State old=*S; double oldObj=fabs(log(max(1e-300,P.sum*Q.sum))) + 0.02*fabs((double)P.idx.size()-(double)Q.idx.size());
     int action=rng()%3;
     if(action==0 && S->idx.size()>2){ int pos=rng()%S->idx.size(); S->sum-=items[S->idx[pos]].inv; S->idx.erase(S->idx.begin()+pos); }
     else { int id=distItem(rng); if(ok_add(*S,id) && S->idx.size()<20){ S->idx.push_back(id); S->sum+=items[id].inv; }}
     double obj=fabs(log(max(1e-300,P.sum*Q.sum))) + 0.02*fabs((double)P.idx.size()-(double)Q.idx.size());
     if(obj<best){ best=obj; }
     if(obj>oldObj && exp((oldObj-obj)/temp) < (double)(rng()%1000000)/1000000.0) *S=old;
     if(fabs(P.sum*Q.sum-1.0)<1e-10){ exacts++; if(exact(P,Q)){ cout<<"WITNESS_FOUND:\n"; print_state("P",P); print_state("Q",Q); return 0; }}
   }
 }
 cout<<"NO_WITNESS_UP_TO:\nphase: randomized_local\nP_max: "<<maxEl<<"\nsize_max: 20\nproduct_bound: adaptive\nsets_examined: "<<steps<<"\npartition_count: "<<exacts<<"\nruntime: "<<seconds<<"s\nnext_phase: meet-in-the-middle partial D/N search\n";
}
