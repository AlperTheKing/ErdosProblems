#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <set>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace {

struct Column {
    int sum = 0;
    unsigned support = 0;
    int epsilon = 0;
};

struct Search {
    int max_width;
    std::uint64_t sidon_rulers = 0;
    std::uint64_t valid_pairs = 0;
    std::array<int, 8> z{};
    std::vector<unsigned char> used;

    explicit Search(int maximum) : max_width(maximum), used(maximum + 1, 0) {}

    bool valid_gap(int gap) const {
        std::set<int> differences;
        std::set<int> sums;
        for (int i = 0; i < 8; ++i) {
            for (int j = i + 1; j < 8; ++j) {
                differences.insert(z[j] - z[i]);
            }
            for (int j = i; j < 8; ++j) {
                sums.insert(z[i] + z[j]);
            }
        }
        for (int sum : sums) {
            if (differences.contains(gap + sum)) {
                return false;
            }
        }
        return true;
    }

    std::vector<Column> columns(int width) const {
        std::vector<unsigned char> represented(width, 0);
        for (int i = 0; i < 7; ++i) {
            for (int j = i; j < 7; ++j) {
                for (int k = j; k < 7; ++k) {
                    const int total = z[i] + z[j] + z[k];
                    if (total < width) {
                        represented[total] = 1;
                    }
                }
            }
        }

        std::vector<Column> result;
        for (unsigned mask = 1; mask < (1U << 7); ++mask) {
            const int size = std::popcount(mask);
            int sum = 0;
            int maximum = 0;
            for (int i = 0; i < 7; ++i) {
                if (mask & (1U << i)) {
                    sum += z[i];
                    maximum = z[i];
                }
            }
            const int numerator = 3 * sum;
            if (numerator % size != 0) {
                continue;
            }
            const int total = numerator / size;
            if (total >= width || maximum > total || !represented[total]) {
                continue;
            }
            int center_index = -1;
            if (total % 3 == 0) {
                const int center = total / 3;
                for (int i = 0; i < 7; ++i) {
                    if (z[i] == center) {
                        center_index = i;
                    }
                }
            }
            const int epsilon = center_index >= 0 ? 1 : 0;
            if (size % 3 != epsilon) {
                continue;
            }
            if (epsilon && !(mask & (1U << center_index))) {
                continue;
            }
            result.push_back({total, mask, epsilon});
        }
        std::ranges::sort(result, {}, [](const Column& column) {
            return std::pair(column.sum, column.support);
        });
        return result;
    }

    bool inspect(int width) {
        ++sidon_rulers;
        const auto cols = columns(width);
        struct Violation {
            Column left;
            Column right;
            int left_size;
            int right_size;
            int left_blocks;
            int right_blocks;
            unsigned intersection;
        };
        std::vector<Violation> violations;
        for (std::size_t i = 0; i < cols.size(); ++i) {
            const int bi = std::popcount(cols[i].support);
            const int qi = (bi + 2 * cols[i].epsilon) / 3;
            for (std::size_t j = i + 1; j < cols.size(); ++j) {
                if (cols[i].sum == cols[j].sum) {
                    continue;
                }
                const int bj = std::popcount(cols[j].support);
                const int qj = (bj + 2 * cols[j].epsilon) / 3;
                const unsigned intersection = cols[i].support & cols[j].support;
                if (std::popcount(intersection) > qi + qj) {
                    violations.push_back(
                        {cols[i], cols[j], bi, bj, qi, qj, intersection}
                    );
                }
            }
        }
        if (violations.empty()) {
            return false;
        }

        for (int gap = 1; gap < width; ++gap) {
            const int cutoff = width - gap;
            if (!valid_gap(gap)) {
                continue;
            }
            ++valid_pairs;
            for (const auto& violation : violations) {
                    if (violation.right.sum > cutoff) {
                        continue;
                    }
                    const int h = std::popcount(violation.intersection);
                    std::cout << "FOUND\nwidth=" << width << "\nZ=";
                    for (int index = 0; index < 8; ++index) {
                        std::cout << (index == 0 ? "" : ",") << z[index];
                    }
                    std::cout << "\nG=" << gap << "\nK=" << cutoff
                              << "\nx=" << violation.left.sum
                              << "\ny=" << violation.right.sum
                              << "\nA_x_mask=" << violation.left.support
                              << "\nA_y_mask=" << violation.right.support
                              << "\nintersection_mask=" << violation.intersection
                              << "\nb_x=" << violation.left_size
                              << "\nb_y=" << violation.right_size
                              << "\nq_parameter_x=" << violation.left_blocks
                              << "\nq_parameter_y=" << violation.right_blocks
                              << "\nintersection=" << h
                              << "\nendpoint_sidon_rulers_scanned=" << sidon_rulers
                              << "\nadmissible_gaps_on_rulers_with_static_violations="
                              << valid_pairs << "\n";
                    return true;
            }
        }
        return false;
    }

    bool extend(int width, int depth, int next) {
        if (depth == 7) {
            return inspect(width);
        }
        const int remaining = 7 - depth;
        for (int value = next; value <= width - remaining; ++value) {
            std::array<int, 8> fresh{};
            int fresh_count = 0;
            bool admissible = true;
            for (int i = 0; i < depth; ++i) {
                const int difference = value - z[i];
                if (used[difference]) {
                    admissible = false;
                    break;
                }
                fresh[fresh_count++] = difference;
            }
            const int endpoint_difference = width - value;
            if (!admissible || used[endpoint_difference]) {
                continue;
            }
            for (int i = 0; i < fresh_count; ++i) {
                if (fresh[i] == endpoint_difference) {
                    admissible = false;
                    break;
                }
            }
            if (!admissible) {
                continue;
            }

            z[depth] = value;
            for (int i = 0; i < fresh_count; ++i) {
                used[fresh[i]] = 1;
            }
            used[endpoint_difference] = 1;
            if (extend(width, depth + 1, value + 1)) {
                return true;
            }
            used[endpoint_difference] = 0;
            for (int i = 0; i < fresh_count; ++i) {
                used[fresh[i]] = 0;
            }
        }
        return false;
    }

    bool run() {
        for (int width = 1; width <= max_width; ++width) {
            std::fill(used.begin(), used.end(), 0);
            z.fill(0);
            z[0] = 0;
            z[7] = width;
            used[width] = 1;
            if (extend(width, 1, 1)) {
                return true;
            }
        }
        std::cout << "NONE\nmax_width=" << max_width
                  << "\nendpoint_sidon_rulers_scanned=" << sidon_rulers
                  << "\nadmissible_gaps_on_rulers_with_static_violations="
                  << valid_pairs << "\n";
        return false;
    }
};

}  // namespace

int main(int argc, char** argv) {
    int max_width = 300;
    if (argc == 3 && std::string(argv[1]) == "--max-width") {
        max_width = std::atoi(argv[2]);
    } else if (argc != 1) {
        std::cerr << "usage: search_intersection_falsifier [--max-width N]\n";
        return 2;
    }
    if (max_width < 1) {
        std::cerr << "max width must be positive\n";
        return 2;
    }
    Search search(max_width);
    return search.run() ? 0 : 1;
}
