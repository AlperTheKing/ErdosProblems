#define main audit_small_base_blowups_main
#include "audit_small_base_blowups.cpp"
#undef main

int main() {
    constexpr int n = 7;
    constexpr U64 total = U64{1} << (n * (n - 1) / 2);
    U64 count = 0;
    for (U64 mask = 0; mask < total; ++mask) {
        if (d2c(graph_from_mask(n, mask))) ++count;
    }
    std::cout << "n=7 labeled_d2c=" << count << " total=" << total << "\n";
}
