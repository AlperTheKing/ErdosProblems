#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <mutex>
#include <set>
#include <stdexcept>
#include <string>
#include <thread>
#include <unordered_set>
#include <utility>
#include <vector>

using u64 = std::uint64_t;
using u128 = unsigned __int128;

struct Record {
    u64 id = 0;
    int order = 0;
    std::string label;
    std::vector<u64> polynomial;
};

static std::string decimal(u128 value) {
    if (value == 0) return "0";
    std::string out;
    while (value != 0) {
        out.push_back(static_cast<char>('0' + value % 10));
        value /= 10;
    }
    std::reverse(out.begin(), out.end());
    return out;
}

static std::size_t value_position(const std::string& line, const std::string& key) {
    const std::string token = "\"" + key + "\":";
    const std::size_t pos = line.find(token);
    if (pos == std::string::npos) throw std::runtime_error("missing JSON key: " + key);
    return pos + token.size();
}

static u64 parse_u64(const std::string& line, std::size_t& pos) {
    if (pos >= line.size() || !std::isdigit(static_cast<unsigned char>(line[pos]))) {
        throw std::runtime_error("expected unsigned decimal integer");
    }
    u128 value = 0;
    while (pos < line.size() && std::isdigit(static_cast<unsigned char>(line[pos]))) {
        value = value * 10 + static_cast<unsigned>(line[pos] - '0');
        if (value > static_cast<u128>(UINT64_MAX)) {
            throw std::overflow_error("JSON integer exceeds uint64");
        }
        ++pos;
    }
    return static_cast<u64>(value);
}

static std::string parse_string(const std::string& line, std::size_t& pos) {
    if (pos >= line.size() || line[pos] != '"') throw std::runtime_error("expected JSON string");
    ++pos;
    std::string out;
    while (pos < line.size()) {
        const char ch = line[pos++];
        if (ch == '"') return out;
        if (ch == '\\') {
            if (pos >= line.size()) throw std::runtime_error("truncated JSON escape");
            const char escaped = line[pos++];
            if (escaped == '"' || escaped == '\\' || escaped == '/') out.push_back(escaped);
            else throw std::runtime_error("unsupported JSON escape in label");
        } else {
            out.push_back(ch);
        }
    }
    throw std::runtime_error("unterminated JSON string");
}

static std::vector<u64> parse_polynomial(const std::string& line, std::size_t& pos) {
    if (pos >= line.size() || line[pos] != '[') throw std::runtime_error("expected coefficient array");
    ++pos;
    std::vector<u64> coefficients;
    while (true) {
        if (pos >= line.size()) throw std::runtime_error("unterminated coefficient array");
        if (line[pos] == ']') {
            ++pos;
            break;
        }
        u64 value = parse_u64(line, pos);
        if (value == 0) throw std::runtime_error("nonpositive coefficient");
        coefficients.push_back(value);
        if (pos >= line.size()) throw std::runtime_error("unterminated coefficient array");
        if (line[pos] == ',') {
            ++pos;
            continue;
        }
        if (line[pos] == ']') {
            ++pos;
            break;
        }
        throw std::runtime_error("bad coefficient separator");
    }
    if (coefficients.empty()) throw std::runtime_error("empty coefficient array");
    return coefficients;
}

static Record parse_record(const std::string& line) {
    Record out;
    std::size_t pos = value_position(line, "id");
    out.id = parse_u64(line, pos);
    pos = value_position(line, "label");
    out.label = parse_string(line, pos);
    pos = value_position(line, "order");
    const u64 order = parse_u64(line, pos);
    if (order > static_cast<u64>(INT32_MAX)) throw std::overflow_error("order exceeds int");
    out.order = static_cast<int>(order);
    pos = value_position(line, "independence_polynomial");
    out.polynomial = parse_polynomial(line, pos);
    return out;
}

static bool unimodal_sequence(const std::vector<u64>& p) {
    bool falling = false;
    for (std::size_t k = 0; k + 1 < p.size(); ++k) {
        if (p[k] > p[k + 1]) falling = true;
        else if (falling && p[k] < p[k + 1]) return false;
    }
    return true;
}

static bool log_concave(const std::vector<u64>& p) {
    for (std::size_t k = 1; k + 1 < p.size(); ++k) {
        if (static_cast<u128>(p[k]) * p[k] <
            static_cast<u128>(p[k - 1]) * p[k + 1]) return false;
    }
    return true;
}

static bool product_is_unimodal(const std::vector<u64>& a,
                                const std::vector<u64>& b,
                                std::array<u128, 128>& product,
                                std::size_t& length,
                                std::size_t& valley_transition) {
    length = a.size() + b.size() - 1;
    if (length > product.size()) throw std::overflow_error("product degree exceeds fixed audit buffer");
    std::fill(product.begin(), product.begin() + static_cast<std::ptrdiff_t>(length), u128{0});
    for (std::size_t i = 0; i < a.size(); ++i) {
        for (std::size_t j = 0; j < b.size(); ++j) {
            product[i + j] += static_cast<u128>(a[i]) * b[j];
        }
    }
    bool falling = false;
    for (std::size_t k = 0; k + 1 < length; ++k) {
        if (product[k] > product[k + 1]) falling = true;
        else if (falling && product[k] < product[k + 1]) {
            valley_transition = k;
            return false;
        }
    }
    return true;
}

static void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error("self-test failed: " + message);
}

static void self_test() {
    std::array<u128, 128> product{};
    std::size_t length = 0;
    std::size_t valley = 0;
    const std::vector<u64> forced_a{1, 1, 2};
    const std::vector<u64> forced_b{1, 1, 3};
    require(unimodal_sequence(forced_a) && unimodal_sequence(forced_b),
            "forced-valley factors must each be unimodal");
    require(!product_is_unimodal(forced_a, forced_b, product, length, valley),
            "forced-valley convolution was not rejected");
    const std::array<u64, 5> expected_forced{1, 2, 6, 5, 6};
    require(length == expected_forced.size(), "forced-valley product length");
    for (std::size_t i = 0; i < length; ++i) {
        require(product[i] == expected_forced[i], "forced-valley coefficient mismatch");
    }
    require(valley == 3, "forced-valley transition index");

    const std::vector<u64> control_a{1, 2, 1};
    const std::vector<u64> control_b{1, 3, 1};
    require(product_is_unimodal(control_a, control_b, product, length, valley),
            "unimodal control convolution rejected");
    require(decimal(~u128{0}) == "340282366920938463463374607431768211455",
            "uint128 decimal conversion");

    const std::string sample =
        "{\"id\":7,\"label\":\"sample\",\"order\":3,"
        "\"independence_polynomial\":[1,3,1]}";
    const Record parsed = parse_record(sample);
    require(parsed.id == 7 && parsed.label == "sample" && parsed.order == 3,
            "JSON scalar parsing");
    require(parsed.polynomial == std::vector<u64>({1, 3, 1}),
            "JSON polynomial parsing");
}

static std::vector<Record> load_and_validate(const std::string& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("cannot open frozen JSONL");
    std::vector<Record> records;
    std::unordered_set<std::string> labels;
    std::set<std::vector<u64>> polynomials;
    std::string line;
    std::size_t line_number = 0;
    while (std::getline(input, line)) {
        ++line_number;
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty()) throw std::runtime_error("blank JSONL line");
        Record record = parse_record(line);
        if (record.id != records.size()) throw std::runtime_error("nonsequential record id");
        if (record.label.empty() || !labels.insert(record.label).second) {
            throw std::runtime_error("empty or duplicate label");
        }
        if (!polynomials.insert(record.polynomial).second) {
            throw std::runtime_error("duplicate coefficient vector");
        }
        if (record.order < 1 || record.polynomial.size() < 2 ||
            record.polynomial[0] != 1 ||
            record.polynomial[1] != static_cast<u64>(record.order)) {
            throw std::runtime_error("invalid independence-polynomial prefix");
        }
        if (!unimodal_sequence(record.polynomial)) {
            throw std::runtime_error("catalog contains nonunimodal component");
        }
        if (log_concave(record.polynomial)) {
            throw std::runtime_error("catalog contains log-concave component");
        }
        records.push_back(std::move(record));
    }
    if (!input.eof()) throw std::runtime_error("JSONL read failure");
    if (line_number != 4499 || records.size() != 4499 ||
        labels.size() != 4499 || polynomials.size() != 4499) {
        throw std::runtime_error("frozen catalog cardinality mismatch");
    }
    return records;
}

struct Hit {
    std::size_t i = 0;
    std::size_t j = 0;
    std::size_t valley_transition = 0;
    std::vector<u128> product;
};

int main(int argc, char** argv) {
    try {
        std::string input_path;
        int threads = 1;
        bool self_test_only = false;
        for (int i = 1; i < argc; ++i) {
            const std::string arg = argv[i];
            if (arg == "--input" && i + 1 < argc) input_path = argv[++i];
            else if (arg == "--threads" && i + 1 < argc) threads = std::stoi(argv[++i]);
            else if (arg == "--self-test") self_test_only = true;
            else throw std::runtime_error("unknown or incomplete argument: " + arg);
        }
        if (threads < 1 || threads > 64) throw std::runtime_error("threads must be in 1..64");
        self_test();
        std::cout << "{\"phase\":\"self_test\",\"status\":\"PASS\","
                     "\"forced_product\":[1,2,6,5,6],\"valley_transition\":3}\n";
        if (self_test_only) return 0;
        if (input_path.empty()) throw std::runtime_error("--input is required");

        const auto parse_start = std::chrono::steady_clock::now();
        const std::vector<Record> records = load_and_validate(input_path);
        const auto parse_end = std::chrono::steady_clock::now();
        std::size_t max_degree = 0;
        u64 max_coefficient = 0;
        for (const Record& record : records) {
            max_degree = std::max(max_degree, record.polynomial.size() - 1);
            for (u64 value : record.polynomial) max_coefficient = std::max(max_coefficient, value);
        }
        std::cout << "{\"phase\":\"parse\",\"status\":\"PASS\",\"records\":"
                  << records.size() << ",\"unique_labels\":" << records.size()
                  << ",\"unique_polynomials\":" << records.size()
                  << ",\"max_degree\":" << max_degree
                  << ",\"max_coefficient\":" << max_coefficient
                  << ",\"seconds\":"
                  << std::chrono::duration<double>(parse_end - parse_start).count()
                  << "}\n";

        const std::size_t n = records.size();
        const u64 expected = static_cast<u64>(n) * (n + 1) / 2;
        std::atomic<std::size_t> next_i{0};
        std::atomic<u64> tested{0};
        std::atomic<bool> stop{false};
        std::mutex hit_mutex;
        Hit hit;
        const auto scan_start = std::chrono::steady_clock::now();
        auto worker = [&]() {
            std::array<u128, 128> product{};
            u64 local_tested = 0;
            while (!stop.load(std::memory_order_relaxed)) {
                const std::size_t i = next_i.fetch_add(1, std::memory_order_relaxed);
                if (i >= n) break;
                for (std::size_t j = i; j < n; ++j) {
                    std::size_t length = 0;
                    std::size_t valley_transition = 0;
                    const bool unimodal =
                        product_is_unimodal(records[i].polynomial, records[j].polynomial,
                                            product, length, valley_transition);
                    ++local_tested;
                    if (!unimodal) {
                        bool expected_stop = false;
                        if (stop.compare_exchange_strong(expected_stop, true)) {
                            std::lock_guard<std::mutex> lock(hit_mutex);
                            hit.i = i;
                            hit.j = j;
                            hit.valley_transition = valley_transition;
                            hit.product.assign(product.begin(),
                                               product.begin() + static_cast<std::ptrdiff_t>(length));
                        }
                        break;
                    }
                    if (stop.load(std::memory_order_relaxed)) break;
                }
            }
            tested.fetch_add(local_tested, std::memory_order_relaxed);
        };
        std::vector<std::thread> pool;
        pool.reserve(static_cast<std::size_t>(threads));
        for (int k = 0; k < threads; ++k) pool.emplace_back(worker);
        for (std::thread& thread : pool) thread.join();
        const auto scan_end = std::chrono::steady_clock::now();

        if (stop.load()) {
            std::cout << "{\"phase\":\"scan\",\"status\":\"RAW_HIT\",\"i\":" << hit.i
                      << ",\"j\":" << hit.j
                      << ",\"label_i\":\"" << records[hit.i].label
                      << "\",\"label_j\":\"" << records[hit.j].label
                      << "\",\"valley_transition\":" << hit.valley_transition
                      << ",\"product\":[";
            for (std::size_t k = 0; k < hit.product.size(); ++k) {
                if (k != 0) std::cout << ',';
                std::cout << decimal(hit.product[k]);
            }
            std::cout << "],\"tested\":" << tested.load()
                      << ",\"seconds\":"
                      << std::chrono::duration<double>(scan_end - scan_start).count()
                      << "}\n";
            return 10;
        }

        const u64 actual = tested.load();
        std::cout << "{\"phase\":\"scan\",\"status\":\"NO_HIT\",\"tested\":" << actual
                  << ",\"expected\":" << expected << ",\"threads\":" << threads
                  << ",\"seconds\":"
                  << std::chrono::duration<double>(scan_end - scan_start).count()
                  << "}\n";
        return actual == expected && expected == 10122750 ? 0 : 4;
    } catch (const std::exception& error) {
        std::cerr << "FAILED: " << error.what() << "\n";
        return 2;
    }
}
