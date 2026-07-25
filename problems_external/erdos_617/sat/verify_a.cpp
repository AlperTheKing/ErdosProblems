#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;

struct Coloring {
  int n = -1;
  int colors = -1;
  std::vector<int> edge;
};

static int &at(Coloring &g, int u, int v) {
  return g.edge[static_cast<std::size_t>(u) * g.n + v];
}

static int at(const Coloring &g, int u, int v) {
  return g.edge[static_cast<std::size_t>(u) * g.n + v];
}

static Coloring affine25() {
  Coloring g{25, 5, std::vector<int>(625, -1)};
  for (int u = 0; u < 25; ++u) {
    const int ux = u / 5, uy = u % 5;
    for (int v = u + 1; v < 25; ++v) {
      const int vx = v / 5, vy = v % 5;
      const int dx = (vx - ux + 5) % 5;
      const int dy = (vy - uy + 5) % 5;
      int color = 4;  // vertical and slope 4 are merged.
      if (dx != 0) {
        int inverse = 0;
        for (int z = 1; z < 5; ++z)
          if ((dx * z) % 5 == 1) inverse = z;
        const int slope = (dy * inverse) % 5;
        if (slope < 4) color = slope;
      }
      at(g, u, v) = at(g, v, u) = color;
    }
  }
  return g;
}

static void write_coloring(const fs::path &path, const Coloring &g) {
  std::ofstream out(path, std::ios::binary);
  if (!out) throw std::runtime_error("cannot write " + path.string());
  out << "c Erdos 617 canonical edge-colouring\n";
  out << "p edgecolor " << g.n << ' ' << g.colors << "\n";
  for (int u = 0; u < g.n; ++u)
    for (int v = u + 1; v < g.n; ++v)
      out << "e " << u << ' ' << v << ' ' << at(g, u, v) << "\n";
}

static void generate_fixtures(const fs::path &dir) {
  fs::create_directories(dir);
  const Coloring good = affine25();
  write_coloring(dir / "affine_k25.col", good);

  Coloring bad = good;
  for (int u = 0; u < 6; ++u)
    for (int v = u + 1; v < 6; ++v)
      if (at(bad, u, v) == 4) at(bad, u, v) = at(bad, v, u) = 0;
  write_coloring(dir / "negative_missing_colour.col", bad);

  {
    std::ofstream out(dir / "negative_duplicate_edge.col", std::ios::binary);
    out << "p edgecolor 25 5\n";
    out << "e 0 1 " << at(good, 0, 1) << "\n";
    for (int u = 0; u < 25; ++u)
      for (int v = u + 1; v < 25; ++v)
        if (!(u == 24 - 1 && v == 24))
          out << "e " << u << ' ' << v << ' ' << at(good, u, v) << "\n";
  }
  {
    std::ofstream out(dir / "negative_loop.col", std::ios::binary);
    out << "p edgecolor 25 5\n";
    out << "e 0 0 0\n";
    for (int u = 0; u < 25; ++u)
      for (int v = u + 1; v < 25; ++v)
        out << "e " << u << ' ' << v << ' ' << at(good, u, v) << "\n";
  }
  std::cout << "GENERATED dir=" << dir.string()
            << " positive_edges=300 negative_fixtures=3\n";
}

static Coloring read_coloring(const fs::path &path) {
  std::ifstream in(path, std::ios::binary);
  if (!in) throw std::runtime_error("cannot read " + path.string());
  Coloring g;
  bool header = false;
  std::string line;
  int line_number = 0;
  while (std::getline(in, line)) {
    ++line_number;
    if (line.empty() || line[0] == 'c') continue;
    std::istringstream ss(line);
    char tag = '\0';
    ss >> tag;
    if (tag == 'p') {
      std::string kind, extra;
      if (header || !(ss >> kind >> g.n >> g.colors) || (ss >> extra) ||
          kind != "edgecolor" || g.n < 2 || g.colors < 1)
        throw std::runtime_error("invalid header at line " +
                                 std::to_string(line_number));
      g.edge.assign(static_cast<std::size_t>(g.n) * g.n, -1);
      header = true;
    } else if (tag == 'e') {
      int u, v, color;
      std::string extra;
      if (!header || !(ss >> u >> v >> color) || (ss >> extra))
        throw std::runtime_error("invalid edge syntax at line " +
                                 std::to_string(line_number));
      if (u < 0 || v < 0 || u >= g.n || v >= g.n || u >= v)
        throw std::runtime_error("edge is not canonical at line " +
                                 std::to_string(line_number));
      if (color < 0 || color >= g.colors)
        throw std::runtime_error("invalid colour at line " +
                                 std::to_string(line_number));
      if (at(g, u, v) != -1)
        throw std::runtime_error("duplicate edge at line " +
                                 std::to_string(line_number));
      at(g, u, v) = at(g, v, u) = color;
    } else {
      throw std::runtime_error("unknown record at line " +
                               std::to_string(line_number));
    }
  }
  if (!header) throw std::runtime_error("missing header");
  for (int u = 0; u < g.n; ++u)
    for (int v = u + 1; v < g.n; ++v)
      if (at(g, u, v) < 0)
        throw std::runtime_error("missing edge " + std::to_string(u) + "," +
                                 std::to_string(v));
  return g;
}

static bool next_combination(std::vector<int> &a, int n) {
  const int k = static_cast<int>(a.size());
  for (int i = k - 1; i >= 0; --i) {
    if (a[i] < n - k + i) {
      ++a[i];
      for (int j = i + 1; j < k; ++j) a[j] = a[j - 1] + 1;
      return true;
    }
  }
  return false;
}

static bool verify(const Coloring &g) {
  if (g.colors >= 63) throw std::runtime_error("too many colours");
  const int k = g.colors + 1;
  if (g.n < k) throw std::runtime_error("fewer vertices than audit set size");
  const std::uint64_t full = (std::uint64_t{1} << g.colors) - 1;
  std::vector<std::uint64_t> missing(g.colors, 0);
  std::vector<int> first;
  std::uint64_t sets = 0, failing = 0;
  std::vector<int> a(k);
  for (int i = 0; i < k; ++i) a[i] = i;
  do {
    ++sets;
    std::uint64_t mask = 0;
    for (int i = 0; i < k; ++i)
      for (int j = i + 1; j < k; ++j)
        mask |= std::uint64_t{1} << at(g, a[i], a[j]);
    if (mask != full) {
      ++failing;
      if (first.empty()) first = a;
      for (int c = 0; c < g.colors; ++c)
        if (!(mask & (std::uint64_t{1} << c))) ++missing[c];
    }
  } while (next_combination(a, g.n));

  std::cout << "AUDIT n=" << g.n << " colors=" << g.colors
            << " edges=" << (g.n * (g.n - 1) / 2) << " sets=" << sets
            << " failing_sets=" << failing;
  for (int c = 0; c < g.colors; ++c)
    std::cout << " missing_c" << c << '=' << missing[c];
  std::cout << "\n";
  if (!first.empty()) {
    std::cout << "FIRST_FAIL";
    for (int v : first) std::cout << ' ' << v;
    std::cout << "\n";
  }
  return failing == 0;
}

int main(int argc, char **argv) {
  try {
    if (argc == 3 && std::string(argv[1]) == "--generate-fixtures") {
      generate_fixtures(argv[2]);
      return 0;
    }
    if (argc != 2) {
      std::cerr << "usage: verify_a FILE | verify_a --generate-fixtures DIR\n";
      return 64;
    }
    const Coloring g = read_coloring(argv[1]);
    const bool ok = verify(g);
    std::cout << (ok ? "VERIFIED\n" : "REJECTED\n");
    return ok ? 0 : 2;
  } catch (const std::exception &e) {
    std::cerr << "FORMAT_ERROR " << e.what() << "\n";
    return 1;
  }
}
