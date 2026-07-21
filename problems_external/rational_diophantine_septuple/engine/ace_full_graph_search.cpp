#include <eclib/points.h>
#include <omp.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <climits>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;
constexpr long long SCALE = 1'000'000'000'000LL;
constexpr long long HEIGHT_BOUND = 1'000LL;
constexpr int COORDINATE_BOUND = 55;
constexpr int EXPECTED_VERTICES = 24'356;
constexpr long long HEIGHT_MATRIX[4][4] = {
    {3066644681814LL, -1604217266982LL, 2304106286354LL, -2647588945619LL},
    {-1604217266982LL, 4852120801592LL, 2186366222773LL, -805702796450LL},
    {2304106286354LL, 2186366222773LL, 8991728418553LL, -4979765774895LL},
    {-2647588945619LL, -805702796450LL, -4979765774895LL, 4515819823940LL},
};
constexpr std::array<int, 40> FILTERS = {
    65521, 65519, 65497, 65479, 65449, 65447, 65437, 65423,
    65419, 65413, 65407, 65393, 65381, 65371, 65357, 65353,
    65327, 65323, 65309, 65293, 65287, 65269, 65267, 65257,
    65239, 65213, 65203, 65183, 65179, 65173, 65171, 65167,
    65147, 65141, 65129, 65123, 65119, 65111, 65101, 65099,
};

struct Rational {
    bigint numerator;
    bigint denominator;

    Rational(bigint num, bigint den) : numerator(num), denominator(den) {
        if (denominator == 0) {
            throw std::runtime_error("zero rational denominator");
        }
        if (denominator < 0) {
            numerator = -numerator;
            denominator = -denominator;
        }
        bigint divisor = gcd(numerator, denominator);
        if (divisor < 0) {
            divisor = -divisor;
        }
        numerator /= divisor;
        denominator /= divisor;
    }
};

struct Vertex {
    std::array<int, 4> vector;
    long long q12;
    Rational h;
};

bool prime_by_trial_division(int value) {
    if (value < 2) {
        return false;
    }
    for (int divisor = 2; divisor * divisor <= value; ++divisor) {
        if (value % divisor == 0) {
            return false;
        }
    }
    return true;
}

long long proxy_height(const std::array<int, 4>& vector) {
    __int128 result = 0;
    for (int row = 0; row < 4; ++row) {
        for (int column = 0; column < 4; ++column) {
            result += static_cast<__int128>(vector[row])
                * HEIGHT_MATRIX[row][column] * vector[column];
        }
    }
    if (result < 0 || result > INT64_MAX) {
        throw std::runtime_error("proxy height overflow or loss of positivity");
    }
    return static_cast<long long>(result);
}

bool equal_rational(const Rational& value, long numerator, long denominator) {
    return value.numerator * denominator == bigint(numerator) * value.denominator;
}

std::string rational_text(const Rational& value) {
    std::ostringstream stream;
    stream << value.numerator;
    if (value.denominator != 1) {
        stream << "/" << value.denominator;
    }
    return stream.str();
}

long small_mod(const bigint& value, int modulus) {
    long result = bigint_mod_long(value, modulus);
    if (result < 0) {
        result += modulus;
    }
    return result;
}

bool exact_compatible(const Rational& left, const Rational& right) {
    const bigint denominator_product = left.denominator * right.denominator;
    const bigint numerator =
        left.numerator * right.numerator + denominator_product;
    if (numerator < 0) {
        return false;
    }
    const bigint witness = numerator * denominator_product;
    bigint root;
    SqrRoot(root, witness);
    return root * root == witness;
}

std::uint64_t pair_offset(std::uint64_t left, std::uint64_t count) {
    return left * (2 * count - left - 1) / 2;
}

std::uint64_t pair_ordinal(
    std::uint64_t left, std::uint64_t right, std::uint64_t count
) {
    return pair_offset(left, count) + (right - left - 1);
}

std::vector<Vertex> generate_vertices(const std::filesystem::path& output_path) {
    set_precision(200);
    initprimes("PRIMES", 0);
    Curvedata curve(
        ZZ(0), ZZ(2568913), ZZ(0), ZZ(1535181310080LL),
        ZZ(59427518261760000LL), 0
    );
    std::array<Point, 4> basis = {
        Point(curve, ZZ(-861840), ZZ(65622960), ZZ(1)),
        Point(curve, ZZ(-860928), ZZ(60830400), ZZ(1)),
        Point(curve, ZZ(-855520), ZZ(10311840), ZZ(1)),
        Point(curve, ZZ(-1506120), ZZ(-397614360), ZZ(1)),
    };
    Point torsion(curve, ZZ(-1672000), ZZ(0), ZZ(1));

    std::array<std::vector<Point>, 4> multiples;
    for (int coordinate = 0; coordinate < 4; ++coordinate) {
        multiples[coordinate].reserve(2 * COORDINATE_BOUND + 1);
        for (
            int coefficient = -COORDINATE_BOUND;
            coefficient <= COORDINATE_BOUND;
            ++coefficient
        ) {
            multiples[coordinate].push_back(coefficient * basis[coordinate]);
        }
    }

    std::vector<Vertex> vertices;
    vertices.reserve(EXPECTED_VERTICES);
    std::set<std::string> unique_values;
    for (int k1 = 1; k1 <= 55; k1 += 2) {
        for (int k2 = -55; k2 <= 55; k2 += 2) {
            for (int k3 = -55; k3 <= 55; k3 += 2) {
                for (int k4 = -54; k4 <= 54; k4 += 2) {
                    const std::array<int, 4> vector = {k1, k2, k3, k4};
                    const long long q12 = proxy_height(vector);
                    if (q12 > HEIGHT_BOUND * SCALE) {
                        continue;
                    }
                    Point point = torsion;
                    point += multiples[0][k1 + COORDINATE_BOUND];
                    point += multiples[1][k2 + COORDINATE_BOUND];
                    point += multiples[2][k3 + COORDINATE_BOUND];
                    point += multiples[3][k4 + COORDINATE_BOUND];
                    if (point.is_zero() || !point.isvalid()) {
                        throw std::runtime_error("invalid canonical coset point");
                    }
                    Rational h(
                        bigint(7) * point.getX(),
                        bigint(5'078'700) * point.getZ()
                    );
                    if (h.numerator == 0) {
                        continue;
                    }
                    if (
                        equal_rational(h, 243, 560)
                        || equal_rational(h, 1100, 63)
                        || equal_rational(h, 95, 112)
                    ) {
                        continue;
                    }
                    const std::string normalized = rational_text(h);
                    if (!unique_values.insert(normalized).second) {
                        throw std::runtime_error("duplicate h after k1>0 canonicalization");
                    }
                    vertices.push_back(Vertex{vector, q12, std::move(h)});
                }
            }
        }
    }
    if (static_cast<int>(vertices.size()) != EXPECTED_VERTICES) {
        throw std::runtime_error("vertex count differs from declared 24356");
    }

    std::ofstream output(output_path);
    if (!output) {
        throw std::runtime_error("cannot create vertices.tsv");
    }
    output << "index\tk1\tk2\tk3\tk4\tq12_scaled\tnumerator\tdenominator\n";
    for (std::size_t index = 0; index < vertices.size(); ++index) {
        const Vertex& vertex = vertices[index];
        output << index;
        for (int coefficient : vertex.vector) {
            output << '\t' << coefficient;
        }
        output << '\t' << vertex.q12 << '\t' << vertex.h.numerator
               << '\t' << vertex.h.denominator << '\n';
    }
    return vertices;
}

std::vector<std::uint64_t> find_edges_and_write_survivors(
    const std::vector<Vertex>& vertices,
    const std::vector<std::uint8_t>& certificate,
    const std::filesystem::path& survivors_path,
    const std::filesystem::path& edges_path,
    std::uint64_t& survivor_count
) {
    const std::uint64_t count = vertices.size();
    std::vector<std::uint64_t> edges;
    std::ofstream survivors(survivors_path);
    std::ofstream edges_output(edges_path);
    if (!survivors || !edges_output) {
        throw std::runtime_error("cannot create survivor or edge artifact");
    }
    survivors << "left\tright\tis_edge\n";
    edges_output << "left\tright\n";
    survivor_count = 0;
    for (std::uint64_t left = 0; left < count; ++left) {
        for (std::uint64_t right = left + 1; right < count; ++right) {
            const std::uint64_t ordinal = pair_ordinal(left, right, count);
            if (certificate[ordinal] != 0) {
                continue;
            }
            ++survivor_count;
            const bool compatible = exact_compatible(vertices[left].h, vertices[right].h);
            survivors << left << '\t' << right << '\t' << (compatible ? 1 : 0) << '\n';
            if (compatible) {
                edges.push_back((left << 32) | right);
                edges_output << left << '\t' << right << '\n';
            }
        }
    }
    return edges;
}

std::array<std::uint32_t, 4> find_four_clique(
    std::size_t vertex_count,
    const std::vector<std::uint64_t>& edges,
    std::uint64_t& triangle_count
) {
    const std::size_t words = (vertex_count + 63) / 64;
    std::vector<std::uint64_t> adjacency(vertex_count * words, 0);
    for (std::uint64_t encoded : edges) {
        const std::uint32_t left = static_cast<std::uint32_t>(encoded >> 32);
        const std::uint32_t right = static_cast<std::uint32_t>(encoded);
        adjacency[static_cast<std::size_t>(left) * words + right / 64]
            |= std::uint64_t(1) << (right % 64);
        adjacency[static_cast<std::size_t>(right) * words + left / 64]
            |= std::uint64_t(1) << (left % 64);
    }

    std::vector<std::uint64_t> common(words);
    triangle_count = 0;
    for (std::uint64_t encoded : edges) {
        const std::uint32_t left = static_cast<std::uint32_t>(encoded >> 32);
        const std::uint32_t right = static_cast<std::uint32_t>(encoded);
        const std::size_t first_word = right / 64;
        for (std::size_t word = 0; word < first_word; ++word) {
            common[word] = 0;
        }
        for (std::size_t word = first_word; word < words; ++word) {
            common[word] =
                adjacency[static_cast<std::size_t>(left) * words + word]
                & adjacency[static_cast<std::size_t>(right) * words + word];
        }
        const unsigned right_bit = right % 64;
        common[first_word] &= right_bit == 63
            ? 0
            : (~std::uint64_t(0) << (right_bit + 1));

        for (std::size_t word = first_word; word < words; ++word) {
            triangle_count += static_cast<std::uint64_t>(__builtin_popcountll(common[word]));
        }
        for (std::size_t word = first_word; word < words; ++word) {
            std::uint64_t pending = common[word];
            while (pending != 0) {
                const unsigned bit = static_cast<unsigned>(__builtin_ctzll(pending));
                const std::uint32_t third = static_cast<std::uint32_t>(word * 64 + bit);
                pending &= pending - 1;
                const std::size_t third_word = third / 64;
                for (std::size_t candidate_word = third_word; candidate_word < words; ++candidate_word) {
                    std::uint64_t fourths =
                        common[candidate_word]
                        & adjacency[static_cast<std::size_t>(third) * words + candidate_word];
                    if (candidate_word == third_word) {
                        const unsigned third_bit = third % 64;
                        fourths &= third_bit == 63
                            ? 0
                            : (~std::uint64_t(0) << (third_bit + 1));
                    }
                    if (fourths != 0) {
                        const unsigned fourth_bit =
                            static_cast<unsigned>(__builtin_ctzll(fourths));
                        const std::uint32_t fourth =
                            static_cast<std::uint32_t>(candidate_word * 64 + fourth_bit);
                        return {left, right, third, fourth};
                    }
                }
            }
        }
    }
    return {UINT32_MAX, UINT32_MAX, UINT32_MAX, UINT32_MAX};
}

double seconds_since(const Clock::time_point& start) {
    return std::chrono::duration<double>(Clock::now() - start).count();
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc < 2 || argc > 4) {
            std::cerr << "usage: ace_full_graph_search OUTPUT_DIR [THREADS] [--vertices-only]\n";
            return 2;
        }
        const std::filesystem::path output_dir(argv[1]);
        const int workers = argc >= 3 ? std::stoi(argv[2]) : 64;
        const bool vertices_only = argc == 4 && std::string(argv[3]) == "--vertices-only";
        if (workers < 1 || workers > 64) {
            throw std::runtime_error("worker count must be in [1,64]");
        }
        for (int modulus : FILTERS) {
            if (!prime_by_trial_division(modulus)) {
                throw std::runtime_error("declared filter is not prime");
            }
        }
        std::filesystem::create_directories(output_dir);
        const Clock::time_point total_start = Clock::now();
        const Clock::time_point vertex_start = Clock::now();
        std::vector<Vertex> vertices = generate_vertices(output_dir / "vertices.tsv");
        const double vertex_seconds = seconds_since(vertex_start);
        if (vertices_only) {
            std::cout << "{\"status\":\"VERTICES_ONLY\",\"vertex_count\":"
                      << vertices.size() << ",\"vertex_seconds\":" << vertex_seconds
                      << "}\n";
            return 0;
        }

        const std::size_t count = vertices.size();
        const std::uint64_t pair_count = count * (count - 1) / 2;
        if (pair_count != 296'595'190ULL) {
            throw std::runtime_error("pair count differs from declared scope");
        }

        std::vector<std::vector<std::uint8_t>> square_residues;
        square_residues.reserve(FILTERS.size());
        for (int modulus : FILTERS) {
            std::vector<std::uint8_t> residues(modulus, 0);
            for (int value = 0; value < modulus; ++value) {
                residues[static_cast<std::uint64_t>(value) * value % modulus] = 1;
            }
            square_residues.push_back(std::move(residues));
        }

        std::vector<std::uint16_t> numerator_mod(count * FILTERS.size());
        std::vector<std::uint16_t> denominator_mod(count * FILTERS.size());
        for (std::size_t vertex = 0; vertex < count; ++vertex) {
            for (std::size_t filter = 0; filter < FILTERS.size(); ++filter) {
                numerator_mod[vertex * FILTERS.size() + filter] =
                    static_cast<std::uint16_t>(small_mod(vertices[vertex].h.numerator, FILTERS[filter]));
                denominator_mod[vertex * FILTERS.size() + filter] =
                    static_cast<std::uint16_t>(small_mod(vertices[vertex].h.denominator, FILTERS[filter]));
            }
        }

        std::vector<std::uint8_t> certificate(pair_count, 0);
        std::vector<std::array<std::uint64_t, FILTERS.size()>> thread_rejects(workers);
        for (auto& counts : thread_rejects) {
            counts.fill(0);
        }
        const Clock::time_point filter_start = Clock::now();
#pragma omp parallel for schedule(dynamic, 8) num_threads(workers)
        for (long long left_signed = 0; left_signed < static_cast<long long>(count); ++left_signed) {
            const std::size_t left = static_cast<std::size_t>(left_signed);
            const int thread = omp_get_thread_num();
            for (std::size_t right = left + 1; right < count; ++right) {
                std::uint8_t code = 0;
                for (std::size_t filter = 0; filter < FILTERS.size(); ++filter) {
                    const std::uint64_t modulus = FILTERS[filter];
                    const std::uint64_t denominator_product =
                        static_cast<std::uint64_t>(
                            denominator_mod[left * FILTERS.size() + filter]
                        ) * denominator_mod[right * FILTERS.size() + filter] % modulus;
                    const std::uint64_t numerator_product =
                        static_cast<std::uint64_t>(
                            numerator_mod[left * FILTERS.size() + filter]
                        ) * numerator_mod[right * FILTERS.size() + filter] % modulus;
                    const std::uint64_t witness =
                        ((numerator_product + denominator_product) % modulus)
                        * denominator_product % modulus;
                    if (!square_residues[filter][witness]) {
                        code = static_cast<std::uint8_t>(filter + 1);
                        ++thread_rejects[thread][filter];
                        break;
                    }
                }
                certificate[pair_ordinal(left, right, count)] = code;
            }
        }
        const double filter_seconds = seconds_since(filter_start);

        std::array<std::uint64_t, FILTERS.size()> reject_counts{};
        reject_counts.fill(0);
        for (const auto& local : thread_rejects) {
            for (std::size_t filter = 0; filter < FILTERS.size(); ++filter) {
                reject_counts[filter] += local[filter];
            }
        }
        std::uint64_t rejected_count = 0;
        for (std::uint64_t value : reject_counts) {
            rejected_count += value;
        }

        const std::filesystem::path certificate_path = output_dir / "pair_certificate.bin";
        std::ofstream certificate_output(certificate_path, std::ios::binary);
        if (!certificate_output) {
            throw std::runtime_error("cannot create pair certificate");
        }
        certificate_output.write(
            reinterpret_cast<const char*>(certificate.data()),
            static_cast<std::streamsize>(certificate.size())
        );
        certificate_output.close();
        if (!certificate_output) {
            throw std::runtime_error("pair certificate write failed");
        }

        const Clock::time_point exact_start = Clock::now();
        std::uint64_t survivor_count = 0;
        std::vector<std::uint64_t> edges = find_edges_and_write_survivors(
            vertices,
            certificate,
            output_dir / "survivors.tsv",
            output_dir / "edges.tsv",
            survivor_count
        );
        if (rejected_count + survivor_count != pair_count) {
            throw std::runtime_error("certificate partition does not cover every pair");
        }
        const double exact_seconds = seconds_since(exact_start);

        const Clock::time_point clique_start = Clock::now();
        std::uint64_t triangle_count = 0;
        const std::array<std::uint32_t, 4> clique =
            find_four_clique(vertices.size(), edges, triangle_count);
        const bool hit = clique[0] != UINT32_MAX;
        const double clique_seconds = seconds_since(clique_start);

        if (hit) {
            std::ofstream candidate(output_dir / "candidate.json");
            candidate << "{\n  \"name\": \"ace-q12-full-graph\",\n  \"indices\": ["
                      << clique[0] << ", " << clique[1] << ", " << clique[2]
                      << ", " << clique[3] << "],\n  \"values\": [\"243/560\", "
                      << "\"1100/63\", \"95/112\"";
            for (std::uint32_t index : clique) {
                candidate << ", \"" << rational_text(vertices[index].h) << "\"";
            }
            candidate << "]\n}\n";
        }

        std::ofstream summary(output_dir / "summary.json");
        summary << "{\n"
                << "  \"status\": \"" << (hit ? "HIT" : "NO_HIT") << "\",\n"
                << "  \"workers\": " << workers << ",\n"
                << "  \"vertex_count\": " << vertices.size() << ",\n"
                << "  \"pair_count\": " << pair_count << ",\n"
                << "  \"certificate_bytes\": " << certificate.size() << ",\n"
                << "  \"modular_survivors\": " << survivor_count << ",\n"
                << "  \"exact_square_tests\": " << survivor_count << ",\n"
                << "  \"edge_count\": " << edges.size() << ",\n"
                << "  \"triangle_count_until_hit_or_exhaustion\": " << triangle_count << ",\n"
                << "  \"clique\": ";
        if (hit) {
            summary << "[" << clique[0] << ", " << clique[1] << ", "
                    << clique[2] << ", " << clique[3] << "]";
        } else {
            summary << "null";
        }
        summary << ",\n  \"filters\": [";
        for (std::size_t index = 0; index < FILTERS.size(); ++index) {
            if (index) summary << ", ";
            summary << FILTERS[index];
        }
        summary << "],\n  \"reject_counts\": [";
        for (std::size_t index = 0; index < reject_counts.size(); ++index) {
            if (index) summary << ", ";
            summary << reject_counts[index];
        }
        summary << "],\n"
                << "  \"vertex_seconds\": " << vertex_seconds << ",\n"
                << "  \"filter_seconds\": " << filter_seconds << ",\n"
                << "  \"exact_seconds\": " << exact_seconds << ",\n"
                << "  \"clique_seconds\": " << clique_seconds << ",\n"
                << "  \"total_seconds\": " << seconds_since(total_start) << "\n"
                << "}\n";
        summary.close();

        std::cout << "{\"status\":\"" << (hit ? "HIT" : "NO_HIT")
                  << "\",\"vertex_count\":" << vertices.size()
                  << ",\"pair_count\":" << pair_count
                  << ",\"modular_survivors\":" << survivor_count
                  << ",\"edge_count\":" << edges.size()
                  << ",\"triangle_count\":" << triangle_count << "}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }
}
