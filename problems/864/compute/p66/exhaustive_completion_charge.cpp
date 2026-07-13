#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

using u64 = std::uint64_t;

struct Witness {
    bool valid = false;
    std::vector<int> A;
    int span = 0;
    int sigma = 0;
    int p = 0;
    int delta = 0;
    int c = 0;
    int u = 0;
    int beta = 0;
    int hS = 0;
    int v = 0;
    int w = 0;
    int hD = 0;
    int dR = 0;
    int margin = 0;
    int tau = 0;
};

static bool witness_less(const Witness& x, const Witness& y) {
    if (!y.valid) return true;
    if (x.margin != y.margin) return x.margin < y.margin;
    if (x.span != y.span) return x.span < y.span;
    if (x.A.size() != y.A.size()) return x.A.size() < y.A.size();
    return x.A < y.A;
}

static bool ratio_greater(const Witness& x, const Witness& y) {
    if (!y.valid) return true;
    if (x.hS == 0 || y.hS == 0) {
        if (x.hS == 0 && y.hS != 0) return x.beta > 0;
        if (x.hS != 0 && y.hS == 0) return false;
    }
    const long long lhs = 2LL * x.beta * y.hS;
    const long long rhs = 2LL * y.beta * x.hS;
    if (lhs != rhs) return lhs > rhs;
    if (x.span != y.span) return x.span < y.span;
    return x.A < y.A;
}

struct Stats {
    int span = 0;
    u64 admissible = 0;
    u64 repeated_residual = 0;
    u64 unproved_range = 0;
    u64 midpoint = 0;
    u64 nonzero_shift = 0;
    u64 failures = 0;
    u64 two_v_failures = 0;
    u64 v_plus_u_failures = 0;
    u64 w_failures = 0;
    u64 mixed_failures = 0;
    Witness min_margin;
    Witness min_unproved_margin;
    Witness max_ratio;
    Witness first_failure;
    Witness first_two_v_failure;
    Witness first_v_plus_u_failure;
    Witness first_w_failure;
    Witness first_mixed_failure;
};

class SpanSearch {
  public:
    explicit SpanSearch(int L)
        : L_(L), sum_count_(2 * L + 1, 0), present_(L + 1, false) {
        A_.push_back(0);
        present_[0] = true;
        sum_count_[0] = 1;
        stats_.span = L;
    }

    Stats run() {
        recurse(1, 0);
        return stats_;
    }

  private:
    int L_;
    std::vector<int> A_;
    std::vector<int> sum_count_;
    std::vector<bool> present_;
    Stats stats_;

    void recurse(int x, int repeated_labels) {
        if (x == L_) {
            add_endpoint_and_evaluate(repeated_labels);
            return;
        }

        recurse(x + 1, repeated_labels);
        add_and_recurse(x, repeated_labels);
    }

    bool increment_new_sums(int x, int repeated_labels,
                            int& new_repeated, std::vector<int>& labels) {
        new_repeated = repeated_labels;
        labels.clear();
        labels.reserve(A_.size() + 1);

        for (int old : A_) {
            const int label = old + x;
            if (sum_count_[label] == 1) ++new_repeated;
            ++sum_count_[label];
            labels.push_back(label);
            if (new_repeated > 1) return false;
        }
        const int diagonal = 2 * x;
        if (sum_count_[diagonal] == 1) ++new_repeated;
        ++sum_count_[diagonal];
        labels.push_back(diagonal);
        return new_repeated <= 1;
    }

    void undo_sums(const std::vector<int>& labels) {
        for (auto it = labels.rbegin(); it != labels.rend(); ++it) {
            --sum_count_[*it];
        }
    }

    void add_and_recurse(int x, int repeated_labels) {
        int new_repeated = repeated_labels;
        std::vector<int> labels;
        const bool valid = increment_new_sums(x, repeated_labels, new_repeated, labels);
        if (valid) {
            A_.push_back(x);
            present_[x] = true;
            recurse(x + 1, new_repeated);
            present_[x] = false;
            A_.pop_back();
        }
        undo_sums(labels);
    }

    void add_endpoint_and_evaluate(int repeated_labels) {
        int new_repeated = repeated_labels;
        std::vector<int> labels;
        const bool valid = increment_new_sums(L_, repeated_labels, new_repeated, labels);
        if (valid) {
            A_.push_back(L_);
            present_[L_] = true;
            evaluate(new_repeated);
            present_[L_] = false;
            A_.pop_back();
        }
        undo_sums(labels);
    }

    [[noreturn]] void fail(const std::string& message) const {
        std::cerr << "internal audit failure at span " << L_ << ": " << message << "\n";
        std::exit(3);
    }

    void evaluate(int repeated_labels) {
        ++stats_.admissible;
        if (repeated_labels == 0) return;

        int sigma = -1;
        int support = 0;
        for (int s = 0; s <= 2 * L_; ++s) {
            if (sum_count_[s] > 0) ++support;
            if (sum_count_[s] >= 2) {
                if (sigma != -1) fail("two repeated sum labels reached a leaf");
                sigma = s;
            }
        }
        if (sigma < 0) fail("repeated-label state disagrees with sum counts");

        std::vector<int> core;
        std::vector<int> residual;
        for (int x : A_) {
            const int mate = sigma - x;
            if (0 <= mate && mate <= L_ && present_[mate]) core.push_back(x);
            else residual.push_back(x);
        }
        if (residual.empty()) return;
        ++stats_.repeated_residual;

        const int delta = (sigma % 2 == 0 && 0 <= sigma / 2 &&
                           sigma / 2 <= L_ && present_[sigma / 2]) ? 1 : 0;
        if ((static_cast<int>(core.size()) - delta) % 2 != 0) fail("core parity");
        const int c = static_cast<int>(core.size());
        const int u = static_cast<int>(residual.size());
        const int p = (c - delta) / 2;

        if (sum_count_[sigma] != p + delta || p + delta < 2)
            fail("exceptional multiplicity/core identity");

        std::vector<bool> differences(L_ + 1, false);
        int difference_support = 0;
        for (std::size_t j = 0; j < A_.size(); ++j) {
            for (std::size_t i = 0; i < j; ++i) {
                const int d = A_[j] - A_[i];
                if (!differences[d]) {
                    differences[d] = true;
                    ++difference_support;
                }
            }
        }
        const int expected_differences = p * (p + delta) + c * u + u * (u - 1) / 2;
        if (difference_support != expected_differences) fail("difference support identity");

        std::vector<int> q_count(2 * L_ + 1, 0);
        for (std::size_t j = 0; j < residual.size(); ++j) {
            for (std::size_t i = 0; i <= j; ++i) {
                const int label = std::abs(residual[i] + residual[j] - sigma);
                if (label == 0) fail("residual pair sums to exceptional label");
                ++q_count[label];
                if (q_count[label] > 2) fail("three virtual pairs share a folded label");
            }
        }

        int beta = 0;
        int v = 0;
        int fold_w = 0;
        for (int d = 1; d <= 2 * L_; ++d) {
            const int old = (d <= L_ && differences[d]) ? 1 : 0;
            beta += std::max(0, old + q_count[d] - 1);
            if (old) v += q_count[d];
            else fold_w += std::max(0, q_count[d] - 1);
        }
        if (beta != v + fold_w) fail("beta decomposition");

        const int expected_support = 2 * p * (p + delta) + 1
                                   + c * u + u * (u + 1) / 2;
        if (support != expected_support) fail("sum support identity");
        const int hS = 2 * L_ + 1 - support;
        const int formula_hS = 2 * L_ - (2 * p * (p + delta)
                              + c * u + u * (u + 1) / 2);
        if (hS != formula_hS || hS < 0) fail("sum-hole identity");
        const int hD = L_ - difference_support;
        const int dR = c * u + u * (u - 1) / 2;
        if (hS != 2 * hD + dR - u) fail("sum/difference hole identity");

        Witness w;
        w.valid = true;
        w.A = A_;
        w.span = L_;
        w.sigma = sigma;
        w.p = p;
        w.delta = delta;
        w.c = c;
        w.u = u;
        w.beta = beta;
        w.hS = hS;
        w.v = v;
        w.w = fold_w;
        w.hD = hD;
        w.dR = dR;
        w.margin = hS - 2 * beta;
        w.tau = std::abs(sigma - L_);

        if (delta) ++stats_.midpoint;
        if (w.tau != 0) ++stats_.nonzero_shift;
        if (witness_less(w, stats_.min_margin)) stats_.min_margin = w;
        if (ratio_greater(w, stats_.max_ratio)) stats_.max_ratio = w;

        if (u > 2 * c - 5) {
            ++stats_.unproved_range;
            if (witness_less(w, stats_.min_unproved_margin)) stats_.min_unproved_margin = w;
        }
        if (w.margin < 0) {
            ++stats_.failures;
            if (!stats_.first_failure.valid || w.span < stats_.first_failure.span ||
                (w.span == stats_.first_failure.span && w.A < stats_.first_failure.A)) {
                stats_.first_failure = w;
            }
        }
        auto record_first = [&](Witness& slot) {
            if (!slot.valid || w.span < slot.span ||
                (w.span == slot.span && w.A < slot.A)) slot = w;
        };
        if (2 * v > dR) {
            ++stats_.two_v_failures;
            record_first(stats_.first_two_v_failure);
        }
        if (v + u > dR) {
            ++stats_.v_plus_u_failures;
            record_first(stats_.first_v_plus_u_failure);
        }
        if (fold_w > hD) {
            ++stats_.w_failures;
            record_first(stats_.first_w_failure);
        }
        if (2 * v + fold_w + u > dR + hD) {
            ++stats_.mixed_failures;
            record_first(stats_.first_mixed_failure);
        }
    }
};

static void print_int_array(std::ostream& out, const std::vector<int>& xs) {
    out << '[';
    for (std::size_t i = 0; i < xs.size(); ++i) {
        if (i) out << ',';
        out << xs[i];
    }
    out << ']';
}

static void print_witness(std::ostream& out, const Witness& w) {
    if (!w.valid) {
        out << "null";
        return;
    }
    out << "{\"A\":";
    print_int_array(out, w.A);
    out << ",\"span\":" << w.span
        << ",\"sigma\":" << w.sigma
        << ",\"p\":" << w.p
        << ",\"delta\":" << w.delta
        << ",\"c\":" << w.c
        << ",\"u\":" << w.u
        << ",\"beta\":" << w.beta
        << ",\"hS\":" << w.hS
        << ",\"v\":" << w.v
        << ",\"w\":" << w.w
        << ",\"hD\":" << w.hD
        << ",\"dR\":" << w.dR
        << ",\"margin\":" << w.margin
        << ",\"tau\":" << w.tau << '}';
}

int main(int argc, char** argv) {
    int max_span = 35;
    int threads = 1;
    std::string output = "problems/864/compute/p66/exhaustive_N36.json";
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--max-span" && i + 1 < argc) max_span = std::stoi(argv[++i]);
        else if (arg == "--threads" && i + 1 < argc) threads = std::stoi(argv[++i]);
        else if (arg == "--output" && i + 1 < argc) output = argv[++i];
        else {
            std::cerr << "usage: " << argv[0]
                      << " [--max-span L] [--threads T] [--output FILE]\n";
            return 2;
        }
    }
    if (max_span < 1 || threads < 1 || threads > 64) {
        std::cerr << "require max-span>=1 and 1<=threads<=64\n";
        return 2;
    }

    std::vector<Stats> by_span(max_span + 1);
    std::atomic<int> next_span{1};
    std::mutex log_mutex;
    std::vector<std::thread> pool;
    const int worker_count = std::min(threads, max_span);
    for (int worker = 0; worker < worker_count; ++worker) {
        pool.emplace_back([&]() {
            while (true) {
                const int L = next_span.fetch_add(1);
                if (L > max_span) break;
                by_span[L] = SpanSearch(L).run();
                std::lock_guard<std::mutex> lock(log_mutex);
                std::cerr << "span=" << L
                          << " admissible=" << by_span[L].admissible
                          << " records=" << by_span[L].repeated_residual
                          << " failures=" << by_span[L].failures << "\n";
            }
        });
    }
    for (auto& thread : pool) thread.join();

    Stats total;
    for (int L = 1; L <= max_span; ++L) {
        const Stats& s = by_span[L];
        total.admissible += s.admissible;
        total.repeated_residual += s.repeated_residual;
        total.unproved_range += s.unproved_range;
        total.midpoint += s.midpoint;
        total.nonzero_shift += s.nonzero_shift;
        total.failures += s.failures;
        total.two_v_failures += s.two_v_failures;
        total.v_plus_u_failures += s.v_plus_u_failures;
        total.w_failures += s.w_failures;
        total.mixed_failures += s.mixed_failures;
        if (s.min_margin.valid && witness_less(s.min_margin, total.min_margin))
            total.min_margin = s.min_margin;
        if (s.min_unproved_margin.valid &&
            witness_less(s.min_unproved_margin, total.min_unproved_margin))
            total.min_unproved_margin = s.min_unproved_margin;
        if (s.max_ratio.valid && ratio_greater(s.max_ratio, total.max_ratio))
            total.max_ratio = s.max_ratio;
        if (s.first_failure.valid && !total.first_failure.valid)
            total.first_failure = s.first_failure;
        if (s.first_two_v_failure.valid && !total.first_two_v_failure.valid)
            total.first_two_v_failure = s.first_two_v_failure;
        if (s.first_v_plus_u_failure.valid && !total.first_v_plus_u_failure.valid)
            total.first_v_plus_u_failure = s.first_v_plus_u_failure;
        if (s.first_w_failure.valid && !total.first_w_failure.valid)
            total.first_w_failure = s.first_w_failure;
        if (s.first_mixed_failure.valid && !total.first_mixed_failure.valid)
            total.first_mixed_failure = s.first_mixed_failure;
    }

    std::ofstream out(output);
    if (!out) {
        std::cerr << "cannot open output " << output << "\n";
        return 2;
    }
    out << "{\n  \"arithmetic\":\"integer only\",\n"
        << "  \"domain\":\"all endpoint-normalized admissible subsets of [0,L], 1<=L<="
        << max_span << "\",\n"
        << "  \"threads\":" << worker_count << ",\n"
        << "  \"counts\":{\"admissible\":" << total.admissible
        << ",\"repeated_residual\":" << total.repeated_residual
        << ",\"unproved_range\":" << total.unproved_range
        << ",\"midpoint\":" << total.midpoint
        << ",\"nonzero_shift\":" << total.nonzero_shift
        << ",\"failures\":" << total.failures << "},\n";
    out << "  \"decomposition_counts\":{\"two_v_failures\":" << total.two_v_failures
        << ",\"v_plus_u_failures\":" << total.v_plus_u_failures
        << ",\"w_failures\":" << total.w_failures
        << ",\"mixed_failures\":" << total.mixed_failures << "},\n";
    out << "  \"min_margin\":"; print_witness(out, total.min_margin); out << ",\n";
    out << "  \"min_unproved_margin\":"; print_witness(out, total.min_unproved_margin); out << ",\n";
    out << "  \"max_ratio\":"; print_witness(out, total.max_ratio); out << ",\n";
    out << "  \"first_failure\":"; print_witness(out, total.first_failure); out << ",\n";
    out << "  \"first_two_v_failure\":"; print_witness(out, total.first_two_v_failure); out << ",\n";
    out << "  \"first_v_plus_u_failure\":"; print_witness(out, total.first_v_plus_u_failure); out << ",\n";
    out << "  \"first_w_failure\":"; print_witness(out, total.first_w_failure); out << ",\n";
    out << "  \"first_mixed_failure\":"; print_witness(out, total.first_mixed_failure); out << ",\n";
    out << "  \"by_span\":[\n";
    for (int L = 1; L <= max_span; ++L) {
        const Stats& s = by_span[L];
        out << "    {\"span\":" << L
            << ",\"admissible\":" << s.admissible
            << ",\"repeated_residual\":" << s.repeated_residual
            << ",\"unproved_range\":" << s.unproved_range
            << ",\"failures\":" << s.failures << '}';
        out << (L == max_span ? "\n" : ",\n");
    }
    out << "  ]\n}\n";
    out.close();

    std::cout << "admissible=" << total.admissible
              << " records=" << total.repeated_residual
              << " unproved=" << total.unproved_range
              << " failures=" << total.failures << "\n";
    return total.failures == 0 ? 0 : 1;
}
