#include <bits/stdc++.h>
using namespace std;
static const int N=15;
int maxcut_active(const uint16_t adj[N], const int* verts, int k, int* medges_out){
    static thread_local int ladj[N]; int medges=0;
    for(int i=0;i<k;i++) ladj[i]=0;
    for(int i=0;i<k;i++){int v=verts[i];uint16_t nb=adj[v];
        for(int j=i+1;j<k;j++){int w=verts[j];if((nb>>w)&1){ladj[i]|=(1<<j);ladj[j]|=(1<<i);medges++;}}}
    *medges_out=medges; if(k==0)return 0;
    int full=(1<<k)-1,c=0,cut=0,best=0; long lim=1L<<k;
    for(long step=1;step<lim;step++){int i=__builtin_ctzl(step);int nb=ladj[i];int ci=(c>>i)&1;
        int same=ci?c:((~c)&full);int snb=nb&same;int onb=nb&(~same&full);
        cut+=__builtin_popcount(snb)-__builtin_popcount(onb);c^=(1<<i);if(cut>best)best=cut;}
    return best;}
int beta_active(const uint16_t adj[N],const int*v,int k){int me;int mc=maxcut_active(adj,v,k,&me);return me-mc;}
int main(){
    uint16_t adj[N]; for(int i=0;i<N;i++)adj[i]=0;
    // C5[3]: parts i = [3i,3i+3), connect consecutive
    auto add=[&](int u,int v){adj[u]|=(1<<v);adj[v]|=(1<<u);};
    for(int i=0;i<5;i++){int j=(i+1)%5;for(int a=0;a<3;a++)for(int b=0;b<3;b++)add(3*i+a,3*j+b);}
    int allv[N];for(int i=0;i<N;i++)allv[i]=i;
    printf("beta C5[3] = %d\n", beta_active(adj,allv,N));
    // transversal removal 0,3,6,9,12
    int rem[10];int idx=0;for(int v=0;v<N;v++){if(v==0||v==3||v==6||v==9||v==12)continue;rem[idx++]=v;}
    printf("beta(G-T) = %d  drop=%d\n", beta_active(adj,rem,10), beta_active(adj,allv,N)-beta_active(adj,rem,10));
    return 0;}
