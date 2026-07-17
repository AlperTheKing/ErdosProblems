#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

using u64 = std::uint64_t;
using u128 = unsigned __int128;

namespace {

struct Ray {
  const char* name;
  int a;
  int b;
  int c;
  int kmax;
  int Kmax;
};

struct Bits {
  u64 modulus = 1;
  std::vector<u64> words;
  u64 count = 0;
};

struct Layer {
  int k = 0;
  u64 modulus = 1;
  u64 offset_count = 0;
  int selected_residue = 0;
  std::vector<u64> U;
  std::vector<u64> V;
};

struct LightRow {
  u64 cutoff = 0;
  u64 support = 0;
  u64 edge_mass = 0;
};

struct ProductAudit {
  int K = 0;
  int first_i = 0;
  int last_i = 0;
  u64 scale = 1;
  u64 edges = 0;
  u64 support = 0;
  u64 max_multiplicity = 0;
  u128 energy = 0;
  std::vector<u64> multiplicity_histogram;
  std::vector<LightRow> light;
};

std::string decimal(u128 value) {
  if (value == 0) return "0";
  std::string out;
  while (value != 0) {
    out.push_back(static_cast<char>('0' + value % 10));
    value /= 10;
  }
  std::reverse(out.begin(), out.end());
  return out;
}

u64 checked_mul(u64 x, u64 y) {
  if (y != 0 && x > std::numeric_limits<u64>::max() / y) {
    throw std::overflow_error("uint64 multiplication overflow");
  }
  return x * y;
}

u64 ipow(u64 base, int exponent) {
  u64 out = 1;
  for (int i = 0; i < exponent; ++i) out = checked_mul(out, base);
  return out;
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

std::size_t state_index(int a, int b, int c, int B, int C) {
  return (static_cast<std::size_t>(a) * (B + 1) + b) * (C + 1) + c;
}

std::vector<std::vector<u64>> exact_ray_offsets(const Ray& ray) {
  const int A = ray.a * ray.kmax;
  const int B = ray.b * ray.kmax;
  const int C = ray.c * ray.kmax;
  std::vector<Bits> states(static_cast<std::size_t>(A + 1) * (B + 1) * (C + 1));

  for (int total = 0; total <= A + B + C; ++total) {
    for (int a = 0; a <= A; ++a) {
      for (int b = 0; b <= B; ++b) {
        const int c = total - a - b;
        if (c < 0 || c > C) continue;
        Bits& target = states[state_index(a, b, c, B, C)];
        target.modulus = checked_mul(checked_mul(ipow(2, a), ipow(3, b)), ipow(5, c));
        target.words.assign(static_cast<std::size_t>((target.modulus + 63) / 64), 0);
        if (total == 0) {
          set_bit(target, 0);
        } else {
          const auto add_parent = [&](int pa, int pb, int pc, u64 multiplier, u64 offset) {
            const Bits& parent = states[state_index(pa, pb, pc, B, C)];
            for_each_bit(parent, [&](u64 d) { set_bit(target, multiplier * d + offset); });
          };
          if (a > 0) add_parent(a - 1, b, c, 2, 0);
          if (b > 0) add_parent(a, b - 1, c, 3, 1);
          if (c > 0) add_parent(a, b, c - 1, 5, 3);
        }
        for (u64 word : target.words) target.count += std::popcount(word);
      }
    }
  }

  std::vector<std::vector<u64>> result(static_cast<std::size_t>(ray.kmax + 1));
  result[0].push_back(0);
  for (int k = 1; k <= ray.kmax; ++k) {
    const Bits& target = states[state_index(ray.a * k, ray.b * k, ray.c * k, B, C)];
    result[static_cast<std::size_t>(k)].reserve(static_cast<std::size_t>(target.count));
    for_each_bit(target, [&](u64 d) { result[static_cast<std::size_t>(k)].push_back(d); });
  }
  return result;
}

std::vector<Layer> make_layers(const Ray& ray, const std::vector<std::vector<u64>>& offsets) {
  const u64 Q = checked_mul(checked_mul(ipow(2, ray.a), ipow(3, ray.b)), ipow(5, ray.c));
  std::vector<Layer> layers(static_cast<std::size_t>(ray.kmax + 1));
  for (int k = 1; k <= ray.kmax; ++k) {
    Layer layer;
    layer.k = k;
    layer.modulus = ipow(Q, k);
    layer.offset_count = static_cast<u64>(offsets[static_cast<std::size_t>(k)].size());
    std::array<u64, 3> color_count{0, 0, 0};
    for (u64 d : offsets[static_cast<std::size_t>(k)]) {
      const u64 h = checked_mul(8, layer.modulus) + d + 1;
      ++color_count[static_cast<std::size_t>(h % 3)];
    }
    if (color_count[1] != 0) throw std::runtime_error("generated block has forbidden residue 1 mod 3");
    layer.selected_residue = color_count[2] >= color_count[0] ? 2 : 0;
    const u64 selected = color_count[static_cast<std::size_t>(layer.selected_residue)];
    if (2 * selected < layer.offset_count) throw std::runtime_error("majority color check failed");
    layer.U.reserve(static_cast<std::size_t>(selected));
    layer.V.reserve(static_cast<std::size_t>(selected));
    for (u64 d : offsets[static_cast<std::size_t>(k)]) {
      const u64 h = checked_mul(8, layer.modulus) + d + 1;
      if (static_cast<int>(h % 3) != layer.selected_residue) continue;
      if (h <= 5) throw std::runtime_error("block input is not distinct from every seed multiplier");
      const u64 u = layer.selected_residue == 2 ? 2 * h - 1 : 4 * h - 3;
      const u64 v = 3 * h - 1;
      if (u % 3 != 0 || v % 3 != 2 || u == v) {
        throw std::runtime_error("color separation or distinct-input check failed");
      }
      layer.U.push_back(u);
      layer.V.push_back(v);
    }
    layers[static_cast<std::size_t>(k)] = std::move(layer);
  }
  return layers;
}

ProductAudit audit_products(const std::vector<Layer>& layers, u64 Q, int K) {
  ProductAudit audit;
  audit.K = K;
  audit.scale = ipow(Q, K);
  audit.first_i = (K + 2) / 3;
  audit.last_i = (2 * K) / 3;
  std::vector<std::tuple<int, u64, u64>> channels;
  for (int i = audit.first_i; i <= audit.last_i; ++i) {
    const int j = K - i;
    if (i <= 0 || j <= 0 || i >= static_cast<int>(layers.size()) ||
        j >= static_cast<int>(layers.size())) {
      continue;
    }
    const u64 channel_edges = checked_mul(
        static_cast<u64>(layers[static_cast<std::size_t>(i)].U.size()),
        static_cast<u64>(layers[static_cast<std::size_t>(j)].V.size()));
    channels.emplace_back(i, audit.edges, channel_edges);
    if (audit.edges > std::numeric_limits<u64>::max() - channel_edges) {
      throw std::overflow_error("edge count overflow");
    }
    audit.edges += channel_edges;
  }
  if (channels.empty()) return audit;

  std::vector<u64> products(static_cast<std::size_t>(audit.edges));
  for (const auto& [i, base, channel_edges] : channels) {
    (void)channel_edges;
    const auto& left = layers[static_cast<std::size_t>(i)].U;
    const auto& right = layers[static_cast<std::size_t>(K - i)].V;
#pragma omp parallel for schedule(static)
    for (std::int64_t x = 0; x < static_cast<std::int64_t>(left.size()); ++x) {
      const u64 row = base + static_cast<u64>(x) * static_cast<u64>(right.size());
      for (std::size_t y = 0; y < right.size(); ++y) {
        products[static_cast<std::size_t>(row + y)] = checked_mul(left[static_cast<std::size_t>(x)], right[y]);
      }
    }
  }
  std::sort(products.begin(), products.end());

  constexpr std::array<u64, 12> cutoffs{1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096};
  audit.light.reserve(cutoffs.size());
  for (u64 cutoff : cutoffs) audit.light.push_back(LightRow{cutoff, 0, 0});
  for (std::size_t begin = 0; begin < products.size();) {
    std::size_t end = begin + 1;
    while (end < products.size() && products[end] == products[begin]) ++end;
    const u64 multiplicity = static_cast<u64>(end - begin);
    ++audit.support;
    audit.max_multiplicity = std::max(audit.max_multiplicity, multiplicity);
    audit.energy += static_cast<u128>(multiplicity) * multiplicity;
    if (audit.multiplicity_histogram.size() <= multiplicity) {
      audit.multiplicity_histogram.resize(static_cast<std::size_t>(multiplicity + 1), 0);
    }
    ++audit.multiplicity_histogram[static_cast<std::size_t>(multiplicity)];
    for (LightRow& row : audit.light) {
      if (multiplicity <= row.cutoff) {
        ++row.support;
        row.edge_mass += multiplicity;
      }
    }
    begin = end;
  }
  return audit;
}

void write_ratio(std::ostream& out, u128 numerator, u128 denominator) {
  out << "{\"numerator\": \"" << decimal(numerator) << "\", \"denominator\": \""
      << decimal(denominator) << "\", \"decimal\": ";
  const long double value = static_cast<long double>(numerator) / static_cast<long double>(denominator);
  out << std::setprecision(15) << static_cast<double>(value) << "}";
}

void write_ray(std::ostream& out, const Ray& ray) {
  const auto offsets = exact_ray_offsets(ray);
  const auto layers = make_layers(ray, offsets);
  const u64 Q = checked_mul(checked_mul(ipow(2, ray.a), ipow(3, ray.b)), ipow(5, ray.c));

  std::vector<ProductAudit> audits;
  for (int K = 2; K <= ray.Kmax; ++K) audits.push_back(audit_products(layers, Q, K));

  out << "    {\n"
      << "      \"name\": \"" << ray.name << "\",\n"
      << "      \"letter_counts\": [" << ray.a << ", " << ray.b << ", " << ray.c << "],\n"
      << "      \"Q\": " << Q << ",\n"
      << "      \"kmax\": " << ray.kmax << ",\n"
      << "      \"layers\": [\n";
  for (int k = 1; k <= ray.kmax; ++k) {
    const Layer& layer = layers[static_cast<std::size_t>(k)];
    out << "        {\"k\": " << k << ", \"D\": " << layer.offset_count
        << ", \"selected_residue\": " << layer.selected_residue
        << ", \"selected_size\": " << layer.U.size() << "}";
    out << (k == ray.kmax ? "\n" : ",\n");
  }
  out << "      ],\n      \"product_audits\": [\n";
  for (std::size_t p = 0; p < audits.size(); ++p) {
    const ProductAudit& audit = audits[p];
    out << "        {\n"
        << "          \"K\": " << audit.K << ",\n"
        << "          \"i_range\": [" << audit.first_i << ", " << audit.last_i << "],\n"
        << "          \"Q_pow_K\": " << audit.scale << ",\n"
        << "          \"edges\": " << audit.edges << ",\n"
        << "          \"support\": " << audit.support << ",\n"
        << "          \"max_multiplicity\": " << audit.max_multiplicity << ",\n"
        << "          \"energy\": \"" << decimal(audit.energy) << "\",\n"
        << "          \"edges_over_Q_pow_K\": ";
    write_ratio(out, audit.edges, audit.scale);
    out << ",\n          \"support_over_Q_pow_K\": ";
    write_ratio(out, audit.support, audit.scale);
    out << ",\n          \"energy_over_edges\": ";
    write_ratio(out, audit.energy, audit.edges);
    out << ",\n          \"multiplicity_histogram\": {";
    bool first_histogram_entry = true;
    for (std::size_t multiplicity = 1; multiplicity < audit.multiplicity_histogram.size();
         ++multiplicity) {
      const u64 count = audit.multiplicity_histogram[multiplicity];
      if (count == 0) continue;
      out << (first_histogram_entry ? "" : ", ") << "\"" << multiplicity << "\": " << count;
      first_histogram_entry = false;
    }
    out << "},\n          \"light_decoder\": [\n";
    for (std::size_t j = 0; j < audit.light.size(); ++j) {
      const LightRow& row = audit.light[j];
      out << "            {\"L\": " << row.cutoff << ", \"support\": " << row.support
          << ", \"edge_mass\": " << row.edge_mass << ", \"edge_fraction\": ";
      write_ratio(out, row.edge_mass, audit.edges);
      out << "}" << (j + 1 == audit.light.size() ? "\n" : ",\n");
    }
    out << "          ]\n"
        << "        }" << (p + 1 == audits.size() ? "\n" : ",\n");
  }
  out << "      ]\n    }";
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2 || argc > 3) {
    std::cerr << "usage: C102_truncated_decoder OUTPUT_JSON [THREADS]\n";
    return 2;
  }
  const int threads = argc == 3 ? std::stoi(argv[2]) : 1;
#ifdef _OPENMP
  omp_set_num_threads(threads);
#else
  if (threads != 1) throw std::invalid_argument("binary lacks OpenMP support");
#endif

  const std::array<Ray, 2> rays{{
      {"ray_2_1_1", 2, 1, 1, 4, 5},
      {"ray_3_2_1", 3, 2, 1, 3, 4},
  }};
  std::ofstream out(argv[1]);
  if (!out) throw std::runtime_error("cannot open output JSON");
  out << "{\n  \"threads\": " << threads << ",\n"
      << "  \"central_index_rule\": \"ceil(K/3) <= i <= floor(2K/3)\",\n"
      << "  \"rays\": [\n";
  for (std::size_t i = 0; i < rays.size(); ++i) {
    write_ray(out, rays[i]);
    out << (i + 1 == rays.size() ? "\n" : ",\n");
  }
  out << "  ]\n}\n";
  std::cout << "wrote " << argv[1] << "\n";
}
