#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

int main(int argc, char** argv) {
    try {
        if (argc != 4) {
            throw std::runtime_error("usage: decode_model <map> <model> <matrix-out>");
        }
        std::ifstream map_in(argv[1]);
        std::ifstream model_in(argv[2]);
        if (!map_in || !model_in) throw std::runtime_error("cannot open input");
        std::string tag;
        int n;
        if (!(map_in >> tag >> n) || tag != "n") throw std::runtime_error("bad map header");
        std::vector<std::tuple<int, int, int>> vars;
        int var, u, v;
        while (map_in >> tag >> var >> u >> v) {
            if (tag != "x") throw std::runtime_error("bad map row");
            vars.emplace_back(var, u, v);
        }
        std::set<int> positive;
        std::string token;
        while (model_in >> token) {
            if (token == "v" || token == "s" || token == "SATISFIABLE" ||
                token == "SAT" || token == "UNKNOWN") continue;
            int lit;
            try {
                std::size_t pos = 0;
                lit = std::stoi(token, &pos);
                if (pos != token.size()) continue;
            } catch (...) {
                continue;
            }
            if (lit > 0) positive.insert(lit);
        }
        std::vector<std::string> a(n, std::string(n, '0'));
        for (const auto& [x, s, t] : vars) {
            if (positive.count(x)) a[s][t] = a[t][s] = '1';
        }
        std::ofstream out(argv[3]);
        if (!out) throw std::runtime_error("cannot create matrix output");
        out << "N " << n << "\n";
        for (const auto& row : a) out << row << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "ERROR: " << e.what() << "\n";
        return 2;
    }
}
