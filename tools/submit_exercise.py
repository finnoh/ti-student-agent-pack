#!/usr/bin/env python3

import argparse
import http.cookiejar
import json
import re
import shutil
import subprocess
import sys
import time
import webbrowser
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

REQUIRED_FIELDS = ["exercise_id", "student_name", "answer"]
ALL_FIELDS = REQUIRED_FIELDS

ENV_KEYS = {
    "google_form_url": "GOOGLE_FORM_URL",
    "exercise_id": "GOOGLE_FORM_EXERCISE_FIELD",
    "student_name": "GOOGLE_FORM_STUDENT_NAME_FIELD",
    "answer": "GOOGLE_FORM_ANSWER_FIELD",
}

NAME_PATTERNS = [
    re.compile(r"^\s*(?:name|preferred_name)\s*:\s*(.+?)\s*$", re.IGNORECASE),
    re.compile(r"^\s*(?:what should i call you\??)\s*:\s*(.+?)\s*$", re.IGNORECASE),
    re.compile(r"^\s*-\s*(?:name|preferred name)\s*:\s*(.+?)\s*$", re.IGNORECASE),
]


def default_config_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config" / "form_config.json"


def default_submissions_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "submissions"


def default_bootstrap_path() -> Path:
    return Path(__file__).resolve().parent.parent / "BOOTSTRAP.md"


def load_config(path: Path) -> dict:
    if not path.exists():
        return {"google_form_url": "", "field_ids": {}}
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"Invalid JSON root in {path}")
    parsed.setdefault("google_form_url", "")
    parsed.setdefault("google_sheet_id", "")
    parsed.setdefault("field_ids", {})
    if not isinstance(parsed["field_ids"], dict):
        raise ValueError("field_ids must be an object")
    return parsed


def save_config(path: Path, config: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _getenv(key: str) -> str:
    import os

    return os.environ.get(key, "").strip()


def apply_env_overrides(config: dict) -> dict:
    merged = {
        "google_form_url": config.get("google_form_url", "").strip(),
        "google_sheet_id": config.get("google_sheet_id", "").strip(),
        "field_ids": dict(config.get("field_ids", {})),
    }
    form_url = _getenv(ENV_KEYS["google_form_url"])
    if form_url:
        merged["google_form_url"] = form_url

    for field_name in ALL_FIELDS:
        env_name = ENV_KEYS.get(field_name)
        if not env_name:
            continue
        override = _getenv(env_name)
        if override:
            merged["field_ids"][field_name] = override
    return merged


def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    raw = input(f"{label}{suffix}: ").strip()
    return raw if raw else default


def _prompt_yes_no(label: str, default_yes: bool = True) -> bool:
    default = "y" if default_yes else "n"
    answer = _prompt(label, default).strip().lower()
    return answer in {"y", "yes"}


def ensure_form_url(config_path: Path, config: dict) -> tuple[dict, str]:
    form_url = str(config.get("google_form_url", "")).strip()
    if form_url:
        return config, form_url
    if not sys.stdin.isatty():
        return config, ""

    print("No Google Form URL configured yet.")
    entered = _prompt("Paste Google Form URL")
    if not entered:
        return config, ""

    save_choice = _prompt("Save this URL in config/form_config.json? (y/n)", "y").lower()
    config["google_form_url"] = entered
    if save_choice in {"y", "yes"}:
        save_config(config_path, config)
        print(f"Saved form URL to {config_path}")
    return config, entered


def read_answer_from_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def parse_markdown_submission(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    metadata = {}
    body_start = 0
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            line = lines[idx]
            if line.strip() == "---":
                body_start = idx + 1
                break
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    body = "\n".join(lines[body_start:]).strip() if body_start else text.strip()
    payload = {key: metadata.get(key, "") for key in ALL_FIELDS}
    payload["answer"] = body or payload.get("answer", "")
    return payload


def load_submitter_name(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        for pattern in NAME_PATTERNS:
            match = pattern.match(line)
            if match:
                return match.group(1).strip()

    for raw_line in text.splitlines():
        line = raw_line.strip().lstrip("#").strip()
        if line and line.lower() not in {"bootstrap", "profile"}:
            return line
    return ""


def apply_submitter_name(payload: dict, submitter_name: str) -> dict:
    if not submitter_name:
        return payload
    student_name = str(payload.get("student_name", "")).strip()
    if student_name:
        return payload
    payload["student_name"] = submitter_name
    return payload


def normalize_payload(payload: dict) -> dict:
    clean = {key: str(payload.get(key, "")).strip() for key in ALL_FIELDS}
    clean["exercise_id"] = clean["exercise_id"].upper()
    return clean


def validate_payload(payload: dict) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_FIELDS:
        if not payload.get(key, "").strip():
            errors.append(f"Missing required field: {key}")

    if payload.get("exercise_id") and not re.fullmatch(r"E\d+", payload["exercise_id"]):
        errors.append("exercise_id must look like E1, E2, ...")

    return errors


def build_prefilled_url(form_url: str, field_ids: dict, payload: dict) -> tuple[str, list[str]]:
    parsed = urlparse(form_url)
    params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    missing_prefill = []
    for field_name in ALL_FIELDS:
        value = payload.get(field_name, "").strip()
        if not value:
            continue
        field_id = str(field_ids.get(field_name, "")).strip()
        if not field_id:
            missing_prefill.append(field_name)
            continue
        params[f"entry.{field_id}"] = value
    updated = parsed._replace(query=urlencode(params))
    return urlunparse(updated), missing_prefill


def build_form_response_url(form_url: str) -> str:
    parsed = urlparse(form_url)
    path = parsed.path
    if path.endswith("/viewform"):
        path = path[: -len("/viewform")] + "/formResponse"
    elif not path.endswith("/formResponse"):
        path = path.rstrip("/") + "/formResponse"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def build_form_payload(field_ids: dict, payload: dict) -> tuple[dict[str, str], list[str]]:
    form_data: dict[str, str] = {}
    missing_ids: list[str] = []
    for field_name in ALL_FIELDS:
        value = payload.get(field_name, "").strip()
        if not value:
            continue
        field_id = str(field_ids.get(field_name, "")).strip()
        if not field_id:
            missing_ids.append(field_name)
            continue
        form_data[f"entry.{field_id}"] = value
    return form_data, missing_ids


def submit_form_http(form_url: str, form_data: dict[str, str], timeout: int) -> tuple[int, str]:
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib_request_opener(cookie_jar)
    tokens = fetch_form_tokens(form_url, timeout=timeout, opener=opener)
    submit_url = build_form_response_url(form_url)
    payload = dict(form_data)
    payload.setdefault("fvv", tokens.get("fvv", "1"))
    payload.setdefault("partialResponse", tokens.get("partialResponse", "[null,null,\"0\"]"))
    payload.setdefault("pageHistory", tokens.get("pageHistory", "0"))
    payload.setdefault("submissionTimestamp", tokens.get("submissionTimestamp", "-1"))
    payload.setdefault("submit", "Submit")
    if tokens.get("fbzx"):
        payload["fbzx"] = tokens["fbzx"]

    body = urlencode(payload).encode("utf-8")
    request = Request(
        submit_url,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "TI-Student-Agent-Pack/1.1",
            "Referer": form_url,
        },
        method="POST",
    )
    with opener.open(request, timeout=timeout) as response:
        status = int(getattr(response, "status", 200))
        final_url = str(getattr(response, "url", submit_url))
    return status, final_url


def urllib_request_opener(cookie_jar: http.cookiejar.CookieJar):
    from urllib.request import HTTPCookieProcessor, build_opener

    return build_opener(HTTPCookieProcessor(cookie_jar))


def fetch_form_tokens(form_url: str, timeout: int, opener) -> dict[str, str]:
    request = Request(
        form_url,
        headers={
            "User-Agent": "TI-Student-Agent-Pack/1.1",
        },
        method="GET",
    )
    with opener.open(request, timeout=timeout) as response:
        html = response.read().decode("utf-8", errors="ignore")

    tokens: dict[str, str] = {}
    for key in ["fvv", "partialResponse", "pageHistory", "fbzx", "submissionTimestamp"]:
        match = re.search(rf'name="{key}"\s+value="([^"]*)"', html)
        if match:
            tokens[key] = match.group(1)

    if "fbzx" not in tokens:
        match = re.search(r'"fbzx"\s*,\s*"([^"]+)"', html)
        if match:
            tokens["fbzx"] = match.group(1)

    return tokens


def submit_with_retry(
    form_url: str,
    form_data: dict[str, str],
    retry_count: int,
    backoff_seconds: float,
    timeout: int,
) -> tuple[bool, int, str, list[dict], str]:
    attempts: list[dict] = []
    max_attempts = retry_count + 1
    final_status = 0
    final_url = build_form_response_url(form_url)
    final_error = ""

    for attempt in range(1, max_attempts + 1):
        started = datetime.now(UTC).replace(microsecond=0).isoformat()
        try:
            status, url = submit_form_http(form_url, form_data, timeout=timeout)
            final_status = status
            final_url = url
            success = 200 <= status < 400
            attempts.append(
                {
                    "attempt": attempt,
                    "started_at": started,
                    "status": status,
                    "url": url,
                    "success": success,
                    "error": "",
                }
            )
            if success:
                return True, final_status, final_url, attempts, ""
            final_error = f"Unexpected HTTP status {status}"
        except HTTPError as exc:
            final_status = int(getattr(exc, "code", 0) or 0)
            final_error = f"HTTPError {final_status}: {exc.reason}"
            attempts.append(
                {
                    "attempt": attempt,
                    "started_at": started,
                    "status": final_status,
                    "url": final_url,
                    "success": False,
                    "error": final_error,
                }
            )
        except URLError as exc:
            final_error = f"URLError: {exc.reason}"
            attempts.append(
                {
                    "attempt": attempt,
                    "started_at": started,
                    "status": 0,
                    "url": final_url,
                    "success": False,
                    "error": final_error,
                }
            )
        except Exception as exc:  # pragma: no cover
            final_error = f"Unexpected error: {exc}"
            attempts.append(
                {
                    "attempt": attempt,
                    "started_at": started,
                    "status": 0,
                    "url": final_url,
                    "success": False,
                    "error": final_error,
                }
            )

        if attempt < max_attempts:
            sleep_seconds = max(0.0, backoff_seconds * (2 ** (attempt - 1)))
            print(f"Attempt {attempt} failed. Retrying in {sleep_seconds:.1f}s...")
            time.sleep(sleep_seconds)

    return False, final_status, final_url, attempts, final_error


def persist_submission(payload: dict, submissions_dir: Path) -> Path:
    submissions_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    exercise = payload.get("exercise_id", "EX")
    student_raw = str(payload.get("student_name", "student"))
    student = re.sub(r"[^A-Za-z0-9._-]+", "_", student_raw).strip("_") or "student"
    filename = f"{ts}_{exercise}_{student}.json"
    path = submissions_dir / filename
    stored = {
        "saved_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "submission": payload,
    }
    path.write_text(json.dumps(stored, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return path


def persist_receipt(
    submissions_dir: Path,
    saved_submission_path: Path,
    payload: dict,
    prefilled_url: str,
    attempts: list[dict],
    success: bool,
    status: int,
    endpoint_url: str,
    error: str,
) -> Path:
    receipts_dir = submissions_dir / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    exercise = payload.get("exercise_id", "EX")
    student_raw = str(payload.get("student_name", "student"))
    student = re.sub(r"[^A-Za-z0-9._-]+", "_", student_raw).strip("_") or "student"
    receipt_path = receipts_dir / f"{ts}_{exercise}_{student}_receipt.json"

    receipt = {
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "success": success,
        "status": status,
        "endpoint_url": endpoint_url,
        "error": error,
        "prefilled_url": prefilled_url,
        "saved_submission_path": str(saved_submission_path),
        "attempts": attempts,
        "submission": payload,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return receipt_path


def print_copy_paste_fallback(payload: dict, prefilled_url: str) -> None:
    print("\nSubmission failed after retries.")
    print("Copy/paste fallback payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    print("\nOpen this link to submit manually (Cmd + left click):")
    print(prefilled_url)


def maybe_append_to_sheet(payload: dict, sheet_id: str) -> tuple[bool, str]:
    if not sheet_id.strip():
        return False, ""
    if shutil.which("gws") is None:
        return False, ""

    values = [[payload.get("exercise_id", ""), payload.get("student_name", ""), payload.get("answer", "")]]
    params = {
        "spreadsheetId": sheet_id,
        "range": "A:C",
        "valueInputOption": "RAW",
    }
    body = {"values": values}

    command = [
        "gws",
        "sheets",
        "spreadsheets",
        "values",
        "append",
        "--params",
        json.dumps(params),
        "--json",
        json.dumps(body),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return False, (result.stderr.strip() or result.stdout.strip() or "sheet append failed")
    return True, ""


def _fit_ascii(text: str, width: int) -> str:
    value = str(text)
    if len(value) <= width:
        return value.ljust(width)
    if width <= 3:
        return "." * width
    return (value[: width - 3] + "...")


def print_good_job_message(payload: dict, receipt_path: Path) -> None:
    inner_width = 58
    border = "+" + "-" * (inner_width + 2) + "+"

    def row(text: str) -> str:
        return f"| {_fit_ascii(text, inner_width)} |"

    print("")
    print(border)
    print(row("Good job! Your exercise was submitted."))
    print(border)
    print(row(f"Exercise: {payload.get('exercise_id', '')}"))
    print(row(f"Student: {payload.get('student_name', '')}"))
    print(row(f"Receipt: {receipt_path.name}"))
    print(row("Signal to Finn that you are finished."))
    print(border)


def interactive_payload(args: argparse.Namespace) -> dict:
    markdown_payload = {}
    if args.from_markdown:
        markdown_payload = parse_markdown_submission(Path(args.from_markdown))

    answer = args.answer.strip()
    if args.answer_file:
        answer = read_answer_from_file(Path(args.answer_file))

    payload = {
        "exercise_id": args.exercise_id or markdown_payload.get("exercise_id", ""),
        "student_name": args.student_name or markdown_payload.get("student_name", ""),
        "answer": answer or markdown_payload.get("answer", ""),
    }

    missing_any = any(not str(value).strip() for value in payload.values() if value is not None)
    if args.non_interactive or not sys.stdin.isatty() or not missing_any:
        return payload

    payload["exercise_id"] = _prompt("exercise_id", payload["exercise_id"] or "E1")
    payload["student_name"] = _prompt("student_name", payload["student_name"])
    if not payload["answer"]:
        payload["answer"] = _prompt("answer")
    return payload


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate exercise submission, save local JSON, and submit via prefilled URL or code."
    )
    parser.add_argument("--config", default=str(default_config_path()), help="Path to form_config.json")
    parser.add_argument("--submissions-dir", default=str(default_submissions_dir()), help="Local submission log dir")
    parser.add_argument(
        "--bootstrap-path",
        default=str(default_bootstrap_path()),
        help="Path to BOOTSTRAP.md used to infer submitter name",
    )

    parser.add_argument("--exercise-id", default="")
    parser.add_argument("--student-name", default="")
    parser.add_argument("--answer", default="")
    parser.add_argument("--answer-file", default="", help="Path to text/markdown file used as answer")
    parser.add_argument("--from-markdown", default="", help="Load fields from markdown front matter + body")

    parser.add_argument("--timeout", type=int, default=25, help="HTTP timeout seconds")
    parser.add_argument("--retry-count", type=int, default=2, help="Retry attempts after first attempt")
    parser.add_argument("--retry-backoff", type=float, default=1.5, help="Base backoff seconds")
    parser.add_argument(
        "--submit-mode",
        choices=["prefilled", "code"],
        default="prefilled",
        help="Submission mode: prefilled URL flow (default) or direct code POST",
    )
    parser.add_argument("--no-open", action="store_true", help="Do not open prefilled URL in browser")
    parser.add_argument("--non-interactive", action="store_true", help="Do not prompt for missing values")
    parser.add_argument("--no-submit", action="store_true", help="Do not POST to Google Form (validation only)")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    submissions_dir = Path(args.submissions_dir)
    config_path = Path(args.config)
    config = apply_env_overrides(load_config(config_path))
    config, form_url = ensure_form_url(config_path, config)
    if not form_url:
        print("ERROR: Missing google_form_url in config or GOOGLE_FORM_URL env var.")
        print(f"Expected config path: {config_path}")
        return 2

    payload = normalize_payload(interactive_payload(args))
    inferred_name = args.student_name.strip() or load_submitter_name(Path(args.bootstrap_path))
    payload = apply_submitter_name(payload, inferred_name)
    errors = validate_payload(payload)
    if errors:
        print("Submission validation failed:")
        for error in errors:
            print(f"- {error}")
        return 2

    saved_path = persist_submission(payload, submissions_dir)
    prefilled_url, missing_prefill = build_prefilled_url(form_url, config.get("field_ids", {}), payload)
    form_data, missing_ids = build_form_payload(config.get("field_ids", {}), payload)

    print(f"Saved local submission record: {saved_path}")
    if missing_prefill:
        print(f"Warning: these fields have no configured field ID: {', '.join(missing_prefill)}")

    print("Prefilled submission URL:")
    print(prefilled_url)

    required_missing = [key for key in REQUIRED_FIELDS if key in missing_ids]
    if required_missing:
        print("ERROR: Missing field IDs for required fields (cannot submit via code):")
        for key in required_missing:
            print(f"- {key}")
        print("Update config/form_config.json field_ids and retry.")
        return 2

    if args.no_submit:
        receipt_path = persist_receipt(
            submissions_dir=submissions_dir,
            saved_submission_path=saved_path,
            payload=payload,
            prefilled_url=prefilled_url,
            attempts=[],
            success=False,
            status=0,
            endpoint_url=build_form_response_url(form_url),
            error="Skipped submission (--no-submit)",
        )
        print(f"Wrote submission receipt: {receipt_path}")
        print("Skipped submission (--no-submit).")
        return 0

    if args.submit_mode == "prefilled":
        if not args.no_open:
            opened = webbrowser.open(prefilled_url)
            if opened:
                print("Opened prefilled form URL in browser.")
            else:
                print("Could not auto-open browser.")

        print("Submit via browser now (Cmd + left click opens the link if needed).")
        print(prefilled_url)

        if args.non_interactive or not sys.stdin.isatty():
            receipt_path = persist_receipt(
                submissions_dir=submissions_dir,
                saved_submission_path=saved_path,
                payload=payload,
                prefilled_url=prefilled_url,
                attempts=[],
                success=False,
                status=0,
                endpoint_url=form_url,
                error="Manual browser confirmation pending",
            )
            print(f"Wrote submission receipt: {receipt_path}")
            print("Manual confirmation pending. Re-run without --non-interactive to confirm.")
            return 0

        submitted = _prompt_yes_no("Did you submit successfully in the browser? (y/n)", True)
        if submitted:
            receipt_path = persist_receipt(
                submissions_dir=submissions_dir,
                saved_submission_path=saved_path,
                payload=payload,
                prefilled_url=prefilled_url,
                attempts=[],
                success=True,
                status=0,
                endpoint_url=form_url,
                error="",
            )
            print(f"Wrote submission receipt: {receipt_path}")
            print("Submission confirmed via prefilled Google Form.")
            print_good_job_message(payload=payload, receipt_path=receipt_path)
            return 0

        sheet_id = str(config.get("google_sheet_id", "")).strip() or _getenv("WORKSHOP_SPREADSHEET_ID")
        sheet_ok, sheet_error = maybe_append_to_sheet(payload, sheet_id)
        receipt_path = persist_receipt(
            submissions_dir=submissions_dir,
            saved_submission_path=saved_path,
            payload=payload,
            prefilled_url=prefilled_url,
            attempts=[],
            success=sheet_ok,
            status=0,
            endpoint_url=form_url,
            error="Browser submit reported failed",
        )
        if sheet_ok:
            print(f"Wrote submission receipt: {receipt_path}")
            print("Browser submission was not confirmed; code fallback to Google Sheets succeeded.")
            print_good_job_message(payload=payload, receipt_path=receipt_path)
            return 0

        print(f"Wrote submission receipt: {receipt_path}")
        if sheet_error:
            print(f"Sheet fallback also failed: {sheet_error}")
        print_copy_paste_fallback(payload=payload, prefilled_url=prefilled_url)
        return 2

    success, status, endpoint_url, attempts, error = submit_with_retry(
        form_url=form_url,
        form_data=form_data,
        retry_count=max(0, args.retry_count),
        backoff_seconds=max(0.0, args.retry_backoff),
        timeout=max(1, args.timeout),
    )

    receipt_path = persist_receipt(
        submissions_dir=submissions_dir,
        saved_submission_path=saved_path,
        payload=payload,
        prefilled_url=prefilled_url,
        attempts=attempts,
        success=success,
        status=status,
        endpoint_url=endpoint_url,
        error=error,
    )

    if success:
        print(f"Submitted via code. HTTP status: {status}")
        print(f"Submission endpoint: {endpoint_url}")
        print(f"Wrote submission receipt: {receipt_path}")
        print_good_job_message(payload=payload, receipt_path=receipt_path)
        return 0

    sheet_id = str(config.get("google_sheet_id", "")).strip() or _getenv("WORKSHOP_SPREADSHEET_ID")
    sheet_ok, sheet_error = maybe_append_to_sheet(payload, sheet_id)
    if sheet_ok:
        print(f"Wrote submission receipt: {receipt_path}")
        print("Form HTTP submission failed, but code fallback to Google Sheets succeeded.")
        print_good_job_message(payload=payload, receipt_path=receipt_path)
        return 0

    print(f"Wrote submission receipt: {receipt_path}")
    if sheet_error:
        print(f"Sheet fallback also failed: {sheet_error}")
    print_copy_paste_fallback(payload=payload, prefilled_url=prefilled_url)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
