#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <mutex>
#include <numeric>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <tuple>
#include <vector>

namespace fs = std::filesystem;

struct Instance {
    int n = 0;
    int edge_count = 0;
    std::array<std::array<int, 26>, 26> edge_index{};
    std::vector<std::pair<uint8_t, uint8_t>> endpoints;
    std::vector<std::array<uint16_t, 15>> six_edges;
    std::vector<std::array<uint8_t, 6>> six_vertices;
    std::vector<std::vector<uint32_t>> incident_sixes;

    explicit Instance(int vertex_count) : n(vertex_count) {
        if (n < 6 || n > 26) throw std::runtime_error("n must lie in [6,26]");
        for (auto &row : edge_index) row.fill(-1);
        for (int u = 0; u < n; ++u) {
            for (int v = u + 1; v < n; ++v) {
                int e = static_cast<int>(endpoints.size());
                edge_index[u][v] = edge_index[v][u] = e;
                endpoints.push_back({static_cast<uint8_t>(u), static_cast<uint8_t>(v)});
            }
        }
        edge_count = static_cast<int>(endpoints.size());
        incident_sixes.resize(edge_count);
        for (int a = 0; a < n - 5; ++a)
        for (int b = a + 1; b < n - 4; ++b)
        for (int c = b + 1; c < n - 3; ++c)
        for (int d = c + 1; d < n - 2; ++d)
        for (int e = d + 1; e < n - 1; ++e)
        for (int f = e + 1; f < n; ++f) {
            std::array<uint8_t, 6> vv{
                static_cast<uint8_t>(a), static_cast<uint8_t>(b),
                static_cast<uint8_t>(c), static_cast<uint8_t>(d),
                static_cast<uint8_t>(e), static_cast<uint8_t>(f)};
            std::array<uint16_t, 15> ee{};
            int k = 0;
            for (int i = 0; i < 6; ++i) {
                for (int j = i + 1; j < 6; ++j) {
                    ee[k++] = static_cast<uint16_t>(edge_index[vv[i]][vv[j]]);
                }
            }
            uint32_t s = static_cast<uint32_t>(six_edges.size());
            six_vertices.push_back(vv);
            six_edges.push_back(ee);
            for (uint16_t edge : ee) incident_sixes[edge].push_back(s);
        }
    }
};

struct Verification {
    bool parser_ok = false;
    bool property_ok = false;
    uint64_t subsets_checked = 0;
    uint64_t missing_pairs = 0;
    std::array<uint8_t, 6> first_vertices{};
    uint8_t first_missing_mask = 0;
    std::string error;
};

static int inv5(int x) {
    static constexpr int inv[5] = {0, 1, 3, 2, 4};
    return inv[x];
}

static std::vector<uint8_t> affine25(const Instance &g, int merged_a = 0, int merged_b = 5,
                                     const std::array<int, 5> &label = {0,1,2,3,4}) {
    if (g.n != 25) throw std::runtime_error("affine25 requires n=25");
    std::vector<uint8_t> colors(g.edge_count);
    for (int e = 0; e < g.edge_count; ++e) {
        int u = g.endpoints[e].first, v = g.endpoints[e].second;
        int x1 = u % 5, y1 = u / 5, x2 = v % 5, y2 = v / 5;
        int dx = (x2 - x1 + 5) % 5, dy = (y2 - y1 + 5) % 5;
        int slope = dx == 0 ? 5 : (dy * inv5(dx)) % 5;
        int bucket;
        if (slope == merged_a || slope == merged_b) bucket = 0;
        else {
            bucket = 1;
            for (int s = 0; s < 6; ++s) {
                if (s == merged_a || s == merged_b) continue;
                if (s == slope) break;
                ++bucket;
            }
        }
        colors[e] = static_cast<uint8_t>(label[bucket]);
    }
    return colors;
}

static Verification verify_colors(const Instance &g, const std::vector<uint8_t> &colors) {
    Verification out;
    if (static_cast<int>(colors.size()) != g.edge_count) {
        out.error = "wrong edge-vector length";
        return out;
    }
    for (uint8_t c : colors) {
        if (c >= 5) {
            out.error = "colour outside [0,4]";
            return out;
        }
    }
    out.parser_ok = true;
    for (size_t s = 0; s < g.six_edges.size(); ++s) {
        uint8_t present = 0;
        for (uint16_t e : g.six_edges[s]) present |= static_cast<uint8_t>(1u << colors[e]);
        uint8_t missing = static_cast<uint8_t>((~present) & 31u);
        ++out.subsets_checked;
        if (missing) {
            out.missing_pairs += std::popcount(static_cast<unsigned>(missing));
            if (out.first_missing_mask == 0) {
                out.first_missing_mask = missing;
                out.first_vertices = g.six_vertices[s];
            }
        }
    }
    out.property_ok = out.missing_pairs == 0;
    return out;
}

static bool parse_raw(const Instance &g, const fs::path &path, std::vector<uint8_t> &colors,
                      std::string &error) {
    std::ifstream in(path);
    if (!in) {
        error = "cannot open " + path.string();
        return false;
    }
    colors.assign(g.edge_count, 255);
    std::string line;
    int line_no = 0, records = 0;
    while (std::getline(in, line)) {
        ++line_no;
        if (line.empty() || line[0] == '#') continue;
        std::istringstream ss(line);
        int u, v, c;
        if (!(ss >> u >> v >> c)) {
            error = "line " + std::to_string(line_no) + ": expected three integers";
            return false;
        }
        std::string trailing;
        if (ss >> trailing) {
            error = "line " + std::to_string(line_no) + ": trailing token";
            return false;
        }
        if (u < 0 || v < 0 || u >= g.n || v >= g.n || u == v) {
            error = "line " + std::to_string(line_no) + ": invalid endpoints";
            return false;
        }
        if (c < 0 || c >= 5) {
            error = "line " + std::to_string(line_no) + ": invalid colour";
            return false;
        }
        if (u > v) std::swap(u, v);
        int e = g.edge_index[u][v];
        if (colors[e] != 255) {
            error = "line " + std::to_string(line_no) + ": duplicate edge";
            return false;
        }
        colors[e] = static_cast<uint8_t>(c);
        ++records;
    }
    if (records != g.edge_count) {
        error = "expected " + std::to_string(g.edge_count) + " edges, got " + std::to_string(records);
        return false;
    }
    for (uint8_t c : colors) {
        if (c == 255) {
            error = "missing edge";
            return false;
        }
    }
    return true;
}

static void write_raw(const Instance &g, const std::vector<uint8_t> &colors, const fs::path &path) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("cannot write " + path.string());
    for (int e = 0; e < g.edge_count; ++e) {
        out << static_cast<int>(g.endpoints[e].first) << ' '
            << static_cast<int>(g.endpoints[e].second) << ' '
            << static_cast<int>(colors[e]) << '\n';
    }
}

struct State {
    std::vector<uint8_t> colors;
    std::vector<std::array<uint8_t, 5>> counts;
    std::vector<uint8_t> missing_mask;
    std::vector<int32_t> bad_pos;
    std::vector<uint32_t> bad_sets;
    int score = 0;
};

static void add_bad(State &st, uint32_t s) {
    if (st.bad_pos[s] >= 0) return;
    st.bad_pos[s] = static_cast<int32_t>(st.bad_sets.size());
    st.bad_sets.push_back(s);
}

static void remove_bad(State &st, uint32_t s) {
    int32_t p = st.bad_pos[s];
    if (p < 0) return;
    uint32_t last = st.bad_sets.back();
    st.bad_sets[p] = last;
    st.bad_pos[last] = p;
    st.bad_sets.pop_back();
    st.bad_pos[s] = -1;
}

static void rebuild(const Instance &g, State &st) {
    st.counts.assign(g.six_edges.size(), {});
    st.missing_mask.assign(g.six_edges.size(), 0);
    st.bad_pos.assign(g.six_edges.size(), -1);
    st.bad_sets.clear();
    st.score = 0;
    for (size_t s = 0; s < g.six_edges.size(); ++s) {
        for (uint16_t e : g.six_edges[s]) ++st.counts[s][st.colors[e]];
        uint8_t mask = 0;
        for (int c = 0; c < 5; ++c) if (st.counts[s][c] == 0) mask |= static_cast<uint8_t>(1u << c);
        st.missing_mask[s] = mask;
        st.score += std::popcount(static_cast<unsigned>(mask));
        if (mask) add_bad(st, static_cast<uint32_t>(s));
    }
}

static int delta_recolor(const Instance &g, const State &st, int edge, uint8_t target) {
    uint8_t old = st.colors[edge];
    if (old == target) return 0;
    int delta = 0;
    for (uint32_t s : g.incident_sixes[edge]) {
        if (st.counts[s][old] == 1) ++delta;
        if (st.counts[s][target] == 0) --delta;
    }
    return delta;
}

static void apply_recolor(const Instance &g, State &st, int edge, uint8_t target) {
    uint8_t old = st.colors[edge];
    if (old == target) return;
    int delta = 0;
    for (uint32_t s : g.incident_sixes[edge]) {
        uint8_t old_mask = st.missing_mask[s];
        if (st.counts[s][old] == 1) {
            st.missing_mask[s] |= static_cast<uint8_t>(1u << old);
            ++delta;
        }
        --st.counts[s][old];
        if (st.counts[s][target] == 0) {
            st.missing_mask[s] &= static_cast<uint8_t>(~(1u << target));
            --delta;
        }
        ++st.counts[s][target];
        uint8_t new_mask = st.missing_mask[s];
        if (old_mask == 0 && new_mask != 0) add_bad(st, s);
        else if (old_mask != 0 && new_mask == 0) remove_bad(st, s);
    }
    st.colors[edge] = target;
    st.score += delta;
}

static int score_full(const Instance &g, const std::vector<uint8_t> &colors) {
    return static_cast<int>(verify_colors(g, colors).missing_pairs);
}

static std::vector<uint8_t> seed_affine26(const Instance &g, std::mt19937_64 &rng, int variant) {
    if (g.n != 26) throw std::runtime_error("seed_affine26 requires n=26");
    Instance g25(25);
    int a = variant % 6;
    int b = (variant / 6) % 6;
    if (b == a) b = (b + 1) % 6;
    std::array<int, 5> labels{0,1,2,3,4};
    std::shuffle(labels.begin(), labels.end(), rng);
    auto base = affine25(g25, a, b, labels);
    std::vector<uint8_t> colors(g.edge_count, 0);
    for (int e = 0; e < g25.edge_count; ++e) {
        auto [u,v] = g25.endpoints[e];
        colors[g.edge_index[u][v]] = base[e];
    }
    int aa = static_cast<int>(rng() % 5), bb = static_cast<int>(rng() % 5);
    int cc = static_cast<int>(rng() % 5);
    for (int u = 0; u < 25; ++u) {
        int x = u % 5, y = u / 5;
        int c = (aa * x + bb * y + cc) % 5;
        if ((variant & 2) != 0 && (rng() & 3) == 0) c = static_cast<int>(rng() % 5);
        colors[g.edge_index[u][25]] = static_cast<uint8_t>(c);
    }
    int perturb = variant % 4;
    for (int k = 0; k < perturb; ++k) {
        int e = static_cast<int>(rng() % g.edge_count);
        colors[e] = static_cast<uint8_t>(rng() % 5);
    }
    return colors;
}

struct SearchShared {
    std::atomic<bool> stop{false};
    std::atomic<int> global_best{std::numeric_limits<int>::max()};
    std::atomic<uint64_t> total_moves{0};
    std::mutex best_mutex;
    std::vector<uint8_t> best_colors;
    fs::path out_dir;
    std::chrono::steady_clock::time_point deadline;
};

static void publish_best(const Instance &g, SearchShared &sh, int worker, uint64_t moves,
                         const State &st) {
    int observed = sh.global_best.load(std::memory_order_relaxed);
    while (st.score < observed &&
           !sh.global_best.compare_exchange_weak(observed, st.score, std::memory_order_acq_rel)) {}
    if (st.score <= sh.global_best.load(std::memory_order_acquire)) {
        std::lock_guard<std::mutex> lock(sh.best_mutex);
        if (sh.best_colors.empty() || st.score <= score_full(g, sh.best_colors)) {
            sh.best_colors = st.colors;
            write_raw(g, st.colors, sh.out_dir / "best_checkpoint.col");
            std::ofstream meta(sh.out_dir / "best_checkpoint.txt");
            meta << "worker " << worker << "\nmoves " << moves << "\nscore " << st.score << "\n";
        }
    }
}

static void search_worker(const Instance &g, SearchShared &sh, int worker, uint64_t base_seed) {
    std::mt19937_64 rng(base_seed + 0x9e3779b97f4a7c15ULL * static_cast<uint64_t>(worker + 1));
    State st;
    uint64_t moves = 0;
    int restart = 0;
    while (!sh.stop.load(std::memory_order_relaxed) &&
           std::chrono::steady_clock::now() < sh.deadline) {
        if ((restart % 5) == 4) {
            st.colors.resize(g.edge_count);
            for (uint8_t &c : st.colors) c = static_cast<uint8_t>(rng() % 5);
        } else {
            st.colors = seed_affine26(g, rng, worker * 97 + restart * 13);
        }
        rebuild(g, st);
        publish_best(g, sh, worker, moves, st);
        int local_best = st.score;
        uint64_t last_improvement = moves;
        std::vector<uint64_t> tabu_until(g.edge_count, 0);
        while (!sh.stop.load(std::memory_order_relaxed) &&
               std::chrono::steady_clock::now() < sh.deadline &&
               moves - last_improvement < 25000) {
            if (st.score == 0) {
                Verification v = verify_colors(g, st.colors);
                if (v.parser_ok && v.property_ok) {
                    {
                        std::lock_guard<std::mutex> lock(sh.best_mutex);
                        sh.best_colors = st.colors;
                        write_raw(g, st.colors, sh.out_dir / "verified_hit.col");
                        std::ofstream report(sh.out_dir / "verified_hit_b.txt");
                        report << "status VERIFIED_HIT\nworker " << worker << "\nmoves " << moves
                               << "\nsubsets_checked " << v.subsets_checked
                               << "\nmissing_pairs " << v.missing_pairs << "\n";
                    }
                    sh.global_best.store(0);
                    sh.stop.store(true);
                    return;
                }
                throw std::runtime_error("incremental score zero disagreed with verifier");
            }
            if (st.bad_sets.empty()) throw std::runtime_error("empty bad set at positive score");
            uint32_t s = st.bad_sets[rng() % st.bad_sets.size()];
            uint8_t mm = st.missing_mask[s];
            int missing_options[5], nm = 0;
            for (int c = 0; c < 5; ++c) if (mm & (1u << c)) missing_options[nm++] = c;
            uint8_t target = static_cast<uint8_t>(missing_options[rng() % nm]);
            int best_delta = std::numeric_limits<int>::max();
            int candidates[15], nc = 0;
            for (uint16_t e : g.six_edges[s]) {
                if (st.colors[e] == target) continue;
                int d = delta_recolor(g, st, e, target);
                bool tabu = tabu_until[e] > moves;
                if (tabu && st.score + d >= sh.global_best.load(std::memory_order_relaxed)) continue;
                if (d < best_delta) {
                    best_delta = d;
                    nc = 0;
                    candidates[nc++] = e;
                } else if (d == best_delta) {
                    candidates[nc++] = e;
                }
            }
            int chosen;
            if (nc == 0 || (rng() % 100) < 7) {
                do { chosen = g.six_edges[s][rng() % 15]; } while (st.colors[chosen] == target);
            } else {
                chosen = candidates[rng() % nc];
            }
            uint8_t previous = st.colors[chosen];
            apply_recolor(g, st, chosen, target);
            tabu_until[chosen] = moves + 4 + (rng() % 13);
            (void)previous;
            ++moves;
            if (st.score < local_best) {
                local_best = st.score;
                last_improvement = moves;
                publish_best(g, sh, worker, moves, st);
            }
            if ((moves & 8191u) == 0) {
                int exact = score_full(g, st.colors);
                if (exact != st.score) throw std::runtime_error("periodic incremental score disagreement");
                sh.total_moves.fetch_add(8192, std::memory_order_relaxed);
            }
            if (moves - last_improvement > 6000 && (moves % 256) == 0) {
                for (int k = 0; k < 3; ++k) {
                    int e = static_cast<int>(rng() % g.edge_count);
                    uint8_t c = static_cast<uint8_t>(rng() % 5);
                    if (c != st.colors[e]) apply_recolor(g, st, e, c);
                }
            }
        }
        ++restart;
    }
    sh.total_moves.fetch_add(moves & 8191u, std::memory_order_relaxed);
}

static bool objective_audit(const Instance &g, std::string &why) {
    std::mt19937_64 rng(61720260723ULL);
    State st;
    st.colors.resize(g.edge_count);
    for (uint8_t &c : st.colors) c = static_cast<uint8_t>(rng() % 5);
    rebuild(g, st);
    if (st.score != score_full(g, st.colors)) {
        why = "initial incremental/full score mismatch";
        return false;
    }
    for (int k = 0; k < 300; ++k) {
        int e = static_cast<int>(rng() % g.edge_count);
        uint8_t c = static_cast<uint8_t>(rng() % 5);
        if (c == st.colors[e]) { --k; continue; }
        int before = st.score;
        int predicted = delta_recolor(g, st, e, c);
        apply_recolor(g, st, e, c);
        int exact = score_full(g, st.colors);
        if (st.score != exact || exact - before != predicted) {
            why = "delta mismatch at audit move " + std::to_string(k);
            return false;
        }
    }
    State rebuilt = st;
    rebuild(g, rebuilt);
    if (rebuilt.score != st.score || rebuilt.counts != st.counts ||
        rebuilt.missing_mask != st.missing_mask) {
        why = "rebuild disagreement after audit";
        return false;
    }
    return true;
}

static int selftest(const fs::path &fixture_dir) {
    fs::create_directories(fixture_dir);
    Instance g25(25);
    auto affine = affine25(g25);
    fs::path good = fixture_dir / "affine_k25.col";
    write_raw(g25, affine, good);
    std::vector<uint8_t> parsed;
    std::string error;
    if (!parse_raw(g25, good, parsed, error)) {
        std::cerr << "FAIL parse affine: " << error << "\n";
        return 1;
    }
    Verification v = verify_colors(g25, parsed);
    if (!v.property_ok || v.subsets_checked != 177100 || v.missing_pairs != 0) {
        std::cerr << "FAIL affine property subsets=" << v.subsets_checked
                  << " missing=" << v.missing_pairs << "\n";
        return 1;
    }

    fs::path missing = fixture_dir / "corrupt_missing_edge.col";
    {
        std::ifstream in(good);
        std::ofstream out(missing);
        std::string line;
        int k = 0;
        while (std::getline(in, line)) if (++k < g25.edge_count) out << line << '\n';
    }
    if (parse_raw(g25, missing, parsed, error)) {
        std::cerr << "FAIL parser accepted missing edge\n";
        return 1;
    }

    fs::path duplicate = fixture_dir / "corrupt_duplicate_edge.col";
    {
        std::ifstream in(good);
        std::ofstream out(duplicate);
        std::string first, line;
        std::getline(in, first);
        out << first << '\n' << first << '\n';
        while (std::getline(in, line)) out << line << '\n';
    }
    if (parse_raw(g25, duplicate, parsed, error)) {
        std::cerr << "FAIL parser accepted duplicate edge\n";
        return 1;
    }

    fs::path bad_colour = fixture_dir / "corrupt_bad_colour.col";
    {
        std::ifstream in(good);
        std::ofstream out(bad_colour);
        std::string line;
        std::getline(in, line);
        out << "0 1 5\n";
        while (std::getline(in, line)) out << line << '\n';
    }
    if (parse_raw(g25, bad_colour, parsed, error)) {
        std::cerr << "FAIL parser accepted colour 5\n";
        return 1;
    }

    fs::path all_zero = fixture_dir / "corrupt_all_zero.col";
    auto zero = affine;
    std::fill(zero.begin(), zero.end(), 0);
    write_raw(g25, zero, all_zero);
    if (!parse_raw(g25, all_zero, parsed, error) || verify_colors(g25, parsed).property_ok) {
        std::cerr << "FAIL semantic verifier accepted all-zero colouring\n";
        return 1;
    }

    bool found_single = false;
    auto one = affine;
    for (int e = 0; e < g25.edge_count && !found_single; ++e) {
        uint8_t old = one[e];
        for (int c = 0; c < 5; ++c) {
            if (c == old) continue;
            one[e] = static_cast<uint8_t>(c);
            if (!verify_colors(g25, one).property_ok) {
                found_single = true;
                break;
            }
        }
        if (!found_single) one[e] = old;
    }
    if (!found_single) {
        std::cerr << "FAIL could not construct a one-edge semantic corruption\n";
        return 1;
    }
    fs::path one_edge = fixture_dir / "corrupt_one_edge.col";
    write_raw(g25, one, one_edge);
    if (!parse_raw(g25, one_edge, parsed, error) || verify_colors(g25, parsed).property_ok) {
        std::cerr << "FAIL one-edge corruption was not rejected semantically\n";
        return 1;
    }

    Instance g26(26);
    std::string why;
    if (!objective_audit(g26, why)) {
        std::cerr << "FAIL objective audit: " << why << "\n";
        return 1;
    }
    std::cout << "SELFTEST PASS\n"
              << "affine_k25_edges " << g25.edge_count << "\n"
              << "affine_k25_sixsets " << v.subsets_checked << "\n"
              << "affine_k25_missing_pairs " << v.missing_pairs << "\n"
              << "parser_corruptions_rejected 3\n"
              << "semantic_corruptions_rejected 2\n"
              << "objective_delta_audit_moves 300\n"
              << "k26_sixsets " << g26.six_edges.size() << "\n";
    return 0;
}

static void usage() {
    std::cerr << "Usage:\n"
              << "  erdos617_native_b --selftest FIXTURE_DIR\n"
              << "  erdos617_native_b --verify N FILE\n"
              << "  erdos617_native_b --search THREADS SECONDS SEED OUT_DIR\n";
}

int main(int argc, char **argv) {
    try {
        if (argc >= 2 && std::string(argv[1]) == "--selftest") {
            if (argc != 3) { usage(); return 2; }
            return selftest(argv[2]);
        }
        if (argc >= 2 && std::string(argv[1]) == "--verify") {
            if (argc != 4) { usage(); return 2; }
            int n = std::stoi(argv[2]);
            Instance g(n);
            std::vector<uint8_t> colors;
            std::string error;
            if (!parse_raw(g, argv[3], colors, error)) {
                std::cout << "status PARSE_REJECT\nerror " << error << "\n";
                return 1;
            }
            Verification v = verify_colors(g, colors);
            std::cout << "status " << (v.property_ok ? "VERIFIED" : "PROPERTY_REJECT") << "\n"
                      << "n " << n << "\nedges " << g.edge_count
                      << "\nsubsets_checked " << v.subsets_checked
                      << "\nmissing_pairs " << v.missing_pairs << "\n";
            if (!v.property_ok) {
                std::cout << "first_vertices";
                for (uint8_t x : v.first_vertices) std::cout << ' ' << static_cast<int>(x);
                std::cout << "\nfirst_missing_colours";
                for (int c = 0; c < 5; ++c) if (v.first_missing_mask & (1u << c)) std::cout << ' ' << c;
                std::cout << "\n";
            }
            return v.property_ok ? 0 : 1;
        }
        if (argc >= 2 && std::string(argv[1]) == "--search") {
            if (argc != 6) { usage(); return 2; }
            int threads = std::stoi(argv[2]);
            int seconds = std::stoi(argv[3]);
            uint64_t seed = std::stoull(argv[4]);
            fs::path out_dir = argv[5];
            if (threads < 1 || threads > 64 || seconds < 1) {
                throw std::runtime_error("threads must be 1..64 and seconds positive");
            }
            fs::create_directories(out_dir);
            Instance g(26);
            std::string why;
            if (!objective_audit(g, why)) throw std::runtime_error("pre-search audit failed: " + why);
            SearchShared sh;
            sh.out_dir = out_dir;
            sh.deadline = std::chrono::steady_clock::now() + std::chrono::seconds(seconds);
            std::vector<std::thread> pool;
            for (int i = 0; i < threads; ++i) pool.emplace_back(search_worker, std::cref(g), std::ref(sh), i, seed);
            auto next = std::chrono::steady_clock::now() + std::chrono::seconds(5);
            while (!sh.stop.load() && std::chrono::steady_clock::now() < sh.deadline) {
                std::this_thread::sleep_for(std::chrono::milliseconds(200));
                if (std::chrono::steady_clock::now() >= next) {
                    std::cout << "best " << sh.global_best.load() << " moves " << sh.total_moves.load() << "\n";
                    next += std::chrono::seconds(5);
                }
            }
            sh.stop.store(true);
            for (auto &t : pool) t.join();
            int best = sh.global_best.load();
            std::ofstream summary(out_dir / "summary.txt");
            summary << "status " << (best == 0 ? "VERIFIED_HIT" : "NO_HIT") << "\n"
                    << "threads " << threads << "\nseconds " << seconds << "\nseed " << seed
                    << "\nbest_missing_pairs " << best << "\ntotal_moves " << sh.total_moves.load() << "\n";
            std::cout << "FINAL " << (best == 0 ? "VERIFIED_HIT" : "NO_HIT")
                      << " best " << best << " moves " << sh.total_moves.load() << "\n";
            return best == 0 ? 0 : 3;
        }
        usage();
        return 2;
    } catch (const std::exception &e) {
        std::cerr << "ERROR " << e.what() << "\n";
        return 2;
    }
}
