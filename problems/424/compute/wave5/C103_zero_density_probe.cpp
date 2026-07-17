#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using u64 = std::uint64_t;

namespace {

std::vector<std::uint32_t> smallest_prime_factors(std::uint32_t limit) {
  std::vector<std::uint32_t> spf(static_cast<std::size_t>(limit) + 1);
  std::iota(spf.begin(), spf.end(), 0U);
  for (std::uint32_t p = 2; static_cast<u64>(p) * p <= limit; ++p) {
    if (spf[p] != p) continue;
    for (u64 multiple = static_cast<u64>(p) * p; multiple <= limit;
         multiple += p) {
      if (spf[static_cast<std::size_t>(multiple)] == multiple) {
        spf[static_cast<std::size_t>(multiple)] = p;
      }
    }
  }
  return spf;
}

void divisors_below_sqrt(
    const std::vector<std::pair<std::uint32_t, std::uint32_t>>& factors,
    std::size_t index,
    u64 current,
    u64 product,
    std::vector<std::uint32_t>& divisors) {
  if (index == factors.size()) {
    if (current >= 2 && current < product / current) {
      divisors.push_back(static_cast<std::uint32_t>(current));
    }
    return;
  }
  const auto [prime, exponent] = factors[index];
  u64 power = 1;
  for (std::uint32_t e = 0; e <= exponent; ++e) {
    if (current > product / power) break;
    const u64 next = current * power;
    if (next > product / next) break;
    divisors_below_sqrt(factors, index + 1, next, product, divisors);
    if (e != exponent) power *= prime;
  }
}

struct BandAudit {
  std::uint32_t lo = 0;
  std::uint32_t hi = 0;
  u64 min_count = 0;
  std::uint32_t min_x = 0;
  u64 max_count = 0;
  std::uint32_t max_x = 0;
};

bool ratio_less(u64 a_num, u64 a_den, u64 b_num, u64 b_den) {
  return a_num * b_den < b_num * a_den;
}

void print_histogram(std::ostream& out, const std::vector<u64>& histogram,
                     const std::string& indent) {
  out << "[";
  bool first = true;
  for (std::size_t i = 0; i < histogram.size(); ++i) {
    if (histogram[i] == 0) continue;
    if (!first) out << ",";
    out << "\n" << indent << "[" << i << ", " << histogram[i] << "]";
    first = false;
  }
  if (!first) out << "\n  ";
  out << "]";
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 3) {
    std::cerr << "usage: C103_zero_density_probe LIMIT OUTPUT_JSON\n";
    return 2;
  }
  const u64 parsed_limit = std::stoull(argv[1]);
  if (parsed_limit < 10 || parsed_limit > std::numeric_limits<std::uint32_t>::max() - 1ULL) {
    throw std::invalid_argument("LIMIT must lie in [10, 2^32-2]");
  }
  const auto limit = static_cast<std::uint32_t>(parsed_limit);
  const auto started = std::chrono::steady_clock::now();
  auto spf = smallest_prime_factors(limit + 1);

  std::vector<std::uint8_t> member(static_cast<std::size_t>(limit) + 1, 0);
  std::vector<std::uint16_t> min_depth(static_cast<std::size_t>(limit) + 1, 0);
  std::vector<std::uint16_t> min_leaves(static_cast<std::size_t>(limit) + 1, 0);
  member[2] = member[3] = 1;
  min_leaves[2] = min_leaves[3] = 1;

  std::vector<u64> depth_histogram(64, 0);
  std::vector<u64> leaf_histogram(128, 0);
  depth_histogram[0] = 2;
  leaf_histogram[1] = 2;

  u64 count = 2;
  u64 members_with_small_root = 0;
  u64 members_without_small_root = 0;
  u64 members_with_multiple_roots = 0;
  u64 total_root_witnesses = 0;
  std::uint32_t max_min_depth = 0;
  std::uint32_t max_min_leaves = 1;
  std::uint32_t first_without_small_root = 0;

  std::vector<std::pair<std::uint32_t, u64>> checkpoints;
  std::vector<std::pair<std::uint32_t, u64>> powers_two;
  std::vector<BandAudit> decade_bands;
  u64 next_decade = 10;
  u64 next_power_two = 16;
  std::uint32_t band_lo = 10;
  BandAudit current_band;
  current_band.lo = 10;
  current_band.hi = std::min<std::uint32_t>(99, limit);

  std::vector<std::uint32_t> divisors;
  divisors.reserve(512);
  for (std::uint32_t value = 4; value <= limit; ++value) {
    const std::uint32_t product = value + 1;
    std::uint32_t remaining = product;
    std::vector<std::pair<std::uint32_t, std::uint32_t>> factors;
    while (remaining > 1) {
      const std::uint32_t prime = spf[remaining];
      std::uint32_t exponent = 0;
      do {
        remaining /= prime;
        ++exponent;
      } while (remaining % prime == 0);
      factors.emplace_back(prime, exponent);
    }
    divisors.clear();
    divisors_below_sqrt(factors, 0, 1, product, divisors);

    std::uint16_t best_depth = std::numeric_limits<std::uint16_t>::max();
    std::uint16_t best_leaves = std::numeric_limits<std::uint16_t>::max();
    std::uint32_t witness_count = 0;
    bool small_root = false;
    for (const std::uint32_t left : divisors) {
      const std::uint32_t right = product / left;
      if (!member[left] || !member[right]) continue;
      ++witness_count;
      small_root = small_root || left == 2 || left == 3 || left == 5;
      best_depth = std::min<std::uint16_t>(
          best_depth, 1 + std::max(min_depth[left], min_depth[right]));
      best_leaves = std::min<std::uint16_t>(
          best_leaves, min_leaves[left] + min_leaves[right]);
    }

    if (witness_count != 0) {
      member[value] = 1;
      min_depth[value] = best_depth;
      min_leaves[value] = best_leaves;
      ++count;
      total_root_witnesses += witness_count;
      members_with_multiple_roots += witness_count >= 2;
      if (small_root) {
        ++members_with_small_root;
      } else {
        ++members_without_small_root;
        if (first_without_small_root == 0) first_without_small_root = value;
      }
      if (best_depth >= depth_histogram.size()) depth_histogram.resize(best_depth + 1, 0);
      if (best_leaves >= leaf_histogram.size()) leaf_histogram.resize(best_leaves + 1, 0);
      ++depth_histogram[best_depth];
      ++leaf_histogram[best_leaves];
      max_min_depth = std::max<std::uint32_t>(max_min_depth, best_depth);
      max_min_leaves = std::max<std::uint32_t>(max_min_leaves, best_leaves);
    }

    while (next_decade <= limit && value == next_decade) {
      checkpoints.emplace_back(value, count);
      if (next_decade > limit / 10) break;
      next_decade *= 10;
    }
    while (next_power_two <= limit && value == next_power_two) {
      powers_two.emplace_back(value, count);
      if (next_power_two > limit / 2) break;
      next_power_two *= 2;
    }

    if (value >= band_lo) {
      if (current_band.min_x == 0 ||
          ratio_less(count, value, current_band.min_count, current_band.min_x)) {
        current_band.min_count = count;
        current_band.min_x = value;
      }
      if (current_band.max_x == 0 ||
          ratio_less(current_band.max_count, current_band.max_x, count, value)) {
        current_band.max_count = count;
        current_band.max_x = value;
      }
      if (value == current_band.hi) {
        decade_bands.push_back(current_band);
        if (value != limit) {
          band_lo = value + 1;
          const u64 next_hi = std::min<u64>(limit, static_cast<u64>(band_lo) * 10 - 1);
          current_band = BandAudit{};
          current_band.lo = band_lo;
          current_band.hi = static_cast<std::uint32_t>(next_hi);
        }
      }
    }
  }
  if (checkpoints.empty() || checkpoints.back().first != limit) {
    checkpoints.emplace_back(limit, count);
  }
  if (powers_two.empty() || powers_two.back().first != limit) {
    powers_two.emplace_back(limit, count);
  }

  const auto finished = std::chrono::steady_clock::now();
  std::ofstream out(argv[2]);
  if (!out) throw std::runtime_error("cannot open output JSON");
  out << "{\n"
      << "  \"schema_version\": 1,\n"
      << "  \"arithmetic\": \"exact ascending divisor recurrence\",\n"
      << "  \"limit\": " << limit << ",\n"
      << "  \"count\": " << count << ",\n"
      << "  \"density\": [" << count << ", " << limit << "],\n"
      << "  \"max_min_depth\": " << max_min_depth << ",\n"
      << "  \"max_min_leaves\": " << max_min_leaves << ",\n"
      << "  \"nonseed_members\": " << count - 2 << ",\n"
      << "  \"members_with_root_factor_2_3_or_5\": " << members_with_small_root << ",\n"
      << "  \"members_without_root_factor_2_3_or_5\": " << members_without_small_root << ",\n"
      << "  \"first_without_root_factor_2_3_or_5\": " << first_without_small_root << ",\n"
      << "  \"members_with_multiple_root_witnesses\": " << members_with_multiple_roots << ",\n"
      << "  \"total_root_witnesses\": " << total_root_witnesses << ",\n"
      << "  \"min_depth_histogram\": ";
  print_histogram(out, depth_histogram, "    ");
  out << ",\n  \"min_leaf_histogram\": ";
  print_histogram(out, leaf_histogram, "    ");
  out << ",\n  \"checkpoints\": [";
  for (std::size_t i = 0; i < checkpoints.size(); ++i) {
    out << (i == 0 ? "\n" : ",\n") << "    [" << checkpoints[i].first
        << ", " << checkpoints[i].second << "]";
  }
  out << "\n  ],\n  \"power_two_checkpoints\": [";
  for (std::size_t i = 0; i < powers_two.size(); ++i) {
    out << (i == 0 ? "\n" : ",\n") << "    [" << powers_two[i].first
        << ", " << powers_two[i].second << "]";
  }
  out << "\n  ],\n  \"decade_density_extrema\": [";
  for (std::size_t i = 0; i < decade_bands.size(); ++i) {
    const auto& band = decade_bands[i];
    out << (i == 0 ? "\n" : ",\n")
        << "    {\"range\": [" << band.lo << ", " << band.hi
        << "], \"min\": [" << band.min_x << ", " << band.min_count
        << "], \"max\": [" << band.max_x << ", " << band.max_count << "]}";
  }
  out << "\n  ],\n"
      << "  \"seconds\": " << std::fixed << std::setprecision(6)
      << std::chrono::duration<double>(finished - started).count() << "\n"
      << "}\n";
  std::cout << "limit=" << limit << " count=" << count
            << " max_min_depth=" << max_min_depth
            << " max_min_leaves=" << max_min_leaves << "\n";
}
