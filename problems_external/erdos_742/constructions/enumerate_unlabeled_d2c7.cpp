#define main audit_small_base_blowups_main
#include "audit_small_base_blowups.cpp"
#undef main

int main() {
    constexpr int n = 7;
    constexpr U64 total = U64{1} << (n * (n - 1) / 2);
    std::set<U64> classes;
    U64 labeled = 0;
    for (U64 mask = 0; mask < total; ++mask) {
        const Graph g = graph_from_mask(n, mask);
        if (!d2c(g)) continue;
        ++labeled;
        classes.insert(canonical_mask(g));
    }
    std::cout << "n=7 labeled_d2c=" << labeled
              << " unlabeled_d2c=" << classes.size() << "\n";
    for (U64 mask : classes) std::cout << "base_mask=" << mask << "\n";
}
