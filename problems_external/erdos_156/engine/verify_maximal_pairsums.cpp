#include <algorithm>
#include <iostream>
#include <set>
#include <string>
#include <vector>

static bool sidon_by_pair_sums(const std::vector<int>& a) {
  std::set<int> sums;
  for (std::size_t i = 0; i < a.size(); ++i) {
    for (std::size_t j = i; j < a.size(); ++j) {
      if (!sums.insert(a[i] + a[j]).second) return false;
    }
  }
  return true;
}

int main(int argc, char** argv) {
  if (argc < 3) {
    std::cerr << "usage: verify_maximal_pairsums N a1 ... ak\n";
    return 2;
  }
  int n = std::stoi(argv[1]);
  std::vector<int> a;
  for (int i = 2; i < argc; ++i) a.push_back(std::stoi(argv[i]));
  std::sort(a.begin(), a.end());
  if (a.empty() || a.front() < 1 || a.back() > n ||
      std::adjacent_find(a.begin(), a.end()) != a.end()) {
    std::cout << "INVALID_DOMAIN\n";
    return 1;
  }
  if (!sidon_by_pair_sums(a)) {
    std::cout << "NOT_SIDON\n";
    return 1;
  }
  std::set<int> members(a.begin(), a.end());
  for (int x = 1; x <= n; ++x) {
    if (members.count(x)) continue;
    std::vector<int> extended = a;
    extended.push_back(x);
    std::sort(extended.begin(), extended.end());
    if (sidon_by_pair_sums(extended)) {
      std::cout << "NOT_MAXIMAL addable=" << x << "\n";
      return 1;
    }
  }
  std::cout << "VERIFIED N=" << n << " K=" << a.size() << "\n";
  return 0;
}
