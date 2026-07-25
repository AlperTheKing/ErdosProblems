/* f8_anneal.c -- simulated annealing over triangle-free graphs on n vertices,
   maximising a heuristic estimate of bip(G) (= m - maxcut).  The estimate is a
   multi-restart local search; it is an UPPER bound on bip, so any record found
   must be re-verified exactly with f8_bip.exe.
   Usage: f8_anneal.exe n steps restarts seed [outfile.g6]
   Prints the best graph found in graph6 plus its bip estimate.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

#define MAXN 64
static uint64_t rs;
static inline uint64_t xr(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static inline double ur(void){ return (double)(xr()>>11) * (1.0/9007199254740992.0); }

static int n;
static uint64_t adj[MAXN];
static int nb[MAXN][MAXN], deg[MAXN], m;

static void rebuild(void){
    m = 0;
    for (int i=0;i<n;i++){ deg[i]=0; }
    for (int i=0;i<n;i++)
        for (int j=0;j<n;j++) if (i!=j && ((adj[i]>>j)&1)) nb[i][deg[i]++]=j;
    for (int i=0;i<n;i++) m += deg[i];
    m/=2;
}

static int side[MAXN], cnt[MAXN];
static int bip_est(int restarts){
    int best = m;
    for (int r=0;r<restarts;r++){
        for (int i=0;i<n;i++) side[i]=(int)(xr()&1);
        for (int i=0;i<n;i++) cnt[i]=0;
        for (int i=0;i<n;i++) for (int k=0;k<deg[i];k++) if (side[nb[i][k]]) cnt[i]++;
        int mono=0;
        for (int i=0;i<n;i++) mono += side[i]?cnt[i]:deg[i]-cnt[i];
        mono/=2;
        int improved=1;
        while (improved){
            improved=0;
            for (int i=0;i<n;i++){
                int same = side[i]?cnt[i]:deg[i]-cnt[i];
                int gain = 2*same - deg[i];
                if (gain>0){
                    mono -= gain; side[i]^=1;
                    if (side[i]) for(int k=0;k<deg[i];k++) cnt[nb[i][k]]++;
                    else         for(int k=0;k<deg[i];k++) cnt[nb[i][k]]--;
                    improved=1;
                }
            }
        }
        if (mono<best) best=mono;
        if (best==0) break;
    }
    return best;
}

static void g6(char *out){
    int k=0;
    out[k++] = (char)(n+63);
    int bits=0, acc=0;
    for (int j=1;j<n;j++)
        for (int i=0;i<j;i++){
            acc = (acc<<1) | (int)((adj[i]>>j)&1);
            if (++bits==6){ out[k++]=(char)(acc+63); acc=0; bits=0; }
        }
    if (bits){ acc <<= (6-bits); out[k++]=(char)(acc+63); }
    out[k]=0;
}

int main(int argc,char**argv){
    if (argc<5){ fprintf(stderr,"usage: n steps restarts seed [out.g6]\n"); return 1; }
    n = atoi(argv[1]);
    long steps = atol(argv[2]);
    int restarts = atoi(argv[3]);
    rs = (uint64_t)atoll(argv[4]) * 2862933555777941757ULL + 3037000493ULL;
    for (int i=0;i<64;i++) xr();

    /* start from a random maximal triangle-free graph */
    for (int i=0;i<n;i++) adj[i]=0;
    int P = n*(n-1)/2, *pi = malloc(sizeof(int)*P), *pj = malloc(sizeof(int)*P), np=0;
    for (int i=0;i<n;i++) for (int j=i+1;j<n;j++){ pi[np]=i; pj[np]=j; np++; }
    for (int k=np-1;k>0;k--){ int t=(int)(xr()%(uint64_t)(k+1)); int a=pi[k];pi[k]=pi[t];pi[t]=a; a=pj[k];pj[k]=pj[t];pj[t]=a; }
    for (int k=0;k<np;k++){ int i=pi[k], j=pj[k]; if (!(adj[i]&adj[j])){ adj[i]|=1ull<<j; adj[j]|=1ull<<i; } }
    rebuild();
    int cur = bip_est(restarts);
    int best = cur;
    uint64_t bestadj[MAXN];
    memcpy(bestadj, adj, sizeof(adj));

    double T0 = 1.2, T1 = 0.02;
    for (long s=0;s<steps;s++){
        double T = T0 * pow(T1/T0, (double)s/(double)steps);
        int k = (int)(xr()%(uint64_t)np);
        int i = pi[k], j = pj[k];
        int isedge = (adj[i]>>j)&1;
        if (!isedge && (adj[i]&adj[j])) continue;         /* would create a triangle */
        if (isedge){ adj[i]&=~(1ull<<j); adj[j]&=~(1ull<<i); }
        else       { adj[i]|= (1ull<<j); adj[j]|= (1ull<<i); }
        rebuild();
        int v = bip_est(restarts);
        int d = v - cur;
        if (d >= 0 || ur() < exp((double)d / T)) {
            cur = v;
            if (v > best){ best=v; memcpy(bestadj,adj,sizeof(adj)); }
        } else {
            if (isedge){ adj[i]|=1ull<<j; adj[j]|=1ull<<i; }
            else       { adj[i]&=~(1ull<<j); adj[j]&=~(1ull<<i); }
            rebuild();
        }
    }
    memcpy(adj,bestadj,sizeof(adj));
    rebuild();
    char buf[8192]; g6(buf);
    printf("%s n=%d m=%d bipEST=%d ratio=%d/%d %.9f\n", buf, n, m, best, best, n*n,
           (double)best/((double)n*n));
    if (argc>5){ FILE*f=fopen(argv[5],"a"); fprintf(f,"%s\n",buf); fclose(f); }
    return 0;
}
