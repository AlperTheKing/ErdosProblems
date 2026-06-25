// Independent referee re-computation of min kappa(X) over all X with
// 2 <= |X| <= n-2 where both X and X^c span an edge of K, via the flow
// reduction: kappa(X) = cut_{K+}(X), K+ = K + stub vertex s with cap b(v)
// edges to each deficient v, s on the sink side.
// min over ordered disjoint edge pairs (e1 -> e2 + s), capped Dinic.
// Input (stdin): n m  then m lines "a b", then "k" then k lines "v b(v)".
// Output: min flow value (capped at CAP) and the argmin pair.
#include <bits/stdc++.h>
using namespace std;

struct Dinic {
    struct E { int to, cap, rev; };
    vector<vector<E>> g;
    vector<int> level, iter;
    int n;
    Dinic(int n_) : g(n_), level(n_), iter(n_), n(n_) {}
    void add(int a, int b, int c, int c2) {
        g[a].push_back({b, c, (int)g[b].size()});
        g[b].push_back({a, c2, (int)g[a].size() - 1});
    }
    bool bfs(int s, int t) {
        fill(level.begin(), level.end(), -1);
        deque<int> q; level[s] = 0; q.push_back(s);
        while (!q.empty()) {
            int v = q.front(); q.pop_front();
            for (auto &e : g[v]) if (e.cap > 0 && level[e.to] < 0) {
                level[e.to] = level[v] + 1; q.push_back(e.to);
            }
        }
        return level[t] >= 0;
    }
    int dfs(int v, int t, int f) {
        if (v == t) return f;
        for (int &i = iter[v]; i < (int)g[v].size(); i++) {
            E &e = g[v][i];
            if (e.cap > 0 && level[v] < level[e.to]) {
                int d = dfs(e.to, t, min(f, e.cap));
                if (d > 0) { e.cap -= d; g[e.to][e.rev].cap += d; return d; }
            }
        }
        return 0;
    }
    int maxflow(int s, int t, int cap) {
        int fl = 0;
        while (fl < cap && bfs(s, t)) {
            fill(iter.begin(), iter.end(), 0);
            int f;
            while (fl < cap && (f = dfs(s, t, cap - fl)) > 0) fl += f;
        }
        return fl;
    }
};

int main() {
    int n, m; scanf("%d %d", &n, &m);
    vector<pair<int,int>> ed(m);
    for (auto &e : ed) scanf("%d %d", &e.first, &e.second);
    int k; scanf("%d", &k);
    vector<pair<int,int>> stubs(k);
    for (auto &s : stubs) scanf("%d %d", &s.first, &s.second);
    const int CAP = 8;
    // nodes: 0..n-1 graph, n = s(stub), n+1 = super-source, n+2 = super-sink
    int S = n + 1, T = n + 2, N = n + 3;
    long long best = LLONG_MAX; int bi = -1, bj = -1; long long cnt = 0;
    for (int i = 0; i < m; i++) {
        auto [a1, b1] = ed[i];
        for (int j = 0; j < m; j++) {
            if (j == i) continue;
            auto [a2, b2] = ed[j];
            if (a2 == a1 || a2 == b1 || b2 == a1 || b2 == b1) continue;
            cnt++;
            Dinic D(N);
            for (auto &e : ed) D.add(e.first, e.second, 1, 1); // undirected cap 1
            for (auto &s : stubs) D.add(s.first, n, s.second, 0);
            D.add(S, a1, CAP, 0); D.add(S, b1, CAP, 0);
            D.add(a2, T, CAP, 0); D.add(b2, T, CAP, 0);
            D.add(n, T, CAP, 0);
            int f = D.maxflow(S, T, CAP);
            if (f < best) { best = f; bi = i; bj = j; }
        }
    }
    printf("pairs=%lld minflow(cap%d)=%lld argmin e1=(%d,%d) e2=(%d,%d)\n",
           cnt, CAP, best, ed[bi].first, ed[bi].second, ed[bj].first, ed[bj].second);
    return 0;
}
