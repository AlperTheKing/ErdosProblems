// Classify list-critical terminal patterns on the six-vertex TB6 shape.
//
// Vertices p,q,r,s,t,u are 0,1,2,3,4,5 with edges
// pr, ps, pt, qr, qt, qu, rs, rt, su.
// A pattern chooses a free terminal a and an A-forbidden set R containing the
// mate a' but not a.  Vertices in R have list {B,C}; others have {A,B,C}.
// We report patterns where the whole graph is list-uncolourable but every
// proper induced subgraph is list-colourable.
#include <array>
#include <cstdint>
#include <functional>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using namespace std;

static constexpr uint8_t ALL = 0b111;
static const char* namev = "pqrstu";

struct Graph {
  uint32_t adj[6]{};
  void add(int a, int b) { adj[a] |= 1u << b; adj[b] |= 1u << a; }
};

static bool list_colourable(const Graph& g, uint32_t mask, const array<uint8_t, 6>& lists) {
  vector<int> verts;
  for (int v = 0; v < 6; v++) if ((mask >> v) & 1u) verts.push_back(v);
  array<int8_t, 6> col;
  col.fill(-1);
  function<bool(int)> dfs = [&](int pos) -> bool {
    if (pos == (int)verts.size()) return true;
    int v = verts[pos];
    uint8_t avail = lists[v];
    uint32_t nb = g.adj[v] & mask;
    while (nb) {
      int u = __builtin_ctz(nb);
      nb &= nb - 1;
      if (col[u] >= 0) avail &= (uint8_t)~(1u << col[u]);
    }
    for (int c = 0; c < 3; c++) {
      if (((avail >> c) & 1u) == 0) continue;
      col[v] = (int8_t)c;
      if (dfs(pos + 1)) return true;
      col[v] = -1;
    }
    return false;
  };
  return dfs(0);
}

static string set_name(uint32_t mask) {
  string s = "{";
  bool first = true;
  for (int v = 0; v < 6; v++) {
    if (((mask >> v) & 1u) == 0) continue;
    if (!first) s += ",";
    first = false;
    s.push_back(namev[v]);
  }
  s += "}";
  return s;
}

int main() {
  Graph g;
  g.add(0,2); g.add(0,3); g.add(0,4);
  g.add(1,2); g.add(1,4); g.add(1,5);
  g.add(2,3); g.add(2,4); g.add(3,5);
  uint32_t full = 0b111111;
  map<int, int> by_restricted_size;
  int total = 0;
  for (int terminal = 0; terminal < 6; terminal++) {
    for (int mate = 0; mate < 6; mate++) {
      if (mate == terminal) continue;
      for (uint32_t R = 0; R < 64; R++) {
        if (((R >> terminal) & 1u) != 0) continue;
        if (((R >> mate) & 1u) == 0) continue;
        array<uint8_t, 6> lists;
        lists.fill(ALL);
        for (int v = 0; v < 6; v++) {
          if ((R >> v) & 1u) lists[v] = 0b110;
        }
        if (list_colourable(g, full, lists)) continue;
        bool minimal = true;
        for (int v = 0; v < 6; v++) {
          if (!list_colourable(g, full & ~(1u << v), lists)) {
            minimal = false;
            break;
          }
        }
        if (!minimal) continue;
        total++;
        by_restricted_size[__builtin_popcount(R)]++;
        cout << "PATTERN terminal=" << namev[terminal]
             << " mate=" << namev[mate]
             << " restricted=" << set_name(R)
             << " free=" << set_name(full & ~R)
             << "\n";
      }
    }
  }
  cout << "SUMMARY total=" << total << " byRestrictedSize";
  for (auto [k, v] : by_restricted_size) cout << " [" << k << "]=" << v;
  cout << "\n";
}
