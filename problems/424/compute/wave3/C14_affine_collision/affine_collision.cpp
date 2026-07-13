#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using u32 = std::uint32_t;
using u64 = std::uint64_t;
using u128 = unsigned __int128;
using i128 = __int128;

constexpr std::array<u32, 10> kA = {3, 9, 27, 33, 51, 69, 81, 84, 87, 99};
constexpr std::array<u32, 13> kB = {2, 5, 14, 17, 26, 41, 44, 50, 53, 65, 77, 80, 98};
constexpr u64 kWNumerator = 12246282477409697ULL;
constexpr u64 kWDenominator = 11187720423079200ULL;

std::string show_u128(u128 value) {
  if (value == 0) return "0";
  std::string result;
  while (value != 0) {
    result.push_back(static_cast<char>('0' + value % 10));
    value /= 10;
  }
  std::reverse(result.begin(), result.end());
  return result;
}

std::string show_i128(i128 value) {
  if (value >= 0) return show_u128(static_cast<u128>(value));
  return "-" + show_u128(static_cast<u128>(-value));
}

u128 gcd_u128(u128 left, u128 right) {
  while (right != 0) {
    const u128 remainder = left % right;
    left = right;
    right = remainder;
  }
  return left;
}

struct Fraction {
  i128 numerator;
  u128 denominator;
};

Fraction reduced_fraction(i128 numerator, u128 denominator) {
  if (denominator == 0) throw std::logic_error("zero fraction denominator");
  if (numerator == 0) return {0, 1};
  const u128 magnitude = numerator < 0 ? static_cast<u128>(-numerator)
                                       : static_cast<u128>(numerator);
  const u128 divisor = gcd_u128(magnitude, denominator);
  return {numerator / static_cast<i128>(divisor), denominator / divisor};
}

std::string decimal_truncated(const Fraction& fraction, unsigned places = 15) {
  const bool negative = fraction.numerator < 0;
  u128 magnitude = negative ? static_cast<u128>(-fraction.numerator)
                            : static_cast<u128>(fraction.numerator);
  const u128 whole = magnitude / fraction.denominator;
  u128 remainder = magnitude % fraction.denominator;
  std::string result = negative ? "-" : "";
  result += show_u128(whole);
  result.push_back('.');
  for (unsigned index = 0; index < places; ++index) {
    remainder *= 10;
    result.push_back(static_cast<char>('0' + remainder / fraction.denominator));
    remainder %= fraction.denominator;
  }
  return result;
}

struct UnsignedFraction {
  u128 numerator;
  u128 denominator;
};

UnsignedFraction add_fraction(UnsignedFraction left, u128 numerator, u128 denominator) {
  left.numerator = left.numerator * denominator + numerator * left.denominator;
  left.denominator *= denominator;
  const u128 divisor = gcd_u128(left.numerator, left.denominator);
  left.numerator /= divisor;
  left.denominator /= divisor;
  return left;
}

void verify_weight() {
  UnsignedFraction weight{0, 1};
  for (const u32 a : kA) weight = add_fraction(weight, 1, a);
  for (const u32 b : kB) weight = add_fraction(weight, 1, 2 * b);
  if (weight.numerator != kWNumerator || weight.denominator != kWDenominator) {
    throw std::logic_error("map list does not reproduce the certified weight W");
  }
}

std::vector<u32> smallest_prime_factors(u32 limit) {
  std::vector<u32> spf(static_cast<std::size_t>(limit) + 1, 0);
  for (u32 prime = 2; prime <= limit / prime; ++prime) {
    if (spf[prime] != 0) continue;
    for (u64 multiple = u64(prime) * prime; multiple <= limit; multiple += prime) {
      u32& cell = spf[static_cast<std::size_t>(multiple)];
      if (cell == 0) cell = prime;
    }
  }
  return spf;
}

bool generated(u32 n,
               const std::vector<u32>& spf,
               const std::vector<std::uint8_t>& in_g,
               std::vector<u32>& divisors) {
  const u32 product = n + 1;
  u32 remaining = product;
  std::array<std::pair<u32, u32>, 16> factors{};
  std::size_t factor_count = 0;
  while (remaining > 1) {
    const u32 prime = spf[remaining] == 0 ? remaining : spf[remaining];
    u32 exponent = 0;
    do {
      remaining /= prime;
      ++exponent;
    } while (remaining > 1 && remaining % prime == 0);
    if (factor_count == factors.size()) throw std::logic_error("factor buffer exhausted");
    factors[factor_count++] = {prime, exponent};
  }

  divisors.clear();
  divisors.push_back(1);
  for (std::size_t factor_index = 0; factor_index < factor_count; ++factor_index) {
    const auto [prime, exponent] = factors[factor_index];
    const std::size_t old_size = divisors.size();
    u64 prime_power = 1;
    for (u32 power = 1; power <= exponent; ++power) {
      prime_power *= prime;
      for (std::size_t index = 0; index < old_size; ++index) {
        const u64 divisor = u64(divisors[index]) * prime_power;
        // This retains exactly the divisors at most sqrt(product), using integers only.
        if (divisor <= product / divisor) divisors.push_back(static_cast<u32>(divisor));
      }
    }
  }

  for (const u32 divisor : divisors) {
    if (divisor < 2) continue;
    const u32 quotient = product / divisor;
    if (divisor < quotient && in_g[divisor] && in_g[quotient]) return true;
  }
  return false;
}

std::vector<std::uint8_t> generate_closure(u32 limit, u64& member_count) {
  auto spf = smallest_prime_factors(limit + 1);
  std::vector<std::uint8_t> in_g(static_cast<std::size_t>(limit) + 1, 0);
  member_count = 0;
  if (limit >= 2) {
    in_g[2] = 1;
    ++member_count;
  }
  if (limit >= 3) {
    in_g[3] = 1;
    ++member_count;
  }
  std::vector<u32> divisors;
  divisors.reserve(256);
  for (u32 n = 4; n <= limit; ++n) {
    if (generated(n, spf, in_g, divisors)) {
      in_g[n] = 1;
      ++member_count;
    }
  }
  if (limit >= 24 && (in_g[8] || in_g[24])) {
    throw std::logic_error("distinct-input sentinels 8 and 24 must be absent");
  }
  return in_g;
}

struct Map {
  char kind;
  u32 operand;
  u32 slope;
  u32 subtract;

  u64 image(u32 parent) const {
    return u64(slope) * parent - subtract;
  }

  u64 parent_cutoff(u64 x) const {
    if (kind == 'F') return x / operand + 1;
    return (x + u64(3) * operand) / (u64(2) * operand);
  }
};

std::vector<Map> maps() {
  std::vector<Map> result;
  result.reserve(kA.size() + kB.size());
  for (const u32 a : kA) result.push_back({'F', a, a, a});
  for (const u32 b : kB) result.push_back({'H', b, 2 * b, 3 * b});
  return result;
}

std::vector<u64> checkpoints(u64 limit) {
  std::vector<u64> result;
  for (u64 point = 1000; point <= limit;) {
    result.push_back(point);
    if (point > limit / 10) break;
    point *= 10;
  }
  if (result.empty() || result.back() != limit) result.push_back(limit);
  return result;
}

u64 count_to(const std::vector<u32>& values, u64 cutoff) {
  if (cutoff >= std::numeric_limits<u32>::max()) return values.size();
  return static_cast<u64>(std::upper_bound(values.begin(), values.end(),
                                            static_cast<u32>(cutoff)) -
                          values.begin());
}

struct Node {
  u64 value;
  std::size_t map_index;
  std::size_t parent_index;
};

struct NodeGreater {
  bool operator()(const Node& left, const Node& right) const {
    if (left.value != right.value) return left.value > right.value;
    return left.map_index > right.map_index;
  }
};

struct Row {
  u64 x;
  u64 q;
  u64 parent_mass;
  u64 union_size;
  u64 collision_tax;
  u128 energy;
};

std::vector<Row> affine_census(u64 limit,
                               const std::vector<u32>& support,
                               const std::vector<Map>& affine_maps) {
  std::priority_queue<Node, std::vector<Node>, NodeGreater> heap;
  if (!support.empty()) {
    for (std::size_t map_index = 0; map_index < affine_maps.size(); ++map_index) {
      const u64 value = affine_maps[map_index].image(support.front());
      if (value <= limit) heap.push({value, map_index, 0});
    }
  }

  u64 parent_mass = 0;
  u64 union_size = 0;
  u128 energy = 0;
  std::vector<Row> rows;
  for (const u64 point : checkpoints(limit)) {
    while (!heap.empty() && heap.top().value <= point) {
      const u64 value = heap.top().value;
      u64 multiplicity = 0;
      do {
        Node node = heap.top();
        heap.pop();
        ++multiplicity;
        ++node.parent_index;
        if (node.parent_index < support.size()) {
          const u64 next = affine_maps[node.map_index].image(support[node.parent_index]);
          if (next <= limit) heap.push({next, node.map_index, node.parent_index});
        }
      } while (!heap.empty() && heap.top().value == value);
      parent_mass += multiplicity;
      ++union_size;
      energy += u128(multiplicity) * multiplicity;
    }

    u64 formula_mass = 0;
    for (const Map& map : affine_maps) {
      formula_mass += count_to(support, map.parent_cutoff(point));
    }
    if (formula_mass != parent_mass) {
      throw std::logic_error("stream mass disagrees with the exact parent-mass formula");
    }
    const u64 q = count_to(support, point);
    rows.push_back({point, q, parent_mass, union_size, parent_mass - union_size, energy});
  }
  return rows;
}

void verify_c07_rows(const std::vector<Row>& rows) {
  struct Expected {
    u64 x;
    u64 q;
    u64 mass;
    u64 union_size;
    u64 collision_tax;
    u64 energy;
  };
  constexpr std::array<Expected, 3> expected = {{{1000, 118, 113, 93, 20, 153},
                                                  {10000, 1591, 1350, 1188, 162, 1688},
                                                  {100000, 20391, 17905, 15367, 2538, 23265}}};
  for (const Expected& benchmark : expected) {
    const auto found = std::find_if(rows.begin(), rows.end(), [&](const Row& row) {
      return row.x == benchmark.x;
    });
    if (found == rows.end()) continue;
    if (found->q != benchmark.q || found->parent_mass != benchmark.mass ||
        found->union_size != benchmark.union_size ||
        found->collision_tax != benchmark.collision_tax ||
        found->energy != benchmark.energy) {
      throw std::logic_error("C07 benchmark mismatch at X=" + std::to_string(benchmark.x));
    }
  }
}

void write_fraction(std::ostream& out, const Fraction& fraction) {
  out << "{\"numerator\": \"" << show_i128(fraction.numerator)
      << "\", \"denominator\": \"" << show_u128(fraction.denominator)
      << "\", \"decimal_15_truncated\": \"" << decimal_truncated(fraction) << "\"}";
}

void write_json(const std::string& path,
                u64 limit,
                u32 closure_limit,
                u64 closure_count,
                std::size_t g0_count,
                std::size_t g2_count,
                u64 product_pair_count,
                const std::vector<Map>& affine_maps,
                const std::vector<Row>& rows,
                u64 closure_ms,
                u64 support_ms,
                u64 affine_ms) {
  std::ofstream out(path);
  if (!out) throw std::runtime_error("cannot open output path: " + path);
  out << "{\n"
      << "  \"schema_version\": 1,\n"
      << "  \"arithmetic\": \"exact integer, complete unthinned support and all 23 labeled maps\",\n"
      << "  \"limit\": " << limit << ",\n"
      << "  \"threads_used\": 1,\n"
      << "  \"closure_limit\": " << closure_limit << ",\n"
      << "  \"closure_count_to_closure_limit\": " << closure_count << ",\n"
      << "  \"relevant_g0_count\": " << g0_count << ",\n"
      << "  \"relevant_g2_count\": " << g2_count << ",\n"
      << "  \"cross_color_pair_count_to_limit\": " << product_pair_count << ",\n"
      << "  \"W\": {\"numerator\": \"" << kWNumerator
      << "\", \"denominator\": \"" << kWDenominator << "\"},\n"
      << "  \"collision_threshold_1_minus_1_over_W\": {\"numerator\": \""
      << (kWNumerator - kWDenominator) << "\", \"denominator\": \""
      << kWNumerator << "\"},\n"
      << "  \"maps\": [\n";
  for (std::size_t index = 0; index < affine_maps.size(); ++index) {
    const Map& map = affine_maps[index];
    out << "    {\"kind\": \"" << map.kind << "\", \"operand\": " << map.operand
        << ", \"slope\": " << map.slope << ", \"subtract\": " << map.subtract << "}"
        << (index + 1 == affine_maps.size() ? "\n" : ",\n");
  }
  out << "  ],\n"
      << "  \"checks\": {\"C07_rows_through_1e5\": true, "
      << "\"stream_mass_equals_parent_formula_at_every_checkpoint\": true, "
      << "\"distinct_input_sentinels_8_24_absent\": true},\n"
      << "  \"milliseconds\": {\"closure\": " << closure_ms
      << ", \"support\": " << support_ms << ", \"affine_merge\": " << affine_ms << "},\n"
      << "  \"checkpoints\": [\n";
  for (std::size_t index = 0; index < rows.size(); ++index) {
    const Row& row = rows[index];
    const Fraction energy_per_mass =
        reduced_fraction(static_cast<i128>(row.energy), row.parent_mass);
    const Fraction energy_excess = reduced_fraction(
        static_cast<i128>(row.energy) * kWDenominator -
            static_cast<i128>(row.parent_mass) * kWNumerator,
        u128(row.parent_mass) * kWDenominator);
    const Fraction tax_per_mass =
        reduced_fraction(row.collision_tax, row.parent_mass);
    const Fraction tax_excess = reduced_fraction(
        static_cast<i128>(row.collision_tax) * kWNumerator -
            static_cast<i128>(row.parent_mass) * (kWNumerator - kWDenominator),
        u128(row.parent_mass) * kWNumerator);
    out << "    {\n"
        << "      \"X\": " << row.x << ", \"Q\": " << row.q
        << ", \"parent_mass_M\": " << row.parent_mass
        << ", \"union_U\": " << row.union_size
        << ", \"collision_tax_Delta\": " << row.collision_tax
        << ", \"affine_energy_sum_r2\": \"" << show_u128(row.energy) << "\",\n"
        << "      \"affine_energy_over_M\": ";
    write_fraction(out, energy_per_mass);
    out << ",\n      \"affine_energy_over_M_minus_W\": ";
    write_fraction(out, energy_excess);
    out << ",\n      \"Delta_over_M\": ";
    write_fraction(out, tax_per_mass);
    out << ",\n      \"Delta_over_M_minus_1_minus_1_over_W\": ";
    write_fraction(out, tax_excess);
    out << "\n    }" << (index + 1 == rows.size() ? "\n" : ",\n");
  }
  out << "  ]\n}\n";
}

u64 elapsed_ms(std::chrono::steady_clock::time_point start,
               std::chrono::steady_clock::time_point finish) {
  return static_cast<u64>(
      std::chrono::duration_cast<std::chrono::milliseconds>(finish - start).count());
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 3) {
      std::cerr << "usage: affine_collision LIMIT OUTPUT_JSON\n";
      return 2;
    }
    const u64 parsed_limit = std::stoull(argv[1]);
    if (parsed_limit < 1000 || parsed_limit > std::numeric_limits<u32>::max() - 1ULL) {
      throw std::invalid_argument("LIMIT must lie in [1000, UINT32_MAX-1]");
    }
    const u32 limit = static_cast<u32>(parsed_limit);
    const std::string output_path = argv[2];
    verify_weight();
    const std::vector<Map> affine_maps = maps();

    const auto started = std::chrono::steady_clock::now();
    const u32 closure_limit = limit / 2;
    u64 closure_count = 0;
    auto in_g = generate_closure(closure_limit, closure_count);
    const auto closure_finished = std::chrono::steady_clock::now();

    std::vector<u32> g0;
    std::vector<u32> g2;
    for (u32 n = 2; n <= closure_limit; ++n) {
      if (!in_g[n]) continue;
      if (n % 3 == 0) g0.push_back(n);
      if (n % 3 == 2 && n <= limit / 3) g2.push_back(n);
    }
    const std::size_t g0_count = g0.size();
    const std::size_t g2_count = g2.size();
    std::vector<std::uint8_t>().swap(in_g);

    std::vector<std::uint8_t> support_bitmap(static_cast<std::size_t>(limit) + 1, 0);
    u64 product_pair_count = 0;
    for (const u32 a : g0) {
      const u32 factor_limit = limit / a;
      const auto end = std::upper_bound(g2.begin(), g2.end(), factor_limit);
      product_pair_count += static_cast<u64>(end - g2.begin());
      for (auto it = g2.begin(); it != end; ++it) {
        support_bitmap[static_cast<std::size_t>(u64(a) * *it)] = 1;
      }
    }
    const u64 support_count = static_cast<u64>(
        std::count(support_bitmap.begin(), support_bitmap.end(), std::uint8_t{1}));
    std::vector<u32> support;
    support.reserve(static_cast<std::size_t>(support_count));
    for (u32 n = 1; n <= limit; ++n) {
      if (support_bitmap[n]) support.push_back(n);
    }
    std::vector<std::uint8_t>().swap(support_bitmap);
    std::vector<u32>().swap(g0);
    std::vector<u32>().swap(g2);
    const auto support_finished = std::chrono::steady_clock::now();

    const std::vector<Row> rows = affine_census(limit, support, affine_maps);
    verify_c07_rows(rows);
    const auto affine_finished = std::chrono::steady_clock::now();

    write_json(output_path, limit, closure_limit, closure_count,
               g0_count, g2_count, product_pair_count, affine_maps, rows,
               elapsed_ms(started, closure_finished),
               elapsed_ms(closure_finished, support_finished),
               elapsed_ms(support_finished, affine_finished));
    std::cout << "limit=" << limit << " Q=" << rows.back().q
              << " M=" << rows.back().parent_mass
              << " U=" << rows.back().union_size
              << " Delta=" << rows.back().collision_tax
              << " E_aff=" << show_u128(rows.back().energy)
              << " total_ms=" << elapsed_ms(started, affine_finished) << '\n';
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}
