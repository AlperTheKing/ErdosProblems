# Independent replay certificate

Running python replay.py decodes K??E@cyjFgWk, invokes only pinned canonical row-family helpers (never MICRO_FLOW), and reconstructs the Gamma-minimum connected maximum cut, complete shortest-row families, choice [0,4,5,7], and tuple index 377.

The graph is triangle-free. Every selected shortest row has five vertices. Exact family sizes are [6,5,8,10]. result.json exports the graph, cut, raw Gamma, all families, selected rows, support, active structure, owner quantities, every ordered FreeHalf relation key and reason, ScopedReserved keys, a 65-edge injective assignment, alternating min-cut certificate, and all eight owner-shore cuts.

Raw demand is 28 + 25*2 = 78. Owners with positive demand are [7,10,11]; the maximum-defect shore is [10,11], with demand minus reachable ordered FreeHalves equal to 13. The explicit matching value is 65.

These are raw graph/matching quantities. FullBank sink capacity is capQ/25, but no capQ is used here. Ordered FreeHalf keys are not typed CapSource keys. No legal port incidence or checked FullBank ledger is constructed. Matching injectivity prevents reuse inside this raw assignment only; it does not establish FullBank no-double-spend or an aggregate FullBank repair.

Replay command: python replay.py
