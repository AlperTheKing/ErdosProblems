use ehrcalc_kostka_engine::kostka_dp::skew_kostka_stats;
use ehrcalc_kostka_engine::Partition;
use fs2::FileExt;
use ktt_kostka_gate::{
    adversarial_instances, evaluate_power, exhaustive_instances, interpolate_consecutive,
    rigorous_degree_bound, Instance, ADVERSARIAL_COUNT, ADVERSARIAL_MAX_LENGTH,
    ADVERSARIAL_MAX_SIZE, DEFAULT_SEED, EXHAUSTIVE_MAX_LENGTH, EXHAUSTIVE_MAX_SIZE,
    PINNED_EHRCALC_COMMIT, SCHEMA_VERSION,
};
use num_bigint::{BigInt, BigUint, ToBigInt};
use num_rational::BigRational;
use num_traits::{One, Zero};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::any::Any;
use std::env;
use std::fs::{self, File, OpenOptions};
use std::io::{self, BufWriter, Read, Seek, SeekFrom, Write};
use std::panic::{self, AssertUnwindSafe};
use std::path::{Path, PathBuf};
use std::process::{self, Command};
use std::time::{SystemTime, UNIX_EPOCH};

const DEFAULT_MAX_STATES: usize = 2_000_000;
const DEFAULT_MAX_CERTIFIED_DIMENSION: usize = 49;
const DEFAULT_CHECKPOINT_EVERY: usize = 100;

#[derive(Debug)]
struct Args {
    output_dir: PathBuf,
    resume: bool,
    max_states: usize,
    max_certified_dimension: usize,
    checkpoint_every: usize,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
struct RunConfig {
    schema_version: u32,
    binary_sha256: String,
    vendor_ehrcalc_commit: String,
    seed: u64,
    exhaustive_max_size: u32,
    exhaustive_max_length: usize,
    adversarial_count: usize,
    adversarial_max_size: u32,
    adversarial_max_length: usize,
    exhaustive_schedule_sha256: String,
    adversarial_schedule_sha256: String,
    combined_schedule_sha256: String,
    max_states_per_dp_level: usize,
    max_certified_dimension: usize,
    rayon_threads: usize,
    interpolation_rule: String,
    held_out_rule: String,
}

#[derive(Clone, Debug)]
struct ScheduledInstance {
    sequence: usize,
    source: &'static str,
    source_index: usize,
    instance: Instance,
    instance_id: String,
}

#[derive(Debug)]
struct Schedule {
    rows: Vec<ScheduledInstance>,
    exhaustive_sha256: String,
    adversarial_sha256: String,
    combined_sha256: String,
}

#[derive(Clone, Debug)]
struct RecoveredRecord {
    instance_id: String,
    source: String,
    source_index: usize,
    instance: Instance,
}

#[derive(Clone, Debug, Default, Deserialize, Serialize)]
struct Stats {
    processed_records: u64,
    exhaustive_records: u64,
    adversarial_records: u64,
    eligible_nonzero: u64,
    excluded_zero: u64,
    screened_nonnegative: u64,
    negative_candidates: u64,
    resource_errors: u64,
    skipped_policy: u64,
    invariant_errors: u64,
}

impl Stats {
    fn apply(&mut self, record: &Value) -> Result<(), String> {
        self.processed_records += 1;
        match record.get("source").and_then(Value::as_str) {
            Some("exhaustive") => self.exhaustive_records += 1,
            Some("adversarial") => self.adversarial_records += 1,
            other => return Err(format!("invalid record source: {other:?}")),
        }
        if record
            .get("base_nonzero")
            .and_then(Value::as_bool)
            .unwrap_or(false)
        {
            self.eligible_nonzero += 1;
        }
        match record.get("status").and_then(Value::as_str) {
            Some("excluded_zero") => self.excluded_zero += 1,
            Some("screened_nonnegative") => self.screened_nonnegative += 1,
            Some("negative_candidate") => self.negative_candidates += 1,
            Some("resource_error") => self.resource_errors += 1,
            Some("skipped_policy") => self.skipped_policy += 1,
            Some("invariant_error") => self.invariant_errors += 1,
            other => return Err(format!("invalid record status: {other:?}")),
        }
        Ok(())
    }

    fn screened(&self) -> u64 {
        self.screened_nonnegative + self.negative_candidates
    }
}

#[derive(Debug)]
struct CountAt {
    value: BigUint,
    peak_states: usize,
}

#[derive(Debug)]
enum CountFailure {
    Resource(String),
    Invalid(String),
}

#[derive(Debug)]
enum StopReason {
    Negative,
    Invariant,
}

fn main() {
    // Windows gives the process main thread a much smaller default stack than
    // Rust's test threads.  The exact partition/dimension routines are
    // recursive, so execute the frozen scanner on an explicitly bounded stack
    // that is recorded here rather than depending on a platform linker default.
    let worker = match std::thread::Builder::new()
        .name("ktt-kostka-gate".to_owned())
        .stack_size(64 * 1024 * 1024)
        .spawn(run)
    {
        Ok(worker) => worker,
        Err(error) => {
            eprintln!("fatal: cannot start scanner worker: {error}");
            process::exit(2);
        }
    };
    let exit_code = match worker.join() {
        Ok(Ok(code)) => code,
        Ok(Err(error)) => {
            eprintln!("fatal: {error}");
            2
        }
        Err(payload) => panic::resume_unwind(payload),
    };
    process::exit(exit_code);
}

fn run() -> Result<i32, String> {
    let args = parse_args()?;
    if env::var_os("RAYON_NUM_THREADS").is_none() {
        env::set_var("RAYON_NUM_THREADS", "1");
    } else if env::var("RAYON_NUM_THREADS").ok().as_deref() != Some("1") {
        return Err("RAYON_NUM_THREADS must be unset or equal to 1".to_owned());
    }
    verify_vendor_commit()?;
    let binary_sha256 = hash_file(&env::current_exe().map_err(io_error)?)?;
    eprintln!("generating the deterministic candidate schedule...");
    let schedule_contract = build_schedule()?;
    let schedule = &schedule_contract.rows;
    let config = RunConfig {
        schema_version: SCHEMA_VERSION,
        binary_sha256,
        vendor_ehrcalc_commit: PINNED_EHRCALC_COMMIT.to_owned(),
        seed: DEFAULT_SEED,
        exhaustive_max_size: EXHAUSTIVE_MAX_SIZE,
        exhaustive_max_length: EXHAUSTIVE_MAX_LENGTH,
        adversarial_count: ADVERSARIAL_COUNT,
        adversarial_max_size: ADVERSARIAL_MAX_SIZE,
        adversarial_max_length: ADVERSARIAL_MAX_LENGTH,
        exhaustive_schedule_sha256: schedule_contract.exhaustive_sha256.clone(),
        adversarial_schedule_sha256: schedule_contract.adversarial_sha256.clone(),
        combined_schedule_sha256: schedule_contract.combined_sha256.clone(),
        max_states_per_dp_level: args.max_states,
        max_certified_dimension: args.max_certified_dimension,
        rayon_threads: 1,
        interpolation_rule:
            "exact counts n=0..U, U=(ell(weight)-1)(ell(lambda)-1); exact Newton interpolation"
                .to_owned(),
        held_out_rule: "direct exact counts at U+1 and U+2".to_owned(),
    };
    let config_bytes = serde_json::to_vec(&config).map_err(json_error)?;
    let config_sha256 = hash_bytes(&config_bytes);

    prepare_output(&args.output_dir, args.resume, &config, &config_sha256)?;
    let lock_path = args.output_dir.join("run.lock");
    let lock_file = OpenOptions::new()
        .create(true)
        .truncate(false)
        .read(true)
        .write(true)
        .open(&lock_path)
        .map_err(io_error)?;
    lock_file
        .try_lock_exclusive()
        .map_err(|error| format!("another scanner holds {}: {error}", lock_path.display()))?;

    let records_path = args.output_dir.join("records.jsonl");
    let (recovered, mut stats) = recover_records(&records_path, &config_sha256)?;
    if recovered.len() > schedule.len() {
        return Err("records contain more rows than the deterministic schedule".to_owned());
    }
    for (index, recorded) in recovered.iter().enumerate() {
        let expected = &schedule[index];
        if recorded.instance_id != expected.instance_id
            || recorded.source != expected.source
            || recorded.source_index != expected.source_index
            || recorded.instance != expected.instance
        {
            return Err(format!(
                "resume schedule mismatch at sequence {index}: record={recorded:?}, expected_id={}",
                expected.instance_id
            ));
        }
    }

    if stats.negative_candidates > 0 || stats.invariant_errors > 0 {
        let state = if stats.negative_candidates > 0 {
            "negative_candidate_recorded"
        } else {
            "invariant_failure"
        };
        let records_sha256 = hash_file(&records_path)?;
        write_checkpoint_and_summary(
            &args.output_dir,
            &config,
            &config_sha256,
            &stats,
            schedule.len(),
            state,
            Some(&records_sha256),
        )?;
        return Ok(if stats.negative_candidates > 0 { 10 } else { 4 });
    }

    let records_file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&records_path)
        .map_err(io_error)?;
    let mut records = BufWriter::new(records_file);
    let negative_path = args.output_dir.join("negative_candidates.jsonl");
    let mut stop_reason = None;

    write_checkpoint_and_summary(
        &args.output_dir,
        &config,
        &config_sha256,
        &stats,
        schedule.len(),
        "running",
        None,
    )?;

    for scheduled in schedule.iter().skip(recovered.len()) {
        let record = screen(scheduled, &config, &config_sha256);
        let status = record
            .get("status")
            .and_then(Value::as_str)
            .ok_or_else(|| "generated record is missing status".to_owned())?;

        if status == "negative_candidate" {
            append_synced_json_line(&negative_path, &record)?;
        }
        append_json_line(&mut records, &record)?;
        stats.apply(&record)?;

        if status == "negative_candidate" {
            stop_reason = Some(StopReason::Negative);
        } else if status == "invariant_error" {
            stop_reason = Some(StopReason::Invariant);
        }

        if (stats.processed_records as usize).is_multiple_of(args.checkpoint_every)
            || stop_reason.is_some()
        {
            records.flush().map_err(io_error)?;
            records.get_ref().sync_data().map_err(io_error)?;
            let state = match stop_reason {
                Some(StopReason::Negative) => "negative_candidate_recorded",
                Some(StopReason::Invariant) => "invariant_failure",
                None => "running",
            };
            write_checkpoint_and_summary(
                &args.output_dir,
                &config,
                &config_sha256,
                &stats,
                schedule.len(),
                state,
                None,
            )?;
            eprintln!(
                "checkpoint: {}/{} records, {} screened, {} resource errors",
                stats.processed_records,
                schedule.len(),
                stats.screened(),
                stats.resource_errors
            );
        }
        if stop_reason.is_some() {
            break;
        }
    }

    records.flush().map_err(io_error)?;
    records.get_ref().sync_all().map_err(io_error)?;
    let records_sha256 = hash_file(&records_path)?;
    let all_processed = stats.processed_records as usize == schedule.len();
    let final_state = match stop_reason {
        Some(StopReason::Negative) => "negative_candidate_recorded",
        Some(StopReason::Invariant) => "invariant_failure",
        None if !all_processed => "interrupted",
        None if stats.resource_errors > 0 || stats.skipped_policy > 0 => {
            "bounded_gate_incomplete_resource_or_policy_skips"
        }
        None => "bounded_gate_complete_no_negative",
    };
    write_checkpoint_and_summary(
        &args.output_dir,
        &config,
        &config_sha256,
        &stats,
        schedule.len(),
        final_state,
        Some(&records_sha256),
    )?;

    Ok(match stop_reason {
        Some(StopReason::Negative) => 10,
        Some(StopReason::Invariant) => 4,
        None if stats.resource_errors > 0 || stats.skipped_policy > 0 => 3,
        None => 0,
    })
}

fn parse_args() -> Result<Args, String> {
    let mut output_dir = None;
    let mut resume = false;
    let mut max_states = DEFAULT_MAX_STATES;
    let mut max_certified_dimension = DEFAULT_MAX_CERTIFIED_DIMENSION;
    let mut checkpoint_every = DEFAULT_CHECKPOINT_EVERY;
    let mut arguments = env::args().skip(1);
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output-dir" => {
                output_dir = Some(PathBuf::from(
                    arguments
                        .next()
                        .ok_or_else(|| "--output-dir requires a path".to_owned())?,
                ));
            }
            "--resume" => resume = true,
            "--max-states" => {
                max_states = parse_positive(&argument, arguments.next())?;
            }
            "--max-certified-dimension" => {
                max_certified_dimension = parse_positive(&argument, arguments.next())?;
            }
            "--checkpoint-every" => {
                checkpoint_every = parse_positive(&argument, arguments.next())?;
            }
            "-h" | "--help" => {
                println!(
                    "ktt-kostka-gate --output-dir PATH [--resume] \\\n+                     [--max-states N] [--max-certified-dimension N] \\\n+                     [--checkpoint-every N]\n\nThe contract fixes the exhaustive bounds, seed, and adversarial count at 50,000."
                );
                process::exit(0);
            }
            other => return Err(format!("unknown argument: {other}")),
        }
    }
    Ok(Args {
        output_dir: output_dir.ok_or_else(|| "--output-dir is required".to_owned())?,
        resume,
        max_states,
        max_certified_dimension,
        checkpoint_every,
    })
}

fn parse_positive(flag: &str, value: Option<String>) -> Result<usize, String> {
    let parsed = value
        .ok_or_else(|| format!("{flag} requires an integer"))?
        .parse::<usize>()
        .map_err(|error| format!("invalid {flag}: {error}"))?;
    if parsed == 0 {
        return Err(format!("{flag} must be positive"));
    }
    Ok(parsed)
}

fn build_schedule() -> Result<Schedule, String> {
    let exhaustive = exhaustive_instances();
    if exhaustive.len() != 69_218 {
        return Err(format!(
            "exhaustive enumerator drift: got {}, expected 69218",
            exhaustive.len()
        ));
    }
    let adversarial = adversarial_instances(ADVERSARIAL_COUNT, DEFAULT_SEED);
    if adversarial.len() != ADVERSARIAL_COUNT {
        return Err("adversarial generator did not return exactly 50,000 instances".to_owned());
    }
    let mut schedule = Vec::with_capacity(exhaustive.len() + adversarial.len());
    let mut exhaustive_hasher = Sha256::new();
    let mut adversarial_hasher = Sha256::new();
    let mut combined_hasher = Sha256::new();
    for (source, instances) in [("exhaustive", exhaustive), ("adversarial", adversarial)] {
        for (source_index, instance) in instances.into_iter().enumerate() {
            let sequence = schedule.len();
            let instance_id = hash_bytes(instance.key().as_bytes());
            let line = format!("{source}\t{source_index}\t{}\n", instance.key());
            if source == "exhaustive" {
                exhaustive_hasher.update(line.as_bytes());
            } else {
                adversarial_hasher.update(line.as_bytes());
            }
            combined_hasher.update(line.as_bytes());
            schedule.push(ScheduledInstance {
                sequence,
                source,
                source_index,
                instance,
                instance_id,
            });
        }
    }
    Ok(Schedule {
        rows: schedule,
        exhaustive_sha256: format!("{:x}", exhaustive_hasher.finalize()),
        adversarial_sha256: format!("{:x}", adversarial_hasher.finalize()),
        combined_sha256: format!("{:x}", combined_hasher.finalize()),
    })
}

fn screen(scheduled: &ScheduledInstance, config: &RunConfig, config_sha256: &str) -> Value {
    let base = base_record(scheduled, config_sha256);
    let max_size = if scheduled.source == "exhaustive" {
        EXHAUSTIVE_MAX_SIZE
    } else {
        ADVERSARIAL_MAX_SIZE
    };
    let max_length = if scheduled.source == "exhaustive" {
        EXHAUSTIVE_MAX_LENGTH
    } else {
        ADVERSARIAL_MAX_LENGTH
    };
    if let Err(detail) = scheduled.instance.validate(max_size, max_length) {
        return merge(
            base,
            json!({
                "status": "invariant_error",
                "base_nonzero": false,
                "detail": format!("candidate validation failed: {detail}")
            }),
        );
    }

    let base_count = match count_at(&scheduled.instance, 1, config.max_states_per_dp_level) {
        Ok(result) => result,
        Err(failure) => return failure_record(base, failure, "base_count", 1, false),
    };
    if base_count.value.is_zero() {
        if scheduled.source == "adversarial" {
            return merge(
                base,
                json!({
                    "status": "invariant_error",
                    "base_nonzero": false,
                    "base_count": "0",
                    "base_peak_states": base_count.peak_states,
                    "detail": "constructive adversarial generator produced a zero instance"
                }),
            );
        }
        return merge(
            base,
            json!({
                "status": "excluded_zero",
                "base_nonzero": false,
                "base_count": "0",
                "base_peak_states": base_count.peak_states
            }),
        );
    }

    let bound = rigorous_degree_bound(&scheduled.instance);
    let dimension = match scheduled.instance.certified_dimension() {
        Some(dimension) => dimension,
        None => {
            return merge(
                base,
                json!({
                    "status": "invariant_error",
                    "base_nonzero": true,
                    "base_count": base_count.value.to_string(),
                    "detail": "positive base count but dimension routine returned empty"
                }),
            );
        }
    };
    if dimension > bound {
        return merge(
            base,
            json!({
                "status": "invariant_error",
                "base_nonzero": true,
                "base_count": base_count.value.to_string(),
                "rigorous_degree_bound": bound,
                "certified_dimension": dimension,
                "detail": "certified dimension exceeds the rigorous ambient degree bound"
            }),
        );
    }
    if dimension > config.max_certified_dimension {
        return merge(
            base,
            json!({
                "status": "skipped_policy",
                "base_nonzero": true,
                "base_count": base_count.value.to_string(),
                "rigorous_degree_bound": bound,
                "certified_dimension": dimension,
                "detail": "certified dimension exceeds configured safety policy"
            }),
        );
    }

    let mut values = Vec::with_capacity(bound + 1);
    let mut interpolation_counts = Vec::with_capacity(bound + 1);
    let mut peak_states = base_count.peak_states;
    for dilation in 0..=bound {
        let count = if dilation == 1 {
            CountAt {
                value: base_count.value.clone(),
                peak_states: base_count.peak_states,
            }
        } else {
            match count_at(
                &scheduled.instance,
                dilation as u64,
                config.max_states_per_dp_level,
            ) {
                Ok(result) => result,
                Err(failure) => {
                    return failure_record(base, failure, "interpolation_count", dilation, true)
                }
            }
        };
        peak_states = peak_states.max(count.peak_states);
        interpolation_counts.push(count.value.to_string());
        values.push(count.value);
    }
    if values.first() != Some(&BigUint::one()) {
        return merge(
            base,
            json!({
                "status": "invariant_error",
                "base_nonzero": true,
                "rigorous_degree_bound": bound,
                "certified_dimension": dimension,
                "interpolation_counts": interpolation_counts,
                "detail": "P(0) != 1"
            }),
        );
    }

    let coefficients = interpolate_consecutive(&values);
    let trimmed_degree = coefficients.len() - 1;
    if trimmed_degree != dimension {
        return merge(
            base,
            json!({
                "status": "invariant_error",
                "base_nonzero": true,
                "rigorous_degree_bound": bound,
                "certified_dimension": dimension,
                "trimmed_degree": trimmed_degree,
                "interpolation_counts": interpolation_counts,
                "power_coefficients": rational_strings(&coefficients),
                "detail": "trimmed exact degree differs from independently computed intrinsic dimension"
            }),
        );
    }

    let mut held_out = Vec::with_capacity(2);
    for dilation in [bound + 1, bound + 2] {
        let count = if dilation == 1 {
            CountAt {
                value: base_count.value.clone(),
                peak_states: base_count.peak_states,
            }
        } else {
            match count_at(
                &scheduled.instance,
                dilation as u64,
                config.max_states_per_dp_level,
            ) {
                Ok(result) => result,
                Err(failure) => {
                    return failure_record(base, failure, "held_out_count", dilation, true)
                }
            }
        };
        peak_states = peak_states.max(count.peak_states);
        let predicted = evaluate_power(&coefficients, dilation as u64);
        if predicted.denom() != &BigInt::one()
            || predicted.to_integer() != count.value.to_bigint().unwrap()
        {
            return merge(
                base,
                json!({
                    "status": "invariant_error",
                    "base_nonzero": true,
                    "rigorous_degree_bound": bound,
                    "certified_dimension": dimension,
                    "trimmed_degree": trimmed_degree,
                    "interpolation_counts": interpolation_counts,
                    "power_coefficients": rational_strings(&coefficients),
                    "held_out_dilation": dilation,
                    "held_out_direct": count.value.to_string(),
                    "held_out_predicted": rational_string(&predicted),
                    "detail": "held-out direct count disagrees with exact interpolation"
                }),
            );
        }
        held_out.push(json!({
            "n": dilation,
            "direct": count.value.to_string(),
            "predicted": rational_string(&predicted),
            "peak_states": count.peak_states
        }));
    }

    let negative_indices: Vec<usize> = coefficients
        .iter()
        .enumerate()
        .filter_map(|(index, coefficient)| (coefficient < &BigRational::zero()).then_some(index))
        .collect();
    let status = if negative_indices.is_empty() {
        "screened_nonnegative"
    } else {
        "negative_candidate"
    };
    merge(
        base,
        json!({
            "status": status,
            "base_nonzero": true,
            "base_count": base_count.value.to_string(),
            "rigorous_degree_bound": bound,
            "certified_dimension": dimension,
            "trimmed_degree": trimmed_degree,
            "interpolation_counts": interpolation_counts,
            "power_coefficients": rational_strings(&coefficients),
            "negative_coefficient_indices": negative_indices,
            "held_out": held_out,
            "max_peak_states": peak_states
        }),
    )
}

fn base_record(scheduled: &ScheduledInstance, config_sha256: &str) -> Value {
    json!({
        "schema_version": SCHEMA_VERSION,
        "config_sha256": config_sha256,
        "sequence": scheduled.sequence,
        "source": scheduled.source,
        "source_index": scheduled.source_index,
        "instance_id": scheduled.instance_id,
        "lambda": scheduled.instance.lambda,
        "beta": scheduled.instance.beta,
        "weight": scheduled.instance.weight
    })
}

fn failure_record(
    base: Value,
    failure: CountFailure,
    phase: &str,
    dilation: usize,
    base_nonzero: bool,
) -> Value {
    match failure {
        CountFailure::Resource(detail) => merge(
            base,
            json!({
                "status": "resource_error",
                "base_nonzero": base_nonzero,
                "phase": phase,
                "dilation": dilation,
                "detail": detail
            }),
        ),
        CountFailure::Invalid(detail) => merge(
            base,
            json!({
                "status": "invariant_error",
                "base_nonzero": base_nonzero,
                "phase": phase,
                "dilation": dilation,
                "detail": detail
            }),
        ),
    }
}

fn count_at(
    instance: &Instance,
    dilation: u64,
    max_states: usize,
) -> Result<CountAt, CountFailure> {
    let factor = u32::try_from(dilation)
        .map_err(|_| CountFailure::Invalid("dilation does not fit u32".to_owned()))?;
    let scale = |parts: &[u32]| -> Result<Vec<u32>, CountFailure> {
        parts
            .iter()
            .map(|part| {
                part.checked_mul(factor).ok_or_else(|| {
                    CountFailure::Invalid("u32 overflow while scaling an instance".to_owned())
                })
            })
            .collect()
    };
    let lambda = Partition::from_sorted(scale(&instance.lambda)?);
    let beta = Partition::from_sorted(scale(&instance.beta)?);
    let weight = scale(&instance.weight)?;
    let stats = catch_engine_resource(|| {
        skew_kostka_stats(&lambda, &beta, &weight, Some(max_states), true)
    })?;
    Ok(CountAt {
        value: stats.value,
        peak_states: stats.peak_states,
    })
}

fn catch_engine_resource<T>(operation: impl FnOnce() -> T) -> Result<T, CountFailure> {
    let previous_hook = panic::take_hook();
    panic::set_hook(Box::new(|_| {}));
    let result = panic::catch_unwind(AssertUnwindSafe(operation));
    panic::set_hook(previous_hook);
    match result {
        Ok(value) => Ok(value),
        Err(payload) => {
            let message = panic_payload(&payload);
            if message.contains("exceeds --max-states") {
                Err(CountFailure::Resource(message))
            } else {
                panic::resume_unwind(payload)
            }
        }
    }
}

fn panic_payload(payload: &Box<dyn Any + Send>) -> String {
    if let Some(message) = payload.downcast_ref::<String>() {
        message.clone()
    } else if let Some(message) = payload.downcast_ref::<&str>() {
        (*message).to_owned()
    } else {
        "non-string panic payload".to_owned()
    }
}

fn rational_strings(coefficients: &[BigRational]) -> Vec<String> {
    coefficients.iter().map(rational_string).collect()
}

fn rational_string(value: &BigRational) -> String {
    if value.denom() == &BigInt::one() {
        value.numer().to_string()
    } else {
        format!("{}/{}", value.numer(), value.denom())
    }
}

fn merge(mut base: Value, extra: Value) -> Value {
    let base_object = base.as_object_mut().expect("base record must be an object");
    for (key, value) in extra.as_object().expect("extra record must be an object") {
        base_object.insert(key.clone(), value.clone());
    }
    base
}

fn prepare_output(
    output_dir: &Path,
    resume: bool,
    config: &RunConfig,
    config_sha256: &str,
) -> Result<(), String> {
    let manifest_path = output_dir.join("manifest.json");
    if resume {
        let manifest: Value =
            serde_json::from_slice(&fs::read(&manifest_path).map_err(|error| {
                format!("cannot resume without {}: {error}", manifest_path.display())
            })?)
            .map_err(json_error)?;
        let recorded = manifest
            .get("config_sha256")
            .and_then(Value::as_str)
            .ok_or_else(|| "manifest is missing config_sha256".to_owned())?;
        if recorded != config_sha256 {
            return Err(format!(
                "resume configuration mismatch: manifest={recorded}, current={config_sha256}"
            ));
        }
        return Ok(());
    }

    if output_dir.exists() && output_dir.read_dir().map_err(io_error)?.next().is_some() {
        return Err(format!(
            "output directory {} is not empty; use --resume only for the identical manifest",
            output_dir.display()
        ));
    }
    fs::create_dir_all(output_dir).map_err(io_error)?;
    let manifest = json!({
        "schema_version": SCHEMA_VERSION,
        "config_sha256": config_sha256,
        "config": config,
        "scope": "one bounded skew-Kostka falsification gate",
        "null_result_claim": "none; a finite null scan is not evidence for full KTT"
    });
    atomic_write_json(&manifest_path, &manifest)
}

fn recover_records(
    path: &Path,
    config_sha256: &str,
) -> Result<(Vec<RecoveredRecord>, Stats), String> {
    if !path.exists() {
        return Ok((Vec::new(), Stats::default()));
    }
    let bytes = fs::read(path).map_err(io_error)?;
    let mut cursor = 0usize;
    let mut valid_end = 0usize;
    let mut recovered = Vec::new();
    let mut stats = Stats::default();
    let mut valid_without_newline = false;
    while cursor < bytes.len() {
        let newline = bytes[cursor..]
            .iter()
            .position(|byte| *byte == b'\n')
            .map(|offset| cursor + offset);
        let end = newline.unwrap_or(bytes.len());
        let mut line = &bytes[cursor..end];
        if line.last() == Some(&b'\r') {
            line = &line[..line.len() - 1];
        }
        if line.is_empty() {
            return Err(format!("empty JSONL row at byte {cursor}"));
        }
        let parsed: Value = match serde_json::from_slice(line) {
            Ok(value) => value,
            Err(error) if newline.is_none() || end + 1 == bytes.len() => {
                let mut file = OpenOptions::new()
                    .write(true)
                    .open(path)
                    .map_err(io_error)?;
                file.set_len(valid_end as u64).map_err(io_error)?;
                file.seek(SeekFrom::Start(valid_end as u64))
                    .map_err(io_error)?;
                file.sync_all().map_err(io_error)?;
                eprintln!("repaired truncated final JSONL row: {error}");
                break;
            }
            Err(error) => {
                return Err(format!(
                    "invalid non-final JSONL row at byte {cursor}: {error}"
                ))
            }
        };
        let sequence = parsed
            .get("sequence")
            .and_then(Value::as_u64)
            .ok_or_else(|| format!("record at byte {cursor} lacks sequence"))?;
        if sequence != recovered.len() as u64 {
            return Err(format!(
                "noncontiguous record sequence: got {sequence}, expected {}",
                recovered.len()
            ));
        }
        if parsed.get("config_sha256").and_then(Value::as_str) != Some(config_sha256) {
            return Err(format!("record {sequence} has a different config hash"));
        }
        let instance_id = parsed
            .get("instance_id")
            .and_then(Value::as_str)
            .ok_or_else(|| format!("record {sequence} lacks instance_id"))?
            .to_owned();
        let source = parsed
            .get("source")
            .and_then(Value::as_str)
            .ok_or_else(|| format!("record {sequence} lacks source"))?
            .to_owned();
        let source_index = parsed
            .get("source_index")
            .and_then(Value::as_u64)
            .and_then(|value| usize::try_from(value).ok())
            .ok_or_else(|| format!("record {sequence} has invalid source_index"))?;
        let array = |field: &str| -> Result<Vec<u32>, String> {
            serde_json::from_value(
                parsed
                    .get(field)
                    .ok_or_else(|| format!("record {sequence} lacks {field}"))?
                    .clone(),
            )
            .map_err(json_error)
        };
        recovered.push(RecoveredRecord {
            instance_id,
            source,
            source_index,
            instance: Instance {
                lambda: array("lambda")?,
                beta: array("beta")?,
                weight: array("weight")?,
            },
        });
        stats.apply(&parsed)?;
        valid_end = newline.map_or(end, |position| position + 1);
        valid_without_newline = newline.is_none();
        cursor = valid_end;
    }
    if valid_without_newline && valid_end == bytes.len() {
        let mut file = OpenOptions::new()
            .append(true)
            .open(path)
            .map_err(io_error)?;
        file.write_all(b"\n").map_err(io_error)?;
        file.sync_data().map_err(io_error)?;
    }
    Ok((recovered, stats))
}

fn append_json_line(writer: &mut BufWriter<File>, value: &Value) -> Result<(), String> {
    serde_json::to_writer(&mut *writer, value).map_err(json_error)?;
    writer.write_all(b"\n").map_err(io_error)?;
    writer.flush().map_err(io_error)
}

fn append_synced_json_line(path: &Path, value: &Value) -> Result<(), String> {
    let file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)
        .map_err(io_error)?;
    let mut writer = BufWriter::new(file);
    append_json_line(&mut writer, value)?;
    writer.get_ref().sync_all().map_err(io_error)
}

fn write_checkpoint_and_summary(
    output_dir: &Path,
    config: &RunConfig,
    config_sha256: &str,
    stats: &Stats,
    scheduled_total: usize,
    run_status: &str,
    records_sha256: Option<&str>,
) -> Result<(), String> {
    let checkpoint = json!({
        "schema_version": SCHEMA_VERSION,
        "config_sha256": config_sha256,
        "next_sequence": stats.processed_records,
        "stats": stats,
        "updated_unix_seconds": unix_seconds()
    });
    atomic_write_json(&output_dir.join("checkpoint.json"), &checkpoint)?;

    let complete = stats.processed_records as usize == scheduled_total;
    let summary = json!({
        "schema_version": SCHEMA_VERSION,
        "run_status": run_status,
        "config_sha256": config_sha256,
        "vendor_ehrcalc_commit": config.vendor_ehrcalc_commit,
        "binary_sha256": config.binary_sha256,
        "exhaustive_schedule_sha256": config.exhaustive_schedule_sha256,
        "adversarial_schedule_sha256": config.adversarial_schedule_sha256,
        "combined_schedule_sha256": config.combined_schedule_sha256,
        "records_sha256": records_sha256,
        "scheduled_total": scheduled_total,
        "scheduled_exhaustive_canonical": 69_218,
        "scheduled_adversarial_constructively_nonzero": ADVERSARIAL_COUNT,
        "processed_all_scheduled": complete,
        "stats": stats,
        "screened_total": stats.screened(),
        "bounded_gate_exhausted": complete
            && stats.resource_errors == 0
            && stats.skipped_policy == 0
            && stats.invariant_errors == 0
            && stats.negative_candidates == 0,
        "route_exit_if_exhausted_without_negative":
            "DEAD: bounded Kostka falsification exhausted -- no theorem-closing bridge.",
        "mathematical_claim": if stats.negative_candidates > 0 {
            "raw candidate only; independent LR replay and second reconstruction are still required"
        } else {
            "none; finite null output is not evidence for full KTT"
        }
    });
    atomic_write_json(&output_dir.join("summary.json"), &summary)
}

fn atomic_write_json(path: &Path, value: &Value) -> Result<(), String> {
    let temporary = path.with_extension("tmp");
    {
        let file = File::create(&temporary).map_err(io_error)?;
        let mut writer = BufWriter::new(file);
        serde_json::to_writer_pretty(&mut writer, value).map_err(json_error)?;
        writer.write_all(b"\n").map_err(io_error)?;
        writer.flush().map_err(io_error)?;
        writer.get_ref().sync_all().map_err(io_error)?;
    }
    if path.exists() {
        fs::remove_file(path).map_err(io_error)?;
    }
    fs::rename(&temporary, path).map_err(io_error)
}

fn verify_vendor_commit() -> Result<(), String> {
    if env!("KTT_EHRCALC_COMMIT") != PINNED_EHRCALC_COMMIT {
        return Err("compile-time ehrcalc commit does not match the scanner pin".to_owned());
    }
    let vendor = Path::new(env!("CARGO_MANIFEST_DIR")).join("../vendor/ehrcalc");
    let output = Command::new("git")
        .arg("-C")
        .arg(vendor)
        .args(["rev-parse", "HEAD"])
        .output()
        .map_err(io_error)?;
    if !output.status.success() {
        return Err(format!(
            "cannot verify vendor commit: {}",
            String::from_utf8_lossy(&output.stderr).trim()
        ));
    }
    let actual = String::from_utf8(output.stdout)
        .map_err(|error| error.to_string())?
        .trim()
        .to_owned();
    if actual != PINNED_EHRCALC_COMMIT {
        return Err(format!(
            "vendor commit drift: expected {PINNED_EHRCALC_COMMIT}, got {actual}"
        ));
    }
    Ok(())
}

fn hash_file(path: &Path) -> Result<String, String> {
    let mut file = File::open(path).map_err(io_error)?;
    let mut hasher = Sha256::new();
    let mut buffer = [0u8; 1024 * 1024];
    loop {
        let count = file.read(&mut buffer).map_err(io_error)?;
        if count == 0 {
            break;
        }
        hasher.update(&buffer[..count]);
    }
    Ok(format!("{:x}", hasher.finalize()))
}

fn hash_bytes(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn unix_seconds() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("system clock is before the Unix epoch")
        .as_secs()
}

fn io_error(error: io::Error) -> String {
    error.to_string()
}

fn json_error(error: serde_json::Error) -> String {
    error.to_string()
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    fn record(sequence: usize, status: &str, source: &str, base_nonzero: bool) -> Value {
        json!({
            "schema_version": SCHEMA_VERSION,
            "config_sha256": "cfg",
            "sequence": sequence,
            "source": source,
            "source_index": sequence,
            "instance_id": format!("id-{sequence}"),
            "lambda": [2,1],
            "beta": [1],
            "weight": [2],
            "status": status,
            "base_nonzero": base_nonzero
        })
    }

    #[test]
    fn stats_never_count_skips_as_screened() {
        let mut stats = Stats::default();
        for value in [
            record(0, "screened_nonnegative", "exhaustive", true),
            record(1, "resource_error", "exhaustive", true),
            record(2, "skipped_policy", "adversarial", true),
            record(3, "excluded_zero", "exhaustive", false),
        ] {
            stats.apply(&value).unwrap();
        }
        assert_eq!(stats.processed_records, 4);
        assert_eq!(stats.screened(), 1);
        assert_eq!(stats.resource_errors, 1);
        assert_eq!(stats.skipped_policy, 1);
        assert_eq!(stats.excluded_zero, 1);
    }

    #[test]
    fn recovery_truncates_only_the_partial_final_row() {
        let directory = tempdir().unwrap();
        let path = directory.path().join("records.jsonl");
        let mut bytes =
            serde_json::to_vec(&record(0, "screened_nonnegative", "exhaustive", true)).unwrap();
        bytes.push(b'\n');
        let valid_length = bytes.len();
        bytes.extend_from_slice(b"{\"schema_version\":1,\"sequence\":1");
        fs::write(&path, bytes).unwrap();

        let (rows, stats) = recover_records(&path, "cfg").unwrap();
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0].source, "exhaustive");
        assert_eq!(rows[0].instance.lambda, vec![2, 1]);
        assert_eq!(stats.screened(), 1);
        assert_eq!(fs::metadata(&path).unwrap().len(), valid_length as u64);
    }

    #[test]
    fn recovery_rejects_noncontiguous_sequences() {
        let directory = tempdir().unwrap();
        let path = directory.path().join("records.jsonl");
        let mut bytes =
            serde_json::to_vec(&record(1, "screened_nonnegative", "exhaustive", true)).unwrap();
        bytes.push(b'\n');
        fs::write(&path, bytes).unwrap();
        assert!(recover_records(&path, "cfg")
            .unwrap_err()
            .contains("noncontiguous"));
    }

    #[test]
    #[ignore = "prints the full deterministic schedule hashes"]
    fn print_full_schedule_hashes() {
        let schedule = build_schedule().unwrap();
        eprintln!("exhaustive={}", schedule.exhaustive_sha256);
        eprintln!("adversarial={}", schedule.adversarial_sha256);
        eprintln!("combined={}", schedule.combined_sha256);
        assert_eq!(schedule.rows.len(), 69_218 + ADVERSARIAL_COUNT);
    }
}
