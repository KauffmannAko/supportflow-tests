"""Daemon-free orchestration checks: python3 scripts/check-integration-runner.py."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

RUNNER = Path(__file__).with_name('test-integration.sh').resolve()


class IntegrationRunnerChecks(unittest.TestCase):
    def run_case(self, fail_stage='', fail_code=1, mode='test'):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docker = root / 'docker'
            docker.write_text('''#!/bin/sh
[ "$1" = compose ] || exit 91
shift
printf '%s\\n' "$*" >> "$CALL_LOG"
if [ -n "$FAIL_STAGE" ] && [ "$*" = "$FAIL_STAGE" ]; then
  exit "$FAIL_CODE"
fi
''')
            docker.chmod(0o755)
            env = dict(os.environ, PATH=f'{root}:{os.environ["PATH"]}',
                       CALL_LOG=str(root / 'calls'), FAIL_STAGE=fail_stage,
                       FAIL_CODE=str(fail_code))
            result = subprocess.run(['sh', str(RUNNER), mode], env=env, capture_output=True, text=True)
            return result.returncode, (root / 'calls').read_text().splitlines()

    def test_make_test_uses_runner(self):
        result = subprocess.run(['make', '--no-print-directory', '-n', 'test'],
                                cwd=RUNNER.parent.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), 'sh scripts/test-integration.sh')

    def test_make_up_uses_runner(self):
        result = subprocess.run(['make', '--no-print-directory', '-n', 'up'],
                                cwd=RUNNER.parent.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), 'sh scripts/test-integration.sh up')

    def test_up_builds_and_starts_without_tests_or_cleanup(self):
        status, calls = self.run_case(mode='up')
        self.assertEqual(status, 0)
        self.assertEqual(calls, [
            'config --quiet', 'pull api db', 'build api-tests',
            'up -d --wait --wait-timeout 120 db',
            'run --rm --no-deps -T api python manage.py migrate --noinput',
            'up -d --no-deps --wait --wait-timeout 120 api'])

    def test_up_failure_propagates(self):
        for stage in ('config --quiet', 'pull api db', 'build api-tests',
                      'up -d --wait --wait-timeout 120 db',
                      'run --rm --no-deps -T api python manage.py migrate --noinput',
                      'up -d --no-deps --wait --wait-timeout 120 api'):
            with self.subTest(stage=stage):
                status, calls = self.run_case(stage, 3, mode='up')
                self.assertEqual(status, 3)
                self.assertNotIn('run --rm --no-deps -T api-tests', calls)
                self.assertFalse(any(call.startswith(('down', 'stop', 'rm ')) for call in calls))

    def test_success_order(self):
        status, calls = self.run_case()
        self.assertEqual(status, 0)
        self.assertEqual(calls, [
            'config --quiet', 'pull api db', 'build api-tests',
            'up -d --wait --wait-timeout 120 db',
            'run --rm --no-deps -T api python manage.py migrate --noinput',
            'up -d --no-deps --wait --wait-timeout 120 api',
            'run --rm --no-deps -T api-tests'])

    def test_failures_report_without_cleanup(self):
        for stage, code in [
            ('up -d --wait --wait-timeout 120 db', 1),
            ('run --rm --no-deps -T api python manage.py migrate --noinput', 3),
            ('up -d --no-deps --wait --wait-timeout 120 api', 1),
            ('run --rm --no-deps -T api-tests', 5),
        ]:
            with self.subTest(stage=stage):
                status, calls = self.run_case(stage, code)
                self.assertEqual(status, code)
                self.assertEqual(calls[-2:], ['ps -a', 'logs --no-color --tail=100 db api'])
                self.assertEqual(calls.index(stage), len(calls) - 3)
                self.assertFalse(any(call.startswith(('down', 'stop', 'rm ')) for call in calls))

    def test_make_clean_removes_volumes(self):
        result = subprocess.run(['make', '--no-print-directory', '-n', 'clean'],
                                cwd=RUNNER.parent.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), 'docker compose down --volumes --remove-orphans')

    def test_validation_failure_creates_no_resources(self):
        status, calls = self.run_case('config --quiet', 2)
        self.assertEqual(status, 2)
        self.assertEqual(calls, ['config --quiet'])


if __name__ == '__main__':
    unittest.main()
