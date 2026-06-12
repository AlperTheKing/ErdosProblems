#include <bits/stdc++.h>
using namespace std;
using u64=uint64_t; using u128=__uint128_t;

const int P_MAX=5000, K_SIZE_MAX=6; const u64 PROD_BOUND=1000000000000000000ULL;
vector<int> primes; unordered_map<int,int> pidx;
struct Cand{int x; u128 mask;}; vector<Cand> cands;

u64 mul_mod(u64 a,u64 b,u64 mod){ return (u128)a*b%mod; }
u64 pow_mod(u64 a,u64 d,u64 mod){ u64 r=1; while(d){ if(d&1) r=mul_mod(r,a,mod); a=mul_mod(a,a,mod); d>>=1;} return r; }
bool isPrime64(u64 n){ if(n<2) return false; for(u64 p: {2ULL,3ULL,5ULL,7ULL,11ULL,13ULL,17ULL,19ULL,23ULL,29ULL,31ULL,37ULL}){ if(n%p==0) return n==p; } u64 d=n-1,s=0; while((d&1)==0){d>>=1;s++;} for(u64 a: {2ULL,3ULL,5ULL,7ULL,11ULL,13ULL,17ULL,19ULL,23ULL,29ULL,31ULL,37ULL}){ if(a>=n) continue; u64 x=pow_mod(a,d,n); if(x==1||x==n-1) continue; bool comp=true; for(u64 r=1;r<s;r++){ x=mul_mod(x,x,n); if(x==n-1){comp=false;break;} } if(comp) return false; } return true; }
mt19937_64 rng(1234567);
u64 pollard(u64 n){ if(n%2==0) return 2; if(n%3==0) return 3; while(true){ u64 c=uniform_int_distribution<u64>(1,n-1)(rng), x=uniform_int_distribution<u64>(0,n-1)(rng), y=x,d=1; auto f=[&](u64 v){return (mul_mod(v,v,n)+c)%n;}; for(int iter=0; d==1; iter++){ x=f(x); y=f(f(y)); u64 diff=x>y?x-y:y-x; d=std::gcd(diff,n); if(iter>10000) break; } if(d>1 && d<n) return d; } }
void factor_rec(u64 n, vector<u64>& fs){ if(n==1) return; if(isPrime64(n)){fs.push_back(n);return;} u64 d=pollard(n); factor_rec(d,fs); factor_rec(n/d,fs); }
vector<u64> prime_power_blocks(u64 n){ vector<u64> fs; factor_rec(n,fs); sort(fs.begin(),fs.end()); vector<u64> blocks; for(size_t i=0;i<fs.size();){ u64 p=fs[i], pp=1; while(i<fs.size()&&fs[i]==p){ pp*=p; i++; } blocks.push_back(pp); } return blocks; }

double greedy_ub(int start,u128 mask,int slots,u64 pleft){ double s=0; int c=0; for(int j=start;j<(int)cands.size();j++){ int x=cands[j].x; if(c>=slots) break; if((u64)x>pleft) break; if(mask & cands[j].mask) continue; s += 1.0/x; c++; pleft/=x; mask |= cands[j].mask; } return s; }

bool rec_part(const vector<u64>& blocks, const vector<u64>& prod, u64 Np, u64 Dp, int unused, u64 acc, vector<u64>& group){
    if(acc>Dp) return false;
    if(unused==0) return group.size()>=2 && acc==Dp;
    u64 mx=0; int mm=unused; while(mm){ int l=mm&-mm; int i=__builtin_ctz(l); mx += Np/blocks[i]; mm^=l; if(acc+mx>=Dp && mx>Dp){} }
    if(acc+mx<Dp) return false;
    if(acc + Np/prod[unused] > Dp) return false;
    int lsb=unused&-unused, rest=unused^lsb;
    vector<pair<u64,int>> subs; int sub=rest;
    while(true){ int g=sub|lsb; subs.push_back({Np/prod[g],g}); if(sub==0) break; sub=(sub-1)&rest; }
    sort(subs.begin(),subs.end());
    for(auto [contrib,g]: subs){ group.push_back(prod[g]); if(rec_part(blocks,prod,Np,Dp,unused^g,acc+contrib,group)) return true; group.pop_back(); }
    return false;
}

bool has_Q(u64 Np,u64 Dp, vector<u64>& out){
    auto blocks=prime_power_blocks(Np); int r=blocks.size(); if(r<2 || r>24) return false;
    u128 mx=0; for(u64 b: blocks) mx += Np/b; if(mx < Dp) return false;
    int full=(1<<r)-1; vector<u64> prod(1<<r,1); for(int m=1;m<=full;m++){ int l=m&-m; int i=__builtin_ctz(l); prod[m]=prod[m^l]*blocks[i]; }
    vector<u64> group; if(rec_part(blocks,prod,Np,Dp,full,0,group)){ out=group; return true; } return false;
}

u64 to_u64(u128 x){ return (u64)x; }
string s128(u128 x){ if(x==0) return "0"; string s; while(x){ s.push_back('0'+x%10); x/=10;} reverse(s.begin(),s.end()); return s; }

u64 examined=0;
void dfs(int start,u128 mask,u64 D,u128 N,int size, vector<int>& elems){
    if(size>=2 && N>D){ examined++; vector<u64> q; if(N <= numeric_limits<u64>::max() && has_Q((u64)N,D,q)){ cout << "WITNESS_FOUND\nP"; for(int e: elems) cout << ' ' << e; cout << "\nD " << D << "\nN " << s128(N) << "\nQ"; sort(q.begin(),q.end()); for(u64 x:q) cout << ' ' << x; cout << "\n"; exit(0); } }
    if(size>=K_SIZE_MAX) return;
    if((long double)N/(long double)D + greedy_ub(start,mask,K_SIZE_MAX-size,PROD_BOUND/D) <= 1.0L) return;
    for(int j=start;j<(int)cands.size();j++){
        int x=cands[j].x; if(D > PROD_BOUND/(u64)x) break; if(mask & cands[j].mask) continue; u64 D2=D*x; u128 N2=N*x + D; if((long double)N2/(long double)D2 + greedy_ub(j+1,mask|cands[j].mask,K_SIZE_MAX-size-1,PROD_BOUND/D2) <= 1.0L) continue; elems.push_back(x); dfs(j+1,mask|cands[j].mask,D2,N2,size+1,elems); elems.pop_back();
    }
}
int main(){
    for(int n=2;n<=P_MAX;n++){ bool ok=true; for(int p:primes){ if(p*p>n) break; if(n%p==0){ok=false;break;} } if(ok){pidx[n]=primes.size(); primes.push_back(n);} }
    for(int x=2;x<=P_MAX;x++){ int y=x; u128 m=0; for(int p:primes){ if(p*p>y) break; if(y%p==0){ m |= ((u128)1<<pidx[p]); while(y%p==0) y/=p; } } if(y>1) m |= ((u128)1<<pidx[y]); cands.push_back({x,m}); }
    vector<int> elems; dfs(0,0,1,0,0,elems);
    cout << "NO_WITNESS_UP_TO\nP_max: " << P_MAX << "\nK_SIZE_MAX: " << K_SIZE_MAX << "\nproduct_bound: " << PROD_BOUND << "\nsets_examined: " << examined << "\nnext_range: increase size/P bound and run reverse numerator-product search\n";
}
