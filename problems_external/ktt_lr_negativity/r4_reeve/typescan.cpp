// typescan.cpp -- enumerate the COMBINATORIAL TYPES (chambers) of the r=4 hive
// polytope over the 9-dimensional gap moduli space, and emit exact samples of
// (gap vector, 6*a1) per type.
//
// WHY.  For a FIXED normal fan Sigma the polytopes Q_b are the lattice points of
// the type cone; Q_b is a Cartier divisor D_b on the toric variety X_Sigma and
// Riemann-Roch gives  a_1(b) = integral over X of D_b . Td_2(X_Sigma),  which is
// LINEAR in b -- hence linear in the gap vector g.  So on each chamber
//      6*a_1(g) = w . g        for a fixed rational vector w.
// If every chamber has w >= 0 componentwise then, because the realisable gap
// vectors form a subcone of the nonnegative orthant, a_1 >= 0 for ALL r=4 hive
// polytopes and the King-Tollu-Toumazet conjecture holds in the r=4 cell.
// This program produces the data; fit_types.py does the exact fit and the sign test.
//
// The combinatorial type is recorded as the sorted multiset of 18-bit tight-row
// masks of the vertices of Q (a complete invariant of the face lattice together
// with which rows support which face).
//
// Build: g++ -O3 -o typescan typescan.cpp
// Usage: typescan GMAX STEP        (walks every STEP-th realisable gap vector)
//        typescan --rand KMAX N SEED

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <algorithm>

typedef long long ll;

struct RowXYZ { int p, q, r; ll rhs; };

static int build_rows_xyz(const ll lam[4], const ll mu[4], const ll nu[4], RowXYZ out[24]) {
    ll B[5][5];
    for (int i = 0; i < 5; i++) for (int j = 0; j < 5; j++) B[i][j] = 0;
    ll sl = lam[0] + lam[1] + lam[2] + lam[3];
    ll acc = 0; for (int y = 0; y <= 4; y++) { B[0][y] = acc; if (y < 4) acc += lam[y]; }
    acc = 0; for (int x = 0; x <= 4; x++) { B[x][4 - x] = sl + acc; if (x < 4) acc += mu[x]; }
    acc = 0; for (int x = 0; x <= 4; x++) { B[x][0] = acc; if (x < 4) acc += nu[x]; }
    B[0][0] = 0;
    auto isInt = [](int x, int y) { return (x == 1 && y == 1) || (x == 1 && y == 2) || (x == 2 && y == 1); };
    auto idx = [](int x, int y) { return (x == 1 && y == 1) ? 0 : (x == 1 && y == 2) ? 1 : 2; };
    int nr = 0; bool infeasible = false;
    auto add = [&](int px[2], int py[2], int mx[2], int my[2]) {
        ll co[3] = {0, 0, 0}; ll cst = 0;
        for (int t = 0; t < 2; t++) {
            if (isInt(px[t], py[t])) co[idx(px[t], py[t])] -= 1; else cst -= B[px[t]][py[t]];
            if (isInt(mx[t], my[t])) co[idx(mx[t], my[t])] += 1; else cst += B[mx[t]][my[t]];
        }
        if (!co[0] && !co[1] && !co[2]) { if (cst > 0) infeasible = true; return; }
        out[nr].p = (int)co[0]; out[nr].q = (int)co[1]; out[nr].r = (int)co[2]; out[nr].rhs = -cst; nr++;
    };
    for (int x = 0; x <= 4; x++) for (int y = 0; y <= 4; y++) {
        if (x + y <= 2) { int px[2] = {x + 1, x}, py[2] = {y, y + 1}, mx[2] = {x, x + 1}, my[2] = {y, y + 1}; add(px, py, mx, my); }
        if (y >= 1 && x + y <= 3) { int px[2] = {x, x + 1}, py[2] = {y, y}, mx[2] = {x, x + 1}, my[2] = {y + 1, y - 1}; add(px, py, mx, my); }
        if (x >= 1 && x + y <= 3) { int px[2] = {x, x}, py[2] = {y, y + 1}, mx[2] = {x + 1, x - 1}, my[2] = {y, y + 1}; add(px, py, mx, my); }
    }
    return infeasible ? -1 : nr;
}

static ll det3(ll a, ll b, ll c, ll d, ll e, ll f, ll g, ll h, ll i) {
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
}

// L(n) via integer fibres over (u,v) with (x,u,v) = (h11, h12-h11, h21-h11)
static ll lattice_count(const RowXYZ *R, int nr, ll n, ll ulo, ll uhi, ll vlo, ll vhi) {
    ll total = 0;
    for (ll u = n * ulo; u <= n * uhi; u++)
        for (ll v = n * vlo; v <= n * vhi; v++) {
            ll lo = -(1LL << 60), hi = (1LL << 60); bool ok = true;
            for (int k = 0; k < nr; k++) {
                int s = R[k].p + R[k].q + R[k].r;
                ll rem = n * R[k].rhs - (ll)R[k].q * u - (ll)R[k].r * v;
                if (s == 0) { if (rem < 0) { ok = false; break; } }
                else if (s > 0) { if (rem < hi) hi = rem; }
                else { if (-rem > lo) lo = -rem; }
                if (lo > hi) { ok = false; break; }
            }
            if (ok && hi >= lo) total += hi - lo + 1;
        }
    return total;
}

struct Out { bool ok; std::string sig; ll six_a1, V, L1; };

static Out eval(const int a[3], const int b[3], const int c[3]) {
    Out o; o.ok = false; o.six_a1 = o.V = o.L1 = 0;
    ll Aw = 3LL * a[2] + 2LL * a[1] + a[0], Bw = 3LL * b[2] + 2LL * b[1] + b[0], Cw = 3LL * c[2] + 2LL * c[1] + c[0];
    ll D = Cw - Aw - Bw;
    if (((D % 4) + 4) % 4 != 0) return o;
    ll k = D / 4, l4 = 0, m4 = 0, n4 = 0;
    if (k >= 0) l4 = k; else n4 = -k;
    ll lam[4] = {l4 + a[2] + a[1] + a[0], l4 + a[2] + a[1], l4 + a[2], l4};
    ll mu[4] = {m4 + b[2] + b[1] + b[0], m4 + b[2] + b[1], m4 + b[2], m4};
    ll nu[4] = {n4 + c[2] + c[1] + c[0], n4 + c[2] + c[1], n4 + c[2], n4};
    RowXYZ R[24]; int nr = build_rows_xyz(lam, mu, nu, R);
    if (nr < 0) return o;
    // exact vertex enumeration: every 3-subset, integer Cramer, exact feasibility
    std::map<std::vector<ll>, int> verts;   // (num0,num1,num2,den) -> mask
    for (int i = 0; i < nr; i++) for (int j = i + 1; j < nr; j++) for (int l = j + 1; l < nr; l++) {
        ll M[3][3] = {{R[i].p, R[i].q, R[i].r}, {R[j].p, R[j].q, R[j].r}, {R[l].p, R[l].q, R[l].r}};
        ll Dt = det3(M[0][0], M[0][1], M[0][2], M[1][0], M[1][1], M[1][2], M[2][0], M[2][1], M[2][2]);
        if (!Dt) continue;
        ll bb[3] = {R[i].rhs, R[j].rhs, R[l].rhs};
        ll num[3];
        for (int cix = 0; cix < 3; cix++) {
            ll N[3][3];
            for (int rr = 0; rr < 3; rr++) for (int cc = 0; cc < 3; cc++) N[rr][cc] = (cc == cix) ? bb[rr] : M[rr][cc];
            num[cix] = det3(N[0][0], N[0][1], N[0][2], N[1][0], N[1][1], N[1][2], N[2][0], N[2][1], N[2][2]);
        }
        ll den = Dt;
        if (den < 0) { den = -den; for (int t = 0; t < 3; t++) num[t] = -num[t]; }
        bool feas = true; int mask = 0;
        for (int t = 0; t < nr; t++) {
            ll lhs = (ll)R[t].p * num[0] + (ll)R[t].q * num[1] + (ll)R[t].r * num[2];
            ll rr = R[t].rhs * den;
            if (lhs > rr) { feas = false; break; }
            if (lhs == rr) mask |= (1 << t);
        }
        if (!feas) continue;
        std::vector<ll> key(4); key[0] = num[0]; key[1] = num[1]; key[2] = num[2]; key[3] = den;
        // normalise the fraction representation
        ll gg = den; for (int t = 0; t < 3; t++) { ll x = key[t] < 0 ? -key[t] : key[t]; while (x) { ll z = gg % x; gg = x; x = z; } }
        if (gg > 1) { for (int t = 0; t < 4; t++) key[t] /= gg; }
        verts[key] = mask;
    }
    if (verts.size() < 4) return o;
    std::vector<int> masks;
    for (std::map<std::vector<ll>, int>::iterator it = verts.begin(); it != verts.end(); ++it) masks.push_back(it->second);
    std::sort(masks.begin(), masks.end());
    char buf[32]; std::string sig;
    for (size_t t = 0; t < masks.size(); t++) { snprintf(buf, sizeof(buf), "%x.", masks[t]); sig += buf; }
    ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
    if (ulo > uhi || vlo > vhi) return o;
    ll L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
    if (L1 == 0) return o;
    ll L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
    ll L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
    o.six_a1 = -11 + 18 * L1 - 9 * L2 + 2 * L3;
    o.V = L3 - 3 * L2 + 3 * L1 - 1;
    if (o.V <= 0) return o;           // dim < 3
    o.L1 = L1; o.sig = sig; o.ok = true;
    return o;
}

struct Bucket { ll count; std::vector<std::vector<ll> > samples; };  // sample = g[9] + six_a1

int main(int argc, char **argv) {
    std::map<std::string, Bucket> types;
    const size_t MAXS = 40;
    ll examined = 0;
    if (argc > 1 && !strcmp(argv[1], "--rand")) {
        ll K = atoll(argv[2]), N = atoll(argv[3]);
        unsigned long long st = (argc > 4) ? strtoull(argv[4], 0, 10) : 999ULL;
        for (ll it = 0; it < N; it++) {
            int g[9];
            for (int i = 0; i < 9; i++) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; g[i] = (int)(st % (unsigned long long)(K + 1)); }
            Out o = eval(g, g + 3, g + 6);
            if (!o.ok) continue;
            examined++;
            Bucket &B = types[o.sig]; B.count++;
            if (B.samples.size() < MAXS) { std::vector<ll> s(10); for (int i = 0; i < 9; i++) s[i] = g[i]; s[9] = o.six_a1; B.samples.push_back(s); }
        }
    } else {
        int G = atoi(argv[1]); ll STEP = (argc > 2) ? atoll(argv[2]) : 1;
        ll W = G + 1, TOT = 1; for (int i = 0; i < 9; i++) TOT *= W;
        for (ll code = 0; code < TOT; code += STEP) {
            int g[9]; ll t = code;
            for (int i = 0; i < 9; i++) { g[i] = (int)(t % W); t /= W; }
            Out o = eval(g, g + 3, g + 6);
            if (!o.ok) continue;
            examined++;
            Bucket &B = types[o.sig]; B.count++;
            if (B.samples.size() < MAXS) { std::vector<ll> s(10); for (int i = 0; i < 9; i++) s[i] = g[i]; s[9] = o.six_a1; B.samples.push_back(s); }
        }
    }
    fprintf(stderr, "dim-3 polytopes examined: %lld ; distinct combinatorial types: %zu\n", examined, types.size());
    for (std::map<std::string, Bucket>::iterator it = types.begin(); it != types.end(); ++it) {
        printf("TYPE %s %lld\n", it->first.c_str(), it->second.count);
        for (size_t s = 0; s < it->second.samples.size(); s++) {
            for (int i = 0; i < 9; i++) printf("%lld ", it->second.samples[s][i]);
            printf("| %lld\n", it->second.samples[s][9]);
        }
    }
    return 0;
}
