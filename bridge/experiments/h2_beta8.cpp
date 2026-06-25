// Search specifically for high-beta (>=7) triangle-free graphs with large min5drop,
// using simulated annealing that REWARDS min5drop while keeping beta in [7,9].
#include <bits/stdc++.h>
using namespace std;
static const int N=15;
int maxcut_active(const uint16_t adj[N],const int*verts,int k,int*me){
    static thread_local int ladj[N];int m=0;for(int i=0;i<k;i++)ladj[i]=0;
    for(int i=0;i<k;i++){int v=verts[i];uint16_t nb=adj[v];for(int j=i+1;j<k;j++){int w=verts[j];
        if((nb>>w)&1){ladj[i]|=(1<<j);ladj[j]|=(1<<i);m++;}}}
    *me=m;if(k==0)return 0;int full=(1<<k)-1,c=0,cut=0,best=0;long lim=1L<<k;
    for(long s=1;s<lim;s++){int i=__builtin_ctzl(s);int nb=ladj[i];int ci=(c>>i)&1;int same=ci?c:((~c)&full);
        cut+=__builtin_popcount(nb&same)-__builtin_popcount(nb&(~same&full));c^=(1<<i);if(cut>best)best=cut;}
    return best;}
int beta_active(const uint16_t adj[N],const int*v,int k){int me;int mc=maxcut_active(adj,v,k,&me);return me-mc;}
int min5drop(const uint16_t adj[N],int&bG){
    int allv[N];for(int i=0;i<N;i++)allv[i]=i;bG=beta_active(adj,allv,N);int best=INT_MAX;int rem[10];
    for(int a=0;a<N;a++)for(int b=a+1;b<N;b++)for(int c=b+1;c<N;c++)for(int d=c+1;d<N;d++)for(int e=d+1;e<N;e++){
        int idx=0;for(int v=0;v<N;v++){if(v==a||v==b||v==c||v==d||v==e)continue;rem[idx++]=v;}
        int dr=bG-beta_active(adj,rem,10);if(dr<best)best=dr;}
    return best;}
bool tf(const uint16_t adj[N]){for(int u=0;u<N;u++){uint16_t nu=adj[u];for(int v=u+1;v<N;v++)if((nu>>v)&1)if(adj[u]&adj[v])return false;}return true;}
mutex mtx;atomic<int>gbest{-1};atomic<long>hits{0};
void worker(int seed,long iters){
    mt19937_64 rng(seed);uint16_t adj[N];
    for(long it=0;it<iters;it++){
        // start from C5[3]
        for(int i=0;i<N;i++)adj[i]=0;
        for(int p=0;p<5;p++){int q=(p+1)%5;for(int a=0;a<3;a++)for(int b=0;b<3;b++){adj[3*p+a]|=(1<<(3*q+b));adj[3*q+b]|=(1<<(3*p+a));}}
        int bG;int md=min5drop(adj,bG);
        double Tm=2.0;
        for(int step=0;step<2000;step++){
            int u=rng()%N,v=rng()%N;if(u==v)continue;if(u>v)swap(u,v);
            uint16_t su=adj[u],sv=adj[v];bool pres=(adj[u]>>v)&1;
            if(pres){adj[u]&=~(1<<v);adj[v]&=~(1<<u);}else{if(adj[u]&adj[v])continue;adj[u]|=(1<<v);adj[v]|=(1<<u);}
            int b2;int md2=min5drop(adj,b2);
            auto fit=[&](int m_,int b_){if(b_<6)return -1000.0+b_;if(b_>9)return -500.0;return (double)(m_*10+b_);};
            double df=fit(md2,b2)-fit(md,bG);
            if(df>=0 || (exp(df/Tm) > (double)rng()/rng.max())){md=md2;bG=b2;}
            else {adj[u]=su;adj[v]=sv;}
            Tm*=0.999;
            if(bG>=6&&bG<=9&&md>gbest.load()){gbest=md;
                if(md>=6){hits++;lock_guard<mutex>lk(mtx);
                    fprintf(stderr,"ANNEALHIT beta=%d md=%d edges=",bG,md);
                    for(int x=0;x<N;x++)for(int y=x+1;y<N;y++)if((adj[x]>>y)&1)fprintf(stderr,"[%d,%d]",x,y);
                    fprintf(stderr,"\n");fflush(stderr);}
            }
        }
    }
}
int main(int argc,char**argv){int nt=argc>1?atoi(argv[1]):16;long it=argc>2?atol(argv[2]):50;
    vector<thread>T;for(int t=0;t<nt;t++)T.emplace_back(worker,777+t*20011,it);
    for(auto&x:T)x.join();printf("gbest=%d hits=%ld\n",gbest.load(),hits.load());return 0;}
