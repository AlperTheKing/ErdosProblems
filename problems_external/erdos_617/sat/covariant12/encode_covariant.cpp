#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

static constexpr int N = 26, Q = 5, CLASSES = 12;

static int mod5(int x) {
  x %= 5;
  return x < 0 ? x + 5 : x;
}

static std::vector<std::pair<int, int>> representatives() {
  std::set<std::pair<int, int>> reps;
  for (int dx = 0; dx < 5; ++dx)
    for (int dy = 0; dy < 5; ++dy) {
      if (dx == 0 && dy == 0) continue;
      const std::pair<int, int> d{dx, dy};
      const std::pair<int, int> neg{mod5(-dx), mod5(-dy)};
      reps.insert(std::min(d, neg));
    }
  return {reps.begin(), reps.end()};
}

static int class_id(int dx, int dy,
                    const std::map<std::pair<int, int>, int> &ids) {
  const std::pair<int, int> d{mod5(dx), mod5(dy)};
  const std::pair<int, int> neg{mod5(-dx), mod5(-dy)};
  return ids.at(std::min(d, neg));
}

static int var(int cls, int value) { return Q * cls + value + 1; }

static bool next6(std::array<int, 6> &a) {
  for (int i = 5; i >= 0; --i) {
    if (a[i] < N - 6 + i) {
      ++a[i];
      for (int j = i + 1; j < 6; ++j) a[j] = a[j - 1] + 1;
      return true;
    }
  }
  return false;
}

int main(int argc, char **argv) {
  try {
    if (argc != 2) {
      std::cerr << "usage: encode_covariant OUT.cnf\n";
      return 64;
    }
    const auto reps = representatives();
    if (reps.size() != CLASSES) throw std::runtime_error("class count");
    std::map<std::pair<int, int>, int> ids;
    for (int i = 0; i < CLASSES; ++i) ids[reps[i]] = i;

    std::vector<std::vector<int>> clauses;
    clauses.reserve(193000);
    for (int k = 0; k < CLASSES; ++k) {
      std::vector<int> atleast;
      for (int h = 0; h < Q; ++h) atleast.push_back(var(k, h));
      clauses.push_back(std::move(atleast));
      for (int h = 0; h < Q; ++h)
        for (int j = h + 1; j < Q; ++j)
          clauses.push_back({-var(k, h), -var(k, j)});
    }

    std::array<int, 31> by_length{};
    std::uint64_t sets = 0, fixed_tautologies = 0, coverage = 0;
    std::array<int, 6> a{0, 1, 2, 3, 4, 5};
    do {
      ++sets;
      bool fixed_zero = false;
      std::set<int> literals;
      for (int i = 0; i < 6; ++i) {
        if (a[i] == 25) continue;
        const int ux = a[i] / 5;
        if (a[5] == 25 && ux == 0) fixed_zero = true;
      }
      for (int i = 0; i < 6; ++i)
        for (int j = i + 1; j < 6; ++j) {
          const int u = a[i], v = a[j];
          if (v == 25) continue;
          const int ux = u / 5, uy = u % 5;
          const int vx = v / 5, vy = v % 5;
          const int cls = class_id(vx - ux, vy - uy, ids);
          const int midpoint_x = mod5(3 * (ux + vx));  // 2^{-1}=3 in F_5.
          const int required_h = mod5(-midpoint_x);
          literals.insert(var(cls, required_h));
        }
      if (fixed_zero) {
        ++fixed_tautologies;
      } else {
        if (literals.empty()) throw std::runtime_error("empty coverage clause");
        clauses.emplace_back(literals.begin(), literals.end());
        ++coverage;
        ++by_length[clauses.back().size()];
      }
    } while (next6(a));

    std::ofstream out(argv[1], std::ios::binary);
    if (!out) throw std::runtime_error("cannot write output");
    static std::vector<char> buffer(1 << 20);
    out.rdbuf()->pubsetbuf(buffer.data(), static_cast<std::streamsize>(buffer.size()));
    out << "c 12-class translation-covariant K26 family over F5^2 plus infinity\n";
    for (int k = 0; k < CLASSES; ++k)
      out << "c class " << k << " representative " << reps[k].first << ' '
          << reps[k].second << "\n";
    out << "c variable(k,h)=5*k+h+1; no SAT symmetry breaker\n";
    out << "p cnf 60 " << clauses.size() << "\n";
    for (const auto &clause : clauses) {
      for (int literal : clause) out << literal << ' ';
      out << "0\n";
    }
    out.close();
    if (!out) throw std::runtime_error("write failure");
    std::cout << "COVARIANT_ENCODED vars=60 clauses=" << clauses.size()
              << " classes=12 alo=12 amo=120 six_sets=" << sets
              << " fixed_tautologies=" << fixed_tautologies
              << " coverage=" << coverage << " symmetry_breakers=0";
    for (int k = 1; k <= 30; ++k)
      if (by_length[k]) std::cout << " len" << k << '=' << by_length[k];
    std::cout << "\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "ERROR " << e.what() << "\n";
    return 1;
  }
}
