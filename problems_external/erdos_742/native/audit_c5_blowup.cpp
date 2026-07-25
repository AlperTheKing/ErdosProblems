#include <array>
#include <iostream>

int main() {
    int best = -1;
    std::array<int, 5> arg{};
    long long compositions = 0;
    for (int a = 1; a <= 21; ++a) {
        for (int b = 1; b <= 22 - a; ++b) {
            for (int c = 1; c <= 23 - a - b; ++c) {
                for (int d = 1; d <= 24 - a - b - c; ++d) {
                    const int e = 25 - a - b - c - d;
                    if (e < 1) continue;
                    ++compositions;
                    const int edges =
                        a * b + b * c + c * d + d * e + e * a;
                    if (edges > best) {
                        best = edges;
                        arg = {a, b, c, d, e};
                    }
                }
            }
        }
    }
    std::cout << "{\"verified\":true,\"compositions\":" << compositions
              << ",\"maximum\":" << best << ",\"parts\":["
              << arg[0] << "," << arg[1] << "," << arg[2] << ","
              << arg[3] << "," << arg[4] << "]}\n";
    return best == 145 ? 0 : 1;
}
