use ehrcalc_kostka_engine::gt_dim::gt_polytope_dim;
use ehrcalc_kostka_engine::Partition;
use num_bigint::{BigInt, BigUint, ToBigInt};
use num_rational::BigRational;
use num_traits::{One, Zero};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

pub const SCHEMA_VERSION: u32 = 1;
pub const EXHAUSTIVE_MAX_SIZE: u32 = 12;
pub const EXHAUSTIVE_MAX_LENGTH: usize = 6;
pub const ADVERSARIAL_MAX_SIZE: u32 = 40;
pub const ADVERSARIAL_MAX_LENGTH: usize = 8;
pub const ADVERSARIAL_COUNT: usize = 50_000;
pub const DEFAULT_SEED: u64 = 0x4b54_542d_4b4f_5354;
pub const PINNED_EHRCALC_COMMIT: &str = "51c0606810b37944043952fcbe5b3e41d7123273";

#[derive(Clone, Debug, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct Instance {
    pub lambda: Vec<u32>,
    pub beta: Vec<u32>,
    pub weight: Vec<u32>,
}

impl Instance {
    pub fn key(&self) -> String {
        fn join(parts: &[u32]) -> String {
            parts
                .iter()
                .map(u32::to_string)
                .collect::<Vec<_>>()
                .join(",")
        }
        format!(
            "{}|{}|{}",
            join(&self.lambda),
            join(&self.beta),
            join(&self.weight)
        )
    }

    pub fn outer_size(&self) -> u32 {
        self.lambda.iter().sum()
    }

    pub fn skew_size(&self) -> u32 {
        self.outer_size() - self.beta.iter().sum::<u32>()
    }

    pub fn certified_dimension(&self) -> Option<usize> {
        gt_polytope_dim(&self.lambda, &self.beta, &self.weight)
    }

    pub fn validate(&self, max_size: u32, max_length: usize) -> Result<(), String> {
        if self.lambda.is_empty() {
            return Err("lambda is empty".to_owned());
        }
        if self.outer_size() > max_size {
            return Err(format!("|lambda|={} exceeds {max_size}", self.outer_size()));
        }
        if self.lambda.len() > max_length
            || self.beta.len() > max_length
            || self.weight.len() > max_length
        {
            return Err("length bound exceeded".to_owned());
        }
        if !is_partition(&self.lambda) || !is_partition(&self.beta) || !is_partition(&self.weight) {
            return Err("lambda, beta, and weight must be canonical partitions".to_owned());
        }
        if self.weight.is_empty() || self.skew_size() == 0 {
            return Err("skew shape and weight must be nonempty".to_owned());
        }
        if self.skew_size() != self.weight.iter().sum::<u32>() {
            return Err("skew size and weight size differ".to_owned());
        }
        for i in 0..self.lambda.len().max(self.beta.len()) {
            let l = self.lambda.get(i).copied().unwrap_or(0);
            let b = self.beta.get(i).copied().unwrap_or(0);
            if b > l {
                return Err("beta is not contained in lambda".to_owned());
            }
        }
        Ok(())
    }
}

pub fn exhaustive_instances() -> Vec<Instance> {
    let mut instances = Vec::new();
    for outer_size in 1..=EXHAUSTIVE_MAX_SIZE {
        for lambda in Partition::all_of_size_bounded(outer_size, EXHAUSTIVE_MAX_LENGTH, outer_size)
        {
            for beta_size in 0..outer_size {
                let betas = if beta_size == 0 {
                    vec![Partition::empty()]
                } else {
                    Partition::all_of_size_bounded(beta_size, lambda.num_parts(), lambda.part(0))
                };
                for beta in betas {
                    if !beta.partition_less_equal(&lambda) {
                        continue;
                    }
                    let skew_size = outer_size - beta_size;
                    for weight in
                        Partition::all_of_size_bounded(skew_size, EXHAUSTIVE_MAX_LENGTH, skew_size)
                    {
                        instances.push(Instance {
                            lambda: lambda.parts().to_vec(),
                            beta: beta.parts().to_vec(),
                            weight: weight.parts().to_vec(),
                        });
                    }
                }
            }
        }
    }
    instances
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct SplitMix64 {
    state: u64,
}

impl SplitMix64 {
    pub fn new(seed: u64) -> Self {
        Self { state: seed }
    }

    pub fn next_u64(&mut self) -> u64 {
        self.state = self.state.wrapping_add(0x9e37_79b9_7f4a_7c15);
        let mut z = self.state;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
        z ^ (z >> 31)
    }

    pub fn below(&mut self, upper: u64) -> u64 {
        assert!(upper > 0);
        let zone = u64::MAX - u64::MAX % upper;
        loop {
            let value = self.next_u64();
            if value < zone {
                return value % upper;
            }
        }
    }

    pub fn inclusive(&mut self, low: u32, high: u32) -> u32 {
        assert!(low <= high);
        low + self.below(u64::from(high - low) + 1) as u32
    }
}

pub fn adversarial_instances(count: usize, seed: u64) -> Vec<Instance> {
    let mut rng = SplitMix64::new(seed);
    let mut seen = HashSet::with_capacity(count * 2);
    let mut result = Vec::with_capacity(count);
    let draw_limit = count.saturating_mul(2_000).max(10_000);

    for _draw in 0..draw_limit {
        if result.len() == count {
            break;
        }
        let Some(instance) = adversarial_draw(&mut rng) else {
            continue;
        };
        let key = instance.key();
        if seen.insert(key) {
            result.push(instance);
        }
    }
    assert_eq!(
        result.len(),
        count,
        "deterministic adversarial generator exhausted its draw budget"
    );
    result
}

fn adversarial_draw(rng: &mut SplitMix64) -> Option<Instance> {
    // Keep this bounded family disjoint from the exhaustive |lambda|<=12 stage.
    // Most draws are large and use many rows/labels to bias toward higher-dimensional,
    // irregular skew GT slices rather than multiplicity-one cases.
    let outer_size = if rng.below(10) < 8 {
        rng.inclusive(28, ADVERSARIAL_MAX_SIZE)
    } else {
        rng.inclusive(13, 27)
    };
    let rows = rng.inclusive(3, ADVERSARIAL_MAX_LENGTH as u32) as usize;
    let mut lambda = vec![1u32; rows];
    for _ in rows as u32..outer_size {
        let row = rng.below(rows as u64) as usize;
        lambda[row] += 1;
    }
    lambda.sort_unstable_by(|a, b| b.cmp(a));

    let labels = rng.inclusive(4, ADVERSARIAL_MAX_LENGTH as u32) as usize;
    let mut outer = lambda.clone();
    let mut strip_sizes = Vec::with_capacity(labels);
    for step in 0..labels {
        if outer.is_empty() {
            return None;
        }
        let mut inner = Vec::with_capacity(outer.len());
        for i in 0..outer.len() {
            let lower = outer.get(i + 1).copied().unwrap_or(0);
            inner.push(rng.inclusive(lower, outer[i]));
        }
        while inner.last() == Some(&0) {
            inner.pop();
        }
        if inner == outer {
            let last = outer.len() - 1;
            inner = outer.clone();
            inner[last] -= 1;
            while inner.last() == Some(&0) {
                inner.pop();
            }
        }
        if inner.is_empty() && step + 1 < labels {
            return None;
        }
        let removed = outer.iter().sum::<u32>() - inner.iter().sum::<u32>();
        if removed == 0 {
            return None;
        }
        strip_sizes.push(removed);
        outer = inner;
    }
    if outer.is_empty() {
        return None;
    }
    strip_sizes.sort_unstable_by(|a, b| b.cmp(a));
    let instance = Instance {
        lambda,
        beta: outer,
        weight: strip_sizes,
    };
    if instance
        .validate(ADVERSARIAL_MAX_SIZE, ADVERSARIAL_MAX_LENGTH)
        .is_err()
    {
        return None;
    }
    // Dimensions 0--2 cannot supply the intended difficult Ehrhart geometry.
    // This cheap exact filter makes the fixed sample adversarial without any
    // coefficient-dependent selection.
    if instance.certified_dimension()? < 3 {
        return None;
    }
    Some(instance)
}

fn is_partition(parts: &[u32]) -> bool {
    !parts.contains(&0) && parts.windows(2).all(|pair| pair[0] >= pair[1])
}

/// Interpolate exact values P(0),...,P(U) in the ordinary monomial basis.
///
/// This deliberately does not use the vendor dimension routine as an
/// interpolation bound. It expands the Newton series
/// `sum_k Delta^k P(0) * binom(n,k)` over Q.
pub fn interpolate_consecutive(values: &[BigUint]) -> Vec<BigRational> {
    assert!(!values.is_empty());
    let mut layer: Vec<BigInt> = values
        .iter()
        .map(|value| value.to_bigint().unwrap())
        .collect();
    let mut result = vec![BigRational::zero(); values.len()];
    let mut binomial_basis = vec![BigRational::one()];

    for order in 0..values.len() {
        let delta = BigRational::from(layer[0].clone());
        for (index, coefficient) in binomial_basis.iter().enumerate() {
            result[index] += &delta * coefficient;
        }
        if order + 1 == values.len() {
            break;
        }
        layer = layer.windows(2).map(|pair| &pair[1] - &pair[0]).collect();

        // binom(n,order+1) = binom(n,order)*(n-order)/(order+1).
        let denominator = BigRational::from(BigInt::from(order + 1));
        let shift = BigRational::from(BigInt::from(order));
        let mut next = vec![BigRational::zero(); binomial_basis.len() + 1];
        for (index, coefficient) in binomial_basis.iter().enumerate() {
            next[index] -= coefficient * &shift / &denominator;
            next[index + 1] += coefficient / &denominator;
        }
        binomial_basis = next;
    }
    trim_power_coefficients(result)
}

pub fn trim_power_coefficients(mut coefficients: Vec<BigRational>) -> Vec<BigRational> {
    while coefficients.len() > 1 && coefficients.last().is_some_and(Zero::is_zero) {
        coefficients.pop();
    }
    coefficients
}

pub fn evaluate_power(coefficients: &[BigRational], n: u64) -> BigRational {
    let n = BigRational::from(BigInt::from(n));
    coefficients
        .iter()
        .rev()
        .fold(BigRational::zero(), |value, coefficient| {
            value * &n + coefficient
        })
}

pub fn rigorous_degree_bound(instance: &Instance) -> usize {
    instance
        .weight
        .len()
        .saturating_sub(1)
        .saturating_mul(instance.lambda.len().saturating_sub(1))
}

#[cfg(test)]
mod tests {
    use super::*;
    use ehrcalc_kostka_engine::kostka_dp::skew_kostka;
    use num_traits::Zero;

    fn dilated_count(instance: &Instance, dilation: u32) -> BigUint {
        let lambda =
            Partition::from_sorted(instance.lambda.iter().map(|part| part * dilation).collect());
        let beta =
            Partition::from_sorted(instance.beta.iter().map(|part| part * dilation).collect());
        let weight: Vec<u32> = instance.weight.iter().map(|part| part * dilation).collect();
        skew_kostka(&lambda, &beta, &weight, None, true)
    }

    #[test]
    fn splitmix64_reference_vector() {
        let mut rng = SplitMix64::new(0);
        assert_eq!(rng.next_u64(), 0xe220_a839_7b1d_cdaf);
        assert_eq!(rng.next_u64(), 0x6e78_9e6a_a1b9_65f4);
        assert_eq!(rng.next_u64(), 0x06c4_5d18_8009_454f);
        assert_eq!(rng.next_u64(), 0xf88b_b8a8_724c_81ec);
        assert_eq!(rng.next_u64(), 0x1b39_896a_51a8_749b);
    }

    #[test]
    fn exhaustive_enumeration_is_canonical_and_complete() {
        let instances = exhaustive_instances();
        assert_eq!(instances.len(), 69_218);
        let unique: HashSet<_> = instances.iter().map(Instance::key).collect();
        assert_eq!(unique.len(), instances.len());
        for instance in instances {
            instance
                .validate(EXHAUSTIVE_MAX_SIZE, EXHAUSTIVE_MAX_LENGTH)
                .unwrap();
        }
    }

    #[test]
    fn adversarial_generator_is_reproducible_unique_and_nonzero() {
        let left = adversarial_instances(256, DEFAULT_SEED);
        let right = adversarial_instances(256, DEFAULT_SEED);
        assert_eq!(left, right);
        let unique: HashSet<_> = left.iter().map(Instance::key).collect();
        assert_eq!(unique.len(), left.len());
        for instance in &left {
            instance
                .validate(ADVERSARIAL_MAX_SIZE, ADVERSARIAL_MAX_LENGTH)
                .unwrap();
            assert!(instance.outer_size() > EXHAUSTIVE_MAX_SIZE);
            assert!(instance.certified_dimension().unwrap() >= 3);
        }
        for instance in left.iter().take(32) {
            let lambda = Partition::from_sorted(instance.lambda.clone());
            let beta = Partition::from_sorted(instance.beta.clone());
            let value = skew_kostka(&lambda, &beta, &instance.weight, None, true);
            assert!(
                !value.is_zero(),
                "constructed zero instance: {}",
                instance.key()
            );
        }
    }

    #[test]
    #[ignore = "full 50,000-row deterministic schedule audit"]
    fn full_adversarial_schedule_has_contract_size() {
        let instances = adversarial_instances(ADVERSARIAL_COUNT, DEFAULT_SEED);
        assert_eq!(instances.len(), ADVERSARIAL_COUNT);
        let unique: HashSet<_> = instances.iter().map(Instance::key).collect();
        assert_eq!(unique.len(), ADVERSARIAL_COUNT);
    }

    #[test]
    fn consecutive_interpolation_round_trip() {
        // P(n)=(n^3+6n^2+11n+6)/6.
        let values: Vec<BigUint> = (0u32..=6)
            .map(|n| BigUint::from(((n + 1) * (n + 2) * (n + 3) / 6) as u64))
            .collect();
        let coefficients = interpolate_consecutive(&values);
        assert_eq!(coefficients.len(), 4);
        for (n, value) in values.iter().enumerate() {
            assert_eq!(
                evaluate_power(&coefficients, n as u64).to_integer(),
                value.to_bigint().unwrap()
            );
        }
    }

    #[test]
    fn stale_readme_skew_sample_has_degree_eight_and_constant_one() {
        let instance = Instance {
            lambda: vec![4, 3, 2, 1],
            beta: vec![2, 1],
            weight: vec![2, 2, 2, 1],
        };
        let bound = rigorous_degree_bound(&instance);
        assert_eq!(bound, 9);
        let values: Vec<BigUint> = (0..=bound as u32)
            .map(|n| dilated_count(&instance, n))
            .collect();
        let coefficients = interpolate_consecutive(&values);
        assert_eq!(coefficients.len() - 1, 8);
        assert_eq!(instance.certified_dimension(), Some(8));
        assert_eq!(coefficients[0], BigRational::one());
        for n in [bound as u32 + 1, bound as u32 + 2] {
            let direct = dilated_count(&instance, n);
            assert_eq!(
                evaluate_power(&coefficients, u64::from(n)).to_integer(),
                direct.to_bigint().unwrap()
            );
        }
    }
}
