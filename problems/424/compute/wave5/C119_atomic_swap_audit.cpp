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
#include <utility>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

using u32 = std::uint32_t;
using u64 = std::uint64_t;

namespace {

constexpr u64 Q = 360;
constexpr u64 CODE_MASK = (u64{1} << 28) - 1;

struct Bits {
  u64 modulus = 1;
  std::vector<u64> words;
};

struct Layer {
  int k = 0;
  int residue = 0;
  std::vector<u64> offsets;
  std::vector<u64> left;
  std::vector<u64> right;
};

struct EdgeProduct {
  u64 product;
  u64 code;
};

struct DecodedEdge {
  int layer;
  u32 left_index;
  u32 right_index;
  u64 left_offset;
  u64 right_offset;
  u64 u;
  u64 v;
};

struct Witness {
  bool present = false;
  int K = 0;
  u64 product = 0;
  std::vector<DecodedEdge> fibre;
  std::size_t first = 0;
  std::size_t second = 0;
  u64 g = 0;
  u64 a = 0;
  u64 b = 0;
  u64 c = 0;
};

struct Summary {
  int K = 0;
  u64 edges = 0;
  u64 support = 0;
  u64 repeated_fibres = 0;
  u64 repeated_edge_mass = 0;
  u64 collision_pairs = 0;
  u64 atomic_pairs = 0;
  u64 non_atomic_pairs = 0;
  u64 bilateral_non_atomic_pairs = 0;
  u64 max_multiplicity = 0;
  u64 max_atomic_degree = 0;
  std::array<u64, 16> histogram{};
};

static_assert(sizeof(EdgeProduct) == 16);

std::size_t state_index(int a, int b, int c, int B, int C) {
  return (static_cast<std::size_t>(a) * static_cast<std::size_t>(B + 1) +
          static_cast<std::size_t>(b)) *
             static_cast<std::size_t>(C + 1) +
         static_cast<std::size_t>(c);
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

std::vector<u64> exact_offsets(int k) {
  const int A = 3 * k;
  const int B = 2 * k;
  const int C = k;
  std::vector<Bits> states(static_cast<std::size_t>(A + 1) *
                           static_cast<std::size_t>(B + 1) *
                           static_cast<std::size_t>(C + 1));
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
  std::vector<u64> result;
  for_each_bit(states[state_index(A, B, C, B, C)],
               [&](u64 d) { result.push_back(d); });
  return result;
}

Layer make_layer(int k) {
  Layer layer;
  layer.k = k;
  const u64 scale = ipow(Q, k);
  const std::vector<u64> offsets = exact_offsets(k);
  u64 count_zero = 0;
  u64 count_two = 0;
  for (u64 d : offsets) {
    const u64 residue = (8 * scale + d + 1) % 3;
    if (residue == 0) ++count_zero;
    if (residue == 2) ++count_two;
  }
  layer.residue = count_two >= count_zero ? 2 : 0;
  for (u64 d : offsets) {
    const u64 h = 8 * scale + d + 1;
    if (h % 3 != static_cast<u64>(layer.residue)) continue;
    layer.offsets.push_back(d);
    layer.left.push_back(layer.residue == 2 ? 2 * h - 1 : 4 * h - 3);
    layer.right.push_back(3 * h - 1);
  }
  return layer;
}

u64 encode(int layer, u32 left_index, u32 right_index) {
  return (static_cast<u64>(layer) << 56) |
         (static_cast<u64>(left_index) << 28) | static_cast<u64>(right_index);
}

void decode_code(u64 code, int& layer, u32& left_index, u32& right_index) {
  layer = static_cast<int>(code >> 56);
  left_index = static_cast<u32>((code >> 28) & CODE_MASK);
  right_index = static_cast<u32>(code & CODE_MASK);
}

DecodedEdge decode_edge(const EdgeProduct& edge, int K,
                        const std::array<Layer, 3>& layers) {
  int layer = 0;
  u32 x = 0;
  u32 y = 0;
  decode_code(edge.code, layer, x, y);
  const Layer& left_layer = layers[static_cast<std::size_t>(layer)];
  const Layer& right_layer = layers[static_cast<std::size_t>(K - layer)];
  return {layer,
          x,
          y,
          left_layer.offsets.at(x),
          right_layer.offsets.at(y),
          left_layer.left.at(x),
          right_layer.right.at(y)};
}

int omega_capped_two(u64 n) {
  int omega = 0;
  if ((n & 1U) == 0) {
    ++omega;
    while ((n & 1U) == 0) n >>= 1;
  }
  for (u64 p = 3; p <= n / p; p += 2) {
    if (n % p != 0) continue;
    ++omega;
    if (omega >= 2) return omega;
    do {
      n /= p;
    } while (n % p == 0);
  }
  if (n > 1) ++omega;
  return omega;
}

std::vector<std::pair<u64, int>> factor(u64 n) {
  std::vector<std::pair<u64, int>> result;
  for (u64 p = 2; p <= n / p; p += (p == 2 ? 1 : 2)) {
    if (n % p != 0) continue;
    int exponent = 0;
    do {
      n /= p;
      ++exponent;
    } while (n % p == 0);
    result.emplace_back(p, exponent);
  }
  if (n > 1) result.emplace_back(n, 1);
  return result;
}

void store_witness(Witness& target, int K, u64 product,
                   const std::vector<DecodedEdge>& fibre, std::size_t first,
                   std::size_t second) {
  const u64 g = std::gcd(fibre[first].u, fibre[second].u);
  const u64 a = fibre[first].u / g;
  const u64 b = fibre[second].u / g;
  if (fibre[first].v % b != 0 || fibre[second].v % a != 0) {
    throw std::runtime_error("coprime swap divisibility failed");
  }
  const u64 c = fibre[first].v / b;
  if (fibre[second].v / a != c || g * a * b * c != product) {
    throw std::runtime_error("coprime swap replay failed");
  }
  target = {true, K, product, fibre, first, second, g, a, b, c};
}

Summary scan_K(int K, const std::array<Layer, 3>& layers, Witness& first_non_atomic,
               Witness& first_bilateral) {
  const int lo = (K + 2) / 3;
  const int hi = (2 * K) / 3;
  u64 edge_count = 0;
  for (int i = lo; i <= hi; ++i) {
    edge_count += static_cast<u64>(layers[static_cast<std::size_t>(i)].left.size()) *
                  static_cast<u64>(layers[static_cast<std::size_t>(K - i)].right.size());
  }
  std::vector<EdgeProduct> products(static_cast<std::size_t>(edge_count));
  u64 base = 0;
  for (int i = lo; i <= hi; ++i) {
    const Layer& left_layer = layers[static_cast<std::size_t>(i)];
    const Layer& right_layer = layers[static_cast<std::size_t>(K - i)];
    const u64 width = static_cast<u64>(right_layer.right.size());
#pragma omp parallel for schedule(static)
    for (std::int64_t x = 0; x < static_cast<std::int64_t>(left_layer.left.size()); ++x) {
      const u64 row = base + static_cast<u64>(x) * width;
      for (u32 y = 0; y < right_layer.right.size(); ++y) {
        products[static_cast<std::size_t>(row + y)] = {
            left_layer.left[static_cast<std::size_t>(x)] * right_layer.right[y],
            encode(i, static_cast<u32>(x), y)};
      }
    }
    base += static_cast<u64>(left_layer.left.size()) * width;
  }
  std::sort(products.begin(), products.end(), [](const EdgeProduct& x, const EdgeProduct& y) {
    if (x.product != y.product) return x.product < y.product;
    return x.code < y.code;
  });

  Summary summary;
  summary.K = K;
  summary.edges = edge_count;
  for (std::size_t begin = 0; begin < products.size();) {
    std::size_t end = begin + 1;
    while (end < products.size() && products[end].product == products[begin].product) ++end;
    const u64 multiplicity = static_cast<u64>(end - begin);
    ++summary.support;
    summary.max_multiplicity = std::max(summary.max_multiplicity, multiplicity);
    if (multiplicity >= summary.histogram.size()) {
      throw std::runtime_error("histogram bound exceeded");
    }
    ++summary.histogram[static_cast<std::size_t>(multiplicity)];
    if (multiplicity > 1) {
      ++summary.repeated_fibres;
      summary.repeated_edge_mass += multiplicity;
      std::vector<DecodedEdge> fibre;
      fibre.reserve(static_cast<std::size_t>(multiplicity));
      for (std::size_t pos = begin; pos < end; ++pos) {
        DecodedEdge decoded = decode_edge(products[pos], K, layers);
        if (decoded.u * decoded.v != products[pos].product) {
          throw std::runtime_error("edge product replay failed");
        }
        fibre.push_back(decoded);
      }
      std::vector<u64> atomic_degree(static_cast<std::size_t>(multiplicity), 0);
      for (std::size_t x = 0; x < fibre.size(); ++x) {
        for (std::size_t y = x + 1; y < fibre.size(); ++y) {
          ++summary.collision_pairs;
          const u64 g = std::gcd(fibre[x].u, fibre[y].u);
          const u64 a = fibre[x].u / g;
          const u64 b = fibre[y].u / g;
          const int omega_a = omega_capped_two(a);
          const int omega_b = omega_capped_two(b);
          const bool atomic = omega_a <= 1 && omega_b <= 1;
          if (atomic) {
            ++summary.atomic_pairs;
            ++atomic_degree[x];
            ++atomic_degree[y];
          } else {
            ++summary.non_atomic_pairs;
            if (!first_non_atomic.present) {
              store_witness(first_non_atomic, K, products[begin].product, fibre, x, y);
            }
            if (omega_a >= 2 && omega_b >= 2) {
              ++summary.bilateral_non_atomic_pairs;
              if (!first_bilateral.present) {
                store_witness(first_bilateral, K, products[begin].product, fibre, x, y);
              }
            }
          }
        }
      }
      for (u64 degree : atomic_degree) {
        summary.max_atomic_degree = std::max(summary.max_atomic_degree, degree);
      }
    }
    begin = end;
  }
  return summary;
}

void write_factorization(std::ostream& out, u64 n) {
  out << '[';
  const auto factors = factor(n);
  for (std::size_t i = 0; i < factors.size(); ++i) {
    if (i != 0) out << ',';
    out << '[' << factors[i].first << ',' << factors[i].second << ']';
  }
  out << ']';
}

void write_edge(std::ostream& out, const DecodedEdge& edge) {
  out << "{\"layer\":" << edge.layer << ",\"left_index\":" << edge.left_index
      << ",\"right_index\":" << edge.right_index
      << ",\"left_offset\":" << edge.left_offset
      << ",\"right_offset\":" << edge.right_offset << ",\"u\":" << edge.u
      << ",\"v\":" << edge.v << '}';
}

void write_witness(std::ostream& out, const Witness& witness) {
  if (!witness.present) {
    out << "null";
    return;
  }
  out << "{\"K\":" << witness.K << ",\"product\":" << witness.product
      << ",\"multiplicity\":" << witness.fibre.size() << ",\"pair_indices\":["
      << witness.first << ',' << witness.second << "],\"fibre\":[";
  for (std::size_t i = 0; i < witness.fibre.size(); ++i) {
    if (i != 0) out << ',';
    write_edge(out, witness.fibre[i]);
  }
  out << "],\"normal_form\":{\"g\":" << witness.g << ",\"a\":" << witness.a
      << ",\"b\":" << witness.b << ",\"c\":" << witness.c
      << ",\"factor_a\":";
  write_factorization(out, witness.a);
  out << ",\"factor_b\":";
  write_factorization(out, witness.b);
  out << "}}";
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2 || argc > 3) {
    std::cerr << "usage: C119_atomic_swap_audit OUTPUT.json [THREADS]\n";
    return 2;
  }
#ifdef _OPENMP
  if (argc == 3) omp_set_num_threads(std::stoi(argv[2]));
#else
  (void)argc;
#endif

  std::array<Layer, 3> layers;
  layers[1] = make_layer(1);
  layers[2] = make_layer(2);
  if (layers[1].offsets.size() != 36 || layers[2].offsets.size() != 7779 ||
      layers[1].residue != 2 || layers[2].residue != 2) {
    throw std::runtime_error("published layer data mismatch");
  }

  Witness first_non_atomic;
  Witness first_bilateral;
  std::vector<Summary> summaries;
  for (int K = 2; K <= 4; ++K) {
    summaries.push_back(scan_K(K, layers, first_non_atomic, first_bilateral));
    std::cout << "K " << K << " edges " << summaries.back().edges << " support "
              << summaries.back().support << " non_atomic_pairs "
              << summaries.back().non_atomic_pairs << '\n';
  }

  if (summaries[0].edges != 1296 || summaries[1].edges != 560088 ||
      summaries[2].edges != 60512841 || summaries[2].support != 60496906 ||
      summaries[2].histogram[1] != 60480975 || summaries[2].histogram[2] != 15927 ||
      summaries[2].histogram[3] != 4) {
    throw std::runtime_error("published product census mismatch");
  }

  std::ofstream out(argv[1]);
  if (!out) throw std::runtime_error("cannot open output");
  out << "{\n  \"ray\":[3,2,1],\n  \"Q\":360,\n  \"atomic_definition\":\"omega(a)<=1 and omega(b)<=1\",\n"
      << "  \"layers\":{\"1\":{\"selected_residue\":" << layers[1].residue
      << ",\"selected_size\":" << layers[1].offsets.size()
      << "},\"2\":{\"selected_residue\":" << layers[2].residue
      << ",\"selected_size\":" << layers[2].offsets.size() << "}},\n"
      << "  \"summaries\":[\n";
  for (std::size_t index = 0; index < summaries.size(); ++index) {
    const Summary& s = summaries[index];
    if (index != 0) out << ",\n";
    out << "    {\"K\":" << s.K << ",\"edges\":" << s.edges
        << ",\"support\":" << s.support << ",\"repeated_fibres\":"
        << s.repeated_fibres << ",\"repeated_edge_mass\":" << s.repeated_edge_mass
        << ",\"collision_pairs\":" << s.collision_pairs
        << ",\"atomic_pairs\":" << s.atomic_pairs
        << ",\"non_atomic_pairs\":" << s.non_atomic_pairs
        << ",\"bilateral_non_atomic_pairs\":" << s.bilateral_non_atomic_pairs
        << ",\"max_multiplicity\":" << s.max_multiplicity
        << ",\"max_atomic_degree\":" << s.max_atomic_degree << ",\"histogram\":{";
    bool first = true;
    for (std::size_t m = 1; m < s.histogram.size(); ++m) {
      if (s.histogram[m] == 0) continue;
      if (!first) out << ',';
      first = false;
      out << '\"' << m << "\":" << s.histogram[m];
    }
    out << "}}";
  }
  out << "\n  ],\n  \"AO1_all_collision_pairs_atomic\":"
      << (first_non_atomic.present ? "false" : "true")
      << ",\n  \"AO2_max_atomic_degree_at_most_2\":";
  bool ao2 = true;
  for (const Summary& summary : summaries) ao2 = ao2 && summary.max_atomic_degree <= 2;
  out << (ao2 ? "true" : "false") << ",\n  \"first_non_atomic_witness\":";
  write_witness(out, first_non_atomic);
  out << ",\n  \"first_bilateral_non_atomic_witness\":";
  write_witness(out, first_bilateral);
  out << "\n}\n";
  return 0;
}
