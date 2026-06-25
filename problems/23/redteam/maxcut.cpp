// Exact MaxCut + beta for small N (<=30) via Gray-code enumeration with multithreading.
// Reads from stdin: N then E then E lines "u v" (0-indexed). Optionally multiple graphs.
// Protocol: first line = number of graphs G. Then for each: N E, then E pairs.
// Output per graph: "beta E maxcut density tri_free(0/1)"
#include <bits/stdc++.h>
#include <thread>
using namespace std;

int Nv;
vector<unsigned long long> nbr;
vector<pair<int,int>> edges;

bool triangle_free(){
    // adjacency bitsets in nbr
    for(auto&e:edges){
        int u=e.first,v=e.second;
        if(nbr[u]&nbr[v]) return false; // common neighbor
    }
    return true;
}

// exact maxcut by enumerating side assignments, vertex0 fixed to side0.
// We parallelize by fixing top 'P' bits across threads.
long long maxcut_exact(){
    int m=Nv-1; // free bits = vertices 1..N-1
    if(m<=0) return 0;
    // We'll split work: enumerate high bits in threads.
    int HW = m>20 ? 8 : (m>14? 6 : 0); // high bits handled by thread index
    long long globalBest=0;
    int nThreads = 1<<HW;
    vector<long long> bestT(nThreads,0);
    int lowBits=m-HW;
    auto worker=[&](int t){
        // high bits fixed = t (these correspond to vertices (1+lowBits)..(N-1))
        unsigned long long highMask=0;
        for(int b=0;b<HW;b++) if((t>>b)&1) highMask|=(1ULL<<(1+lowBits+b));
        // base side = highMask (vertex0 on side0)
        // enumerate low bits via gray code
        long long best=0;
        unsigned long long side=highMask;
        long long cut=0;
        unsigned long long fullmask=(Nv>=64)?~0ULL:((1ULL<<Nv)-1);
        // compute initial cut for side=highMask
        for(auto&e:edges){
            int u=e.first,v=e.second;
            if(((side>>u)&1)!=((side>>v)&1)) cut++;
        }
        best=cut;
        long long total=1LL<<lowBits;
        unsigned long long gprev=0;
        for(long long i=1;i<total;i++){
            unsigned long long g=i^(i>>1);
            unsigned long long diff=g^gprev;
            int b=__builtin_ctzll(diff);
            int vbit=b+1; // vertices 1..lowBits
            unsigned long long nb=nbr[vbit];
            long long opp=__builtin_popcountll(nb & side);
            long long same=__builtin_popcountll(nb & (~side) & fullmask);
            long long delta;
            if((side>>vbit)&1) delta=opp-same; else delta=same-opp;
            side^=(1ULL<<vbit);
            cut+=delta;
            if(cut>best)best=cut;
            gprev=g;
        }
        bestT[t]=best;
    };
    vector<thread> ths;
    int hwThreads=thread::hardware_concurrency(); if(hwThreads<1)hwThreads=8;
    // run in batches
    for(int t=0;t<nThreads;){
        int batch=min(hwThreads,nThreads-t);
        for(int k=0;k<batch;k++) ths.emplace_back(worker,t+k);
        for(auto&th:ths)th.join();
        ths.clear();
        t+=batch;
    }
    for(auto x:bestT) globalBest=max(globalBest,x);
    return globalBest;
}

int main(){
    int G; 
    if(!(cin>>G)) return 0;
    while(G--){
        int E; cin>>Nv>>E;
        edges.clear(); nbr.assign(Nv,0ULL);
        for(int i=0;i<E;i++){int u,v;cin>>u>>v;edges.push_back({u,v});nbr[u]|=(1ULL<<v);nbr[v]|=(1ULL<<u);}
        bool tf=triangle_free();
        long long mc=maxcut_exact();
        long long beta=(long long)E-mc;
        double dens=2.0*E/((double)Nv*Nv);
        cout<<beta<<" "<<E<<" "<<mc<<" "<<fixed<<setprecision(4)<<dens<<" "<<(tf?1:0)<<"\n";
    }
    return 0;
}
