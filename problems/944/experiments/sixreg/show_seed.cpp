// Print basic labelled structure of a graph6/edge-list seed.
#include <algorithm>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;

struct G {
  int n = 0;
  uint32_t adj[32]{};
  void add(int u, int v) {
    n = max(n, max(u, v) + 1);
    adj[u] |= 1u << v;
    adj[v] |= 1u << u;
  }
  bool edge(int u, int v) const { return (adj[u] >> v) & 1u; }
};

static G parse(const string& path) {
  ifstream in(path);
  if (!in) throw runtime_error("cannot open");
  string text((istreambuf_iterator<char>(in)), istreambuf_iterator<char>());
  size_t first = text.find_first_not_of(" \t\r\n");
  if (first == string::npos) throw runtime_error("empty");
  G g;
  if (!isdigit((unsigned char)text[first]) && text[first] != '[' && text[first] != '(') {
    string s = text.substr(first);
    size_t end = s.find_first_of("\r\n \t");
    if (end != string::npos) s = s.substr(0, end);
    int n = s[0] - 63;
    g.n = n;
    int bit = 0;
    for (int j = 1; j < n; j++) {
      for (int i = 0; i < j; i++) {
        int byte = 1 + bit / 6, off = 5 - bit % 6;
        if (((s[byte] - 63) >> off) & 1) g.add(i, j);
        bit++;
      }
    }
    return g;
  }
  vector<int> vals;
  for (size_t i = 0; i < text.size();) {
    if (!isdigit((unsigned char)text[i])) {
      i++;
      continue;
    }
    int x = 0;
    while (i < text.size() && isdigit((unsigned char)text[i])) {
      x = 10 * x + (text[i] - '0');
      i++;
    }
    vals.push_back(x);
  }
  for (size_t i = 0; i + 1 < vals.size(); i += 2) g.add(vals[i], vals[i + 1]);
  return g;
}

int main(int argc, char** argv) {
  if (argc < 2) return 2;
  G g = parse(argv[1]);
  cout << "n=" << g.n << "\n";
  cout << "edges";
  for (int i = 0; i < g.n; i++) {
    for (int j = i + 1; j < g.n; j++) {
      if (g.edge(i, j)) cout << " (" << i << "," << j << ")";
    }
  }
  cout << "\n";
  for (int i = 0; i < g.n; i++) {
    cout << i << ":";
    for (int j = 0; j < g.n; j++) {
      if (g.edge(i, j)) cout << " " << j;
    }
    cout << "\n";
  }
  cout << "nonedges";
  for (int i = 0; i < g.n; i++) {
    for (int j = i + 1; j < g.n; j++) {
      if (!g.edge(i, j)) cout << " (" << i << "," << j << ")";
    }
  }
  cout << "\n";
  return 0;
}
