#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

static constexpr int N = 26, FREE = 4, PCOUNT = FREE * N * N;
static int pv(int c, int i, int u) { return 1 + (c * N + i) * N + u; }

int main(int argc, char **argv) {
  try {
    if (argc != 3) {
      std::cerr << "usage: decode_r4_model SOLUTION.txt OUT.perm\n";
      return 64;
    }
    std::ifstream in(argv[1]);
    if (!in) throw std::runtime_error("cannot read solution");
    std::array<int, PCOUNT + 1> value{};
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
        if (v <= PCOUNT) {
          if (value[v]) throw std::runtime_error("duplicate model variable");
          value[v] = literal > 0 ? 1 : -1;
        }
      }
    }
    if (!sat) throw std::runtime_error("not SAT");
    std::ofstream out(argv[2], std::ios::binary);
    if (!out) throw std::runtime_error("cannot write packing");
    out << "c copy 0 fixed identity by host relabelling\n";
    out << "p permutations 26 5\n";
    out << "m 0";
    for (int i = 0; i < N; ++i) out << ' ' << i;
    out << "\n";
    for (int c = 0; c < FREE; ++c) {
      out << "m " << c + 1;
      std::array<bool, N> used{};
      for (int i = 0; i < N; ++i) {
        int image = -1;
        for (int u = 0; u < N; ++u)
          if (value[pv(c, i, u)] == 1) {
            if (image >= 0) throw std::runtime_error("multiple images");
            image = u;
          }
        if (image < 0 || used[image]) throw std::runtime_error("bad permutation");
        used[image] = true;
        out << ' ' << image;
      }
      out << "\n";
    }
    std::cout << "R4_MODEL_DECODED output=" << argv[2] << "\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "R4_MODEL_REJECTED " << e.what() << "\n";
    return 1;
  }
}
