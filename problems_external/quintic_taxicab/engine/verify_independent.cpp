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
    bool positive = false;
    bool fifth_power_equal = false;
    bool cross_disjoint = false;
    bool primitive = false;
    bool valid = false;
    cpp_int left_sum = 0;
    cpp_int right_sum = 0;
    cpp_int common_gcd = 0;
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

cpp_int absolute(cpp_int value) {
    return value < 0 ? -value : value;
}

cpp_int exact_gcd(cpp_int left, cpp_int right) {
    left = absolute(left);
    right = absolute(right);
    while (right != 0) {
        cpp_int remainder = left % right;
        left = right;
        right = remainder;
    }
    return left;
}

cpp_int fifth_power(const cpp_int& value) {
    const cpp_int square = value * value;
    return square * square * value;
}

CheckResult check_candidate(const std::array<cpp_int, 4>& values) {
    CheckResult result;
    result.positive = true;
    for (const cpp_int& value : values) {
        result.positive = result.positive && value > 0;
        result.common_gcd = exact_gcd(result.common_gcd, value);
    }

    result.left_sum = fifth_power(values[0]) + fifth_power(values[1]);
    result.right_sum = fifth_power(values[2]) + fifth_power(values[3]);
    result.fifth_power_equal = result.left_sum == result.right_sum;
    result.cross_disjoint =
        values[0] != values[2] && values[0] != values[3] &&
        values[1] != values[2] && values[1] != values[3];
    result.primitive = result.common_gcd == 1;
    result.valid =
        result.positive && result.fifth_power_equal && result.cross_disjoint;
    return result;
}

void emit_result(const CheckResult& result) {
    std::cout << "{\"valid\":" << (result.valid ? "true" : "false")
              << ",\"code\":\""
              << (result.valid ? "VERIFIED" : "REJECTED") << "\""
              << ",\"checks\":{\"positive\":"
              << (result.positive ? "true" : "false")
              << ",\"fifth_power_equal\":"
              << (result.fifth_power_equal ? "true" : "false")
              << ",\"cross_disjoint\":"
              << (result.cross_disjoint ? "true" : "false") << "}"
              << ",\"primitive\":" << (result.primitive ? "true" : "false")
              << ",\"common_gcd\":\"" << decimal(result.common_gcd) << "\""
              << ",\"left_sum\":\"" << decimal(result.left_sum) << "\""
              << ",\"right_sum\":\"" << decimal(result.right_sum) << "\"}"
              << '\n';
}

int emit_input_error(const std::string& code, int index = -1,
                     std::size_t count = 0) {
    std::cout << "{\"valid\":false,\"code\":\"" << code << "\"";
    if (index >= 0) {
        std::cout << ",\"index\":" << index;
    }
    if (code == "COUNT") {
        std::cout << ",\"count\":" << count;
    }
    std::cout << "}\n";
    return 2;
}

bool read_file_tokens(const std::string& path,
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

int run_self_test() {
    int checks = 0;
    const auto require = [&checks](bool condition, const char* name) {
        ++checks;
        if (!condition) {
            std::cout << "{\"valid\":false,\"code\":\"SELF_TEST_FAILED\","
                      << "\"check\":" << checks << ",\"name\":\"" << name
                      << "\"}\n";
        }
        return condition;
    };

    cpp_int parsed;
    if (!require(parse_decimal("+12345678901234567890", parsed) &&
                     decimal(parsed) == "12345678901234567890",
                 "parse-large-positive")) {
        return 7;
    }
    if (!require(parse_decimal("-42", parsed) && parsed == -42,
                 "parse-negative")) {
        return 7;
    }
    if (!require(!parse_decimal("12x", parsed), "reject-malformed")) {
        return 7;
    }
    if (!require(
            decimal(fifth_power(cpp_int("12345678901234567890"))) ==
                "286797186173370403767041767776920429666954333495933335798264659838306817363852838672048294900000",
            "large-fifth-power")) {
        return 7;
    }
    if (!require(fifth_power(cpp_int(-2)) == -32, "signed-fifth-power")) {
        return 7;
    }
    if (!require(exact_gcd(cpp_int(-84), cpp_int(30)) == 6,
                 "exact-gcd")) {
        return 7;
    }

    const CheckResult trivial = check_candidate({1, 2, 1, 2});
    if (!require(trivial.positive && trivial.fifth_power_equal &&
                     !trivial.cross_disjoint && !trivial.valid,
                 "trivial-equality-rejected")) {
        return 7;
    }

    const CheckResult signed_zero_sum = check_candidate({1, -1, 2, -2});
    if (!require(!signed_zero_sum.positive &&
                     signed_zero_sum.fifth_power_equal &&
                     signed_zero_sum.cross_disjoint &&
                     !signed_zero_sum.valid,
                 "signed-equality-rejected")) {
        return 7;
    }

    const CheckResult unequal = check_candidate({1, 2, 3, 4});
    if (!require(unequal.positive && !unequal.fifth_power_equal &&
                     unequal.cross_disjoint && !unequal.valid,
                 "unequal-rejected")) {
        return 7;
    }

    const CheckResult scaled = check_candidate({2, 4, 2, 4});
    if (!require(!scaled.primitive && scaled.common_gcd == 2,
                 "primitive-diagnostic")) {
        return 7;
    }

    const CheckResult repeated_left = check_candidate({2, 2, 3, 4});
    if (!require(repeated_left.cross_disjoint,
                 "within-side-repetition-permitted")) {
        return 7;
    }

    std::cout << "{\"valid\":true,\"code\":\"SELF_TEST_OK\",\"checks\":"
              << checks << "}\n";
    return 0;
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        return run_self_test();
    }

    std::vector<std::string> tokens;
    if (argc == 3 && std::string(argv[1]) == "--file") {
        if (!read_file_tokens(argv[2], tokens)) {
            return emit_input_error("FILE_IO");
        }
    } else if (argc == 5) {
        for (int index = 1; index < argc; ++index) {
            tokens.emplace_back(argv[index]);
        }
    } else {
        return emit_input_error("USAGE");
    }

    if (tokens.size() != 4) {
        return emit_input_error("COUNT", -1, tokens.size());
    }

    std::array<cpp_int, 4> values;
    for (std::size_t index = 0; index < tokens.size(); ++index) {
        if (!parse_decimal(tokens[index], values[index])) {
            return emit_input_error("PARSE", static_cast<int>(index));
        }
    }

    const CheckResult result = check_candidate(values);
    emit_result(result);
    return result.valid ? 0 : 1;
}
