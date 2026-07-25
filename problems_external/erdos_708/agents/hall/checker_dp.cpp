#include <algorithm>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <utility>
#include <vector>

using namespace std;

static vector<int> placements_for(int a, int first, int M) {
    vector<int> out;
    for (int j = 0; j < M; ++j) {
        if ((first + j) % a == 0) out.push_back(1 << j);
    }
    for (int u = 2; u * u <= a; ++u) {
        if (a % u != 0) continue;
        int v = a / u;
        if (v == 1) continue;
        for (int j = 0; j < M; ++j) {
            if ((first + j) % u != 0) continue;
            for (int k = 0; k < M; ++k) {
                if (j == k || (first + k) % v != 0) continue;
                out.push_back((1 << j) | (1 << k));
            }
        }
        if (u != v) {
            for (int j = 0; j < M; ++j) {
                if ((first + j) % v != 0) continue;
                for (int k = 0; k < M; ++k) {
                    if (j == k || (first + k) % u != 0) continue;
                    out.push_back((1 << j) | (1 << k));
                }
            }
        }
    }
    sort(out.begin(), out.end());
    out.erase(unique(out.begin(), out.end()), out.end());
    return out;
}

static bool feasible(const vector<int>& A, const vector<vector<int>>& placements,
                     int M, vector<int>* witness = nullptr) {
    const int S = 1 << M;
    vector<uint8_t> now(S), next(S);
    vector<vector<pair<int, int>>> parent;
    if (witness) parent.assign(A.size() + 1, vector<pair<int, int>>(S, {-1, -1}));
    now[0] = 1;
    for (size_t i = 0; i < A.size(); ++i) {
        fill(next.begin(), next.end(), 0);
        for (int used = 0; used < S; ++used) {
            if (!now[used]) continue;
            for (int pm : placements[A[i]]) {
                if (used & pm) continue;
                int nu = used | pm;
                if (!next[nu]) {
                    next[nu] = 1;
                    if (witness) parent[i + 1][nu] = {used, pm};
                }
            }
        }
        now.swap(next);
        if (none_of(now.begin(), now.end(), [](uint8_t x) { return x != 0; }))
            return false;
    }
    if (witness) {
        int used = int(find(now.begin(), now.end(), uint8_t(1)) - now.begin());
        witness->assign(A.size(), 0);
        for (int i = int(A.size()); i >= 1; --i) {
            auto [old, pm] = parent[i][used];
            (*witness)[i - 1] = pm;
            used = old;
        }
    }
    return true;
}

int main(int argc, char** argv) {
    int maxM = argc >= 2 ? stoi(argv[1]) : 10;
    for (int M = 2; M <= maxM; ++M) {
        int L = 1;
        for (int d = 1; d <= M; ++d) L = lcm(L, d);
        cerr << "M=" << M << " period=" << L << "\n";
        for (int first = 1; first <= L; ++first) {
            vector<vector<int>> placements(M + 1);
            for (int a = 2; a <= M; ++a)
                placements[a] = placements_for(a, first, M);
            for (int subset = 1; subset < (1 << (M - 1)); ++subset) {
                vector<int> A;
                bool immediate = false;
                for (int bit = 0; bit < M - 1; ++bit) {
                    if (!(subset & (1 << bit))) continue;
                    int a = bit + 2;
                    A.push_back(a);
                    if (placements[a].empty()) immediate = true;
                }
                if (immediate || !feasible(A, placements, M)) {
                    cout << "FAIL M=" << M << " first=" << first << " A=";
                    for (int a : A) cout << a << ",";
                    cout << "\nI=";
                    for (int j = 0; j < M; ++j) cout << first + j << ",";
                    cout << "\n";
                    return 1;
                }
            }
        }
        cout << "PASS M=" << M << " intervals=" << L
             << " subsets_per_interval=" << ((1 << (M - 1)) - 1) << "\n";
    }
    return 0;
}
