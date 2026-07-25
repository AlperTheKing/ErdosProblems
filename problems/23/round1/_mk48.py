import claude_h1_groups as G
g = G.binary_octahedral_exact()
print("2O built and verified, order", g[1])
pool = G.build_pool([48], verbose=False)
cur = pool[48]
print("pool from constructions:", len(cur))
new = G.dedupe(cur + [g])
print("after adding 2O:", len(new), " (known count for order 48 = 52)")
G.write_groups("h1_groups/groups_48.txt", 48, new)
print("wrote h1_groups/groups_48.txt with", len(new))
