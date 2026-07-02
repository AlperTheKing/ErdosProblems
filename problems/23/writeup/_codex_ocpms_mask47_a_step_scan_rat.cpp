#include <algorithm>
#include <atomic>
#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

using boost::multiprecision::cpp_int;

struct Rat {
  cpp_int n = 0;
  cpp_int d = 1;
};

struct Best {
  bool set = false;
  Rat diff;
  Rat w[10];
  Rat prev[10];
};

static cpp_int abs_int(cpp_int x) { return x < 0 ? -x : x; }

static cpp_int gcd_int(cpp_int a, cpp_int b) {
  a = abs_int(a);
  b = abs_int(b);
  while (b != 0) {
    cpp_int r = a % b;
    a = b;
    b = r;
  }
  return a == 0 ? 1 : a;
}

static Rat norm(Rat x) {
  if (x.d < 0) {
    x.n = -x.n;
    x.d = -x.d;
  }
  cpp_int g = gcd_int(x.n, x.d);
  x.n /= g;
  x.d /= g;
  return x;
}

static Rat R(long long x) { return {x, 1}; }

static Rat add(Rat a, Rat b) { return norm({a.n * b.d + b.n * a.d, a.d * b.d}); }
static Rat sub(Rat a, Rat b) { return norm({a.n * b.d - b.n * a.d, a.d * b.d}); }
static Rat mul(Rat a, Rat b) { return norm({a.n * b.n, a.d * b.d}); }
static Rat divr(Rat a, Rat b) { return norm({a.n * b.d, a.d * b.n}); }

static bool lt(Rat a, Rat b) { return a.n * b.d < b.n * a.d; }
static bool le(Rat a, Rat b) { return a.n * b.d <= b.n * a.d; }
static bool ge(Rat a, Rat b) { return a.n * b.d >= b.n * a.d; }

static std::string str(Rat x) {
  x = norm(x);
  if (x.d == 1) return x.n.convert_to<std::string>();
  return x.n.convert_to<std::string>() + "/" + x.d.convert_to<std::string>();
}

static void make_point(long long a, long long p, long long q, long long x, long long y, Rat out[10]) {
  Rat rr = norm({cpp_int(x) * p + cpp_int(y) * q + cpp_int(q) * p - cpp_int(a) * p, y + p});
  out[0] = R(a);
  out[1] = R(x);
  out[2] = R(y);
  out[3] = R(y);
  out[4] = R(x);
  out[5] = R(p);
  out[6] = R(q);
  out[7] = R(q);
  out[8] = rr;
  out[9] = R(p);
}

static bool selected_ok(const Rat w[10]) {
  Rat m = add(add(mul(w[1], w[9]), mul(w[2], w[7])), mul(w[7], w[9]));
  return ge(w[5], w[9]) && ge(w[6], w[7]) &&
         ge(add(w[3], w[5]), add(w[2], w[9])) &&
         ge(add(w[4], w[6]), add(w[1], w[7])) &&
         ge(add(add(mul(w[0], w[6]), mul(w[3], w[8])), mul(w[5], w[8])), m) &&
         ge(add(add(mul(w[0], w[5]), mul(w[3], w[8])), mul(w[5], w[8])), m) &&
         ge(add(add(mul(w[0], w[6]), mul(w[4], w[8])), mul(w[6], w[8])), m);
}

static Rat pms_margin(const Rat w[10]) {
  Rat z27 = mul(w[6], add(add(mul(w[0], w[5]), mul(w[3], w[8])), mul(w[5], w[8])));
  Rat a27 = add(add(add(add(add(add(mul(w[0], w[5]), mul(w[0], w[6])), mul(w[3], w[6])),
                         mul(w[3], w[8])),
                     mul(w[5], w[6])),
                 mul(w[5], w[8])),
             mul(w[6], w[8]));
  Rat z19 = mul(w[5], add(add(mul(w[0], w[6]), mul(w[4], w[8])), mul(w[6], w[8])));
  Rat a19 = add(add(add(add(add(add(mul(w[0], w[5]), mul(w[0], w[6])), mul(w[4], w[5])),
                         mul(w[4], w[8])),
                     mul(w[5], w[6])),
                 mul(w[5], w[8])),
             mul(w[6], w[8]));
  Rat z79 = add(add(add(add(mul(mul(w[0], w[5]), w[6]), mul(mul(w[3], w[4]), w[8])),
                       mul(mul(w[3], w[6]), w[8])),
                   mul(mul(w[4], w[5]), w[8])),
               mul(mul(w[5], w[6]), w[8]));
  Rat a79 = add(add(add(add(add(add(add(add(add(mul(w[0], w[5]), mul(w[0], w[6])),
                                           mul(w[3], w[4])),
                                       mul(w[3], w[6])),
                                   mul(w[3], w[8])),
                               mul(w[4], w[5])),
                           mul(w[4], w[8])),
                       mul(w[5], w[6])),
                   mul(w[5], w[8])),
               mul(w[6], w[8]));

  Rat core = add(add(add(add(add(w[0], w[3]), w[4]), w[5]), w[6]), w[8]);
  Rat endpoints = add(add(add(w[1], w[2]), w[7]), w[9]);
  Rat total = add(core, endpoints);
  Rat f0 = sub(sub(sub(add(mul(R(2), mul(total, total)), mul(R(75), core)),
                   mul(R(225), mul(w[1], w[9]))),
               mul(R(225), mul(w[2], w[7]))),
           mul(R(200), mul(w[7], w[9])));
  Rat reservoir = add(
      add(mul(mul(R(75), sub(Rat{7, 3}, divr(a19, z19))), mul(w[1], w[9])),
          mul(mul(R(75), sub(Rat{7, 3}, divr(a27, z27))), mul(w[2], w[7]))),
      mul(mul(R(75), sub(R(2), divr(a79, z79))), mul(w[7], w[9])));
  return add(f0, reservoir);
}

static void update_best(Best& best, Rat diff, const Rat w[10], const Rat prev[10]) {
  if (!best.set || lt(diff, best.diff)) {
    best.set = true;
    best.diff = diff;
    std::copy(w, w + 10, best.w);
    std::copy(prev, prev + 10, best.prev);
  }
}

int main(int argc, char** argv) {
  int B = argc >= 2 ? std::stoi(argv[1]) : 30;
  int workers = argc >= 3 ? std::stoi(argv[2]) : (int)std::thread::hardware_concurrency();
  workers = std::max(1, workers);

  std::atomic<long long> compared{0};
  std::atomic<long long> lower{0};
  std::atomic<bool> stop{false};
  std::mutex mu;
  Best global_best;
  Best global_bucket[3];
  Best global_rbucket[3][2];
  Best fail;

  int tasks = B * B;
  auto worker = [&](int tid) {
    Best local_best;
    Best local_bucket[3];
    Best local_rbucket[3][2];
    Rat w[10], prev[10];
    for (int task = tid; task < tasks && !stop.load(); task += workers) {
      int p = task / B + 1;
      int q = task % B + 1;
      if (q < p) continue;
      for (int x = 1; x <= B && !stop.load(); ++x) {
        for (int y = 1; y <= B && !stop.load(); ++y) {
          if (cpp_int(x) * p >= cpp_int(q) * y) continue;
          for (int a = 2; a <= B && !stop.load(); ++a) {
            make_point(a, p, q, x, y, w);
            make_point(a - 1, p, q, x, y, prev);
            if (!le(R(1), w[8]) || !le(w[8], R(B)) || !le(R(1), prev[8]) || !le(prev[8], R(B))) {
              continue;
            }
            if (!selected_ok(w) || !selected_ok(prev)) continue;
            Rat mw = pms_margin(w);
            Rat mp = pms_margin(prev);
            Rat diff = sub(mw, mp);
            compared.fetch_add(1, std::memory_order_relaxed);
            update_best(local_best, diff, w, prev);
            int bucket = 0;
            if (y < x) {
              bucket = 0;
            } else if (y - x <= q - p) {
              bucket = 1;
            } else {
              bucket = 2;
            }
            update_best(local_bucket[bucket], diff, w, prev);
            int rbucket = (w[8].n == w[8].d) ? 0 : 1;
            update_best(local_rbucket[bucket][rbucket], diff, w, prev);
            if (diff.n < 0) {
              lower.fetch_add(1, std::memory_order_relaxed);
              std::lock_guard<std::mutex> lock(mu);
              if (!stop.load()) {
                stop.store(true);
                fail.set = true;
                fail.diff = diff;
                std::copy(w, w + 10, fail.w);
                std::copy(prev, prev + 10, fail.prev);
              }
            }
          }
        }
      }
    }
    std::lock_guard<std::mutex> lock(mu);
    if (local_best.set) update_best(global_best, local_best.diff, local_best.w, local_best.prev);
    for (int i = 0; i < 3; ++i) {
      if (local_bucket[i].set) {
        update_best(global_bucket[i], local_bucket[i].diff, local_bucket[i].w, local_bucket[i].prev);
      }
      for (int j = 0; j < 2; ++j) {
        if (local_rbucket[i][j].set) {
          update_best(global_rbucket[i][j], local_rbucket[i][j].diff,
                      local_rbucket[i][j].w, local_rbucket[i][j].prev);
        }
      }
    }
  };

  std::vector<std::thread> threads;
  for (int i = 0; i < workers; ++i) threads.emplace_back(worker, i);
  for (auto& th : threads) th.join();

  std::cout << "B " << B << " workers " << workers << " compared " << compared.load()
            << " lower " << lower.load() << "\n";
  if (fail.set) {
    std::cout << "first_lower " << str(fail.diff) << " w";
    for (auto z : fail.w) std::cout << " " << str(z);
    std::cout << " prev";
    for (auto z : fail.prev) std::cout << " " << str(z);
    std::cout << "\nVERDICT FAIL\n";
    return 1;
  }
  if (global_best.set) {
    std::cout << "best_diff " << str(global_best.diff) << " w";
    for (auto z : global_best.w) std::cout << " " << str(z);
    std::cout << " prev";
    for (auto z : global_best.prev) std::cout << " " << str(z);
    std::cout << "\n";
  }
  const char* names[3] = {"y<x", "y>=x,d<=s", "y>=x,d>s"};
  const char* rnames[2] = {"r=1", "r>1"};
  for (int i = 0; i < 3; ++i) {
    if (!global_bucket[i].set) continue;
    std::cout << "bucket " << names[i] << " best_diff " << str(global_bucket[i].diff) << " w";
    for (auto z : global_bucket[i].w) std::cout << " " << str(z);
    std::cout << " prev";
    for (auto z : global_bucket[i].prev) std::cout << " " << str(z);
    std::cout << "\n";
    for (int j = 0; j < 2; ++j) {
      if (!global_rbucket[i][j].set) continue;
      std::cout << "bucket " << names[i] << " " << rnames[j]
                << " best_diff " << str(global_rbucket[i][j].diff) << " w";
      for (auto z : global_rbucket[i][j].w) std::cout << " " << str(z);
      std::cout << " prev";
      for (auto z : global_rbucket[i][j].prev) std::cout << " " << str(z);
      std::cout << "\n";
    }
  }
  std::cout << "VERDICT PASS\n";
  return 0;
}
