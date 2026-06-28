"""Census-only run of the logic audit (no large Mycielskians; brute maxcut caps at N<=23)."""
from _bdef_logic import run_census

if __name__ == "__main__":
    print("=== census J1/J2/J3 audit (full triangle-free connected census) ===")
    run_census(11, 5, 1)
