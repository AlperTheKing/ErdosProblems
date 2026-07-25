"""Export every Vega graph (i = 2..IMAX) to P3_input.txt for the C++ engines.

Format per graph:
  NAME <name> <i> <n> <m>
  EDGES <u0> <v0> <u1> <v1> ...            (0-indexed, m pairs)
  ROLE  <role of vertex 0> ... <role of vertex n-1>
        role = circle position 1..3i-1 for Gamma_i vertices, or one of x y a b c u v w
  AUT <k>
  <k permutation lines, each n integers>
  WEIGHT <w0> ... <w_{n-1}>                (the paper's regular weight function)
Vertex order is the canonical one of P3_vega.canon_order.
"""
import sys
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
import P3_vega as V


def main(imax=8, out='P3_input.txt'):
    f = open(out, 'w')
    for i in range(2, imax + 1):
        fam, _ = V.vega_family(i)
        for name, G, w in fam:
            order = V.canon_order(G)
            idx = {t: k for k, t in enumerate(order)}
            n = len(order)
            E = sorted((idx[a], idx[b]) if idx[a] < idx[b] else (idx[b], idx[a])
                       for a, b in G.edges())
            f.write('NAME %s %d %d %d\n' % (name, i, n, len(E)))
            f.write('EDGES ' + ' '.join('%d %d' % e for e in E) + '\n')
            f.write('ROLE ' + ' '.join(str(t) for t in order) + '\n')
            gm = GraphMatcher(G, G)
            perms = []
            for mp in gm.isomorphisms_iter():
                perms.append([idx[mp[t]] for t in order])
            perms.sort()
            f.write('AUT %d\n' % len(perms))
            for p in perms:
                f.write(' '.join(map(str, p)) + '\n')
            f.write('WEIGHT ' + ' '.join(str(w[t]) for t in order) + '\n')
            print(name, 'n=%d m=%d |Aut|=%d' % (n, len(E), len(perms)))
    f.close()
    print('wrote', out)


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
