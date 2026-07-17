#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

using u32 = std::uint32_t;
using u64 = std::uint64_t;
using u128 = unsigned __int128;
using State = std::array<int, 3>;

namespace {

std::string u128_string(u128 value) {
    if (value == 0) return "0";
    std::string out;
    while (value != 0) {
        out.push_back(static_cast<char>('0' + value % 10));
        value /= 10;
    }
    std::reverse(out.begin(), out.end());
    return out;
}

u128 gcd128(u128 a, u128 b) {
    while (b != 0) {
        const u128 r = a % b;
        a = b;
        b = r;
    }
    return a;
}

u64 checked_mul(u64 a, u64 b) {
    if (a != 0 && b > std::numeric_limits<u64>::max() / a) {
        throw std::overflow_error("uint64 multiplication overflow");
    }
    return a * b;
}

u64 ipow(u64 base, int exponent) {
    u64 out = 1;
    for (int i = 0; i < exponent; ++i) out = checked_mul(out, base);
    return out;
}

u128 binomial(int n, int k) {
    k = std::min(k, n - k);
    u128 out = 1;
    for (int i = 1; i <= k; ++i) {
        out = out * static_cast<unsigned>(n - k + i) / static_cast<unsigned>(i);
    }
    return out;
}

u128 multinomial(int a, int b, int c) {
    return binomial(a + b + c, a) * binomial(b + c, b);
}

std::vector<u64> merge_offset_images(
    const std::vector<u64>* d2,
    const std::vector<u64>* d3,
    const std::vector<u64>* d5) {
    const std::array<const std::vector<u64>*, 3> sources{d2, d3, d5};
    const std::array<u64, 3> slope{2, 3, 5};
    const std::array<u64, 3> bias{0, 1, 3};
    std::array<std::size_t, 3> pos{0, 0, 0};
    std::size_t capacity = 0;
    for (const auto* source : sources) {
        if (source != nullptr) capacity += source->size();
    }

    std::vector<u64> out;
    out.reserve(capacity);
    while (true) {
        bool found = false;
        u64 least = std::numeric_limits<u64>::max();
        for (int j = 0; j < 3; ++j) {
            if (sources[j] != nullptr && pos[j] < sources[j]->size()) {
                const u64 value = slope[j] * (*sources[j])[pos[j]] + bias[j];
                least = std::min(least, value);
                found = true;
            }
        }
        if (!found) break;
        out.push_back(least);
        for (int j = 0; j < 3; ++j) {
            if (sources[j] != nullptr && pos[j] < sources[j]->size()) {
                const u64 value = slope[j] * (*sources[j])[pos[j]] + bias[j];
                if (value == least) ++pos[j];
            }
        }
    }
    return out;
}

// This is the exact set recursion (48), evaluated one total-letter layer at a time.
std::vector<u64> build_offsets(int A, int B, int C) {
    std::map<State, std::vector<u64>> previous;
    previous[{0, 0, 0}] = {0};
    for (int n = 1; n <= A + B + C; ++n) {
        std::map<State, std::vector<u64>> current;
        for (int a = 0; a <= A; ++a) {
            for (int b = 0; b <= B; ++b) {
                const int c = n - a - b;
                if (c < 0 || c > C) continue;
                const std::vector<u64>* d2 = nullptr;
                const std::vector<u64>* d3 = nullptr;
                const std::vector<u64>* d5 = nullptr;
                if (a > 0) d2 = &previous.at({a - 1, b, c});
                if (b > 0) d3 = &previous.at({a, b - 1, c});
                if (c > 0) d5 = &previous.at({a, b, c - 1});
                current[{a, b, c}] = merge_offset_images(d2, d3, d5);
            }
        }
        previous = std::move(current);
    }
    return std::move(previous.at({A, B, C}));
}

u64 fnv1a_offsets(const std::vector<u64>& offsets) {
    u64 hash = 14695981039346656037ULL;
    for (u64 value : offsets) {
        for (int byte = 0; byte < 8; ++byte) {
            hash ^= (value >> (8 * byte)) & 0xffU;
            hash *= 1099511628211ULL;
        }
    }
    return hash;
}

std::string hex64(u64 value) {
    std::ostringstream out;
    out << std::hex << std::setfill('0') << std::setw(16) << value;
    return out.str();
}

struct Block {
    int k = 0;
    int a = 0;
    int b = 0;
    int c = 0;
    u64 M = 0;
    u128 words = 0;
    u64 D = 0;
    u64 offset_min = 0;
    u64 offset_max = 0;
    u64 offset_fnv = 0;
    u128 offset_sum = 0;
    u128 offset_sum_sq = 0;
    u64 g0_count = 0;
    u64 g2_count = 0;
    std::string selected_color;
    std::vector<u64> U;
    std::vector<u64> V;
};

Block build_block(int va, int vb, int vc, int k, u64 Q, const std::string& tie_policy) {
    Block block;
    block.k = k;
    block.a = va * k;
    block.b = vb * k;
    block.c = vc * k;
    block.M = ipow(Q, k);
    block.words = multinomial(block.a, block.b, block.c);

    std::vector<u64> offsets = build_offsets(block.a, block.b, block.c);
    if (!std::is_sorted(offsets.begin(), offsets.end()) ||
        std::adjacent_find(offsets.begin(), offsets.end()) != offsets.end()) {
        throw std::runtime_error("offset support is not strictly sorted");
    }
    block.D = offsets.size();
    block.offset_min = offsets.front();
    block.offset_max = offsets.back();
    block.offset_fnv = fnv1a_offsets(offsets);
    for (u64 d : offsets) {
        if (d >= block.M) throw std::runtime_error("offset outside [0,M)");
        block.offset_sum += d;
        block.offset_sum_sq += static_cast<u128>(d) * d;
    }

    std::vector<u64> g0;
    std::vector<u64> g2;
    g0.reserve(offsets.size() / 2);
    g2.reserve(offsets.size() / 2);
    for (u64 d : offsets) {
        const u64 h = checked_mul(8, block.M) + d + 1;
        if (!(checked_mul(8, block.M) < h && h <= checked_mul(9, block.M))) {
            throw std::runtime_error("H element outside the stated block");
        }
        if (h % 3 == 0) {
            g0.push_back(h);
        } else if (h % 3 == 2) {
            g2.push_back(h);
        } else {
            throw std::runtime_error("H contains the forbidden residue 1 mod 3");
        }
    }
    block.g0_count = g0.size();
    block.g2_count = g2.size();

    bool select_g0;
    if (g0.size() > g2.size()) {
        select_g0 = true;
    } else if (g2.size() > g0.size()) {
        select_g0 = false;
    } else {
        select_g0 = tie_policy == "g0";
    }
    const auto& selected = select_g0 ? g0 : g2;
    if (selected.size() * 2 < offsets.size()) {
        throw std::runtime_error("selected color is not a majority half");
    }
    block.selected_color = select_g0 ? "G0" : "G2";
    block.U.reserve(selected.size());
    block.V.reserve(selected.size());
    for (u64 h : selected) {
        if (select_g0) {
            const u64 u = h;
            const u64 v = checked_mul(3, h) - 1;
            if (h == 3 || u % 3 != 0 || v % 3 != 2) {
                throw std::runtime_error("G0 -> G2 map check failed");
            }
            block.U.push_back(u);
            block.V.push_back(v);
        } else {
            const u64 u = checked_mul(2, h) - 1;
            const u64 v = h;
            if (h == 2 || u % 3 != 0 || v % 3 != 2) {
                throw std::runtime_error("G2 -> G0 map check failed");
            }
            block.U.push_back(u);
            block.V.push_back(v);
        }
    }
    return block;
}

bool disjoint_sorted(const std::vector<u64>& a, const std::vector<u64>& b) {
    std::size_t i = 0;
    std::size_t j = 0;
    while (i < a.size() && j < b.size()) {
        if (a[i] == b[j]) return false;
        if (a[i] < b[j]) ++i;
        else ++j;
    }
    return true;
}

void radix_sort_u64(std::vector<u64>& values) {
    if (values.size() < 1000000) {
        std::sort(values.begin(), values.end());
        return;
    }
    constexpr std::size_t radix = 1U << 16;
    int threads = 1;
#ifdef _OPENMP
    threads = std::min<int>(omp_get_max_threads(),
                            std::max<std::size_t>(1, values.size() / 1000000));
#endif
    std::vector<u64> scratch(values.size());
    std::vector<u64> positions(static_cast<std::size_t>(threads) * radix);
    std::vector<u64>* source = &values;
    std::vector<u64>* destination = &scratch;

    for (int shift = 0; shift < 64; shift += 16) {
        std::fill(positions.begin(), positions.end(), 0);
#ifdef _OPENMP
#pragma omp parallel num_threads(threads)
#endif
        {
            int tid = 0;
#ifdef _OPENMP
            tid = omp_get_thread_num();
#endif
            const std::size_t begin = source->size() * static_cast<std::size_t>(tid) / threads;
            const std::size_t end = source->size() * static_cast<std::size_t>(tid + 1) / threads;
            u64* local = positions.data() + static_cast<std::size_t>(tid) * radix;
            for (std::size_t i = begin; i < end; ++i) {
                ++local[((*source)[i] >> shift) & 0xffffU];
            }
        }

        u64 global = 0;
        for (std::size_t bucket = 0; bucket < radix; ++bucket) {
            u64 next = global;
            for (int tid = 0; tid < threads; ++tid) {
                u64& cell = positions[static_cast<std::size_t>(tid) * radix + bucket];
                const u64 count = cell;
                cell = next;
                next += count;
            }
            global = next;
        }
        if (global != source->size()) throw std::runtime_error("radix count mismatch");

#ifdef _OPENMP
#pragma omp parallel num_threads(threads)
#endif
        {
            int tid = 0;
#ifdef _OPENMP
            tid = omp_get_thread_num();
#endif
            const std::size_t begin = source->size() * static_cast<std::size_t>(tid) / threads;
            const std::size_t end = source->size() * static_cast<std::size_t>(tid + 1) / threads;
            u64* local = positions.data() + static_cast<std::size_t>(tid) * radix;
            for (std::size_t i = begin; i < end; ++i) {
                const u64 value = (*source)[i];
                (*destination)[local[(value >> shift) & 0xffffU]++] = value;
            }
        }
        std::swap(source, destination);
    }
    if (source != &values) values.swap(*source);
}

struct Runs {
    std::vector<u64> value;
    std::vector<u32> count;
};

Runs product_runs(const std::vector<u64>& A, const std::vector<u64>& B) {
    const u128 pair_count_128 = static_cast<u128>(A.size()) * B.size();
    if (pair_count_128 > std::numeric_limits<std::size_t>::max()) {
        throw std::overflow_error("product vector does not fit size_t");
    }
    const std::size_t pair_count = static_cast<std::size_t>(pair_count_128);
    std::vector<u64> products(pair_count);

#ifdef _OPENMP
#pragma omp parallel for schedule(static)
#endif
    for (std::int64_t i = 0; i < static_cast<std::int64_t>(A.size()); ++i) {
        u64* row = products.data() + static_cast<std::size_t>(i) * B.size();
        for (std::size_t j = 0; j < B.size(); ++j) row[j] = A[i] * B[j];
    }
    radix_sort_u64(products);

    std::size_t distinct = products.empty() ? 0 : 1;
    for (std::size_t i = 1; i < products.size(); ++i) {
        if (products[i] != products[i - 1]) ++distinct;
    }
    Runs runs;
    runs.value.reserve(distinct);
    runs.count.reserve(distinct);
    for (std::size_t begin = 0; begin < products.size();) {
        std::size_t end = begin + 1;
        while (end < products.size() && products[end] == products[begin]) ++end;
        const std::size_t multiplicity = end - begin;
        if (multiplicity > std::numeric_limits<u32>::max()) {
            throw std::overflow_error("single-rectangle multiplicity exceeds uint32");
        }
        runs.value.push_back(products[begin]);
        runs.count.push_back(static_cast<u32>(multiplicity));
        begin = end;
    }
    return runs;
}

struct EnergyResult {
    int K = 0;
    int lo = 0;
    int hi = 0;
    std::vector<int> source_k;
    std::vector<u64> block_pairs;
    u128 N = 0;
    bool computed = false;
    std::string status;
    u64 distinct_products = 0;
    u64 product_min = 0;
    u64 product_max = 0;
    u128 E = 0;
    u128 within_collision_pairs = 0;
    u128 cross_collision_pairs = 0;
    u64 max_r = 0;
    std::vector<u128> matrix;
    std::map<u64, u64> histogram;
};

EnergyResult compute_energy(
    int K,
    int lo,
    int hi,
    const std::vector<Block>& blocks,
    u64 max_pairs) {
    EnergyResult result;
    result.K = K;
    result.lo = lo;
    result.hi = hi;
    for (int k = lo; k <= hi; ++k) {
        result.source_k.push_back(k);
        const u128 count = static_cast<u128>(blocks[k].U.size()) * blocks[K - k].V.size();
        if (count > std::numeric_limits<u64>::max()) {
            throw std::overflow_error("rectangle pair count exceeds uint64");
        }
        result.block_pairs.push_back(static_cast<u64>(count));
        result.N += count;
    }
    if (result.N > max_pairs) {
        result.status = "skipped_pair_cap";
        return result;
    }

    std::vector<Runs> all_runs;
    all_runs.reserve(result.source_k.size());
    for (int k : result.source_k) {
        std::cerr << "K=" << K << " rectangle k=" << k << " pairs="
                  << blocks[k].U.size() * blocks[K - k].V.size() << std::endl;
        all_runs.push_back(product_runs(blocks[k].U, blocks[K - k].V));
    }

    const std::size_t m = all_runs.size();
    result.matrix.assign(m * m, 0);
    std::vector<std::size_t> pos(m, 0);
    bool first_product = true;
    while (true) {
        bool found = false;
        u64 least = std::numeric_limits<u64>::max();
        for (std::size_t i = 0; i < m; ++i) {
            if (pos[i] < all_runs[i].value.size()) {
                least = std::min(least, all_runs[i].value[pos[i]]);
                found = true;
            }
        }
        if (!found) break;
        std::vector<u64> count(m, 0);
        u64 total = 0;
        for (std::size_t i = 0; i < m; ++i) {
            if (pos[i] < all_runs[i].value.size() && all_runs[i].value[pos[i]] == least) {
                count[i] = all_runs[i].count[pos[i]];
                total += count[i];
                ++pos[i];
            }
        }
        if (first_product) {
            result.product_min = least;
            first_product = false;
        }
        result.product_max = least;
        ++result.distinct_products;
        result.E += static_cast<u128>(total) * total;
        result.max_r = std::max(result.max_r, total);
        ++result.histogram[total];
        for (std::size_t i = 0; i < m; ++i) {
            for (std::size_t j = 0; j < m; ++j) {
                result.matrix[i * m + j] += static_cast<u128>(count[i]) * count[j];
            }
        }
    }

    u128 matrix_sum = 0;
    u128 diagonal = 0;
    u128 cross = 0;
    for (std::size_t i = 0; i < m; ++i) {
        for (std::size_t j = 0; j < m; ++j) {
            matrix_sum += result.matrix[i * m + j];
        }
        diagonal += result.matrix[i * m + i];
        for (std::size_t j = i + 1; j < m; ++j) cross += result.matrix[i * m + j];
    }
    if (matrix_sum != result.E || diagonal < result.N || (diagonal - result.N) % 2 != 0) {
        throw std::runtime_error("collision matrix identity failed");
    }
    result.within_collision_pairs = (diagonal - result.N) / 2;
    result.cross_collision_pairs = cross;
    if (result.E != result.N + 2 * (result.within_collision_pairs + result.cross_collision_pairs)) {
        throw std::runtime_error("E=N+2C identity failed");
    }

    u128 hist_N = 0;
    u128 hist_E = 0;
    u64 hist_P = 0;
    for (const auto& [r, count] : result.histogram) {
        hist_P += count;
        hist_N += static_cast<u128>(r) * count;
        hist_E += static_cast<u128>(r) * r * count;
    }
    if (hist_P != result.distinct_products || hist_N != result.N || hist_E != result.E) {
        throw std::runtime_error("multiplicity histogram identity failed");
    }
    result.computed = true;
    result.status = "computed";
    return result;
}

std::string decimal_ratio(u128 numerator, u128 denominator) {
    const long double ratio = static_cast<long double>(numerator) /
                              static_cast<long double>(denominator);
    std::ostringstream out;
    out << std::fixed << std::setprecision(12) << ratio;
    return out.str();
}

void write_json(
    const std::string& path,
    int va,
    int vb,
    int vc,
    u64 Q,
    int kmax,
    u64 max_pairs,
    const std::string& tie_policy,
    const std::vector<Block>& blocks,
    const std::vector<EnergyResult>& energies,
    bool pair_sets_disjoint) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot open output JSON");
    out << "{\n";
    out << "  \"schema\": \"C26-rd-aggregated-energy-v1\",\n";
    out << "  \"ray\": [" << va << ", " << vb << ", " << vc << "],\n";
    out << "  \"base_Q\": \"" << Q << "\",\n";
    out << "  \"kmax\": " << kmax << ",\n";
    out << "  \"tie_policy\": \"" << tie_policy << "\",\n";
    out << "  \"max_pairs\": \"" << max_pairs << "\",\n";
    out << "  \"checks\": {\"pair_sets_disjoint_across_k\": "
        << (pair_sets_disjoint ? "true" : "false")
        << ", \"offset_recursion\": true, \"residue_constraints\": true},\n";
    out << "  \"blocks\": [\n";
    for (int k = 1; k <= kmax; ++k) {
        const Block& b = blocks[k];
        out << "    {\"k\": " << k
            << ", \"counts\": [" << b.a << ", " << b.b << ", " << b.c << "]"
            << ", \"M\": \"" << b.M << "\""
            << ", \"W\": \"" << u128_string(b.words) << "\""
            << ", \"D\": \"" << b.D << "\""
            << ", \"offset_min\": \"" << b.offset_min << "\""
            << ", \"offset_max\": \"" << b.offset_max << "\""
            << ", \"offset_fnv1a64_le\": \"" << hex64(b.offset_fnv) << "\""
            << ", \"offset_sum\": \"" << u128_string(b.offset_sum) << "\""
            << ", \"offset_sum_sq\": \"" << u128_string(b.offset_sum_sq) << "\""
            << ", \"H_G0\": \"" << b.g0_count << "\""
            << ", \"H_G2\": \"" << b.g2_count << "\""
            << ", \"selected_color\": \"" << b.selected_color << "\""
            << ", \"U_size\": \"" << b.U.size() << "\""
            << ", \"V_size\": \"" << b.V.size() << "\""
            << ", \"U_min\": \"" << b.U.front() << "\""
            << ", \"U_max\": \"" << b.U.back() << "\""
            << ", \"V_min\": \"" << b.V.front() << "\""
            << ", \"V_max\": \"" << b.V.back() << "\"}"
            << (k == kmax ? "\n" : ",\n");
    }
    out << "  ],\n";
    out << "  \"energies\": [\n";
    for (std::size_t index = 0; index < energies.size(); ++index) {
        const EnergyResult& e = energies[index];
        out << "    {\"K\": " << e.K << ", \"I\": [" << e.lo << ", " << e.hi << "]"
            << ", \"source_k\": [";
        for (std::size_t i = 0; i < e.source_k.size(); ++i) {
            if (i) out << ", ";
            out << e.source_k[i];
        }
        out << "], \"block_pairs\": [";
        for (std::size_t i = 0; i < e.block_pairs.size(); ++i) {
            if (i) out << ", ";
            out << "\"" << e.block_pairs[i] << "\"";
        }
        out << "], \"N\": \"" << u128_string(e.N) << "\", \"status\": \"" << e.status << "\"";
        if (e.computed) {
            const u128 divisor = gcd128(e.E, e.N);
            out << ", \"distinct_products\": \"" << e.distinct_products << "\""
                << ", \"product_min\": \"" << e.product_min << "\""
                << ", \"product_max\": \"" << e.product_max << "\""
                << ", \"E\": \"" << u128_string(e.E) << "\""
                << ", \"E_over_N\": {\"numerator\": \"" << u128_string(e.E / divisor)
                << "\", \"denominator\": \"" << u128_string(e.N / divisor)
                << "\", \"decimal\": \"" << decimal_ratio(e.E, e.N) << "\"}"
                << ", \"within_collision_pairs\": \"" << u128_string(e.within_collision_pairs) << "\""
                << ", \"cross_collision_pairs\": \"" << u128_string(e.cross_collision_pairs) << "\""
                << ", \"max_r\": \"" << e.max_r << "\""
                << ", \"matrix\": [";
            const std::size_t m = e.source_k.size();
            for (std::size_t i = 0; i < m; ++i) {
                if (i) out << ", ";
                out << "[";
                for (std::size_t j = 0; j < m; ++j) {
                    if (j) out << ", ";
                    out << "\"" << u128_string(e.matrix[i * m + j]) << "\"";
                }
                out << "]";
            }
            out << "]"
                << ", \"multiplicity_histogram\": [";
            bool first = true;
            for (const auto& [r, count] : e.histogram) {
                if (!first) out << ", ";
                first = false;
                out << "{\"r\": \"" << r << "\", \"products\": \"" << count << "\"}";
            }
            out << "]";
        }
        out << "}" << (index + 1 == energies.size() ? "\n" : ",\n");
    }
    out << "  ]\n";
    out << "}\n";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 9) {
            std::cerr << "usage: rd_energy_probe va vb vc kmax max_pairs tie_policy output.json threads\n";
            return 2;
        }
        const int va = std::stoi(argv[1]);
        const int vb = std::stoi(argv[2]);
        const int vc = std::stoi(argv[3]);
        const int kmax = std::stoi(argv[4]);
        const u64 max_pairs = std::stoull(argv[5]);
        const std::string tie_policy = argv[6];
        const std::string output_path = argv[7];
        const int threads = std::stoi(argv[8]);
        if (va <= 0 || vb <= 0 || vc <= 0 || kmax <= 0 ||
            (tie_policy != "g0" && tie_policy != "g2") || threads <= 0 || threads > 64) {
            throw std::invalid_argument("invalid arguments");
        }
#ifdef _OPENMP
        omp_set_num_threads(threads);
#else
        if (threads != 1) throw std::invalid_argument("binary lacks OpenMP; use threads=1");
#endif

        const u64 Q = checked_mul(ipow(2, va), checked_mul(ipow(3, vb), ipow(5, vc)));
        std::vector<Block> blocks(static_cast<std::size_t>(kmax + 1));
        for (int k = 1; k <= kmax; ++k) {
            std::cerr << "building block k=" << k << std::endl;
            blocks[k] = build_block(va, vb, vc, k, Q, tie_policy);
            std::cerr << "  D=" << blocks[k].D << " selected=" << blocks[k].selected_color
                      << " size=" << blocks[k].U.size() << std::endl;
        }

        bool pair_sets_disjoint = true;
        for (int i = 1; i <= kmax; ++i) {
            for (int j = i + 1; j <= kmax; ++j) {
                pair_sets_disjoint = pair_sets_disjoint && disjoint_sorted(blocks[i].U, blocks[j].U);
            }
        }
        if (!pair_sets_disjoint) throw std::runtime_error("U blocks overlap across k");

        std::vector<EnergyResult> energies;
        for (int K = 2; K <= 2 * kmax; ++K) {
            const int lo = (K + 3) / 4;
            const int hi = (3 * K) / 4;
            bool feasible = lo <= hi;
            for (int k = lo; k <= hi && feasible; ++k) {
                feasible = k >= 1 && k <= kmax && K - k >= 1 && K - k <= kmax;
            }
            if (!feasible) continue;
            std::cerr << "starting energy K=" << K << " I=[" << lo << "," << hi << "]" << std::endl;
            EnergyResult result = compute_energy(K, lo, hi, blocks, max_pairs);
            std::cerr << "  status=" << result.status << " N=" << u128_string(result.N);
            if (result.computed) {
                std::cerr << " E=" << u128_string(result.E)
                          << " E/N=" << decimal_ratio(result.E, result.N);
            }
            std::cerr << std::endl;
            energies.push_back(std::move(result));
        }

        write_json(output_path, va, vb, vc, Q, kmax, max_pairs, tie_policy,
                   blocks, energies, pair_sets_disjoint);
        std::cerr << "wrote " << output_path << std::endl;
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << std::endl;
        return 1;
    }
}
