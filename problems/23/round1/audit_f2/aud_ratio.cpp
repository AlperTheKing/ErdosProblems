// Independent exact re-run of "is there a triangle-free G with 5*bip(G) > |E| ?"
// reads graph6 lines on stdin, exact max cut by brute force over 2^(n-1).
#include <cstdio>
#include <cstring>
#include <vector>
#include <string>
#include <iostream>
using namespace std;

int main(){
    string line;
    long long cnt=0; long long bestNum=0,bestDen=1; string bestG; int bn=0,be=0,bb=0;
    long long beats=0; string firstBeat;
    while(getline(cin,line)){
        if(line.empty()) continue;
        int n = line[0]-63;
        vector<int> bits;
        for(size_t i=1;i<line.size();++i){int x=line[i]-63;for(int k=5;k>=0;--k)bits.push_back((x>>k)&1);}
        vector<pair<int,int>> E; int idx=0;
        for(int j=1;j<n;++j) for(int i=0;i<j;++i){ if(idx<(int)bits.size()&&bits[idx])E.push_back({i,j}); ++idx; }
        int m=E.size(); if(!m) continue;
        // triangle check
        vector<int> adj(n,0);
        for(auto&e:E){adj[e.first]|=1<<e.second; adj[e.second]|=1<<e.first;}
        for(auto&e:E) if(adj[e.first]&adj[e.second]){fprintf(stderr,"TRIANGLE\n");return 1;}
        int best=-1;
        for(int mask=0;mask<(1<<(n-1));++mask){
            int s=mask<<1; int c=0;
            for(auto&e:E) if(((s>>e.first)^(s>>e.second))&1) ++c;
            if(c>best)best=c;
        }
        int bip=m-best; ++cnt;
        if(5LL*bip> (long long)m){ ++beats; if(firstBeat.empty()) firstBeat=line; }
        if((long long)bip*bestDen > bestNum*(long long)m){ bestNum=bip; bestDen=m; bestG=line; bn=n;be=m;bb=bip; }
    }
    printf("graphs=%lld  max bip/|E| = %lld/%lld  at %s (n=%d,|E|=%d,bip=%d)  #with 5*bip>|E| = %lld  %s\n",
           cnt,bestNum,bestDen,bestG.c_str(),bn,be,bb,beats,firstBeat.c_str());
    return 0;
}
