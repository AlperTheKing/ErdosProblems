#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <mutex>
#include <random>
#include <string>
#include <thread>
#include <vector>

namespace {

constexpr int P = 5;
constexpr int N = 8;
constexpr int POINTS = 1 << 14; // 4^7, representatives with x_0 = 1.

using Matrix = std::array<std::array<uint8_t, N>, N>;

struct Score {
    int raw;
    int64_t weighted;
};

struct Move {
    int row = -1;
    int col = -1;
    uint8_t value = 0;
    Score score{std::numeric_limits<int>::max(), std::numeric_limits<int64_t>::max()};
};

std::array<std::vector<uint8_t>, N> xvals;
std::atomic<int> global_best{POINTS + 1};
std::atomic<bool> stop_requested{false};
std::atomic<uint64_t> total_iterations{0};
std::mutex output_mutex;
std::string output_path;

uint8_t inv5(uint8_t x) {
    static constexpr uint8_t inv[5] = {0, 1, 3, 2, 4};
    return inv[x];
}

int rank_mod5(Matrix a) {
    int rank = 0;
    for (int col = 0; col < N; ++col) {
        int pivot = rank;
        while (pivot < N && a[pivot][col] == 0) ++pivot;
        if (pivot == N) continue;
        std::swap(a[pivot], a[rank]);
        const uint8_t scale = inv5(a[rank][col]);
        for (int j = col; j < N; ++j) a[rank][j] = (a[rank][j] * scale) % P;
        for (int i = 0; i < N; ++i) {
            if (i == rank || a[i][col] == 0) continue;
            const uint8_t factor = a[i][col];
            for (int j = col; j < N; ++j) {
                a[i][j] = static_cast<uint8_t>((a[i][j] + P - factor * a[rank][j] % P) % P);
            }
        }
        ++rank;
    }
    return rank;
}

void normalize_row(Matrix& a, int row, std::vector<uint8_t>* row_sums = nullptr) {
    int first = 0;
    while (first < N && a[row][first] == 0) ++first;
    if (first == N) return;
    const uint8_t scale = inv5(a[row][first]);
    if (scale == 1) return;
    for (int j = 0; j < N; ++j) a[row][j] = (a[row][j] * scale) % P;
    if (row_sums != nullptr) {
        for (uint8_t& value : *row_sums) value = (value * scale) % P;
    }
}

void write_matrix(const Matrix& a, int score, int worker, uint64_t iteration) {
    std::lock_guard<std::mutex> lock(output_mutex);
    if (score != global_best.load(std::memory_order_relaxed)) return;
    const std::string tmp = output_path + ".tmp";
    {
        std::ofstream out(tmp, std::ios::trunc);
        for (const auto& row : a) {
            for (int j = 0; j < N; ++j) {
                if (j) out << ' ';
                out << static_cast<int>(row[j]);
            }
            out << '\n';
        }
    }
    std::error_code ec;
    std::filesystem::remove(output_path, ec);
    ec.clear();
    std::filesystem::rename(tmp, output_path, ec);
    std::cout << "{\"event\":\"best\",\"uncovered_projective\":" << score
              << ",\"worker\":" << worker << ",\"iteration\":" << iteration << "}" << std::endl;
}

void publish_best(const Matrix& a, int score, int worker, uint64_t iteration) {
    int previous = global_best.load(std::memory_order_relaxed);
    while (score < previous &&
           !global_best.compare_exchange_weak(previous, score, std::memory_order_relaxed)) {
    }
    if (score == global_best.load(std::memory_order_relaxed)) write_matrix(a, score, worker, iteration);
    if (score == 0) stop_requested.store(true, std::memory_order_relaxed);
}

struct State {
    Matrix a{};
    std::array<std::vector<uint8_t>, N> sums;
    std::vector<uint8_t> cover_count;
    std::vector<uint16_t> weight;
    Score score{POINTS, POINTS};

    State() : cover_count(POINTS), weight(POINTS, 1) {
        for (auto& row : sums) row.resize(POINTS);
    }
};

template <class Rng>
void randomize(State& state, Rng& rng) {
    std::uniform_int_distribution<int> value_dist(0, P - 1);
    do {
        for (auto& row : state.a) {
            for (uint8_t& value : row) value = static_cast<uint8_t>(value_dist(rng));
        }
    } while (rank_mod5(state.a) != N);
    for (int r = 0; r < N; ++r) normalize_row(state.a, r);

    std::fill(state.cover_count.begin(), state.cover_count.end(), 0);
    std::fill(state.weight.begin(), state.weight.end(), 1);
    for (int r = 0; r < N; ++r) {
        auto& row_sums = state.sums[r];
        for (int point = 0; point < POINTS; ++point) {
            int sum = 0;
            for (int c = 0; c < N; ++c) sum += state.a[r][c] * xvals[c][point];
            row_sums[point] = static_cast<uint8_t>(sum % P);
            if (row_sums[point] == 0) ++state.cover_count[point];
        }
    }
    state.score = {0, 0};
    for (int point = 0; point < POINTS; ++point) {
        if (state.cover_count[point] == 0) {
            ++state.score.raw;
            state.score.weighted += state.weight[point];
        }
    }
}

Score projected_score(const State& state, int row, int col, uint8_t new_value) {
    const int delta = (new_value + P - state.a[row][col]) % P;
    Score result = state.score;
    const auto& row_sums = state.sums[row];
    const auto& column = xvals[col];
    for (int point = 0; point < POINTS; ++point) {
        const bool old_zero = row_sums[point] == 0;
        const bool new_zero = ((row_sums[point] + delta * column[point]) % P) == 0;
        if (old_zero && !new_zero && state.cover_count[point] == 1) {
            ++result.raw;
            result.weighted += state.weight[point];
        } else if (!old_zero && new_zero && state.cover_count[point] == 0) {
            --result.raw;
            result.weighted -= state.weight[point];
        }
    }
    return result;
}

bool valid_move(State& state, int row, int col, uint8_t new_value) {
    const uint8_t old = state.a[row][col];
    state.a[row][col] = new_value;
    const bool valid = rank_mod5(state.a) == N;
    state.a[row][col] = old;
    return valid;
}

void apply_move(State& state, const Move& move) {
    const int row = move.row;
    const int col = move.col;
    const int delta = (move.value + P - state.a[row][col]) % P;
    auto& row_sums = state.sums[row];
    const auto& column = xvals[col];
    for (int point = 0; point < POINTS; ++point) {
        const bool old_zero = row_sums[point] == 0;
        const uint8_t new_sum = static_cast<uint8_t>((row_sums[point] + delta * column[point]) % P);
        const bool new_zero = new_sum == 0;
        if (old_zero && !new_zero) --state.cover_count[point];
        if (!old_zero && new_zero) ++state.cover_count[point];
        row_sums[point] = new_sum;
    }
    state.a[row][col] = move.value;
    normalize_row(state.a, row, &row_sums);
    state.score = move.score;
}

template <class Rng>
int choose_uncovered(const State& state, Rng& rng) {
    std::uniform_int_distribution<int> point_dist(0, POINTS - 1);
    for (int attempt = 0; attempt < 32; ++attempt) {
        const int point = point_dist(rng);
        if (state.cover_count[point] == 0) return point;
    }
    const int start = point_dist(rng);
    for (int offset = 0; offset < POINTS; ++offset) {
        const int point = (start + offset) % POINTS;
        if (state.cover_count[point] == 0) return point;
    }
    return -1;
}

void reweight(State& state) {
    state.score.weighted = 0;
    for (int point = 0; point < POINTS; ++point) {
        if (state.cover_count[point] == 0) {
            if (state.weight[point] < 4095) ++state.weight[point];
            state.score.weighted += state.weight[point];
        }
    }
}

void worker(int worker_id, uint64_t seed, std::chrono::steady_clock::time_point deadline) {
    std::mt19937_64 rng(seed + 0x9e3779b97f4a7c15ULL * static_cast<uint64_t>(worker_id + 1));
    std::uniform_int_distribution<int> row_dist(0, N - 1);
    std::uniform_int_distribution<int> col_dist(0, N - 1);
    std::uniform_int_distribution<int> value_dist(0, P - 1);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    State state;
    uint64_t iteration = 0;
    int local_best = POINTS + 1;
    int since_best = 0;

    randomize(state, rng);
    publish_best(state.a, state.score.raw, worker_id, iteration);
    local_best = state.score.raw;

    while (!stop_requested.load(std::memory_order_relaxed) && std::chrono::steady_clock::now() < deadline) {
        Move best;
        const int uncovered = choose_uncovered(state, rng);
        constexpr int BATCH = 6;
        for (int k = 0; k < BATCH; ++k) {
            const int row = row_dist(rng);
            const int col = col_dist(rng);
            uint8_t value;
            if (k < BATCH - 1 && uncovered >= 0) {
                const uint8_t old_sum = state.sums[row][uncovered];
                const uint8_t delta = static_cast<uint8_t>((P - old_sum * inv5(xvals[col][uncovered]) % P) % P);
                value = static_cast<uint8_t>((state.a[row][col] + delta) % P);
            } else {
                do value = static_cast<uint8_t>(value_dist(rng)); while (value == state.a[row][col]);
            }
            if (value == state.a[row][col] || !valid_move(state, row, col, value)) continue;
            const Score candidate_score = projected_score(state, row, col, value);
            if (candidate_score.weighted < best.score.weighted ||
                (candidate_score.weighted == best.score.weighted && candidate_score.raw < best.score.raw)) {
                best = {row, col, value, candidate_score};
            }
        }

        if (best.row >= 0) {
            const int64_t delta = best.score.weighted - state.score.weighted;
            const double temperature = 8.0 + 60.0 * std::exp(-static_cast<double>(since_best) / 1200.0);
            const bool accept = delta <= 0 || unit(rng) < std::exp(-static_cast<double>(delta) / temperature);
            if (accept) apply_move(state, best);
        }

        ++iteration;
        ++since_best;
        if (state.score.raw < local_best) {
            local_best = state.score.raw;
            since_best = 0;
            publish_best(state.a, state.score.raw, worker_id, iteration);
        }
        if (state.score.raw == 0) break;
        if (since_best > 0 && since_best % 400 == 0) reweight(state);
        if (since_best >= 12000) {
            randomize(state, rng);
            local_best = state.score.raw;
            since_best = 0;
            publish_best(state.a, state.score.raw, worker_id, iteration);
        }
    }
    total_iterations.fetch_add(iteration, std::memory_order_relaxed);
}

void build_points() {
    for (auto& column : xvals) column.resize(POINTS);
    for (int point = 0; point < POINTS; ++point) {
        xvals[0][point] = 1;
        int code = point;
        for (int col = 1; col < N; ++col) {
            xvals[col][point] = static_cast<uint8_t>(1 + (code & 3));
            code >>= 2;
        }
    }
}

} // namespace

int main(int argc, char** argv) {
    int threads = static_cast<int>(std::thread::hardware_concurrency());
    int seconds = 60;
    uint64_t seed = 0xA17F5008ULL;
    output_path = "best.matrix";
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--threads" && i + 1 < argc) threads = std::stoi(argv[++i]);
        else if (arg == "--seconds" && i + 1 < argc) seconds = std::stoi(argv[++i]);
        else if (arg == "--seed" && i + 1 < argc) seed = std::stoull(argv[++i]);
        else if (arg == "--out" && i + 1 < argc) output_path = argv[++i];
        else {
            std::cerr << "usage: local_search [--threads N] [--seconds S] [--seed K] [--out FILE]\n";
            return 2;
        }
    }
    if (threads < 1 || seconds < 1) return 2;
    build_points();
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(seconds);
    std::vector<std::thread> pool;
    pool.reserve(threads);
    for (int id = 0; id < threads; ++id) pool.emplace_back(worker, id, seed, deadline);
    for (auto& thread : pool) thread.join();
    std::cout << "{\"event\":\"summary\",\"status\":\""
              << (global_best.load() == 0 ? "CANDIDATE" : "NO_HIT")
              << "\",\"best_uncovered_projective\":" << global_best.load()
              << ",\"iterations\":" << total_iterations.load() << "}" << std::endl;
    return global_best.load() == 0 ? 0 : 1;
}
