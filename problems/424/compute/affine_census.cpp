#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    if (argc < 4) {
        std::cerr << "usage: affine_census LIMIT OUTPUT K...\n";
        return 2;
    }
    const int limit = std::stoi(argv[1]);
    const std::string output = argv[2];
    std::vector<int> multipliers;
    for (int i = 3; i < argc; ++i) multipliers.push_back(std::stoi(argv[i]));
    std::vector<uint8_t> reached(limit + 1, 0);
    for (int seed : multipliers) if (seed <= limit) reached[seed] = 1;
    int64_t count = 0;
    int previous = 0;
    int maximum_gap = 0;
    int gap_left = 0;
    int gap_right = 0;
    std::vector<std::pair<int,int64_t>> checkpoints;
    int64_t next_checkpoint = 10;
    for (int value = 1; value <= limit; ++value) {
        if (!reached[value]) {
            for (int k : multipliers) {
                if ((value + 1) % k != 0) continue;
                const int parent = (value + 1) / k;
                if (parent == k || parent >= value) continue;
                if (reached[parent]) {
                    reached[value] = 1;
                    break;
                }
            }
        }
        if (reached[value]) {
            ++count;
            if (previous && value - previous > maximum_gap) {
                maximum_gap = value - previous;
                gap_left = previous;
                gap_right = value;
            }
            previous = value;
        }
        if (value == next_checkpoint) {
            checkpoints.emplace_back(value, count);
            next_checkpoint *= 10;
        }
    }
    if (checkpoints.empty() || checkpoints.back().first != limit)
        checkpoints.emplace_back(limit, count);
    std::ofstream out(output);
    out << "{\n  \"limit\": " << limit << ",\n  \"multipliers\": [";
    for (std::size_t i=0;i<multipliers.size();++i) {
        if (i) out << ", ";
        out << multipliers[i];
    }
    out << "],\n  \"count\": " << count << ",\n";
    out << "  \"maximum_gap\": " << maximum_gap << ",\n";
    out << "  \"maximum_gap_endpoints\": [" << gap_left << ", " << gap_right << "],\n";
    out << "  \"checkpoints\": [\n";
    for (std::size_t i=0;i<checkpoints.size();++i) {
        out << "    [" << checkpoints[i].first << ", " << checkpoints[i].second << "]";
        out << (i+1==checkpoints.size()?"\n":",\n");
    }
    out << "  ]\n}\n";
    std::cout << "count=" << count << " max_gap=" << maximum_gap << "\n";
}
