#include <iostream>
#include <set>
#include <utility>
#include <vector>

using namespace std;

static bool assign_occurrences(const vector<int>& factors, const vector<int>& I,
                               size_t k, vector<bool>& used) {
    if (k == factors.size()) return true;
    for (size_t j = 0; j < I.size(); ++j) {
        if (!used[j] && I[j] % factors[k] == 0) {
            used[j] = true;
            if (assign_occurrences(factors, I, k + 1, used)) return true;
            used[j] = false;
        }
    }
    return false;
}

static bool choose_splits(const vector<int>& A, const vector<int>& I, size_t k,
                          vector<int>& factors, int& split_count) {
    if (k == A.size()) {
        ++split_count;
        vector<bool> used(I.size());
        return assign_occurrences(factors, I, 0, used);
    }
    int a = A[k];
    for (int u = 1; u <= a; ++u) {
        if (a % u != 0) continue;
        int v = a / u;
        size_t old = factors.size();
        if (u != 1) factors.push_back(u);
        if (v != 1) factors.push_back(v);
        if (choose_splits(A, I, k + 1, factors, split_count)) return true;
        factors.resize(old);
    }
    return false;
}

int main() {
    const vector<int> A{2, 3};
    const vector<int> I{5, 6, 7};

    if (A.size() != 2 || I.size() != 3) return 2;
    if (I.back() - I.front() + 1 != int(I.size())) return 3;
    if (I.size() != 3 || A.back() != 3) return 4;

    vector<int> factors;
    int split_count = 0;
    bool feasible = choose_splits(A, I, 0, factors, split_count);

    set<int> neighborhood;
    for (int b : I)
        if (b % 2 == 0 || b % 3 == 0) neighborhood.insert(b);

    cout << "A={2,3}; I={5,6,7}; split_choices=" << split_count << "\n";
    cout << "N(2)={6}; N(3)={6}; union_size=" << neighborhood.size()
         << "; occurrence_count=2\n";
    cout << "two_split_SDR=" << (feasible ? "SAT" : "UNSAT") << "\n";
    return feasible ? 1 : 0;
}
