#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

static constexpr int N = 26, Q = 5, EDGES = 325, VARS = 1625;

int main(int argc, char **argv) {
  try {
    if (argc != 3) {
      std::cerr << "usage: decode_model SOLUTION.txt OUT.col\n";
      return 64;
    }
    std::ifstream in(argv[1]);
    if (!in) throw std::runtime_error("cannot read solution");
    std::vector<int> value(VARS + 1, 0);
    bool sat = false;
    std::string line;
    while (std::getline(in, line)) {
      if (line.rfind("s SATISFIABLE", 0) == 0) sat = true;
      if (line.empty() || line[0] != 'v') continue;
      std::istringstream s(line.substr(1));
      int lit;
      while (s >> lit) {
        if (!lit) continue;
        const int v = std::abs(lit);
        if (v > VARS || value[v]) throw std::runtime_error("bad model literal");
        value[v] = lit > 0 ? 1 : -1;
      }
    }
    if (!sat) throw std::runtime_error("solution is not SAT");
    std::ofstream out(argv[2], std::ios::binary);
    if (!out) throw std::runtime_error("cannot write colouring");
    out << "c decoded unrestricted K26 candidate\n";
    out << "p edgecolor 26 5\n";
    int edge = 0;
    for (int u = 0; u < N; ++u)
      for (int v = u + 1; v < N; ++v, ++edge) {
        int chosen = -1;
        for (int c = 0; c < Q; ++c) {
          const int variable = Q * edge + c + 1;
          if (value[variable] == 1) {
            if (chosen >= 0) throw std::runtime_error("multiple edge colours");
            chosen = c;
          }
        }
        if (chosen < 0) throw std::runtime_error("missing edge colour");
        out << "e " << u << ' ' << v << ' ' << chosen << "\n";
      }
    std::cout << "MODEL_DECODED edges=325 colours=5 output=" << argv[2] << "\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "MODEL_DECODE_FAIL " << e.what() << "\n";
    return 1;
  }
}
