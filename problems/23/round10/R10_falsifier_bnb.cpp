// Exact strict-falsifier search for the R10 Gamma_11 arc-cut frontier.
//
// We seek an integer vector x >= 0, sum x = q, with
//
//       25 * ARCBOUND_Gamma_11(x) > q^2.
//
// For integer x this is equivalent to every one of the 56 distinct arc
// monochromatic forms being at least T=floor(q^2/25)+1.
//
// This is a proof-producing finite search, not a sampler.  Two exact reductions
// make it substantially smaller than raw composition enumeration.
//
// (1) If ARCBOUND(x)>0, supp(x) meets a monochromatic edge of every arc.
//     Direct enumeration of the 2^11 support masks shows that the inclusion-
//     minimal such supports are exactly the 33 induced C5s of Gamma_11.
//
// (2) Those 33 C5s have three D_22 orbits, represented by
//       {0,1,4,5,8}, {0,1,4,6,8}, {0,2,4,6,8}.
//     Hence it is enough to search three cases in which all five coordinates
//     of one representative are positive.
//
// At a partial assignment, for each arc form f we use the exact upper bound
//
//   f <= current + U(H,c,r),
//
// where r is the unassigned mass and c_j is the already-assigned
// monochromatic-neighbour mass seen by unassigned vertex j.  Here U is computed
// exactly.  For
//
//       F(y) = sum_j c_j y_j + sum_{uv in E(H)} y_u y_v,  sum y_j=r,
//
// the usual Motzkin--Straus compression remains valid with the linear term:
// if u,v are nonadjacent, F is affine while y_u+y_v is fixed, so all their
// mass may be moved to one endpoint without decreasing F.  Thus a maximizer is
// supported on a clique.  H is triangle-free, so only single vertices and
// edges need be checked.  The edge maximization is a one-variable integer
// concave quadratic.  If current+U is below T for one arc, the subtree is
// impossible.
//
// Build:
//   clang++ -O3 -march=native -std=c++17 R10_falsifier_bnb.cpp -o R10_falsifier_bnb.exe
//
// Usage:
//   R10_falsifier_bnb.exe q_lo q_hi [threads]
//
// The thread count is rejected if it exceeds the project cap of 64.

#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <mutex>
#include <thread>
#include <utility>
#include <vector>

using std::array;
using std::pair;
using std::vector;

namespace {

constexpr int N = 11;
constexpr int MAX_ARCS = 56;

struct ArcData {
    int count = 0;
    array<array<array<unsigned char, N>, N>, MAX_ARCS> mono{};
};

bool adjacent(int u, int v) {
    int d = std::abs(u - v);
    d = std::min(d, N - d);
    return 3 * d > N;
}

ArcData build_arcs() {
    vector<array<unsigned char, N * N>> unique;
    for (int s = 0; s < N; ++s) {
        for (int len = 0; len <= N; ++len) {
            array<unsigned char, N> side{};
            for (int t = 0; t < len; ++t) side[(s + t) % N] = 1;
            array<unsigned char, N * N> form{};
            for (int u = 0; u < N; ++u) {
                for (int v = u + 1; v < N; ++v) {
                    if (adjacent(u, v) && side[u] == side[v]) {
                        form[u * N + v] = form[v * N + u] = 1;
                    }
                }
            }
            if (std::find(unique.begin(), unique.end(), form) == unique.end()) {
                unique.push_back(form);
            }
        }
    }
    std::sort(unique.begin(), unique.end(),
              [](const auto& a, const auto& b) {
                  int ca = 0, cb = 0;
                  for (auto z : a) ca += z;
                  for (auto z : b) cb += z;
                  return ca < cb;
              });
    ArcData out;
    out.count = static_cast<int>(unique.size());
    if (out.count != MAX_ARCS) {
        std::fprintf(stderr, "internal error: expected 56 arcs, got %d\n", out.count);
        std::exit(3);
    }
    for (int a = 0; a < out.count; ++a) {
        for (int u = 0; u < N; ++u) {
            for (int v = 0; v < N; ++v) {
                out.mono[a][u][v] = unique[a][u * N + v];
            }
        }
    }
    return out;
}

const array<array<int, 5>, 3> C5_REPS{{
    {{0, 1, 4, 5, 8}},
    {{0, 1, 4, 6, 8}},
    {{0, 2, 4, 6, 8}},
}};

struct Task {
    int rep = 0;
    int first = 0;
    int second = 0;
};

struct Shared {
    const ArcData* arcs = nullptr;
    int q = 0;
    int target = 0;
    std::atomic<bool> found{false};
    std::mutex witness_mutex;
    array<int, N> witness{};
    std::atomic<std::uint64_t> nodes{0};
    std::atomic<std::uint64_t> pruned{0};
    std::atomic<std::uint64_t> leaves{0};
};

struct State {
    Shared* shared = nullptr;
    array<int, N> order{};
    array<int, N> position{};
    array<unsigned char, N> required{};
    array<int, N + 1> suffix_min{};
    array<int, N> x{};
    array<long long, MAX_ARCS> current{};
    array<array<long long, N>, MAX_ARCS> cross{};

    explicit State(Shared* s, int rep) : shared(s) {
        required.fill(0);
        for (int v : C5_REPS[rep]) required[v] = 1;

        int p = 0;
        for (int v : C5_REPS[rep]) order[p++] = v;
        for (int v = 0; v < N; ++v) {
            if (!required[v]) order[p++] = v;
        }
        for (int i = 0; i < N; ++i) position[order[i]] = i;
        suffix_min[N] = 0;
        for (int i = N - 1; i >= 0; --i) {
            suffix_min[i] = suffix_min[i + 1] + (required[order[i]] ? 1 : 0);
        }
    }

    static long long floor_div2(long long z) {
        return z >= 0 ? z / 2 : -((-z + 1) / 2);
    }

    long long exact_future_upper(int a, int depth, int rem) {
        const auto& A = *shared->arcs;
        if (rem == 0) return 0;
        long long best = 0;
        for (int d = depth; d < N; ++d) {
            const int v = order[d];
            best = std::max(best, static_cast<long long>(rem) * cross[a][v]);
        }
        for (int du = depth; du < N; ++du) {
            const int u = order[du];
            for (int dv = du + 1; dv < N; ++dv) {
                const int v = order[dv];
                if (!A.mono[a][u][v]) continue;
                const long long b = static_cast<long long>(rem) + cross[a][u] - cross[a][v];
                const long long center = floor_div2(b);
                const long long candidates[4] = {0, rem, center, center + 1};
                for (long long mass_u : candidates) {
                    mass_u = std::max(0LL, std::min(static_cast<long long>(rem), mass_u));
                    const long long mass_v = rem - mass_u;
                    const long long value = cross[a][u] * mass_u
                                          + cross[a][v] * mass_v
                                          + mass_u * mass_v;
                    best = std::max(best, value);
                }
            }
        }
        return best;
    }

    bool upper_bound_prunes(int depth, int rem) {
        const auto& A = *shared->arcs;
        for (int a = 0; a < A.count; ++a) {
            const long long ub = current[a] + exact_future_upper(a, depth, rem);
            if (ub < shared->target) return true;
        }
        return false;
    }

    void assign(int depth, int value) {
        const auto& A = *shared->arcs;
        const int v = order[depth];
        x[v] = value;
        for (int a = 0; a < A.count; ++a) {
            current[a] += static_cast<long long>(value) * cross[a][v];
            for (int d = depth + 1; d < N; ++d) {
                const int w = order[d];
                if (A.mono[a][v][w]) cross[a][w] += value;
            }
        }
    }

    void unassign(int depth, int value) {
        const auto& A = *shared->arcs;
        const int v = order[depth];
        for (int a = 0; a < A.count; ++a) {
            for (int d = depth + 1; d < N; ++d) {
                const int w = order[d];
                if (A.mono[a][v][w]) cross[a][w] -= value;
            }
            current[a] -= static_cast<long long>(value) * cross[a][v];
        }
        x[v] = 0;
    }

    void dfs(int depth, int rem) {
        if (shared->found.load(std::memory_order_relaxed)) return;
        shared->nodes.fetch_add(1, std::memory_order_relaxed);
        if (upper_bound_prunes(depth, rem)) {
            shared->pruned.fetch_add(1, std::memory_order_relaxed);
            return;
        }
        if (depth == N) {
            if (rem != 0) return;
            shared->leaves.fetch_add(1, std::memory_order_relaxed);
            for (int a = 0; a < shared->arcs->count; ++a) {
                if (current[a] < shared->target) return;
            }
            bool expected = false;
            if (shared->found.compare_exchange_strong(expected, true)) {
                std::lock_guard<std::mutex> lock(shared->witness_mutex);
                shared->witness = x;
            }
            return;
        }
        const int lo = required[order[depth]] ? 1 : 0;
        const int hi = rem - suffix_min[depth + 1];
        if (hi < lo) return;

        // Values near q/5 are tested first; this changes only discovery order.
        const int pivot = std::max(lo, std::min(hi, shared->q / 5));
        for (int delta = 0; delta <= hi - lo; ++delta) {
            const int candidates[2] = {pivot + delta, pivot - delta};
            for (int z = 0; z < 2; ++z) {
                const int value = candidates[z];
                if (value < lo || value > hi || (delta == 0 && z == 1)) continue;
                assign(depth, value);
                dfs(depth + 1, rem - value);
                unassign(depth, value);
                if (shared->found.load(std::memory_order_relaxed)) return;
            }
        }
    }
};

bool exact_check(const ArcData& arcs, const array<int, N>& x, int q, int target) {
    long long sum = 0;
    for (int z : x) {
        if (z < 0) return false;
        sum += z;
    }
    if (sum != q) return false;
    for (int a = 0; a < arcs.count; ++a) {
        long long f = 0;
        for (int u = 0; u < N; ++u) {
            for (int v = u + 1; v < N; ++v) {
                if (arcs.mono[a][u][v]) f += static_cast<long long>(x[u]) * x[v];
            }
        }
        if (f < target) return false;
    }
    return true;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 3) {
        std::fprintf(stderr, "usage: %s q_lo q_hi [threads]\n", argv[0]);
        return 2;
    }
    const int q_lo = std::atoi(argv[1]);
    const int q_hi = std::atoi(argv[2]);
    int threads = argc >= 4 ? std::atoi(argv[3]) : 16;
    if (q_lo < 1 || q_hi < q_lo || threads < 1 || threads > 64) {
        std::fprintf(stderr, "invalid range or thread count (cap is 64)\n");
        return 2;
    }

    const ArcData arcs = build_arcs();
    int degree = 0;
    for (int v = 1; v < N; ++v) degree += adjacent(0, v);
    std::printf("# Gamma_11 degree=%d distinct_arcs=%d C5_orbits=3 threads=%d\n",
                degree, arcs.count, threads);

    for (int q = q_lo; q <= q_hi; ++q) {
        Shared shared;
        shared.arcs = &arcs;
        shared.q = q;
        shared.target = static_cast<int>((static_cast<long long>(q) * q) / 25 + 1);

        vector<Task> tasks;
        for (int rep = 0; rep < 3; ++rep) {
            State template_state(&shared, rep);
            const int lo0 = 1;
            const int hi0 = q - template_state.suffix_min[1];
            for (int x0 = lo0; x0 <= hi0; ++x0) {
                const int rem1 = q - x0;
                const int lo1 = 1;
                const int hi1 = rem1 - template_state.suffix_min[2];
                for (int x1 = lo1; x1 <= hi1; ++x1) {
                    tasks.push_back({rep, x0, x1});
                }
            }
        }

        std::atomic<std::size_t> next{0};
        vector<std::thread> pool;
        for (int tid = 0; tid < threads; ++tid) {
            pool.emplace_back([&]() {
                while (!shared.found.load(std::memory_order_relaxed)) {
                    const std::size_t at = next.fetch_add(1);
                    if (at >= tasks.size()) break;
                    const Task task = tasks[at];
                    State state(&shared, task.rep);
                    state.assign(0, task.first);
                    state.assign(1, task.second);
                    state.dfs(2, q - task.first - task.second);
                }
            });
        }
        for (auto& t : pool) t.join();

        if (shared.found.load()) {
            const bool checked = exact_check(arcs, shared.witness, q, shared.target);
            std::printf("q=%d TARGET=%d RESULT=COUNTEREXAMPLE exact_check=%s x=[",
                        q, shared.target, checked ? "PASS" : "FAIL");
            for (int i = 0; i < N; ++i) {
                std::printf("%d%s", shared.witness[i], i + 1 == N ? "" : ",");
            }
            std::printf("] nodes=%llu pruned=%llu leaves=%llu\n",
                        static_cast<unsigned long long>(shared.nodes.load()),
                        static_cast<unsigned long long>(shared.pruned.load()),
                        static_cast<unsigned long long>(shared.leaves.load()));
            return checked ? 1 : 4;
        }

        std::printf("q=%d TARGET=%d RESULT=NO_STRICT_FALSIFIER nodes=%llu pruned=%llu leaves=%llu\n",
                    q, shared.target,
                    static_cast<unsigned long long>(shared.nodes.load()),
                    static_cast<unsigned long long>(shared.pruned.load()),
                    static_cast<unsigned long long>(shared.leaves.load()));
        std::fflush(stdout);
    }
    return 0;
}
