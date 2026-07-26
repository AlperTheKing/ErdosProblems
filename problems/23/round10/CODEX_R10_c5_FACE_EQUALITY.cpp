// Exact collector for Gamma_11 arc-bound equality rays.
//
// For q divisible by 5, enumerate all nonnegative integer x with sum x=q and
//
//     min_S q_S(x) = q^2/25,
//
// up to D22 and positive integer scaling.  Only primitive vectors (gcd=1)
// are retained.  The search uses the same exact branch upper bound as the
// independently audited strict-falsifier search.  It does not solve an SDP.
//
// Positive ARCBOUND forces the support to contain an induced C5.  The 33
// induced C5s have three D22 orbits, so it is enough to search vectors
// positive on one of three fixed representative C5s.  Results from overlapping
// representatives are canonicalized and deduplicated.
//
// Build:
//   clang++ -O3 -march=native -std=c++17 CODEX_R10_c5_FACE_EQUALITY.cpp \
//       -o CODEX_R10_c5_FACE_EQUALITY.exe
//
// Usage:
//   CODEX_R10_c5_FACE_EQUALITY.exe 5 50 32

#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <mutex>
#include <numeric>
#include <set>
#include <thread>
#include <vector>

using std::array;
using std::set;
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
    for (int start = 0; start < N; ++start) {
        for (int length = 0; length <= N; ++length) {
            array<unsigned char, N> side{};
            for (int offset = 0; offset < length; ++offset) {
                side[(start + offset) % N] = 1;
            }
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
    std::sort(unique.begin(), unique.end());
    ArcData output;
    output.count = static_cast<int>(unique.size());
    if (output.count != MAX_ARCS) {
        std::fprintf(stderr, "expected 56 arc forms, got %d\n", output.count);
        std::exit(3);
    }
    for (int arc = 0; arc < output.count; ++arc) {
        for (int u = 0; u < N; ++u) {
            for (int v = 0; v < N; ++v) {
                output.mono[arc][u][v] = unique[arc][u * N + v];
            }
        }
    }
    return output;
}

const array<array<int, 5>, 3> C5_REPS{{
    {{0, 1, 4, 5, 8}},
    {{0, 1, 4, 6, 8}},
    {{0, 2, 4, 6, 8}},
}};

array<int, N> canonical_d22(const array<int, N>& x) {
    array<int, N> best{};
    best.fill(std::numeric_limits<int>::max());
    for (int sign : {1, -1}) {
        for (int shift = 0; shift < N; ++shift) {
            array<int, N> image{};
            for (int vertex = 0; vertex < N; ++vertex) {
                const int target = (sign * vertex + shift + 2 * N) % N;
                image[target] = x[vertex];
            }
            if (image < best) best = image;
        }
    }
    return best;
}

int vector_gcd(const array<int, N>& x) {
    int result = 0;
    for (int value : x) result = std::gcd(result, value);
    return result;
}

struct Task {
    int representative = 0;
    int first = 0;
    int second = 0;
};

struct Shared {
    const ArcData* arcs = nullptr;
    int q = 0;
    int target = 0;
    std::atomic<bool> strict_violation{false};
    std::mutex equality_mutex;
    set<array<int, N>> primitive_orbits;
    std::atomic<std::uint64_t> nodes{0};
    std::atomic<std::uint64_t> pruned{0};
    std::atomic<std::uint64_t> leaves{0};
    std::atomic<std::uint64_t> equality_leaves{0};
};

struct State {
    Shared* shared = nullptr;
    array<int, N> order{};
    array<unsigned char, N> required{};
    array<int, N + 1> suffix_min{};
    array<int, N> x{};
    array<long long, MAX_ARCS> current{};
    array<array<long long, N>, MAX_ARCS> cross{};

    State(Shared* shared_value, int representative) : shared(shared_value) {
        required.fill(0);
        for (int vertex : C5_REPS[representative]) required[vertex] = 1;
        int at = 0;
        for (int vertex : C5_REPS[representative]) order[at++] = vertex;
        for (int vertex = 0; vertex < N; ++vertex) {
            if (!required[vertex]) order[at++] = vertex;
        }
        suffix_min[N] = 0;
        for (int depth = N - 1; depth >= 0; --depth) {
            suffix_min[depth] =
                suffix_min[depth + 1] + (required[order[depth]] ? 1 : 0);
        }
    }

    static long long floor_divide_two(long long value) {
        return value >= 0 ? value / 2 : -((-value + 1) / 2);
    }

    long long exact_future_upper(int arc, int depth, int remaining) {
        if (remaining == 0) return 0;
        const auto& data = *shared->arcs;
        long long best = 0;
        for (int d = depth; d < N; ++d) {
            const int vertex = order[d];
            best = std::max(
                best,
                static_cast<long long>(remaining) * cross[arc][vertex]);
        }
        for (int left_depth = depth; left_depth < N; ++left_depth) {
            const int u = order[left_depth];
            for (int right_depth = left_depth + 1; right_depth < N;
                 ++right_depth) {
                const int v = order[right_depth];
                if (!data.mono[arc][u][v]) continue;
                const long long center_numerator =
                    static_cast<long long>(remaining) + cross[arc][u]
                    - cross[arc][v];
                const long long center =
                    floor_divide_two(center_numerator);
                const long long candidates[4] = {
                    0, remaining, center, center + 1
                };
                for (long long mass_u : candidates) {
                    mass_u =
                        std::max(0LL, std::min<long long>(remaining, mass_u));
                    const long long mass_v = remaining - mass_u;
                    const long long value =
                        cross[arc][u] * mass_u
                        + cross[arc][v] * mass_v
                        + mass_u * mass_v;
                    best = std::max(best, value);
                }
            }
        }
        return best;
    }

    bool upper_bound_prunes(int depth, int remaining) {
        for (int arc = 0; arc < shared->arcs->count; ++arc) {
            const long long upper =
                current[arc] + exact_future_upper(arc, depth, remaining);
            if (upper < shared->target) return true;
        }
        return false;
    }

    void assign(int depth, int value) {
        const int vertex = order[depth];
        x[vertex] = value;
        for (int arc = 0; arc < shared->arcs->count; ++arc) {
            current[arc] +=
                static_cast<long long>(value) * cross[arc][vertex];
            for (int future = depth + 1; future < N; ++future) {
                const int other = order[future];
                if (shared->arcs->mono[arc][vertex][other]) {
                    cross[arc][other] += value;
                }
            }
        }
    }

    void unassign(int depth, int value) {
        const int vertex = order[depth];
        for (int arc = 0; arc < shared->arcs->count; ++arc) {
            for (int future = depth + 1; future < N; ++future) {
                const int other = order[future];
                if (shared->arcs->mono[arc][vertex][other]) {
                    cross[arc][other] -= value;
                }
            }
            current[arc] -=
                static_cast<long long>(value) * cross[arc][vertex];
        }
        x[vertex] = 0;
    }

    void record_leaf() {
        long long minimum = std::numeric_limits<long long>::max();
        for (int arc = 0; arc < shared->arcs->count; ++arc) {
            minimum = std::min(minimum, current[arc]);
        }
        if (minimum > shared->target) {
            shared->strict_violation.store(true);
            return;
        }
        if (minimum != shared->target) return;
        shared->equality_leaves.fetch_add(1, std::memory_order_relaxed);
        if (vector_gcd(x) != 1) return;
        const array<int, N> canonical = canonical_d22(x);
        std::lock_guard<std::mutex> lock(shared->equality_mutex);
        shared->primitive_orbits.insert(canonical);
    }

    void dfs(int depth, int remaining) {
        shared->nodes.fetch_add(1, std::memory_order_relaxed);
        if (upper_bound_prunes(depth, remaining)) {
            shared->pruned.fetch_add(1, std::memory_order_relaxed);
            return;
        }
        if (depth == N) {
            if (remaining != 0) return;
            shared->leaves.fetch_add(1, std::memory_order_relaxed);
            record_leaf();
            return;
        }
        const int lower = required[order[depth]] ? 1 : 0;
        const int upper = remaining - suffix_min[depth + 1];
        if (upper < lower) return;
        const int pivot =
            std::max(lower, std::min(upper, shared->q / 5));
        for (int delta = 0; delta <= upper - lower; ++delta) {
            const int candidates[2] = {pivot + delta, pivot - delta};
            for (int which = 0; which < 2; ++which) {
                const int value = candidates[which];
                if (value < lower || value > upper) continue;
                if (delta == 0 && which == 1) continue;
                assign(depth, value);
                dfs(depth + 1, remaining - value);
                unassign(depth, value);
            }
        }
    }
};

void print_vector(const array<int, N>& x) {
    std::printf("[");
    for (int i = 0; i < N; ++i) {
        std::printf("%d%s", x[i], i + 1 == N ? "" : ",");
    }
    std::printf("]");
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 3) {
        std::fprintf(stderr, "usage: %s q_lo q_hi [threads]\n", argv[0]);
        return 2;
    }
    const int q_lo = std::atoi(argv[1]);
    const int q_hi = std::atoi(argv[2]);
    const int threads = argc >= 4 ? std::atoi(argv[3]) : 32;
    if (q_lo < 1 || q_hi < q_lo || threads < 1 || threads > 64) {
        std::fprintf(stderr, "invalid range or thread count; cap is 64\n");
        return 2;
    }
    if (argc >= 5 && std::freopen(argv[4], "wb", stdout) == nullptr) {
        std::fprintf(stderr, "cannot open output log %s\n", argv[4]);
        return 2;
    }

    const ArcData arcs = build_arcs();
    std::printf(
        "# EXACT_EQUALITY_COLLECTION Gamma_11 arcs=%d threads=%d "
        "D22_and_scaling_deduplicated=true\n",
        arcs.count, threads);

    set<array<int, N>> all_primitive_orbits;
    for (int q = q_lo; q <= q_hi; ++q) {
        if (q % 5 != 0) continue;
        Shared shared;
        shared.arcs = &arcs;
        shared.q = q;
        shared.target = q * q / 25;

        vector<Task> tasks;
        for (int representative = 0; representative < 3; ++representative) {
            State template_state(&shared, representative);
            const int max_first = q - template_state.suffix_min[1];
            for (int first = 1; first <= max_first; ++first) {
                const int remaining = q - first;
                const int max_second =
                    remaining - template_state.suffix_min[2];
                for (int second = 1; second <= max_second; ++second) {
                    tasks.push_back({representative, first, second});
                }
            }
        }

        std::atomic<std::size_t> next_task{0};
        vector<std::thread> pool;
        for (int thread_index = 0; thread_index < threads; ++thread_index) {
            pool.emplace_back([&]() {
                while (true) {
                    const std::size_t task_index = next_task.fetch_add(1);
                    if (task_index >= tasks.size()) break;
                    const Task task = tasks[task_index];
                    State state(&shared, task.representative);
                    state.assign(0, task.first);
                    state.assign(1, task.second);
                    state.dfs(2, q - task.first - task.second);
                }
            });
        }
        for (auto& thread : pool) thread.join();

        if (shared.strict_violation.load()) {
            std::fprintf(
                stderr,
                "STRICT_VIOLATION_ENCOUNTERED q=%d; collector aborts\n",
                q);
            return 4;
        }
        all_primitive_orbits.insert(
            shared.primitive_orbits.begin(), shared.primitive_orbits.end());
        std::printf(
            "Q_DONE q=%d target=%d primitive_orbits_at_q=%zu "
            "cumulative_orbits=%zu nodes=%llu pruned=%llu leaves=%llu "
            "equality_leaves=%llu\n",
            q,
            shared.target,
            shared.primitive_orbits.size(),
            all_primitive_orbits.size(),
            static_cast<unsigned long long>(shared.nodes.load()),
            static_cast<unsigned long long>(shared.pruned.load()),
            static_cast<unsigned long long>(shared.leaves.load()),
            static_cast<unsigned long long>(shared.equality_leaves.load()));
        std::fflush(stdout);
    }

    std::printf("BEGIN_PRIMITIVE_EQUALITY_ORBITS count=%zu\n",
                all_primitive_orbits.size());
    for (const auto& x : all_primitive_orbits) {
        const int q = std::accumulate(x.begin(), x.end(), 0);
        std::printf("EQ q=%d x=", q);
        print_vector(x);
        std::printf("\n");
    }
    std::printf("END_PRIMITIVE_EQUALITY_ORBITS\n");
    std::printf("EXACT_FINITE_COLLECTION_ONLY: no all-real theorem claim\n");
    return 0;
}
