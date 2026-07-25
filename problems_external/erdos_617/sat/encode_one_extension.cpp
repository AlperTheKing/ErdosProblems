#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Coloring {
  int n = -1, colors = -1;
  std::vector<int> edge;
};

static int &at(Coloring &g, int u, int v) {
  return g.edge[static_cast<std::size_t>(u) * g.n + v];
}
static int at(const Coloring &g, int u, int v) {
  return g.edge[static_cast<std::size_t>(u) * g.n + v];
}

static Coloring read_base(const std::string &path) {
  std::ifstream in(path, std::ios::binary);
  if (!in) throw std::runtime_error("cannot read base");
  Coloring g;
  bool header = false;
  std::string line;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == 'c') continue;
    std::istringstream ss(line);
    char tag;
    ss >> tag;
    if (tag == 'p') {
      std::string kind, extra;
      if (header || !(ss >> kind >> g.n >> g.colors) || (ss >> extra) ||
          kind != "edgecolor")
        throw std::runtime_error("bad header");
      g.edge.assign(static_cast<std::size_t>(g.n) * g.n, -1);
      header = true;
    } else if (tag == 'e') {
      int u, v, c;
      std::string extra;
      if (!header || !(ss >> u >> v >> c) || (ss >> extra) || u < 0 ||
          u >= v || v >= g.n || c < 0 || c >= g.colors || at(g, u, v) >= 0)
        throw std::runtime_error("bad edge");
      at(g, u, v) = at(g, v, u) = c;
    } else {
      throw std::runtime_error("bad record");
    }
  }
  if (g.n != 25 || g.colors != 5)
    throw std::runtime_error("expected a K25 five-colouring");
  for (int u = 0; u < g.n; ++u)
    for (int v = u + 1; v < g.n; ++v)
      if (at(g, u, v) < 0) throw std::runtime_error("missing edge");
  return g;
}

static bool next_combination(std::array<int, 5> &a, int n) {
  for (int i = 4; i >= 0; --i) {
    if (a[i] < n - 5 + i) {
      ++a[i];
      for (int j = i + 1; j < 5; ++j) a[j] = a[j - 1] + 1;
      return true;
    }
  }
  return false;
}

static int var(int vertex, int color) { return vertex * 5 + color + 1; }

int main(int argc, char **argv) {
  try {
    if (argc != 3) {
      std::cerr << "usage: encode_one_extension BASE.col OUT.cnf\n";
      return 64;
    }
    const Coloring g = read_base(argv[1]);
    std::vector<std::vector<int>> clauses;
    std::array<std::uint64_t, 5> absent_count{};

    // Exactly one colour on each of the 25 new incident edges.
    for (int v = 0; v < 25; ++v) {
      std::vector<int> atleast;
      for (int c = 0; c < 5; ++c) atleast.push_back(var(v, c));
      clauses.push_back(std::move(atleast));
      for (int c = 0; c < 5; ++c)
        for (int d = c + 1; d < 5; ++d)
          clauses.push_back({-var(v, c), -var(v, d)});
    }

    // For each old five-set S and each colour absent inside S, some new edge
    // from vertex 25 to S must have that colour.
    std::array<int, 5> a{0, 1, 2, 3, 4};
    std::uint64_t five_sets = 0;
    do {
      ++five_sets;
      int mask = 0;
      for (int i = 0; i < 5; ++i)
        for (int j = i + 1; j < 5; ++j)
          mask |= 1 << at(g, a[i], a[j]);
      for (int c = 0; c < 5; ++c) {
        if (!(mask & (1 << c))) {
          std::vector<int> clause;
          for (int i = 0; i < 5; ++i) clause.push_back(var(a[i], c));
          clauses.push_back(std::move(clause));
          ++absent_count[c];
        }
      }
    } while (next_combination(a, 25));

    std::ofstream out(argv[2], std::ios::binary);
    if (!out) throw std::runtime_error("cannot write CNF");
    out << "c x(v,c) = variable 5*v+c+1 for v=0..24,c=0..4\n";
    out << "c no symmetry-breaking clauses\n";
    out << "p cnf 125 " << clauses.size() << "\n";
    for (const auto &clause : clauses) {
      for (int lit : clause) out << lit << ' ';
      out << "0\n";
    }
    std::cout << "ENCODED vars=125 clauses=" << clauses.size()
              << " exactly_one_atleast=25 exactly_one_atmost=250"
              << " five_sets=" << five_sets
              << " extension_clauses=" << (clauses.size() - 275)
              << " symmetry_breakers=0";
    for (int c = 0; c < 5; ++c)
      std::cout << " absent_c" << c << '=' << absent_count[c];
    std::cout << "\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "ERROR " << e.what() << "\n";
    return 1;
  }
}
