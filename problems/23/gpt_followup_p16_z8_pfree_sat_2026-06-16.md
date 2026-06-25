FOLLOW-UP: Your proposed P-free exact A/B-state verifier was implemented for the p16/eR21 z8 row.

Target:
- row z=8,s1=s2=0,d=6,p=16,e_R=21,cap=74
- category (ZZ,ZD)=(0,21)

Implementation included:
- labelled A states X_i (i=1..6) and B states Y_j (j=1..6), each independent in R
- exact M=sum_R m_r=74
- m_r<=8 and degree lower bounds
- root-colour visibility through D for every A/B vertex
- terminal equality for zeros with d_D(z)=2
- full R/R edge/nonedge codegree constraints
- exact A/B law: |X_i cap Y_j|=0 count is exactly p=16; |X_i cap Y_j|=1 forbidden
- A/B degree lower bounds using the induced exact A-B edge count per vertex
- A/A and B/B nonedge codegrees using induced A-B edges plus shared R-neighbours
- A/R and B/R nonedge codegrees using induced A-B edges plus R-neighbours

Result:
- CP-SAT found SAT for category (ZZ,ZD)=(0,21) in ~8 seconds.
- This is not a full graph witness, only a P-free state/skeleton survivor. It means the P-free exact-p verifier is not sufficient as stated.

Question:
What is the smallest missing constraint or next structural lemma for z8 p16? Please be adversarial. If the P-free exact A/B-state law is still valid, identify what additional condition it needs to eliminate this SAT survivor before fixed-P. If the SAT survivor indicates the approach is too weak, propose the next narrow finite certificate for z8 (preferably zero/D skeleton + state constraints), not broad fixed-P enumeration.

Please give concrete constraints/checks to add, and list the weakest assumptions.
