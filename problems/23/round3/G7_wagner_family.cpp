// G7_wagner_family.cpp
// Exact test of a FIXED family C of cuts of Gamma_3 = C8({1,4}) (Wagner V8):
//     is   min_{S in C} Q_S(a)  <=  q^2/25   for every a >= 0 with sum a = q ?
// If yes for all q in a range, C is a candidate certificate family for
//     max_x psi(Gamma_3,x) <= 1/25            (BL2 of G7.md).
// If no, the witness a proves C is TOO SMALL (it does not refute anything).
// Exact int64 throughout.  usage:  G7_wagner_family <maxmono> <qmax>

#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cstdint>

static int EU[12], EV[12];
static int NE = 12;
static std::vector<std::vector<std::pair<int,int> > > FAM;

int main(int argc, char **argv) {
    int maxmono = (argc > 1) ? atoi(argv[1]) : 3;
    int qmax    = (argc > 2) ? atoi(argv[2]) : 40;
    int k = 0;
    for (int j = 0; j < 8; j++) { EU[k] = j; EV[k] = (j + 1) % 8; k++; }
    for (int j = 0; j < 4; j++) { EU[k] = j; EV[k] = j + 4; k++; }
    NE = k;
    for (int S = 0; S < (1 << 7); S++) {
        std::vector<std::pair<int,int> > M;
        for (int e = 0; e < NE; e++)
            if ((((S >> EU[e]) ^ (S >> EV[e])) & 1) == 0) M.push_back(std::make_pair(EU[e], EV[e]));
        if ((int)M.size() <= maxmono) FAM.push_back(M);
    }
    printf("family: cuts with at most %d monochromatic edges -> %d cuts\n", maxmono, (int)FAM.size());
    long long worstnum = 0, worstden = 1; int warg[8] = {0};
    for (int q = 1; q <= qmax; q++) {
        long long best = -1; int barg[8] = {0};
        int a[8];
        for (a[0] = 0; a[0] <= q; a[0]++)
        for (a[1] = 0; a[1] <= q - a[0]; a[1]++)
        for (a[2] = 0; a[2] <= q - a[0] - a[1]; a[2]++)
        for (a[3] = 0; a[3] <= q - a[0] - a[1] - a[2]; a[3]++)
        for (a[4] = 0; a[4] <= q - a[0] - a[1] - a[2] - a[3]; a[4]++)
        for (a[5] = 0; a[5] <= q - a[0] - a[1] - a[2] - a[3] - a[4]; a[5]++)
        for (a[6] = 0; a[6] <= q - a[0] - a[1] - a[2] - a[3] - a[4] - a[5]; a[6]++) {
            a[7] = q - a[0] - a[1] - a[2] - a[3] - a[4] - a[5] - a[6];
            long long mn = -1;
            for (size_t t = 0; t < FAM.size(); t++) {
                long long s = 0;
                for (size_t e = 0; e < FAM[t].size(); e++)
                    s += (long long)a[FAM[t][e].first] * a[FAM[t][e].second];
                if (mn < 0 || s < mn) { mn = s; if (best >= 0 && mn <= best) break; }
            }
            if (mn > best) { best = mn; for (int v = 0; v < 8; v++) barg[v] = a[v]; }
        }
        // compare best/q^2 with 1/25
        int bad = (25 * best > (long long)q * q);
        if (best * worstden > worstnum * ((long long)q * q)) {
            worstnum = best; worstden = (long long)q * q;
            for (int v = 0; v < 8; v++) warg[v] = barg[v];
        }
        printf("q=%3d  max_a min_C = %-8lld  25*max/q^2 = %.9f  %s  arg=",
               q, best, 25.0 * best / (double)(q * q), bad ? "FAMILY-TOO-SMALL" : "ok");
        for (int v = 0; v < 8; v++) printf("%d ", barg[v]);
        printf("\n");
        fflush(stdout);
    }
    printf("worst ratio 25*num/den = 25*%lld/%lld = %.9f  at a=",
           worstnum, worstden, 25.0 * worstnum / (double)worstden);
    for (int v = 0; v < 8; v++) printf("%d ", warg[v]);
    printf("\n");
    return 0;
}
