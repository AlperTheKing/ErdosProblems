#include <algorithm>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <vector>

int main(int argc, char** argv) {
  const int limit = argc > 1 ? std::stoi(argv[1]) : 10000000;
  const int max_sum = argc > 2 ? std::stoi(argv[2]) : 2000;
  const int first = 1849;
  std::vector<int> remaining(limit - first + 1);
  std::iota(remaining.begin(), remaining.end(), first);
  int max_used = 0;
  for (int s = 3; s <= max_sum && !remaining.empty(); ++s) {
    std::vector<int64_t> threshold(s, INT64_MAX);
    for (int a = 1; a * 2 < s; ++a) {
      const int b = s - a;
      const int residue = (int)((int64_t)a * b % s);
      threshold[residue] = std::min(threshold[residue],
          (int64_t)a * b + (int64_t)(b + 1) * s);
    }
    size_t out = 0;
    size_t before = remaining.size();
    for (int n : remaining) {
      if ((int64_t)n < threshold[n % s]) remaining[out++] = n;
    }
    remaining.resize(out);
    if (out != before) max_used = s;
    if (s <= 20 || s % 50 == 0 || remaining.empty())
      std::cout << "s=" << s << " remaining=" << remaining.size() << '\n';
  }
  std::cout << "limit=" << limit << " max_used=" << max_used
            << " remaining=" << remaining.size() << '\n';
  for (size_t i = 0; i < std::min<size_t>(remaining.size(), 40); ++i)
    std::cout << remaining[i] << (i + 1 == std::min<size_t>(remaining.size(), 40) ? '\n' : ' ');
  return remaining.empty() ? 0 : 2;
}
