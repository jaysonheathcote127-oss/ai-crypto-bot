"""Run frozen experiment tests in separate interpreters to avoid import leakage."""
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent
    failures = []
    for path in sorted(root.glob('test_*.py')):
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', path.stem, '-v'],
            cwd=root, capture_output=True, text=True,
        )
        print(f'{path.name}: {"PASS" if result.returncode == 0 else "FAIL"}', flush=True)
        print(result.stdout + result.stderr, flush=True)
        if result.returncode:
            failures.append(path.name)
    print(f'Failed modules: {failures}', flush=True)
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
