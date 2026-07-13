#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

namespace {

using u64 = std::uint64_t;

struct Options {
  u64 limit = 10000000;
  int threads = 1;
};

Options parse_options(int argc, char** argv) {
  Options options;
#ifdef _OPENMP
  options.threads = std::min(64, omp_get_max_threads());
#endif
  for (int i = 1; i < argc; ++i) {
    const std::string argument = argv[i];
    if (argument == "--limit" && i + 1 < argc) {
      options.limit = std::stoull(argv[++i]);
    } else if (argument == "--threads" && i + 1 < argc) {
      options.threads = std::stoi(argv[++i]);
    } else {
      throw std::invalid_argument("usage: affine_census --limit N [--threads T]");
    }
  }
  if (options.limit == std::numeric_limits<u64>::max()) {
    throw std::invalid_argument("limit is too large");
  }
  if (options.limit < 1 ||
      options.limit > static_cast<u64>(std::numeric_limits<std::int64_t>::max())) {
    throw std::invalid_argument("limit must lie in [1,INT64_MAX]");
  }
  if (options.limit > static_cast<u64>(std::numeric_limits<std::size_t>::max() - 1)) {
    throw std::invalid_argument("limit does not fit address space");
  }
  if (options.threads < 1 || options.threads > 64) {
    throw std::invalid_argument("threads must lie in [1,64]");
  }
  return options;
}

inline unsigned witness_mask(u64 n, const std::vector<std::uint8_t>& member) {
  const u64 shifted = n + 1;
  unsigned mask = 0;
  if ((shifted & 1U) == 0) {
    const u64 parent = shifted / 2;
    if (parent != 2 && member[static_cast<std::size_t>(parent)]) mask |= 1;
  }
  if (shifted % 3 == 0) {
    const u64 parent = shifted / 3;
    if (parent != 3 && member[static_cast<std::size_t>(parent)]) mask |= 2;
  }
  if (shifted % 5 == 0) {
    const u64 parent = shifted / 5;
    if (parent != 5 && member[static_cast<std::size_t>(parent)]) mask |= 4;
  }
  return mask;
}

std::vector<u64> checkpoints(u64 limit) {
  std::vector<u64> points;
  for (u64 x = 10; x <= limit;) {
    points.push_back(x);
    if (x > limit / 10) break;
    x *= 10;
  }
  for (u64 x = 16; x <= limit;) {
    points.push_back(x);
    if (x > limit / 2) break;
    x *= 2;
  }
  points.push_back(limit);
  std::sort(points.begin(), points.end());
  points.erase(std::unique(points.begin(), points.end()), points.end());
  return points;
}

}  // namespace

int main(int argc, char** argv) {
  try {
    const Options options = parse_options(argc, argv);
#ifdef _OPENMP
    omp_set_dynamic(0);
    omp_set_num_threads(options.threads);
#endif

    const auto started = std::chrono::steady_clock::now();
    std::vector<std::uint8_t> member(static_cast<std::size_t>(options.limit + 1), 0);
    if (options.limit >= 2) member[2] = 1;
    if (options.limit >= 3) member[3] = 1;
    if (options.limit >= 5) member[5] = 1;

    // A layer [lo, 2*lo-2] only reads indices below lo.
    for (u64 lo = 6; lo <= options.limit;) {
      const u64 hi = lo > (options.limit + 2) / 2
                         ? options.limit
                         : std::min(options.limit, 2 * lo - 2);
#pragma omp parallel for schedule(static)
      for (std::int64_t signed_n = static_cast<std::int64_t>(lo);
           signed_n <= static_cast<std::int64_t>(hi); ++signed_n) {
        const u64 n = static_cast<u64>(signed_n);
        member[static_cast<std::size_t>(n)] = witness_mask(n, member) != 0;
      }
      if (hi == options.limit) break;
      lo = hi + 1;
    }

    const auto generated = std::chrono::steady_clock::now();
    std::cout << "limit=" << options.limit << " threads=" << options.threads
              << " bytes=" << member.size() << '\n';
    std::cout << "X,count,density,mask1,mask2,mask3,mask4,mask5,mask6,mask7,collision_tax\n";

    u64 cumulative = 0;
    std::array<u64, 8> cumulative_masks{};
    u64 previous = 0;
    for (const u64 point : checkpoints(options.limit)) {
      u64 interval_count = 0;
      u64 m1 = 0, m2 = 0, m3 = 0, m4 = 0, m5 = 0, m6 = 0, m7 = 0;
#pragma omp parallel for schedule(static) reduction(+ : interval_count, m1, m2, m3, m4, m5, m6, m7)
      for (std::int64_t signed_n = static_cast<std::int64_t>(previous + 1);
           signed_n <= static_cast<std::int64_t>(point); ++signed_n) {
        const u64 n = static_cast<u64>(signed_n);
        if (!member[static_cast<std::size_t>(n)]) continue;
        ++interval_count;
        const unsigned mask = witness_mask(n, member);
        switch (mask) {
          case 1: ++m1; break;
          case 2: ++m2; break;
          case 3: ++m3; break;
          case 4: ++m4; break;
          case 5: ++m5; break;
          case 6: ++m6; break;
          case 7: ++m7; break;
          default: break;  // Seeds 2 and 3 have no affine parent.
        }
      }
      cumulative += interval_count;
      cumulative_masks[1] += m1;
      cumulative_masks[2] += m2;
      cumulative_masks[3] += m3;
      cumulative_masks[4] += m4;
      cumulative_masks[5] += m5;
      cumulative_masks[6] += m6;
      cumulative_masks[7] += m7;
      const u64 collision_tax = cumulative_masks[3] + cumulative_masks[5] +
                                cumulative_masks[6] + 2 * cumulative_masks[7];
      std::cout << point << ',' << cumulative << ',' << std::fixed
                << std::setprecision(12)
                << static_cast<long double>(cumulative) / point;
      for (unsigned mask = 1; mask <= 7; ++mask) {
        std::cout << ',' << cumulative_masks[mask];
      }
      std::cout << ',' << collision_tax << '\n';
      previous = point;
    }

    const auto finished = std::chrono::steady_clock::now();
    const double generation_seconds =
        std::chrono::duration<double>(generated - started).count();
    const double scan_seconds =
        std::chrono::duration<double>(finished - generated).count();
    std::cout << "generation_seconds=" << generation_seconds
              << " scan_seconds=" << scan_seconds << '\n';
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}
