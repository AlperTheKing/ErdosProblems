#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

static constexpr int N = 26, M = 61, H = 325, FREE_COPIES = 4;
static constexpr int P_COUNT = FREE_COPIES * N * N;
static constexpr int A_COUNT = FREE_COPIES * M * H * 2;
static constexpr int Y_COUNT = FREE_COPIES * H;
static constexpr int VARS = P_COUNT + A_COUNT + Y_COUNT;
static constexpr std::uint64_t CLAUSES =
    208 + 67600 + 3ULL * A_COUNT + A_COUNT + Y_COUNT +
    FREE_COPIES * M + 6 * H;

struct Graph {
  std::vector<std::pair<int, int>> edges;
  std::array<std::array<int, N>, N> host_id{};
  std::vector<std::pair<int, int>> host_edges;
};

static Graph load_graph(const std::string &path) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot read graph");
  Graph g;
  for (auto &row : g.host_id) row.fill(-1);
  for (int u = 0; u < N; ++u)
    for (int v = u + 1; v < N; ++v) {
      const int id = static_cast<int>(g.host_edges.size());
      g.host_id[u][v] = g.host_id[v][u] = id;
      g.host_edges.push_back({u, v});
    }
  int declared_n = -1, declared_m = -1;
  std::array<std::array<bool, N>, N> seen{};
  std::string line;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == 'c') continue;
    std::istringstream s(line);
    char tag;
    s >> tag;
    if (tag == 'p') {
      std::string kind, extra;
      if (!(s >> kind >> declared_n >> declared_m) || (s >> extra) ||
          kind != "edge")
        throw std::runtime_error("bad graph header");
    } else if (tag == 'e') {
      int u, v;
      std::string extra;
      if (!(s >> u >> v) || (s >> extra) || u < 0 || u >= v || v >= N ||
          seen[u][v])
        throw std::runtime_error("bad graph edge");
      seen[u][v] = seen[v][u] = true;
      g.edges.push_back({u, v});
    } else {
      throw std::runtime_error("bad graph record");
    }
  }
  if (declared_n != N || declared_m != M || g.edges.size() != M)
    throw std::runtime_error("graph count mismatch");
  return g;
}

static int pvar(int c, int source, int host) {
  return 1 + (c * N + source) * N + host;
}
static int avar(int c, int source_edge, int host_edge, int orientation) {
  return 1 + P_COUNT +
         (((c * M + source_edge) * H + host_edge) * 2 + orientation);
}
static int yvar(int c, int host_edge) {
  return 1 + P_COUNT + A_COUNT + c * H + host_edge;
}

int main(int argc, char **argv) {
  try {
    if (argc != 3) {
      std::cerr << "usage: generate_r4_packing_cnf G61.edges OUT.cnf\n";
      return 64;
    }
    const Graph g = load_graph(argv[1]);
    std::ofstream out(argv[2], std::ios::binary);
    if (!out) throw std::runtime_error("cannot write CNF");
    static std::vector<char> buffer(1 << 20);
    out.rdbuf()->pubsetbuf(buffer.data(), static_cast<std::streamsize>(buffer.size()));
    out << "c R4 exact packing; copy 0 fixed identity WLOG\n";
    out << "c p(c,i,u), a(c,e,h,o), y(c,h) for free copies c=1..4\n";
    out << "c a iff endpoint mappings; y iff OR of a; no other symmetry\n";
    out << "p cnf " << VARS << ' ' << CLAUSES << "\n";
    std::uint64_t count = 0;

    for (int c = 0; c < FREE_COPIES; ++c) {
      for (int i = 0; i < N; ++i) {
        for (int u = 0; u < N; ++u) out << pvar(c, i, u) << ' ';
        out << "0\n";
        ++count;
        for (int u = 0; u < N; ++u)
          for (int v = u + 1; v < N; ++v) {
            out << -pvar(c, i, u) << ' ' << -pvar(c, i, v) << " 0\n";
            ++count;
          }
      }
      for (int u = 0; u < N; ++u) {
        for (int i = 0; i < N; ++i) out << pvar(c, i, u) << ' ';
        out << "0\n";
        ++count;
        for (int i = 0; i < N; ++i)
          for (int j = i + 1; j < N; ++j) {
            out << -pvar(c, i, u) << ' ' << -pvar(c, j, u) << " 0\n";
            ++count;
          }
      }
    }

    for (int c = 0; c < FREE_COPIES; ++c)
      for (int e = 0; e < M; ++e)
        for (int h = 0; h < H; ++h)
          for (int o = 0; o < 2; ++o) {
            const auto [i, j] = g.edges[e];
            const auto [u, v] = g.host_edges[h];
            const int pi = o == 0 ? pvar(c, i, u) : pvar(c, i, v);
            const int pj = o == 0 ? pvar(c, j, v) : pvar(c, j, u);
            const int a = avar(c, e, h, o);
            const int y = yvar(c, h);
            out << -a << ' ' << pi << " 0\n";
            out << -a << ' ' << pj << " 0\n";
            out << -pi << ' ' << -pj << ' ' << a << " 0\n";
            out << -a << ' ' << y << " 0\n";
            count += 4;
          }

    for (int c = 0; c < FREE_COPIES; ++c)
      for (int h = 0; h < H; ++h) {
        out << -yvar(c, h) << ' ';
        for (int e = 0; e < M; ++e)
          for (int o = 0; o < 2; ++o) out << avar(c, e, h, o) << ' ';
        out << "0\n";
        ++count;
      }

    for (int c = 0; c < FREE_COPIES; ++c)
      for (const auto &[u, v] : g.edges) {
        out << -yvar(c, g.host_id[u][v]) << " 0\n";
        ++count;
      }

    for (int h = 0; h < H; ++h)
      for (int c = 0; c < FREE_COPIES; ++c)
        for (int d = c + 1; d < FREE_COPIES; ++d) {
          out << -yvar(c, h) << ' ' << -yvar(d, h) << " 0\n";
          ++count;
        }
    out.close();
    if (!out || count != CLAUSES) throw std::runtime_error("clause mismatch");
    std::cout << "R4_CNF_GENERATED vars=" << VARS << " clauses=" << count
              << " p=" << P_COUNT << " a=" << A_COUNT << " y=" << Y_COUNT
              << " permutation_alo=208 permutation_amo=67600"
              << " a_definition=" << 3 * A_COUNT
              << " a_implies_y=" << A_COUNT << " y_reverse=" << Y_COUNT
              << " fixed_copy_units=" << FREE_COPIES * M
              << " cross_copy_amo=" << 6 * H
              << " symmetry=copy0_identity_only\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "ERROR " << e.what() << "\n";
    return 1;
  }
}
