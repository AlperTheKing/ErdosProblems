// lr_hive.cpp — exact Littlewood-Richardson coefficients via the Knutson-Tao hive model.
//
// c(nu; lam, mu) = number of integer hives of side n = #parts(nu) with boundary:
//   coordinates (x,y), x>=0, y>=0, x+y<=n  (bottom-left corner (0,0)=0)
//   left  edge (0,y):   partial sums of lam  (0 at bottom-left, |lam| at top (0,n))
//   right edge (k,n-k): |lam| + partial sums of mu (top -> bottom-right (n,0)=|lam|+|mu|)
//   bottom edge (x,0):  partial sums of nu   (0 -> |nu| at (n,0))
// subject to the three rhombus inequalities (obtuse-corner sum >= acute-corner sum):
//   (A) h(x+1,y)+h(x,y+1) >= h(x,y)  +h(x+1,y+1)   for x,y>=0, x+y<=n-2
//   (B) h(x,y)  +h(x+1,y) >= h(x,y+1)+h(x+1,y-1)   for y>=1, x>=0, x+y<=n-1
//   (C) h(x,y)  +h(x,y+1) >= h(x+1,y)+h(x-1,y+1)   for x>=1, y>=0, x+y<=n-1
// Interior vertices: x>=1, y>=1, x+y<=n-1  — exactly (n-1)(n-2)/2 of them.
//
// Counting: DFS over interior vertices in bottom-up row-major order. Every rhombus
// inequality is imposed as an upper/lower bound on its last-assigned vertex; each
// interior vertex provably has at least one earlier-only LB and UB, so intervals are
// always finite. At the last vertex the interval length is added directly.
// All arithmetic is int64; counts are uint64 with an abort cap.
//
// CLI:  lr_hive.exe "lam" "mu" "nu" [cap]     -> one line: exact count | CAP_EXCEEDED | ERROR
//       lr_hive.exe --batch <file>            -> lines "lam;mu;nu;cap" -> one output line each
// Partitions: comma-separated weakly decreasing nonnegative integers; "0" or "" = empty.
// cap: count > cap  => CAP_EXCEEDED. Node-visit safety cap (env LR_HIVE_NODE_CAP,
// default 2e8) also reports CAP_EXCEEDED (triple too fat -> skip; never a math verdict).

#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
#include <iostream>
#include <algorithm>

using namespace std;
typedef long long ll;
typedef unsigned long long ull;

static const ull DEFAULT_CAP = 1000000000000ULL; // 1e12
static ull NODE_CAP = 200000000ULL;              // 2e8, env-overridable

struct Cst { int a, b, c; };                     // bound value = h[a]+h[b]-h[c]

struct Solver {
    int n = 0, K = 0;
    vector<ll> h;                                // flat (n+1)*(n+1), index x*(n+1)+y
    vector<int> vid;                             // interior flat ids, DFS order
    vector<vector<Cst>> lbs, ubs;                // per interior rank
    struct Pure { int p1, p2, m1, m2; };         // all-boundary rhombi: h[p1]+h[p2]>=h[m1]+h[m2]
    vector<Pure> pure;
    ull cap = DEFAULT_CAP, cnt = 0, nodes = 0;
    bool capHit = false;

    int id(int x, int y) const { return x * (n + 1) + y; }

    void addIneq(const vector<int>& rank, int p1, int p2, int m1, int m2) {
        int rp1 = rank[p1], rp2 = rank[p2], rm1 = rank[m1], rm2 = rank[m2];
        int mx = max(max(rp1, rp2), max(rm1, rm2));
        if (mx < 0) { pure.push_back({p1, p2, m1, m2}); return; }
        if (mx == rp1)      lbs[mx].push_back({m1, m2, p2});   // p1 >= m1+m2-p2
        else if (mx == rp2) lbs[mx].push_back({m1, m2, p1});
        else if (mx == rm1) ubs[mx].push_back({p1, p2, m2});   // m1 <= p1+p2-m2
        else                ubs[mx].push_back({p1, p2, m1});
    }

    // lam/mu/nu: zero-stripped partitions, sums already verified equal, n = nu.size() >= 1,
    // lam.size() <= n, mu.size() <= n.
    void build(const vector<ll>& lam, const vector<ll>& mu, const vector<ll>& nu) {
        n = (int)nu.size();
        h.assign((n + 1) * (n + 1), 0);
        // boundary
        ll s = 0;
        for (int y = 0; y <= n; ++y) {                    // left edge
            h[id(0, y)] = s = (y == 0 ? 0 : s + (y - 1 < (int)lam.size() ? lam[y - 1] : 0));
        }
        ll slam = h[id(0, n)];
        s = slam;
        for (int k = 0; k <= n; ++k) {                    // right edge (k, n-k)
            if (k > 0) s += (k - 1 < (int)mu.size() ? mu[k - 1] : 0);
            h[id(k, n - k)] = s;
        }
        s = 0;
        for (int x = 0; x <= n; ++x) {                    // bottom edge
            if (x > 0) s += nu[x - 1];
            h[id(x, 0)] = s;
        }
        // interior order + ranks
        vector<int> rank((n + 1) * (n + 1), -1);
        vid.clear();
        for (int y = 1; y <= n - 2; ++y)
            for (int x = 1; x + y <= n - 1; ++x) {
                rank[id(x, y)] = (int)vid.size();
                vid.push_back(id(x, y));
            }
        K = (int)vid.size();
        lbs.assign(K, {}); ubs.assign(K, {}); pure.clear();
        // rhombi
        for (int x = 0; x <= n; ++x)
            for (int y = 0; x + y <= n; ++y) {
                if (x + y <= n - 2)          // (A)
                    addIneq(rank, id(x + 1, y), id(x, y + 1), id(x, y), id(x + 1, y + 1));
                if (y >= 1 && x + y <= n - 1) // (B)
                    addIneq(rank, id(x, y), id(x + 1, y), id(x, y + 1), id(x + 1, y - 1));
                if (x >= 1 && x + y <= n - 1) // (C)
                    addIneq(rank, id(x, y), id(x, y + 1), id(x + 1, y), id(x - 1, y + 1));
            }
    }

    void dfs(int k) {
        if (++nodes > NODE_CAP) { capHit = true; return; }
        ll lo = LLONG_MIN / 4, hi = LLONG_MAX / 4;
        for (const Cst& c : lbs[k]) { ll t = h[c.a] + h[c.b] - h[c.c]; if (t > lo) lo = t; }
        for (const Cst& c : ubs[k]) { ll t = h[c.a] + h[c.b] - h[c.c]; if (t < hi) hi = t; }
        if (lo > hi) return;
        if (lo <= LLONG_MIN / 8 || hi >= LLONG_MAX / 8) { capHit = true; return; } // defensive
        int v = vid[k];
        if (k == K - 1) {
            cnt += (ull)(hi - lo + 1);
            if (cnt > cap) capHit = true;
            return;
        }
        for (ll val = lo; val <= hi; ++val) {
            h[v] = val;
            dfs(k + 1);
            if (capHit) return;
        }
    }

    // returns count; capHit flag signals CAP_EXCEEDED
    ull run() {
        cnt = 0; nodes = 0; capHit = false;
        for (const Pure& p : pure)
            if (h[p.p1] + h[p.p2] < h[p.m1] + h[p.m2]) return 0;
        if (K == 0) return 1;
        dfs(0);
        return cnt;
    }
};

// ---- parsing ----------------------------------------------------------------

static bool parsePartition(const string& s, vector<ll>& out) {
    out.clear();
    string t;
    for (char ch : s) if (!isspace((unsigned char)ch)) t += ch;
    if (t.empty()) return true;                       // empty partition
    size_t pos = 0;
    while (pos <= t.size()) {
        size_t nx = t.find(',', pos);
        string tok = t.substr(pos, nx == string::npos ? string::npos : nx - pos);
        if (tok.empty() || tok.size() > 12) return false;
        for (char ch : tok) if (!isdigit((unsigned char)ch)) return false;
        out.push_back(atoll(tok.c_str()));
        if (nx == string::npos) break;
        pos = nx + 1;
    }
    for (size_t i = 1; i < out.size(); ++i)
        if (out[i] > out[i - 1]) return false;        // must be weakly decreasing
    while (!out.empty() && out.back() == 0) out.pop_back();   // strip zeros
    if (out.size() > 400) return false;
    return true;
}

// result: "ERROR", "CAP_EXCEEDED", or decimal count
static string solveOne(const string& slam, const string& smu, const string& snu, ull cap) {
    vector<ll> lam, mu, nu;
    if (!parsePartition(slam, lam) || !parsePartition(smu, mu) || !parsePartition(snu, nu))
        return "ERROR";
    ll a = 0, b = 0, c = 0;
    for (ll v : lam) a += v;
    for (ll v : mu)  b += v;
    for (ll v : nu)  c += v;
    if (a + b != c) return "0";
    if ((int)lam.size() > (int)nu.size() || (int)mu.size() > (int)nu.size()) return "0";
    if (nu.empty()) return "1";                       // all empty
    Solver S;
    S.cap = cap;
    S.build(lam, mu, nu);
    ull r = S.run();
    if (S.capHit) return "CAP_EXCEEDED";
    char buf[32];
    snprintf(buf, sizeof buf, "%llu", r);
    return string(buf);
}

int main(int argc, char** argv) {
    if (const char* e = getenv("LR_HIVE_NODE_CAP")) {
        ull v = strtoull(e, nullptr, 10);
        if (v > 0) NODE_CAP = v;
    }
    if (argc >= 3 && strcmp(argv[1], "--batch") == 0) {
        ifstream f(argv[2]);
        if (!f) { fprintf(stderr, "cannot open %s\n", argv[2]); return 2; }
        string line;
        string outbuf;
        while (getline(f, line)) {
            while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
            if (line.empty() || line[0] == '#') continue;
            // split on ';'
            vector<string> parts;
            size_t pos = 0;
            while (pos <= line.size()) {
                size_t nx = line.find(';', pos);
                parts.push_back(line.substr(pos, nx == string::npos ? string::npos : nx - pos));
                if (nx == string::npos) break;
                pos = nx + 1;
            }
            if (parts.size() < 3) { outbuf += "ERROR\n"; continue; }
            ull cap = DEFAULT_CAP;
            if (parts.size() >= 4 && !parts[3].empty()) {
                ull v = strtoull(parts[3].c_str(), nullptr, 10);
                if (v > 0) cap = v;
            }
            outbuf += solveOne(parts[0], parts[1], parts[2], cap);
            outbuf += '\n';
            if (outbuf.size() > (1u << 20)) { fputs(outbuf.c_str(), stdout); outbuf.clear(); }
        }
        fputs(outbuf.c_str(), stdout);
        fflush(stdout);
        return 0;
    }
    if (argc == 4 || argc == 5) {
        ull cap = DEFAULT_CAP;
        if (argc == 5) {
            ull v = strtoull(argv[4], nullptr, 10);
            if (v > 0) cap = v;
        }
        string r = solveOne(argv[1], argv[2], argv[3], cap);
        printf("%s\n", r.c_str());
        return r == "ERROR" ? 2 : 0;
    }
    fprintf(stderr,
        "usage: lr_hive.exe \"lam\" \"mu\" \"nu\" [cap]\n"
        "       lr_hive.exe --batch <file>   (lines: lam;mu;nu;cap)\n");
    return 2;
}
