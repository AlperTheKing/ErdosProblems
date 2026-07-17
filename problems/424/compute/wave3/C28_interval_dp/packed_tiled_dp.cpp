#include <algorithm>
#include <atomic>
#include <bit>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <immintrin.h>
#include <omp.h>

using u64 = std::uint64_t;

struct Span {
    u64 lo = 0;
    u64 hi = 0;
    std::size_t word_offset = 0;
    std::size_t word_count = 0;
};

struct Level {
    std::vector<Span> spans;
    std::vector<u64> words;
};

struct Config {
    int A = 0;
    int B = 0;
    int C = 0;
    u64 tile_bits = 0;
    int threads = 1;
    u64 tile_begin = 0;
    u64 tile_end = std::numeric_limits<u64>::max();
};

class TiledCounter {
  public:
    explicit TiledCounter(Config cfg) : cfg_(cfg) {
        pow2_.resize(cfg_.A + 1, 1);
        pow3_.resize(cfg_.B + 1, 1);
        pow5_.resize(cfg_.C + 1, 1);
        for (int i = 1; i <= cfg_.A; ++i) pow2_[i] = pow2_[i - 1] * 2;
        for (int i = 1; i <= cfg_.B; ++i) pow3_[i] = pow3_[i - 1] * 3;
        for (int i = 1; i <= cfg_.C; ++i) pow5_[i] = pow5_[i - 1] * 5;
        state_count_ = static_cast<std::size_t>(cfg_.A + 1) * (cfg_.B + 1) * (cfg_.C + 1);
        state_modulus_.resize(state_count_);
        for (int a = 0; a <= cfg_.A; ++a) {
            for (int b = 0; b <= cfg_.B; ++b) {
                for (int c = 0; c <= cfg_.C; ++c) {
                    state_modulus_[index(a, b, c)] = pow2_[a] * pow3_[b] * pow5_[c];
                }
            }
        }
        modulus_ = state_modulus_[index(cfg_.A, cfg_.B, cfg_.C)];
        if (cfg_.tile_bits == 0) throw std::invalid_argument("tile-bits must be positive");
    }

    u64 modulus() const { return modulus_; }

    u64 tile_count() const { return (modulus_ + cfg_.tile_bits - 1) / cfg_.tile_bits; }

    u64 peak_bytes_per_worker_bound() const {
        std::vector<u64> level_bytes(cfg_.A + cfg_.B + cfg_.C + 1, 0);
        const u64 width = std::min(cfg_.tile_bits, modulus_);
        for (int a = 0; a <= cfg_.A; ++a) {
            for (int b = 0; b <= cfg_.B; ++b) {
                for (int c = 0; c <= cfg_.C; ++c) {
                    const u64 p = modulus_ / state_modulus_[index(a, b, c)];
                    const u64 length_bound = std::min(
                        state_modulus_[index(a, b, c)], (width + p - 1) / p + 1);
                    const u64 words = (length_bound + 63) / 64 + 1;
                    level_bytes[a + b + c] += 8 * words;
                }
            }
        }
        u64 peak = level_bytes[0];
        for (std::size_t n = 1; n < level_bytes.size(); ++n) {
            peak = std::max(peak, level_bytes[n - 1] + level_bytes[n]);
        }
        return peak;
    }

    u64 count_tile(u64 tile_index) const {
        const u64 lo = tile_index * cfg_.tile_bits;
        const u64 hi = std::min(modulus_, lo + cfg_.tile_bits);
        Level prev = make_level(0, lo, hi);
        Span &base = prev.spans[index(0, 0, 0)];
        if (base.lo == 0 && base.hi > 0) {
            prev.words[base.word_offset] |= 1;
        }

        for (int n = 1; n <= cfg_.A + cfg_.B + cfg_.C; ++n) {
            Level curr = make_level(n, lo, hi);
            const int amin = std::max(0, n - cfg_.B - cfg_.C);
            const int amax = std::min(cfg_.A, n);
            for (int a = amin; a <= amax; ++a) {
                const int bmin = std::max(0, n - a - cfg_.C);
                const int bmax = std::min(cfg_.B, n - a);
                for (int b = bmin; b <= bmax; ++b) {
                    const int c = n - a - b;
                    Span &out = curr.spans[index(a, b, c)];
                    if (a > 0) {
                        scatter(prev, prev.spans[index(a - 1, b, c)], curr, out, 2, 0);
                    }
                    if (b > 0) {
                        scatter(prev, prev.spans[index(a, b - 1, c)], curr, out, 3, 1);
                    }
                    if (c > 0) {
                        scatter(prev, prev.spans[index(a, b, c - 1)], curr, out, 5, 3);
                    }
                }
            }
            prev = std::move(curr);
        }

        const Span &target = prev.spans[index(cfg_.A, cfg_.B, cfg_.C)];
        u64 count = 0;
        const std::size_t full_words = static_cast<std::size_t>((target.hi - target.lo) / 64);
        for (std::size_t i = 0; i < full_words; ++i) {
            count += std::popcount(prev.words[target.word_offset + i]);
        }
        const unsigned tail = static_cast<unsigned>((target.hi - target.lo) % 64);
        if (tail != 0) {
            count += std::popcount(
                prev.words[target.word_offset + full_words] & ((u64{1} << tail) - 1));
        }
        return count;
    }

  private:
    Config cfg_;
    std::vector<u64> pow2_;
    std::vector<u64> pow3_;
    std::vector<u64> pow5_;
    std::vector<u64> state_modulus_;
    std::size_t state_count_ = 0;
    u64 modulus_ = 0;

    std::size_t index(int a, int b, int c) const {
        return (static_cast<std::size_t>(a) * (cfg_.B + 1) + b) * (cfg_.C + 1) + c;
    }

    Level make_level(int n, u64 target_lo, u64 target_hi) const {
        Level level;
        level.spans.resize(state_count_);
        std::size_t total_words = 0;
        const int amin = std::max(0, n - cfg_.B - cfg_.C);
        const int amax = std::min(cfg_.A, n);
        for (int a = amin; a <= amax; ++a) {
            const int bmin = std::max(0, n - a - cfg_.C);
            const int bmax = std::min(cfg_.B, n - a);
            for (int b = bmin; b <= bmax; ++b) {
                const int c = n - a - b;
                Span &span = level.spans[index(a, b, c)];
                const u64 state_m = state_modulus_[index(a, b, c)];
                const u64 p = modulus_ / state_m;
                span.lo = target_lo / p;
                span.hi = std::min(state_m, (target_hi + p - 1) / p);
                span.word_offset = total_words;
                span.word_count = static_cast<std::size_t>((span.hi - span.lo + 63) / 64);
                total_words += span.word_count + 1;
            }
        }
        level.words.assign(total_words, 0);
        return level;
    }

    static u64 ceil_nonnegative_difference(u64 value, unsigned residue, unsigned p) {
        if (value <= residue) return 0;
        return (value - residue + p - 1) / p;
    }

    static u64 extract_bits(const Level &level, const Span &span, u64 local_bit, unsigned count) {
        const std::size_t word = static_cast<std::size_t>(local_bit / 64);
        const unsigned shift = static_cast<unsigned>(local_bit % 64);
        u64 value = level.words[span.word_offset + word] >> shift;
        if (shift != 0) {
            value |= level.words[span.word_offset + word + 1] << (64 - shift);
        }
        if (count < 64) value &= (u64{1} << count) - 1;
        return value;
    }

    static void or_pattern(Level &level, const Span &span, u64 local_bit, u64 pattern) {
        const std::size_t word = static_cast<std::size_t>(local_bit / 64);
        const unsigned shift = static_cast<unsigned>(local_bit % 64);
        level.words[span.word_offset + word] |= pattern << shift;
        if (shift != 0) {
            level.words[span.word_offset + word + 1] |= pattern >> (64 - shift);
        }
    }

    static u64 dilation_mask(unsigned p, unsigned chunk) {
        u64 mask = 0;
        for (unsigned i = 0; i < chunk; ++i) mask |= u64{1} << (p * i);
        return mask;
    }

    static void scatter(
        const Level &input,
        const Span &child,
        Level &output,
        const Span &parent,
        unsigned p,
        unsigned residue) {
        u64 xlo = ceil_nonnegative_difference(parent.lo, residue, p);
        u64 xhi = ceil_nonnegative_difference(parent.hi, residue, p);
        xlo = std::max(xlo, child.lo);
        xhi = std::min(xhi, child.hi);
        if (xlo >= xhi) return;

        const unsigned chunk = 64 / p;
        const u64 mask = dilation_mask(p, chunk);
        u64 x = xlo;
        u64 out_bit = p * x + residue - parent.lo;
        while (x < xhi) {
            const unsigned take = static_cast<unsigned>(std::min<u64>(chunk, xhi - x));
            const u64 bits = extract_bits(input, child, x - child.lo, take);
            if (bits != 0) {
                or_pattern(output, parent, out_bit, _pdep_u64(bits, mask));
            }
            x += take;
            out_bit += static_cast<u64>(p) * take;
        }
    }
};

static Config parse_args(int argc, char **argv) {
    Config cfg;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto value = [&]() -> std::string {
            if (++i >= argc) throw std::invalid_argument("missing value after " + arg);
            return argv[i];
        };
        if (arg == "--a") cfg.A = std::stoi(value());
        else if (arg == "--b") cfg.B = std::stoi(value());
        else if (arg == "--c") cfg.C = std::stoi(value());
        else if (arg == "--tile-bits") cfg.tile_bits = std::stoull(value());
        else if (arg == "--threads") cfg.threads = std::stoi(value());
        else if (arg == "--tile-begin") cfg.tile_begin = std::stoull(value());
        else if (arg == "--tile-end") cfg.tile_end = std::stoull(value());
        else throw std::invalid_argument("unknown argument: " + arg);
    }
    if (cfg.A < 0 || cfg.B < 0 || cfg.C < 0 || cfg.threads < 1) {
        throw std::invalid_argument("counts must be nonnegative and threads positive");
    }
    return cfg;
}

int main(int argc, char **argv) {
    try {
        Config cfg = parse_args(argc, argv);
        TiledCounter counter(cfg);
        const u64 all_tiles = counter.tile_count();
        const u64 begin = std::min(cfg.tile_begin, all_tiles);
        const u64 end = std::min(cfg.tile_end, all_tiles);
        if (begin > end) throw std::invalid_argument("tile-begin exceeds tile-end");
        const u64 jobs = end - begin;
        const u64 report_every = std::max<u64>(1, jobs / 20);
        std::atomic<u64> done{0};
        std::atomic<u64> total{0};
        const auto started = std::chrono::steady_clock::now();
        omp_set_num_threads(cfg.threads);

#pragma omp parallel for schedule(dynamic, 1)
        for (long long raw = static_cast<long long>(begin);
             raw < static_cast<long long>(end);
             ++raw) {
            const u64 count = counter.count_tile(static_cast<u64>(raw));
            total.fetch_add(count, std::memory_order_relaxed);
            const u64 finished = done.fetch_add(1, std::memory_order_relaxed) + 1;
            if (finished % report_every == 0 || finished == jobs) {
                const double seconds = std::chrono::duration<double>(
                    std::chrono::steady_clock::now() - started).count();
#pragma omp critical
                std::cerr << "tiles " << finished << "/" << jobs << " count "
                          << total.load(std::memory_order_relaxed) << " seconds "
                          << std::fixed << std::setprecision(3) << seconds << "\n";
            }
        }

        const double seconds = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - started).count();
        std::cout << "{"
                  << "\"a\":" << cfg.A << ","
                  << "\"b\":" << cfg.B << ","
                  << "\"c\":" << cfg.C << ","
                  << "\"modulus\":" << counter.modulus() << ","
                  << "\"tile_bits\":" << cfg.tile_bits << ","
                  << "\"tile_begin\":" << begin << ","
                  << "\"tile_end\":" << end << ","
                  << "\"tiles\":" << jobs << ","
                  << "\"threads\":" << cfg.threads << ","
                  << "\"count\":" << total.load() << ","
                  << "\"seconds\":" << std::fixed << std::setprecision(6) << seconds << ","
                  << "\"peak_bytes_per_worker_bound\":" << counter.peak_bytes_per_worker_bound()
                  << "}\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "error: " << error.what() << "\n";
        return 2;
    }
}
