#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

struct Search {
  int n;
  int k;
  std::atomic<bool> found{false};
  std::atomic<std::uint64_t> leaves{0};
  std::mutex answer_mutex;
  std::vector<int> answer;

  bool maximal(const std::vector<int>& a,
               const std::vector<unsigned char>& used_diff) const {
    std::vector<unsigned char> in_set(n + 1, 0);
    for (int x : a) in_set[x] = 1;
    for (int x = 1; x <= n; ++x) {
      if (in_set[x]) continue;
      std::vector<unsigned char> new_diff(n + 1, 0);
      bool addable = true;
      for (int y : a) {
        int d = std::abs(x - y);
        if (used_diff[d] || new_diff[d]) {
          addable = false;
          break;
        }
        new_diff[d] = 1;
      }
      if (addable) return false;
    }
    return true;
  }

  void dfs(int next, std::vector<int>& a,
           std::vector<unsigned char>& used_diff) {
    if (found.load(std::memory_order_relaxed)) return;
    if (static_cast<int>(a.size()) == k) {
      leaves.fetch_add(1, std::memory_order_relaxed);
      if (maximal(a, used_diff)) {
        std::lock_guard<std::mutex> lock(answer_mutex);
        if (!found.exchange(true)) answer = a;
      }
      return;
    }
    int need = k - static_cast<int>(a.size());
    for (int x = next; x <= n - need + 1; ++x) {
      if (found.load(std::memory_order_relaxed)) return;
      std::vector<int> added;
      bool ok = true;
      for (int y : a) {
        int d = x - y;
        if (used_diff[d]) {
          ok = false;
          break;
        }
        added.push_back(d);
      }
      if (!ok) continue;
      for (int d : added) used_diff[d] = 1;
      a.push_back(x);
      dfs(x + 1, a, used_diff);
      a.pop_back();
      for (int d : added) used_diff[d] = 0;
    }
  }
};

int main(int argc, char** argv) {
  if (argc != 4) {
    std::cerr << "usage: small_maximal_search N K THREADS\n";
    return 2;
  }
  Search s;
  s.n = std::stoi(argv[1]);
  s.k = std::stoi(argv[2]);
  int threads = std::max(1, std::stoi(argv[3]));
  std::atomic<int> first{1};
  auto start = std::chrono::steady_clock::now();
  std::vector<std::thread> pool;
  for (int tid = 0; tid < threads; ++tid) {
    pool.emplace_back([&]() {
      while (!s.found.load(std::memory_order_relaxed)) {
        int x = first.fetch_add(1);
        if (x > s.n - s.k + 1) break;
        std::vector<int> a{x};
        std::vector<unsigned char> used_diff(s.n + 1, 0);
        s.dfs(x + 1, a, used_diff);
      }
    });
  }
  for (auto& t : pool) t.join();
  double sec = std::chrono::duration<double>(
                   std::chrono::steady_clock::now() - start)
                   .count();
  std::cout << "N=" << s.n << " K=" << s.k << " threads=" << threads
            << " leaves=" << s.leaves.load() << " seconds=" << sec << "\n";
  if (!s.found.load()) {
    std::cout << "NO_HIT\n";
    return 1;
  }
  std::cout << "HIT";
  for (int x : s.answer) std::cout << ' ' << x;
  std::cout << "\n";
  return 0;
}
