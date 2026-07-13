"""Exact cut-parity gate for the minimal one-owner 6/5 repair.

Two alternating five-vertex rows share a triple C.  Their remaining pairs are
the opposite shores {m,v} and {x,y} of the detour square.  Every alternating
five-path has a 3/2 color split.  No coloring of C makes both rows possible.
"""

from itertools import product


def balanced_five(colors):
    count = sum(colors)
    return count in (2, 3)


def main():
    survivors = []
    for common in product((0, 1), repeat=3):
        row_m_v = common + (0, 0)
        row_x_y = common + (1, 1)
        if balanced_five(row_m_v) and balanced_five(row_x_y):
            survivors.append(common)
    assert survivors == []
    print("verdict=PASS_NO_SHARED_TRIPLE_COLORING")
    print("common_colorings_checked=8 survivors=0")


if __name__ == "__main__":
    main()
