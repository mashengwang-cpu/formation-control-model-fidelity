"""Check the selected stored traces; never run simulations or rewrite source data."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile

import numpy as np


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inside(root, relative):
    require(isinstance(relative, str) and relative, "Empty or non-string path")
    rel = PurePosixPath(relative.replace("\\", "/"))
    require(not rel.is_absolute() and ".." not in rel.parts and
            all(":" not in part for part in rel.parts), f"Unsafe path: {relative}")
    path = (root / Path(*rel.parts)).resolve()
    require(path.is_relative_to(root) and path.is_file(), f"Missing/escaping file: {relative}")
    return path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_arrays(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), f"Duplicate NPZ members: {path}")
        require(all(name.endswith(".npy") for name in names), f"Unexpected NPZ member: {path}")
        require(archive.testzip() is None, f"NPZ CRC failure: {path}")
    with np.load(path, allow_pickle=False) as archive:
        arrays = {name: archive[name] for name in archive.files}
    require(all(not a.dtype.hasobject for a in arrays.values()), f"Object array: {path}")
    return arrays


def metrics_from_arrays(arrays, metrics, duration):
    require(metrics.get("complete") is True, "Subset metric recomputation requires a complete run")
    time, errors = arrays["time"], arrays["error_norm"]
    require(time.ndim == 1 and len(time) >= 2 and np.all(np.diff(time) > 0), "Invalid time axis")
    require(errors.ndim == 2 and errors.shape[0] == len(time) and errors.shape[1] > 0,
            "Error/time shape mismatch")
    require(np.isfinite(duration) and duration > 0 and np.isclose(time[0], 0, atol=1e-12)
            and np.isclose(time[-1], duration, rtol=1e-12, atol=1e-12), "Incomplete time coverage")
    require(np.isfinite(time).all() and np.isfinite(errors).all() and (errors >= 0).all(),
            "Non-finite or negative tracking errors")
    values = {"J_m": float(np.trapezoid(errors.mean(axis=1), time) / duration)}
    for array_name, metric in [("actual_force_squared_integral", "force_effort_N2s"),
                               ("actual_moment_squared_integral", "moment_effort_N2m2s")]:
        a = arrays[array_name]
        require(a.shape == (len(time) - 1, errors.shape[1]) and np.isfinite(a).all(),
                f"Invalid integral array: {array_name}")
        values[metric] = float(a.sum())
    differences = {}
    for key, actual in values.items():
        expected = metrics[key]
        require(expected is not None and np.isfinite(expected), f"Non-finite recorded {key}")
        tolerance = 1e-12 if key == "J_m" else 1e-9
        require(np.isclose(actual, expected, rtol=1e-12, atol=tolerance),
                f"Metric mismatch {key}: array={actual!r}; record={expected!r}")
        differences[key] = actual - expected
    return {"recomputed": values, "array_minus_record": differences}


def verify(workspace, index):
    formal, numerical = index["formal"], index["numerical"]
    require(len(formal) == 56 and len(numerical) == 3, "Expected 56 formal jobs and 3 numerical cases")
    seen = set()
    formal_results, numerical_results = [], []
    for item in formal:
        record_path, trace_path = inside(workspace, item["record"]), inside(workspace, item["trace"])
        require(trace_path not in seen, "Duplicate trace would inflate subset size")
        seen.add(trace_path)
        record = read_json(record_path)
        expected_trace = (record_path.parent.parent / record["trace"]).resolve()
        require(expected_trace == trace_path, "Formal record/trace mapping mismatch")
        digest = sha256(trace_path)
        require(digest == record["trace_sha256"], "Formal trace SHA-256 mismatch")
        result = metrics_from_arrays(load_arrays(trace_path), record["metrics"], record["job"]["duration"])
        formal_results.append({"record": item["record"], "trace": item["trace"], "sha256": digest, **result})
    for item in numerical:
        record_path = inside(workspace, item["record"])
        record = read_json(record_path)
        case_id = record["case_id"]
        require(record_path.stem == case_id, "Numerical case ID mismatch")
        comparisons = record["comparisons"]
        require(len(comparisons) == 4, "Expected all four fixed steps")
        expected = {f"{case_id}_reference.npz": ("reference", record["reference"])}
        for comparison in comparisons:
            name = f"{case_id}_h{comparison['physics_dt']:.8f}.npz"
            require(name not in expected, "Duplicate numerical step")
            expected[name] = (comparison["physics_dt"], comparison["metrics"])
        paths = [inside(workspace, relative) for relative in item["arrays"]]
        require(len(paths) == 5 and {p.name for p in paths} == set(expected), "Incomplete numerical step mapping")
        results = []
        for relative, path in zip(item["arrays"], paths):
            require(path.parent == record_path.parent and path not in seen, "Invalid/duplicate numerical trace")
            seen.add(path)
            step, metrics = expected[path.name]
            results.append({"trace": relative, "step": step, "sha256": sha256(path),
                            **metrics_from_arrays(load_arrays(path), metrics, record["job"]["duration"])})
        production = [c for c in comparisons if np.isclose(c["physics_dt"], record["job"]["physics_dt"], atol=1e-14)]
        finest = min(comparisons, key=lambda c: c["physics_dt"])
        require(len(production) == 1 and production[0]["pass"] is False, "Expected retained production restriction")
        require(finest["pass"] is True, "Expected recorded finest-step pass")
        numerical_results.append({"record": item["record"], "case_id": case_id,
                                  "production_pass_recorded": False, "finest_pass_recorded": True,
                                  "arrays": results})
    require(len(seen) == 71, "Expected 71 unique NPZ files")
    return {"status": "pass", "formal_jobs": len(formal_results), "numerical_cases": len(numerical_results),
            "npz_files_crc_and_arrays_checked": len(seen), "formal": formal_results, "numerical": numerical_results,
            "scope": "Stored-array CRC, object rejection, mapping and scalar metric recomputation for this selected subset only.",
            "not_recomputed": ["State/attitude trajectory discrepancies and constraint-event equivalence between integrators.",
                               "Numerical pass decisions, their threshold logic, reference convergence or physical correctness.",
                               "Force and moment integrals from finer physical inputs: only saved interval integrals are summed.",
                               "Full-campaign trajectory validation or simulations; this selection is not a random sample."],
            "numerical_interpretation": "Production/finest pass flags are checked against the frozen record, not independently re-established."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True, help="Extracted outputs/workspace directory")
    parser.add_argument("--index", type=Path, default=Path(__file__).with_name("TRACE_SUBSET.json"))
    parser.add_argument("--output", type=Path, help="Optional new JSON report; must not be inside the frozen workspace")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    require(workspace.is_dir(), "Workspace directory does not exist")
    output = args.output.resolve() if args.output else None
    if output:
        require(not output.is_relative_to(workspace) and not output.exists(), "Output must be new and outside frozen workspace")
    try:
        result = verify(workspace, read_json(args.index))
    except (ValueError, KeyError, OSError, zipfile.BadZipFile, TypeError) as error:
        result = {"status": "fail", "error": str(error), "scope": "Selected stored traces only; no simulations were run."}
    text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
