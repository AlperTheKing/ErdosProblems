#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

// Exact integer grid falsifier for the S7 sibling lemma.
//
// It checks variables a,b,c,d,e,f,x,y,u,v in [1,B], filters the seven S7
// slacks, and tests Phi >= 0 after multiplying by positive denominator e*Y*Z:
//
//   Phi = 2(N^2-25m)-75*(x(u+v)A/Z + yvB/(eY) - C0).
//
// All arithmetic is signed __int128; B<=20 is comfortably safe.

using i128 = __int128_t;

static std::string to_string_i128(i128 v) {
  if (v == 0) return "0";
  bool neg = v < 0;
  if (neg) v = -v;
  std::string s;
  while (v > 0) {
    s.push_back(char('0' + v % 10));
    v /= 10;
  }
  if (neg) s.push_back('-');
  std::reverse(s.begin(), s.end());
  return s;
}

int main(int argc, char** argv) {
  int B = 5;
  if (argc >= 2) B = std::atoi(argv[1]);

  std::uint64_t checked = 0;
  std::uint64_t feasible = 0;
  i128 best_num = std::numeric_limits<long long>::max();
  std::array<int, 10> best{};
  std::array<i128, 7> best_slack{};
  i128 best_den = 1;

  for (int a = 1; a <= B; ++a)
  for (int b = 1; b <= B; ++b)
  for (int c = 1; c <= B; ++c)
  for (int d = 1; d <= B; ++d)
  for (int e = 1; e <= B; ++e)
  for (int f = 1; f <= B; ++f)
  for (int x = 1; x <= B; ++x)
  for (int y = 1; y <= B; ++y)
  for (int u = 1; u <= B; ++u)
  for (int v = 1; v <= B; ++v) {
    ++checked;
    const i128 m = i128(x)*u + i128(x)*v + i128(y)*v;
    const i128 N = i128(a)+b+c+d+e+f+x+y+u+v;
    const i128 Y = i128(a)*c + i128(b)*f + i128(c)*f;
    const i128 Z = i128(e)*Y + i128(d)*f*(b+c);
    const i128 A = i128(b)*d + i128(c)*d + i128(d)*f + i128(a)*c + i128(a)*e
                 + i128(b)*f + i128(b)*e + i128(c)*f + i128(c)*e + i128(e)*f;
    const i128 BB = i128(a)*c + i128(a)*e + i128(b)*f + i128(b)*e
                  + i128(c)*f + i128(c)*e + i128(e)*f;
    std::array<i128, 7> s = {
      i128(e) - v,
      i128(d) + e - u - v,
      i128(b) + c - x - y,
      Y - m,
      i128(a)*e + i128(b)*f + i128(c)*f - m,
      i128(a)*c + i128(d)*f + i128(e)*f - m,
      i128(a)*e + i128(d)*f + i128(e)*f - m,
    };
    bool ok = true;
    for (i128 z : s) {
      if (z < 0) {
        ok = false;
        break;
      }
    }
    if (!ok) continue;
    ++feasible;

    const i128 C0 = i128(a)+b+c+d+e+f;
    const i128 den = i128(e) * Y * Z;
    const i128 num = (2*(N*N - 25*m) + 75*C0) * den
                   - 75 * (i128(x)*(u+v)*A * e * Y + i128(y)*v*BB * Z);
    if (num < 0) {
      std::cout << "FAIL\n";
      std::cout << "B " << B << "\n";
      std::cout << "tuple "
                << a << " " << b << " " << c << " " << d << " " << e << " "
                << f << " " << x << " " << y << " " << u << " " << v << "\n";
      std::cout << "num " << to_string_i128(num) << "\n";
      std::cout << "den " << to_string_i128(den) << "\n";
      std::cout << "slacks";
      for (i128 z : s) std::cout << " " << to_string_i128(z);
      std::cout << "\n";
      return 1;
    }
    if (feasible == 1 || num * best_den < best_num * den) {
      best_num = num;
      best_den = den;
      best = {a,b,c,d,e,f,x,y,u,v};
      best_slack = s;
    }
  }

  std::cout << "PASS\n";
  std::cout << "B " << B << "\n";
  std::cout << "checked " << checked << "\n";
  std::cout << "feasible " << feasible << "\n";
  std::cout << "best_num " << to_string_i128(best_num) << "\n";
  std::cout << "best_den " << to_string_i128(best_den) << "\n";
  std::cout << "best_tuple";
  for (int z : best) std::cout << " " << z;
  std::cout << "\n";
  std::cout << "best_slacks";
  for (i128 z : best_slack) std::cout << " " << to_string_i128(z);
  std::cout << "\n";
  return 0;
}
