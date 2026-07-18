#include <cstdio>

namespace {
struct LineBufferedStdout {
    LineBufferedStdout() { std::setvbuf(stdout, nullptr, _IOLBF, 0); }
};

LineBufferedStdout line_buffered_stdout;
}  // namespace
