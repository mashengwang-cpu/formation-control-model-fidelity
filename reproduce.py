"""Offline package preparation and replay. No simulation runs by default."""
from pathlib import Path, PurePosixPath
import argparse, csv, gzip, hashlib, json, os, subprocess, sys, tarfile, zipfile, time

ROOT = Path(__file__).resolve().parent
WORK = ROOT / 'outputs' / 'workspace'
sys.dont_write_bytecode = True
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.environ.setdefault('MPLBACKEND', 'Agg')
os.environ['MPLCONFIGDIR'] = str(ROOT / 'outputs' / 'matplotlib_cache')
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def target(root, name):
    if '\\' in name or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts:
        raise ValueError('Unsafe member path: ' + name)
    path = (root / name).resolve()
    path.relative_to(root.resolve())
    return path


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def members():
    with gzip.open(ROOT / 'INPUT_MEMBERS.csv.gz', 'rt', encoding='utf-8', newline='') as stream:
        return {row['path']: row for row in csv.DictReader(stream)}


def verify():
    manifest = read(ROOT / 'SHA256SUMS.json')
    for name, expected in manifest.items():
        if sha(target(ROOT, name)) != expected:
            raise RuntimeError('Package hash mismatch: ' + name)
    for row in read(ROOT / 'PAYLOADS.json'):
        path = ROOT / 'payloads' / row['bundle']
        if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise RuntimeError('Payload mismatch: ' + path.name)
    print(f'Package hashes verified: {len(manifest)} files.', flush=True)


def prepare():
    verify()
    fingerprint = sha(ROOT / 'PAYLOADS.json') + sha(ROOT / 'INPUT_MEMBERS.csv.gz')
    marker = WORK / '.prepared.json'
    if marker.exists() and read(marker).get('fingerprint') == fingerprint:
        print('Using prepared workspace; verify-inputs rechecks every extracted input.', flush=True)
        return WORK
    expected = members()
    WORK.mkdir(parents=True, exist_ok=True)
    seen = set()
    def write(name, raw, bundle):
        row = expected.get(name)
        if row is None or row['bundle'] != bundle or name in seen:
            raise RuntimeError('Unexpected/duplicate member: ' + name)
        if len(raw) != int(row['bytes']) or hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise RuntimeError('Member checksum mismatch: ' + name)
        dst = target(WORK, name)
        if dst.exists() and sha(dst) != row['sha256']:
            raise RuntimeError('Existing workspace file differs; use a fresh package extraction: ' + name)
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(raw)
        seen.add(name)
    for row in read(ROOT / 'PAYLOADS.json'):
        path = ROOT / 'payloads' / row['bundle']
        if path.name == 'baseline.zip':
            with zipfile.ZipFile(path) as archive:
                for item in archive.infolist():
                    if item.is_dir():
                        continue
                    if not item.filename.startswith('formation-control-repro/'):
                        raise RuntimeError('Unexpected baseline prefix')
                    dst = target(WORK / 'baseline', item.filename.split('/', 1)[1])
                    raw = archive.read(item)
                    if dst.exists() and dst.read_bytes() != raw:
                        raise RuntimeError('Baseline workspace was modified: ' + item.filename)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if not dst.exists():
                        dst.write_bytes(raw)
        elif path.suffix == '.zip':
            with zipfile.ZipFile(path) as archive:
                for item in archive.infolist():
                    if item.is_dir():
                        raise RuntimeError('Unexpected directory member')
                    write(item.filename, archive.read(item), path.name)
        else:
            with tarfile.open(path, 'r:xz') as archive:
                for item in archive:
                    if not item.isfile():
                        raise RuntimeError('Only regular-file tar members are allowed')
                    write(item.name, archive.extractfile(item).read(), path.name)
        print('Prepared ' + path.name, flush=True)
    if seen != set(expected):
        raise RuntimeError('Input member set incomplete')
    marker.write_text(json.dumps({'fingerprint': fingerprint, 'members': len(seen)}), encoding='utf-8')
    return WORK


def verify_inputs():
    work = prepare()
    for name, row in members().items():
        if sha(target(work, name)) != row['sha256']:
            raise RuntimeError('Extracted input changed: ' + name)
    call(work / 'baseline', ['reproduce.py', 'verify'], 'baseline_hashes')
    print(f'Extracted input hashes verified: {len(members())} plus baseline.', flush=True)


def call(cwd, args, log):
    output = ROOT / 'outputs' / 'validation'
    output.mkdir(parents=True, exist_ok=True)
    print('+ python -B ' + ' '.join(map(str, args)), flush=True)
    result = subprocess.run([sys.executable, '-B', '-X', 'utf8', *map(str, args)], cwd=cwd,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / (log + '.txt')).write_bytes(result.stdout)
    print(result.stdout.decode('utf-8', errors='replace'), flush=True)
    if result.returncode:
        raise RuntimeError(f'{log} exited with {result.returncode}')


def run(command, dpi):
    if command == 'verify':
        verify()
        return
    if command == 'verify-inputs':
        verify_inputs()
        return
    work = prepare()
    if command == 'prepare':
        return
    if command in ('latest-results', 'latest-all'):
        call(work / 'campaign', ['analyse_campaign.py', '--scope', 'all'], 'latest_results')
        rows = {n:r for n,r in members().items() if n.startswith('campaign/analysis/')}
        assert len(rows) == 31
        for name, row in rows.items():
            if sha(work / name) != row['sha256']:
                raise RuntimeError('Recomputed output differs: ' + name)
        print('All 31 latest analysis outputs are byte-identical.', flush=True)
    if command in ('latest-audit', 'latest-all'):
        call(work / 'campaign', ['audit_completed_campaign.py', '--hash-only'], 'latest_sources')
        for rep in (1, 2, 3):
            call(work / 'campaign', ['audit_completed_campaign.py', '--scope', 'search', '--repetition', str(rep)], f'search_{rep}_audit')
        call(work / 'campaign', ['audit_completed_campaign.py', '--scope', 'factorial'], 'factorial_audit')
    if command in ('latest-figures', 'latest-all'):
        call(work / 'new_figures', ['plot_new_results.py', '--output', ROOT/'outputs/figures', '--dpi', str(dpi)], 'latest_figures')
    if command in ('traces', 'latest-all'):
        report = ROOT/'outputs/validation'/f'trace_subset_{time.time_ns()}.json'
        call(ROOT, ['verify_trace_subset.py', '--workspace', work, '--output', report], 'trace_subset')
    if command == 'previous-results':
        os.environ['FORMATION_REPRO_PACKAGE'] = str(work/'baseline')
        for script in ('direct_contrasts.py', 'verify_analysis.py', 'selection_audit.py', 'otter_allocation_check.py'):
            call(work/'previous_analysis', [script], script[:-3])
    if command.startswith('baseline-'):
        call(work/'baseline', ['reproduce.py', command.removeprefix('baseline-')], command)


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Do not use Python -O; scientific contract assertions are required.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['verify','prepare','verify-inputs','latest-results','latest-audit','latest-figures','traces','latest-all','previous-results','baseline-results','baseline-selection','baseline-figures','baseline-test','baseline-smoke'])
    parser.add_argument('--dpi', type=int, default=150)
    args = parser.parse_args()
    if args.dpi <= 0:
        parser.error('--dpi must be positive')
    run(args.command, args.dpi)
