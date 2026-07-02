"""Relaxed version of _codex_ocpms_sibling_embedding.

Print sibling overloaded rows that are not strict equality-atom bad-set
images, but do share row/cut/spanning-supergraph data.
"""

from _codex_ocpms_sibling_embedding import (
    EQ,
    SIB,
    image_edges,
    image_path,
    overloaded_rows,
    side_image,
    subgraph_embeddings,
)


def main():
    eq_rows = overloaded_rows(EQ)
    sib_rows = overloaded_rows(SIB)
    embs = subgraph_embeddings(eq_rows[0]["E"], sib_rows[0]["E"])
    for sr in sib_rows:
        strict = False
        relaxed = []
        for er in eq_rows:
            for mp in embs:
                if side_image(er["side"], mp) != sr["side"]:
                    continue
                mapped_p = image_path(er["P"], mp)
                if mapped_p != sr["P"] and tuple(reversed(mapped_p)) != sr["P"]:
                    continue
                extra = sr["E"] - image_edges(er["E"], mp)
                if not extra or not extra <= sr["B"]:
                    continue
                mapped_m = image_edges(er["M"], mp)
                if mapped_m == sr["M"]:
                    strict = True
                else:
                    relaxed.append((er, extra, mapped_m))
        if strict:
            continue
        print(
            "ROW",
            "side",
            sr["side"],
            "P",
            sr["P"],
            "I",
            sr["I"],
            "M",
            sorted(sr["M"]),
            "relaxed",
            len(relaxed),
        )
        for er, extra, mapped_m in relaxed[:10]:
            print(
                "  REL",
                "eq_side",
                er["side"],
                "eq_P",
                er["P"],
                "eq_I",
                er["I"],
                "mapped_M",
                sorted(mapped_m),
                "extra_blue",
                sorted(extra),
            )


if __name__ == "__main__":
    main()
