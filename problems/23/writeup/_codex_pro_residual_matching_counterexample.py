"""Exact arithmetic falsifier to the proposed CollisionHalf matching repair.

The proposal matches two half-copies of each collision plus hit-only needs
into two half-copies of each free source, then gives every need slot a positive
token.  This permits a free source to cancel a collision debit and fund a token
simultaneously.  The official component ledger instead has spendable residual
Free - Collision, so the reuse is invalid.
"""

from fractions import Fraction
import json


def main() -> None:
    free = 1
    collision = 1
    hit_need = 0
    collision_charged_need = 1
    need = collision_charged_need + hit_need
    token_unit = Fraction(1, 2)
    residual_unit = Fraction(1, 25)

    proposed_domain = 2 * collision + hit_need
    proposed_codomain = 2 * free
    proposed_matching_exists = proposed_domain <= proposed_codomain
    counting_assignment_exists = need <= collision + hit_need

    residual_units = free - collision
    token_spend = need * token_unit
    residual_budget = residual_units * residual_unit

    assert proposed_matching_exists
    assert counting_assignment_exists
    assert residual_units == 0
    assert token_spend > residual_budget

    # Correct no-double-use condition: collision debits and token needs must
    # occupy disjoint positive sources.
    corrected_matching_exists = 2 * collision + 25 * need <= 2 * free
    assert not corrected_matching_exists

    # Independent scale-only obstruction: even without a collision debit,
    # twelve free ordered pairs cannot fund one half-unit endpoint token.
    scale_free = 12
    scale_collision = 0
    scale_need = 1
    scale_proposed_matching = scale_need <= 2 * scale_free
    scale_token_spend = Fraction(scale_need, 2)
    scale_residual_budget = Fraction(scale_free - scale_collision, 25)
    assert scale_proposed_matching
    assert scale_token_spend > scale_residual_budget

    print(json.dumps({
        "free": free,
        "collision": collision,
        "need": need,
        "proposedMatching": proposed_matching_exists,
        "tokenSpend": str(token_spend),
        "officialResidualBudget": str(residual_budget),
        "ledgerViolation": str(token_spend - residual_budget),
        "correctedCondition": "2*Collision + 25*Need <= 2*Free",
        "correctedMatching": corrected_matching_exists,
        "scaleCountermodel": {
            "free": scale_free,
            "collision": scale_collision,
            "need": scale_need,
            "proposedMatching": scale_proposed_matching,
            "tokenSpend": str(scale_token_spend),
            "officialResidualBudget": str(scale_residual_budget),
        },
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
