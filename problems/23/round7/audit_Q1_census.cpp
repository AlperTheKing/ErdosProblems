// audit_Q1_census.cpp -- INDEPENDENT re-implementation for the Q1 audit.
// Deliberately different algorithms from Q1_indcut.cpp:
//   * graph6 decode by explicit (j,i) nested-loop indexing (no while-search for the pair)
//   * maxcut by subset-DP  e[S] = e[S\{lsb}] + popcount(adj[lsb] & (S\{lsb}))  then
//     bip = min_S  e[S] + e[~S]      (NOT a Gray code)
//   * TWO families:
//       famI  = min over INDEPENDENT sets I of mono(N(I))            (what Q1_indcut computes)
//       famU  = min over ALL subsets  I of mono(union_{v in I} N(v)) (what Q1.md section 3 claims)
//   * c5 = number of induced C5 = number of 5-subsets inducing a 2-regular connected graph
//     (equals the number of C5 subgraphs in a triangle-free graph; NOT tr(A^5)/10)
// All arithmetic is exact integer.
//
// build: clang++ -O3 -march=native -std=c++17 audit_Q1_census.cpp -o audit_Q1_census.exe
#include <cstdio>
#include <cstdint>
#include <string>
#include <vector>
#include <iostream>
#include <algorithm>

static inline int pc(unsigned x){ return __builtin_popcount(x); }

int main(int argc, char** argv){
    std::ios::sync_with_stdio(false);
    long long nread=0, nA=0, nAU=0, nB=0, nBU=0, ntri=0;
    long long bestbn=0, bestbd=1; std::string bestbg;
    unsigned long long pn=0, pd=1; std::string pg;      // max bip^5/c5^2, exact
    std::vector<std::string> hitsB, hitsBU;
    std::string line;
    const int MAXS = 1<<16;
    std::vector<int> eS(MAXS), Uof(MAXS);
    std::vector<unsigned char> indf(MAXS), seen(MAXS);
    while(std::getline(std::cin,line)){
        while(!line.empty() && (line.back()=='\n'||line.back()=='\r')) line.pop_back();
        if(line.empty()) continue;
        int n = (int)line[0]-63;
        if(n<1||n>16){ fprintf(stderr,"bad n=%d\n",n); return 1; }
        unsigned adj[16]={0};
        {
            int byteidx=1, bitleft=0, cur=0;
            for(int j=1;j<n;j++) for(int i=0;i<j;i++){
                if(bitleft==0){
                    if((size_t)byteidx>=line.size()){ fprintf(stderr,"short g6: %s\n",line.c_str()); return 1; }
                    cur = (int)line[byteidx++]-63; bitleft=6;
                }
                int bit=(cur>>(bitleft-1))&1; bitleft--;
                if(bit){ adj[i]|=1u<<j; adj[j]|=1u<<i; }
            }
        }
        int m=0; for(int i=0;i<n;i++) m+=pc(adj[i]); m/=2;
        for(int i=0;i<n;i++){ unsigned t=adj[i]&~((1u<<(i+1))-1u);
            while(t){ int j=__builtin_ctz(t); t&=t-1; if(adj[i]&adj[j]) ntri++; } }
        unsigned full=(1u<<n)-1u;
        eS[0]=0; Uof[0]=0; indf[0]=1;
        for(unsigned S=1;S<=full;S++){
            int v=__builtin_ctz(S); unsigned R=S&(S-1);
            eS[S]=eS[R]+pc(adj[v]&R);
            Uof[S]=(int)(((unsigned)Uof[R])|adj[v]);
            indf[S]= (indf[R] && !(adj[v]&R)) ? 1:0;
        }
        int bip=m;
        for(unsigned S=0;S<=full;S+=2){ int t=eS[S]+eS[full^S]; if(t<bip) bip=t; }
        int famU=m, famI=m;
        for(unsigned S=0;S<=full;S++) seen[S]=0;
        for(unsigned I=0;I<=full;I++){
            unsigned U=(unsigned)Uof[I];
            int mo;
            if(!seen[U]){ seen[U]=1; mo=eS[U]+eS[full^U]; if(mo<famU) famU=mo; if(indf[I]&&mo<famI) famI=mo; }
            else if(indf[I]){ mo=eS[U]+eS[full^U]; if(mo<famI) famI=mo; }
        }
        long long c5=0;
        for(unsigned S=0;S<=full;S++){
            if(pc(S)!=5||eS[S]!=5) continue;
            bool ok=true; unsigned t=S;
            while(t){ int v=__builtin_ctz(t); t&=t-1; if(pc(adj[v]&S)!=2){ ok=false; break; } }
            if(!ok) continue;
            unsigned start=S&(~S+1u), comp=start, fr=start;
            while(fr){ unsigned nx=0,u=fr; while(u){ int v=__builtin_ctz(u); u&=u-1; nx|=adj[v]&S&~comp; } comp|=nx; fr=nx; }
            if(comp==S) c5++;
        }
        nread++;
        if(famI>bip) nA++;
        if(famU>bip) nAU++;
        if(25LL*famI>(long long)n*n){ nB++; if(hitsB.size()<10) hitsB.push_back(line+" bip="+std::to_string(bip)+" famI="+std::to_string(famI)+" n="+std::to_string(n)); }
        if(25LL*famU>(long long)n*n){ nBU++; if(hitsBU.size()<10) hitsBU.push_back(line+" bip="+std::to_string(bip)+" famU="+std::to_string(famU)+" n="+std::to_string(n)); }
        if(25LL*bip*bestbd > bestbn*(long long)n*n){ bestbn=25LL*bip; bestbd=(long long)n*n; bestbg=line+" bip="+std::to_string(bip)+" n="+std::to_string(n); }
        if(c5>0&&bip>0){
            unsigned long long num=1; for(int i=0;i<5;i++) num*=(unsigned long long)bip;
            unsigned long long den=(unsigned long long)c5*(unsigned long long)c5;
            if((__int128)num*(__int128)pd > (__int128)pn*(__int128)den){ pn=num; pd=den; pg=line+" bip="+std::to_string(bip)+" c5="+std::to_string(c5)+" n="+std::to_string(n); }
        }
    }
    printf("graphs read        : %lld\n", nread);
    printf("triangles seen     : %lld\n", ntri);
    printf("famI > bip         : %lld\n", nA);
    printf("famU > bip         : %lld\n", nAU);
    printf("25*famI > n^2      : %lld\n", nB);
    for(auto&s:hitsB) printf("   BI %s\n", s.c_str());
    printf("25*famU > n^2      : %lld\n", nBU);
    for(auto&s:hitsBU) printf("   BU %s\n", s.c_str());
    printf("max 25*bip/n^2     : %lld/%lld  at %s\n", bestbn, bestbd, bestbg.c_str());
    printf("max bip^5/c5^2     : %llu/%llu  at %s\n", pn, pd, pg.c_str());
    return 0;
}
