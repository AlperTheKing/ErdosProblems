"""Emit the n>30 catalogue members as graph6 for the heuristic screen."""
import pickle
from f8_core import g6_encode, edges_of, is_triangle_free

big = pickle.load(open('f8_fam_big.pkl', 'rb'))
with open('f8_fam_big.g6', 'w') as f, open('f8_fam_big_names.txt', 'w') as g:
    for name, n, adj in big:
        assert is_triangle_free(n, adj), name
        s = g6_encode(n, adj)
        f.write(s + "\n")
        g.write(f"{s}\t{name}\n")
print("wrote", len(big))
