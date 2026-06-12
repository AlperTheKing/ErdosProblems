// Tiny graph6 isomorphism checker for n <= 10-ish diagnostics.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

struct G {
  int n = 0;
  bool e[16][16]{};
};

static G decode(const string& s) {
  G g;
  g.n = s[0] - 63;
  int bit = 0;
  for (int j = 1; j < g.n; j++) {
    for (int i = 0; i < j; i++) {
      int byte = 1 + bit / 6, off = 5 - bit % 6;
      bool edge = ((s[byte] - 63) >> off) & 1;
      g.e[i][j] = g.e[j][i] = edge;
      bit++;
    }
  }
  return g;
}

int main(int argc, char** argv) {
  if (argc != 3) {
    cerr << "usage: iso_g6.exe g6a g6b\n";
    return 2;
  }
  G a = decode(argv[1]), b = decode(argv[2]);
  if (a.n != b.n) {
    cout << "isomorphic=0\n";
    return 0;
  }
  vector<int> p(a.n);
  for (int i = 0; i < a.n; i++) p[i] = i;
  do {
    bool ok = true;
    for (int i = 0; i < a.n && ok; i++) {
      for (int j = i + 1; j < a.n; j++) {
        if (a.e[i][j] != b.e[p[i]][p[j]]) {
          ok = false;
          break;
        }
      }
    }
    if (ok) {
      cout << "isomorphic=1 permutation";
      for (int x : p) cout << " " << x;
      cout << "\n";
      return 0;
    }
  } while (next_permutation(p.begin(), p.end()));
  cout << "isomorphic=0\n";
  return 0;
}
