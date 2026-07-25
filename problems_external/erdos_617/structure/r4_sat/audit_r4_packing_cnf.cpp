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

static constexpr int N = 26, M = 61, H = 325, C = 4;
static constexpr int PCOUNT = C * N * N, ACOUNT = C * M * H * 2;
static constexpr int YCOUNT = C * H, VARS = PCOUNT + ACOUNT + YCOUNT;
static constexpr int CLAUSES = 705702;

struct Tables {
  std::vector<std::pair<int, int>> source;
  std::vector<std::pair<int, int>> host;
  std::array<std::array<int, N>, N> host_id{};
  std::vector<unsigned char> source_host_edge;
};

static Tables tables(const std::string &path) {
  Tables t;
  for (auto &row : t.host_id) row.fill(-1);
  for (int u = 0; u < N; ++u)
    for (int v = u + 1; v < N; ++v) {
      t.host_id[u][v] = t.host_id[v][u] = static_cast<int>(t.host.size());
      t.host.push_back({u, v});
    }
  t.source_host_edge.assign(H, 0);
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot read graph");
  std::string line;
  int dn = -1, dm = -1;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == 'c') continue;
    std::istringstream s(line);
    char tag;
    s >> tag;
    if (tag == 'p') {
      std::string kind;
      if (!(s >> kind >> dn >> dm) || kind != "edge")
        throw std::runtime_error("graph header");
    } else if (tag == 'e') {
      int u, v;
      if (!(s >> u >> v) || u < 0 || u >= v || v >= N)
        throw std::runtime_error("graph edge");
      const int h = t.host_id[u][v];
      if (t.source_host_edge[h]) throw std::runtime_error("duplicate graph edge");
      t.source_host_edge[h] = 1;
      t.source.push_back({u, v});
    } else {
      throw std::runtime_error("graph record");
    }
  }
  if (dn != N || dm != M || t.source.size() != M)
    throw std::runtime_error("graph count");
  return t;
}

static int pv(int c, int i, int u) { return 1 + (c * N + i) * N + u; }
static int av(int c, int e, int h, int o) {
  return 1 + PCOUNT + (((c * M + e) * H + h) * 2 + o);
}
static int yv(int c, int h) { return 1 + PCOUNT + ACOUNT + c * H + h; }
static bool is_p(int x) { return 1 <= x && x <= PCOUNT; }
static bool is_a(int x) { return PCOUNT < x && x <= PCOUNT + ACOUNT; }
static bool is_y(int x) { return PCOUNT + ACOUNT < x && x <= VARS; }

static void decode_p(int x, int &c, int &i, int &u) {
  int z = x - 1;
  u = z % N;
  z /= N;
  i = z % N;
  c = z / N;
}
static void decode_a(int x, int &c, int &e, int &h, int &o) {
  int z = x - 1 - PCOUNT;
  o = z % 2;
  z /= 2;
  h = z % H;
  z /= H;
  e = z % M;
  c = z / M;
}
static void decode_y(int x, int &c, int &h) {
  const int z = x - 1 - PCOUNT - ACOUNT;
  h = z % H;
  c = z / H;
}
static int pair_rank(int a, int b, int n) {
  if (a > b) std::swap(a, b);
  return a * (2 * n - a - 1) / 2 + b - a - 1;
}

int main(int argc, char **argv) {
  try {
    if (argc != 3) {
      std::cerr << "usage: audit_r4_packing_cnf G61.edges INSTANCE.cnf\n";
      return 64;
    }
    const Tables t = tables(argv[1]);
    std::vector<unsigned char> row_alo(C * N), col_alo(C * N);
    std::vector<unsigned char> row_amo(C * N * H), col_amo(C * N * H);
    std::vector<unsigned char> a_to_p(ACOUNT), a_def(ACOUNT), a_to_y(ACOUNT);
    std::vector<unsigned char> y_reverse(YCOUNT), fixed(YCOUNT);
    std::vector<unsigned char> y_amo(H * 6);

    std::ifstream in(argv[2], std::ios::binary);
    if (!in) throw std::runtime_error("cannot read CNF");
    std::string line;
    bool header = false;
    int parsed = 0;
    while (std::getline(in, line)) {
      if (line.empty() || line[0] == 'c') continue;
      if (line[0] == 'p') {
        std::istringstream s(line);
        char p;
        std::string cnf;
        int vars, clauses;
        if (header || !(s >> p >> cnf >> vars >> clauses) || cnf != "cnf" ||
            vars != VARS || clauses != CLAUSES)
          throw std::runtime_error("CNF header");
        header = true;
        continue;
      }
      if (!header) throw std::runtime_error("clause before header");
      std::istringstream s(line);
      std::vector<int> q;
      int literal;
      bool zero = false;
      while (s >> literal) {
        if (!literal) {
          zero = true;
          break;
        }
        if (std::abs(literal) > VARS) throw std::runtime_error("literal range");
        q.push_back(literal);
      }
      if (!zero || q.empty()) throw std::runtime_error("bad clause");
      ++parsed;

      if (q.size() == 26) {
        for (int x : q)
          if (x <= 0 || !is_p(x)) throw std::runtime_error("bad P ALO");
        int c0, i0, u0;
        decode_p(q[0], c0, i0, u0);
        bool row = true, col = true;
        std::array<bool, N> row_values{}, col_values{};
        for (int x : q) {
          int c, i, u;
          decode_p(x, c, i, u);
          if (c != c0 || i != i0) row = false;
          if (c != c0 || u != u0) col = false;
          row_values[u] = true;
          col_values[i] = true;
        }
        if (row && std::all_of(row_values.begin(), row_values.end(),
                              [](bool x) { return x; })) {
          if (row_alo[c0 * N + i0]++) throw std::runtime_error("duplicate row ALO");
        } else if (col && std::all_of(col_values.begin(), col_values.end(),
                                     [](bool x) { return x; })) {
          if (col_alo[c0 * N + u0]++) throw std::runtime_error("duplicate col ALO");
        } else {
          throw std::runtime_error("bad P ALO identity");
        }
      } else if (q.size() == 3) {
        int apos = -1;
        std::vector<int> negp;
        for (int x : q) {
          if (x > 0 && is_a(x)) apos = x;
          else if (x < 0 && is_p(-x)) negp.push_back(-x);
          else throw std::runtime_error("bad A definition signs");
        }
        if (apos < 0 || negp.size() != 2) throw std::runtime_error("bad A definition");
        int c, e, h, o;
        decode_a(apos, c, e, h, o);
        const auto [i, j] = t.source[e];
        const auto [u, v] = t.host[h];
        std::array<int, 2> want{
            o == 0 ? pv(c, i, u) : pv(c, i, v),
            o == 0 ? pv(c, j, v) : pv(c, j, u)};
        std::sort(want.begin(), want.end());
        std::sort(negp.begin(), negp.end());
        if (negp[0] != want[0] || negp[1] != want[1])
          throw std::runtime_error("wrong A definition");
        const int ai = apos - 1 - PCOUNT;
        if (a_def[ai]++) throw std::runtime_error("duplicate A definition");
      } else if (q.size() == 123) {
        int negative_y = -1;
        std::vector<int> positives;
        for (int x : q) {
          if (x < 0 && is_y(-x)) negative_y = -x;
          else if (x > 0 && is_a(x)) positives.push_back(x);
          else throw std::runtime_error("bad reverse Y signs");
        }
        if (negative_y < 0 || positives.size() != 122)
          throw std::runtime_error("bad reverse Y arity");
        int c, h;
        decode_y(negative_y, c, h);
        std::vector<int> want;
        for (int e = 0; e < M; ++e)
          for (int o = 0; o < 2; ++o) want.push_back(av(c, e, h, o));
        std::sort(want.begin(), want.end());
        std::sort(positives.begin(), positives.end());
        if (positives != want) throw std::runtime_error("wrong reverse Y");
        const int yi = negative_y - 1 - PCOUNT - ACOUNT;
        if (y_reverse[yi]++) throw std::runtime_error("duplicate reverse Y");
      } else if (q.size() == 1) {
        if (q[0] >= 0 || !is_y(-q[0])) throw std::runtime_error("bad fixed unit");
        int c, h;
        decode_y(-q[0], c, h);
        if (!t.source_host_edge[h]) throw std::runtime_error("unit not fixed edge");
        const int yi = c * H + h;
        if (fixed[yi]++) throw std::runtime_error("duplicate fixed unit");
      } else if (q.size() == 2) {
        const int x = q[0], z = q[1];
        if (x < 0 && z < 0 && is_p(-x) && is_p(-z)) {
          int c1, i1, u1, c2, i2, u2;
          decode_p(-x, c1, i1, u1);
          decode_p(-z, c2, i2, u2);
          if (c1 != c2) throw std::runtime_error("cross-copy P AMO");
          if (i1 == i2 && u1 != u2) {
            const int r = pair_rank(u1, u2, N);
            const int idx = (c1 * N + i1) * H + r;
            if (row_amo[idx]++) throw std::runtime_error("duplicate row AMO");
          } else if (u1 == u2 && i1 != i2) {
            const int r = pair_rank(i1, i2, N);
            const int idx = (c1 * N + u1) * H + r;
            if (col_amo[idx]++) throw std::runtime_error("duplicate col AMO");
          } else {
            throw std::runtime_error("bad P AMO");
          }
        } else if (x < 0 && z < 0 && is_y(-x) && is_y(-z)) {
          int c1, h1, c2, h2;
          decode_y(-x, c1, h1);
          decode_y(-z, c2, h2);
          if (h1 != h2 || c1 == c2) throw std::runtime_error("bad Y AMO");
          const int idx = h1 * 6 + pair_rank(c1, c2, C);
          if (y_amo[idx]++) throw std::runtime_error("duplicate Y AMO");
        } else {
          int aneg = -1, positive = -1;
          for (int w : q) {
            if (w < 0 && is_a(-w)) aneg = -w;
            else if (w > 0 && (is_p(w) || is_y(w))) positive = w;
            else throw std::runtime_error("bad A implication");
          }
          if (aneg < 0 || positive < 0) throw std::runtime_error("bad implication");
          int c, e, h, o;
          decode_a(aneg, c, e, h, o);
          const int ai = aneg - 1 - PCOUNT;
          if (is_p(positive)) {
            const auto [i, j] = t.source[e];
            const auto [u, v] = t.host[h];
            const int p1 = o == 0 ? pv(c, i, u) : pv(c, i, v);
            const int p2 = o == 0 ? pv(c, j, v) : pv(c, j, u);
            unsigned char bit = positive == p1 ? 1 : positive == p2 ? 2 : 0;
            if (!bit || (a_to_p[ai] & bit)) throw std::runtime_error("wrong A->P");
            a_to_p[ai] |= bit;
          } else {
            if (positive != yv(c, h) || a_to_y[ai]++)
              throw std::runtime_error("wrong A->Y");
          }
        }
      } else {
        throw std::runtime_error("unexpected clause length");
      }
    }
    if (!header || parsed != CLAUSES) throw std::runtime_error("final clause count");
    auto all_one = [](const auto &v) {
      return std::all_of(v.begin(), v.end(), [](auto x) { return x == 1; });
    };
    if (!all_one(row_alo) || !all_one(col_alo) || !all_one(row_amo) ||
        !all_one(col_amo) || !all_one(a_def) || !all_one(a_to_y) ||
        !all_one(y_reverse) || !all_one(y_amo))
      throw std::runtime_error("missing required clause");
    if (!std::all_of(a_to_p.begin(), a_to_p.end(),
                     [](unsigned char x) { return x == 3; }))
      throw std::runtime_error("incomplete A->P");
    for (int c = 0; c < C; ++c)
      for (int h = 0; h < H; ++h)
        if (fixed[c * H + h] != t.source_host_edge[h])
          throw std::runtime_error("fixed unit set mismatch");
    std::cout << "R4_CNF_AUDIT_OK vars=" << VARS << " clauses=" << CLAUSES
              << " p=" << PCOUNT << " a=" << ACOUNT << " y=" << YCOUNT
              << " bidirectional_a=1 bidirectional_y=1"
              << " symmetry=copy0_identity_only\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "R4_CNF_AUDIT_FAIL " << e.what() << "\n";
    return 1;
  }
}
