from fractions import Fraction
import argparse


def orbit(modulus):
    seen = bytearray(modulus)
    queue = []
    def add(x):
        x %= modulus
        if not seen[x]:
            seen[x] = 1
            queue.append(x)
    for x in (9, 14, 2, 3, 5):
        add(x)
    head = 0
    while head < len(queue):
        x = queue[head]
        head += 1
        add(2*x - 1)
        add(3*x - 1)
        add(5*x - 1)
    return seen, len(queue)


def collision_stats(modulus):
    seen, size = orbit(modulus)
    c23 = c25 = c35 = c235 = 0
    for t in range(modulus):
        b2 = seen[(2*t) % modulus]
        b3 = seen[(3*t) % modulus]
        b5 = seen[(5*t) % modulus]
        c23 += bool(b2 and b3)
        c25 += bool(b2 and b5)
        c35 += bool(b3 and b5)
        c235 += bool(
            seen[(6*t) % modulus]
            and seen[(10*t) % modulus]
            and seen[(15*t) % modulus]
        )
    beta = (
        Fraction(c23, 6*modulus)
        + Fraction(c25, 10*modulus)
        + Fraction(c35, 15*modulus)
        - Fraction(c235, 30*modulus)
    )
    return size, c23, c25, c35, c235, beta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-power', type=int, default=4)
    args = parser.parse_args()
    expected = {
        1: (16, 7, 11, 11, 1),
        2: (389, 115, 139, 199, 6),
        3: (10150, 2229, 2966, 3480, 44),
        4: (275033, 54131, 74383, 76799, 1106),
    }
    modulus = 1
    print('a,modulus,orbit,c23,c25,c35,c235,beta,30beta')
    for a in range(1, args.max_power + 1):
        modulus *= 30
        size, c23, c25, c35, c235, beta = collision_stats(modulus)
        if a in expected:
            assert (size, c23, c25, c35, c235) == expected[a]
        print(f'{a},{modulus},{size},{c23},{c25},{c35},{c235},{beta},{30*beta}')


if __name__ == '__main__':
    main()
