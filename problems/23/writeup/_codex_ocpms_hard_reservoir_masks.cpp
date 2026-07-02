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

struct Ratio {
  i128 num = 0;
  i128 den = 1;
};

struct Best {
  bool set = false;
  Ratio ratio;
  long long w[10]{};
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

static int active_mask(const long long w[10]) {
  long long w0 = w[0], w1 = w[1], w2 = w[2], w3 = w[3], w4 = w[4];
  long long w5 = w[5], w6 = w[6], w7 = w[7], w8 = w[8], w9 = w[9];
  i128 m = (i128)w1 * w9 + (i128)w2 * w7 + (i128)w7 * w9;
  int mask = 0;
  if (w5 == w9) mask |= 1 << 0;
  if (w6 == w7) mask |= 1 << 1;
  if (w3 + w5 == w2 + w9) mask |= 1 << 2;
  if (w4 + w6 == w1 + w7) mask |= 1 << 3;
  if ((i128)w0 * w6 + (i128)w3 * w8 + (i128)w5 * w8 == m) mask |= 1 << 4;
  if ((i128)w0 * w5 + (i128)w3 * w8 + (i128)w5 * w8 == m) mask |= 1 << 5;
  if ((i128)w0 * w6 + (i128)w4 * w8 + (i128)w6 * w8 == m) mask |= 1 << 6;
  return mask;
}

static std::string mask_names(int mask) {
  const char* names[7] = {"w5=w9", "w6=w7", "linL", "linR", "D27", "D0", "D19"};
  std::string out;
  for (int i = 0; i < 7; ++i) {
    if (!(mask & (1 << i))) continue;
    if (!out.empty()) out += ",";
    out += names[i];
  }
  return out.empty() ? "-" : out;
}

static bool eval_ratio(const long long w[10], Ratio& ratio) {
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
  if (f0 >= 0) return false;

  i128 n19 = 25 * (7 * z19 - 3 * a19) * x * v;
  i128 n27 = 25 * (7 * z27 - 3 * a27) * y * u;
  i128 n79 = 75 * (2 * z79 - a79) * u * v;
  i128 den = z19 * z27 * z79;
  i128 res_num = n19 * z27 * z79 + n27 * z19 * z79 + n79 * z19 * z27;
  ratio = {res_num, den * (-f0)};
  return true;
}

static void update_best(Best& best, const Ratio& ratio, const long long w[10]) {
  if (!best.set || ratio_less(ratio, best.ratio)) {
    best.set = true;
    best.ratio = ratio;
    std::copy(w, w + 10, best.w);
  }
}

int main(int argc, char** argv) {
  int B = argc >= 2 ? std::stoi(argv[1]) : 8;
  int workers = argc >= 3 ? std::stoi(argv[2]) : (int)std::thread::hardware_concurrency();
  workers = std::max(1, workers);

  std::atomic<long long> selected{0};
  std::atomic<long long> crude_neg{0};
  std::array<Best, 128> global{};
  std::mutex mu;

  auto worker = [&](int tid) {
    std::array<Best, 128> local{};
    long long w[10];
    const int tasks = B * B;
    for (int task = tid; task < tasks; task += workers) {
      w[0] = task / B + 1;
      w[1] = task % B + 1;
      for (w[2] = 1; w[2] <= B; ++w[2])
      for (w[3] = 1; w[3] <= B; ++w[3])
      for (w[4] = 1; w[4] <= B; ++w[4])
      for (w[5] = 1; w[5] <= B; ++w[5])
      for (w[6] = 1; w[6] <= B; ++w[6])
      for (w[7] = 1; w[7] <= B; ++w[7])
      for (w[8] = 1; w[8] <= B; ++w[8])
      for (w[9] = 1; w[9] <= B; ++w[9]) {
        if (!selected_ok(w)) continue;
        selected.fetch_add(1, std::memory_order_relaxed);
        Ratio ratio;
        if (!eval_ratio(w, ratio)) continue;
        crude_neg.fetch_add(1, std::memory_order_relaxed);
        update_best(local[active_mask(w)], ratio, w);
      }
    }
    std::lock_guard<std::mutex> lock(mu);
    for (int i = 0; i < 128; ++i) {
      if (local[i].set) update_best(global[i], local[i].ratio, local[i].w);
    }
  };

  std::vector<std::thread> threads;
  for (int i = 0; i < workers; ++i) threads.emplace_back(worker, i);
  for (auto& th : threads) th.join();

  std::vector<int> masks;
  for (int i = 0; i < 128; ++i) {
    if (global[i].set) masks.push_back(i);
  }
  std::sort(masks.begin(), masks.end(), [&](int a, int b) {
    return ratio_less(global[a].ratio, global[b].ratio);
  });

  std::cout << "B " << B << " workers " << workers << " selected " << selected
            << " crude_neg " << crude_neg << " masks " << masks.size() << "\n";
  int limit = std::min<int>(30, masks.size());
  for (int rank = 0; rank < limit; ++rank) {
    int mask = masks[rank];
    const Best& best = global[mask];
    std::cout << "rank " << (rank + 1) << " mask " << mask << " pop "
              << __builtin_popcount((unsigned)mask) << " ratio "
              << frac_string(best.ratio.num, best.ratio.den) << " active "
              << mask_names(mask) << " w";
    for (long long x : best.w) std::cout << " " << x;
    std::cout << "\n";
  }
}
