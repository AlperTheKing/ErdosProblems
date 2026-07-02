#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

using i128 = __int128_t;

struct Rat {
  i128 n = 0;
  i128 d = 1;
};

struct Best {
  bool set = false;
  Rat diff;
  long long w[10]{};
  long long b[10]{};
};

static std::string to_string_i128(i128 x) {
  if (x == 0) return "0";
  bool neg = x < 0;
  if (neg) x = -x;
  std::string s;
  while (x > 0) {
    s.push_back(char('0' + int(x % 10)));
    x /= 10;
  }
  if (neg) s.push_back('-');
  std::reverse(s.begin(), s.end());
  return s;
}

static i128 gcd_i128(i128 a, i128 b) {
  if (a < 0) a = -a;
  if (b < 0) b = -b;
  while (b != 0) {
    i128 r = a % b;
    a = b;
    b = r;
  }
  return a == 0 ? 1 : a;
}

static std::string frac_string(i128 n, i128 d) {
  if (d < 0) {
    n = -n;
    d = -d;
  }
  i128 g = gcd_i128(n, d);
  n /= g;
  d /= g;
  if (d == 1) return to_string_i128(n);
  return to_string_i128(n) + "/" + to_string_i128(d);
}

static bool rat_less(const Rat& a, const Rat& b) {
  return a.n * b.d < b.n * a.d;
}

static bool selected_ok(const long long w[10]) {
  long long w0 = w[0], w1 = w[1], w2 = w[2], w3 = w[3], w4 = w[4];
  long long w5 = w[5], w6 = w[6], w7 = w[7], w8 = w[8], w9 = w[9];
  i128 m = (i128)w1 * w9 + (i128)w2 * w7 + (i128)w7 * w9;
  return w5 >= w9 && w6 >= w7 && w3 + w5 >= w2 + w9 &&
         w4 + w6 >= w1 + w7 &&
         (i128)w0 * w6 + (i128)w3 * w8 + (i128)w5 * w8 >= m &&
         (i128)w0 * w5 + (i128)w3 * w8 + (i128)w5 * w8 >= m &&
         (i128)w0 * w6 + (i128)w4 * w8 + (i128)w6 * w8 >= m;
}

static Rat pms_margin(const long long w[10]) {
  i128 w0 = w[0], w1 = w[1], w2 = w[2], w3 = w[3], w4 = w[4];
  i128 w5 = w[5], w6 = w[6], w7 = w[7], w8 = w[8], w9 = w[9];
  i128 z27 = w6 * (w0 * w5 + w3 * w8 + w5 * w8);
  i128 a27 = w0 * w5 + w0 * w6 + w3 * w6 + w3 * w8 + w5 * w6 + w5 * w8 + w6 * w8;
  i128 z19 = w5 * (w0 * w6 + w4 * w8 + w6 * w8);
  i128 a19 = w0 * w5 + w0 * w6 + w4 * w5 + w4 * w8 + w5 * w6 + w5 * w8 + w6 * w8;
  i128 z79 = w0 * w5 * w6 + w3 * w4 * w8 + w3 * w6 * w8 + w4 * w5 * w8 + w5 * w6 * w8;
  i128 a79 = w0 * w5 + w0 * w6 + w3 * w4 + w3 * w6 + w3 * w8 + w4 * w5 +
              w4 * w8 + w5 * w6 + w5 * w8 + w6 * w8;

  i128 core = w0 + w3 + w4 + w5 + w6 + w8;
  i128 endpoints = w1 + w2 + w7 + w9;
  i128 f0 = 2 * (core + endpoints) * (core + endpoints) + 75 * core -
             225 * w1 * w9 - 225 * w2 * w7 - 200 * w7 * w9;

  i128 den = z19 * z27 * z79;
  i128 num = f0 * den;
  num += 25 * (7 * z19 - 3 * a19) * w1 * w9 * z27 * z79;
  num += 25 * (7 * z27 - 3 * a27) * w2 * w7 * z19 * z79;
  num += 75 * (2 * z79 - a79) * w7 * w9 * z19 * z27;
  return {num, den};
}

static void update_best(Best& best, const Rat& diff, const long long w[10], const long long b[10]) {
  if (!best.set || rat_less(diff, best.diff)) {
    best.set = true;
    best.diff = diff;
    std::copy(w, w + 10, best.w);
    std::copy(b, b + 10, best.b);
  }
}

int main(int argc, char** argv) {
  int B = argc >= 2 ? std::stoi(argv[1]) : 80;
  int workers = argc >= 3 ? std::stoi(argv[2]) : (int)std::thread::hardware_concurrency();
  workers = std::max(1, workers);

  std::atomic<long long> compared{0};
  std::atomic<long long> lower{0};
  std::atomic<bool> stop{false};
  std::mutex mu;
  Best global_best;
  long long bad_w[10]{}, bad_b[10]{};
  Rat bad_diff;

  int tasks = B * B;
  auto worker = [&](int tid) {
    Best local_best;
    long long w[10], b[10];
    for (int task = tid; task < tasks && !stop.load(); task += workers) {
      int p = task / B + 1;
      int q = task % B + 1;
      if (q < p) continue;
      for (int x = 1; x <= B && !stop.load(); ++x) {
        for (int y = 1; y <= B && !stop.load(); ++y) {
          if ((i128)x * p >= (i128)q * y) continue;
          long long den = y + p;
          long long num0 = x * p + y * q + q * p - p;
          if (num0 % den) continue;
          long long r0 = num0 / den;
          if (r0 < 1 || r0 > B) continue;
          long long boundary[10] = {1, x, y, y, x, p, q, q, r0, p};
          if (!selected_ok(boundary)) continue;
          Rat mb = pms_margin(boundary);

          long long amax = (x * p + y * q + q * p - den) / p;
          amax = std::min<long long>(amax, B);
          for (int a = 2; a <= amax && !stop.load(); ++a) {
            long long num = x * p + y * q + q * p - a * p;
            if (num % den) continue;
            long long r = num / den;
            if (r < 1 || r > B) continue;
            long long cur[10] = {a, x, y, y, x, p, q, q, r, p};
            if (!selected_ok(cur)) continue;
            Rat mc = pms_margin(cur);
            Rat diff{mc.n * mb.d - mb.n * mc.d, mc.d * mb.d};
            compared.fetch_add(1, std::memory_order_relaxed);
            update_best(local_best, diff, cur, boundary);
            if (diff.n < 0) {
              std::lock_guard<std::mutex> lock(mu);
              if (!stop.load()) {
                lower.fetch_add(1, std::memory_order_relaxed);
                stop.store(true);
                bad_diff = diff;
                std::copy(cur, cur + 10, bad_w);
                std::copy(boundary, boundary + 10, bad_b);
              }
            }
          }
        }
      }
    }
    std::lock_guard<std::mutex> lock(mu);
    if (local_best.set) update_best(global_best, local_best.diff, local_best.w, local_best.b);
  };

  std::vector<std::thread> threads;
  for (int i = 0; i < workers; ++i) threads.emplace_back(worker, i);
  for (auto& th : threads) th.join();

  std::cout << "B " << B << " workers " << workers << " compared " << compared
            << " lower " << lower << "\n";
  if (lower.load()) {
    std::cout << "first_lower " << frac_string(bad_diff.n, bad_diff.d) << " w";
    for (long long z : bad_w) std::cout << " " << z;
    std::cout << " boundary";
    for (long long z : bad_b) std::cout << " " << z;
    std::cout << "\n";
    return 1;
  }
  if (global_best.set) {
    std::cout << "best_diff " << frac_string(global_best.diff.n, global_best.diff.d) << " w";
    for (long long z : global_best.w) std::cout << " " << z;
    std::cout << " boundary";
    for (long long z : global_best.b) std::cout << " " << z;
    std::cout << "\n";
  }
  std::cout << "VERDICT PASS\n";
}
