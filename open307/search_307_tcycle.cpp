#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <numeric>
#include <random>
#include <string>
#include <thread>
#include <vector>

using u64 = std::uint64_t;
using u128 = unsigned __int128;

struct Task {
  int start = 0;
  u64 D = 1;
  u128 N = 0;
  long double sum = 0;
  std::vector<int> elems;
};

struct Factor {
  u64 p = 0;
  int e = 0;
};

static std::atomic<bool> found(false);
static std::atomic<u64> tested(0), factored(0), squarefree(0), congruent(0);
static std::mutex out_mu;
static std::chrono::steady_clock::time_point t0;
static int seconds_limit = 0;

static std::string u128s(u128 x) {
  if (x == 0) return "0";
  std::string s;
  while (x) {
    s.push_back(char('0' + x % 10));
    x /= 10;
  }
  std::reverse(s.begin(), s.end());
  return s;
}

static bool timed_out() {
  return seconds_limit > 0 &&
         std::chrono::duration_cast<std::chrono::seconds>(
             std::chrono::steady_clock::now() - t0).count() >= seconds_limit;
}

static u64 gcd64(u64 a, u64 b) {
  while (b) {
    u64 r = a % b;
    a = b;
    b = r;
  }
  return a;
}

static u64 mul_mod(u64 a, u64 b, u64 m) {
  return (u64)((u128)a * b % m);
}

static u64 pow_mod(u64 a, u64 e, u64 m) {
  u64 r = 1 % m;
  while (e) {
    if (e & 1) r = mul_mod(r, a, m);
    a = mul_mod(a, a, m);
    e >>= 1;
  }
  return r;
}

static bool is_prime64(u64 n) {
  if (n < 2) return false;
  for (u64 p : {2ULL, 3ULL, 5ULL, 7ULL, 11ULL, 13ULL, 17ULL, 19ULL, 23ULL,
                29ULL, 31ULL, 37ULL}) {
    if (n % p == 0) return n == p;
  }
  u64 d = n - 1;
  int s = 0;
  while ((d & 1) == 0) {
    d >>= 1;
    ++s;
  }
  for (u64 a : {2ULL, 325ULL, 9375ULL, 28178ULL, 450775ULL, 9780504ULL,
                1795265022ULL}) {
    if (a % n == 0) continue;
    u64 x = pow_mod(a % n, d, n);
    if (x == 1 || x == n - 1) continue;
    bool ok = false;
    for (int r = 1; r < s; ++r) {
      x = mul_mod(x, x, n);
      if (x == n - 1) {
        ok = true;
        break;
      }
    }
    if (!ok) return false;
  }
  return true;
}

static u64 pollard(u64 n, std::mt19937_64& rng) {
  if ((n & 1) == 0) return 2;
  if (n % 3 == 0) return 3;
  std::uniform_int_distribution<u64> dist(2, n - 2);
  while (true) {
    u64 c = dist(rng);
    u64 x = dist(rng);
    u64 y = x;
    u64 d = 1;
    auto f = [&](u64 v) { return (mul_mod(v, v, n) + c) % n; };
    for (int iter = 0; d == 1 && iter < 20000; ++iter) {
      x = f(x);
      y = f(f(y));
      u64 diff = x > y ? x - y : y - x;
      d = gcd64(diff, n);
    }
    if (d > 1 && d < n) return d;
  }
}

static void factor_rec(u64 n, std::vector<u64>& fs, std::mt19937_64& rng) {
  if (n == 1) return;
  if (is_prime64(n)) {
    fs.push_back(n);
    return;
  }
  u64 d = pollard(n, rng);
  factor_rec(d, fs, rng);
  factor_rec(n / d, fs, rng);
}

static bool factor_squarefree(u64 n, std::vector<u64>& primes, std::mt19937_64& rng) {
  std::vector<u64> fs;
  factor_rec(n, fs, rng);
  std::sort(fs.begin(), fs.end());
  primes.clear();
  for (std::size_t i = 0; i < fs.size();) {
    std::size_t j = i + 1;
    while (j < fs.size() && fs[j] == fs[i]) ++j;
    if (j - i != 1) return false;
    primes.push_back(fs[i]);
    i = j;
  }
  return true;
}

static std::vector<int> primes_upto(int n) {
  std::vector<char> comp(n + 1);
  std::vector<int> ps;
  for (int i = 2; i <= n; ++i) {
    if (comp[i]) continue;
    ps.push_back(i);
    if (1LL * i * i <= n) {
      for (long long j = 1LL * i * i; j <= n; j += i) comp[(int)j] = 1;
    }
  }
  return ps;
}

static long double max_tail_sum(const std::vector<int>& primes, int start, int slots) {
  long double s = 0;
  for (int i = start; i < (int)primes.size() && slots > 0; ++i, --slots) {
    s += 1.0L / primes[i];
  }
  return s;
}

static void emit_witness(const std::vector<int>& P, const std::vector<u64>& Q, u64 D, u64 N,
                         u128 NQ) {
  std::lock_guard<std::mutex> lock(out_mu);
  if (found.exchange(true)) return;
  std::cout << "WITNESS_FOUND\nP";
  for (int p : P) std::cout << ' ' << p;
  std::cout << "\nDp " << D << "\nNp " << N << "\nQ";
  for (u64 q : Q) std::cout << ' ' << q;
  std::cout << "\nDq " << N << "\nNq " << u128s(NQ) << "\n";
}

static void test_set(const std::vector<int>& P, u64 D, u128 N128, std::mt19937_64& rng) {
  tested.fetch_add(1, std::memory_order_relaxed);
  if (N128 <= D || N128 > UINT64_MAX) return;
  u64 N = (u64)N128;
  if (gcd64(D, N) != 1) return;
  factored.fetch_add(1, std::memory_order_relaxed);

  std::vector<u64> Q;
  if (!factor_squarefree(N, Q, rng) || Q.size() < 2) return;
  squarefree.fetch_add(1, std::memory_order_relaxed);

  for (int p : P) {
    u64 mod = (u64)p;
    u64 sm = 0;
    for (u64 q : Q) sm = (sm + (N / q) % mod) % mod;
    if (sm != 0) return;
  }
  congruent.fetch_add(1, std::memory_order_relaxed);

  u128 NQ = 0;
  for (u64 q : Q) NQ += (u128)N / q;
  if (NQ == D) emit_witness(P, Q, D, N, NQ);
}

static void dfs(const std::vector<int>& primes, int start, int max_size, u64 bound, u64 D,
                u128 N, long double sum, std::vector<int>& elems, std::mt19937_64& rng) {
  if (found.load(std::memory_order_relaxed) || timed_out()) return;
  int size = (int)elems.size();
  if (size >= 2 && sum > 1.0L) test_set(elems, D, N, rng);
  if (size >= max_size) return;
  if (sum + max_tail_sum(primes, start, max_size - size) <= 1.0L) return;

  for (int i = start; i < (int)primes.size(); ++i) {
    int p = primes[i];
    if (D > bound / (u64)p) break;
    u64 D2 = D * (u64)p;
    u128 N2 = N * (u128)p + D;
    elems.push_back(p);
    dfs(primes, i + 1, max_size, bound, D2, N2, sum + 1.0L / p, elems, rng);
    elems.pop_back();
    if (found.load(std::memory_order_relaxed) || timed_out()) return;
  }
}

int main(int argc, char** argv) {
  if (argc < 7) {
    std::cerr << "usage: search_307_tcycle pmax maxSize productBound threads seconds mode\n";
    std::cerr << "mode: include2 | no2 | both\n";
    return 2;
  }
  int pmax = std::stoi(argv[1]);
  int max_size = std::stoi(argv[2]);
  u64 bound = std::stoull(argv[3]);
  int threads = std::max(1, std::stoi(argv[4]));
  seconds_limit = std::stoi(argv[5]);
  std::string mode = argv[6];
  t0 = std::chrono::steady_clock::now();

  auto primes = primes_upto(pmax);
  std::vector<Task> tasks;
  int idx2 = (primes.size() && primes[0] == 2) ? 0 : -1;
  if ((mode == "include2" || mode == "both") && idx2 == 0) {
    for (int j = 1; j < (int)primes.size(); ++j) {
      int p = primes[j];
      if ((u64)2 > bound / (u64)p) break;
      tasks.push_back({j + 1, (u64)2 * p, (u128)p + 2, 0.5L + 1.0L / p, {2, p}});
    }
  }
  if (mode == "no2" || mode == "both") {
    for (int j = 1; j < (int)primes.size(); ++j) {
      int p = primes[j];
      tasks.push_back({j + 1, (u64)p, 1, 1.0L / p, {p}});
    }
  }

  std::atomic<std::size_t> next{0};
  auto worker = [&](int tid) {
    std::mt19937_64 rng(0x3077c1c1eULL + 0x9e3779b97f4a7c15ULL * (tid + 1));
    while (!found.load(std::memory_order_relaxed) && !timed_out()) {
      std::size_t id = next.fetch_add(1, std::memory_order_relaxed);
      if (id >= tasks.size()) break;
      Task task = tasks[id];
      dfs(primes, task.start, max_size, bound, task.D, task.N, task.sum, task.elems, rng);
      if (tid == 0) {
        auto elapsed = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - t0).count();
        std::lock_guard<std::mutex> lock(out_mu);
        std::cerr << "progress tasks=" << next.load() << "/" << tasks.size()
                  << " tested=" << tested.load() << " factored=" << factored.load()
                  << " squarefree=" << squarefree.load() << " congruent=" << congruent.load()
                  << " elapsed=" << elapsed << "s\n";
      }
    }
  };

  std::vector<std::thread> pool;
  for (int t = 0; t < threads; ++t) pool.emplace_back(worker, t);
  for (auto& th : pool) th.join();

  auto elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  if (!found.load()) {
    std::cout << "NO_WITNESS_T_CYCLE pmax=" << pmax << " maxSize=" << max_size
              << " productBound=" << bound << " mode=" << mode
              << " tasks=" << tasks.size() << " tested=" << tested.load()
              << " factored=" << factored.load() << " squarefree=" << squarefree.load()
              << " congruent=" << congruent.load() << " elapsed=" << elapsed << "s\n";
  }
  return found.load() ? 0 : 1;
}
