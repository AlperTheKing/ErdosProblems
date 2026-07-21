#include <boost/multiprecision/cpp_int.hpp>

#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using boost::multiprecision::cpp_int;

namespace {

struct CheckResult {
    bool valid = false;
    std::string code;
    std::size_t count = 0;
    int index = -1;
    int other_index = -1;
    int line = -1;
    cpp_int expected_sum = 0;
    cpp_int actual_sum = 0;
    std::vector<cpp_int> roots;
};

std::string decimal(const cpp_int& value) {
    std::ostringstream out;
    out << value;
    return out.str();
}

bool parse_decimal(const std::string& token, cpp_int& value) {
    if (token.empty()) {
        return false;
    }

    std::size_t position = 0;
    bool negative = false;
    if (token[position] == '+' || token[position] == '-') {
        negative = token[position] == '-';
        ++position;
    }
    if (position == token.size()) {
        return false;
    }

    cpp_int parsed = 0;
    for (; position < token.size(); ++position) {
        const char ch = token[position];
        if (ch < '0' || ch > '9') {
            return false;
        }
        parsed *= 10;
        parsed += static_cast<unsigned int>(ch - '0');
    }

    value = negative ? -parsed : parsed;
    return true;
}

cpp_int integer_square_root(const cpp_int& value) {
    if (value <= 0) {
        return 0;
    }

    const unsigned int bit_count =
        static_cast<unsigned int>(boost::multiprecision::msb(value)) + 1U;
    cpp_int estimate = cpp_int(1) << ((bit_count + 1U) / 2U);

    for (;;) {
        const cpp_int next = (estimate + value / estimate) >> 1;
        if (next >= estimate) {
            break;
        }
        estimate = next;
    }

    while (estimate * estimate > value) {
        --estimate;
    }
    while ((estimate + 1) * (estimate + 1) <= value) {
        ++estimate;
    }
    return estimate;
}

bool exact_square_root(const cpp_int& value, cpp_int& root) {
    if (value < 0) {
        return false;
    }
    root = integer_square_root(value);
    return root * root == value;
}

bool all_positive(const std::vector<cpp_int>& entries, int& bad_index) {
    for (std::size_t i = 0; i < entries.size(); ++i) {
        if (entries[i] <= 0) {
            bad_index = static_cast<int>(i);
            return false;
        }
    }
    return true;
}

bool all_exact_squares(const std::vector<cpp_int>& entries,
                       std::vector<cpp_int>& roots,
                       int& bad_index) {
    roots.clear();
    roots.reserve(entries.size());
    for (std::size_t i = 0; i < entries.size(); ++i) {
        cpp_int root;
        if (!exact_square_root(entries[i], root)) {
            bad_index = static_cast<int>(i);
            roots.clear();
            return false;
        }
        roots.push_back(root);
    }
    return true;
}

bool all_distinct(const std::vector<cpp_int>& entries,
                  int& first_index,
                  int& second_index) {
    for (std::size_t i = 0; i < entries.size(); ++i) {
        for (std::size_t j = i + 1; j < entries.size(); ++j) {
            if (entries[i] == entries[j]) {
                first_index = static_cast<int>(i);
                second_index = static_cast<int>(j);
                return false;
            }
        }
    }
    return true;
}

bool eight_sums_equal(const std::vector<cpp_int>& entries,
                      cpp_int& expected,
                      cpp_int& actual,
                      int& bad_line) {
    static constexpr std::array<std::array<int, 3>, 8> lines = {{
        {{0, 1, 2}},
        {{3, 4, 5}},
        {{6, 7, 8}},
        {{0, 3, 6}},
        {{1, 4, 7}},
        {{2, 5, 8}},
        {{0, 4, 8}},
        {{2, 4, 6}},
    }};

    const auto line_sum = [&entries](const std::array<int, 3>& line) {
        return entries[static_cast<std::size_t>(line[0])] +
               entries[static_cast<std::size_t>(line[1])] +
               entries[static_cast<std::size_t>(line[2])];
    };

    expected = line_sum(lines[0]);
    for (std::size_t i = 1; i < lines.size(); ++i) {
        actual = line_sum(lines[i]);
        if (actual != expected) {
            bad_line = static_cast<int>(i);
            return false;
        }
    }
    actual = expected;
    return true;
}

CheckResult check_candidate(const std::vector<cpp_int>& entries) {
    CheckResult result;
    result.count = entries.size();

    if (entries.size() != 9) {
        result.code = "COUNT";
        return result;
    }
    if (!all_positive(entries, result.index)) {
        result.code = "NONPOSITIVE";
        return result;
    }
    if (!all_exact_squares(entries, result.roots, result.index)) {
        result.code = "NOT_SQUARE";
        return result;
    }
    if (!all_distinct(entries, result.index, result.other_index)) {
        result.code = "DUPLICATE";
        return result;
    }
    if (!eight_sums_equal(entries,
                          result.expected_sum,
                          result.actual_sum,
                          result.line)) {
        result.code = "SUM_MISMATCH";
        return result;
    }

    result.valid = true;
    result.code = "OK";
    return result;
}

int exit_code_for(const std::string& code) {
    if (code == "OK") {
        return 0;
    }
    if (code == "COUNT" || code == "PARSE" || code == "FILE_IO" ||
        code == "USAGE") {
        return 2;
    }
    if (code == "NONPOSITIVE") {
        return 3;
    }
    if (code == "NOT_SQUARE") {
        return 4;
    }
    if (code == "DUPLICATE") {
        return 5;
    }
    if (code == "SUM_MISMATCH") {
        return 6;
    }
    return 7;
}

void emit_check_result(const CheckResult& result) {
    std::cout << "{\"valid\":" << (result.valid ? "true" : "false")
              << ",\"code\":\"" << result.code << "\"";

    if (result.code == "COUNT") {
        std::cout << ",\"count\":" << result.count;
    } else if (result.code == "NONPOSITIVE" ||
               result.code == "NOT_SQUARE") {
        std::cout << ",\"index\":" << result.index;
    } else if (result.code == "DUPLICATE") {
        std::cout << ",\"index\":" << result.index
                  << ",\"other_index\":" << result.other_index;
    } else if (result.code == "SUM_MISMATCH") {
        std::cout << ",\"line\":" << result.line
                  << ",\"expected\":\"" << decimal(result.expected_sum)
                  << "\",\"actual\":\"" << decimal(result.actual_sum) << "\"";
    } else if (result.valid) {
        std::cout << ",\"magic_sum\":\"" << decimal(result.expected_sum)
                  << "\",\"roots\":[";
        for (std::size_t i = 0; i < result.roots.size(); ++i) {
            if (i != 0) {
                std::cout << ',';
            }
            std::cout << '"' << decimal(result.roots[i]) << '"';
        }
        std::cout << ']';
    }
    std::cout << "}\n";
}

bool parse_tokens(const std::vector<std::string>& tokens,
                  std::vector<cpp_int>& entries,
                  int& bad_index) {
    entries.clear();
    entries.reserve(tokens.size());
    for (std::size_t i = 0; i < tokens.size(); ++i) {
        cpp_int value;
        if (!parse_decimal(tokens[i], value)) {
            bad_index = static_cast<int>(i);
            entries.clear();
            return false;
        }
        entries.push_back(value);
    }
    return true;
}

bool read_tokens(const std::string& path,
                 std::vector<std::string>& tokens) {
    std::ifstream input(path);
    if (!input) {
        return false;
    }

    tokens.clear();
    std::string token;
    while (input >> token) {
        tokens.push_back(token);
    }
    return !input.bad();
}

bool expect_code(const std::vector<cpp_int>& entries,
                 const std::string& expected_code) {
    return check_candidate(entries).code == expected_code;
}

int run_self_test() {
    int checks = 0;
    const auto require = [&checks](bool condition) {
        ++checks;
        return condition;
    };

    cpp_int parsed;
    if (!require(parse_decimal("+12345678901234567890", parsed) &&
                 decimal(parsed) == "12345678901234567890")) {
        std::cout << "{\"valid\":false,\"code\":\"SELF_TEST_FAILED\","
                     "\"check\":"
                  << checks << "}\n";
        return 7;
    }
    if (!require(!parse_decimal("12x", parsed))) {
        std::cout << "{\"valid\":false,\"code\":\"SELF_TEST_FAILED\","
                     "\"check\":"
                  << checks << "}\n";
        return 7;
    }

    const cpp_int large_root("123456789012345678901234567890");
    const cpp_int large_square = large_root * large_root;
    cpp_int recovered;
    if (!require(exact_square_root(large_square, recovered) &&
                 recovered == large_root)) {
        std::cout << "{\"valid\":false,\"code\":\"SELF_TEST_FAILED\","
                     "\"check\":"
                  << checks << "}\n";
        return 7;
    }
    if (!require(!exact_square_root(large_square + 1, recovered))) {
        std::cout << "{\"valid\":false,\"code\":\"SELF_TEST_FAILED\","
                     "\"check\":"
                  << checks << "}\n";
        return 7;
    }

    const std::vector<cpp_int> square_domain = {
        1, 4, 9, 16, 25, 36, 49, 64, 81};
    int first = -1;
    int second = -1;
    if (!require(all_positive(square_domain, first) &&
                 all_distinct(square_domain, first, second))) {
        std::cout << "{\"valid\":false,\"code\":\"SELF_TEST_FAILED\","
                     "\"check\":"
                  << checks << "}\n";
        return 7;
    }
    std::vector<cpp_int> roots;
    if (!require(all_exact_squares(square_domain, roots, first) &&
                 roots.size() == 9 && roots[8] == 9)) {
        std::cout << "{\"valid\":false,\"code\":\"SELF_TEST_FAILED\","
                     "\"check\":"
                  << checks << "}\n";
        return 7;
    }

    const std::vector<cpp_int> magic_structure = {
        8, 1, 6, 3, 5, 7, 4, 9, 2};
    cpp_int expected;
    cpp_int actual;
    int line = -1;
    if (!require(eight_sums_equal(magic_structure, expected, actual, line) &&
                 expected == 15)) {
        std::cout << "{\"valid\":false,\"code\":\"SELF_TEST_FAILED\","
                     "\"check\":"
                  << checks << "}\n";
        return 7;
    }

    if (!require(expect_code(std::vector<cpp_int>(8, cpp_int(1)), "COUNT")) ||
        !require(expect_code({0, 1, 4, 9, 16, 25, 36, 49, 64},
                             "NONPOSITIVE")) ||
        !require(expect_code(magic_structure, "NOT_SQUARE")) ||
        !require(expect_code(std::vector<cpp_int>(9, cpp_int(1)),
                             "DUPLICATE")) ||
        !require(expect_code(square_domain, "SUM_MISMATCH"))) {
        std::cout << "{\"valid\":false,\"code\":\"SELF_TEST_FAILED\","
                     "\"check\":"
                  << checks << "}\n";
        return 7;
    }

    std::cout << "{\"valid\":true,\"code\":\"SELF_TEST_OK\",\"checks\":"
              << checks << "}\n";
    return 0;
}

int emit_simple_failure(const std::string& code, int index = -1) {
    std::cout << "{\"valid\":false,\"code\":\"" << code << "\"";
    if (index >= 0) {
        std::cout << ",\"index\":" << index;
    }
    std::cout << "}\n";
    return exit_code_for(code);
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        return run_self_test();
    }

    std::vector<std::string> tokens;
    if (argc == 3 && std::string(argv[1]) == "--file") {
        if (!read_tokens(argv[2], tokens)) {
            return emit_simple_failure("FILE_IO");
        }
    } else if (argc == 2) {
        if (!read_tokens(argv[1], tokens)) {
            return emit_simple_failure("FILE_IO");
        }
    } else if (argc == 10) {
        for (int i = 1; i < argc; ++i) {
            tokens.emplace_back(argv[i]);
        }
    } else {
        return emit_simple_failure("USAGE");
    }

    if (tokens.size() != 9) {
        CheckResult result;
        result.code = "COUNT";
        result.count = tokens.size();
        emit_check_result(result);
        return exit_code_for(result.code);
    }

    std::vector<cpp_int> entries;
    int bad_index = -1;
    if (!parse_tokens(tokens, entries, bad_index)) {
        return emit_simple_failure("PARSE", bad_index);
    }

    const CheckResult result = check_candidate(entries);
    emit_check_result(result);
    return exit_code_for(result.code);
}
