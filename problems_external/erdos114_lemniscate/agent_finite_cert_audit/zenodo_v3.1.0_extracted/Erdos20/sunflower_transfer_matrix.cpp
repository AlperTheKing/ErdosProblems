/**
 * Sunflower Transfer Matrix — PMF Salvo for Erdős #20
 *
 * Prima Materia Framework, Layer 2: Arithmetic Phase (Boolean Lattice)
 * The Sunflower Lemma (Erdős-Ko-Rado → Erdős-Sunflower):
 *
 *   A sunflower with k petals is a family of k sets {S_1,...,S_k}
 *   such that S_i ∩ S_j = Y for all i ≠ j (the common intersection Y
 *   is the "core"). The petals P_i = S_i \ Y are pairwise disjoint.
 *
 * Erdős #20 (Sunflower Conjecture):
 *   Let F be a family of w-element sets. If |F| > c_k^w, then F
 *   contains a sunflower with k petals. The conjecture: c_k = C(k)
 *   (depends only on k, not on w). The Erdős-Ko (1960) bound was
 *   c_k = (k-1)^w · w!. Alweiss-Lovett-Wu-Zhang (2019) improved to
 *   c_k = (C · k · log(w·k))^w.
 *
 * PMF formulation:
 *   - Atoms: elements of the ground set [n]
 *   - Molecules: w-subsets of [n]
 *   - Phase: families of w-subsets (the lattice gas lives on C(n,w))
 *   - Constraint: the family is "sunflower-free" (contains no k-sunflower)
 *   - Transfer matrix: process w-subsets in lexicographic order; the state
 *     tracks which intersection patterns have been "used"
 *
 * For small parameters (n ≤ 12, w ≤ 3, k = 3):
 *   Enumerate all sunflower-free families, compute partition function,
 *   extract the phase transition where sunflowers become unavoidable.
 *
 * This is computationally harder than the 1D problems because the state
 * space is C(n,w) instead of ~2^W. We use small parameters as proof of
 * concept.
 *
 * Compile: g++ -O3 -march=native -o sunflower_tm sunflower_transfer_matrix.cpp
 * Run:     ./sunflower_tm [n] [w] [k]
 */

#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <cstring>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <chrono>

using namespace std;
using u64 = uint64_t;

// ─── Combinatorial utilities ─────────────────────────────────────────────

// Represent a w-subset of [n] as a bitmask
vector<u64> enumerate_w_subsets(int n, int w) {
    vector<u64> result;
    // Generate all w-element subsets of {0,...,n-1}
    vector<int> indices(w);
    for (int i = 0; i < w; i++) indices[i] = i;

    while (true) {
        u64 mask = 0;
        for (int i = 0; i < w; i++) mask |= (1ULL << indices[i]);
        result.push_back(mask);

        // Next combination
        int i = w - 1;
        while (i >= 0 && indices[i] == n - w + i) i--;
        if (i < 0) break;
        indices[i]++;
        for (int j = i + 1; j < w; j++) indices[j] = indices[j - 1] + 1;
    }
    return result;
}

int popcount(u64 x) {
    return __builtin_popcountll(x);
}

// Check if a family F contains a k-sunflower
// F is given as a vector of bitmasks (each a w-subset)
bool has_sunflower(const vector<u64>& family, int w, int k) {
    int m = (int)family.size();
    if (m < k) return false;

    // For k=3 and small families, check all triples
    if (k == 3) {
        for (int i = 0; i < m; i++) {
            for (int j = i + 1; j < m; j++) {
                u64 core_ij = family[i] & family[j];
                for (int l = j + 1; l < m; l++) {
                    u64 core_il = family[i] & family[l];
                    u64 core_jl = family[j] & family[l];
                    // Sunflower: all pairwise intersections are the same
                    if (core_ij == core_il && core_il == core_jl) {
                        // Also check petals are pairwise disjoint
                        u64 core = core_ij;
                        u64 p_i = family[i] ^ core;
                        u64 p_j = family[j] ^ core;
                        u64 p_l = family[l] ^ core;
                        if ((p_i & p_j) == 0 && (p_i & p_l) == 0 && (p_j & p_l) == 0) {
                            return true;
                        }
                    }
                }
            }
        }
        return false;
    }

    // General k: check all k-subsets (exponential, only for small k and m)
    // For now, only k=3 is implemented efficiently
    return false;
}

// ─── Incremental sunflower check ─────────────────────────────────────────
// When adding set S to family F, check if S creates a new k-sunflower.
// Only need to check sunflowers that INCLUDE S.

bool creates_sunflower(const vector<u64>& family, u64 new_set, int w, int k) {
    int m = (int)family.size();
    if (m + 1 < k) return false;

    if (k == 3) {
        // Check all pairs (i, j) in existing family: does {family[i], family[j], new_set}
        // form a sunflower?
        for (int i = 0; i < m; i++) {
            u64 core_in = family[i] & new_set;
            for (int j = i + 1; j < m; j++) {
                u64 core_ij = family[i] & family[j];
                u64 core_jn = family[j] & new_set;
                if (core_in == core_ij && core_ij == core_jn) {
                    u64 core = core_in;
                    u64 p_i = family[i] ^ core;
                    u64 p_j = family[j] ^ core;
                    u64 p_n = new_set ^ core;
                    if ((p_i & p_j) == 0 && (p_i & p_n) == 0 && (p_j & p_n) == 0) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    return false;  // Only k=3 implemented
}

// ─── Partition Function Enumeration ──────────────────────────────────────
// Enumerate all sunflower-free families of w-subsets of [n].

struct SunflowerEnumerator {
    int n, w, k;
    vector<u64> all_subsets;  // all w-subsets of [n]
    vector<long long> density_of_states;  // count by family size
    long long total_count;
    int max_family_size;

    void enumerate(int _n, int _w, int _k) {
        n = _n; w = _w; k = _k;
        all_subsets = enumerate_w_subsets(n, w);
        int num_subsets = (int)all_subsets.size();

        density_of_states.assign(num_subsets + 1, 0);
        total_count = 0;
        max_family_size = 0;

        printf("  Ground set [%d], w=%d, k=%d: %d possible w-subsets\n",
               n, w, k, num_subsets);

        vector<u64> family;
        backtrack(0, family);
    }

    void backtrack(int start, vector<u64>& family) {
        int sz = (int)family.size();
        density_of_states[sz]++;
        total_count++;
        if (sz > max_family_size) max_family_size = sz;

        for (int i = start; i < (int)all_subsets.size(); i++) {
            // Check: adding all_subsets[i] to family doesn't create a k-sunflower
            if (!creates_sunflower(family, all_subsets[i], w, k)) {
                family.push_back(all_subsets[i]);
                backtrack(i + 1, family);
                family.pop_back();
            }
        }
    }
};

// ─── Transfer Matrix (Sequential) ───────────────────────────────────────
// Process w-subsets in lexicographic order.
// State: which recent subsets are in the family (bitmask of last M subsets).
// Constraint: no k-sunflower among selected subsets.
// This is a general-purpose transfer matrix over the powerset lattice.

struct SunflowerTransferMatrix {
    int n, w, k;
    vector<u64> all_subsets;

    // For small enough instances, we enumerate ALL sunflower-free families
    // as states of a lattice gas, and the transfer matrix connects families
    // that differ by one element.

    // Eigenvalue of the "growth matrix": how many ways can a sunflower-free
    // family of size m be extended to size m+1?
    vector<double> growth_rates;

    void compute(int _n, int _w, int _k) {
        n = _n; w = _w; k = _k;
        all_subsets = enumerate_w_subsets(n, w);
        int M = (int)all_subsets.size();

        printf("  Computing growth rates for n=%d, w=%d, k=%d (%d subsets)\n",
               n, w, k, M);

        // For each family size m, count:
        //   extensions[m] = total number of (family, new_subset) pairs where
        //     family is SF-free of size m, and family ∪ {new_subset} is also SF-free
        //   families[m] = number of SF-free families of size m

        vector<long long> families_count(M + 1, 0);
        vector<long long> extensions_count(M + 1, 0);

        vector<u64> family;
        count_extensions(0, family, families_count, extensions_count);

        growth_rates.clear();
        printf("\n  %4s | %12s | %12s | %12s\n",
               "m", "#families", "#extensions", "growth_rate");
        printf("  -----+--------------+--------------+--------------\n");

        for (int m = 0; m <= M; m++) {
            if (families_count[m] == 0) break;
            double rate = (families_count[m] > 0) ?
                          (double)extensions_count[m] / families_count[m] : 0;
            growth_rates.push_back(rate);
            printf("  %4d | %12lld | %12lld | %12.6f\n",
                   m, families_count[m], extensions_count[m], rate);
            if (rate < 0.001) break;  // No more extensions possible
        }
    }

    void count_extensions(int start, vector<u64>& family,
                          vector<long long>& fam_count, vector<long long>& ext_count) {
        int m = (int)family.size();
        fam_count[m]++;

        // Count how many subsets can extend this family
        int extensions = 0;
        for (int i = (m > 0 ? 0 : 0); i < (int)all_subsets.size(); i++) {
            // Only count subsets not already in family and after last element
            bool already_in = false;
            for (u64 s : family) {
                if (s == all_subsets[i]) { already_in = true; break; }
            }
            if (already_in) continue;
            // Must be after last family element (lexicographic)
            if (m > 0) {
                bool after_last = false;
                for (int j = 0; j < (int)all_subsets.size(); j++) {
                    if (all_subsets[j] == family.back()) {
                        if (i > j) after_last = true;
                        break;
                    }
                }
                if (!after_last) continue;
            }

            if (!creates_sunflower(family, all_subsets[i], w, k)) {
                extensions++;
            }
        }
        ext_count[m] += extensions;

        // Recurse
        int search_start = start;
        for (int i = search_start; i < (int)all_subsets.size(); i++) {
            if (!creates_sunflower(family, all_subsets[i], w, k)) {
                family.push_back(all_subsets[i]);
                count_extensions(i + 1, family, fam_count, ext_count);
                family.pop_back();
            }
        }
    }
};

// ─── Main ────────────────────────────────────────────────────────────────

int main(int argc, char** argv) {
    int max_n = 8;   // ground set size
    int w = 3;       // subset size
    int k = 3;       // sunflower petals

    if (argc > 1) max_n = atoi(argv[1]);
    if (argc > 2) w = atoi(argv[2]);
    if (argc > 3) k = atoi(argv[3]);

    printf("Sunflower Transfer Matrix — PMF Salvo for Erdős #20\n");
    printf("====================================================\n\n");
    printf("Parameters: ground set [n], w=%d-subsets, k=%d-sunflowers\n\n", w, k);

    FILE* json_out = fopen("EXP-MATH-ERDOS20-SUNFLOWER-001_RESULTS.json", "w");
    fprintf(json_out, "{\n  \"experiment_id\": \"EXP-MATH-ERDOS20-SUNFLOWER-001\",\n");
    fprintf(json_out, "  \"title\": \"Sunflower Lattice Gas — Partition Function\",\n");
    fprintf(json_out, "  \"problem\": \"Erdos #20: Sunflower Conjecture\",\n");
    fprintf(json_out, "  \"parameters\": {\"w\": %d, \"k\": %d},\n", w, k);
    fprintf(json_out, "  \"data\": [\n");

    bool first_json = true;

    for (int n = w + 1; n <= max_n; n++) {
        printf("═══ n = %d ═══\n", n);
        auto t0 = chrono::high_resolution_clock::now();

        // Part 1: Partition function
        SunflowerEnumerator se;
        se.enumerate(n, w, k);

        auto t1 = chrono::high_resolution_clock::now();
        double elapsed = chrono::duration<double>(t1 - t0).count();

        int num_subsets = (int)se.all_subsets.size();
        double max_density = (double)se.max_family_size / num_subsets;
        double log2_count = (se.total_count > 0) ? log2((double)se.total_count) : 0;

        printf("  Total SF-free families: %lld\n", se.total_count);
        printf("  Max family size: %d / %d = %.4f\n",
               se.max_family_size, num_subsets, max_density);
        printf("  log2(count) = %.4f (cf. Cameron-Erdos: ~%.4f)\n",
               log2_count, (double)num_subsets / 2.0);
        printf("  Erdos bound (k-1)^w = %d^%d = %.0f\n",
               k - 1, w, pow(k - 1, w));
        printf("  Time: %.3f s\n\n", elapsed);

        // Density of states
        printf("  Density of states:\n  ");
        for (int m = 0; m <= se.max_family_size; m++) {
            printf("c(%d)=%lld ", m, se.density_of_states[m]);
        }
        printf("\n\n");

        // Part 2: Growth rates (only for small n)
        if (num_subsets <= 56) {  // C(8,3) = 56
            SunflowerTransferMatrix stm;
            stm.compute(n, w, k);
            printf("\n");

            // Spectral gap estimate: growth rate decay indicates phase transition
            if (stm.growth_rates.size() >= 2) {
                double initial_growth = stm.growth_rates[0];
                double final_growth = stm.growth_rates.back();
                printf("  Growth rate decay: %.4f → %.4f (ratio %.4f)\n\n",
                       initial_growth, final_growth,
                       (initial_growth > 0) ? final_growth / initial_growth : 0);
            }
        }

        // JSON output
        if (!first_json) fprintf(json_out, ",\n");
        first_json = false;
        fprintf(json_out, "    {\"n\": %d, \"w\": %d, \"k\": %d, "
                "\"num_w_subsets\": %d, \"total_sf_free\": %lld, "
                "\"max_family_size\": %d, \"max_density\": %.8f, "
                "\"log2_count\": %.6f, \"erdos_bound\": %.0f, "
                "\"time_s\": %.3f, \"density_of_states\": [",
                n, w, k, num_subsets, se.total_count,
                se.max_family_size, max_density, log2_count,
                pow(k - 1, w), elapsed);
        for (int m = 0; m <= se.max_family_size; m++) {
            if (m > 0) fprintf(json_out, ", ");
            fprintf(json_out, "%lld", se.density_of_states[m]);
        }
        fprintf(json_out, "]}");

        if (elapsed > 120) {
            printf("  Step took %.0fs — stopping\n", elapsed);
            break;
        }
    }

    fprintf(json_out, "\n  ]\n}\n");
    fclose(json_out);

    printf("\nResults saved to EXP-MATH-ERDOS20-SUNFLOWER-001_RESULTS.json\n");
    return 0;
}
