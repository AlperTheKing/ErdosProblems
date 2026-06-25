// peel_test.cpp — test the per-graph Peeling Lemma (H2) on small n.
// Reads graph6 lines (triangle-free graphs on N=5n vertices) from stdin.
// For each G: beta(G) = min monochromatic edges over 2-colourings.
//             pc(G)   = min over 5-subsets S of ( beta(G) - beta(G-S) ).
// (H2) for this n asserts pc(G) <= 2n-1 for all G.
// Outputs: counts, max beta a(5n), distribution of pc over ALL graphs and
// over beta-extremal graphs, max pc + a witness g6.
#include <bits/stdc++.h>
using namespace std;

static int N;                 // vertices
static vector<int> adj;       // adjacency bitmask per vertex (N<=20)

// decode one graph6 string into adj[], return false on blank
bool decode_g6(const string& s){
    if(s.empty()) return false;
    int p=0; int n;
    int c0 = (unsigned char)s[p];
    if(c0==126){ // 63+something multi-byte; not expected for N<=62
        // 0x7e: 3 following bytes
        n = ((( (unsigned char)s[p+1]-63)<<12) | (((unsigned char)s[p+2]-63)<<6) | ((unsigned char)s[p+3]-63));
        p+=4;
    } else { n = c0-63; p+=1; }
    N=n; adj.assign(N,0);
    // bits: column-major upper triangle: for j=1..n-1, for i=0..j-1
    int bitpos=0; int cur=0; int curbits=0;
    auto nextbit=[&]()->int{
        if(curbits==0){ cur=(unsigned char)s[p++]-63; curbits=6; }
        int b=(cur>>5)&1; cur=(cur<<1)&63; curbits--; return b;
    };
    for(int j=1;j<N;j++) for(int i=0;i<j;i++){
        int b=nextbit();
        if(b){ adj[i]|=(1<<j); adj[j]|=(1<<i); }
    }
    (void)bitpos;
    return true;
}

// beta of induced subgraph on vertex set 'verts' (vector of original indices)
// brute force over 2^k colourings, fix vertex0 colour=0.
int beta_induced(const vector<int>& verts){
    int k=verts.size();
    if(k<=1) return 0;
    // build local edge list
    vector<pair<int,int>> E;
    for(int a=0;a<k;a++) for(int b=a+1;b<k;b++)
        if(adj[verts[a]]>>verts[b] & 1) E.push_back({a,b});
    if(E.empty()) return 0;
    int best=INT_MAX;
    int lim = 1<<(k-1); // fix vertex 0
    for(int c=0;c<lim;c++){
        int col=c<<1; // bit0 = vertex0 colour 0
        int mono=0;
        for(auto&e:E) if(((col>>e.first)&1)==((col>>e.second)&1)) mono++;
        best=min(best,mono);
        if(best==0) break;
    }
    return best;
}

int beta_full(){
    vector<int> all(N); iota(all.begin(),all.end(),0);
    return beta_induced(all);
}

int main(int argc,char**argv){
    int n = (argc>1)? atoi(argv[1]) : 2; // 5n = N expected
    int incr = 2*n-1;
    ios::sync_with_stdio(false);
    string line;
    long long total=0;
    int a5n=0;
    map<int,long long> pcDistAll, pcDistExtremal;
    int maxpc=INT_MIN; string maxpc_g6;
    long long fails=0; // pc > incr
    // first pass to get a5n we need beta of all; do single pass storing nothing,
    // but a5n needed to know extremal. We'll do two-pass via storing lines.
    vector<string> lines;
    while(getline(cin,line)){ if(!line.empty()) lines.push_back(line); }
    // pass1: compute beta, find a5n
    vector<int> betas(lines.size());
    for(size_t idx=0; idx<lines.size(); ++idx){
        decode_g6(lines[idx]);
        betas[idx]=beta_full();
        a5n=max(a5n,betas[idx]);
    }
    // pass2: pc
    for(size_t idx=0; idx<lines.size(); ++idx){
        decode_g6(lines[idx]);
        int b=betas[idx];
        // min over 5-subsets S of beta(G)-beta(G-S) = b - max_S beta(G-S)
        int bestRemain=-1; // max beta(G-S)
        // enumerate 5-subsets S => complement has N-5 vertices = the kept set
        vector<int> idxv(N); iota(idxv.begin(),idxv.end(),0);
        // choose 5 to REMOVE: iterate combinations
        vector<int> comb(5);
        // simple combination enumeration
        function<void(int,int)> rec=[&](int start,int depth){
            if(depth==5){
                // kept = all not in comb
                int rm=0; for(int x:comb) rm|=(1<<x);
                vector<int> kept;
                for(int v=0;v<N;v++) if(!(rm>>v&1)) kept.push_back(v);
                int br=beta_induced(kept);
                if(br>bestRemain) bestRemain=br;
                return;
            }
            for(int v=start; v<N; v++){ comb[depth]=v; rec(v+1,depth+1); }
        };
        rec(0,0);
        int pc = b - bestRemain;
        total++;
        pcDistAll[pc]++;
        if(b==a5n) pcDistExtremal[pc]++;
        if(pc>maxpc){ maxpc=pc; maxpc_g6=lines[idx]; }
        if(pc>incr) fails++;
    }
    cout<<"N="<<N<<" n="<<n<<" incr(2n-1)="<<incr<<"\n";
    cout<<"total graphs="<<total<<"\n";
    cout<<"a(5n)=max beta="<<a5n<<"\n";
    cout<<"max pc over all graphs="<<maxpc<<"  (H2 needs pc<="<<incr<<")\n";
    cout<<"# graphs with pc>incr (per-graph H2 FAILURES)="<<fails<<"\n";
    cout<<"witness g6 of max pc: "<<maxpc_g6<<"\n";
    cout<<"pc distribution (ALL): ";
    for(auto&kv:pcDistAll) cout<<kv.first<<":"<<kv.second<<" ";
    cout<<"\npc distribution (beta-extremal, beta="<<a5n<<"): ";
    for(auto&kv:pcDistExtremal) cout<<kv.first<<":"<<kv.second<<" ";
    cout<<"\n";
    return 0;
}
