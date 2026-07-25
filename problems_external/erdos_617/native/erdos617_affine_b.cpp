#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <mutex>
#include <random>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace fs = std::filesystem;

static constexpr int N = 26;
static constexpr int OLD = 25;
static constexpr int COLORS = 5;

static int inv5(int x) {
    static constexpr int inv[5] = {0, 1, 3, 2, 4};
    return inv[x];
}

struct Clause {
    uint8_t color = 0;
    std::array<uint8_t, 15> vars{};
    uint8_t size = 0;
};

struct Model {
    std::array<std::array<int, N>, N> edge_index{};
    std::array<std::array<int, N>, N> var_index{};
    std::vector<std::pair<uint8_t, uint8_t>> edges;
    std::vector<std::pair<uint8_t, uint8_t>> vars;
    std::vector<uint8_t> fixed_colors;
    std::vector<Clause> clauses;
    std::vector<std::vector<uint16_t>> incidence;

    Model() {
        for (auto &r : edge_index) r.fill(-1);
        for (auto &r : var_index) r.fill(-1);
        for (int u = 0; u < N; ++u) {
            for (int v = u + 1; v < N; ++v) {
                int e = static_cast<int>(edges.size());
                edge_index[u][v] = edge_index[v][u] = e;
                edges.push_back({static_cast<uint8_t>(u), static_cast<uint8_t>(v)});
            }
        }
        fixed_colors.assign(edges.size(), 255);
        for (int e = 0; e < static_cast<int>(edges.size()); ++e) {
            int u = edges[e].first, v = edges[e].second;
            if (v == 25 || u % 5 == v % 5) {
                int z = static_cast<int>(vars.size());
                var_index[u][v] = var_index[v][u] = z;
                vars.push_back(edges[e]);
            } else {
                int dx = (v % 5 - u % 5 + 5) % 5;
                int dy = (v / 5 - u / 5 + 5) % 5;
                fixed_colors[e] = static_cast<uint8_t>((dy * inv5(dx)) % 5);
            }
        }
        if (vars.size() != 75) throw std::runtime_error("expected exactly 75 mutable edges");

        for (int a = 0; a < OLD - 4; ++a)
        for (int b = a + 1; b < OLD - 3; ++b)
        for (int c = b + 1; c < OLD - 2; ++c)
        for (int d = c + 1; d < OLD - 1; ++d)
        for (int e = d + 1; e < OLD; ++e) {
            std::array<int, 5> vv{a,b,c,d,e};
            uint8_t fixed_present = 0;
            std::array<uint8_t, 15> local_vars{};
            uint8_t nv = 0;
            for (int i = 0; i < 5; ++i) {
                local_vars[nv++] = static_cast<uint8_t>(var_index[vv[i]][25]);
                for (int j = i + 1; j < 5; ++j) {
                    int ge = edge_index[vv[i]][vv[j]];
                    if (fixed_colors[ge] != 255) {
                        fixed_present |= static_cast<uint8_t>(1u << fixed_colors[ge]);
                    } else {
                        local_vars[nv++] = static_cast<uint8_t>(var_index[vv[i]][vv[j]]);
                    }
                }
            }
            std::sort(local_vars.begin(), local_vars.begin() + nv);
            if (std::adjacent_find(local_vars.begin(), local_vars.begin() + nv) !=
                local_vars.begin() + nv) {
                throw std::runtime_error("duplicate variable in clause support");
            }
            for (int color = 0; color < COLORS; ++color) {
                if (fixed_present & (1u << color)) continue;
                Clause q;
                q.color = static_cast<uint8_t>(color);
                q.vars = local_vars;
                q.size = nv;
                clauses.push_back(q);
            }
        }
        if (clauses.size() != 15625) {
            throw std::runtime_error("expected exactly 15625 residual clauses, got " +
                                     std::to_string(clauses.size()));
        }
        incidence.resize(vars.size());
        for (int q = 0; q < static_cast<int>(clauses.size()); ++q) {
            for (int i = 0; i < clauses[q].size; ++i) {
                incidence[clauses[q].vars[i]].push_back(static_cast<uint16_t>(q));
            }
        }
    }

    std::vector<uint8_t> materialize(const std::vector<uint8_t> &assignment) const {
        if (assignment.size() != vars.size()) throw std::runtime_error("bad assignment length");
        std::vector<uint8_t> colors(edges.size());
        for (int e = 0; e < static_cast<int>(edges.size()); ++e) {
            if (fixed_colors[e] != 255) {
                colors[e] = fixed_colors[e];
            } else {
                auto [u,v] = edges[e];
                colors[e] = assignment[var_index[u][v]];
            }
        }
        return colors;
    }

    void write_raw(const std::vector<uint8_t> &assignment, const fs::path &path) const {
        auto colors = materialize(assignment);
        std::ofstream out(path);
        if (!out) throw std::runtime_error("cannot write " + path.string());
        for (int e = 0; e < static_cast<int>(edges.size()); ++e) {
            out << static_cast<int>(edges[e].first) << ' '
                << static_cast<int>(edges[e].second) << ' '
                << static_cast<int>(colors[e]) << '\n';
        }
    }
};

static int full_score(const Model &m, const std::vector<uint8_t> &assignment,
                      uint64_t *checked = nullptr) {
    auto colors = m.materialize(assignment);
    int score = 0;
    uint64_t count = 0;
    for (int a = 0; a < N - 5; ++a)
    for (int b = a + 1; b < N - 4; ++b)
    for (int c = b + 1; c < N - 3; ++c)
    for (int d = c + 1; d < N - 2; ++d)
    for (int e = d + 1; e < N - 1; ++e)
    for (int f = e + 1; f < N; ++f) {
        std::array<int, 6> vv{a,b,c,d,e,f};
        uint8_t present = 0;
        for (int i = 0; i < 6; ++i) {
            for (int j = i + 1; j < 6; ++j) {
                present |= static_cast<uint8_t>(1u << colors[m.edge_index[vv[i]][vv[j]]]);
            }
        }
        score += std::popcount(static_cast<unsigned>((~present) & 31u));
        ++count;
    }
    if (checked) *checked = count;
    return score;
}

struct State {
    std::vector<uint8_t> value;
    std::vector<uint8_t> sat_count;
    std::vector<int32_t> bad_pos;
    std::vector<uint16_t> bad;
    int score = 0;
};

static void add_bad(State &s, uint16_t q) {
    if (s.bad_pos[q] >= 0) return;
    s.bad_pos[q] = static_cast<int32_t>(s.bad.size());
    s.bad.push_back(q);
}

static void remove_bad(State &s, uint16_t q) {
    int p = s.bad_pos[q];
    if (p < 0) return;
    uint16_t last = s.bad.back();
    s.bad[p] = last;
    s.bad_pos[last] = p;
    s.bad.pop_back();
    s.bad_pos[q] = -1;
}

static void rebuild(const Model &m, State &s) {
    s.sat_count.assign(m.clauses.size(), 0);
    s.bad_pos.assign(m.clauses.size(), -1);
    s.bad.clear();
    s.score = 0;
    for (int q = 0; q < static_cast<int>(m.clauses.size()); ++q) {
        const Clause &cl = m.clauses[q];
        for (int i = 0; i < cl.size; ++i) {
            if (s.value[cl.vars[i]] == cl.color) ++s.sat_count[q];
        }
        if (s.sat_count[q] == 0) {
            ++s.score;
            add_bad(s, static_cast<uint16_t>(q));
        }
    }
}

static int delta(const Model &m, const State &s, int var, uint8_t target) {
    uint8_t old = s.value[var];
    if (old == target) return 0;
    int d = 0;
    for (uint16_t q : m.incidence[var]) {
        uint8_t c = m.clauses[q].color;
        if (c == old && s.sat_count[q] == 1) ++d;
        if (c == target && s.sat_count[q] == 0) --d;
    }
    return d;
}

static void apply_move(const Model &m, State &s, int var, uint8_t target) {
    uint8_t old = s.value[var];
    if (old == target) return;
    int d = 0;
    for (uint16_t q : m.incidence[var]) {
        uint8_t c = m.clauses[q].color;
        if (c == old) {
            if (s.sat_count[q] == 1) {
                ++d;
                add_bad(s, q);
            }
            --s.sat_count[q];
        }
        if (c == target) {
            if (s.sat_count[q] == 0) {
                --d;
                remove_bad(s, q);
            }
            ++s.sat_count[q];
        }
    }
    s.value[var] = target;
    s.score += d;
}

static int clause_score(const Model &m, const std::vector<uint8_t> &assignment) {
    State s;
    s.value = assignment;
    rebuild(m, s);
    return s.score;
}

static bool audit(const Model &m, std::string &error) {
    if (m.vars.size() != 75 || m.clauses.size() != 15625) {
        error = "model dimensions disagree";
        return false;
    }
    std::mt19937_64 rng(61775102ULL);
    for (int trial = 0; trial < 30; ++trial) {
        std::vector<uint8_t> a(75);
        for (uint8_t &x : a) x = static_cast<uint8_t>(rng() % 5);
        int reduced = clause_score(m, a);
        uint64_t checked = 0;
        int full = full_score(m, a, &checked);
        if (checked != 230230 || full != reduced) {
            error = "family/full mismatch at random trial " + std::to_string(trial);
            return false;
        }
    }
    State s;
    s.value.resize(75);
    for (uint8_t &x : s.value) x = static_cast<uint8_t>(rng() % 5);
    rebuild(m, s);
    for (int k = 0; k < 500; ++k) {
        int var = static_cast<int>(rng() % 75);
        uint8_t target;
        do { target = static_cast<uint8_t>(rng() % 5); } while (target == s.value[var]);
        int before = s.score;
        int predicted = delta(m, s, var, target);
        apply_move(m, s, var, target);
        int exact_reduced = clause_score(m, s.value);
        int exact_full = full_score(m, s.value);
        if (s.score != exact_reduced || exact_reduced != exact_full ||
            exact_reduced - before != predicted) {
            error = "incremental mismatch at audit move " + std::to_string(k);
            return false;
        }
    }
    return true;
}

static std::vector<uint8_t> initial_assignment(const Model &m, std::mt19937_64 &rng, int kind) {
    std::vector<uint8_t> a(75);
    int aa = static_cast<int>(rng() % 5), bb = static_cast<int>(rng() % 5);
    int cc = static_cast<int>(rng() % 5), dd = static_cast<int>(rng() % 5);
    for (int z = 0; z < 75; ++z) {
        int u = m.vars[z].first, v = m.vars[z].second;
        if (kind % 4 == 3) {
            a[z] = static_cast<uint8_t>(rng() % 5);
        } else if (v == 25) {
            int x = u % 5, y = u / 5;
            a[z] = static_cast<uint8_t>((aa*x + bb*y + cc) % 5);
        } else {
            int x = u % 5, y1 = u / 5, y2 = v / 5;
            a[z] = static_cast<uint8_t>((aa*x + bb*(y1+y2) + cc*y1*y2 + dd) % 5);
        }
        if (kind % 4 == 2 && (rng() % 7) == 0) a[z] = static_cast<uint8_t>(rng() % 5);
    }
    return a;
}

struct Shared {
    std::atomic<bool> stop{false};
    std::atomic<int> best{std::numeric_limits<int>::max()};
    std::atomic<uint64_t> moves{0};
    std::mutex mutex;
    fs::path out;
    std::chrono::steady_clock::time_point deadline;
};

static void publish(const Model &m, Shared &sh, const State &s, int worker, uint64_t moves) {
    int old = sh.best.load(std::memory_order_relaxed);
    while (s.score < old && !sh.best.compare_exchange_weak(old, s.score)) {}
    if (s.score <= sh.best.load()) {
        std::lock_guard<std::mutex> lock(sh.mutex);
        fs::create_directories(sh.out);
        m.write_raw(s.value, sh.out / "best_checkpoint.col");
        std::ofstream meta(sh.out / "best_checkpoint.txt");
        meta << "worker " << worker << "\nmoves " << moves << "\nscore " << s.score << "\n";
    }
}

static void worker(const Model &m, Shared &sh, int id, uint64_t seed) {
    std::mt19937_64 rng(seed + 0x9e3779b97f4a7c15ULL * static_cast<uint64_t>(id + 1));
    uint64_t moves = 0;
    int restart = 0;
    while (!sh.stop.load() && std::chrono::steady_clock::now() < sh.deadline) {
        State s;
        s.value = initial_assignment(m, rng, id * 11 + restart);
        rebuild(m, s);
        publish(m, sh, s, id, moves);
        int local_best = s.score;
        uint64_t last_improve = moves;
        std::array<uint64_t, 75> tabu{};
        while (!sh.stop.load() && std::chrono::steady_clock::now() < sh.deadline &&
               moves - last_improve < 200000) {
            if (s.score == 0) {
                int full = full_score(m, s.value);
                if (full != 0) throw std::runtime_error("zero reduced score disagrees with full verifier");
                {
                    std::lock_guard<std::mutex> lock(sh.mutex);
                    m.write_raw(s.value, sh.out / "verified_hit.col");
                    std::ofstream rep(sh.out / "verified_hit_affine_b.txt");
                    rep << "status VERIFIED_HIT\nworker " << id << "\nmoves " << moves
                        << "\nresidual_clauses 15625\nfull_sixsets 230230\nmissing_pairs 0\n";
                }
                sh.best.store(0);
                sh.stop.store(true);
                return;
            }
            uint16_t q = s.bad[rng() % s.bad.size()];
            const Clause &cl = m.clauses[q];
            int best_delta = std::numeric_limits<int>::max();
            int choices[15], nc = 0;
            for (int i = 0; i < cl.size; ++i) {
                int z = cl.vars[i];
                int d = delta(m, s, z, cl.color);
                if (tabu[z] > moves && s.score + d >= sh.best.load()) continue;
                if (d < best_delta) {
                    best_delta = d;
                    nc = 0;
                    choices[nc++] = z;
                } else if (d == best_delta) {
                    choices[nc++] = z;
                }
            }
            int z;
            if (nc == 0 || (rng() % 100) < 4) z = cl.vars[rng() % cl.size];
            else z = choices[rng() % nc];
            apply_move(m, s, z, cl.color);
            tabu[z] = moves + 3 + rng() % 19;
            ++moves;
            if (s.score < local_best) {
                local_best = s.score;
                last_improve = moves;
                publish(m, sh, s, id, moves);
            }
            if ((moves & 16383u) == 0) {
                int reduced = clause_score(m, s.value);
                int full = full_score(m, s.value);
                if (s.score != reduced || reduced != full) {
                    throw std::runtime_error("periodic score audit failed");
                }
                sh.moves.fetch_add(16384);
            }
            if (moves - last_improve > 25000 && moves % 512 == 0) {
                for (int k = 0; k < 2; ++k) {
                    int var = static_cast<int>(rng() % 75);
                    uint8_t target = static_cast<uint8_t>(rng() % 5);
                    if (target != s.value[var]) apply_move(m, s, var, target);
                }
            }
        }
        ++restart;
    }
    sh.moves.fetch_add(moves & 16383u);
}

static void usage() {
    std::cerr << "Usage:\n"
              << "  erdos617_affine_b --selftest\n"
              << "  erdos617_affine_b --search THREADS SECONDS SEED OUT_DIR\n";
}

int main(int argc, char **argv) {
    try {
        Model m;
        if (argc == 2 && std::string(argv[1]) == "--selftest") {
            std::string error;
            if (!audit(m, error)) {
                std::cerr << "SELFTEST FAIL " << error << "\n";
                return 1;
            }
            std::cout << "SELFTEST PASS\nmutable_edges 75\nresidual_clauses 15625\n"
                      << "random_family_full_comparisons 30\nincremental_audit_moves 500\n"
                      << "full_sixsets_per_replay 230230\n";
            return 0;
        }
        if (argc == 6 && std::string(argv[1]) == "--search") {
            int threads = std::stoi(argv[2]);
            int seconds = std::stoi(argv[3]);
            uint64_t seed = std::stoull(argv[4]);
            if (threads < 1 || threads > 64 || seconds < 1) {
                throw std::runtime_error("invalid threads/seconds");
            }
            std::string error;
            if (!audit(m, error)) throw std::runtime_error("pre-search audit: " + error);
            Shared sh;
            sh.out = argv[5];
            fs::create_directories(sh.out);
            sh.deadline = std::chrono::steady_clock::now() + std::chrono::seconds(seconds);
            std::vector<std::thread> threads_v;
            for (int i = 0; i < threads; ++i) threads_v.emplace_back(worker, std::cref(m), std::ref(sh), i, seed);
            auto next = std::chrono::steady_clock::now() + std::chrono::seconds(5);
            while (!sh.stop.load() && std::chrono::steady_clock::now() < sh.deadline) {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                if (std::chrono::steady_clock::now() >= next) {
                    std::cout << "best " << sh.best.load() << " moves " << sh.moves.load() << "\n";
                    next += std::chrono::seconds(5);
                }
            }
            sh.stop.store(true);
            for (auto &t : threads_v) t.join();
            int best = sh.best.load();
            std::ofstream summary(sh.out / "summary.txt");
            summary << "status " << (best == 0 ? "VERIFIED_HIT" : "NO_HIT")
                    << "\nthreads " << threads << "\nseconds " << seconds << "\nseed " << seed
                    << "\nbest_missing_pairs " << best << "\ntotal_moves " << sh.moves.load() << "\n";
            std::cout << "FINAL " << (best == 0 ? "VERIFIED_HIT" : "NO_HIT")
                      << " best " << best << " moves " << sh.moves.load() << "\n";
            return best == 0 ? 0 : 3;
        }
        usage();
        return 2;
    } catch (const std::exception &e) {
        std::cerr << "ERROR " << e.what() << "\n";
        return 2;
    }
}
