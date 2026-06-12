#include <bits/stdc++.h>
using namespace std; using u64=uint64_t; using u128=__uint128_t;
struct Key{u64 n,d; bool operator==(Key const&o)const{return n==o.n&&d==o.d;}};
struct H{size_t operator()(Key const&k)const{return (uint64_t)(k.n*11995408973635179863ULL ^ k.d*10150724397891781847ULL);}};
struct Cand{int x; unsigned long long mask;}; vector<int> primes; unordered_map<int,int> pidx; vector<Cand> cands;
string s128(u128 x){ if(!x)return"0"; string s; while(x){s.push_back('0'+x%10); x/=10;} reverse(s.begin(),s.end()); return s;}
int main(int argc,char**argv){ int Pmax=argc>1?atoi(argv[1]):500; int Smax=argc>2?atoi(argv[2]):12; u64 Bound=argc>3?strtoull(argv[3],0,10):1000000000000000000ULL; int seconds=argc>4?atoi(argv[4]):600; vector<bool> comp(Pmax+1); for(int i=2;i<=Pmax;i++) if(!comp[i]){pidx[i]=primes.size(); primes.push_back(i); if((long long)i*i<=Pmax) for(long long j=1LL*i*i;j<=Pmax;j+=i) comp[j]=true;}
 for(int x=2;x<=Pmax;x++){ int y=x; unsigned long long m=0; for(int p:primes){if(p*p>y)break; if(y%p==0){ if(pidx[p]<64)m|=1ULL<<pidx[p]; while(y%p==0)y/=p; }} if(y>1 && pidx[y]<64)m|=1ULL<<pidx[y]; cands.push_back({x,m});}
 unordered_map<Key, vector<int>, H> sub; uint64_t examined=0; auto start=chrono::steady_clock::now();
 vector<int> elems;
 function<void(int,unsigned long long,u64,u128,int)> dfs = [&](int st,unsigned long long mask,u64 D,u128 N,int sz){
   if(chrono::duration_cast<chrono::seconds>(chrono::steady_clock::now()-start).count()>=seconds) return;
   if(sz>=2){ examined++; if(N < D){ sub.try_emplace(Key{(u64)N,D}, elems); } else if(N > D){ auto it=sub.find(Key{D,(u64)N}); if(it!=sub.end()){ cout<<"WITNESS_FOUND:\nP:"; for(int id:elems) cout<<" "<<cands[id].x; cout<<"\nQ:"; for(int id:it->second) cout<<" "<<cands[id].x; cout<<"\n"; exit(0);} } }
   if(sz>=Smax) return;
   for(int j=st;j<(int)cands.size();j++){ if(mask&cands[j].mask) continue; if(D>Bound/(u64)cands[j].x) break; elems.push_back(j); dfs(j+1,mask|cands[j].mask,D*cands[j].x,N*cands[j].x+D,sz+1); elems.pop_back(); }
 };
 dfs(0,0,1,0,0);
 auto runtime=chrono::duration_cast<chrono::seconds>(chrono::steady_clock::now()-start).count();
 cout<<"NO_WITNESS_UP_TO:\nphase: meet_in_the_middle\nP_max: "<<Pmax<<"\nsize_max: "<<Smax<<"\nproduct_bound: "<<Bound<<"\nsets_examined: "<<examined<<"\npartition_count: "<<sub.size()<<"\nruntime: "<<runtime<<"s\nnext_phase: extend MITM and big-factor dual search\n";
}
