#include <algorithm>
#include <fstream>
#include <iostream>
#include <set>
#include <vector>
using namespace std;

int main(int argc, char** argv) {
    if (argc != 2) { cerr << "usage: verify_by_indices CERT\n"; return 2; }
    ifstream f(argv[1]);
    long long N, m0, m1;
    if (!(f >> N >> m0) || N < 0 || m0 < 0) { cout << "PARSE_ERROR\n"; return 3; }
    vector<long long> s[2]; s[0].resize((size_t)m0);
    for (auto& v : s[0]) if (!(f >> v)) { cout << "PARSE_ERROR\n"; return 3; }
    if (!(f >> m1) || m1 < 0) { cout << "PARSE_ERROR\n"; return 3; }
    s[1].resize((size_t)m1);
    for (auto& v : s[1]) if (!(f >> v)) { cout << "PARSE_ERROR\n"; return 3; }
    long long junk; if (f >> junk) { cout << "TRAILING_DATA\n"; return 3; }
    set<long long> seen;
    for (int c=0;c<2;++c) for (auto v:s[c]) if (v<1 || v>N || !seen.insert(v).second) {
        cout << "PARTITION_ERROR\n"; return 4;
    }
    if ((long long)seen.size()!=N) { cout << "PARTITION_ERROR\n"; return 4; }
    for (int c=0;c<2;++c) {
        const auto& a=s[c];
        for (size_t i=0;i<a.size();++i) for (size_t j=i+1;j<a.size();++j) for (size_t k=j+1;k<a.size();++k) {
            bool monotone=(a[i]<a[j] && a[j]<a[k]) || (a[i]>a[j] && a[j]>a[k]);
            if (monotone && a[i]+a[k]==2*a[j]) {
                cout << "INVALID colour=" << c << " indices=" << i << ',' << j << ',' << k
                     << " values=" << a[i] << ',' << a[j] << ',' << a[k] << "\n";
                return 1;
            }
        }
    }
    cout << "VALID n=" << N << " sizes=" << s[0].size() << ',' << s[1].size() << "\n";
    return 0;
}
