// EXACT lower bounds on max_x psi(H,x), via the blow-up identity, for the near-extremal patterns.
//
// By R1-C7, bip(H[a]) = min over cuts S of H of sum_{uv monochromatic} a_u a_v.  Hence for integer
// weights a with sum a = q,
//         psi(H, a/q)  =  bip(H[a]) / q^2,
// so  u_q(H) := max over such a of bip(H[a]) / q^2  is an EXACT rational lower bound on
// max_x psi(H,x), and u_q increases to it along multiples (Fekete, from a(tN) >= t^2 a(N)).
//
// This replaces hill-climbing with exact arithmetic and answers a sharp question: does the
// second-best pattern (the Wagner graph C8(1,4), lower bound 0.0387 from floating-point search)
// keep climbing toward 1/25 = 0.04, which would make it a second extremal object, or does it
// plateau strictly below?
//
// Usage: claude_blowup_sup.exe <pattern> <qmax>      pattern in {c5, wagner, petersen, grotzsch}

#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <string>
#include <functional>
#include <algorithm>

static long long gcdll(long long a, long long b) { while (b) { long long t = a % b; a = b; b = t; } return a; }

int main(int argc, char** argv) {
    std::string which = (argc > 1) ? argv[1] : "wagner";
    int qmax = (argc > 2) ? atoi(argv[2]) : 24;

    int n = 0;
    std::vector<std::pair<int,int>> E;
    if (which == "c5") {
        n = 5;
        for (int i = 0; i < 5; ++i) E.push_back({i, (i + 1) % 5});
    } else if (which == "wagner") {
        n = 8;
        for (int v = 0; v < 8; ++v) {
            int w = (v + 1) % 8; E.push_back({std::min(v,w), std::max(v,w)});
            w = (v + 4) % 8;     E.push_back({std::min(v,w), std::max(v,w)});
        }
    } else if (which == "petersen") {
        n = 10;
        for (int i = 0; i < 5; ++i) {
            E.push_back({i, (i + 1) % 5});
            E.push_back({i, 5 + i});
            int a = 5 + i, b = 5 + (i + 2) % 5;
            E.push_back({std::min(a,b), std::max(a,b)});
        }
    } else if (which == "grotzsch") {
        n = 11;
        for (int i = 0; i < 5; ++i) E.push_back({i, (i + 1) % 5});
        for (int i = 0; i < 5; ++i) {
            int a = 5 + i;
            int b1 = (i + 1) % 5, b2 = (i + 4) % 5;
            E.push_back({std::min(a,b1), std::max(a,b1)});
            E.push_back({std::min(a,b2), std::max(a,b2)});
            E.push_back({std::min(a,10), std::max(a,10)});
        }
    } else { std::fprintf(stderr, "unknown pattern\n"); return 2; }

    // dedupe edges
    std::vector<std::pair<int,int>> ded;
    for (auto& e : E) {
        bool dup = false;
        for (auto& f : ded) if (f == e) dup = true;
        if (!dup) ded.push_back(e);
    }
    E.swap(ded);

    // monochromatic edge lists per cut (vertex 0 fixed)
    std::vector<std::vector<std::pair<int,int>>> cuts;
    for (uint32_t m = 0; m < (1u << (n - 1)); ++m) {
        uint32_t S = (m << 1) | 1u;
        std::vector<std::pair<int,int>> mono;
        for (auto& e : E)
            if (((S >> e.first) & 1u) == ((S >> e.second) & 1u)) mono.push_back(e);
        cuts.push_back(mono);
    }

    std::printf("pattern=%s  n=%d  |E|=%zu  cuts=%zu\n", which.c_str(), n, E.size(), cuts.size());
    std::printf("%4s %14s %16s %14s\n", "q", "max bip(H[a])", "u_q = bip/q^2", "vs 1/25");

    std::vector<int> a(n, 0);
    double bestever = 0;
    for (int q = n; q <= qmax; ++q) {
        long long best = -1;
        std::vector<int> besta;
        // enumerate compositions of q into n positive parts
        std::vector<int> cur(n, 1);
        int rem0 = q - n;
        if (rem0 < 0) continue;
        // recursive enumeration
        std::vector<int> stack_pos;
        // iterative: simple recursion via lambda
        std::vector<int> parts(n, 1);
        std::function<void(int,int)> rec = [&](int idx, int rem) {
            if (idx == n - 1) {
                parts[idx] = 1 + rem;
                long long v = -1;
                for (auto& mono : cuts) {
                    long long s = 0;
                    for (auto& e : mono) s += (long long)parts[e.first] * parts[e.second];
                    if (v < 0 || s < v) v = s;
                    if (best >= 0 && v <= best) break;   // prune: cannot beat the record
                }
                if (v > best) { best = v; besta = parts; }
                return;
            }
            for (int k = 0; k <= rem; ++k) {
                parts[idx] = 1 + k;
                rec(idx + 1, rem - k);
            }
        };
        rec(0, rem0);
        double u = (double)best / ((double)q * q);
        if (u > bestever) bestever = u;
        char buf[64];
        long long g = gcdll(best, (long long)q * q);
        std::snprintf(buf, sizeof buf, "%lld/%lld", best / g, ((long long)q * q) / g);
        std::printf("%4d %14lld %16s %14.6f%s\n", q, best, buf, u,
                    (u > 0.04 + 1e-12) ? "   *** ABOVE 1/25 ***" : "");
        std::fflush(stdout);
    }
    std::printf("best u_q found: %.8f   (1/25 = 0.04000000)\n", bestever);
    return 0;
}

