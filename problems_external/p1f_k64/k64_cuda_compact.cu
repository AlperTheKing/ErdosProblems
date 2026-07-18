#define main k64_cuda_legacy_main
#include "k64_cuda.cu"
#undef main

// Staged survivor-compaction benchmark.  The exact merger, orbit predicate,
// input validation, and independent CPU scorer are shared with k64_cuda.cu.

