#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using u64 = std::uint64_t;

template <typename Residue>
u64 orbit_size(u64 modulus) {
  std::vector<std::uint8_t> seen(static_cast<std::size_t>(modulus), 0);
  std::vector<Residue> queue;

  auto insert = [&](u64 residue) {
    const auto index = static_cast<std::size_t>(residue);
    if (!seen[index]) {
      seen[index] = 1;
      queue.push_back(static_cast<Residue>(residue));
    }
  };

  // Every nonseed element is a word in the three maps applied to 9 or 14.
  insert(9 % modulus);
  insert(14 % modulus);
  for (std::size_t head = 0; head < queue.size(); ++head) {
    const u64 x = queue[head];
    for (const u64 multiplier : std::array<u64, 3>{2, 3, 5}) {
      insert((multiplier * x + modulus - 1) % modulus);
    }
  }
  insert(2 % modulus);
  insert(3 % modulus);
  insert(5 % modulus);
  return queue.size();
}

}  // namespace

int main(int argc, char** argv) {
  try {
    int maximum_power = 6;
    if (argc == 3 && std::string(argv[1]) == "--max-power") {
      maximum_power = std::stoi(argv[2]);
    } else if (argc != 1) {
      throw std::invalid_argument("usage: residue_closure [--max-power A]");
    }
    if (maximum_power < 1) {
      throw std::invalid_argument("maximum power must be positive");
    }

    u64 modulus = 1;
    std::cout << "a,modulus,residues,fraction,seconds\n";
    for (int exponent = 1; exponent <= maximum_power; ++exponent) {
      modulus *= 30;
      const auto started = std::chrono::steady_clock::now();
      const u64 count =
          modulus <= std::numeric_limits<std::uint32_t>::max()
              ? orbit_size<std::uint32_t>(modulus)
              : orbit_size<std::uint64_t>(modulus);
      const double seconds = std::chrono::duration<double>(
                                 std::chrono::steady_clock::now() - started)
                                 .count();
      std::cout << exponent << ',' << modulus << ',' << count << ','
                << std::fixed << std::setprecision(12)
                << static_cast<long double>(count) / modulus << ',' << seconds
                << '\n';
    }
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}
