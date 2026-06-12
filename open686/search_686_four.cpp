#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>

#ifdef _OPENMP
#include <omp.h>
#endif

using namespace std;
using boost::multiprecision::cpp_int;

static const int MOD = 1000003;

cpp_int prod_int(int k, long long x) {
    cpp_int r = 1;
    for (int i = 1; i <= k; i++) r *= (x + i);
    return r;
}

bool exact_hit(int target, int k, long long n, long long m) {
    if (m < n + k) return false;
    return prod_int(k, m) == prod_int(k, n) * target;
}

int prod_mod(int k, long long x) {
    long long r = 1;
    long long xm = x % MOD;
    if (xm < 0) xm += MOD;
    for (int i = 1; i <= k; i++) r = r * ((xm + i) % MOD) % MOD;
    return (int)r;
}

int step_mod(int cur, int k, long long x, const vector<int>& inv) {
    long long den = (x + 1) % MOD;
    if (den < 0) den += MOD;
    if (den == 0) return prod_mod(k, x + 1);
    long long num = (x + k + 1) % MOD;
    if (num < 0) num += MOD;
    return (long long)cur * inv[(int)den] % MOD * num % MOD;
}

long long binary_find(int target, int k, long long n) {
    cpp_int want = prod_int(k, n) * target;
    long long lo = n + k;
    cpp_int plo = prod_int(k, lo);
    if (plo > want) return -1;
    if (plo == want) return lo;

    long double alpha = powl((long double)target, 1.0L / (long double)k);
    long long hi = max(lo + 1, (long long)(alpha * (long double)(n + 1) + k + 16));
    while (prod_int(k, hi) < want) {
        if (hi > (LLONG_MAX - 1) / 2) return -1;
        hi = hi * 2 + 1;
    }
    while (lo + 1 < hi) {
        long long mid = lo + (hi - lo) / 2;
        if (prod_int(k, mid) < want)
            lo = mid;
        else
            hi = mid;
    }
    return prod_int(k, hi) == want ? hi : -1;
}

long long center_from_consts(long double alpha, long double c, long double beta, long long n) {
    long double N = (long double)n + c;
    return llround(alpha * N + beta / N - c);
}

bool validate_known_examples() {
    bool ok = true;
    ok = ok && exact_hit(9, 3, 11, 25);
    ok = ok && exact_hit(16, 3, 4, 13);
    ok = ok && binary_find(9, 3, 11) == 25;
    ok = ok && binary_find(16, 3, 4) == 13;
    cerr << "validation N=9 (3,11,25), N=16 (3,4,13): " << (ok ? "ok" : "FAILED") << "\n";
    return ok;
}

int main(int argc, char** argv) {
    int target = argc > 1 ? atoi(argv[1]) : 4;
    int K0 = argc > 2 ? atoi(argv[2]) : 4;
    int K1 = argc > 3 ? atoi(argv[3]) : 200;
    long long N0 = argc > 4 ? atoll(argv[4]) : 0;
    long long N1 = argc > 5 ? atoll(argv[5]) : 10000000LL;
    int R = argc > 6 ? atoi(argv[6]) : 8;
    long long exact_until = argc > 7 ? atoll(argv[7]) : 20000LL;

    if (!validate_known_examples()) return 2;

    vector<int> inv(MOD);
    inv[1] = 1;
    for (int i = 2; i < MOD; i++) inv[i] = (long long)(MOD - MOD / i) * inv[MOD % i] % MOD;

    atomic<bool> found(false);
    int fk = 0;
    long long fn = 0, fm = 0;

    int threads = 1;
#ifdef _OPENMP
    threads = omp_get_max_threads();
#endif
    cerr << "target=" << target << " K=" << K0 << ".." << K1 << " n=" << N0 << ".." << N1
         << " R=" << R << " exact_until=" << exact_until << " threads=" << threads << "\n";

#pragma omp parallel for schedule(dynamic, 1)
    for (int k = K0; k <= K1; k++) {
        if (found.load()) continue;

        long double alpha = powl((long double)target, 1.0L / (long double)k);
        long double c = ((long double)k + 1.0L) / 2.0L;
        long double A = -((long double)k * ((long double)k * k - 1.0L)) / 24.0L;
        long double beta = alpha * A * (1.0L - 1.0L / (alpha * alpha)) / (long double)k;

        long long local_exact_hi = min(N1, max(N0 - 1, exact_until));
        for (long long n = N0; n <= local_exact_hi && !found.load(); n++) {
            long long m = binary_find(target, k, n);
            if (m >= 0) {
                bool expected = false;
                if (found.compare_exchange_strong(expected, true)) {
                    fk = k;
                    fn = n;
                    fm = m;
                }
                break;
            }
        }

        long long start = max(N0, local_exact_hi + 1);
        if (start <= N1 && !found.load()) {
            long long n = start;
            int pn = prod_mod(k, n);
            vector<long long> mx(2 * R + 1);
            vector<int> pm(2 * R + 1);
            long long cen = center_from_consts(alpha, c, beta, n);
            for (int idx = 0; idx < 2 * R + 1; idx++) {
                long long m = cen + (idx - R);
                mx[idx] = m;
                pm[idx] = m >= 0 ? prod_mod(k, m) : 0;
            }
            for (; n <= N1 && !found.load(); n++) {
                if (n > start) pn = step_mod(pn, k, n - 1, inv);
                long long newcen = center_from_consts(alpha, c, beta, n);
                if (newcen != cen) {
                    for (int idx = 0; idx < 2 * R + 1; idx++) {
                        long long tm = newcen + (idx - R);
                        if (mx[idx] < 0 || tm < mx[idx] || tm - mx[idx] > 20) {
                            mx[idx] = tm;
                            pm[idx] = tm >= 0 ? prod_mod(k, tm) : 0;
                        } else {
                            while (mx[idx] < tm) {
                                pm[idx] = step_mod(pm[idx], k, mx[idx], inv);
                                mx[idx]++;
                            }
                        }
                    }
                    cen = newcen;
                }
                int want = (long long)(target % MOD) * pn % MOD;
                for (int idx = 0; idx < 2 * R + 1; idx++) {
                    long long m = mx[idx];
                    if (m >= n + k && pm[idx] == want && exact_hit(target, k, n, m)) {
                        bool expected = false;
                        if (found.compare_exchange_strong(expected, true)) {
                            fk = k;
                            fn = n;
                            fm = m;
                        }
                        break;
                    }
                }
            }
        }

#pragma omp critical
        {
            if (!found.load()) cerr << "completed k=" << k << "\n";
        }
    }

    if (found.load()) {
        cout << "HIT " << fk << " " << fn << " " << fm << "\n";
        return 0;
    }
    cout << "NO_HIT_TARGET " << target << " " << K0 << " " << K1 << " " << N0 << " " << N1 << "\n";
    return 0;
}
