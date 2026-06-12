from pathlib import Path
root=Path(r'E:\Projects\ErdosProblems')
local=Path(r'E:\Projects\ErdosProblems\workers\codex\formal-conjectures\FormalConjectures\ErdosProblems\26.lean')
apn=root / r'apn-gpt55-workbench\alphaproof-nexus-results\APNOutputs\ErdosProblems\erdos_26.variants.tenenbaum.lean'
ls=local.read_text(encoding='utf-8')
as_=apn.read_text(encoding='utf-8')
open_start=as_.index('open MeasureTheory')
helper_start=as_.index('-- EVOLVE-BLOCK-START')
open_block=as_[open_start:helper_start].rstrip()+"\n\n"
helper_end=as_.index('-- EVOLVE-BLOCK-END', helper_start)
helper_block=as_[helper_start+len('-- EVOLVE-BLOCK-START'):helper_end].strip()+"\n\n"
options='''
set_option maxRecDepth 4000
set_option synthInstance.maxHeartbeats 20000
set_option synthInstance.maxSize 128
set_option maxHeartbeats 200000

'''
insert_block=options+open_block+helper_block
marker='''/--
Let $A\\subset\\mathbb{N}$ be infinite such that $\\sum_{a \\in A} \\frac{1}{a} = \\infty$. Must
'''
if 'lemma exists_x_P_ind' not in ls:
    if marker not in ls:
        raise SystemExit('insert marker not found')
    ls=ls.replace(marker, insert_block+marker, 1)
target='''theorem erdos_26.variants.tenenbaum : answer(False) ↔ ∀ᵉ (A : ℕ → ℕ), StrictMono A → IsThick A →
    (∀ ε > (0 : ℝ), ∃ k, IsWeaklyBehrend (A · + k) ε) := by
  sorry'''
proof='''theorem erdos_26.variants.tenenbaum : answer(False) ↔ ∀ᵉ (A : ℕ → ℕ), StrictMono A → IsThick A →
    (∀ ε > (0 : ℝ), ∃ k, IsWeaklyBehrend (A · + k) ε) := by
  constructor
  · intro h
    exact False.elim h
  · intro h
    have hA : StrictMono seqA := seqA_strict_mono
    have hT : IsThick seqA := seqA_thick
    have h_ex := h seqA hA hT (1/2 : ℝ) (by norm_num)
    rcases h_ex with ⟨k, hk⟩
    have h_not := not_weakly_behrend_seqA k
    exact h_not hk'''
if target not in ls:
    raise SystemExit('target proof pattern not found')
ls=ls.replace(target, proof, 1)
local.write_text(ls, encoding='utf-8', newline='\n')
