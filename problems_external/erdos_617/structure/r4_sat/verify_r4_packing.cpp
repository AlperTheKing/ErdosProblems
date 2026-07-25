#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

static constexpr int N = 26, M = 61, C = 5;

static std::vector<std::pair<int, int>> load_graph(const std::string &path) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot read graph");
  std::vector<std::pair<int, int>> edges;
  std::array<std::array<bool, N>, N> seen{};
  int dn = -1, dm = -1;
  std::string line;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == 'c') continue;
    std::istringstream s(line);
    char tag;
    s >> tag;
    if (tag == 'p') {
      std::string kind;
      if (!(s >> kind >> dn >> dm) || kind != "edge")
        throw std::runtime_error("bad graph header");
    } else if (tag == 'e') {
      int u, v;
      if (!(s >> u >> v) || u < 0 || u >= v || v >= N || seen[u][v])
        throw std::runtime_error("bad graph edge");
      seen[u][v] = seen[v][u] = true;
      edges.push_back({u, v});
    } else {
      throw std::runtime_error("bad graph record");
    }
  }
  if (dn != N || dm != M || edges.size() != M)
    throw std::runtime_error("graph count");
  return edges;
}

static std::array<std::array<int, N>, C> load_permutations(
    const std::string &path) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot read permutations");
  std::array<std::array<int, N>, C> p{};
  std::array<bool, C> got{};
  bool header = false;
  std::string line;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == 'c') continue;
    std::istringstream s(line);
    char tag;
    s >> tag;
    if (tag == 'p') {
      std::string kind;
      int n, copies;
      if (header || !(s >> kind >> n >> copies) || kind != "permutations" ||
          n != N || copies != C)
        throw std::runtime_error("bad permutation header");
      header = true;
    } else if (tag == 'm') {
      int c;
      if (!header || !(s >> c) || c < 0 || c >= C || got[c])
        throw std::runtime_error("bad map row");
      std::array<bool, N> used{};
      for (int i = 0; i < N; ++i) {
        if (!(s >> p[c][i]) || p[c][i] < 0 || p[c][i] >= N ||
            used[p[c][i]])
          throw std::runtime_error("map is not a permutation");
        used[p[c][i]] = true;
      }
      std::string extra;
      if (s >> extra) throw std::runtime_error("map trailing data");
      got[c] = true;
    } else {
      throw std::runtime_error("bad permutation record");
    }
  }
  if (!header || !std::all_of(got.begin(), got.end(), [](bool x) { return x; }))
    throw std::runtime_error("incomplete permutations");
  return p;
}

static bool next6(std::array<int, 6> &a) {
  for (int i = 5; i >= 0; --i) {
    if (a[i] < 20 + i) {
      ++a[i];
      for (int j = i + 1; j < 6; ++j) a[j] = a[j - 1] + 1;
      return true;
    }
  }
  return false;
}

int main(int argc, char **argv) {
  try {
    if (argc != 3 && argc != 4) {
      std::cerr << "usage: verify_r4_packing G61.edges PACKING.perm [OUT.col]\n";
      return 64;
    }
    const auto edges = load_graph(argv[1]);
    const auto p = load_permutations(argv[2]);
    std::array<std::array<int, N>, N> colour;
    for (auto &row : colour) row.fill(-1);
    int packed = 0;
    for (int c = 0; c < C; ++c)
      for (const auto &[i, j] : edges) {
        int u = p[c][i], v = p[c][j];
        if (u > v) std::swap(u, v);
        if (colour[u][v] >= 0)
          throw std::runtime_error("edge overlap at " + std::to_string(u) +
                                   "," + std::to_string(v));
        colour[u][v] = colour[v][u] = c;
        ++packed;
      }
    int uncovered = 0;
    for (int u = 0; u < N; ++u)
      for (int v = u + 1; v < N; ++v)
        if (colour[u][v] < 0) {
          colour[u][v] = colour[v][u] = 0;
          ++uncovered;
        }
    if (packed != 305 || uncovered != 20)
      throw std::runtime_error("packing count mismatch");

    std::array<int, C> missing{};
    std::uint64_t sets = 0, failing = 0;
    std::array<int, 6> a{0, 1, 2, 3, 4, 5};
    do {
      ++sets;
      int mask = 0;
      for (int i = 0; i < 6; ++i)
        for (int j = i + 1; j < 6; ++j) mask |= 1 << colour[a[i]][a[j]];
      if (mask != 31) {
        ++failing;
        for (int c = 0; c < C; ++c)
          if (!(mask & (1 << c))) ++missing[c];
      }
    } while (next6(a));
    if (failing) throw std::runtime_error("six-set audit failed");

    if (argc == 4) {
      std::ofstream out(argv[3], std::ios::binary);
      if (!out) throw std::runtime_error("cannot write colouring");
      out << "c R4 packing; 20 uncovered edges assigned colour 0\n";
      out << "p edgecolor 26 5\n";
      for (int u = 0; u < N; ++u)
        for (int v = u + 1; v < N; ++v)
          out << "e " << u << ' ' << v << ' ' << colour[u][v] << "\n";
    }
    std::cout << "R4_PACKING_VERIFIED copies=5 packed_edges=305"
              << " uncovered=20 six_sets=" << sets
              << " failing_sets=0\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "R4_PACKING_REJECTED " << e.what() << "\n";
    return 1;
  }
}
