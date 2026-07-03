#include <bits/stdc++.h>
using namespace std;

long long gcdll(long long a, long long b){ while(b){ long long t=a%b; a=b; b=t;} return a<0?-a:a; }
long long lcmll(long long a, long long b){ return a / gcdll(a,b) * b; }

int main(int argc, char** argv){
    if(argc < 2){ cerr << "usage: nch_t2_hall_checker rows.txt\n"; return 2; }
    ifstream in(argv[1]);
    if(!in){ cerr << "cannot open " << argv[1] << "\n"; return 2; }
    string name, side; int n, bad, rowN; long long gamma;
    in >> name >> n >> side >> gamma >> bad >> rowN;
    vector<unsigned int> masks(rowN); vector<int> denoms(rowN);
    long long den = 1;
    for(int i=0;i<rowN;i++){ unsigned long long m; int d; in >> m >> d; masks[i]=(unsigned int)m; denoms[i]=d; den=lcmll(den,d); }
    long long globalWorst = LLONG_MAX; pair<int,int> globalPair={-1,-1}; int globalUsize=-1; unsigned int globalMask=0;
    vector<long long> vals;
    for(int t1=0;t1<n;t1++) for(int t2=t1+1;t2<n;t2++){
        vector<int> freev; freev.reserve(n-2);
        int pos[32]; fill(begin(pos), end(pos), -1);
        for(int v=0; v<n; v++) if(v!=t1 && v!=t2){ pos[v]=(int)freev.size(); freev.push_back(v); }
        int k = n-2; unsigned int total = 1u << k;
        vals.assign(total, 0);
        unsigned int tbits = (1u<<t1) | (1u<<t2);
        for(int r=0;r<rowN;r++){
            unsigned int hitbits = masks[r] & tbits;
            int hit = ((hitbits>>t1)&1u) + ((hitbits>>t2)&1u);
            if(!hit) continue;
            unsigned int cm=0, mm=masks[r] & ~tbits;
            while(mm){ int v=__builtin_ctz(mm); mm &= mm-1; cm |= 1u << pos[v]; }
            vals[cm] += (long long)hit * (den / denoms[r]);
        }
        for(int i=0;i<k;i++){
            unsigned int bit=1u<<i;
            for(unsigned int base=0; base<total; base += bit<<1){
                for(unsigned int off=0; off<bit; off++) vals[base+bit+off] += vals[base+off];
            }
        }
        long long worst=LLONG_MAX; unsigned int worstMask=0;
        for(unsigned int m=0; m<total; m++){
            long long margin = (long long)__builtin_popcount(m) * den - vals[m];
            if(margin < worst){ worst=margin; worstMask=m; }
        }
        if(worst < globalWorst){ globalWorst=worst; globalPair={t1,t2}; globalMask=worstMask; globalUsize=__builtin_popcount(worstMask); }
        if(worst < 0){
            cout << "VERDICT FAIL\n";
            cout << "graph " << name << " side " << side << " pair " << t1 << " " << t2 << " den " << den << " worst_num " << worst << " Usize " << __builtin_popcount(worstMask) << "\n";
            cout << "U";
            for(int i=0;i<k;i++) if((worstMask>>i)&1u) cout << " " << freev[i];
            cout << "\n";
            return 1;
        }
    }
    cout << "VERDICT PASS\n";
    cout << "graph " << name << " n " << n << " side " << side << " gamma " << gamma << " bad " << bad << " rows " << rowN << " den " << den << "\n";
    cout << "worst_num " << globalWorst << " pair " << globalPair.first << " " << globalPair.second << " Usize " << globalUsize << " margin " << globalWorst << "/" << den << "\n";
    return 0;
}
