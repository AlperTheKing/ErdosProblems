An admissible fiber-refinement gadget

The following gives option 2: a proved refinement lemma and a fully specified instance. It does not yet produce the two global half-covers, but it gives an exact collision-removal operation for an admissible half-modulus. The underlying problem is still listed as open in the Erdős Problems catalogue. 
erdosproblems.com

Write a(n) for the congruence class a(modn).

Fiber-composition lemma

Let

Q={r
j
	​

(q
j
	​

):1≤j≤k}

be a covering system of Z, with the q
j
	​

 pairwise distinct. Let d≥1, b∈Z, and let F be a finite forbidden set of half-moduli. Suppose that, for every j,

e
j
	​

=dq
j
	​

∈
/
Fand2e
j
	​

+1 is prime.

Then

b(d)=
j=1
⋃
k
	​

(b+dr
j
	​

)(dq
j
	​

).
	​


Consequently, b(d) can be replaced by the child classes on the right. Their half-moduli are distinct, admissible, and avoid F.

Proof. If x∈b(d), write x=b+dt. Since Q covers Z, some j satisfies t≡r
j
	​

(modq
j
	​

), and hence

x=b+dt≡b+dr
j
	​

(moddq
j
	​

).

Conversely, every child class is contained in b(d), since d∣dq
j
	​

 and b+dr
j
	​

≡b(modd). Distinctness follows from the distinctness of the q
j
	​

. □

Fully specified instance

Use the distinct quotient covering system

Q={0(2), 0(3), 1(4), 5(6), 7(12)}.

Its exact coverage is seen modulo 12:

class
0(2)
0(3)
1(4)
5(6)
7(12)
	​

residues modulo 12
0,2,4,6,8,10
0,3,6,9
1,5,9
5,11
7
	​

	​


Thus every residue 0,…,11 occurs; this is a complete-period derivation, not a density argument.

Take

d=105525=3
2
⋅5
2
⋅7⋅67,b=0,

and prescribe the finite forbidden set

F={1,2,…,138600}.

The parent is admissible because

2d+1=211051

is prime. Applying the lemma gives the following five children:

q
2
3
4
6
12
	​

r
0
0
1
5
7
	​

e=dq
211050
316575
422100
633150
1266300
	​

a=dr
0
0
105525
527625
738675
	​

2e+1
422101
633151
844201
1266301
2532601
	​

	​


Hence the concrete identity is

0(mod105525)=
	​

(0(mod211050))∪(0(mod316575))
∪(105525(mod422100))
∪(527625(mod633150))
∪(738675(mod1266300)).
	​

	​


All five child half-moduli are distinct and exceed 138600, so they avoid F. In particular, they avoid every half-modulus occurring in any divisor-supported search with period 27720, 55440, or 138600.

Exact coverage over the full common period

The common period of the five child congruences is

L=lcm(211050,316575,422100,633150,1266300)=1266300=12d.

There are exactly twelve points of the parent fiber in one such period, namely x=dt for t=0,…,11. Their coverage is:

tmod12
0
1
2
3
4
5
6
7
8
9
10
11
	​

covering quotient class
0(2),0(3)
1(4)
0(2)
0(3)
0(2)
1(4),5(6)
0(2),0(3)
7(12)
0(2)
0(3),1(4)
0(2)
5(6)
	​

	​


Every child is contained in 0(105525), so this proves equality rather than merely one-sided coverage.

Exact primality certificates

For the parent prime and the five child primes, N−1 has the following complete factorization:

N
211051
422101
633151
844201
1266301
2532601
	​

N−1
2⋅3
2
⋅5
2
⋅7⋅67
2
2
⋅3
2
⋅5
2
⋅7⋅67
2⋅3
3
⋅5
2
⋅7⋅67
2
3
⋅3
2
⋅5
2
⋅7⋅67
2
2
⋅3
3
⋅5
2
⋅7⋅67
2
3
⋅3
3
⋅5
2
⋅7⋅67
	​

w
3
23
12
13
6
19
	​

	​


For each row, the listed w satisfies

w
N−1
≡1(modN)

and, for every q∈{2,3,5,7,67},

gcd(w
(N−1)/q
−1,N)=1.

Since 67 is prime and the entire factorization of N−1 is known, Pocklington’s theorem proves each N prime. The supplied verifier checks these certificates using exact integer modular arithmetic; it also independently checks primality by trial division through ⌊
N
	​

⌋, and checks the congruence equality over all 1,266,300 residues of the full common period.

erdos273_refinement_check.py

For either parity ε∈{0,1}, the corresponding operation on the original covering-system congruence is

2b+ε(mod2d)⟼2(b+dr
j
	​

)+ε(mod2dq
j
	​

),

so the five resulting original moduli are

422100, 633150, 844200, 1266300, 2532600,

and each is one less than the prime displayed in the table.
