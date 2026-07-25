#define main audit_small_base_blowups_main
#include "audit_small_base_blowups.cpp"
#undef main

int main() {
    const std::array<U64, 10> bases = {
        63, 2046, 3964, 7804, 7867,
        7930, 32700, 42238, 44280, 61112
    };
    Audit audit;
    for (U64 mask : bases) {
        const Graph base = graph_from_mask(7, mask);
        if (!d2c(base) || canonical_mask(base) != mask) return 2;
        std::vector<int> a(7);
        compositions(0, 25, a, base, mask, audit);
    }
    std::cout << "SUMMARY base_n=7 unlabeled_d2c=" << bases.size()
              << " compositions=" << audit.compositions
              << " substitutions=" << audit.substitutions
              << " above_current_best_tested=" << audit.threshold_tests
              << " maximum_with_K12_13_baseline=" << audit.best << "\n";
    if (audit.target.n == 25) {
        std::cout << "RAW_CANDIDATE_BEGIN\n";
        print_edges(audit.target);
        std::cout << "RAW_CANDIDATE_END\n";
        return 1;
    }
    return audit.best == 156 ? 0 : 3;
}
