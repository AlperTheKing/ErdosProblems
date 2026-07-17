#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

using u32 = std::uint32_t;
using u64 = std::uint64_t;

namespace {

struct Bits {
  u64 modulus = 1;
  std::vector<u64> words;
};

struct EdgeProduct {
  u64 product;
  u32 left;
  u32 right;
};

static_assert(sizeof(EdgeProduct) == 16);

std::size_t state_index(int a, int b, int c, int B, int C) {
  return (static_cast<std::size_t>(a) * (B + 1) + b) * (C + 1) + c;
}

u64 ipow(u64 base, int exponent) {
  u64 answer = 1;
  for (int i = 0; i < exponent; ++i) {
    if (answer > std::numeric_limits<u64>::max() / base) {
      throw std::overflow_error("integer power overflow");
    }
    answer *= base;
  }
  return answer;
}

void set_bit(Bits& bits, u64 value) {
  bits.words[static_cast<std::size_t>(value >> 6)] |= u64{1} << (value & 63);
}

template <class F>
void for_each_bit(const Bits& bits, F&& visit) {
  for (std::size_t block = 0; block < bits.words.size(); ++block) {
    u64 word = bits.words[block];
    while (word != 0) {
      const unsigned shift = std::countr_zero(word);
      visit((static_cast<u64>(block) << 6) + shift);
      word &= word - 1;
    }
  }
}

std::vector<u64> exact_offsets() {
  constexpr int A = 6;
  constexpr int B = 4;
  constexpr int C = 2;
  std::vector<Bits> states(static_cast<std::size_t>(A + 1) * (B + 1) * (C + 1));
  for (int total = 0; total <= A + B + C; ++total) {
    for (int a = 0; a <= A; ++a) {
      for (int b = 0; b <= B; ++b) {
        const int c = total - a - b;
        if (c < 0 || c > C) continue;
        Bits& target = states[state_index(a, b, c, B, C)];
        target.modulus = ipow(2, a) * ipow(3, b) * ipow(5, c);
        target.words.assign(static_cast<std::size_t>((target.modulus + 63) / 64), 0);
        if (total == 0) {
          set_bit(target, 0);
          continue;
        }
        const auto add_parent = [&](int pa, int pb, int pc, u64 multiplier, u64 addend) {
          const Bits& parent = states[state_index(pa, pb, pc, B, C)];
          for_each_bit(parent, [&](u64 d) { set_bit(target, multiplier * d + addend); });
        };
        if (a > 0) add_parent(a - 1, b, c, 2, 0);
        if (b > 0) add_parent(a, b - 1, c, 3, 1);
        if (c > 0) add_parent(a, b, c - 1, 5, 3);
      }
    }
  }
  const Bits& target = states[state_index(A, B, C, B, C)];
  std::vector<u64> result;
  for_each_bit(target, [&](u64 d) { result.push_back(d); });
  return result;
}

void write_edge(std::ostream& out, const EdgeProduct& edge, const std::vector<u64>& ds,
                const std::vector<u64>& left, const std::vector<u64>& right) {
  const std::size_t x = edge.left;
  const std::size_t y = edge.right;
  out << "{\"left_index\":" << x << ",\"right_index\":" << y
      << ",\"left_offset\":" << ds[x] << ",\"right_offset\":" << ds[y]
      << ",\"u\":" << left[x] << ",\"v\":" << right[y] << "}";
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2 || argc > 3) {
    std::cerr << "usage: C111_collision_extract OUTPUT.json [THREADS]\n";
    return 2;
  }
#ifdef _OPENMP
  if (argc == 3) omp_set_num_threads(std::stoi(argv[2]));
#else
  (void)argc;
#endif

  constexpr u64 Q = 360;
  constexpr int k = 2;
  const u64 scale = ipow(Q, k);
  const std::vector<u64> all_offsets = exact_offsets();
  if (all_offsets.size() != 13068) throw std::runtime_error("unexpected D_2 size");

  std::vector<u64> selected_offsets;
  std::vector<u64> left;
  std::vector<u64> right;
  for (u64 d : all_offsets) {
    const u64 h = 8 * scale + d + 1;
    if (h % 3 != 2) continue;
    selected_offsets.push_back(d);
    left.push_back(2 * h - 1);
    right.push_back(3 * h - 1);
  }
  if (left.size() != 7779 || right.size() != left.size()) {
    throw std::runtime_error("unexpected selected layer size");
  }

  const u64 edge_count = static_cast<u64>(left.size()) * static_cast<u64>(right.size());
  std::vector<EdgeProduct> products(static_cast<std::size_t>(edge_count));
#pragma omp parallel for schedule(static)
  for (std::int64_t x = 0; x < static_cast<std::int64_t>(left.size()); ++x) {
    const u64 row = static_cast<u64>(x) * static_cast<u64>(right.size());
    for (std::size_t y = 0; y < right.size(); ++y) {
      products[static_cast<std::size_t>(row + y)] = {
          left[static_cast<std::size_t>(x)] * right[y], static_cast<u32>(x),
          static_cast<u32>(y)};
    }
  }
  std::sort(products.begin(), products.end(), [](const EdgeProduct& x, const EdgeProduct& y) {
    if (x.product != y.product) return x.product < y.product;
    if (x.left != y.left) return x.left < y.left;
    return x.right < y.right;
  });

  std::ofstream out(argv[1]);
  if (!out) throw std::runtime_error("cannot open output");
  out << "{\n  \"ray\":[3,2,1],\n  \"Q\":360,\n  \"K\":4,\n"
      << "  \"channel\":[2,2],\n  \"offset_count\":" << all_offsets.size()
      << ",\n  \"selected_residue\":2,\n  \"selected_size\":" << left.size()
      << ",\n  \"edges\":" << edge_count << ",\n  \"fibres\":[\n";

  bool first_fibre = true;
  u64 support = 0;
  u64 repeated_fibres = 0;
  u64 repeated_edge_mass = 0;
  u64 max_multiplicity = 0;
  std::array<u64, 8> histogram{};
  for (std::size_t begin = 0; begin < products.size();) {
    std::size_t end = begin + 1;
    while (end < products.size() && products[end].product == products[begin].product) ++end;
    const u64 multiplicity = static_cast<u64>(end - begin);
    ++support;
    max_multiplicity = std::max(max_multiplicity, multiplicity);
    if (multiplicity >= histogram.size()) throw std::runtime_error("histogram bound exceeded");
    ++histogram[static_cast<std::size_t>(multiplicity)];
    if (multiplicity > 1) {
      ++repeated_fibres;
      repeated_edge_mass += multiplicity;
      if (!first_fibre) out << ",\n";
      first_fibre = false;
      out << "    {\"product\":" << products[begin].product << ",\"edges\":[";
      for (std::size_t pos = begin; pos < end; ++pos) {
        if (pos != begin) out << ',';
        if (products[pos].product != left[products[pos].left] * right[products[pos].right]) {
          throw std::runtime_error("edge replay failed");
        }
        write_edge(out, products[pos], selected_offsets, left, right);
      }
      out << "]}";
    }
    begin = end;
  }
  if (support != 60496906 || repeated_fibres != 15931 || max_multiplicity != 3 ||
      histogram[1] != 60480975 || histogram[2] != 15927 || histogram[3] != 4) {
    throw std::runtime_error("published census mismatch");
  }
  out << "\n  ],\n  \"support\":" << support << ",\n  \"repeated_fibres\":"
      << repeated_fibres << ",\n  \"repeated_edge_mass\":" << repeated_edge_mass
      << ",\n  \"max_multiplicity\":" << max_multiplicity
      << ",\n  \"histogram\":{\"1\":" << histogram[1] << ",\"2\":" << histogram[2]
      << ",\"3\":" << histogram[3] << "}\n}\n";
  std::cout << "edges " << edge_count << "\nrepeated_fibres " << repeated_fibres
            << "\nrepeated_edge_mass " << repeated_edge_mass << "\n";
  return 0;
}
