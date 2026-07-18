#include <cstdio>

// Compile the unmodified upstream program under a private entry-point name.
// The wrapper disables stdout buffering before upstream main starts, so the
// controller can stop every worker immediately after an L44 certificate line.
#define main sorterhunter_upstream_main
#include "SorterHunter/SorterHunter.cpp"
#undef main

int main(int argc, char* argv[]) {
    std::setvbuf(stdout, nullptr, _IONBF, 0);
    return sorterhunter_upstream_main(argc, argv);
}
