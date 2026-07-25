#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main(int argc, char** argv) {
    if (argc != 2) { cerr << "usage: verify_by_values CERT\n"; return 2; }
    ifstream in(argv[1]);
    int n;
    if (!(in >> n) || n < 0) { cout << "{\"status\":\"PARSE_ERROR\"}\n"; return 3; }
    vector<vector<int>> seq(2);
    vector<int> colour(n + 1, -1), pos(n + 1, -1);
    for (int c = 0; c < 2; ++c) {
        int m;
        if (!(in >> m) || m < 0) { cout << "{\"status\":\"PARSE_ERROR\"}\n"; return 3; }
        seq[c].resize(m);
        for (int i = 0; i < m; ++i) {
            int x;
            if (!(in >> x) || x < 1 || x > n || colour[x] != -1) {
                cout << "{\"status\":\"PARTITION_ERROR\",\"colour\":" << c << ",\"position\":" << i << "}\n";
                return 4;
            }
            seq[c][i] = x; colour[x] = c; pos[x] = i;
        }
    }
    string extra;
    if (in >> extra) { cout << "{\"status\":\"TRAILING_DATA\"}\n"; return 3; }
    for (int x = 1; x <= n; ++x) if (colour[x] == -1) {
        cout << "{\"status\":\"PARTITION_ERROR\",\"missing\":" << x << "}\n"; return 4;
    }
    for (int x = 1; x <= n; ++x) for (int d = 1; x + 2*d <= n; ++d) {
        int y = x + d, z = x + 2*d;
        if (colour[x] != colour[y] || colour[x] != colour[z]) continue;
        int px = pos[x], py = pos[y], pz = pos[z];
        if ((px < py && py < pz) || (px > py && py > pz)) {
            cout << "{\"status\":\"INVALID\",\"colour\":" << colour[x]
                 << ",\"witness\":[" << x << ',' << y << ',' << z << "],\"positions\":["
                 << px << ',' << py << ',' << pz << "]}\n";
            return 1;
        }
    }
    cout << "{\"status\":\"VALID\",\"n\":" << n << ",\"sizes\":[" << seq[0].size() << ',' << seq[1].size() << "]}\n";
    return 0;
}
