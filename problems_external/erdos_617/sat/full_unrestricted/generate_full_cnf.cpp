#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

static constexpr int N = 26;
static constexpr int Q = 5;
static constexpr int EDGES = N * (N - 1) / 2;
static constexpr std::uint64_t SIX_SETS = 230230;
static constexpr std::uint64_t COVERAGE = SIX_SETS * Q;
static constexpr std::uint64_t CLAUSES =
    EDGES + EDGES * (Q * (Q - 1) / 2) + 1 + COVERAGE;

static int edge_id(int u, int v) {
  if (!(0 <= u && u < v && v < N)) throw std::runtime_error("bad edge");
  return u * (2 * N - u - 1) / 2 + (v - u - 1);
}

static int var(int u, int v, int c) {
  return Q * edge_id(u, v) + c + 1;
}

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
      std::cerr << "usage: generate_full_cnf OUT.cnf\n";
      return 64;
    }
    std::ofstream out(argv[1], std::ios::binary);
    if (!out) throw std::runtime_error("cannot write output");
    static std::vector<char> buffer(1 << 20);
    out.rdbuf()->pubsetbuf(buffer.data(), static_cast<std::streamsize>(buffer.size()));
    out << "c unrestricted Erdos 617 instance: K26, five edge colours\n";
    out << "c edge_id(u,v)=u*(51-u)/2+(v-u-1), u<v\n";
    out << "c variable(u,v,c)=5*edge_id(u,v)+c+1\n";
    out << "c WLOG normalization colour(0,1)=0; no other symmetry breaking\n";
    out << "p cnf " << EDGES * Q << ' ' << CLAUSES << "\n";

    std::uint64_t alo = 0, amo = 0, normalization = 0, coverage = 0;
    for (int u = 0; u < N; ++u)
      for (int v = u + 1; v < N; ++v) {
        for (int c = 0; c < Q; ++c) out << var(u, v, c) << ' ';
        out << "0\n";
        ++alo;
        for (int c = 0; c < Q; ++c)
          for (int d = c + 1; d < Q; ++d) {
            out << -var(u, v, c) << ' ' << -var(u, v, d) << " 0\n";
            ++amo;
          }
      }

    out << var(0, 1, 0) << " 0\n";
    ++normalization;

    std::array<int, 6> a{0, 1, 2, 3, 4, 5};
    std::uint64_t six_sets = 0;
    do {
      ++six_sets;
      for (int c = 0; c < Q; ++c) {
        for (int i = 0; i < 6; ++i)
          for (int j = i + 1; j < 6; ++j)
            out << var(a[i], a[j], c) << ' ';
        out << "0\n";
        ++coverage;
      }
    } while (next6(a));
    out.close();
    if (!out) throw std::runtime_error("write failure");
    if (six_sets != SIX_SETS || coverage != COVERAGE ||
        alo + amo + normalization + coverage != CLAUSES)
      throw std::runtime_error("internal count mismatch");
    std::cout << "FULL_CNF_GENERATED vars=" << EDGES * Q
              << " clauses=" << CLAUSES << " edges=" << EDGES
              << " alo=" << alo << " amo=" << amo
              << " normalization=" << normalization
              << " six_sets=" << six_sets << " coverage=" << coverage
              << " symmetry_breakers=1\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "ERROR " << e.what() << "\n";
    return 1;
  }
}
