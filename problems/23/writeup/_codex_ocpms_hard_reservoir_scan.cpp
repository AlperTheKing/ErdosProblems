#include <algorithm>
#include <atomic>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <numeric>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

using i128 = __int128_t;

struct Ratio {
  i128 num = 0;
  i128 den = 1;
};

struct Case {
  Ratio ratio;
  long long w[10]{};
  i128 f0 = 0;
  i128 res_num = 0;
  i128 res_den = 1;
  i128 margin_num = 0;
  std::string active;
  bool set = false;
};

static std::string to_string_i128(i128 x) {
  if (x == 0) return "0";
  bool neg = x < 0;
  if (neg) x = -x;
  std::string s;
  while (x > 0) {
    int digit = static_cast<int>(x % 10);
    s.push_back(static_cast<char>('0' + digit));
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

static std::string frac_string(i128 num, i128 den) {
  if (den < 0) {
    num = -num;
    den = -den;
  }
  i128 g = gcd_i128(num, den);
  num /= g;
  den /= g;
  if (den == 1) return to_string_i128(num);
  return to_string_i128(num) + "/" + to_string_i128(den);
}

static bool ratio_less(const Ratio& a, const Ratio& b) {
  return a.num * b.den < b.num * a.den;
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

static std::string active_constraints(const long long w[10]) {
  long long w0 = w[0], w1 = w[1], w2 = w[2], w3 = w[3], w4 = w[4];
  long long w5 = w[5], w6 = w[6], w7 = w[7], w8 = w[8], w9 = w[9];
  i128 m = (i128)w1 * w9 + (i128)w2 * w7 + (i128)w7 * w9;
  std::vector<std::string> a;
  if (w5 == w9) a.push_back("w5=w9");
  if (w6 == w7) a.push_back("w6=w7");
  if (w3 + w5 == w2 + w9) a.push_back("w3+w5=w2+w9");
  if (w4 + w6 == w1 + w7) a.push_back("w4+w6=w1+w7");
  if ((i128)w0 * w6 + (i128)w3 * w8 + (i128)w5 * w8 == m) a.push_back("D27=m");
  if ((i128)w0 * w5 + (i128)w3 * w8 + (i128)w5 * w8 == m) a.push_back("D0=m");
  if ((i128)w0 * w6 + (i128)w4 * w8 + (i128)w6 * w8 == m) a.push_back("D19=m");
  std::ostringstream out;
  for (size_t i = 0; i < a.size(); ++i) {
    if (i) out << ",";
    out << a[i];
  }
  return out.str();
}

static Case evaluate_case(const long long w[10]) {
  long long w0 = w[0], w1 = w[1], w2 = w[2], w3 = w[3], w4 = w[4];
  long long w5 = w[5], w6 = w[6], w7 = w[7], w8 = w[8], w9 = w[9];
  i128 z27 = (i128)w6 * ((i128)w0 * w5 + (i128)w3 * w8 + (i128)w5 * w8);
  i128 a27 = (i128)w0 * w5 + (i128)w0 * w6 + (i128)w3 * w6 +
              (i128)w3 * w8 + (i128)w5 * w6 + (i128)w5 * w8 + (i128)w6 * w8;
  i128 z19 = (i128)w5 * ((i128)w0 * w6 + (i128)w4 * w8 + (i128)w6 * w8);
  i128 a19 = (i128)w0 * w5 + (i128)w0 * w6 + (i128)w4 * w5 +
              (i128)w4 * w8 + (i128)w5 * w6 + (i128)w5 * w8 + (i128)w6 * w8;
  i128 z79 = (i128)w0 * w5 * w6 + (i128)w3 * w4 * w8 +
              (i128)w3 * w6 * w8 + (i128)w4 * w5 * w8 + (i128)w5 * w6 * w8;
  i128 a79 = (i128)w0 * w5 + (i128)w0 * w6 + (i128)w3 * w4 +
              (i128)w3 * w6 + (i128)w3 * w8 + (i128)w4 * w5 +
              (i128)w4 * w8 + (i128)w5 * w6 + (i128)w5 * w8 + (i128)w6 * w8;
  i128 x = w1, y = w2, u = w7, v = w9;
  i128 core = (i128)w0 + w3 + w4 + w5 + w6 + w8;
  i128 s = x + y + u + v;
  i128 f0 = 2 * (core + s) * (core + s) + 75 * core - 225 * x * v - 225 * y * u - 200 * u * v;

  i128 n19 = 25 * (7 * z19 - 3 * a19) * x * v;
  i128 n27 = 25 * (7 * z27 - 3 * a27) * y * u;
  i128 n79 = 75 * (2 * z79 - a79) * u * v;
  i128 den = z19 * z27 * z79;
  i128 res_num = n19 * z27 * z79 + n27 * z19 * z79 + n79 * z19 * z27;

  Case c;
  std::copy(w, w + 10, c.w);
  c.f0 = f0;
  c.res_num = res_num;
  c.res_den = den;
  c.margin_num = f0 * den + res_num;
  c.ratio = {res_num, den * (-f0)};
  c.active = active_constraints(w);
  c.set = true;
  return c;
}

static bool better_case(const Case& a, const Case& b) {
  if (!a.set) return false;
  if (!b.set) return true;
  return ratio_less(a.ratio, b.ratio);
}

int main(int argc, char** argv) {
  int B = argc >= 2 ? std::stoi(argv[1]) : 6;
  int workers = argc >= 3 ? std::stoi(argv[2]) : (int)std::thread::hardware_concurrency();
  workers = std::max(1, workers);

  std::atomic<long long> total{0};
  std::atomic<long long> selected{0};
  std::atomic<long long> crude_neg{0};
  std::atomic<long long> failures{0};
  std::mutex best_mu;
  Case global_best;
  Case global_fail;

  auto worker = [&](int tid) {
    Case local_best;
    Case local_fail;
    long long w[10];
    for (int w0 = 1 + tid; w0 <= B; w0 += workers) {
      w[0] = w0;
      for (w[1] = 1; w[1] <= B; ++w[1])
      for (w[2] = 1; w[2] <= B; ++w[2])
      for (w[3] = 1; w[3] <= B; ++w[3])
      for (w[4] = 1; w[4] <= B; ++w[4])
      for (w[5] = 1; w[5] <= B; ++w[5])
      for (w[6] = 1; w[6] <= B; ++w[6])
      for (w[7] = 1; w[7] <= B; ++w[7])
      for (w[8] = 1; w[8] <= B; ++w[8])
      for (w[9] = 1; w[9] <= B; ++w[9]) {
        total.fetch_add(1, std::memory_order_relaxed);
        if (!selected_ok(w)) continue;
        selected.fetch_add(1, std::memory_order_relaxed);
        Case c = evaluate_case(w);
        if (c.margin_num < 0) {
          failures.fetch_add(1, std::memory_order_relaxed);
          if (better_case(c, local_fail)) local_fail = c;
        }
        if (c.f0 < 0) {
          crude_neg.fetch_add(1, std::memory_order_relaxed);
          if (better_case(c, local_best)) local_best = c;
        }
      }
    }
    std::lock_guard<std::mutex> lock(best_mu);
    if (better_case(local_best, global_best)) global_best = local_best;
    if (better_case(local_fail, global_fail)) global_fail = local_fail;
  };

  std::vector<std::thread> threads;
  for (int t = 0; t < workers; ++t) threads.emplace_back(worker, t);
  for (auto& th : threads) th.join();

  std::cout << "B " << B << " workers " << workers << "\n";
  std::cout << "total " << total << " selected " << selected
            << " crude_neg " << crude_neg << " failures " << failures << "\n";
  if (global_best.set) {
    std::cout << "best_ratio " << frac_string(global_best.ratio.num, global_best.ratio.den) << "\n";
    std::cout << "best_w";
    for (long long x : global_best.w) std::cout << " " << x;
    std::cout << "\n";
    std::cout << "best_active " << (global_best.active.empty() ? "-" : global_best.active) << "\n";
    std::cout << "best_f0 " << to_string_i128(global_best.f0) << "\n";
    std::cout << "best_reservoir " << frac_string(global_best.res_num, global_best.res_den) << "\n";
    std::cout << "best_margin " << frac_string(global_best.margin_num, global_best.res_den) << "\n";
  }
  if (global_fail.set) {
    std::cout << "fail_ratio " << frac_string(global_fail.ratio.num, global_fail.ratio.den) << "\n";
    std::cout << "fail_w";
    for (long long x : global_fail.w) std::cout << " " << x;
    std::cout << "\n";
  }
  return failures.load() == 0 ? 0 : 1;
}
