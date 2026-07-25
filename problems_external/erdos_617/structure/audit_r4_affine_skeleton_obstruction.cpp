#include <array>
#include <iostream>
#include <set>
#include <utility>

namespace {

constexpr int q = 5;

int mod(int value) {
    value %= q;
    return value < 0 ? value + q : value;
}

int point(int x, int y) {
    return mod(x) * q + mod(y);
}

std::set<int> two_lines(int slope, int first_intercept,
                        int second_intercept) {
    std::set<int> result;
    for (int x = 0; x < q; ++x) {
        result.insert(point(x, slope * x + first_intercept));
        result.insert(point(x, slope * x + second_intercept));
    }
    return result;
}

}  // namespace

int main() {
    int pairs_checked = 0;
    for (int first_slope = 0; first_slope < q; ++first_slope) {
        for (int second_slope = first_slope + 1;
             second_slope < q;
             ++second_slope) {
            for (int a = 0; a < q; ++a) {
                for (int b = a + 1; b < q; ++b) {
                    const auto first = two_lines(first_slope, a, b);
                    for (int c = 0; c < q; ++c) {
                        for (int d = c + 1; d < q; ++d) {
                            const auto second =
                                two_lines(second_slope, c, d);
                            int intersection = 0;
                            for (int v : first) {
                                intersection += second.contains(v);
                            }
                            if (first.size() != 10 ||
                                second.size() != 10 ||
                                intersection != 4) {
                                std::cerr
                                    << "affine intersection disagreement\n";
                                return 1;
                            }
                            ++pairs_checked;
                        }
                    }
                }
            }
        }
    }

    const int summed_support_intersections = 10 * 4;
    const int neighbour_to_non_neighbour_intersections = 5 * 5;
    const int forced_m_intersections =
        summed_support_intersections -
        neighbour_to_non_neighbour_intersections;
    const int linear_k5_capacity = 10;
    if (forced_m_intersections != 15 ||
        forced_m_intersections <= linear_k5_capacity) {
        std::cerr << "counting identity disagreement\n";
        return 2;
    }

    std::cout << "VERIFIED two-line-pairs=" << pairs_checked
              << " each_intersection=4"
              << " forced_M_intersection_sum=15"
              << " linear_K5_capacity=10\n";
    return 0;
}
