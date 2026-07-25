#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Clause = std::vector<int>;

struct Base {
  int edge[25][25];
  Base() { std::fill(&edge[0][0], &edge[0][0] + 625, -1); }
};

static Base load_base(const std::string &path) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot read base");
  Base b;
  std::string line;
  int n = -1, q = -1, count = 0;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == 'c') continue;
    std::istringstream s(line);
    char type;
    s >> type;
    if (type == 'p') {
      std::string kind;
      if (!(s >> kind >> n >> q) || kind != "edgecolor" || n != 25 || q != 5)
        throw std::runtime_error("base header mismatch");
    } else if (type == 'e') {
      int u, v, c;
      if (!(s >> u >> v >> c) || u < 0 || u >= v || v >= 25 || c < 0 ||
          c >= 5 || b.edge[u][v] != -1)
        throw std::runtime_error("bad base edge");
      b.edge[u][v] = b.edge[v][u] = c;
      ++count;
    } else {
      throw std::runtime_error("bad base record");
    }
  }
  if (n != 25 || q != 5 || count != 300) throw std::runtime_error("base incomplete");
  return b;
}

static std::map<Clause, int> load_cnf(const std::string &path, int &vars,
                                      int &declared_clauses) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot read CNF");
  std::map<Clause, int> got;
  std::string line;
  bool header = false;
  int parsed = 0;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == 'c') continue;
    if (line[0] == 'p') {
      std::istringstream s(line);
      char p;
      std::string cnf, extra;
      if (header || !(s >> p >> cnf >> vars >> declared_clauses) ||
          (s >> extra) || cnf != "cnf")
        throw std::runtime_error("bad CNF header");
      header = true;
      continue;
    }
    if (!header) throw std::runtime_error("clause before header");
    std::istringstream s(line);
    Clause clause;
    int lit;
    bool zero = false;
    while (s >> lit) {
      if (lit == 0) {
        zero = true;
        std::string extra;
        if (s >> extra) throw std::runtime_error("data after clause zero");
        break;
      }
      if (std::abs(lit) > vars) throw std::runtime_error("literal out of range");
      clause.push_back(lit);
    }
    if (!zero || clause.empty()) throw std::runtime_error("malformed clause");
    ++got[clause];
    ++parsed;
  }
  if (!header || parsed != declared_clauses)
    throw std::runtime_error("CNF clause count mismatch");
  return got;
}

static int variable(int v, int c) { return 5 * v + c + 1; }

static std::map<Clause, int> expected(const Base &b, int &extension_count) {
  std::map<Clause, int> want;
  for (int v = 0; v < 25; ++v) {
    Clause atleast;
    for (int c = 0; c < 5; ++c) atleast.push_back(variable(v, c));
    ++want[atleast];
    for (int c = 0; c < 5; ++c)
      for (int d = c + 1; d < 5; ++d)
        ++want[Clause{-variable(v, c), -variable(v, d)}];
  }
  extension_count = 0;
  for (int a = 0; a < 21; ++a)
    for (int d = a + 1; d < 22; ++d)
      for (int e = d + 1; e < 23; ++e)
        for (int f = e + 1; f < 24; ++f)
          for (int g = f + 1; g < 25; ++g) {
            const int set[5]{a, d, e, f, g};
            int present[5]{};
            for (int i = 0; i < 5; ++i)
              for (int j = i + 1; j < 5; ++j)
                present[b.edge[set[i]][set[j]]] = 1;
            for (int c = 0; c < 5; ++c)
              if (!present[c]) {
                Clause clause;
                for (int i = 0; i < 5; ++i)
                  clause.push_back(variable(set[i], c));
                ++want[clause];
                ++extension_count;
              }
          }
  return want;
}

int main(int argc, char **argv) {
  try {
    if (argc != 3) {
      std::cerr << "usage: audit_one_extension_cnf BASE.col INSTANCE.cnf\n";
      return 64;
    }
    const Base b = load_base(argv[1]);
    int vars = 0, declared = 0, extension_count = 0;
    const auto got = load_cnf(argv[2], vars, declared);
    const auto want = expected(b, extension_count);
    if (vars != 125 || got != want)
      throw std::runtime_error("clause multiset differs from exact encoding");
    std::cout << "CNF_AUDIT_OK vars=125 clauses=" << declared
              << " exactly_one_atleast=25 exactly_one_atmost=250"
              << " extension_clauses=" << extension_count
              << " symmetry_breakers=0\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "CNF_AUDIT_FAIL " << e.what() << "\n";
    return 1;
  }
}
