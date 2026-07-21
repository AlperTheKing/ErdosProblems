#include <algorithm>
#include <bit>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {

constexpr std::size_t kMaxVertices = 16384;
constexpr std::size_t kMaxInputBytes = 64U * 1024U * 1024U;

struct Certificate {
    std::size_t n = 0;
    std::vector<std::vector<std::size_t>> out_neighbors;
};

struct VertexLedger {
    std::size_t vertex = 0;
    std::vector<std::size_t> n1;
    std::size_t d1 = 0;
    std::vector<std::size_t> n2_new;
    std::size_t d2 = 0;
    bool strict = false;
};

class ParseError final : public std::runtime_error {
  public:
    using std::runtime_error::runtime_error;
};

class JsonParser final {
  public:
    explicit JsonParser(std::string_view input) : input_(input) {}

    Certificate parse_certificate() {
        Certificate certificate;
        bool have_n = false;
        bool have_out_neighbors = false;

        skip_ws();
        expect('{', "expected top-level JSON object");
        skip_ws();
        if (consume('}')) {
            fail("top-level object must contain n and out_neighbors");
        }

        while (true) {
            const std::string key = parse_plain_string();
            skip_ws();
            expect(':', "expected ':' after object key");
            skip_ws();

            if (key == "n") {
                if (have_n) {
                    fail("duplicate top-level key 'n'");
                }
                const std::uint64_t value = parse_unsigned_integer();
                if (value > std::numeric_limits<std::size_t>::max()) {
                    fail("n is outside the platform size range");
                }
                certificate.n = static_cast<std::size_t>(value);
                parsed_n_ = certificate.n;
                have_n = true;
            } else if (key == "out_neighbors") {
                if (have_out_neighbors) {
                    fail("duplicate top-level key 'out_neighbors'");
                }
                certificate.out_neighbors = parse_rows();
                have_out_neighbors = true;
            } else {
                fail("unknown top-level key '" + key + "'");
            }

            skip_ws();
            if (consume('}')) {
                break;
            }
            expect(',', "expected ',' or '}' in top-level object");
            skip_ws();
        }

        skip_ws();
        if (position_ != input_.size()) {
            fail("trailing data after top-level object");
        }
        if (!have_n || !have_out_neighbors) {
            fail("top-level object must contain exactly n and out_neighbors");
        }
        return certificate;
    }

    [[nodiscard]] std::optional<std::size_t> parsed_n() const {
        return parsed_n_;
    }

  private:
    std::string_view input_;
    std::size_t position_ = 0;
    std::optional<std::size_t> parsed_n_;

    [[noreturn]] void fail(const std::string& message) const {
        throw ParseError(message + " at byte " + std::to_string(position_));
    }

    void skip_ws() {
        while (position_ < input_.size()) {
            const unsigned char ch = static_cast<unsigned char>(input_[position_]);
            if (ch != ' ' && ch != '\t' && ch != '\r' && ch != '\n') {
                break;
            }
            ++position_;
        }
    }

    bool consume(char expected) {
        if (position_ < input_.size() && input_[position_] == expected) {
            ++position_;
            return true;
        }
        return false;
    }

    void expect(char expected, const char* message) {
        if (!consume(expected)) {
            fail(message);
        }
    }

    std::string parse_plain_string() {
        expect('"', "expected JSON string key");
        std::string result;
        while (position_ < input_.size()) {
            const unsigned char ch = static_cast<unsigned char>(input_[position_++]);
            if (ch == '"') {
                return result;
            }
            if (ch == '\\') {
                fail("escaped object keys are not canonical");
            }
            if (ch < 0x20U || ch > 0x7eU) {
                fail("object keys must be printable ASCII");
            }
            result.push_back(static_cast<char>(ch));
        }
        fail("unterminated JSON string key");
    }

    std::uint64_t parse_unsigned_integer() {
        if (position_ >= input_.size() || !std::isdigit(static_cast<unsigned char>(input_[position_]))) {
            fail("expected unsigned JSON integer");
        }
        if (input_[position_] == '0' && position_ + 1 < input_.size() &&
            std::isdigit(static_cast<unsigned char>(input_[position_ + 1]))) {
            fail("leading zero is not canonical for an integer");
        }

        std::uint64_t value = 0;
        while (position_ < input_.size() &&
               std::isdigit(static_cast<unsigned char>(input_[position_]))) {
            const unsigned digit = static_cast<unsigned>(input_[position_] - '0');
            if (value > (std::numeric_limits<std::uint64_t>::max() - digit) / 10U) {
                fail("integer overflow");
            }
            value = value * 10U + digit;
            ++position_;
        }
        return value;
    }

    std::vector<std::size_t> parse_row() {
        std::vector<std::size_t> row;
        expect('[', "expected adjacency-list row");
        skip_ws();
        if (consume(']')) {
            return row;
        }
        while (true) {
            const std::uint64_t value = parse_unsigned_integer();
            if (value > std::numeric_limits<std::size_t>::max()) {
                fail("neighbor index is outside the platform size range");
            }
            row.push_back(static_cast<std::size_t>(value));
            if (row.size() > kMaxVertices) {
                fail("adjacency-list row exceeds verifier limit");
            }
            skip_ws();
            if (consume(']')) {
                break;
            }
            expect(',', "expected ',' or ']' in adjacency-list row");
            skip_ws();
        }
        return row;
    }

    std::vector<std::vector<std::size_t>> parse_rows() {
        std::vector<std::vector<std::size_t>> rows;
        expect('[', "expected out_neighbors array");
        skip_ws();
        if (consume(']')) {
            return rows;
        }
        while (true) {
            rows.push_back(parse_row());
            if (rows.size() > kMaxVertices) {
                fail("out_neighbors row count exceeds verifier limit");
            }
            skip_ws();
            if (consume(']')) {
                break;
            }
            expect(',', "expected ',' or ']' in out_neighbors array");
            skip_ws();
        }
        return rows;
    }
};

std::string json_quote(std::string_view value) {
    std::ostringstream out;
    out << '"';
    constexpr char hex[] = "0123456789abcdef";
    for (const unsigned char ch : value) {
        switch (ch) {
            case '"': out << "\\\""; break;
            case '\\': out << "\\\\"; break;
            case '\b': out << "\\b"; break;
            case '\f': out << "\\f"; break;
            case '\n': out << "\\n"; break;
            case '\r': out << "\\r"; break;
            case '\t': out << "\\t"; break;
            default:
                if (ch < 0x20U) {
                    out << "\\u00" << hex[ch >> 4U] << hex[ch & 0x0fU];
                } else {
                    out << static_cast<char>(ch);
                }
        }
    }
    out << '"';
    return out.str();
}

template <typename T>
void emit_number_array(std::ostream& out, const std::vector<T>& values) {
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i != 0) {
            out << ',';
        }
        out << values[i];
    }
    out << ']';
}

void emit_invalid(std::optional<std::size_t> n, const std::vector<std::string>& errors) {
    std::cout << "{\"status\":\"INVALID_CERTIFICATE\",\"n\":";
    if (n.has_value()) {
        std::cout << *n;
    } else {
        std::cout << "null";
    }
    std::cout << ",\"per_vertex\":[],\"failing_vertices\":[],\"errors\":[";
    for (std::size_t i = 0; i < errors.size(); ++i) {
        if (i != 0) {
            std::cout << ',';
        }
        std::cout << json_quote(errors[i]);
    }
    std::cout << "]}\n";
}

void emit_valid(const std::string_view status, std::size_t n,
                const std::vector<VertexLedger>& ledger,
                const std::vector<std::size_t>& failing_vertices) {
    std::cout << "{\"status\":" << json_quote(status) << ",\"n\":" << n
              << ",\"per_vertex\":[";
    for (std::size_t i = 0; i < ledger.size(); ++i) {
        if (i != 0) {
            std::cout << ',';
        }
        const VertexLedger& entry = ledger[i];
        std::cout << "{\"vertex\":" << entry.vertex << ",\"n1\":";
        emit_number_array(std::cout, entry.n1);
        std::cout << ",\"d1\":" << entry.d1 << ",\"n2_new\":";
        emit_number_array(std::cout, entry.n2_new);
        std::cout << ",\"d2\":" << entry.d2 << ",\"strict_d2_lt_d1\":"
                  << (entry.strict ? "true" : "false") << '}';
    }
    std::cout << "],\"failing_vertices\":";
    emit_number_array(std::cout, failing_vertices);
    std::cout << ",\"errors\":[]}\n";
}

std::vector<std::string> validate_certificate(const Certificate& certificate) {
    std::vector<std::string> errors;
    const std::size_t n = certificate.n;
    if (n == 0) {
        errors.emplace_back("n must be positive");
    }
    if (n > kMaxVertices) {
        errors.emplace_back("n exceeds verifier limit " + std::to_string(kMaxVertices));
    }
    if (certificate.out_neighbors.size() != n) {
        errors.emplace_back("out_neighbors row count " +
                            std::to_string(certificate.out_neighbors.size()) +
                            " does not equal n " + std::to_string(n));
        return errors;
    }

    for (std::size_t v = 0; v < n; ++v) {
        const auto& row = certificate.out_neighbors[v];
        for (std::size_t i = 0; i < row.size(); ++i) {
            const std::size_t u = row[i];
            if (u >= n) {
                errors.emplace_back("row " + std::to_string(v) +
                                    " contains out-of-range neighbor " + std::to_string(u));
            }
            if (u == v) {
                errors.emplace_back("row " + std::to_string(v) +
                                    " contains forbidden loop " + std::to_string(v));
            }
            if (i != 0 && row[i - 1] >= u) {
                errors.emplace_back("row " + std::to_string(v) +
                                    " is not strictly increasing at position " +
                                    std::to_string(i));
            }
        }
    }
    if (!errors.empty()) {
        return errors;
    }

    for (std::size_t v = 0; v < n; ++v) {
        for (const std::size_t u : certificate.out_neighbors[v]) {
            if (v < u && std::binary_search(certificate.out_neighbors[u].begin(),
                                            certificate.out_neighbors[u].end(), v)) {
                errors.emplace_back("digon between " + std::to_string(v) + " and " +
                                    std::to_string(u));
            }
        }
    }
    return errors;
}

std::vector<VertexLedger> compute_ledger(const Certificate& certificate,
                                         std::vector<std::size_t>& failing_vertices) {
    const std::size_t n = certificate.n;
    const std::size_t words = (n + 63U) / 64U;
    std::vector<std::vector<std::uint64_t>> adjacency(
        n, std::vector<std::uint64_t>(words, UINT64_C(0)));

    for (std::size_t v = 0; v < n; ++v) {
        for (const std::size_t u : certificate.out_neighbors[v]) {
            adjacency[v][u / 64U] |= UINT64_C(1) << (u % 64U);
        }
    }

    std::vector<VertexLedger> ledger;
    ledger.reserve(n);
    for (std::size_t v = 0; v < n; ++v) {
        std::vector<std::uint64_t> second(words, UINT64_C(0));

        for (std::size_t word_index = 0; word_index < words; ++word_index) {
            std::uint64_t pending = adjacency[v][word_index];
            while (pending != 0) {
                const unsigned offset = std::countr_zero(pending);
                const std::size_t u = word_index * 64U + offset;
                for (std::size_t k = 0; k < words; ++k) {
                    second[k] |= adjacency[u][k];
                }
                pending &= pending - UINT64_C(1);
            }
        }

        for (std::size_t k = 0; k < words; ++k) {
            second[k] &= ~adjacency[v][k];
        }
        second[v / 64U] &= ~(UINT64_C(1) << (v % 64U));
        if ((n % 64U) != 0U) {
            second.back() &= (UINT64_C(1) << (n % 64U)) - UINT64_C(1);
        }

        VertexLedger entry;
        entry.vertex = v;
        entry.n1 = certificate.out_neighbors[v];
        entry.d1 = entry.n1.size();
        for (std::size_t word_index = 0; word_index < words; ++word_index) {
            std::uint64_t pending = second[word_index];
            while (pending != 0) {
                const unsigned offset = std::countr_zero(pending);
                entry.n2_new.push_back(word_index * 64U + offset);
                pending &= pending - UINT64_C(1);
            }
        }
        entry.d2 = entry.n2_new.size();
        entry.strict = entry.d2 < entry.d1;
        if (!entry.strict) {
            failing_vertices.push_back(v);
        }
        ledger.push_back(std::move(entry));
    }
    return ledger;
}

std::optional<std::string> read_file(const std::string& path, std::string& error) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        error = "cannot open certificate file '" + path + "'";
        return std::nullopt;
    }
    input.seekg(0, std::ios::end);
    const std::streamoff length = input.tellg();
    if (length < 0) {
        error = "cannot determine certificate file size";
        return std::nullopt;
    }
    if (static_cast<std::uint64_t>(length) > kMaxInputBytes) {
        error = "certificate file exceeds verifier input limit";
        return std::nullopt;
    }
    input.seekg(0, std::ios::beg);
    std::string contents(static_cast<std::size_t>(length), '\0');
    if (length != 0) {
        input.read(contents.data(), length);
        if (!input) {
            error = "failed while reading certificate file";
            return std::nullopt;
        }
    }
    return contents;
}

}  // namespace

int main(int argc, char** argv) {
    // Exit 0: verified counterexample. Exit 1: valid graph, predicate false.
    // Exit 2: I/O, JSON/schema, canonicality, or oriented-graph validation error.
    if (argc != 2) {
        emit_invalid(std::nullopt, {"usage: verify_bitset <certificate.json>"});
        return 2;
    }

    std::string io_error;
    const std::optional<std::string> contents = read_file(argv[1], io_error);
    if (!contents.has_value()) {
        emit_invalid(std::nullopt, {io_error});
        return 2;
    }

    JsonParser parser(*contents);
    Certificate certificate;
    try {
        certificate = parser.parse_certificate();
    } catch (const ParseError& error) {
        emit_invalid(parser.parsed_n(), {error.what()});
        return 2;
    } catch (const std::exception& error) {
        emit_invalid(parser.parsed_n(), {std::string("unexpected parser failure: ") + error.what()});
        return 2;
    }

    const std::vector<std::string> errors = validate_certificate(certificate);
    if (!errors.empty()) {
        emit_invalid(certificate.n, errors);
        return 2;
    }

    std::vector<std::size_t> failing_vertices;
    const std::vector<VertexLedger> ledger = compute_ledger(certificate, failing_vertices);
    if (failing_vertices.empty()) {
        emit_valid("VERIFIED_COUNTEREXAMPLE", certificate.n, ledger, failing_vertices);
        return 0;
    }
    emit_valid("VALID_GRAPH_NOT_COUNTEREXAMPLE", certificate.n, ledger, failing_vertices);
    return 1;
}
