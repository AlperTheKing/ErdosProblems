import os
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
root = pathlib.Path.cwd()
env = os.environ.copy()
env['LEAN_PATH'] = str((root / 'tmp' / 'claude_lean_o_base_v1').resolve()) + os.pathsep + env.get('LEAN_PATH', '')
lean_root = root / 'problems' / '23' / 'lean'
file_path = root / 'problems' / '23' / 'lean' / 'Erdos23Delta0' / 'WalkParity.lean'
proc = subprocess.run(['lake', 'env', 'lean', f'--root={lean_root}', str(file_path)], cwd=root / 'formal-conjectures', env=env, text=True, encoding='utf-8', errors='replace', capture_output=True, timeout=120)
print('RC', proc.returncode)
print(proc.stdout[-8000:])
print(proc.stderr[-8000:])
sys.exit(proc.returncode)
