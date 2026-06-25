// H2 red-team: search triangle-free graphs on N=15 for min5drop >= 6 (breaks H2 at n=3).
// beta(G) = e(G) - MaxCut(G). min5drop = min over 5-sets S of beta(G)-beta(G-S).
// Compile: clang++ -O3 -march=native -std=c++17 -pthread h2_redteam.cpp -o h2rt
#include <bits/stdc++.h>
using namespace std;

static const int N=15;

// adjacency as 16-bit masks
struct Graph { uint16_t adj[N]; int m; };

// MaxCut over an active vertex set given by a 15-bit mask, using adjacency masks.
// Brute over 2^k colorings via gray code on the active vertices.
// active vertices listed; returns maxcut and edge count among active.
int maxcut_active(const uint16_t adj[N], const int* verts, int k, int* medges_out){
    // local adjacency among the k active vertices
    static thread_local int ladj[N];
    int medges=0;
    for(int i=0;i<k;i++) ladj[i]=0;
    for(int i=0;i<k;i++){
        int v=verts[i];
        uint16_t nb=adj[v];
        for(int j=i+1;j<k;j++){
            int w=verts[j];
            if((nb>>w)&1){ ladj[i]|=(1<<j); ladj[j]|=(1<<i); medges++; }
        }
    }
    *medges_out=medges;
    if(k==0) return 0;
    int full=(1<<k)-1;
    int c=0, cut=0, best=0;
    long lim=1L<<k;
    for(long step=1; step<lim; step++){
        int i=__builtin_ctzl(step);
        int nb=ladj[i];
        int ci=(c>>i)&1;
        int same = ci? c : ((~c)&full);
        int same_nb = nb & same;
        int opp_nb = nb & (~same & full);
        cut += __builtin_popcount(same_nb) - __builtin_popcount(opp_nb);
        c ^= (1<<i);
        if(cut>best) best=cut;
    }
    return best;
}

int beta_active(const uint16_t adj[N], const int* verts, int k){
    int me; int mc=maxcut_active(adj,verts,k,&me); return me-mc;
}

bool triangle_free(const uint16_t adj[N]){
    for(int u=0;u<N;u++){
        uint16_t nu=adj[u];
        for(int v=u+1;v<N;v++) if((nu>>v)&1){
            if(adj[u]&adj[v]) return false;
        }
    }
    return true;
}

// returns min5drop and sets argmin; also returns betaG
int min5drop(const uint16_t adj[N], int& betaG, int argS[5]){
    int allv[N]; for(int i=0;i<N;i++) allv[i]=i;
    betaG=beta_active(adj,allv,N);
    int best=INT_MAX;
    int rem[10];
    for(int a=0;a<N;a++)for(int b=a+1;b<N;b++)for(int c=b+1;c<N;c++)
    for(int d=c+1;d<N;d++)for(int e=d+1;e<N;e++){
        // remaining 10 vertices
        int idx=0;
        for(int v=0;v<N;v++){ if(v==a||v==b||v==c||v==d||v==e) continue; rem[idx++]=v; }
        int bGS=beta_active(adj,rem,10);
        int drop=betaG-bGS;
        if(drop<best){ best=drop; argS[0]=a;argS[1]=b;argS[2]=c;argS[3]=d;argS[4]=e; }
    }
    return best;
}

// global best tracking
mutex mtx;
atomic<int> g_best_md{-1};
struct Hit { vector<pair<int,int>> edges; int beta, md; };
vector<Hit> g_hits;
int g_best_beta_for_md=-1;

void edges_of(const uint16_t adj[N], vector<pair<int,int>>& out){
    out.clear();
    for(int u=0;u<N;u++)for(int v=u+1;v<N;v++) if((adj[u]>>v)&1) out.push_back({u,v});
}

// random triangle-free graph builder
void random_tf(uint16_t adj[N], mt19937_64& rng, int target_m){
    for(int i=0;i<N;i++) adj[i]=0;
    vector<pair<int,int>> P;
    for(int i=0;i<N;i++)for(int j=i+1;j<N;j++) P.push_back({i,j});
    shuffle(P.begin(),P.end(),rng);
    int m=0;
    for(auto&pr:P){
        if(m>=target_m) break;
        int u=pr.first,v=pr.second;
        if((adj[u]&adj[v])==0){ adj[u]|=(1<<v); adj[v]|=(1<<u); m++; }
    }
}

void worker(int seed, long iters){
    mt19937_64 rng(seed);
    uint16_t adj[N];
    int argS[5];
    int local_best=-1;
    for(long it=0; it<iters; it++){
        int tm = 30 + (rng()% (46-30)); // 30..45
        random_tf(adj,rng,tm);
        // hill climb a bit: random add/remove keeping tf, accept if min5drop improves & beta in band
        int betaG; int md=min5drop(adj,betaG,argS);
        // local search
        for(int step=0; step<60; step++){
            // pick random move
            int u=rng()%N, v=rng()%N; if(u==v) continue; if(u>v) swap(u,v);
            uint16_t save_u=adj[u], save_v=adj[v];
            bool present=(adj[u]>>v)&1;
            if(present){ adj[u]&=~(1<<v); adj[v]&=~(1<<u); }
            else { if(adj[u]&adj[v]) continue; adj[u]|=(1<<v); adj[v]|=(1<<u); }
            int b2; int md2=min5drop(adj,b2,argS);
            bool inband2 = (b2>=6 && b2<=9);
            bool inband  = (betaG>=6 && betaG<=9);
            // fitness: prefer in-band, then higher md
            auto fitness=[&](int md_,int b_){ if(b_<6) return -1000+b_; if(b_>9) return -500; return md_*10+b_; };
            if(fitness(md2,b2)>=fitness(md,betaG)){
                md=md2; betaG=b2;
            } else {
                adj[u]=save_u; adj[v]=save_v; // revert
            }
        }
        if(betaG>=6 && betaG<=9){
            if(md>local_best) local_best=md;
            if(md>=6){
                lock_guard<mutex> lk(mtx);
                if((int)g_hits.size()<50){
                    Hit h; edges_of(adj,h.edges); h.beta=betaG; h.md=md;
                    g_hits.push_back(h);
                    fprintf(stderr,"HIT beta=%d md=%d\n",betaG,md); fflush(stderr);
                }
            }
            if(md>g_best_md.load()){
                lock_guard<mutex> lk(mtx);
                if(md>g_best_md.load()){ g_best_md=md; g_best_beta_for_md=betaG;
                    fprintf(stderr,"newbest md=%d beta=%d\n",md,betaG); fflush(stderr);
                }
            }
        }
    }
}

int main(int argc, char** argv){
    int nthreads = argc>1? atoi(argv[1]) : 16;
    long iters = argc>2? atol(argv[2]) : 2000;
    vector<thread> T;
    for(int t=0;t<nthreads;t++) T.emplace_back(worker, 1000+t*7919, iters);
    for(auto&th:T) th.join();
    printf("BEST_MD %d (beta %d)\n", g_best_md.load(), g_best_beta_for_md);
    printf("NUM_HITS %zu\n", g_hits.size());
    for(auto&h:g_hits){
        printf("HITGRAPH beta=%d md=%d edges=", h.beta, h.md);
        for(auto&e:h.edges) printf("[%d,%d]",e.first,e.second);
        printf("\n");
    }
    return 0;
}
