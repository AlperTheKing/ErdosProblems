#include <algorithm>
#include <cstdint>
#include <iostream>
#include <vector>

static std::uint64_t numeric_count = 0;
static std::uint64_t graphical_count = 0;
static int n_global = 0;
static int min_sum_global = 0;
static int max_sq_global = 0;

static bool erdos_gallai(std::vector<int> d) {
    std::sort(d.begin(), d.end(), std::greater<int>());
    long long sum = 0;
    for (int x : d) sum += x;
    if (sum & 1) return false;
    long long prefix = 0;
    for (int k = 1; k <= static_cast<int>(d.size()); ++k) {
        prefix += d[k - 1];
        long long rhs = 1LL * k * (k - 1);
        for (int i = k; i < static_cast<int>(d.size()); ++i)
            rhs += std::min(d[i], k);
        if (prefix > rhs) return false;
    }
    return true;
}

static void enumerate(int pos, int last, int max_degree, int sum, int sq,
                      std::vector<int>& sequence) {
    const int left = n_global - pos;
    if (sum + left * max_degree < min_sum_global) return;
    if (sq + left * last * last > max_sq_global) return;
    if (pos == n_global) {
        if (sum >= min_sum_global && !(sum & 1) && sq <= max_sq_global) {
            ++numeric_count;
            if (erdos_gallai(sequence)) ++graphical_count;
        }
        return;
    }
    for (int degree = last; degree <= max_degree; ++degree) {
        const int new_sum = sum + degree;
        const int new_sq = sq + degree * degree;
        if (new_sq > max_sq_global) break;
        const int remaining = n_global - pos - 1;
        if (new_sum + remaining * max_degree < min_sum_global) continue;
        sequence.push_back(degree);
        enumerate(pos + 1, degree, max_degree, new_sum, new_sq, sequence);
        sequence.pop_back();
    }
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: count_degree_sequences N\n";
        return 2;
    }
    n_global = std::stoi(argv[1]);
    const int edge_threshold = (n_global * n_global) / 4 + 1;
    min_sum_global = 2 * edge_threshold;
    max_sq_global = (4 * n_global * n_global * n_global) / 15;
    const int max_degree = (7 * n_global - 1) / 10;

    std::vector<int> sequence;
    enumerate(0, 2, max_degree, 0, 0, sequence);
    std::cout << "n=" << n_global
              << " min_degree=2 max_degree=" << max_degree
              << " min_degree_sum=" << min_sum_global
              << " max_square_sum=" << max_sq_global
              << " numeric_sequences=" << numeric_count
              << " graphical_sequences=" << graphical_count << "\n";
}
