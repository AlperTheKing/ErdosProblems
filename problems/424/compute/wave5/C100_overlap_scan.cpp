#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

using u64 = std::uint64_t;
using u128 = unsigned __int128;

namespace {

struct PairAudit {
  u64 intersection = 0;
  u64 failures = 0;
  u64 first_failure = 0;
  u64 last_failure = 0;
  u64 worst_x = 0;
  u128 worst_excess = 0;
  u64 worst_intersection = 0;
  u64 worst_left_size = 0;
  u64 worst_right_size = 0;
  u64 min_margin_after_5000_x = 0;
  u128 min_margin_after_5000 = std::numeric_limits<u64>::max();
};

struct ResiduePairAudit {
  u64 failures = 0;
  unsigned worst_residue = 0;
  u64 worst_intersection = 0;
  u64 worst_left_size = 0;
  u64 worst_right_size = 0;
  u64 worst_capacity = 0;
  u128 worst_excess = 0;
};

std::string decimal(u128 value) {
  if (value == 0) return "0";
  std::string result;
  while (value != 0) {
    result.push_back(static_cast<char>('0' + value % 10));
    value /= 10;
  }
  std::reverse(result.begin(), result.end());
  return result;
}

unsigned witness_mask(u64 n, const std::vector<std::uint8_t>& member) {
  const u64 shifted = n + 1;
  unsigned mask = 0;
  if (shifted % 2 == 0) {
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

void audit_pair(PairAudit& audit, u64 x, u64 left_size, u64 right_size) {
  const u128 lhs = static_cast<u128>(audit.intersection) * x;
  const u128 rhs = static_cast<u128>(left_size) * right_size;
  if (lhs > rhs) {
    const u128 excess = lhs - rhs;
    ++audit.failures;
    if (audit.first_failure == 0) audit.first_failure = x;
    audit.last_failure = x;
    if (excess > audit.worst_excess) {
      audit.worst_excess = excess;
      audit.worst_x = x;
      audit.worst_intersection = audit.intersection;
      audit.worst_left_size = left_size;
      audit.worst_right_size = right_size;
    }
  } else if (x >= 5000) {
    const u128 margin = rhs - lhs;
    if (margin < audit.min_margin_after_5000) {
      audit.min_margin_after_5000 = margin;
      audit.min_margin_after_5000_x = x;
    }
  }
}

void write_pair(std::ostream& out, const char* name, const PairAudit& audit) {
  out << "    \"" << name << "\": {\n"
      << "      \"intersection\": " << audit.intersection << ",\n"
      << "      \"failures\": " << audit.failures << ",\n"
      << "      \"first_failure\": " << audit.first_failure << ",\n"
      << "      \"last_failure\": " << audit.last_failure << ",\n"
      << "      \"worst_x\": " << audit.worst_x << ",\n"
      << "      \"worst_excess\": \"" << decimal(audit.worst_excess) << "\",\n"
      << "      \"worst_intersection\": " << audit.worst_intersection << ",\n"
      << "      \"worst_left_size\": " << audit.worst_left_size << ",\n"
      << "      \"worst_right_size\": " << audit.worst_right_size << ",\n"
      << "      \"min_margin_after_5000_x\": " << audit.min_margin_after_5000_x << ",\n"
      << "      \"min_margin_after_5000\": \""
      << decimal(audit.min_margin_after_5000) << "\"\n"
      << "    }";
}

void audit_residue_pair(
    ResiduePairAudit& audit,
    const std::array<u64, 30>& capacity,
    const std::array<u64, 30>& left,
    const std::array<u64, 30>& right,
    const std::array<u64, 30>& intersection) {
  for (unsigned residue = 0; residue < 30; ++residue) {
    const u128 lhs = static_cast<u128>(intersection[residue]) * capacity[residue];
    const u128 rhs = static_cast<u128>(left[residue]) * right[residue];
    if (lhs <= rhs) continue;
    ++audit.failures;
    const u128 excess = lhs - rhs;
    if (excess > audit.worst_excess) {
      audit.worst_excess = excess;
      audit.worst_residue = residue;
      audit.worst_intersection = intersection[residue];
      audit.worst_left_size = left[residue];
      audit.worst_right_size = right[residue];
      audit.worst_capacity = capacity[residue];
    }
  }
}

void write_residue_pair(
    std::ostream& out, const char* name, const ResiduePairAudit& audit) {
  out << "    \"" << name << "\": {\n"
      << "      \"failures\": " << audit.failures << ",\n"
      << "      \"worst_residue\": " << audit.worst_residue << ",\n"
      << "      \"worst_intersection\": " << audit.worst_intersection << ",\n"
      << "      \"worst_left_size\": " << audit.worst_left_size << ",\n"
      << "      \"worst_right_size\": " << audit.worst_right_size << ",\n"
      << "      \"worst_capacity\": " << audit.worst_capacity << ",\n"
      << "      \"worst_excess\": \"" << decimal(audit.worst_excess) << "\"\n"
      << "    }";
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 3 || argc > 4) {
    std::cerr << "usage: C100_overlap_scan LIMIT OUTPUT_JSON [THREADS]\n";
    return 2;
  }
  const u64 limit = std::stoull(argv[1]);
  if (limit < 24) throw std::invalid_argument("LIMIT must be at least 24");
  const int threads = argc == 4 ? std::stoi(argv[3]) : 1;
#ifdef _OPENMP
  omp_set_num_threads(threads);
#else
  if (threads != 1) throw std::invalid_argument("binary lacks OpenMP support");
#endif

  const auto started = std::chrono::steady_clock::now();
  std::vector<std::uint8_t> member(static_cast<std::size_t>(limit + 1), 0);
  member[2] = member[3] = member[5] = 1;

  // Every parent of n in [lo, 2*lo-2] is below lo, so each layer is race-free.
  for (u64 lo = 6; lo <= limit;) {
    const u64 hi = std::min(limit, 2 * lo - 2);
#pragma omp parallel for schedule(static)
    for (std::int64_t signed_n = static_cast<std::int64_t>(lo);
         signed_n <= static_cast<std::int64_t>(hi); ++signed_n) {
      const u64 n = static_cast<u64>(signed_n);
      member[static_cast<std::size_t>(n)] = witness_mask(n, member) != 0;
    }
    if (hi == limit) break;
    lo = hi + 1;
  }
  const auto generated = std::chrono::steady_clock::now();

  std::array<u64, 3> parent_cutoff{0, 0, 0};
  std::array<u64, 3> image_size{0, 0, 0};
  constexpr std::array<u64, 3> divisor{2, 3, 5};
  PairAudit p23, p25, p35;
  u64 count = 0;
  u64 collision_tax = 0;
  u64 triple = 0;
  u64 quadratic_failures = 0;
  u64 quadratic_first_failure = 0;
  u64 quadratic_last_failure = 0;
  u64 quadratic_worst_x = 0;
  u128 quadratic_worst_excess = 0;
  std::array<u64, 30> residue_capacity{};
  std::array<std::array<u64, 30>, 3> residue_image{};
  std::array<std::array<u64, 30>, 3> residue_pair{};

  for (u64 x = 0; x <= limit; ++x) {
    ++residue_capacity[x % 30];
    if (member[static_cast<std::size_t>(x)]) ++count;
    for (std::size_t j = 0; j < divisor.size(); ++j) {
      const u64 target = (x + 1) / divisor[j];
      while (parent_cutoff[j] < target) {
        ++parent_cutoff[j];
        if (member[static_cast<std::size_t>(parent_cutoff[j])] &&
            parent_cutoff[j] != divisor[j]) {
          ++image_size[j];
        }
      }
    }

    if (member[static_cast<std::size_t>(x)]) {
      const unsigned mask = witness_mask(x, member);
      const std::size_t residue = static_cast<std::size_t>(x % 30);
      for (unsigned bit = 0; bit < 3; ++bit) {
        if ((mask & (1U << bit)) != 0) ++residue_image[bit][residue];
      }
      if ((mask & 3U) == 3U) ++p23.intersection;
      if ((mask & 5U) == 5U) ++p25.intersection;
      if ((mask & 6U) == 6U) ++p35.intersection;
      if ((mask & 3U) == 3U) ++residue_pair[0][residue];
      if ((mask & 5U) == 5U) ++residue_pair[1][residue];
      if ((mask & 6U) == 6U) ++residue_pair[2][residue];
      if (mask == 7U) ++triple;
    }
    collision_tax = p23.intersection + p25.intersection + p35.intersection - triple;

    if (x >= 24) {
      audit_pair(p23, x, image_size[0], image_size[1]);
      audit_pair(p25, x, image_size[0], image_size[2]);
      audit_pair(p35, x, image_size[1], image_size[2]);

      // This is the direct sufficient consequence of the three pair bounds.
      const u128 lhs = static_cast<u128>(collision_tax) * x;
      const u128 rhs = static_cast<u128>(3) * count * count;
      if (lhs > rhs) {
        const u128 excess = lhs - rhs;
        ++quadratic_failures;
        if (quadratic_first_failure == 0) quadratic_first_failure = x;
        quadratic_last_failure = x;
        if (excess > quadratic_worst_excess) {
          quadratic_worst_excess = excess;
          quadratic_worst_x = x;
        }
      }
    }
  }
  const auto audited = std::chrono::steady_clock::now();
  ResiduePairAudit residue23, residue25, residue35;
  audit_residue_pair(
      residue23, residue_capacity, residue_image[0], residue_image[1], residue_pair[0]);
  audit_residue_pair(
      residue25, residue_capacity, residue_image[0], residue_image[2], residue_pair[1]);
  audit_residue_pair(
      residue35, residue_capacity, residue_image[1], residue_image[2], residue_pair[2]);

  std::ofstream out(argv[2]);
  if (!out) throw std::runtime_error("cannot open output JSON");
  out << "{\n"
      << "  \"limit\": " << limit << ",\n"
      << "  \"threads\": " << threads << ",\n"
      << "  \"orbit_count\": " << count << ",\n"
      << "  \"image_sizes\": {\"2\": " << image_size[0]
      << ", \"3\": " << image_size[1] << ", \"5\": " << image_size[2] << "},\n"
      << "  \"triple_intersection\": " << triple << ",\n"
      << "  \"collision_tax\": " << collision_tax << ",\n"
      << "  \"pair_audits\": {\n";
  write_pair(out, "23", p23); out << ",\n";
  write_pair(out, "25", p25); out << ",\n";
  write_pair(out, "35", p35); out << "\n  },\n"
      << "  \"residue_30_pair_audits\": {\n";
  write_residue_pair(out, "23", residue23); out << ",\n";
  write_residue_pair(out, "25", residue25); out << ",\n";
  write_residue_pair(out, "35", residue35); out << "\n  },\n"
      << "  \"quadratic_tax_audit\": {\n"
      << "    \"inequality\": \"X*Delta(X) <= 3*C(X)^2\",\n"
      << "    \"failures\": " << quadratic_failures << ",\n"
      << "    \"first_failure\": " << quadratic_first_failure << ",\n"
      << "    \"last_failure\": " << quadratic_last_failure << ",\n"
      << "    \"worst_x\": " << quadratic_worst_x << ",\n"
      << "    \"worst_excess\": \"" << decimal(quadratic_worst_excess) << "\"\n"
      << "  },\n"
      << "  \"generation_seconds\": " << std::fixed << std::setprecision(6)
      << std::chrono::duration<double>(generated - started).count() << ",\n"
      << "  \"audit_seconds\": "
      << std::chrono::duration<double>(audited - generated).count() << "\n"
      << "}\n";
  std::cout << "wrote " << argv[2] << "\n";
}
