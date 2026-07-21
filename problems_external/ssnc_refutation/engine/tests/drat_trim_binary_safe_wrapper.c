/*
 * Windows binary-I/O wrapper for the pinned upstream drat-trim.c.
 *
 * The included source opens both the DIMACS input and binary DRAT proof with
 * mode "r".  On the Microsoft CRT that mode treats byte 0x1a as text EOF.
 * This wrapper changes read-only opens to "rb" without editing the pinned
 * upstream source or either certificate artifact.  Write modes are unchanged.
 */

#include <stdio.h>
#include <string.h>

static FILE *drat_binary_safe_fopen(const char *path, const char *mode) {
#ifdef _WIN32
  if (!strcmp(mode, "r"))
    return fopen(path, "rb");
#endif
  return fopen(path, mode);
}

#define fopen drat_binary_safe_fopen
#define main drat_trim_upstream_main
#include "../../../../third_party/cadical/test/cnf/drat-trim.c"
#undef main
#undef fopen

int main(int argc, char **argv) { return drat_trim_upstream_main(argc, argv); }
