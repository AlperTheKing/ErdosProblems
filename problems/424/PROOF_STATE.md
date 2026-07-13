# Proof state

## Definition

`A` is the least positive-integer set containing 2 and 3 and closed under
`xy-1` for distinct inputs. The target is positive lower density.

## Accepted baseline

If every current element is 0 or 2 modulo 3, then `xy-1` is again 0 or 2
modulo 3. Since the seeds are 2 and 0 modulo 3, `A` omits residue 1 modulo
3 and has upper density at most 2/3.

For `n>3`, every factor in a representation `n+1=xy` with `x,y>=2` is
strictly smaller than `n`. Therefore ascending divisor recursion exactly
decides membership once the distinct-factor convention is enforced.

## Frontier

Pending the first computation and blind-agent wave.

