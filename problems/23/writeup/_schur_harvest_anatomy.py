"""Anatomy probe for the Schur harvest inequality.

For a minority overloaded vertex o, write psi=1-h on U.  Then

    rho_o = I_o - a_o,
    I_o = sum_{u in U} c_ou psi_u,
    cU_o = sum_{u in U} c_ou,

where c_ou=-H[o,u].  Harvest

    25*rho_o >= 4*(cU_o-a_o)

is equivalent to

    weighted_average_{c_ou}(psi_u) >= (4*cU_o+21*a_o)/(25*cU_o).

This script dumps the direct-neighbor distribution for the weak harvest and
high-ratio guardrail cases, and scans whether the bound is pointwise on every
direct U-neighbor.  It is a diagnostic, not an acceptance gate.
"""

from fractions import Fraction as F

from _bdef_construct import Cn, mycielski
from _hardy_gate import BETA, build_H, maxcut_ls
from _Rsize_gate import solve_mat
from _satzmu_conn import struct_for_side
from _schur_absorption_hall_gate import adj_from_edges, schur_on_O
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup


def harmonic_psi(H, O, U, T, n):
    Huu = [[H[a][b] for b in U] for a in U]
    rhs = [[F(n) - T[u]] for u in U]
    sol = solve_mat(Huu, rhs)
    if sol is None:
        return None
    return {U[i]: sol[i][0] for i in range(len(U))}


def analyze_cut(name, n, edges, side, focus=None):
    adj = adj_from_edges(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, ell, T, _mu, cyc = st
    if not M:
        return []
    N = F(n)
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    if not O:
        return []
    H = build_H(n, M, ell, T, cyc, BETA)
    S = schur_on_O(H, O, U)
    psi = harmonic_psi(H, O, U, T, n)
    if S is None or psi is None:
        return []
    a = [T[o] - N for o in O]
    A = sum(a)
    rho = [sum(S[i]) for i in range(len(O))]
    out = []
    for i, o in enumerate(O):
        if focus is not None and o != focus:
            continue
        if a[i] > A - a[i]:
            continue
        neigh = []
        for u in U:
            c = -H[o][u]
            if c <= 0:
                continue
            d = N - T[u]
            cO = sum(-H[u][oo] for oo in O if -H[u][oo] > 0)
            cOtherO = cO - c
            cUU = sum(-H[u][w] for w in U if w != u and -H[u][w] > 0)
            row_pull = d + sum((-H[u][w]) * psi[w] for w in U if w != u and -H[u][w] > 0)
            denom = d + cO + cUU
            local_rhs_avg = row_pull / denom if denom else None
            neigh.append(
                dict(
                    u=u,
                    c=c,
                    psi=psi[u],
                    d=d,
                    cO=cO,
                    cOtherO=cOtherO,
                    cUU=cUU,
                    denom=denom,
                    local_rhs_avg=local_rhs_avg,
                )
            )
        cU = sum(row["c"] for row in neigh)
        I = sum(row["c"] * row["psi"] for row in neigh)
        e = cU - a[i]
        g = A - 2 * a[i]
        theta = (4 * cU + 21 * a[i]) / (25 * cU) if cU else None
        minpsi = min((row["psi"] for row in neigh), default=None)
        bad_point = [row for row in neigh if theta is not None and row["psi"] < theta]
        out.append(
            dict(
                name=name,
                n=n,
                side="".join(map(str, side)),
                o=o,
                O=tuple(O),
                a=a[i],
                A=A,
                rho=rho[i],
                cU=cU,
                I=I,
                e=e,
                g=g,
                theta=theta,
                avg=I / cU if cU else None,
                minpsi=minpsi,
                bad_point=bad_point,
                neigh=neigh,
                harvest=25 * rho[i] - 4 * e,
            )
        )
    return out


def fmtq(x):
    if x is None:
        return "None"
    return f"{float(x):.9f} = {x}"


def dump_record(rec, max_neigh=30):
    print("=" * 72)
    print(rec["name"], "n", rec["n"], "side", rec["side"], "o", rec["o"], "O", rec["O"])
    for k in ["a", "A", "rho", "cU", "I", "e", "g", "theta", "avg", "minpsi", "harvest"]:
        print(k, fmtq(rec[k]))
    print("pointwise_below_theta", len(rec["bad_point"]), "of", len(rec["neigh"]))
    below_c = sum(row["c"] for row in rec["bad_point"])
    below_I = sum(row["c"] * row["psi"] for row in rec["bad_point"])
    above = [row for row in rec["neigh"] if row not in rec["bad_point"]]
    above_c = sum(row["c"] for row in above)
    above_I = sum(row["c"] * row["psi"] for row in above)
    print("below_c", fmtq(below_c), "below_avg", fmtq(below_I / below_c if below_c else None))
    print("above_c", fmtq(above_c), "above_avg", fmtq(above_I / above_c if above_c else None))
    for row in sorted(rec["neigh"], key=lambda x: (x["psi"], x["u"]))[:max_neigh]:
        flag = "*" if rec["theta"] is not None and row["psi"] < rec["theta"] else " "
        print(
            flag,
            "u",
            row["u"],
            "c_o",
            fmtq(row["c"]),
            "psi",
            fmtq(row["psi"]),
            "d",
            fmtq(row["d"]),
            "cO",
            fmtq(row["cO"]),
            "cOtherO",
            fmtq(row["cOtherO"]),
            "cUU",
            fmtq(row["cUU"]),
            "rhs/den",
            fmtq(row["local_rhs_avg"]),
        )


def main():
    # Weak harvest blowup guardrail.
    n, edges = odd_blowup(5, [5, 4, 5, 4, 5])
    for _gamma, cuts in [gmins(n, edges)]:
        for side in cuts[:2]:
            for rec in analyze_cut("blow(5,4,5,4,5)", n, edges, side, focus=5):
                dump_record(rec)
                break
            break

    # High-ratio Mycielski guardrail.
    grN, grE = mycielski(5, Cn(5))
    n23, e23 = mycielski(grN, grE)
    adj23 = adj_from_edges(n23, e23)
    side23 = maxcut_ls(n23, adj23)
    for rec in analyze_cut("MycGrotzsch_N23", n23, e23, side23, focus=2):
        dump_record(rec)


if __name__ == "__main__":
    main()
