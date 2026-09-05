import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

classes = Path('platform-results/classes')
classes.mkdir(parents=True, exist_ok=True)
if sys.argv[1] == 'build':
    excluded = {'test', 'testing', 'csm', 'davidson', 'demo', 'debugging', 'demoJS'}
    sources = [p for p in Path('src').rglob('*.java') if p.relative_to('src').parts[0] not in excluded]
    sources += list(Path('test/org/opensourcephysics/tools').glob('*.java'))
    argfile = Path('platform-results/sources.txt')
    argfile.write_text('\n'.join('"' + p.as_posix() + '"' for p in sources), encoding='utf-8')
    subprocess.run(['javac', '-encoding', 'UTF-8', '-Xlint:none', '-d', str(classes), '@' + str(argfile)], check=True)
    for root in [Path('src'), Path('resources')]:
        for p in root.rglob('*'):
            if p.is_file() and p.suffix != '.java':
                dest = classes / p.relative_to(root)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(p, dest)
else:
    failed = []
    for name in ['Precision', 'Report', 'Popup', 'DataToolLayout', 'Constraint']:
        cls = 'CurveFit' + name + 'Test'
        command = ['java', '-Duser.language=en', '-Duser.country=US', '-cp', str(classes), 'org.opensourcephysics.tools.' + cls]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', timeout=90)
            Path('platform-results', cls + '.log').write_text(result.stdout, encoding='utf-8')
            print(cls, 'exit', result.returncode, flush=True)
            print(result.stdout, flush=True)
            if result.returncode: failed.append(cls)
        except subprocess.TimeoutExpired as e:
            Path('platform-results', cls + '.log').write_text('TIMEOUT\n' + str(e.stdout), encoding='utf-8')
            failed.append(cls)
    sys.exit(bool(failed))
