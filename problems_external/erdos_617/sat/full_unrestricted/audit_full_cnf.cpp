#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

static constexpr int N = 26, Q = 5, EDGES = 325, VARS = 1625;
static constexpr int SIX_SETS = 230230, COVERAGE = SIX_SETS * Q;
static constexpr int EXPECTED_CLAUSES = 1154726;

struct Endpoints {
  int u, v;
};

static std::vector<Endpoints> make_endpoints() {
  std::vector<Endpoints> result;
  for (int u = 0; u < N; ++u)
    for (int v = u + 1; v < N; ++v) result.push_back({u, v});
  if (result.size() != EDGES) throw std::runtime_error("edge table failure");
  return result;
}

static std::unordered_map<std::uint32_t, int> make_six_set_ranks() {
  std::unordered_map<std::uint32_t, int> ranks;
  ranks.reserve(SIX_SETS * 2);
  int rank = 0;
  for (int a = 0; a < 21; ++a)
    for (int b = a + 1; b < 22; ++b)
      for (int c = b + 1; c < 23; ++c)
        for (int d = c + 1; d < 24; ++d)
          for (int e = d + 1; e < 25; ++e)
            for (int f = e + 1; f < 26; ++f) {
              const std::uint32_t mask = (std::uint32_t{1} << a) |
                                         (std::uint32_t{1} << b) |
                                         (std::uint32_t{1} << c) |
                                         (std::uint32_t{1} << d) |
                                         (std::uint32_t{1} << e) |
                                         (std::uint32_t{1} << f);
              ranks.emplace(mask, rank++);
            }
  if (rank != SIX_SETS || ranks.size() != SIX_SETS)
    throw std::runtime_error("six-set rank table failure");
  return ranks;
}

int main(int argc, char **argv) {
  try {
    if (argc != 2) {
      std::cerr << "usage: audit_full_cnf INSTANCE.cnf\n";
      return 64;
    }
    const auto endpoints = make_endpoints();
    const auto ranks = make_six_set_ranks();
    std::array<std::array<int, N>, N> edge_lookup{};
    for (auto &row : edge_lookup) row.fill(-1);
    for (int e = 0; e < EDGES; ++e) {
      edge_lookup[endpoints[e].u][endpoints[e].v] = e;
      edge_lookup[endpoints[e].v][endpoints[e].u] = e;
    }
    std::vector<unsigned char> alo_seen(EDGES, 0);
    std::vector<unsigned short> amo_seen(EDGES, 0);
    std::vector<unsigned char> coverage_seen(COVERAGE, 0);
    bool normalization_seen = false;
    int parsed_clauses = 0;

    std::ifstream in(argv[1], std::ios::binary);
    if (!in) throw std::runtime_error("cannot read CNF");
    std::string line;
    bool header = false;
    while (std::getline(in, line)) {
      if (line.empty() || line[0] == 'c') continue;
      if (line[0] == 'p') {
        std::istringstream s(line);
        char p;
        std::string cnf, extra;
        int vars, clauses;
        if (header || !(s >> p >> cnf >> vars >> clauses) || (s >> extra) ||
            cnf != "cnf" || vars != VARS || clauses != EXPECTED_CLAUSES)
          throw std::runtime_error("header mismatch");
        header = true;
        continue;
      }
      if (!header) throw std::runtime_error("clause before header");
      std::istringstream s(line);
      std::vector<int> clause;
      int x;
      bool zero = false;
      while (s >> x) {
        if (x == 0) {
          zero = true;
          std::string extra;
          if (s >> extra) throw std::runtime_error("data after zero");
          break;
        }
        if (std::abs(x) > VARS) throw std::runtime_error("literal range");
        clause.push_back(x);
      }
      if (!zero || clause.empty()) throw std::runtime_error("bad clause");
      ++parsed_clauses;

      if (clause.size() == 1) {
        if (clause[0] != 1 || normalization_seen)
          throw std::runtime_error("bad normalization");
        normalization_seen = true;
      } else if (clause.size() == 2) {
        if (clause[0] >= 0 || clause[1] >= 0)
          throw std::runtime_error("nonnegative binary");
        const int a = -clause[0] - 1, b = -clause[1] - 1;
        if (a / Q != b / Q || a % Q >= b % Q)
          throw std::runtime_error("bad at-most-one");
        const int pair_index = (a % Q) * (2 * Q - (a % Q) - 1) / 2 +
                               (b % Q - a % Q - 1);
        const unsigned short bit = static_cast<unsigned short>(1u << pair_index);
        if (amo_seen[a / Q] & bit) throw std::runtime_error("duplicate AMO");
        amo_seen[a / Q] |= bit;
      } else if (clause.size() == 5) {
        const int first = clause[0] - 1;
        if (first < 0 || first % Q != 0)
          throw std::runtime_error("bad at-least-one start");
        const int edge = first / Q;
        if (edge >= EDGES || alo_seen[edge])
          throw std::runtime_error("duplicate or bad ALO");
        for (int c = 0; c < Q; ++c)
          if (clause[c] != edge * Q + c + 1)
            throw std::runtime_error("bad at-least-one");
        alo_seen[edge] = 1;
      } else if (clause.size() == 15) {
        int colour = -1;
        std::uint32_t vertex_mask = 0;
        std::array<unsigned char, EDGES> edge_seen{};
        for (int literal : clause) {
          if (literal <= 0) throw std::runtime_error("negative coverage literal");
          const int z = literal - 1, edge = z / Q, c = z % Q;
          if (colour < 0) colour = c;
          if (c != colour || edge >= EDGES || edge_seen[edge])
            throw std::runtime_error("coverage colour/edge mismatch");
          edge_seen[edge] = 1;
          vertex_mask |= std::uint32_t{1} << endpoints[edge].u;
          vertex_mask |= std::uint32_t{1} << endpoints[edge].v;
        }
        if (__builtin_popcount(vertex_mask) != 6)
          throw std::runtime_error("coverage is not on six vertices");
        std::array<int, 6> vertices{};
        int k = 0;
        for (int v = 0; v < N; ++v)
          if (vertex_mask & (std::uint32_t{1} << v)) vertices[k++] = v;
        for (int i = 0; i < 6; ++i)
          for (int j = i + 1; j < 6; ++j)
            if (!edge_seen[edge_lookup[vertices[i]][vertices[j]]])
              throw std::runtime_error("coverage omits induced edge");
        const auto it = ranks.find(vertex_mask);
        if (it == ranks.end()) throw std::runtime_error("unranked six-set");
        const int index = Q * it->second + colour;
        if (coverage_seen[index]) throw std::runtime_error("duplicate coverage");
        coverage_seen[index] = 1;
      } else {
        throw std::runtime_error("unexpected clause length");
      }
    }
    if (!header || parsed_clauses != EXPECTED_CLAUSES || !normalization_seen)
      throw std::runtime_error("final count/normalization mismatch");
    for (int e = 0; e < EDGES; ++e)
      if (!alo_seen[e] || amo_seen[e] != 0x3ff)
        throw std::runtime_error("incomplete exactly-one block");
    if (std::find(coverage_seen.begin(), coverage_seen.end(), 0) !=
        coverage_seen.end())
      throw std::runtime_error("missing coverage clause");
    std::cout << "FULL_CNF_AUDIT_OK vars=1625 clauses=1154726 edges=325"
              << " alo=325 amo=3250 normalization=1"
              << " six_sets=230230 coverage=1151150"
              << " symmetry_breakers=1\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "FULL_CNF_AUDIT_FAIL " << e.what() << "\n";
    return 1;
  }
}
