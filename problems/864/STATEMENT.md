# Erdos Problem 864

For A subseteq {1,...,N}, define

    r_A(s) = #{(a,b) : a,b in A, a <= b, a+b=s}.

A is admissible when at most one integer s has r_A(s) >= 2. The exceptional
sum, if present, may have arbitrarily many unordered representations. Diagonal
pairs a+a count.

Let

    F(N) = max{|A| : A subseteq {1,...,N} is admissible}.

Primary target:

    F(N) = (2/sqrt(3) + o(1)) sqrt(N).

Affirmative quantified form: for every epsilon>0 there is N0 such that every
N>=N0 and every admissible A satisfy

    |A| <= (2/sqrt(3)+epsilon)sqrt(N).

A disproof requires an explicit infinite admissible family with normalized
limsup strictly larger than 2/sqrt(3).

Official source: https://www.erdosproblems.com/864
OEIS: https://oeis.org/A389182
