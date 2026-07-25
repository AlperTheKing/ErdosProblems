#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

static int mod5(int x) { return (x % 5 + 5) % 5; }

static std::vector<std::pair<int, int>> reps() {
  std::set<std::pair<int, int>> result;
  for (int x = 0; x < 5; ++x)
    for (int y = 0; y < 5; ++y)
      if (x || y)
        result.insert(std::min(std::pair<int, int>{x, y},
                               std::pair<int, int>{mod5(-x), mod5(-y)}));
  return {result.begin(), result.end()};
}

static int cls(int dx, int dy, const std::vector<std::pair<int, int>> &r) {
  const auto target =
      std::min(std::pair<int, int>{mod5(dx), mod5(dy)},
               std::pair<int, int>{mod5(-dx), mod5(-dy)});
  const auto it = std::find(r.begin(), r.end(), target);
  if (it == r.end()) throw std::runtime_error("bad difference");
  return static_cast<int>(it - r.begin());
}

int main(int argc, char **argv) {
  try {
    if (argc != 3) {
      std::cerr << "usage: materialize_model SOLUTION.txt OUT.col\n";
      return 64;
    }
    std::ifstream in(argv[1]);
    if (!in) throw std::runtime_error("cannot read solution");
    std::array<int, 61> value{};
    bool sat = false;
    std::string line;
    while (std::getline(in, line)) {
      if (line.rfind("s SATISFIABLE", 0) == 0) sat = true;
      if (line.empty() || line[0] != 'v') continue;
      std::istringstream s(line.substr(1));
      int literal;
      while (s >> literal) {
        if (!literal) continue;
        const int v = std::abs(literal);
        if (v > 60 || value[v]) throw std::runtime_error("bad model");
        value[v] = literal > 0 ? 1 : -1;
      }
    }
    if (!sat) throw std::runtime_error("not a SAT solution");
    std::array<int, 12> h{};
    for (int k = 0; k < 12; ++k) {
      h[k] = -1;
      for (int z = 0; z < 5; ++z)
        if (value[5 * k + z + 1] == 1) {
          if (h[k] >= 0) throw std::runtime_error("multiple h values");
          h[k] = z;
        }
      if (h[k] < 0) throw std::runtime_error("missing h value");
    }
    const auto r = reps();
    std::ofstream out(argv[2], std::ios::binary);
    if (!out) throw std::runtime_error("cannot write colouring");
    out << "c 12-class translation-covariant K26 candidate\n";
    out << "c h";
    for (int z : h) out << ' ' << z;
    out << "\np edgecolor 26 5\n";
    for (int u = 0; u < 26; ++u)
      for (int v = u + 1; v < 26; ++v) {
        int colour;
        if (v == 25) {
          colour = u / 5;
        } else {
          const int ux = u / 5, uy = u % 5;
          const int vx = v / 5, vy = v % 5;
          const int midpoint_x = mod5(3 * (ux + vx));
          colour = mod5(midpoint_x + h[cls(vx - ux, vy - uy, r)]);
        }
        out << "e " << u << ' ' << v << ' ' << colour << "\n";
      }
    std::cout << "COVARIANT_MODEL_MATERIALIZED h=";
    for (int z : h) std::cout << z;
    std::cout << " edges=325 output=" << argv[2] << "\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "MATERIALIZE_FAIL " << e.what() << "\n";
    return 1;
  }
}
