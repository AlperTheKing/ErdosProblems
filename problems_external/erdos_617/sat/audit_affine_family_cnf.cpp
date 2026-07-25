#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Clause = std::vector<int>;

static int vertical_edge_id(int x, int y1, int y2) {
  if (y1 > y2) std::swap(y1, y2);
  int rank = 0;
  for (int a = 0; a < y1; ++a) rank += 4 - a;
  rank += y2 - y1 - 1;
  return 10 * x + rank;
}
static int infinity_edge_id(int v) { return 50 + v; }
static int lit(int e, int c) { return 5 * e + c + 1; }

static std::map<Clause, int> parse(const std::string &path, int &vars,
                                   int &count) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot read CNF");
  std::map<Clause, int> result;
  bool header = false;
  int parsed = 0;
  std::string line;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == 'c') continue;
    if (line[0] == 'p') {
      std::istringstream s(line);
      char p;
      std::string cnf, extra;
      if (header || !(s >> p >> cnf >> vars >> count) || (s >> extra) ||
          cnf != "cnf")
        throw std::runtime_error("bad header");
      header = true;
      continue;
    }
    if (!header) throw std::runtime_error("missing header");
    std::istringstream s(line);
    Clause clause;
    int x;
    bool ended = false;
    while (s >> x) {
      if (!x) {
        ended = true;
        std::string extra;
        if (s >> extra) throw std::runtime_error("trailing clause data");
        break;
      }
      if (std::abs(x) > vars) throw std::runtime_error("literal range");
      clause.push_back(x);
    }
    if (!ended || clause.empty()) throw std::runtime_error("bad clause");
    ++result[clause];
    ++parsed;
  }
  if (!header || parsed != count) throw std::runtime_error("count mismatch");
  return result;
}

static std::map<Clause, int> reconstruct() {
  std::map<Clause, int> want;
  for (int e = 0; e < 75; ++e) {
    Clause atleast;
    for (int c = 0; c < 5; ++c) atleast.push_back(lit(e, c));
    ++want[atleast];
    for (int c = 0; c < 5; ++c)
      for (int d = c + 1; d < 5; ++d)
        ++want[Clause{-lit(e, c), -lit(e, d)}];
  }

  // Independent construction: a five-set lacks slope c exactly when it is
  // a transversal of the five parallel lines y-c*x=b. Select one point on
  // each line by independently choosing its x coordinate.
  for (int c = 0; c < 5; ++c) {
    for (int code = 0; code < 3125; ++code) {
      int z = code;
      std::array<int, 5> vertices{};
      for (int b = 0; b < 5; ++b) {
        const int x = z % 5;
        z /= 5;
        const int y = (c * x + b) % 5;
        vertices[b] = 5 * x + y;
      }
      std::sort(vertices.begin(), vertices.end());
      Clause clause;
      for (int v : vertices) clause.push_back(lit(infinity_edge_id(v), c));
      for (int i = 0; i < 5; ++i)
        for (int j = i + 1; j < 5; ++j) {
          const int u = vertices[i], v = vertices[j];
          if (u / 5 == v / 5)
            clause.push_back(lit(vertical_edge_id(u / 5, u % 5, v % 5), c));
        }
      std::sort(clause.begin(), clause.end());
      ++want[clause];
    }
  }
  return want;
}

int main(int argc, char **argv) {
  try {
    if (argc != 2) {
      std::cerr << "usage: audit_affine_family_cnf INSTANCE.cnf\n";
      return 64;
    }
    int vars = 0, clauses = 0;
    const auto got = parse(argv[1], vars, clauses);
    const auto want = reconstruct();
    if (vars != 375 || got != want)
      throw std::runtime_error("clause multiset differs");
    std::cout << "AFFINE_CNF_AUDIT_OK vars=375 clauses=" << clauses
              << " exactly_one_atleast=75 exactly_one_atmost=750"
              << " requirements=15625 symmetry_breakers=0\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "AFFINE_CNF_AUDIT_FAIL " << e.what() << "\n";
    return 1;
  }
}
