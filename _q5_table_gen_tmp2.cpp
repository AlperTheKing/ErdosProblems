#include <algorithm>
#include <array>
#include <cstdint>
#include <functional>
#include <iostream>
#include <numeric>
#include <queue>
#include <vector>

namespace {

std::uint64_t floor_sum(std::uint64_t n, std::uint64_t m,
                        std::uint64_t a, std::uint64_t b) {
  std::uint64_t answer = 0;
  while (true) {
    if (a >= m) {
      answer += (n - 1) * n * (a / m) / 2;
      a %= m;
    }
    if (b >= m) {
      answer += n * (b / m);
      b %= m;
    }
    const std::uint64_t y_max = a * n + b;
    if (y_max < m) {
      return answer;
    }
    n = y_max / m;
    b = y_max % m;
    std::swap(m, a);
  }
}

std::uint64_t work(std::uint64_t h, std::uint64_t p, std::uint64_t q) {
  const std::uint64_t uncapped = std::min(h, h * q / p);
  return h * h + floor_sum(uncapped, q, p, p - 1) +
         (h - uncapped) * h;
}

struct Job { std::uint64_t weight, p, q; };

}  // namespace

int main() {
  std::cout << "(";
  for (std::uint64_t h = 48; h <= 512; ++h) {
    std::vector<Job> jobs;
    for (std::uint64_t p = 1; p <= h; ++p) {
      for (std::uint64_t q = 1; q <= h; ++q) {
        if (std::gcd(p, q) == 1) jobs.push_back({work(h, p, q), p, q});
      }
    }
    std::sort(jobs.begin(), jobs.end(), [](const Job &l, const Job &r) {
      if (l.weight != r.weight) return l.weight > r.weight;
      if (l.p != r.p) return l.p < r.p;
      return l.q < r.q;
    });
    using Lane = std::pair<std::uint64_t, std::uint64_t>;
    std::priority_queue<Lane, std::vector<Lane>, std::greater<Lane>> heap;
    std::array<std::uint64_t, 64> loads{};
    for (std::uint64_t lane = 0; lane < 64; ++lane) heap.emplace(0, lane);
    for (const auto &job : jobs) {
      auto [load, lane] = heap.top(); heap.pop();
      loads[lane] = load + job.weight;
      heap.emplace(loads[lane], lane);
    }
    const auto mm = std::minmax_element(loads.begin(), loads.end());
    if (h != 48) std::cout << ',';
    std::cout << '(' << *mm.first << ',' << *mm.second << ')';
  }
  std::cout << ")\n";
}
