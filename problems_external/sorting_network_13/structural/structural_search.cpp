#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

struct Pair {
    std::uint8_t lo{};
    std::uint8_t hi{};
    bool operator==(const Pair& other) const { return lo == other.lo && hi == other.hi; }
};

using Network = std::vector<Pair>;
using Clock = std::chrono::steady_clock;

static Network loadNetwork(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("cannot open " + path);
    std::string line;
    int n = -1;
    Network result;
    while (std::getline(in, line)) {
        const auto hash = line.find('#');
        if (hash != std::string::npos) line.resize(hash);
        std::istringstream row(line);
        if (n < 0) {
            char key = 0;
            int candidateN = 0;
            if (row >> key >> candidateN) {
                if (key != 'n' || candidateN != 13) throw std::runtime_error("bad header in " + path);
                n = candidateN;
            }
            continue;
        }
        int lo = -1, hi = -1;
        if (!(row >> lo >> hi)) continue;
        if (!(0 <= lo && lo < hi && hi < 13)) throw std::runtime_error("bad comparator in " + path);
        result.push_back(Pair{static_cast<std::uint8_t>(lo), static_cast<std::uint8_t>(hi)});
    }
    if (n != 13 || result.size() != 45) throw std::runtime_error("expected N13L45 in " + path);
    return result;
}

static bool sortsInput(const Network& network, std::uint16_t input) {
    std::uint16_t state = input;
    for (const Pair pair : network) {
        const bool lowOne = ((state >> pair.lo) & 1U) != 0;
        const bool highZero = ((state >> pair.hi) & 1U) == 0;
        if (lowOne && highZero) {
            state ^= static_cast<std::uint16_t>((1U << pair.lo) | (1U << pair.hi));
        }
    }
    for (int i = 0; i < 12; ++i) {
        if (((state >> i) & 3U) == 1U) return false;
    }
    return true;
}

static std::uint64_t networkHash(const Network& network) {
    std::uint64_t hash = 1469598103934665603ULL;
    for (const Pair pair : network) {
        const std::uint64_t value = static_cast<std::uint64_t>(pair.lo) * 13ULL + pair.hi + 1ULL;
        hash ^= value;
        hash *= 1099511628211ULL;
    }
    return hash;
}

static void writeNetwork(const std::string& path, const Network& network, const std::string& tag) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot write " + path);
    out << "# structural_search exact hit: " << tag << "\n";
    out << "n 13\n";
    for (const Pair pair : network) out << static_cast<int>(pair.lo) << ' ' << static_cast<int>(pair.hi) << '\n';
}

struct SearchState {
    Clock::time_point started;
    Clock::time_point deadline;
    std::string outputPath;
    std::vector<std::uint16_t> witnesses;
    std::unordered_set<std::uint64_t> seen;
    std::unordered_map<std::string, std::uint64_t> phaseTests;
    std::uint64_t tested = 0;
    std::uint64_t duplicates = 0;
    std::uint64_t witnessRejected = 0;
    std::uint64_t fullRejected = 0;
    bool hit = false;
    std::string hitTag;

    bool expired() const { return Clock::now() >= deadline; }

    bool test(const Network& candidate, const std::string& phase, const std::string& tag) {
        if (hit || expired()) return hit;
        if (candidate.size() != 44) throw std::runtime_error("candidate length is not 44");
        const auto hash = networkHash(candidate);
        if (!seen.insert(hash).second) {
            ++duplicates;
            return false;
        }
        ++tested;
        ++phaseTests[phase];
        for (const auto witness : witnesses) {
            if (!sortsInput(candidate, witness)) {
                ++witnessRejected;
                return false;
            }
        }
        for (std::uint16_t input = 0; input < 8192; ++input) {
            if (!sortsInput(candidate, input)) {
                ++fullRejected;
                if (std::find(witnesses.begin(), witnesses.end(), input) == witnesses.end()) {
                    witnesses.push_back(input);
                }
                return false;
            }
        }
        hit = true;
        hitTag = tag;
        writeNetwork(outputPath, candidate, tag);
        return true;
    }
};

static std::vector<Pair> alphabet(int n) {
    std::vector<Pair> result;
    for (int lo = 0; lo < n; ++lo) {
        for (int hi = lo + 1; hi < n; ++hi) {
            result.push_back(Pair{static_cast<std::uint8_t>(lo), static_cast<std::uint8_t>(hi)});
        }
    }
    return result;
}

static Network eraseAt(const Network& network, std::size_t index) {
    Network result;
    result.reserve(network.size() - 1);
    result.insert(result.end(), network.begin(), network.begin() + static_cast<std::ptrdiff_t>(index));
    result.insert(result.end(), network.begin() + static_cast<std::ptrdiff_t>(index + 1), network.end());
    return result;
}

static std::uint64_t localSignature(const Network& word, int channels) {
    std::uint64_t signature = 0;
    const int inputs = 1 << channels;
    for (int input = 0; input < inputs; ++input) {
        int state = input;
        for (const Pair pair : word) {
            const bool lowOne = ((state >> pair.lo) & 1) != 0;
            const bool highZero = ((state >> pair.hi) & 1) == 0;
            if (lowOne && highZero) state ^= (1 << pair.lo) | (1 << pair.hi);
        }
        for (int bit = 0; bit < channels; ++bit) {
            if ((state >> bit) & 1) signature |= 1ULL << (input * channels + bit);
        }
    }
    return signature;
}

struct LocalTables {
    std::array<std::vector<std::unordered_map<std::uint64_t, std::vector<std::uint32_t>>>, 5> bySignature;
    std::array<std::vector<Pair>, 5> alphabets;

    explicit LocalTables(int maxLength) {
        for (int channels = 2; channels <= 4; ++channels) {
            alphabets[channels] = alphabet(channels);
            bySignature[channels].resize(maxLength + 1);
            const std::uint32_t base = static_cast<std::uint32_t>(alphabets[channels].size());
            std::uint32_t total = 1;
            for (int length = 1; length <= maxLength; ++length) {
                total *= base;
                auto& table = bySignature[channels][length];
                for (std::uint32_t code = 0; code < total; ++code) {
                    table[signature(channels, length, code)].push_back(code);
                }
            }
        }
    }

    Network decode(int channels, int length, std::uint32_t code) const {
        Network result(static_cast<std::size_t>(length));
        const std::uint32_t base = static_cast<std::uint32_t>(alphabets[channels].size());
        for (int i = length - 1; i >= 0; --i) {
            result[static_cast<std::size_t>(i)] = alphabets[channels][code % base];
            code /= base;
        }
        return result;
    }

    std::uint64_t signature(int channels, int length, std::uint32_t code) const {
        return localSignature(decode(channels, length, code), channels);
    }
};

static bool scanLocalWindows(const Network& network, const std::string& family,
                             const LocalTables& tables, SearchState& search,
                             std::size_t sameLengthCap, const std::string& phase) {
    for (int length = 2; length <= 7 && !search.expired(); ++length) {
        for (std::size_t start = 0; start + static_cast<std::size_t>(length) <= network.size(); ++start) {
            std::array<bool, 13> used{};
            std::vector<int> channels;
            for (int offset = 0; offset < length; ++offset) {
                const Pair pair = network[start + static_cast<std::size_t>(offset)];
                used[pair.lo] = true;
                used[pair.hi] = true;
            }
            for (int channel = 0; channel < 13; ++channel) if (used[channel]) channels.push_back(channel);
            const int k = static_cast<int>(channels.size());
            if (k < 2 || k > 4) continue;
            std::array<int, 13> localIndex{};
            localIndex.fill(-1);
            for (int i = 0; i < k; ++i) localIndex[channels[static_cast<std::size_t>(i)]] = i;
            Network local;
            local.reserve(static_cast<std::size_t>(length));
            for (int offset = 0; offset < length; ++offset) {
                const Pair pair = network[start + static_cast<std::size_t>(offset)];
                local.push_back(Pair{static_cast<std::uint8_t>(localIndex[pair.lo]),
                                     static_cast<std::uint8_t>(localIndex[pair.hi])});
            }
            const auto signature = localSignature(local, k);

            const auto shorterIt = tables.bySignature[k][length - 1].find(signature);
            if (shorterIt != tables.bySignature[k][length - 1].end()) {
                for (const std::uint32_t code : shorterIt->second) {
                    Network replacement = tables.decode(k, length - 1, code);
                    Network candidate;
                    candidate.reserve(44);
                    candidate.insert(candidate.end(), network.begin(), network.begin() + static_cast<std::ptrdiff_t>(start));
                    for (Pair pair : replacement) {
                        pair.lo = static_cast<std::uint8_t>(channels[pair.lo]);
                        pair.hi = static_cast<std::uint8_t>(channels[pair.hi]);
                        candidate.push_back(pair);
                    }
                    candidate.insert(candidate.end(), network.begin() + static_cast<std::ptrdiff_t>(start + length), network.end());
                    if (search.test(candidate, phase, family + ":shorten-window")) return true;
                }
            }

            const auto sameIt = tables.bySignature[k][length].find(signature);
            if (sameIt == tables.bySignature[k][length].end()) continue;
            std::size_t usedAlternatives = 0;
            for (const std::uint32_t code : sameIt->second) {
                if (usedAlternatives++ >= sameLengthCap || search.expired()) break;
                Network replacement = tables.decode(k, length, code);
                for (Pair& pair : replacement) {
                    pair.lo = static_cast<std::uint8_t>(channels[pair.lo]);
                    pair.hi = static_cast<std::uint8_t>(channels[pair.hi]);
                }
                for (int deleted = 0; deleted < length; ++deleted) {
                    Network candidate;
                    candidate.reserve(44);
                    candidate.insert(candidate.end(), network.begin(), network.begin() + static_cast<std::ptrdiff_t>(start));
                    for (int i = 0; i < length; ++i) if (i != deleted) candidate.push_back(replacement[static_cast<std::size_t>(i)]);
                    candidate.insert(candidate.end(), network.begin() + static_cast<std::ptrdiff_t>(start + length), network.end());
                    if (search.test(candidate, phase, family + ":rewrite-delete-window")) return true;
                }
            }
        }
    }
    return false;
}

static Network randomCommutation(const Network& network, std::mt19937_64& rng) {
    const int count = static_cast<int>(network.size());
    std::vector<std::vector<int>> successors(static_cast<std::size_t>(count));
    std::vector<int> indegree(static_cast<std::size_t>(count), 0);
    std::array<int, 13> last;
    last.fill(-1);
    for (int i = 0; i < count; ++i) {
        std::array<int, 2> predecessors{last[network[static_cast<std::size_t>(i)].lo],
                                        last[network[static_cast<std::size_t>(i)].hi]};
        if (predecessors[0] == predecessors[1]) predecessors[1] = -1;
        for (const int predecessor : predecessors) {
            if (predecessor >= 0) {
                successors[static_cast<std::size_t>(predecessor)].push_back(i);
                ++indegree[static_cast<std::size_t>(i)];
            }
        }
        last[network[static_cast<std::size_t>(i)].lo] = i;
        last[network[static_cast<std::size_t>(i)].hi] = i;
    }
    std::vector<int> available;
    for (int i = 0; i < count; ++i) if (indegree[static_cast<std::size_t>(i)] == 0) available.push_back(i);
    Network result;
    result.reserve(network.size());
    while (!available.empty()) {
        std::uniform_int_distribution<std::size_t> choice(0, available.size() - 1);
        const std::size_t slot = choice(rng);
        const int node = available[slot];
        available[slot] = available.back();
        available.pop_back();
        result.push_back(network[static_cast<std::size_t>(node)]);
        for (const int successor : successors[static_cast<std::size_t>(node)]) {
            if (--indegree[static_cast<std::size_t>(successor)] == 0) available.push_back(successor);
        }
    }
    if (result.size() != network.size()) throw std::runtime_error("commutation DAG cycle");
    return result;
}

static std::vector<std::array<int, 13>> smallSupportPermutations(int maximumSupport) {
    std::vector<std::array<int, 13>> result;
    for (int supportSize = 2; supportSize <= maximumSupport; ++supportSize) {
        std::vector<int> chooseMask(13, 0);
        std::fill(chooseMask.begin(), chooseMask.begin() + supportSize, 1);
        do {
            std::vector<int> support;
            for (int i = 0; i < 13; ++i) if (chooseMask[static_cast<std::size_t>(i)]) support.push_back(i);
            std::vector<int> image = support;
            do {
                bool derangement = true;
                for (int i = 0; i < supportSize; ++i) if (image[static_cast<std::size_t>(i)] == support[static_cast<std::size_t>(i)]) derangement = false;
                if (!derangement) continue;
                std::array<int, 13> permutation{};
                std::iota(permutation.begin(), permutation.end(), 0);
                for (int i = 0; i < supportSize; ++i) permutation[static_cast<std::size_t>(support[static_cast<std::size_t>(i)])] = image[static_cast<std::size_t>(i)];
                result.push_back(permutation);
            } while (std::next_permutation(image.begin(), image.end()));
        } while (std::prev_permutation(chooseMask.begin(), chooseMask.end()));
    }
    return result;
}

static Network permuteChannels(const Network& network, const std::array<int, 13>& permutation) {
    Network result;
    result.reserve(network.size());
    for (const Pair pair : network) {
        int lo = permutation[pair.lo];
        int hi = permutation[pair.hi];
        if (lo > hi) std::swap(lo, hi);
        result.push_back(Pair{static_cast<std::uint8_t>(lo), static_cast<std::uint8_t>(hi)});
    }
    return result;
}

static void printSummary(const SearchState& search, const std::string& status) {
    const double elapsed = std::chrono::duration<double>(Clock::now() - search.started).count();
    std::cout << "{\"status\":\"" << status << "\",\"hit\":" << (search.hit ? "true" : "false")
              << ",\"tested\":" << search.tested << ",\"duplicates\":" << search.duplicates
              << ",\"witness_rejected\":" << search.witnessRejected
              << ",\"full_rejected\":" << search.fullRejected
              << ",\"witnesses\":" << search.witnesses.size()
              << ",\"elapsed_s\":" << elapsed << ",\"phase_tests\":{";
    bool first = true;
    for (const auto& [phase, count] : search.phaseTests) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << '\"' << phase << "\":" << count;
    }
    std::cout << "}}\n";
}

int main(int argc, char** argv) {
    if (argc != 9) {
        std::cerr << "usage: structural_search SECONDS OUT.net family1.net ... family6.net\n";
        return 2;
    }
    const int seconds = std::stoi(argv[1]);
    if (seconds <= 0 || seconds > 1800) throw std::runtime_error("SECONDS must be in 1..1800");
    std::vector<std::string> names{"dobbelaere", "end13", "senso13", "cal131016", "lowavg", "max32"};
    std::vector<Network> networks;
    for (int i = 0; i < 6; ++i) networks.push_back(loadNetwork(argv[i + 3]));
    for (std::size_t family = 0; family < networks.size(); ++family) {
        for (std::uint16_t input = 0; input < 8192; ++input) {
            if (!sortsInput(networks[family], input)) throw std::runtime_error("seed is not a sorter: " + names[family]);
        }
    }

    SearchState search;
    search.started = Clock::now();
    search.deadline = search.started + std::chrono::seconds(seconds);
    search.outputPath = argv[2];
    search.seen.reserve(4'000'000);
    search.witnesses.reserve(4096);

    for (std::size_t family = 0; family < networks.size() && !search.expired(); ++family) {
        for (std::size_t deleted = 0; deleted < 45; ++deleted) {
            if (search.test(eraseAt(networks[family], deleted), "single-delete", names[family] + ":single-delete")) {
                printSummary(search, "HIT");
                return 0;
            }
        }
    }

    LocalTables tables(7);
    for (std::size_t family = 0; family < networks.size() && !search.expired(); ++family) {
        if (scanLocalWindows(networks[family], names[family], tables, search, 1000000, "local-exact")) {
            printSummary(search, "HIT");
            return 0;
        }
    }

    const auto globalAlphabet = alphabet(13);
    constexpr int radius = 8;
    for (std::size_t family = 0; family < networks.size() && !search.expired(); ++family) {
        for (int deleted = 0; deleted < 45 && !search.expired(); ++deleted) {
            Network base = eraseAt(networks[family], static_cast<std::size_t>(deleted));
            const int center = std::min(deleted, 43);
            const int from = std::max(0, center - radius);
            const int to = std::min(43, center + radius);
            for (int position = from; position <= to && !search.expired(); ++position) {
                const Pair original = base[static_cast<std::size_t>(position)];
                for (const Pair replacement : globalAlphabet) {
                    if (replacement == original) continue;
                    Network candidate = base;
                    candidate[static_cast<std::size_t>(position)] = replacement;
                    if (search.test(candidate, "delete-replace-r8", names[family] + ":delete-replace-r8")) {
                        printSummary(search, "HIT");
                        return 0;
                    }
                }
            }
            for (int first = from; first <= to && !search.expired(); ++first) {
                for (int second = first + 1; second <= to; ++second) {
                    Network candidate = base;
                    std::swap(candidate[static_cast<std::size_t>(first)], candidate[static_cast<std::size_t>(second)]);
                    if (search.test(candidate, "delete-local-swap-r8", names[family] + ":delete-local-swap-r8")) {
                        printSummary(search, "HIT");
                        return 0;
                    }
                }
            }
        }
    }

    for (std::size_t family = 0; family < networks.size() && !search.expired(); ++family) {
        for (int deleted = 0; deleted < 45 && !search.expired(); ++deleted) {
            Network base = eraseAt(networks[family], static_cast<std::size_t>(deleted));
            for (std::size_t position = 0; position < base.size() && !search.expired(); ++position) {
                const Pair original = base[position];
                for (const Pair replacement : globalAlphabet) {
                    if (replacement == original) continue;
                    Network candidate = base;
                    candidate[position] = replacement;
                    if (search.test(candidate, "delete-replace-global", names[family] + ":delete-replace-global")) {
                        printSummary(search, "HIT");
                        return 0;
                    }
                }
            }
        }
    }

    std::unordered_map<int, std::vector<Pair>> halfAlternatives;
    for (const Pair original : globalAlphabet) {
        auto& alternatives = halfAlternatives[static_cast<int>(original.lo) * 13 + original.hi];
        for (const Pair replacement : globalAlphabet) {
            if (replacement == original) continue;
            if (replacement.lo == original.lo || replacement.lo == original.hi ||
                replacement.hi == original.lo || replacement.hi == original.hi) {
                alternatives.push_back(replacement);
            }
        }
    }

    for (std::size_t family = 0; family < networks.size() && !search.expired(); ++family) {
        for (int deleted = 0; deleted < 45 && !search.expired(); ++deleted) {
            Network base = eraseAt(networks[family], static_cast<std::size_t>(deleted));
            const int center = std::min(deleted, 43);
            const int from = std::max(0, center - 6);
            const int to = std::min(43, center + 6);
            for (int first = from; first <= to && !search.expired(); ++first) {
                for (int second = first + 1; second <= to && !search.expired(); ++second) {
                    const Pair originalFirst = base[static_cast<std::size_t>(first)];
                    const Pair originalSecond = base[static_cast<std::size_t>(second)];
                    const auto& firstAlternatives = halfAlternatives.at(static_cast<int>(originalFirst.lo) * 13 + originalFirst.hi);
                    const auto& secondAlternatives = halfAlternatives.at(static_cast<int>(originalSecond.lo) * 13 + originalSecond.hi);
                    for (const Pair firstReplacement : firstAlternatives) {
                        for (const Pair secondReplacement : secondAlternatives) {
                            Network candidate = base;
                            candidate[static_cast<std::size_t>(first)] = firstReplacement;
                            candidate[static_cast<std::size_t>(second)] = secondReplacement;
                            if (search.test(candidate, "delete-double-half-r6", names[family] + ":delete-double-half-r6")) {
                                printSummary(search, "HIT");
                                return 0;
                            }
                        }
                    }
                }
            }
        }
    }

    for (std::size_t family = 0; family < networks.size() && !search.expired(); ++family) {
        for (int deleted = 0; deleted < 45 && !search.expired(); ++deleted) {
            Network base = eraseAt(networks[family], static_cast<std::size_t>(deleted));
            const int center = std::min(deleted, 43);
            const int from = std::max(0, center - 2);
            const int to = std::min(43, center + 2);
            for (int first = from; first <= to && !search.expired(); ++first) {
                for (int second = first + 1; second <= to && !search.expired(); ++second) {
                    const Pair originalFirst = base[static_cast<std::size_t>(first)];
                    const Pair originalSecond = base[static_cast<std::size_t>(second)];
                    for (const Pair firstReplacement : globalAlphabet) {
                        if (firstReplacement == originalFirst) continue;
                        for (const Pair secondReplacement : globalAlphabet) {
                            if (secondReplacement == originalSecond) continue;
                            Network candidate = base;
                            candidate[static_cast<std::size_t>(first)] = firstReplacement;
                            candidate[static_cast<std::size_t>(second)] = secondReplacement;
                            if (search.test(candidate, "delete-double-replace-r2", names[family] + ":delete-double-replace-r2")) {
                                printSummary(search, "HIT");
                                return 0;
                            }
                        }
                    }
                }
            }
        }
    }

    const auto permutations = smallSupportPermutations(5);
    for (std::size_t family = 0; family < networks.size() && !search.expired(); ++family) {
        for (const auto& permutation : permutations) {
            Network transformed = permuteChannels(networks[family], permutation);
            for (std::size_t deleted = 0; deleted < 45; ++deleted) {
                if (search.test(eraseAt(transformed, deleted), "perm-support-2to5", names[family] + ":perm-delete")) {
                    printSummary(search, "HIT");
                    return 0;
                }
                if (search.expired()) break;
            }
            if (search.expired()) break;
        }
    }

    std::mt19937_64 permutationRng(0x5045524D31333434ULL);
    std::array<int, 13> randomPermutation{};
    std::iota(randomPermutation.begin(), randomPermutation.end(), 0);
    for (int round = 0; round < 100000 && !search.expired(); ++round) {
        std::shuffle(randomPermutation.begin(), randomPermutation.end(), permutationRng);
        for (std::size_t family = 0; family < networks.size() && !search.expired(); ++family) {
            Network transformed = permuteChannels(networks[family], randomPermutation);
            for (std::size_t deleted = 0; deleted < 45 && !search.expired(); ++deleted) {
                if (search.test(eraseAt(transformed, deleted), "perm-random-global", names[family] + ":perm-random-delete")) {
                    printSummary(search, "HIT");
                    return 0;
                }
            }
        }
    }

    std::mt19937_64 rng(0x534E31333434ULL);
    for (int round = 0; round < 50000 && !search.expired(); ++round) {
        for (std::size_t family = 0; family < networks.size() && !search.expired(); ++family) {
            Network variant = randomCommutation(networks[family], rng);
            if (scanLocalWindows(variant, names[family], tables, search, 64, "commute-local-exact")) {
                printSummary(search, "HIT");
                return 0;
            }
        }
    }

    printSummary(search, search.expired() ? "NO_HIT_TIME_LIMIT" : "NO_HIT_EXHAUSTED");
    return 1;
}
