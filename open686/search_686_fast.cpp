#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
using namespace std;
using boost::multiprecision::cpp_int;
static const long long MOD = 1000000007LL;

long long modpow(long long a, long long e){ long long r=1%MOD; while(e){ if(e&1) r=(__int128)r*a%MOD; a=(__int128)a*a%MOD; e>>=1;} return r; }

cpp_int prod_int(int k, long long x){ cpp_int r=1; for(int i=1;i<=k;i++) r *= (x+i); return r; }

long long prod_mod_fact(const vector<int>& fact, const vector<int>& invfact, int k, long long x){
    return (long long)fact[(size_t)(x+k)] * invfact[(size_t)x] % MOD;
}

bool exact_hit(int k, long long n, long long m){
    if(m < n + k) return false;
    cpp_int lhs = prod_int(k,m);
    cpp_int rhs = prod_int(k,n) * 25;
    return lhs == rhs;
}

long long binary_find(int k, long long n){
    cpp_int target = prod_int(k,n) * 25;
    long long lo = n + k;
    if(prod_int(k,lo) > target) return -1;
    long double alpha = powl(25.0L, 1.0L/k);
    long long hi = max(lo+1, (long long)(alpha*(n+1) + k + 16));
    while(prod_int(k,hi) < target){
        if(hi > (LLONG_MAX-1)/2) return -1;
        hi = hi*2+1;
    }
    while(lo+1<hi){
        long long mid = lo + (hi-lo)/2;
        if(prod_int(k,mid) < target) lo=mid; else hi=mid;
    }
    return prod_int(k,hi)==target ? hi : -1;
}

int main(int argc, char** argv){
    int KMAX = argc>1 ? atoi(argv[1]) : 100;
    int NMAX = argc>2 ? atoi(argv[2]) : 1000000;
    int R = argc>3 ? atoi(argv[3]) : 6;
    // k=2 Pell/factorization obstruction
    vector<tuple<long long,long long,long long,long long,long long,long long>> pell;
    for(long long a=-24;a<=24;a++) if(a && (-24)%a==0){
        long long b=-24/a;
        if(((a+b)&1)==0 && (b-a)%10==0){
            long long X=(a+b)/2, Y=(b-a)/10;
            if(X>0 && Y>0 && (X&1) && (Y&1) && X*X-25*Y*Y==-24){
                long long m=(X-3)/2, n=(Y-3)/2;
                if(n>=0 && m>=n+2 && (m+1)*(m+2)==25*(n+1)*(n+2)) pell.emplace_back(n,m,X,Y,a,b);
            }
        }
    }
    cerr << "Pell k=2 admissible solutions=" << pell.size() << "\n";
    int maxX = 0;
    for(int k=2;k<=KMAX;k++){
        long double alpha = powl(25.0L, 1.0L/k);
        long double c = ((long double)k + 1.0L) / 2.0L;
        long long mhi = llround(alpha * ((long double)NMAX + c) - c) + R + 10;
        mhi = max<long long>(mhi, (long long)NMAX + KMAX + R + 10);
        maxX = max<long long>(maxX, mhi + k + 5);
    }
    cerr << "precompute up to " << maxX << " mod " << MOD << "\n";
    vector<int> fact(maxX+1), invfact(maxX+1);
    fact[0]=1;
    for(int i=1;i<=maxX;i++) fact[i]=(long long)fact[i-1]*i%MOD;
    invfact[maxX]=modpow(fact[maxX], MOD-2);
    for(int i=maxX;i>=1;i--) invfact[i-1]=(long long)invfact[i]*i%MOD;

    for(int k=2;k<=KMAX;k++){
        if(k==2){ cerr << "completed k=2 Pell obstruction and candidate scan skipped\n"; continue; }
        long double alpha = powl(25.0L, 1.0L/k);
        long double c = ((long double)k + 1.0L) / 2.0L;
        long long exactSmall = min<long long>(NMAX, 2000);
        for(long long n=0;n<=exactSmall;n++){
            long long m = binary_find(k,n);
            if(m>=0){ cout << "HIT " << k << " " << n << " " << m << "\n"; return 0; }
        }
        for(long long n=exactSmall+1;n<=NMAX;n++){
            long long center = llround(alpha * ((long double)n + c) - c);
            long long pn = prod_mod_fact(fact, invfact, k, n);
            long long target = 25LL * pn % MOD;
            for(int r=-R;r<=R;r++){
                long long m = center + r;
                if(m < n + k || m < 0 || m + k > maxX) continue;
                long long pm = prod_mod_fact(fact, invfact, k, m);
                if(pm == target && exact_hit(k,n,m)){
                    cout << "HIT " << k << " " << n << " " << m << "\n"; return 0;
                }
            }
        }
        cerr << "completed k=" << k << " up to n=" << NMAX << "\n";
    }
    cout << "NO_HIT " << KMAX << " " << NMAX << "\n";
    return 0;
}
