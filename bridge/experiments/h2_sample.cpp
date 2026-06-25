// Pure random-sample sampler: many triangle-free graphs, histogram of (beta,min5drop),
// report any with min5drop>=6 (in band beta in [6,9]). Threaded.
#include <bits/stdc++.h>
using namespace std;
static const int N=15;
int maxcut_active(const uint16_t adj[N], const int* verts, int k, int* me){
    static thread_local int ladj[N]; int m=0; for(int i=0;i<k;i++)ladj[i]=0;
    for(int i=0;i<k;i++){int v=verts[i];uint16_t nb=adj[v];for(int j=i+1;j<k;j++){int w=verts[j];
        if((nb>>w)&1){ladj[i]|=(1<<j);ladj[j]|=(1<<i);m++;}}}
    *me=m; if(k==0)return 0; int full=(1<<k)-1,c=0,cut=0,best=0; long lim=1L<<k;
    for(long s=1;s<lim;s++){int i=__builtin_ctzl(s);int nb=ladj[i];int ci=(c>>i)&1;int same=ci?c:((~c)&full);
        cut+=__builtin_popcount(nb&same)-__builtin_popcount(nb&(~same&full));c^=(1<<i);if(cut>best)best=cut;}
    return best;}
int beta_active(const uint16_t adj[N],const int*v,int k){int me;int mc=maxcut_active(adj,v,k,&me);return me-mc;}
int min5drop(const uint16_t adj[N],int&bG,int arg[5]){
    int allv[N];for(int i=0;i<N;i++)allv[i]=i; bG=beta_active(adj,allv,N); int best=INT_MAX;int rem[10];
    for(int a=0;a<N;a++)for(int b=a+1;b<N;b++)for(int c=b+1;c<N;c++)for(int d=c+1;d<N;d++)for(int e=d+1;e<N;e++){
        int idx=0;for(int v=0;v<N;v++){if(v==a||v==b||v==c||v==d||v==e)continue;rem[idx++]=v;}
        int dr=bG-beta_active(adj,rem,10); if(dr<best){best=dr;arg[0]=a;arg[1]=b;arg[2]=c;arg[3]=d;arg[4]=e;}}
    return best;}
void random_tf(uint16_t adj[N],mt19937_64&rng,int tm){
    for(int i=0;i<N;i++)adj[i]=0; static thread_local vector<pair<int,int>>P;
    if(P.empty())for(int i=0;i<N;i++)for(int j=i+1;j<N;j++)P.push_back({i,j});
    shuffle(P.begin(),P.end(),rng); int m=0;
    for(auto&pr:P){if(m>=tm)break;int u=pr.first,v=pr.second;if((adj[u]&adj[v])==0){adj[u]|=(1<<v);adj[v]|=(1<<u);m++;}}}
mutex mtx; atomic<long> hist[10][10]; atomic<int> gbest{-1}; atomic<long> hits6{0};
void worker(int seed,long iters){
    mt19937_64 rng(seed); uint16_t adj[N]; int arg[5];
    for(long it=0;it<iters;it++){
        int tm=20+rng()%26; // 20..45
        random_tf(adj,rng,tm); int bG; int md=min5drop(adj,bG,arg);
        if(bG>=0&&bG<10&&md>=0&&md<10) hist[bG][md]++;
        if(bG>=6&&bG<=9){ if(md>gbest.load())gbest=md;
            if(md>=6){hits6++; lock_guard<mutex>lk(mtx);
                fprintf(stderr,"SAMPLEHIT beta=%d md=%d edges=",bG,md);
                for(int u=0;u<N;u++)for(int v=u+1;v<N;v++)if((adj[u]>>v)&1)fprintf(stderr,"[%d,%d]",u,v);
                fprintf(stderr,"\n");fflush(stderr);} }
    }}
int main(int argc,char**argv){
    int nt=argc>1?atoi(argv[1]):16; long it=argc>2?atol(argv[2]):100000;
    for(int i=0;i<10;i++)for(int j=0;j<10;j++)hist[i][j]=0;
    vector<thread>T; for(int t=0;t<nt;t++)T.emplace_back(worker,12345+t*104729,it);
    for(auto&x:T)x.join();
    printf("gbest_md=%d hits6=%ld\n",gbest.load(),hits6.load());
    printf("histogram beta\md:\n     ");
    for(int j=0;j<10;j++)printf("%8d",j); printf("\n");
    for(int i=0;i<10;i++){printf("b=%d: ",i);for(int j=0;j<10;j++)printf("%8ld",hist[i][j].load());printf("\n");}
    return 0;}
