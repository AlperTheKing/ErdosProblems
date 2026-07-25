#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <string>
#include <utility>
#include <vector>

namespace {

std::vector<int> prime_factors(int n) {
  std::vector<int> out;
  for (int p = 2; 1LL * p * p <= n; ++p) {
    if (n % p != 0) continue;
    out.push_back(p);
    while (n % p == 0) n /= p;
  }
  if (n > 1) out.push_back(n);
  return out;
}

bool radical_divides(int value, int modulus) {
  value = std::abs(value);
  for (int p = 2; 1LL * p * p <= value; ++p) {
    if (value % p != 0) continue;
    if (modulus % p != 0) return false;
    while (value % p == 0) value /= p;
  }
  return value == 1 || modulus % value == 0;
}

bool protected_by_composite_residue(
    int x, int y, const std::vector<int>& factors) {
  for (int p : factors) {
    if (x % p == 0 || y % p == 0) return true;
  }
  return false;
}

bool allowed(int modulus, int a, int b, int i, int j,
             const std::vector<int>& factors) {
  const int x = a + i;
  const int y = b + j;
  const int d = y - x;
  if (d == 0) return false;
  if (!radical_divides(d, modulus)) return false;
  if (std::gcd(std::abs(x), std::abs(d)) != 1) return false;
  return protected_by_composite_residue(x, y, factors);
}

struct Candidate {
  int modulus = 0;
  int a = 0;
  int b = 0;
  int lift = 0;
  std::string word;
};

bool find_for_modulus(int modulus, Candidate& candidate) {
  const auto factors = prime_factors(modulus);
  const int side = modulus + 1;
  std::vector<char> reachable(static_cast<std::size_t>(side * side), 0);
  std::vector<char> predecessor(static_cast<std::size_t>(side * side), 0);
  const auto index = [side](int i, int j) { return i * side + j; };

  for (int a = 0; a < modulus; ++a) {
    for (int b = 0; b < modulus; ++b) {
      std::fill(reachable.begin(), reachable.end(), 0);
      std::fill(predecessor.begin(), predecessor.end(), 0);
      if (!allowed(modulus, a, b, 0, 0, factors)) continue;
      reachable[index(0, 0)] = 1;

      for (int i = 0; i <= modulus; ++i) {
        for (int j = 0; j <= modulus; ++j) {
          if (i == 0 && j == 0) continue;
          if (!allowed(modulus, a, b, i, j, factors)) continue;
          if (i > 0 && reachable[index(i - 1, j)]) {
            reachable[index(i, j)] = 1;
            predecessor[index(i, j)] = 'E';
          } else if (j > 0 && reachable[index(i, j - 1)]) {
            reachable[index(i, j)] = 1;
            predecessor[index(i, j)] = 'N';
          }
        }
      }

      if (!reachable[index(modulus, modulus)]) continue;
      std::string reversed;
      int i = modulus;
      int j = modulus;
      while (i != 0 || j != 0) {
        const char step = predecessor[index(i, j)];
        if (step == 'E') {
          reversed.push_back('E');
          --i;
        } else if (step == 'N') {
          reversed.push_back('N');
          --j;
        } else {
          std::cerr << "broken predecessor chain\n";
          std::exit(3);
        }
      }
      std::reverse(reversed.begin(), reversed.end());

      const int max_factor =
          factors.empty() ? 1 : *std::max_element(factors.begin(), factors.end());
      int lift = 1;
      while (a + lift * modulus <= max_factor ||
             b + lift * modulus <= max_factor) {
        ++lift;
      }
      candidate = {modulus, a, b, lift, reversed};
      return true;
    }
  }
  return false;
}

}  // namespace

int main(int argc, char** argv) {
  const int max_modulus = argc > 1 ? std::stoi(argv[1]) : 120;
  if (max_modulus < 2 || max_modulus > 10000) {
    std::cerr << "max_modulus must lie in [2,10000]\n";
    return 2;
  }

  std::uint64_t tested_moduli = 0;
  for (int modulus = 2; modulus <= max_modulus; ++modulus) {
    ++tested_moduli;
    Candidate candidate;
    if (!find_for_modulus(modulus, candidate)) continue;
    const int start_x = candidate.a + candidate.lift * candidate.modulus;
    const int start_y = candidate.b + candidate.lift * candidate.modulus;
    std::cout << "{\"status\":\"HIT\",\"M\":" << candidate.modulus
              << ",\"a_residue\":" << candidate.a
              << ",\"b_residue\":" << candidate.b
              << ",\"lift\":" << candidate.lift
              << ",\"start\":[" << start_x << ',' << start_y << ']'
              << ",\"word\":\"" << candidate.word << "\""
              << ",\"tested_moduli\":" << tested_moduli << "}\n";
    return 0;
  }

  std::cout << "{\"status\":\"NO_HIT\",\"max_M\":" << max_modulus
            << ",\"tested_moduli\":" << tested_moduli << "}\n";
  return 1;
}
