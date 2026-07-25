// C3_cut.cpp  -- exact and heuristic bip = |E| - maxcut for (vertex-weighted) graphs.
// Erdos #23 round5, label C3.  EXACT INTEGER ARITHMETIC everywhere.
//
// Modes (argv[1]):
//   exact   FILE           : exact bip over all 2^(n-1) cuts, n<=40 (unweighted, popcount Gray code)
//   exactw  FILE           : exact weighted bip, weights on vertices, n<=32
//   heur    FILE ITERS     : tabu/local-search UPPER bound on bip (valid one-sided refutation)
//   both    FILE           : heur first; if 25*mono_best > n^2 then exact (if n small enough)
//
// FILE format:
//   n m
//   u v         (m lines, 0-based)
//   [w0 w1 ... w_{n-1}]   (optional final line for exactw; default all 1)
//
// Output: single line  "n= N m= M bipUB= X" or "n= N m= M bip= X" plus "N2= n^2" and "25bip= ..".
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <thread>
#include <atomic>
#include <algorithm>
#include <random>
#include <string>
using namespace std;

typedef unsigned long long u64;
typedef long long ll;

static int N, M;
static vector<pair<int,int>> E;
static vector<ll> W;
static vector<u64> adjm;              // adjacency bitmask
static vector<vector<int>> adjl;

static void readfile(const char* fn){
    FILE* f = fopen(fn,"r");
    if(!f){ fprintf(stderr,"cannot open %s\n",fn); exit(1);}
    if(fscanf(f,"%d %d",&N,&M)!=2){ fprintf(stderr,"bad header\n"); exit(1);}
    E.resize(M);
    for(int i=0;i<M;i++){ int u,v; if(fscanf(f,"%d %d",&u,&v)!=2){fprintf(stderr,"bad edge %d\n",i);exit(1);} E[i]={u,v}; }
    W.assign(N,1);
    for(int i=0;i<N;i++){ long long x; if(fscanf(f,"%lld",&x)==1) W[i]=x; else break; }
    fclose(f);
    adjm.assign(N,0ULL); adjl.assign(N,{});
    for(auto&e:E){ adjm[e.first]|=1ULL<<e.second; adjm[e.second]|=1ULL<<e.first;
                   adjl[e.first].push_back(e.second); adjl[e.second].push_back(e.first); }
}

// ---------- exact unweighted: minimise monochromatic edge count over all cuts ----------
// vertex 0 fixed on side 0.  Gray code over bits 1..N-1.
static ll exact_unweighted(){
    int k = N-1;                     // free bits
    int hi = (k>18)? (k-18) : 0;     // split top hi bits over threads
    int lo = k-hi;
    int nchunk = 1<<hi;
    unsigned hw = thread::hardware_concurrency(); if(hw==0) hw=8; if(hw>8) hw=8;
    int T = (int)min<unsigned>(hw, (unsigned)max(1,nchunk));
    vector<ll> best(T, (ll)4e18);
    auto worker=[&](int t){
        ll bst=(ll)4e18;
        for(int c=t;c<nchunk;c+=T){
            // S = set of vertices on side 1 (vertex 0 always side 0)
            u64 S = ((u64)c) << (1+lo);
            // initial mono count
            ll mono=0;
            for(auto&e:E){ bool a=(S>>e.first)&1ULL, b=(S>>e.second)&1ULL; if(a==b) mono++; }
            if(mono<bst) bst=mono;
            u64 lim = 1ULL<<lo;
            for(u64 g=1; g<lim; g++){
                int b = __builtin_ctzll(g);        // bit of low block to flip
                int v = 1+b;                        // vertex index
                u64 av = adjm[v];
                // before flip: v's side
                bool sv = (S>>v)&1ULL;
                u64 sameMask = sv ? S : ~S;
                ll same = __builtin_popcountll(av & sameMask);
                ll diff = (ll)adjl[v].size() - same;
                mono += diff - same;
                S ^= (1ULL<<v);
                if(mono<bst) bst=mono;
            }
        }
        best[t]=bst;
    };
    vector<thread> th;
    for(int t=0;t<T;t++) th.emplace_back(worker,t);
    for(auto&x:th) x.join();
    return *min_element(best.begin(),best.end());
}

// ---------- exact vertex-weighted ----------
static ll exact_weighted(){
    int k=N-1;
    int hi=(k>16)?(k-16):0; int lo=k-hi; int nchunk=1<<hi;
    unsigned hw=thread::hardware_concurrency(); if(hw==0) hw=8; if(hw>8) hw=8;
    int T=(int)min<unsigned>(hw,(unsigned)max(1,nchunk));
    vector<ll> best(T,(ll)4e18);
    auto worker=[&](int t){
        ll bst=(ll)4e18;
        vector<ll> sameW(N,0);
        for(int c=t;c<nchunk;c+=T){
            u64 S=((u64)c)<<(1+lo);
            ll mono=0;
            for(auto&e:E){ bool a=(S>>e.first)&1ULL,b=(S>>e.second)&1ULL; if(a==b) mono+=W[e.first]*W[e.second]; }
            for(int v=0;v<N;v++){ ll s=0; bool sv=(S>>v)&1ULL;
                for(int w:adjl[v]) if((bool)((S>>w)&1ULL)==sv) s+=W[w];
                sameW[v]=s; }
            if(mono<bst) bst=mono;
            u64 lim=1ULL<<lo;
            for(u64 g=1;g<lim;g++){
                int b=__builtin_ctzll(g); int v=1+b;
                ll tot=0; for(int w:adjl[v]) tot+=W[w];
                ll same=sameW[v], diff=tot-same;
                mono += W[v]*(diff-same);
                bool sv=(S>>v)&1ULL;
                // v moves from side sv to !sv : neighbours' sameW change
                for(int w:adjl[v]){ bool sw=(S>>w)&1ULL; if(sw==sv) sameW[w]-=W[v]; else sameW[w]+=W[v]; }
                sameW[v]=diff;
                S^=(1ULL<<v);
                if(mono<bst) bst=mono;
            }
        }
        best[t]=bst;
    };
    vector<thread> th; for(int t=0;t<T;t++) th.emplace_back(worker,t);
    for(auto&x:th) x.join();
    return *min_element(best.begin(),best.end());
}

// ---------- heuristic: repeated randomized 1-opt + tabu, returns UPPER bound on bip ----------
static ll heuristic(long iters, unsigned seed){
    unsigned hw=thread::hardware_concurrency(); if(hw==0) hw=8; if(hw>8) hw=8;
    int T=(int)hw;
    vector<ll> best(T,(ll)4e18);
    auto worker=[&](int t){
        mt19937_64 rng(seed*7919ULL + t*104729ULL + 12345ULL);
        vector<char> side(N); vector<ll> gain(N); vector<int> tabu(N,0);
        ll bst=(ll)4e18;
        long restarts = max(1L, iters/ max(1,(20*N)));
        for(long r=0;r<restarts;r++){
            for(int v=0;v<N;v++) side[v]=(char)(rng()&1);
            ll mono=0;
            for(auto&e:E) if(side[e.first]==side[e.second]) mono+=W[e.first]*W[e.second];
            // gain[v] = change in mono if v flips
            for(int v=0;v<N;v++){ ll s=0,d=0; for(int w:adjl[v]){ if(side[w]==side[v]) s+=W[w]; else d+=W[w]; } gain[v]=W[v]*(d-s); }
            fill(tabu.begin(),tabu.end(),0);
            ll cur=mono; if(cur<bst) bst=cur;
            int noimp=0;
            for(long it=0; it<20L*N && noimp<8*N; it++){
                int bv=-1; ll bg=(ll)4e18;
                for(int v=0;v<N;v++){ if(tabu[v]>it && cur+gain[v]>=bst) continue; if(gain[v]<bg){bg=gain[v];bv=v;} }
                if(bv<0) break;
                // apply
                cur += gain[bv];
                ll gv=gain[bv];
                for(int w:adjl[bv]){
                    // gain[w] = W[w]*(d_w - s_w).  bv leaves w's side => s_w-=W[bv], d_w+=W[bv].
                    if(side[w]==side[bv]) gain[w] += 2*W[bv]*W[w];
                    else                  gain[w] -= 2*W[bv]*W[w];
                }
                side[bv]^=1; gain[bv]=-gv;
                tabu[bv]= (int)(it + 3 + (rng()% (unsigned)max(2,N/4)));
                if(cur<bst){ bst=cur; noimp=0; } else noimp++;
            }
        }
        best[t]=bst;
    };
    vector<thread> th; for(int t=0;t<T;t++) th.emplace_back(worker,t);
    for(auto&x:th) x.join();
    return *min_element(best.begin(),best.end());
}

int main(int argc,char**argv){
    if(argc<3){ fprintf(stderr,"usage: %s exact|exactw|heur|both FILE [iters]\n",argv[0]); return 1; }
    string mode=argv[1];
    readfile(argv[2]);
    ll Wtot=0; for(int i=0;i<N;i++) Wtot+=W[i];
    if(mode=="exact"){
        if(N>40){ fprintf(stderr,"n too large for exact\n"); return 1; }
        ll b=exact_unweighted();
        printf("n= %d m= %d bip= %lld Wtot= %lld 25bip= %lld Wtot2= %lld CE= %d\n",
               N,M,b,Wtot,25*b,Wtot*Wtot,(25*b>Wtot*Wtot)?1:0);
    } else if(mode=="exactw"){
        if(N>34){ fprintf(stderr,"n too large\n"); return 1; }
        ll b=exact_weighted();
        printf("n= %d m= %d bip= %lld Wtot= %lld 25bip= %lld Wtot2= %lld CE= %d\n",
               N,M,b,Wtot,25*b,Wtot*Wtot,(25*b>Wtot*Wtot)?1:0);
    } else if(mode=="heur"){
        long it = (argc>3)? atol(argv[3]) : 2000000L;
        ll b=heuristic(it, 1u);
        printf("n= %d m= %d bipUB= %lld Wtot= %lld 25bipUB= %lld Wtot2= %lld SURVIVES= %d\n",
               N,M,b,Wtot,25*b,Wtot*Wtot,(25*b>Wtot*Wtot)?1:0);
    } else { fprintf(stderr,"bad mode\n"); return 1; }
    return 0;
}
