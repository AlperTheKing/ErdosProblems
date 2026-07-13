#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

struct Term {
  int row;
  int col;
  std::string value;
};

static std::string json_string_value(const std::string& line, const std::string& key) {
  const std::string needle = "\"" + key + "\":";
  size_t p = line.find(needle);
  if (p == std::string::npos) return "";
  p += needle.size();
  while (p < line.size() && (line[p] == ' ' || line[p] == '\t')) ++p;
  if (p < line.size() && line[p] == '"') {
    size_t q = line.find('"', p + 1);
    return q == std::string::npos ? "" : line.substr(p + 1, q - p - 1);
  }
  size_t q = p;
  while (q < line.size() && line[q] != ',' && line[q] != '}') ++q;
  return line.substr(p, q - p);
}

static int json_int_value(const std::string& line, const std::string& key, int def = 0) {
  std::string s = json_string_value(line, key);
  return s.empty() ? def : std::stoi(s);
}

static uint32_t mod_pow(uint32_t a, uint32_t e, uint32_t p) {
  uint64_t res = 1, base = a;
  while (e) {
    if (e & 1) res = (res * base) % p;
    base = (base * base) % p;
    e >>= 1;
  }
  return static_cast<uint32_t>(res);
}

static uint32_t mod_inv(uint32_t a, uint32_t p) {
  return mod_pow(a, p - 2, p);
}

static uint32_t decimal_mod(const std::string& raw, uint32_t p) {
  bool neg = false;
  size_t i = 0;
  if (i < raw.size() && raw[i] == '-') {
    neg = true;
    ++i;
  }
  uint64_t r = 0;
  for (; i < raw.size(); ++i) {
    char c = raw[i];
    if (c < '0' || c > '9') continue;
    r = (r * 10 + static_cast<unsigned>(c - '0')) % p;
  }
  if (neg && r) r = p - r;
  return static_cast<uint32_t>(r);
}

static uint32_t frac_mod(const std::string& s, uint32_t p) {
  size_t slash = s.find('/');
  if (slash == std::string::npos) return decimal_mod(s, p);
  uint32_t num = decimal_mod(s.substr(0, slash), p);
  uint32_t den = decimal_mod(s.substr(slash + 1), p);
  if (den == 0) return UINT32_MAX;
  return static_cast<uint32_t>((static_cast<uint64_t>(num) * mod_inv(den, p)) % p);
}

int main(int argc, char** argv) {
  if (argc != 3) {
    std::cerr << "usage: codex_mod_prime_solve CORE PRIME\n";
    return 2;
  }
  const std::string core_path = argv[1];
  const uint32_t p = static_cast<uint32_t>(std::stoul(argv[2]));

  std::ifstream in(core_path);
  if (!in) {
    std::cerr << "cannot open core\n";
    return 2;
  }

  int n = -1;
  std::vector<Term> terms;
  std::vector<std::pair<int, std::string>> rhs_items;
  std::string line;
  while (std::getline(in, line)) {
    if (line.find("\"type\"") == std::string::npos) continue;
    std::string typ = json_string_value(line, "type");
    if (typ == "meta") {
      n = json_int_value(line, "dimension", -1);
    } else if (typ == "rhs") {
      rhs_items.push_back({json_int_value(line, "row"), json_string_value(line, "value")});
    } else if (typ == "term") {
      terms.push_back({json_int_value(line, "row"), json_int_value(line, "col"), json_string_value(line, "value")});
    }
  }
  if (n <= 0) {
    std::cerr << "missing/invalid dimension\n";
    return 2;
  }

  const int width = n + 1;
  std::vector<uint32_t> aug(static_cast<size_t>(n) * width, 0);
  auto at = [&](int r, int c) -> uint32_t& { return aug[static_cast<size_t>(r) * width + c]; };

  for (const auto& t : terms) {
    uint32_t v = frac_mod(t.value, p);
    if (v == UINT32_MAX) {
      std::cout << "{\"ok\":false,\"prime\":" << p << ",\"reason\":\"zero_denominator\"}\n";
      return 0;
    }
    uint32_t& cell = at(t.row, t.col);
    uint32_t nv = cell + v;
    if (nv >= p || nv < cell) nv %= p;
    cell = nv;
  }
  for (const auto& item : rhs_items) {
    uint32_t v = frac_mod(item.second, p);
    if (v == UINT32_MAX) {
      std::cout << "{\"ok\":false,\"prime\":" << p << ",\"reason\":\"zero_denominator\"}\n";
      return 0;
    }
    at(item.first, n) = v;
  }

  for (int k = 0; k < n; ++k) {
    int piv = -1;
    for (int r = k; r < n; ++r) {
      if (at(r, k) != 0) {
        piv = r;
        break;
      }
    }
    if (piv < 0) {
      std::cout << "{\"ok\":false,\"prime\":" << p << ",\"reason\":\"singular\"}\n";
      return 0;
    }
    if (piv != k) {
      for (int c = k; c <= n; ++c) std::swap(at(k, c), at(piv, c));
    }
    uint32_t inv = mod_inv(at(k, k), p);
    for (int c = k; c <= n; ++c) at(k, c) = static_cast<uint32_t>((static_cast<uint64_t>(at(k, c)) * inv) % p);
    for (int r = k + 1; r < n; ++r) {
      uint32_t factor = at(r, k);
      if (!factor) continue;
      at(r, k) = 0;
      for (int c = k + 1; c <= n; ++c) {
        uint32_t sub = static_cast<uint32_t>((static_cast<uint64_t>(factor) * at(k, c)) % p);
        uint32_t cur = at(r, c);
        at(r, c) = cur >= sub ? (cur - sub) : (cur + p - sub);
      }
    }
  }

  std::vector<uint32_t> x(n, 0);
  for (int i = n - 1; i >= 0; --i) {
    uint64_t total = 0;
    for (int c = i + 1; c < n; ++c) {
      total += static_cast<uint64_t>(at(i, c)) * x[c];
      if ((c & 7) == 7) total %= p;
    }
    total %= p;
    uint32_t rhs = at(i, n);
    x[i] = rhs >= total ? static_cast<uint32_t>(rhs - total) : static_cast<uint32_t>(rhs + p - total);
  }

  std::cout << "{\"ok\":true,\"prime\":" << p << ",\"residues\":[";
  for (int i = 0; i < n; ++i) {
    if (i) std::cout << ',';
    std::cout << x[i];
  }
  std::cout << "]}\n";
  return 0;
}
