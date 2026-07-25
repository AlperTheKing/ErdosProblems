use std::path::PathBuf;
use std::process::Command;

const PINNED_EHRCALC_COMMIT: &str = "51c0606810b37944043952fcbe5b3e41d7123273";

fn main() {
    let manifest_dir = PathBuf::from(std::env::var_os("CARGO_MANIFEST_DIR").unwrap());
    let vendor = manifest_dir.join("../vendor/ehrcalc");
    let output = Command::new("git")
        .arg("-C")
        .arg(&vendor)
        .args(["rev-parse", "HEAD"])
        .output()
        .expect("git is required to verify the pinned ehrcalc dependency");
    if !output.status.success() {
        panic!(
            "cannot read ehrcalc vendor commit: {}",
            String::from_utf8_lossy(&output.stderr).trim()
        );
    }
    let actual = String::from_utf8(output.stdout)
        .expect("ehrcalc commit must be UTF-8")
        .trim()
        .to_owned();
    assert_eq!(
        actual, PINNED_EHRCALC_COMMIT,
        "ehrcalc vendor commit drifted; refusing to build"
    );
    println!("cargo:rustc-env=KTT_EHRCALC_COMMIT={actual}");
    println!(
        "cargo:rerun-if-changed={}",
        vendor.join(".git/HEAD").display()
    );
}
