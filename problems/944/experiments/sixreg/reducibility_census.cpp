// Count simple vertex-critical reducibility witnesses in classify_no_crit output.
//
// In a 4-vertex-critical graph, no two nonadjacent vertices may have comparable
// open neighbourhoods: if N(x) subseteq N(y), then any 3-colouring of G-y
// extends by colouring y like x. This tool checks how often no-critical-edge
// seeds already fail by this reducibility.
#include <cctype>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <map>
#include <string>
using namespace std;

static constexpr int MAXN = 32;

struct G {
  int n = 0;
  uint32_t adj[MAXN]{};
  void add(int u, int v) { adj[u] |= 1u << v; adj[v] |= 1u << u; }
  bool edge(int u, int v) const { return (adj[u] >> v) & 1u; }
};

static bool decode_g6(const string& s, G& g) {
  if (s.empty()) return false;
  int n = s[0] - 63;
  if (n <= 0 || n > MAXN) return false;
  g = G{};
  g.n = n;
  int nbits = n * (n - 1) / 2;
  int need = (nbits + 5) / 6;
  if ((int)s.size() < 1 + need) return false;
  int bit = 0;
  for (int j = 1; j < n; j++) {
    for (int i = 0; i < j; i++) {
      int byte = 1 + bit / 6, off = 5 - bit % 6;
      if (((s[byte] - 63) >> off) & 1) g.add(i, j);
      bit++;
    }
  }
  return true;
}

static string extract_g6(const string& line) {
  size_t p = line.find("G6:");
  if (p == string::npos) return "";
  p += 3;
  while (p < line.size() && isspace((unsigned char)line[p])) p++;
  size_t q = p;
  while (q < line.size() && !isspace((unsigned char)line[q])) q++;
  return line.substr(p, q - p);
}

static int parse_failures(const string& line) {
  size_t p = line.find("failures=");
  if (p == string::npos) return -1;
  p += 9;
  int x = 0;
  while (p < line.size() && isdigit((unsigned char)line[p])) {
    x = 10 * x + (line[p] - '0');
    p++;
  }
  return x;
}

int main() {
  string line;
  long long graphs = 0;
  map<int, long long> graphs_by_failures;
  map<int, long long> comp_pairs_by_failures;
  map<int, long long> twin_pairs_by_failures;
  map<int, long long> graphs_with_comp_by_failures;
  map<int, long long> graphs_with_twin_by_failures;
  map<string, long long> example_count;
  map<string, int> printed_by_bucket;

  while (getline(cin, line)) {
    if (line.rfind("NOCRIT_NOTVC", 0) != 0) continue;
    int failures = parse_failures(line);
    string g6 = extract_g6(line);
    G g;
    if (failures < 0 || !decode_g6(g6, g)) continue;
    graphs++;
    graphs_by_failures[failures]++;
    int comp = 0, twin = 0;
    string first_comp, first_twin;
    for (int x = 0; x < g.n; x++) {
      for (int y = x + 1; y < g.n; y++) {
        if (g.edge(x, y)) continue;
        uint32_t nx = g.adj[x] & ~(1u << y);
        uint32_t ny = g.adj[y] & ~(1u << x);
        bool xy = (nx & ~ny) == 0;
        bool yx = (ny & ~nx) == 0;
        if (xy || yx) {
          comp++;
          if (first_comp.empty()) first_comp = "(" + to_string(x) + "," + to_string(y) + ")";
        }
        if (nx == ny) {
          twin++;
          if (first_twin.empty()) first_twin = "(" + to_string(x) + "," + to_string(y) + ")";
        }
      }
    }
    comp_pairs_by_failures[failures] += comp;
    twin_pairs_by_failures[failures] += twin;
    if (comp) graphs_with_comp_by_failures[failures]++;
    if (twin) graphs_with_twin_by_failures[failures]++;
    string bucket = "fail=" + to_string(failures) + " comp=" + (comp ? "1" : "0");
    if (printed_by_bucket[bucket] < 5 && example_count[g6]++ == 0) {
      printed_by_bucket[bucket]++;
      cout << "EXAMPLE failures=" << failures << " comparable=" << comp
           << " twins=" << twin << " firstComparable=" << first_comp
           << " firstTwin=" << first_twin << " G6: " << g6 << "\n";
    }
  }

  cout << "graphs=" << graphs << "\n";
  cout << "graphs_by_failures";
  for (auto [k, v] : graphs_by_failures) cout << " [" << k << "]=" << v;
  cout << "\n";
  cout << "graphs_with_comparable_by_failures";
  for (auto [k, v] : graphs_with_comp_by_failures) cout << " [" << k << "]=" << v;
  cout << "\n";
  cout << "graphs_with_twins_by_failures";
  for (auto [k, v] : graphs_with_twin_by_failures) cout << " [" << k << "]=" << v;
  cout << "\n";
  cout << "total_comparable_pairs_by_failures";
  for (auto [k, v] : comp_pairs_by_failures) cout << " [" << k << "]=" << v;
  cout << "\n";
  cout << "total_twin_pairs_by_failures";
  for (auto [k, v] : twin_pairs_by_failures) cout << " [" << k << "]=" << v;
  cout << "\n";
  return 0;
}
