#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <limits>
#include <numeric>
#include <string>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

struct Rec {
  long long margin = std::numeric_limits<long long>::max();
  uint32_t mask = 0;
  long long lhs = 0;
  long long rhs = 0;
  int row = -1;
  int size = 0;
  int sigma = 0;
};

static bool better(const Rec& a, const Rec& b) {
  if (a.margin != b.margin) return a.margin < b.margin;
  if (a.mask != b.mask) return a.mask < b.mask;
  return a.row < b.row;
}

static void upd(Rec& dst, const Rec& cand) {
  if (better(cand, dst)) dst = cand;
}

static std::vector<int> vertices(uint32_t mask, int n) {
  std::vector<int> out;
  for (int i = 0; i < n; ++i) {
    if ((mask >> i) & 1u) out.push_back(i);
  }
  return out;
}

static void print_scaled(const std::string& key, long long x, long long scale) {
  long long g = std::gcd(std::llabs(x), scale);
  long long num = x / g;
  long long den = scale / g;
  std::cout << key << ": ";
  if (den == 1) {
    std::cout << num << "\n";
  } else {
    std::cout << num << "/" << den << "\n";
  }
}

static void print_rec(const std::string& label, const Rec& r, int n, long long scale,
                      const std::vector<std::vector<int>>& rows) {
  std::cout << label << ":\n";
  print_scaled("  margin", r.margin, scale);
  std::cout << "  row_index: " << r.row << "\n";
  if (r.row >= 0) {
    std::cout << "  row_vertices:";
    for (int v : rows[r.row]) std::cout << " " << v;
    std::cout << "\n";
  }
  std::cout << "  U:";
  for (int v : vertices(r.mask, n)) std::cout << " " << v;
  std::cout << "\n";
  print_scaled("  lhs", r.lhs, scale);
  print_scaled("  rhs", r.rhs, scale);
  std::cout << "  size: " << r.size << "\n";
  std::cout << "  sigma: " << r.sigma << "\n";
}

int main(int argc, char** argv) {
  int threads = 0;
  if (argc >= 2) threads = std::stoi(argv[1]);
#ifdef _OPENMP
  if (threads > 0) omp_set_num_threads(threads);
#endif

  int n;
  long long scale;
  long long eta_int;
  if (!(std::cin >> n >> scale >> eta_int)) return 2;
  const uint32_t subset_count = 1u << n;

  int nb;
  std::cin >> nb;
  std::vector<std::pair<int, int>> blue(nb);
  for (auto& e : blue) std::cin >> e.first >> e.second;

  int nm;
  std::cin >> nm;
  std::vector<std::pair<int, int>> bad(nm);
  for (auto& e : bad) std::cin >> e.first >> e.second;

  int natoms;
  std::cin >> natoms;
  std::vector<int32_t> tw(static_cast<size_t>(n) * subset_count, 0);
  long long atom_vertex_adds = 0;
  for (int a = 0; a < natoms; ++a) {
    int coeff, k;
    std::cin >> coeff >> k;
    uint32_t pmask = 0;
    std::vector<int> vs(k);
    for (int i = 0; i < k; ++i) {
      std::cin >> vs[i];
      pmask |= 1u << vs[i];
    }
    for (int v : vs) {
      tw[static_cast<size_t>(v) * subset_count + pmask] += coeff;
      ++atom_vertex_adds;
    }
  }

  int nrows;
  std::cin >> nrows;
  std::vector<std::vector<int>> rows(nrows);
  for (int r = 0; r < nrows; ++r) {
    int k;
    std::cin >> k;
    rows[r].resize(k);
    for (int i = 0; i < k; ++i) std::cin >> rows[r][i];
  }

  std::cout << "=== all-row Slack-CAGE zeta scanner ===\n";
  std::cout << "n: " << n << "\n";
  std::cout << "scale: " << scale << "\n";
  std::cout << "eta_int: " << eta_int << "\n";
  std::cout << "blue_edges: " << nb << "\n";
  std::cout << "bad_edges: " << nm << "\n";
  std::cout << "atoms: " << natoms << "\n";
  std::cout << "target_rows: " << nrows << "\n";
  std::cout << "atom_vertex_initial_adds: " << atom_vertex_adds << "\n";

  // Subset zeta transform: after completion tw[v, U] is the sum of all row
  // atom masses containing v whose row vertex set is a subset of U.
#pragma omp parallel for schedule(dynamic, 1)
  for (int v = 0; v < n; ++v) {
    int32_t* arr = tw.data() + static_cast<size_t>(v) * subset_count;
    for (int bit = 0; bit < n; ++bit) {
      uint32_t step = 1u << bit;
      uint32_t period = step << 1;
      for (uint32_t base = 0; base < subset_count; base += period) {
        for (uint32_t off = 0; off < step; ++off) {
          arr[base + off + step] += arr[base + off];
        }
      }
    }
  }

  std::vector<std::vector<std::pair<int, int>>> weights(n);
  std::vector<int> total(n, 0);
  for (auto [u, v] : blue) {
    weights[u].push_back({v, 1});
    weights[v].push_back({u, 1});
    total[u] += 1;
    total[v] += 1;
  }
  for (auto [u, v] : bad) {
    weights[u].push_back({v, -1});
    weights[v].push_back({u, -1});
    total[u] -= 1;
    total[v] -= 1;
  }

  std::vector<int16_t> sigma(subset_count, 0);
  for (uint32_t mask = 1; mask < subset_count; ++mask) {
    uint32_t lb = mask & (~mask + 1u);
    int v = __builtin_ctz(mask);
    uint32_t prev = mask ^ lb;
    int inside = 0;
    for (auto [u, w] : weights[v]) {
      if ((prev >> u) & 1u) inside += w;
    }
    sigma[mask] = static_cast<int16_t>(sigma[prev] + total[v] - 2 * inside);
  }

  Rec global_best, global_empty, global_full, global_proper;
  global_empty.margin = global_full.margin = global_proper.margin =
      std::numeric_limits<long long>::max();

#pragma omp parallel
  {
    Rec local_best, local_empty, local_full, local_proper;
    local_empty.margin = local_full.margin = local_proper.margin =
        std::numeric_limits<long long>::max();
    std::array<int32_t, 64> vals{};

#pragma omp for schedule(static)
    for (int64_t signed_mask = 0; signed_mask < static_cast<int64_t>(subset_count); ++signed_mask) {
      uint32_t mask = static_cast<uint32_t>(signed_mask);
      for (int v = 0; v < n; ++v) {
        vals[v] = tw[static_cast<size_t>(v) * subset_count + mask];
      }
      long long best_lhs = std::numeric_limits<long long>::min();
      int best_row = -1;
      for (int r = 0; r < nrows; ++r) {
        long long lhs = 0;
        for (int v : rows[r]) lhs += vals[v];
        if (lhs > best_lhs) {
          best_lhs = lhs;
          best_row = r;
        }
      }
      int pc = __builtin_popcount(mask);
      long long rhs = (static_cast<long long>(pc) + sigma[mask]) * scale + eta_int;
      Rec rec;
      rec.margin = rhs - best_lhs;
      rec.mask = mask;
      rec.lhs = best_lhs;
      rec.rhs = rhs;
      rec.row = best_row;
      rec.size = pc;
      rec.sigma = sigma[mask];
      upd(local_best, rec);
      if (mask == 0) {
        upd(local_empty, rec);
      } else if (mask + 1u == subset_count) {
        upd(local_full, rec);
      } else {
        upd(local_proper, rec);
      }
    }

#pragma omp critical
    {
      upd(global_best, local_best);
      upd(global_empty, local_empty);
      upd(global_full, local_full);
      upd(global_proper, local_proper);
    }
  }

  print_rec("min_all", global_best, n, scale, rows);
  print_rec("min_empty", global_empty, n, scale, rows);
  print_rec("min_full", global_full, n, scale, rows);
  print_rec("min_proper", global_proper, n, scale, rows);
  std::cout << "VERDICT: " << (global_best.margin >= 0 ? "HOLDS" : "FAILS") << "\n";
  return global_best.margin >= 0 ? 0 : 1;
}
