// Portable launcher: explicit PYTHON, Codex's bundled Python, then installed Python.
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { spawn, spawnSync } from 'node:child_process';

const bundled = process.platform === 'win32' && process.env.USERPROFILE
  ? join(process.env.USERPROFILE, '.cache', 'codex-runtimes', 'codex-primary-runtime', 'dependencies', 'python', 'python.exe') : null;
const candidates = [...new Set([process.env.PYTHON, bundled && existsSync(bundled) ? bundled : null, 'python3', 'python'].filter(Boolean))];
const executable = candidates.find(candidate => {
  const probe = spawnSync(candidate, ['--version'], { encoding: 'utf8', windowsHide: true, timeout: 5000 });
  const match = `${probe.stdout ?? ''}${probe.stderr ?? ''}`.match(/Python (\d+)\.(\d+)/);
  return probe.status === 0 && match && (Number(match[1]) > 3 || (Number(match[1]) === 3 && Number(match[2]) >= 11));
});

if (!executable) {
  console.error('Python 3.11+ was not found. Set PYTHON to a Python executable or install Python 3.11+. No pip packages are needed.');
  process.exit(1);
}
const child = spawn(executable, ['-u', ...process.argv.slice(2)], { stdio: 'inherit', windowsHide: true });
child.on('error', error => { console.error(error.message); process.exitCode = 1; });
child.on('exit', code => { process.exitCode = code ?? 1; });
process.on('SIGINT', () => child.kill('SIGINT'));
process.on('SIGTERM', () => child.kill('SIGTERM'));
