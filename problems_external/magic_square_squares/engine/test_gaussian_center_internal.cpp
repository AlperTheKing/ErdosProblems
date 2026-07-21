#define main gaussian_center_embedded_main
#include "gaussian_center.cpp"
#undef main

#include <iostream>
#include <stdexcept>

int main() {
    if (sha256("abc") !=
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad") {
        throw std::runtime_error("SHA-256 known-vector mismatch");
    }

    bool overflow_rejected = false;
    try {
        (void)parse_u128(
            "999999999999999999999999999999999999999999999999999999999");
    } catch (const std::runtime_error&) {
        overflow_rejected = true;
    }
    if (!overflow_rejected) {
        throw std::runtime_error("u128 overflow was not rejected");
    }

    Options options;
    options.mode = "G";
    options.start = 10;
    options.end = 20;
    options.chunk_size = 3;
    RunState state;
    state.status = "CANDIDATE_VERIFIED";
    state.next_m = 15;
    state.scalar_exit = 0;
    state.independent_exit = 0;
    state.candidate_sha256 = "test";
    state.candidate_file = "candidate.json";
    const std::string summary = summary_json(options, state);
    if (extract_json_integer(summary, "scalar_exit") != 0 ||
        extract_json_integer(summary, "independent_exit") != 0 ||
        extract_json_string(summary, "candidate_file") !=
            "candidate.json") {
        throw std::runtime_error("verification summary round-trip failed");
    }

    std::cout
        << "{\"ok\":true,\"sha256_known_vector\":true,"
           "\"u128_overflow_rejected\":true,"
           "\"verification_summary_round_trip\":true}\n";
    return 0;
}
