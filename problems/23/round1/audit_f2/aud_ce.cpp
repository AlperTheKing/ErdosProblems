#include <cstdio>
#include <vector>
#include <string>
#include <iostream>
using namespace std;
int main(){
    string line; long long cnt=0;
    while(getline(cin,line)){
        if(line.empty()) continue;
        int n=line[0]-63; vector<int> bits;
        for(size_t i=1;i<line.size();++i){int x=line[i]-63;for(int k=5;k>=0;--k)bits.push_back((x>>k)&1);}
        vector<pair<int,int>> E; int idx=0;
        for(int j=1;j<n;++j) for(int i=0;i<j;++i){ if(idx<(int)bits.size()&&bits[idx])E.push_back({i,j}); ++idx; }
        int m=E.size(); if(!m) continue;
        vector<int> adj(n,0), deg(n,0);
        for(auto&e:E){adj[e.first]|=1<<e.second; adj[e.second]|=1<<e.first; deg[e.first]++; deg[e.second]++;}
        bool tri=false; for(auto&e:E) if(adj[e.first]&adj[e.second]) tri=true;
        int best=-1;
        for(int mask=0;mask<(1<<n);++mask){int c=0;for(auto&e:E) if(((mask>>e.first)^(mask>>e.second))&1)++c; if(c>best)best=c;}
        int bip=m-best;
        if(5LL*bip>(long long)m){
            ++cnt;
            printf("g6=%s n=%d |E|=%d maxcut=%d bip=%d 5bip=%d triangle=%d mindeg=", line.c_str(),n,m,best,bip,5*bip,(int)tri);
            int md=99; for(int i=0;i<n;++i) md=min(md,deg[i]); printf("%d edges=",md);
            for(auto&e:E) printf("(%d,%d)",e.first,e.second);
            printf("\n");
        }
    }
    fprintf(stderr,"total counterexamples=%lld\n",cnt);
    return 0;
}
