#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
using namespace std;
using boost::multiprecision::cpp_int;
static const int MOD=1000003;
cpp_int prod_int(int k,long long x){ cpp_int r=1; for(int i=1;i<=k;i++) r*=x+i; return r; }
bool exact_hit(int k,long long n,long long m){ if(m<n+k) return false; return prod_int(k,m)==prod_int(k,n)*25; }
int prod_mod(int k,long long x){ long long r=1, xm=x%MOD; for(int i=1;i<=k;i++) r=r*((xm+i)%MOD)%MOD; return (int)r; }
int step_mod(int cur,int k,long long x,const vector<int>& inv){ long long den=(x+1)%MOD; if(den==0) return prod_mod(k,x+1); long long num=(x+k+1)%MOD; return (long long)cur*inv[(int)den]%MOD*num%MOD; }
int main(int argc,char**argv){
 int K0=argc>1?atoi(argv[1]):61, K1=argc>2?atoi(argv[2]):300; long long N0=argc>3?atoll(argv[3]):1000001LL, N1=argc>4?atoll(argv[4]):100000000LL; int R=argc>5?atoi(argv[5]):4;
 vector<int> inv(MOD); inv[1]=1; for(int i=2;i<MOD;i++) inv[i]=(long long)(MOD-MOD/i)*inv[MOD%i]%MOD;
 atomic<bool> found(false); int fk=0; long long fn=0,fm=0;
 int threads=1;
 #ifdef _OPENMP
 threads=omp_get_max_threads();
 #endif
 cerr << "threads=" << threads << "\n";
 #pragma omp parallel for schedule(dynamic,1)
 for(int k=K0;k<=K1;k++){
   if(found.load()) continue;
   long double alpha=powl(25.0L,1.0L/k); long double c=((long double)k+1.0L)/2.0L; long double A=-((long double)k*((long double)k*k-1.0L))/24.0L; long double beta=alpha*A*(1.0L-1.0L/(alpha*alpha))/(long double)k;
   auto center=[&](long long n)->long long{ long double N=(long double)n+c; return llround(alpha*N+beta/N-c); };
   long long n=N0; int pn=prod_mod(k,n); vector<long long> mx(2*R+1); vector<int> pm(2*R+1); long long cen=center(n);
   for(int idx=0;idx<2*R+1;idx++){ long long m=cen+(idx-R); mx[idx]=m; pm[idx]=m>=0?prod_mod(k,m):0; }
   for(; n<=N1 && !found.load(); n++){
     if(n>N0) pn=step_mod(pn,k,n-1,inv);
     long long newcen=center(n);
     if(newcen!=cen){
       for(int idx=0;idx<2*R+1;idx++){ long long tm=newcen+(idx-R); if(mx[idx]<0||tm<mx[idx]||tm-mx[idx]>20){ mx[idx]=tm; pm[idx]=tm>=0?prod_mod(k,tm):0; } else { while(mx[idx]<tm){ pm[idx]=step_mod(pm[idx],k,mx[idx],inv); mx[idx]++; } } }
       cen=newcen;
     }
     int target=(long long)25*pn%MOD;
     for(int idx=0;idx<2*R+1;idx++){ long long m=mx[idx]; if(m>=n+k && pm[idx]==target && exact_hit(k,n,m)){ bool expected=false; if(found.compare_exchange_strong(expected,true)){ fk=k; fn=n; fm=m; } break; } }
   }
   #pragma omp critical
   { cerr << "completed parallel k=" << k << "\n"; }
 }
 if(found.load()) cout << "HIT " << fk << " " << fn << " " << fm << "\n"; else cout << "NO_HIT_PARALLEL " << K0 << " " << K1 << " " << N1 << "\n";
}
