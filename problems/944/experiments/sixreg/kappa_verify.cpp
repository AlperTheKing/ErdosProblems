// kappa_verify.cpp (2026-06-12): EXACT verification of the minimal-shore axiom
// kappa(X) := 6|X| - 2e(X) >= 8 for all 2 <= |X| <= |V|-2, on the 12 audited
// PG+diamond instances (edge dumps avenue_a_graph_inst*.txt from avenue_a_audit).
// Identity: kappa(X) = sum_{x in X} b(x) + e(X, V\X), b(x) = 6 - deg(x).
// Flow formulation: apex source s with arc capacities b(x) to each x; undirected
// unit capacities on K-edges. For every (s1; {t1,t2}): min cut with s,s1 on the
// source side and t1,t2 on the sink side equals min kappa(X) over X containing
// {t1,t2}, avoiding s1.  |X| = 67 cuts have kappa = 12 - 2 b(s1) >= 10, so any
// cut of value < 8 found this way is a genuine axiom violation with
// 2 <= |X| <= 66; conversely every violating X is caught by some triple.
// Early-exit flows at 8.  Sizes 67 handled by the formula above.
#include <cstdio>
#include <cstring>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

struct Dinic {
  struct E { int to, cap; };
  vector<E> es; vector<vector<int>> g; int n;
  vector<int> level, it;
  void init(int n_) { n = n_; es.clear(); g.assign(n, {}); }
  void add(int a, int b, int c, int c2 = 0) {
    g[a].push_back((int)es.size()); es.push_back({b, c});
    g[b].push_back((int)es.size()); es.push_back({a, c2});
  }
  bool bfs(int s, int t) {
    level.assign(n, -1); level[s] = 0;
    queue<int> q; q.push(s);
    while (!q.empty()) { int u = q.front(); q.pop();
      for (int id : g[u]) if (es[id].cap > 0 && level[es[id].to] < 0) {
        level[es[id].to] = level[u] + 1; q.push(es[id].to); } }
    return level[t] >= 0;
  }
  int dfs(int u, int t, int f) {
    if (u == t) return f;
    for (int& i = it[u]; i < (int)g[u].size(); i++) {
      int id = g[u][i]; auto& e = es[id];
      if (e.cap > 0 && level[e.to] == level[u] + 1) {
        int d = dfs(e.to, t, min(f, e.cap));
        if (d > 0) { e.cap -= d; es[id ^ 1].cap += d; return d; }
      }
    }
    return 0;
  }
  int maxflow(int s, int t, int limit) {
    int fl = 0;
    while (fl < limit && bfs(s, t)) {
      it.assign(n, 0);
      int f;
      while (fl < limit && (f = dfs(s, t, limit - fl)) > 0) fl += f;
    }
    return fl;
  }
};

int main() {
  const int INF = 1 << 28;
  for (int inst = 0; inst < 12; inst++) {
    char fn[64]; snprintf(fn, sizeof fn, "avenue_a_graph_inst%d.txt", inst);
    FILE* fp = fopen(fn, "r");
    if (!fp) { printf("inst %d: no dump\n", inst); continue; }
    vector<pair<int,int>> edges; int a, b, n = 0;
    while (fscanf(fp, "%d %d", &a, &b) == 2) { edges.push_back({a, b}); n = max(n, max(a, b) + 1); }
    fclose(fp);
    vector<int> deg(n, 0);
    for (auto& e : edges) { deg[e.first]++; deg[e.second]++; }
    int S = n;                          // apex source
    // base network
    Dinic base; base.init(n + 1);
    for (auto& e : edges) base.add(e.first, e.second, 1, 1);
    for (int x = 0; x < n; x++) if (deg[x] < 6) base.add(S, x, 6 - deg[x]);
    int globalMin = INF;
    int s1min = -1, t1min = -1, t2min = -1;
    vector<Dinic::E> baseEs = base.es;
    for (int s1 = 0; s1 < n; s1++) {
      for (int t1 = 0; t1 < n; t1++) {
        if (t1 == s1) continue;
        for (int t2 = t1 + 1; t2 < n; t2++) {
          if (t2 == s1) continue;
          Dinic d = base; d.es = baseEs;          // reset capacities
          d.add(S, s1, INF);                      // force s1 to source side
          d.add(t2, t1, INF);                     // force t2 to sink side
          int f = d.maxflow(S, t1, 8);
          if (f < globalMin) { globalMin = f; s1min = s1; t1min = t1; t2min = t2; }
        }
      }
      if (globalMin < 8) break;
    }
    // |X| = 67 cuts: kappa = 12 - 2 b(y) (y the excluded vertex)
    int min67 = INF;
    for (int y = 0; y < n; y++) min67 = min(min67, 12 - 2 * (6 - deg[y]));
    printf("inst %d: n=%d minkappa(2<=|X|<=66) %s 8 (flow min(capped)=%d at s1=%d t={%d,%d}); min kappa(|X|=67)=%d -> axiom %s\n",
           inst, n, globalMin >= 8 ? ">=" : "<", globalMin, s1min, t1min, t2min, min67,
           (globalMin >= 8 && min67 >= 8) ? "VERIFIED" : "VIOLATED");
    fflush(stdout);
  }
  return 0;
}
