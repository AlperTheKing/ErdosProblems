#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

namespace {

bool radical_divides(int value, int modulus) {
  value = std::abs(value);
  if (value == 0) return false;
  for (int p = 2; 1LL * p * p <= value; ++p) {
    if (value % p != 0) continue;
    if (modulus % p != 0) return false;
    while (value % p == 0) value /= p;
  }
  return value == 1 || modulus % value == 0;
}

bool phase_allowed(int east_period, int north_period, int x, int y) {
  const int common_period = std::gcd(east_period, north_period);
  const int determinant = east_period * y - north_period * x;
  if (determinant == 0 ||
      !radical_divides(determinant, common_period)) {
    return false;
  }
  if (std::gcd(std::gcd(std::abs(x), std::abs(y)), common_period) != 1) {
    return false;
  }
  return std::gcd(std::abs(x), east_period) > 1 ||
         std::gcd(std::abs(y), north_period) > 1;
}

struct Candidate {
  int east_period = 0;
  int north_period = 0;
  int x_residue = 0;
  int y_residue = 0;
  int lift = 0;
  std::string word;
};

bool search_period(int east_period, int north_period, Candidate& out) {
  const int width = east_period + 1;
  const int height = north_period + 1;
  const auto index = [height](int i, int j) { return i * height + j; };
  std::vector<unsigned char> reachable(
      static_cast<std::size_t>(width * height), 0);
  std::vector<char> predecessor(
      static_cast<std::size_t>(width * height), 0);

  for (int a = 0; a < east_period; ++a) {
    for (int b = 0; b < north_period; ++b) {
      std::fill(reachable.begin(), reachable.end(), 0);
      std::fill(predecessor.begin(), predecessor.end(), 0);
      if (!phase_allowed(east_period, north_period, a, b)) continue;
      reachable[index(0, 0)] = 1;

      for (int i = 0; i <= east_period; ++i) {
        for (int j = 0; j <= north_period; ++j) {
          if (i == 0 && j == 0) continue;
          if (!phase_allowed(east_period, north_period, a + i, b + j)) {
            continue;
          }
          if (i > 0 && reachable[index(i - 1, j)]) {
            reachable[index(i, j)] = 1;
            predecessor[index(i, j)] = 'E';
          } else if (j > 0 && reachable[index(i, j - 1)]) {
            reachable[index(i, j)] = 1;
            predecessor[index(i, j)] = 'N';
          }
        }
      }

      if (!reachable[index(east_period, north_period)]) continue;
      std::string reversed;
      int i = east_period;
      int j = north_period;
      while (i != 0 || j != 0) {
        const char step = predecessor[index(i, j)];
        if (step == 'E') {
          reversed.push_back(step);
          --i;
        } else if (step == 'N') {
          reversed.push_back(step);
          --j;
        } else {
          std::cerr << "broken predecessor chain\n";
          std::exit(3);
        }
      }
      std::reverse(reversed.begin(), reversed.end());
      int lift = 1;
      while (a + lift * east_period <= east_period ||
             b + lift * north_period <= north_period) {
        ++lift;
      }
      out = {east_period, north_period, a, b, lift, reversed};
      return true;
    }
  }
  return false;
}

}  // namespace

int main(int argc, char** argv) {
  const int limit = argc > 1 ? std::stoi(argv[1]) : 80;
  if (limit < 2 || limit > 500) {
    std::cerr << "limit must lie in [2,500]\n";
    return 2;
  }

  std::uint64_t period_pairs = 0;
  for (int scale = 2; scale <= limit; ++scale) {
    for (int east_period = 2; east_period <= scale; ++east_period) {
      for (int north_period = 2; north_period <= scale; ++north_period) {
        if (east_period == north_period ||
            std::max(east_period, north_period) != scale) {
          continue;
        }
        ++period_pairs;
        Candidate candidate;
        if (!search_period(east_period, north_period, candidate)) continue;
        const int x = candidate.x_residue +
                      candidate.lift * candidate.east_period;
        const int y = candidate.y_residue +
                      candidate.lift * candidate.north_period;
        std::cout << "{\"status\":\"HIT\",\"A\":"
                  << candidate.east_period << ",\"B\":"
                  << candidate.north_period << ",\"x_residue\":"
                  << candidate.x_residue << ",\"y_residue\":"
                  << candidate.y_residue << ",\"lift\":"
                  << candidate.lift << ",\"start\":[" << x << ',' << y
                  << "],\"word\":\"" << candidate.word
                  << "\",\"period_pairs\":" << period_pairs << "}\n";
        return 0;
      }
    }
  }

  std::cout << "{\"status\":\"NO_HIT\",\"limit\":" << limit
            << ",\"period_pairs\":" << period_pairs << "}\n";
  return 1;
}
