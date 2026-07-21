// Independent bitset verifier for an AJT F_5, n=8 matrix certificate.

#include <array>
#include <cstddef>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>

namespace {

constexpr int kModulus = 5;
constexpr int kDimension = 8;
constexpr std::size_t kTorusSize = 65536;
constexpr std::size_t kWordBits = 64;
constexpr std::size_t kWordCount = kTorusSize / kWordBits;

using Matrix = std::array<std::array<int, kDimension>, kDimension>;
using Point = std::array<int, kDimension>;
using Mask = std::array<std::uint64_t, kWordCount>;

enum class Status {
    kCovered,
    kSingular,
    kUncovered,
};

struct VerificationResult {
    Status status;
    int rank;
    Point witness{};
};

int Mod5(long long value) {
    int residue = static_cast<int>(value % kModulus);
    return residue < 0 ? residue + kModulus : residue;
}

bool ReadMatrix(const std::string& path, Matrix* matrix, std::string* error) {
    std::ifstream input(path);
    if (!input) {
        *error = "cannot open matrix file";
        return false;
    }

    for (int row = 0; row < kDimension; ++row) {
        for (int column = 0; column < kDimension; ++column) {
            long long entry = 0;
            if (!(input >> entry)) {
                *error = "expected exactly 64 integer entries";
                return false;
            }
            (*matrix)[row][column] = Mod5(entry);
        }
    }

    std::string extra;
    if (input >> extra) {
        *error = "matrix file has extra token after 64 integer entries";
        return false;
    }
    return true;
}

int RankMod5(const Matrix& matrix) {
    static constexpr std::array<int, kModulus> kInverse = {0, 1, 3, 2, 4};
    Matrix work = matrix;
    int rank = 0;

    for (int column = 0; column < kDimension; ++column) {
        int pivot = rank;
        while (pivot < kDimension && work[pivot][column] == 0) {
            ++pivot;
        }
        if (pivot == kDimension) {
            continue;
        }

        std::swap(work[rank], work[pivot]);
        const int inverse = kInverse[work[rank][column]];
        for (int col = column; col < kDimension; ++col) {
            work[rank][col] = Mod5(work[rank][col] * inverse);
        }

        for (int row = 0; row < kDimension; ++row) {
            if (row == rank) {
                continue;
            }
            const int factor = work[row][column];
            if (factor == 0) {
                continue;
            }
            for (int col = column; col < kDimension; ++col) {
                work[row][col] =
                    Mod5(work[row][col] - factor * work[rank][col]);
            }
        }

        ++rank;
        if (rank == kDimension) {
            break;
        }
    }

    return rank;
}

Point DecodePoint(std::size_t index) {
    Point point{};
    for (int coordinate = 0; coordinate < kDimension; ++coordinate) {
        point[coordinate] = static_cast<int>(index & 3U) + 1;
        index >>= 2U;
    }
    return point;
}

VerificationResult VerifyMatrix(const Matrix& matrix) {
    const int rank = RankMod5(matrix);
    if (rank != kDimension) {
        return {Status::kSingular, rank, {}};
    }

    std::array<Mask, kDimension> kernel_masks{};
    for (std::size_t index = 0; index < kTorusSize; ++index) {
        const Point point = DecodePoint(index);
        const std::size_t word = index / kWordBits;
        const std::uint64_t bit = std::uint64_t{1} << (index % kWordBits);

        for (int row = 0; row < kDimension; ++row) {
            int dot_product = 0;
            for (int column = 0; column < kDimension; ++column) {
                dot_product += matrix[row][column] * point[column];
            }
            if (Mod5(dot_product) == 0) {
                kernel_masks[row][word] |= bit;
            }
        }
    }

    Mask covered{};
    for (int row = 0; row < kDimension; ++row) {
        for (std::size_t word = 0; word < kWordCount; ++word) {
            covered[word] |= kernel_masks[row][word];
        }
    }

    for (std::size_t index = 0; index < kTorusSize; ++index) {
        const std::uint64_t bit =
            std::uint64_t{1} << (index % kWordBits);
        if ((covered[index / kWordBits] & bit) == 0) {
            return {Status::kUncovered, rank, DecodePoint(index)};
        }
    }

    return {Status::kCovered, rank, {}};
}

int RunSelfTest() {
    Matrix identity{};
    for (int index = 0; index < kDimension; ++index) {
        identity[index][index] = 1;
    }

    const VerificationResult result = VerifyMatrix(identity);
    Point expected{};
    expected.fill(1);
    if (result.status != Status::kUncovered ||
        result.rank != kDimension ||
        result.witness != expected) {
        std::cerr << "SELF-TEST FAIL: identity was not rejected as expected\n";
        return 2;
    }

    std::cout << "SELF-TEST PASS: identity rejected with uncovered witness";
    for (const int coordinate : expected) {
        std::cout << ' ' << coordinate;
    }
    std::cout << '\n';
    return 0;
}

void PrintWitness(const Point& point) {
    for (int coordinate = 0; coordinate < kDimension; ++coordinate) {
        if (coordinate != 0) {
            std::cout << ' ';
        }
        std::cout << point[coordinate];
    }
}

}  // namespace

int main(int argc, char** argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        return RunSelfTest();
    }
    if (argc != 2) {
        std::cerr << "usage: verify_bitset MATRIX_FILE\n"
                  << "       verify_bitset --self-test\n";
        return 2;
    }

    Matrix matrix{};
    std::string error;
    if (!ReadMatrix(argv[1], &matrix, &error)) {
        std::cerr << "INPUT ERROR: " << error << '\n';
        return 2;
    }

    const VerificationResult result = VerifyMatrix(matrix);
    if (result.status == Status::kCovered) {
        std::cout << "PASS: rank=8; OR of eight kernel masks covers all "
                  << kTorusSize << " nowhere-zero vectors\n";
        return 0;
    }
    if (result.status == Status::kSingular) {
        std::cout << "FAIL: singular modulo 5; rank=" << result.rank << '\n';
        return 1;
    }

    std::cout << "FAIL: uncovered witness: ";
    PrintWitness(result.witness);
    std::cout << '\n';
    return 1;
}
