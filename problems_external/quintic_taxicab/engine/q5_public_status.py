#!/usr/bin/env python3
"""Capture and audit the live public-status evidence for the Q5 tranche.

The collector has no process-launch capability.  A successful collection
stores each exact HTTP response in a new immutable capture directory and only
then atomically replaces the fixed gate JSON.  Network, decoding, schema, or
classification ambiguity leaves the previous gate untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


SCHEMA_VERSION = 2
KIND = "Q5_PUBLIC_STATUS_GATE"
ENGINE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ENGINE_DIR / "logs" / "q5-eight-hour-tranche-v1" / "public_status_gate.json"
CAPTURE_PARENT_NAME = "public_status_captures"
MAX_BODY_BYTES = 16 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 30.0
ARXIV_URL = "https://arxiv.org/abs/2512.11072"
OEIS_URL = "https://oeis.org/A046881/internal"
FORMAL_REF_URL = (
    "https://api.github.com/repos/google-deepmind/formal-conjectures/git/ref/heads/main"
)
FORMAL_RAW_TEMPLATE = (
    "https://raw.githubusercontent.com/google-deepmind/formal-conjectures/"
    "{commit}/FormalConjectures/Wikipedia/Taxicab.lean"
)
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")


class PublicStatusError(RuntimeError):
    """The evidence could not be captured or classified without ambiguity."""


@dataclass(frozen=True)
class FetchResponse:
    body: bytes
    final_url: str
    status: int
    headers: Mapping[str, str]


Fetcher = Callable[[str], FetchResponse]
Clock = Callable[[], datetime]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_text(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise PublicStatusError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise PublicStatusError(f"value is not canonical JSON: {exc}") from exc


def _pretty_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise PublicStatusError(f"value is not strict JSON: {exc}") from exc


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise PublicStatusError(f"atomic write failed for {path}: {exc}") from exc


def _default_fetcher(timeout: float = DEFAULT_TIMEOUT_SECONDS) -> Fetcher:
    def fetch(url: str) -> FetchResponse:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "*/*",
                "User-Agent": "Q5-public-status/2 (evidence capture; no search launch)",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = int(response.status)
                body = response.read(MAX_BODY_BYTES + 1)
                headers = {key.lower(): value for key, value in response.headers.items()}
                final_url = response.geturl()
        except (OSError, urllib.error.URLError, ValueError) as exc:
            raise PublicStatusError(f"HTTP fetch failed for {url}: {exc}") from exc
        if status != 200:
            raise PublicStatusError(f"HTTP status for {url} is {status}, expected 200")
        if len(body) > MAX_BODY_BYTES:
            raise PublicStatusError(f"HTTP body for {url} exceeds {MAX_BODY_BYTES} bytes")
        if not body:
            raise PublicStatusError(f"HTTP body for {url} is empty")
        return FetchResponse(body=body, final_url=final_url, status=status, headers=headers)

    return fetch


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _html_text(body: bytes, role: str) -> str:
    try:
        decoded = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PublicStatusError(f"{role} body is not UTF-8") from exc
    parser = _VisibleText()
    try:
        parser.feed(decoded)
        parser.close()
    except Exception as exc:
        raise PublicStatusError(f"{role} HTML parse failed: {exc}") from exc
    return html.unescape("\n".join(parser.parts))


def _validate_final_url(
    role: str, requested_url: str, final_url: str, *, commit: str | None = None
) -> None:
    if role == "asiryan_arxiv":
        expected_requested = ARXIV_URL
        expected_host = "arxiv.org"
        expected_path = "/abs/2512.11072"
    elif role == "oeis_a046881":
        expected_requested = OEIS_URL
        expected_host = "oeis.org"
        expected_path = "/A046881/internal"
    elif role == "formal_conjectures_main_ref":
        expected_requested = FORMAL_REF_URL
        expected_host = "api.github.com"
        expected_path = "/repos/google-deepmind/formal-conjectures/git/ref/heads/main"
    elif role == "formal_conjectures_taxicab_raw":
        if not isinstance(commit, str) or COMMIT_RE.fullmatch(commit) is None:
            raise PublicStatusError("raw source URL validation lacks a main commit")
        expected_requested = FORMAL_RAW_TEMPLATE.format(commit=commit)
        expected_host = "raw.githubusercontent.com"
        expected_path = (
            f"/google-deepmind/formal-conjectures/{commit}/"
            "FormalConjectures/Wikipedia/Taxicab.lean"
        )
    else:
        raise PublicStatusError(f"unknown source role {role}")
    if requested_url != expected_requested:
        raise PublicStatusError(f"fixed requested URL mismatch for {role}")
    parsed = urllib.parse.urlparse(final_url)
    if (
        parsed.scheme != "https"
        or (parsed.hostname or "").lower() != expected_host
        or parsed.path != expected_path
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise PublicStatusError(f"non-canonical final URL for {role}")


def _classify_arxiv(body: bytes) -> tuple[str, dict[str, Any]]:
    text = " ".join(_html_text(body, "asiryan_arxiv").split())
    lowered = text.lower()
    required = (
        "arxiv:2512.11072",
        "valery asiryan",
        "genus-one fibrations and the jacobian of linear slices in the quintic equal-sum problem",
        "global open problem of non-trivial solutions",
    )
    present = [token in lowered for token in required]
    if not all(present):
        raise PublicStatusError("Asiryan/arXiv response lacks the explicit open-problem marker")
    return "OPEN", {
        "rule": "all required normalized-text markers are present",
        "required_markers": list(required),
    }


def _classify_oeis(body: bytes) -> tuple[str, dict[str, Any]]:
    text = _html_text(body, "oeis_a046881")
    if "A046881" not in text or "Smallest number that is sum of 2 positive distinct n-th powers" not in text:
        raise PublicStatusError("OEIS response identity or definition mismatch")
    chunks = re.findall(r"%[STU]\s+([^\r\n<]+)", text)
    if not chunks:
        raise PublicStatusError("OEIS response has no %S/%T/%U data records")
    terms: list[int] = []
    for chunk in chunks:
        for raw in chunk.strip().rstrip(",").split(","):
            token = raw.strip()
            if token:
                if re.fullmatch(r"-?[0-9]+", token) is None:
                    raise PublicStatusError("OEIS data record contains a non-integer token")
                terms.append(int(token))
    offset = re.search(r"%O\s+([0-9]+),([0-9]+)", text)
    if offset is None or int(offset.group(1)) != 1:
        raise PublicStatusError("OEIS A046881 offset is absent or not 1")
    n5_defined = len(terms) >= 5
    return ("HAS_N5_VALUE" if n5_defined else "NO_N5_VALUE"), {
        "rule": "the %S/%T/%U term count is interpreted using %O offset 1",
        "offset": 1,
        "term_count": len(terms),
        "n5_defined": n5_defined,
    }


def _classify_formal_ref(body: bytes) -> tuple[str, dict[str, Any]]:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PublicStatusError(f"Formal Conjectures main-ref JSON is invalid: {exc}") from exc
    if not isinstance(value, dict) or value.get("ref") != "refs/heads/main":
        raise PublicStatusError("Formal Conjectures response is not refs/heads/main")
    obj = value.get("object")
    if not isinstance(obj, dict) or obj.get("type") != "commit":
        raise PublicStatusError("Formal Conjectures main ref does not name a commit")
    commit = obj.get("sha")
    if not isinstance(commit, str) or COMMIT_RE.fullmatch(commit) is None:
        raise PublicStatusError("Formal Conjectures main commit SHA is malformed")
    return "MAIN_COMMIT_RESOLVED", {
        "rule": "GitHub refs/heads/main object is a 40-hex commit",
        "commit_sha": commit,
    }


def _lean_code_view(text: str) -> str:
    """Preserve Lean code positions while blanking comments and strings."""

    output = list(text)
    index = 0
    block_depth = 0
    line_comment = False
    in_string = False
    escaped = False
    while index < len(text):
        if line_comment:
            if text[index] == "\n":
                line_comment = False
            else:
                output[index] = " "
            index += 1
            continue
        if block_depth:
            if text.startswith("/-", index):
                output[index] = output[index + 1] = " "
                block_depth += 1
                index += 2
            elif text.startswith("-/", index):
                output[index] = output[index + 1] = " "
                block_depth -= 1
                index += 2
            else:
                if text[index] != "\n":
                    output[index] = " "
                index += 1
            continue
        if in_string:
            character = text[index]
            if character == "\n":
                raise PublicStatusError("Formal Conjectures source has an unterminated string")
            output[index] = " "
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if text.startswith("--", index):
            output[index] = output[index + 1] = " "
            line_comment = True
            index += 2
        elif text.startswith("/-", index):
            output[index] = output[index + 1] = " "
            block_depth = 1
            index += 2
        elif text[index] == '"':
            output[index] = " "
            in_string = True
            index += 1
        else:
            index += 1
    if block_depth or in_string:
        raise PublicStatusError("Formal Conjectures source has unterminated Lean syntax")
    return "".join(output)


def _classify_formal_raw(body: bytes) -> tuple[str, dict[str, Any]]:
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PublicStatusError("Formal Conjectures Taxicab source is not UTF-8") from exc
    code = _lean_code_view(text)
    target_mentions = list(
        re.finditer(
            r"\btaxicab_for_5_2_2\b",
            code,
        )
    )
    if len(target_mentions) > 1:
        raise PublicStatusError("Taxicab source has multiple live target mentions")
    if not target_mentions:
        if "taxicab_for_5_2_2" in text:
            return "NOT_RESEARCH_OPEN", {
                "rule": "no live target mention is present",
                "answer_sorry": False,
            }
        raise PublicStatusError("Taxicab source lacks taxicab_for_5_2_2")
    declarations = list(
        re.finditer(
            r"(?m)^(?:theorem|def)\s+taxicab_for_5_2_2\b",
            code,
        )
    )
    if len(declarations) != 1:
        return "NOT_RESEARCH_OPEN", {
            "rule": "the sole live target mention is not a column-zero theorem or def",
            "answer_sorry": False,
        }
    declaration = declarations[0]
    attribute = re.search(
        r"(?s)@\[(?P<attributes>[^\]]*)\]\s*\Z",
        code[: declaration.start()],
    )
    category_open = (
        attribute is not None
        and re.search(
            r"(?:^|[\s,])category\s+research\s+open(?:$|[\s,])",
            attribute.group("attributes"),
        )
        is not None
    )
    if not category_open:
        return "NOT_RESEARCH_OPEN", {
            "rule": "the immediately adjacent attribute is not category research open",
            "answer_sorry": False,
        }
    header_end = code.find(":=", declaration.end(), declaration.end() + 1500)
    if header_end < 0:
        raise PublicStatusError("Taxicab target declaration header is not bounded by :=")
    header = " ".join(code[declaration.start() : header_end + 2].split())
    expected_header = (
        "theorem taxicab_for_5_2_2 : answer(sorry) \u2194 "
        "\u2203 x : \u2115, IsTaxicabFor 5 2 2 x :="
    )
    if header != expected_header:
        if "answer(sorry)" in header:
            raise PublicStatusError(
                "Taxicab target retains answer(sorry) under an unreviewed signature"
            )
        return "NOT_RESEARCH_OPEN", {
            "rule": "the exact research-open target signature no longer contains answer(sorry)",
            "answer_sorry": False,
        }
    return "RESEARCH_OPEN_ANSWER_SORRY", {
        "rule": "the adjacent open attribute and exact target header match",
        "answer_sorry": True,
        "normalized_header": expected_header,
    }

def _source_record(
    *,
    role: str,
    requested_url: str,
    response: FetchResponse,
    fetched_utc: str,
    content_path: Path,
    observed_status: str,
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "role": role,
        "requested_url": requested_url,
        "final_url": response.final_url,
        "fetched_utc": fetched_utc,
        "http_status": response.status,
        "content_type": response.headers.get("content-type"),
        "etag": response.headers.get("etag"),
        "last_modified": response.headers.get("last-modified"),
        "content_path": str(content_path.resolve()),
        "content_size": len(response.body),
        "content_sha256": _sha256(response.body),
        "observed_status": observed_status,
        "evidence": dict(evidence),
    }


def _capture_index(sources: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    keys = (
        "role",
        "requested_url",
        "final_url",
        "fetched_utc",
        "http_status",
        "content_type",
        "etag",
        "last_modified",
        "content_path",
        "content_size",
        "content_sha256",
    )
    return [{key: source[key] for key in keys} for source in sources]


def collect(
    output: Path = DEFAULT_OUTPUT,
    *,
    fetcher: Fetcher | None = None,
    clock: Clock = _utc_now,
) -> dict[str, Any]:
    """Collect four sources and atomically commit one strict gate artifact."""

    output = output.resolve()
    fetch = _default_fetcher() if fetcher is None else fetcher
    capture_parent = output.parent / CAPTURE_PARENT_NAME
    checked_seed = clock()
    if checked_seed.tzinfo is None or checked_seed.utcoffset() is None:
        raise PublicStatusError("clock returned a naive timestamp")
    capture_id = checked_seed.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "-" + uuid.uuid4().hex
    final_capture = capture_parent / capture_id
    staging = capture_parent / f".{capture_id}.tmp"
    if final_capture.exists() or staging.exists():
        raise PublicStatusError("capture identifier collision")
    staging.mkdir(parents=True, exist_ok=False)
    sources: list[dict[str, Any]] = []
    committed_capture = False
    try:
        fixed = (
            ("asiryan_arxiv", ARXIV_URL, "asiryan_arxiv.response", _classify_arxiv),
            ("oeis_a046881", OEIS_URL, "oeis_a046881.response", _classify_oeis),
            (
                "formal_conjectures_main_ref",
                FORMAL_REF_URL,
                "formal_conjectures_main_ref.response",
                _classify_formal_ref,
            ),
        )
        commit: str | None = None
        for role, url, filename, classifier in fixed:
            response = fetch(url)
            if response.status != 200 or not response.body:
                raise PublicStatusError(f"invalid HTTP response for {role}")
            body_path = staging / filename
            _validate_final_url(role, url, response.final_url)
            with body_path.open("xb") as stream:
                stream.write(response.body)
                stream.flush()
                os.fsync(stream.fileno())
            status, evidence = classifier(response.body)
            if role == "formal_conjectures_main_ref":
                commit = evidence["commit_sha"]
            sources.append(
                _source_record(
                    role=role,
                    requested_url=url,
                    response=response,
                    fetched_utc=_utc_text(clock()),
                    content_path=final_capture / filename,
                    observed_status=status,
                    evidence=evidence,
                )
            )
        if commit is None:
            raise PublicStatusError("Formal Conjectures main commit was not resolved")
        raw_url = FORMAL_RAW_TEMPLATE.format(commit=commit)
        raw_response = fetch(raw_url)
        if raw_response.status != 200 or not raw_response.body:
            raise PublicStatusError("invalid HTTP response for formal_conjectures_taxicab_raw")
        raw_name = "formal_conjectures_taxicab_raw.response"
        _validate_final_url("formal_conjectures_taxicab_raw", raw_url, raw_response.final_url, commit=commit)
        raw_path = staging / raw_name
        with raw_path.open("xb") as stream:
            stream.write(raw_response.body)
            stream.flush()
            os.fsync(stream.fileno())
        raw_status, raw_evidence = _classify_formal_raw(raw_response.body)
        sources.append(
            _source_record(
                role="formal_conjectures_taxicab_raw",
                requested_url=raw_url,
                response=raw_response,
                fetched_utc=_utc_text(clock()),
                content_path=final_capture / raw_name,
                observed_status=raw_status,
                evidence=raw_evidence,
            )
        )
        index = _capture_index(sources)
        index_bytes = _pretty_bytes(index)
        with (staging / "capture_index.json").open("xb") as stream:
            stream.write(index_bytes)
            stream.flush()
            os.fsync(stream.fileno())
        capture_parent.mkdir(parents=True, exist_ok=True)
        os.rename(staging, final_capture)
        committed_capture = True
        checked = clock().astimezone(timezone.utc)
        gate = {
            "schema_version": SCHEMA_VERSION,
            "kind": KIND,
            "checked_utc": _utc_text(checked),
            "expires_utc": _utc_text(checked + timedelta(minutes=5)),
            "problem_open": sources[0]["observed_status"] == "OPEN",
            "oeis_no_n5_value": sources[1]["observed_status"] == "NO_N5_VALUE",
            "formal_conjecture_open": sources[3]["observed_status"]
            == "RESEARCH_OPEN_ANSWER_SORRY",
            "formal_main_commit_sha": commit,
            "capture_dir": str(final_capture.resolve()),
            "capture_set_sha256": _sha256(_canonical_bytes(index)),
            "sources": sources,
        }
        gate["all_open"] = bool(
            gate["problem_open"]
            and gate["oeis_no_n5_value"]
            and gate["formal_conjecture_open"]
        )
        candidate = output.with_name(
            f".{output.name}.{os.getpid()}.{uuid.uuid4().hex}.candidate"
        )
        try:
            _atomic_write(candidate, _pretty_bytes(gate))
            audit_gate(candidate)
            try:
                os.replace(candidate, output)
            except OSError as exc:
                raise PublicStatusError(f"cannot commit public gate: {exc}") from exc
        finally:
            try:
                candidate.unlink(missing_ok=True)
            except OSError:
                pass
        return gate
    except BaseException:
        if not committed_capture:
            shutil.rmtree(staging, ignore_errors=True)
        raise


GATE_KEYS = {
    "schema_version",
    "kind",
    "checked_utc",
    "expires_utc",
    "problem_open",
    "oeis_no_n5_value",
    "formal_conjecture_open",
    "formal_main_commit_sha",
    "capture_dir",
    "capture_set_sha256",
    "sources",
    "all_open",
}
SOURCE_KEYS = {
    "role",
    "requested_url",
    "final_url",
    "fetched_utc",
    "http_status",
    "content_type",
    "etag",
    "last_modified",
    "content_path",
    "content_size",
    "content_sha256",
    "observed_status",
    "evidence",
}
SOURCE_ROLES = (
    "asiryan_arxiv",
    "oeis_a046881",
    "formal_conjectures_main_ref",
    "formal_conjectures_taxicab_raw",
)


def _parse_utc(value: Any, name: str) -> datetime:
    if not isinstance(value, str):
        raise PublicStatusError(f"{name} must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PublicStatusError(f"{name} is not ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PublicStatusError(f"{name} lacks a UTC offset")
    return parsed.astimezone(timezone.utc)


def audit_gate(path: Path, *, now: datetime | None = None, require_fresh: bool = False) -> dict[str, Any]:
    """Recompute every captured response hash and all three assertions."""

    try:
        raw = path.resolve().read_bytes()
        gate = json.loads(raw.decode("ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PublicStatusError(f"cannot load gate {path}: {exc}") from exc
    if not isinstance(gate, dict) or set(gate) != GATE_KEYS:
        raise PublicStatusError("public gate keys differ from schema v2")
    if gate["schema_version"] != SCHEMA_VERSION or gate["kind"] != KIND:
        raise PublicStatusError("public gate identity mismatch")
    checked = _parse_utc(gate["checked_utc"], "checked_utc")
    expires = _parse_utc(gate["expires_utc"], "expires_utc")
    if expires != checked + timedelta(minutes=5):
        raise PublicStatusError("public gate validity interval is not five minutes")
    if require_fresh:
        instant = _utc_now() if now is None else now.astimezone(timezone.utc)
        if instant < checked or instant > expires:
            raise PublicStatusError("public gate is not fresh")
    sources = gate["sources"]
    if not isinstance(sources, list) or len(sources) != 4:
        raise PublicStatusError("public gate source count mismatch")
    if not isinstance(gate["capture_dir"], str):
        raise PublicStatusError("capture_dir must be a string")
    capture_dir = Path(gate["capture_dir"]).resolve()
    if not capture_dir.is_dir():
        raise PublicStatusError("capture_dir is not a directory")
    for expected_role, source in zip(SOURCE_ROLES, sources):
        if not isinstance(source, dict) or set(source) != SOURCE_KEYS:
            raise PublicStatusError(f"source schema mismatch for {expected_role}")
        if source["role"] != expected_role or source["http_status"] != 200:
            raise PublicStatusError(f"source identity/status mismatch for {expected_role}")
        commit_for_url = None
        if not isinstance(source["evidence"], dict):
            raise PublicStatusError(f"source evidence is not an object for {expected_role}")
        if expected_role == "formal_conjectures_taxicab_raw":
            evidence = sources[2].get("evidence")
            if isinstance(evidence, dict):
                commit_for_url = evidence.get("commit_sha")
        _validate_final_url(expected_role, source["requested_url"], source["final_url"], commit=commit_for_url)
        for url_key in ("requested_url", "final_url"):
            url = source[url_key]
            if not isinstance(url, str):
                raise PublicStatusError(f"{url_key} is not a string for {expected_role}")
            parsed_url = urllib.parse.urlparse(url)
            if parsed_url.scheme != "https" or not parsed_url.netloc:
                raise PublicStatusError(f"{url_key} is not HTTPS for {expected_role}")
        if not isinstance(source["content_size"], int) or isinstance(source["content_size"], bool) or source["content_size"] <= 0:
            raise PublicStatusError(f"content_size is invalid for {expected_role}")
        if not isinstance(source["content_sha256"], str) or SHA256_RE.fullmatch(source["content_sha256"]) is None:
            raise PublicStatusError(f"content_sha256 is malformed for {expected_role}")
        fetched = _parse_utc(source["fetched_utc"], f"{expected_role}.fetched_utc")
        if fetched > checked:
            raise PublicStatusError(f"fetched_utc is after checked_utc for {expected_role}")


        if not isinstance(source["content_path"], str):
            raise PublicStatusError(f"content_path is not a string for {expected_role}")
        content_path = Path(source["content_path"]).resolve()
        try:
            content_path.relative_to(capture_dir)
        except ValueError as exc:
            raise PublicStatusError("captured response path escapes capture_dir") from exc
        try:
            body = content_path.read_bytes()
        except OSError as exc:
            raise PublicStatusError(f"cannot read captured bytes for {expected_role}: {exc}") from exc
        if len(body) != source["content_size"] or _sha256(body) != source["content_sha256"]:
            raise PublicStatusError(f"captured bytes drift for {expected_role}")
        if expected_role == "asiryan_arxiv":
            observed, evidence = _classify_arxiv(body)
        elif expected_role == "oeis_a046881":
            observed, evidence = _classify_oeis(body)
        elif expected_role == "formal_conjectures_main_ref":
            observed, evidence = _classify_formal_ref(body)
        else:
            observed, evidence = _classify_formal_raw(body)
        if observed != source["observed_status"] or evidence != source["evidence"]:
            raise PublicStatusError(f"derived assertion drift for {expected_role}")
    commit = sources[2]["evidence"]["commit_sha"]
    expected_raw_url = FORMAL_RAW_TEMPLATE.format(commit=commit)
    fixed_urls = (ARXIV_URL, OEIS_URL, FORMAL_REF_URL)
    for expected_url, source in zip(fixed_urls, sources[:3]):
        if source["requested_url"] != expected_url:
            raise PublicStatusError(f"fixed requested URL mismatch for {source['role']}")

    if sources[3]["requested_url"] != expected_raw_url:
        raise PublicStatusError("raw Taxicab URL is not pinned to captured main commit")
    index = _capture_index(sources)
    if _sha256(_canonical_bytes(index)) != gate["capture_set_sha256"]:
        raise PublicStatusError("capture_set_sha256 mismatch")
    index_path = capture_dir / "capture_index.json"
    try:
        stored_index = json.loads(index_path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PublicStatusError(f"capture index is invalid: {exc}") from exc
    if stored_index != index:
        raise PublicStatusError("capture index differs from gate sources")
    expected_names = {
        "asiryan_arxiv.response",
        "oeis_a046881.response",
        "formal_conjectures_main_ref.response",
        "formal_conjectures_taxicab_raw.response",
        "capture_index.json",
    }
    try:
        entries = list(capture_dir.iterdir())
    except OSError as exc:
        raise PublicStatusError(f"cannot inventory capture_dir: {exc}") from exc
    actual_names = {entry.name for entry in entries if entry.is_file()}
    nonfiles = [entry.name for entry in entries if not entry.is_file()]
    if actual_names != expected_names or nonfiles:
        raise PublicStatusError("capture_dir inventory differs from the immutable schema")



    derived = {
        "problem_open": sources[0]["observed_status"] == "OPEN",
        "oeis_no_n5_value": sources[1]["observed_status"] == "NO_N5_VALUE",
        "formal_conjecture_open": sources[3]["observed_status"]
        == "RESEARCH_OPEN_ANSWER_SORRY",
    }
    derived["all_open"] = all(derived.values())
    for key, value in derived.items():
        if gate[key] is not value:
            raise PublicStatusError(f"gate assertion {key} differs from captured bytes")
    if gate["formal_main_commit_sha"] != commit:
        raise PublicStatusError("formal_main_commit_sha mismatch")
    if SHA256_RE.fullmatch(gate["capture_set_sha256"]) is None:
        raise PublicStatusError("capture_set_sha256 is malformed")
    return gate


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    collect_parser = commands.add_parser("collect")
    collect_parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    collect_parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    audit_parser = commands.add_parser("audit")
    audit_parser.add_argument("--gate", type=Path, default=DEFAULT_OUTPUT)
    audit_parser.add_argument("--require-fresh", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "collect":
            gate = collect(args.output, fetcher=_default_fetcher(args.timeout))
        else:
            gate = audit_gate(args.gate, require_fresh=args.require_fresh)
        print(
            json.dumps(
                {
                    "ok": True,
                    "kind": gate["kind"],
                    "checked_utc": gate["checked_utc"],
                    "all_open": gate["all_open"],
                    "capture_set_sha256": gate["capture_set_sha256"],
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    except PublicStatusError as exc:
        print(
            json.dumps(
                {"ok": False, "status": "FAIL_CLOSED", "error": str(exc)},
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
