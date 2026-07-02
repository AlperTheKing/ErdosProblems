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
  Rat delta;
  int p = 0, dd = 0, e = 0, h = 0;
  int p2 = 0, d2 = 0, e2 = 0, h2 = 0;
  Rat base, nxt;
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
static bool ge(Rat a, Rat b) { return a.n * b.d >= b.n * a.d; }

static std::string str(Rat x) {
  x = norm(x);
  if (x.d == 1) return x.n.convert_to<std::string>();
  return x.n.convert_to<std::string>() + "/" + x.d.convert_to<std::string>();
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

static void make_pair(int p, int dd, int e, int h, Rat cur[10], Rat prev[10]) {
  int q = p + dd + e;
  int x = 1 + h;
  int y = x + dd;
  Rat a = norm({cpp_int(x) * p + cpp_int(y) * q + cpp_int(q) * p - y - p, p});
  Rat rp = add(R(1), norm({p, y + p}));
  cur[0] = a;
  cur[1] = R(x);
  cur[2] = R(y);
  cur[3] = R(y);
  cur[4] = R(x);
  cur[5] = R(p);
  cur[6] = R(q);
  cur[7] = R(q);
  cur[8] = R(1);
  cur[9] = R(p);
  prev[0] = sub(a, R(1));
  prev[1] = R(x);
  prev[2] = R(y);
  prev[3] = R(y);
  prev[4] = R(x);
  prev[5] = R(p);
  prev[6] = R(q);
  prev[7] = R(q);
  prev[8] = rp;
  prev[9] = R(p);
}

static bool stepdiff(int p, int dd, int e, int h, Rat& out) {
  if (dd + e <= 0) return false;
  Rat cur[10], prev[10];
  make_pair(p, dd, e, h, cur, prev);
  if (!ge(cur[0], R(1)) || !ge(prev[0], R(1))) return false;
  if (!selected_ok(cur) || !selected_ok(prev)) return false;
  out = sub(pms_margin(cur), pms_margin(prev));
  return true;
}

static void upd(Best& b, Rat delta, int p, int dd, int e, int h, int p2, int d2, int e2, int h2,
                Rat base, Rat nxt) {
  if (!b.set || lt(delta, b.delta)) {
    b.set = true;
    b.delta = delta;
    b.p = p;
    b.dd = dd;
    b.e = e;
    b.h = h;
    b.p2 = p2;
    b.d2 = d2;
    b.e2 = e2;
    b.h2 = h2;
    b.base = base;
    b.nxt = nxt;
  }
}

int main(int argc, char** argv) {
  int B = argc >= 2 ? std::stoi(argv[1]) : 20;
  int workers = argc >= 3 ? std::stoi(argv[2]) : (int)std::thread::hardware_concurrency();
  workers = std::max(1, workers);
  std::atomic<long long> compared[3];
  std::atomic<long long> lower[3];
  for (int i = 0; i < 3; ++i) {
    compared[i] = 0;
    lower[i] = 0;
  }
  std::atomic<bool> stop{false};
  std::mutex mu;
  Best global[3], fail[3];
  int tasks = B * (B + 1);
  auto worker = [&](int tid) {
    Best local[3];
    for (int task = tid; task < tasks && !stop.load(); task += workers) {
      int p = task / (B + 1) + 1;
      int dd = task % (B + 1);
      for (int e = 0; e <= B && !stop.load(); ++e) {
        for (int h = 0; h <= B && !stop.load(); ++h) {
          Rat base;
          if (!stepdiff(p, dd, e, h, base)) continue;
          const int incs[3][4] = {{p, dd, e, h + 1}, {p, dd + 1, e, h}, {p, dd, e + 1, h}};
          for (int ax = 0; ax < 3; ++ax) {
            Rat nxt;
            if (!stepdiff(incs[ax][0], incs[ax][1], incs[ax][2], incs[ax][3], nxt)) continue;
            Rat delta = sub(nxt, base);
            compared[ax].fetch_add(1, std::memory_order_relaxed);
            upd(local[ax], delta, p, dd, e, h, incs[ax][0], incs[ax][1], incs[ax][2], incs[ax][3],
                base, nxt);
            if (delta.n < 0) {
              lower[ax].fetch_add(1, std::memory_order_relaxed);
              std::lock_guard<std::mutex> lock(mu);
              if (!stop.load()) {
                stop.store(true);
                fail[ax] = local[ax];
              }
            }
          }
        }
      }
    }
    std::lock_guard<std::mutex> lock(mu);
    for (int ax = 0; ax < 3; ++ax) {
      if (local[ax].set) {
        upd(global[ax], local[ax].delta, local[ax].p, local[ax].dd, local[ax].e, local[ax].h,
            local[ax].p2, local[ax].d2, local[ax].e2, local[ax].h2, local[ax].base, local[ax].nxt);
      }
    }
  };
  std::vector<std::thread> threads;
  for (int i = 0; i < workers; ++i) threads.emplace_back(worker, i);
  for (auto& th : threads) th.join();
  const char* names[3] = {"h", "d", "e"};
  std::cout << "B " << B << " workers " << workers << "\n";
  for (int ax = 0; ax < 3; ++ax) {
    std::cout << "axis " << names[ax] << " compared " << compared[ax].load()
              << " lower " << lower[ax].load();
    if (global[ax].set) {
      std::cout << " best_delta " << str(global[ax].delta) << " from (" << global[ax].p << ","
                << global[ax].dd << "," << global[ax].e << "," << global[ax].h << ") to ("
                << global[ax].p2 << "," << global[ax].d2 << "," << global[ax].e2 << ","
                << global[ax].h2 << ") base " << str(global[ax].base) << " next "
                << str(global[ax].nxt);
    }
    std::cout << "\n";
  }
  bool ok = true;
  for (int ax = 0; ax < 3; ++ax) ok = ok && lower[ax].load() == 0;
  std::cout << "VERDICT " << (ok ? "PASS" : "FAIL") << "\n";
  return ok ? 0 : 1;
}
