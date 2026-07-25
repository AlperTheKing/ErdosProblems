#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

// Vertices 0..24 are (x,y) = (v/5,v%5); vertex 25 is infinity.
// Every nonvertical old edge has fixed colour equal to its F_5 slope.
// The 50 vertical old edges and 25 infinity edges are free.

static int inv5(int a) {
  static constexpr int inv[5]{0, 1, 3, 2, 4};
  return inv[a];
}

static int fixed_slope(int u, int v) {
  const int ux = u / 5, uy = u % 5;
  const int vx = v / 5, vy = v % 5;
  const int dx = (vx - ux + 5) % 5;
  if (dx == 0) return -1;
  const int dy = (vy - uy + 5) % 5;
  return (dy * inv5(dx)) % 5;
}

static int free_edge_id(int u, int v) {
  if (u > v) std::swap(u, v);
  if (v == 25 && 0 <= u && u < 25) return 50 + u;
  if (0 <= u && u < v && v < 25 && u / 5 == v / 5) {
    const int x = u / 5, a = u % 5, b = v % 5;
    int within = 0;
    for (int i = 0; i < a; ++i) within += 4 - i;
    within += b - a - 1;
    return 10 * x + within;
  }
  return -1;
}

static int var(int edge_id, int colour) {
  return 5 * edge_id + colour + 1;
}

static bool next5(std::array<int, 5> &s) {
  for (int i = 4; i >= 0; --i) {
    if (s[i] < 20 + i) {
      ++s[i];
      for (int j = i + 1; j < 5; ++j) s[j] = s[j - 1] + 1;
      return true;
    }
  }
  return false;
}

int main(int argc, char **argv) {
  try {
    if (argc != 2) {
      std::cerr << "usage: encode_affine_family OUT.cnf\n";
      return 64;
    }
    std::vector<std::vector<int>> clauses;
    clauses.reserve(17000);

    // Exactly one colour for each of 75 free edges.
    for (int e = 0; e < 75; ++e) {
      std::vector<int> atleast;
      for (int c = 0; c < 5; ++c) atleast.push_back(var(e, c));
      clauses.push_back(std::move(atleast));
      for (int c = 0; c < 5; ++c)
        for (int d = c + 1; d < 5; ++d)
          clauses.push_back({-var(e, c), -var(e, d)});
    }

    std::array<std::uint64_t, 5> need_by_colour{};
    std::array<std::uint64_t, 16> need_by_size{};
    std::array<int, 5> s{0, 1, 2, 3, 4};
    std::uint64_t five_sets = 0, requirements = 0;
    do {
      ++five_sets;
      int fixed_mask = 0;
      for (int i = 0; i < 5; ++i)
        for (int j = i + 1; j < 5; ++j) {
          const int c = fixed_slope(s[i], s[j]);
          if (c >= 0) fixed_mask |= 1 << c;
        }
      for (int c = 0; c < 5; ++c) {
        if (fixed_mask & (1 << c)) continue;
        std::vector<int> clause;
        for (int v : s) clause.push_back(var(free_edge_id(v, 25), c));
        for (int i = 0; i < 5; ++i)
          for (int j = i + 1; j < 5; ++j) {
            const int e = free_edge_id(s[i], s[j]);
            if (e >= 0) clause.push_back(var(e, c));
          }
        std::sort(clause.begin(), clause.end());
        clauses.push_back(std::move(clause));
        ++requirements;
        ++need_by_colour[c];
        ++need_by_size[clauses.back().size()];
      }
    } while (next5(s));

    std::ofstream out(argv[1], std::ios::binary);
    if (!out) throw std::runtime_error("cannot write output");
    out << "c free edges 0..49 vertical old, 50..74 infinity-to-old\n";
    out << "c variable(e,c)=5*e+c+1; no symmetry breaking\n";
    out << "p cnf 375 " << clauses.size() << "\n";
    for (const auto &clause : clauses) {
      for (int lit : clause) out << lit << ' ';
      out << "0\n";
    }
    std::cout << "AFFINE_ENCODED vars=375 clauses=" << clauses.size()
              << " exactly_one_atleast=75 exactly_one_atmost=750"
              << " five_sets=" << five_sets
              << " requirements=" << requirements
              << " symmetry_breakers=0";
    for (int c = 0; c < 5; ++c)
      std::cout << " need_c" << c << '=' << need_by_colour[c];
    for (int k = 5; k <= 15; ++k)
      if (need_by_size[k])
        std::cout << " size" << k << '=' << need_by_size[k];
    std::cout << "\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "ERROR " << e.what() << "\n";
    return 1;
  }
}
