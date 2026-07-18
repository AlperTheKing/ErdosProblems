#include <bits/stdc++.h>
using namespace std;

typedef int64_t ll;
typedef vector<ll> vl;
typedef vector<vl> vvl;

int main() {
	int maxSize = 100;
	vvl minf(maxSize, vl(maxSize, 1e18));
	minf[1][0] = 0;
	for (int size = 2; size < maxSize; size++) {
		ll lowestf = 1e18;
		for (int depth = 1; depth <= size; depth++) {
			for (int leftSize = 1; leftSize < size; leftSize++) {
				int rightSize = size-leftSize;
				for (int leftDepth = 0; leftDepth < depth; leftDepth++) {
					// prevent overflow , does not result in smallest anyway
					if (leftDepth+depth-1 > 61) continue;
					minf[size][depth] = min(minf[size][depth], 2*(minf[leftSize][leftDepth] + minf[rightSize][depth-1] + (1L<<(leftDepth+depth-1))));
				}
			}
			lowestf = min(lowestf, minf[size][depth]);
		}
		cout << size << " " << ceil(log2(lowestf)) << endl;
	}
	return 0;
}
