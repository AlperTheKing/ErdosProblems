// peel_anneal.cpp — simulated-annealing search to MAXIMIZE pc(G) over
// triangle-free graphs on N=5n vertices. Falsification test for per-graph (H2):
// if best pc found <= 2n-1, strong evidence no counterexample at this n.
// Compile: clang++ -O2 -std=c++17 -o peel_anneal.exe peel_anneal.cpp
#include <bits/stdc++.h>
using namespace std;

static int N, n_, incr;
typedef unsigned int u32;

// beta of induced subgraph given adjacency bitmasks and a vertex-set mask 'keep'
int beta_induced(const vector<u32>& adj, u32 keep){
    // collect kept vertices
    int idx[20], k=0;
    for(int v=0; v<N; v++) if(keep>>v&1) idx[k++]=v;
    if(k<=1) return 0;
    // local edges
    static int eu[200], ev_[200]; int m=0;
    for(int a=0;a<k;a++) for(int b=a+1;b<k;b++)
        if(adj[idx[a]]>>idx[b]&1){ eu[m]=a; ev_[m]=b; m++; }
    if(m==0) return 0;
    int best=INT_MAX, lim=1<<(k-1);
    for(int c=0;c<lim;c++){
        int col=c<<1, mono=0;
        for(int e=0;e<m;e++) if(((col>>eu[e])&1)==((col>>ev_[e])&1)) mono++;
        if(mono<best){best=mono; if(best==0) break;}
    }
    return best;
}

int beta_full(const vector<u32>& adj){ return beta_induced(adj,(N==32?~0u:((1u<<N)-1))); }

// pc(G) = beta(G) - max over 5-subsets S of beta(G-S)
int pc_graph(const vector<u32>& adj, int bG){
    u32 full = (N==32?~0u:((1u<<N)-1));
    int bestRemain=-1;
    int idx[20]; for(int i=0;i<N;i++) idx[i]=i;
    // enumerate 5-subsets to remove
    for(int a=0;a<N;a++)for(int b=a+1;b<N;b++)for(int c=b+1;c<N;c++)
     for(int d=c+1;d<N;d++)for(int e=d+1;e<N;e++){
        u32 keep = full & ~((1u<<a)|(1u<<b)|(1u<<c)|(1u<<d)|(1u<<e));
        int br=beta_induced(adj,keep);
        if(br>bestRemain){ bestRemain=br; if(bestRemain==bG) return 0; }
     }
    return bG-bestRemain;
}

bool triangle_free_after_add(const vector<u32>& adj,int u,int v){
    // adding edge u-v keeps triangle-free iff N(u)&N(v)==0
    return (adj[u]&adj[v])==0;
}

mt19937 rng(12345);

int main(int argc,char**argv){
    n_ = argc>1?atoi(argv[1]):3; N=5*n_; incr=2*n_-1;
    int steps = argc>2?atoi(argv[2]):200000;
    unsigned seed = argc>3?atoi(argv[3]):1;
    rng.seed(seed);
    // start from C5[n] blow-up (known pc=incr) to explore around it, plus random
    vector<u32> adj(N,0);
    // random triangle-free start: empty, then random adds
    auto recompute=[&](vector<u32>&a)->pair<int,int>{ int b=beta_full(a); return {b, pc_graph(a,b)}; };
    auto cur=recompute(adj); int bestpc=cur.second; vector<u32> bestadj=adj;
    double T=2.0;
    for(int s=0;s<steps;s++){
        T = 2.0*pow(0.99995, s);
        int u=rng()%N, v=rng()%N; if(u==v) continue;
        bool has = adj[u]>>v&1;
        vector<u32> trial=adj;
        if(has){ trial[u]&=~(1u<<v); trial[v]&=~(1u<<u); }
        else { if(!triangle_free_after_add(adj,u,v)) continue; trial[u]|=(1u<<v); trial[v]|=(1u<<u); }
        auto tr=recompute(trial);
        int d = tr.second - cur.second;
        if(d>=0 || (exp(d/T) > (double)(rng()%100000)/100000.0)){
            adj=trial; cur=tr;
            if(cur.second>bestpc){ bestpc=cur.second; bestadj=adj;
                if(bestpc>incr){ fprintf(stderr,"!!! pc=%d > incr=%d at step %d seed %u\n",bestpc,incr,s,seed); }
            }
        }
    }
    printf("seed=%u n=%d N=%d incr=%d  best_pc_found=%d  %s\n",seed,n_,N,incr,bestpc,
           bestpc>incr?"COUNTEREXAMPLE":"(<=incr, no refute)");
    return 0;
}
