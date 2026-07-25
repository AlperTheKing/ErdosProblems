#define main search_pairs_program_main
#include "search_pairs.cpp"
#undef main

#include <iostream>

static int fail(const char* message) {
    std::cerr << "FAIL " << message << "\n";
    return 1;
}

int main() {
    std::array<u128, 128> out{};
    std::size_t len = 0, valley = 999;

    Poly64 a{1, 1, 2};
    Poly64 b{1, 1, 3};
    if (product_unimodal(a, b, out, len, valley))
        return fail("missed convolution valley");
    const u64 expected1[] = {1, 2, 6, 5, 6};
    if (len != 5 || valley != 3) return fail("wrong valley index");
    for (std::size_t i = 0; i < len; ++i)
        if (out[i] != expected1[i]) return fail("wrong convolution");

    Poly64 plateau{1, 5, 2, 2, 5, 1};
    Poly64 one{1};
    if (product_unimodal(plateau, one, out, len, valley))
        return fail("missed plateau valley");

    Poly64 c{1, 3, 3, 2};
    Poly64 d{1, 2};
    if (!product_unimodal(c, d, out, len, valley))
        return fail("false positive on unimodal convolution");

    std::cout << "ALL PAIR-SCANNER SELF-TESTS PASS\n";
    return 0;
}
