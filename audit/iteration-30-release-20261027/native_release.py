"""Manual I30 driver: real GitHub ZIP, unchanged Docker-only source launcher.

Only the developer harness requires Python. The downloaded app runs through its
documented shell launcher inside an existing Docker CLI image. A test-only
Compose overlay changes only the exposed port. Network forwarders preserve the
fixed product origin for the test browser and let the
unchanged readiness probe reach that exact web service. No replies are faked.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import urllib.request
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/iteration-30-release-20261027'
HERE = Path(__file__).resolve().parent
CLIENT = urllib.request.build_opener(urllib.request.ProxyHandler({}))
PYTHON = 'python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c'


def load(name):
    return json.loads((DATA / name).read_text())


def save(name, value):
    (DATA / name).write_text(json.dumps(value, indent=2) + '\n')


def run(args, label, check=True):
    with (DATA / (label + '.log')).open('ab') as output:
        result = subprocess.run(args, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT, timeout=1800)
    if check and result.returncode:
        raise RuntimeError(label + ' failed; inspect private log')
    return result.returncode


def output(args):
    return subprocess.check_output(args, cwd=ROOT, text=True, timeout=60).strip()


def command(state, action):
    return ['docker', 'exec', state['runner'], 'sh', 'scripts/tangerine', action]


def compose(state, *args):
    source = state['source_root']
    return ['docker', 'exec', state['runner'], 'docker', 'compose',
            '--env-file', source + '/.env', '--env-file', source + '/data/config/runtime.env',
            '-f', source + '/deploy/local/compose.yaml', *args]


def sql(state):
    query = """SELECT json_build_object(
      'workspace_count',(SELECT count(*) FROM workspaces),
      'workspace_id',(SELECT id::text FROM workspaces LIMIT 1),
      'provider_receipts',(SELECT count(*) FROM document WHERE kind='provider-receipt'),
      'exercise_count',(SELECT count(*) FROM exercise_catalog));"""
    return json.loads(output(compose(state, 'exec', '-T', 'postgres', 'psql', '-X', '-At',
                                     '-U', 'tangerine', '-d', 'tangerine', '-c', query)))


def configuration(state):
    with CLIENT.open(state['origin_url'] + '/api/v1/configuration', timeout=20) as reply:
        return json.load(reply)['configuration']


def volumes(state):
    return sorted(output(['docker', 'volume', 'ls', '-q', '--filter',
                          'label=com.docker.compose.project=' + state['project']]).splitlines())


def start():
    publication = load('publication.json')
    archive = DATA / publication['archive_file']
    assert archive.is_file() and publication['archive_url'].startswith('https://api.github.com/')
    unpacked = DATA / 'downloaded'; unpacked.mkdir()
    with zipfile.ZipFile(archive) as source:
        source.extractall(unpacked)
    roots = list(unpacked.iterdir()); assert len(roots) == 1
    source = roots[0]
    assert not (source / '.git').exists() and not (source / '.env').exists()
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]
    project = 'tangerine-i30-' + uuid.uuid4().hex[:8]
    fixtures = DATA / 'fixtures'; (fixtures / 'bin').mkdir(parents=True)
    shutil.copy2(HERE / 'launcher_fixture.sh', fixtures / 'bin/docker')
    (fixtures / 'bin/docker').chmod(0o755)
    shutil.copy2(HERE / 'readiness_forwarder.py', fixtures / 'readiness_forwarder.py')
    (fixtures / 'network-override.yaml').write_text('''services:
  web:
    ports: !override
      - "127.0.0.1:PORT:3000"
'''.replace('PORT', str(port)))
    state = dict(project=project, runner=project + '-launcher', proxy=project + '-probe-network',
                 source_root=str(source), origin_url='http://localhost:' + str(port), web_port=port,
                 archive_revision=publication['archive_revision'])
    save('stack.json', state)  # Durable cleanup identity before resource creation.
    run(['docker', 'run', '-d', '--name', state['runner'],
         '-v', '/var/run/docker.sock:/var/run/docker.sock', '-v', str(DATA) + ':' + str(DATA),
         '-v', str(fixtures) + ':/i30:ro', '-w', str(source),
         '-e', 'COMPOSE_PROJECT_NAME=' + project,
         '-e', 'PATH=/i30/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
         'docker:29-cli', 'sh', '-c', 'while :; do sleep 60; done'], 'runner-create')
    run(['docker', 'run', '-d', '--name', state['proxy'], '--network', 'container:' + state['runner'],
         '-v', str(fixtures) + ':/i30:ro', '-e', 'I30_WEB_PORT=' + str(port),
         PYTHON, 'python', '-B', '/i30/readiness_forwarder.py'], 'network-create')
    browser_network(state)
    code = run(command(state, 'start'), 'source-start', check=False)
    finish_start(state, code)


def browser_network(state):
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]
    state.update(gateway=state['project'] + '-browser-network', browser_port=port,
                 origin_url='http://localhost:' + str(port))
    save('stack.json', state)
    run(['docker', 'run', '-d', '--name', state['gateway'],
         '-v', str(DATA / 'fixtures') + ':/i30:ro',
         '-p', '127.0.0.1:' + str(port) + ':8088',
         '-e', 'I30_WEB_PORT=' + str(state['web_port']), '-e', 'I30_BROWSER_GATEWAY=1',
         '-e', 'I30_BROWSER_ORIGIN=' + state['origin_url'],
         PYTHON, 'python', '-B', '/i30/readiness_forwarder.py'], 'browser-network-create')


def resume_start():
    state = load('stack.json')
    shutil.copy2(HERE / 'readiness_forwarder.py', DATA / 'fixtures/readiness_forwarder.py')
    (DATA / 'fixtures/network-override.yaml').write_text('services:\n  web:\n    ports: !override\n      - "127.0.0.1:' + str(state['web_port']) + ':3000"\n')
    if not state.get('gateway'):
        browser_network(state)
    code = run(command(state, 'start'), 'source-start-recovered', check=False)
    finish_start(state, code, 'source-start-recovered.log')


def finish_start(state, code, log='source-start.log'):
    source = Path(state['source_root']); project = state['project']
    publication = load('publication.json')
    native = dict(source_root=str(source), archive_revision=publication['archive_revision'],
                  origin='Docker-only source launcher; isolated ports, source unchanged', start_exit=code)
    save('native.json', native)
    if code:
        raise RuntimeError('Unchanged downloaded launcher failed; private source-start.log retains failure')
    native['start_message'] = (DATA / log).read_text().splitlines()[-1]
    values = sql(state)
    for field in ['workspace_count', 'workspace_id', 'provider_receipts', 'exercise_count']:
        native[field + '_before'] = values[field]
    native['healthy_services'] = []
    for service in ['api', 'minio', 'postgres', 'speech', 'web']:
        health = output(['docker', 'inspect', '--format', '{{.State.Health.Status}}', project + '-' + service + '-1'])
        if health == 'healthy':
            native['healthy_services'].append(service)
    native['architecture'] = output(['docker', 'image', 'inspect', project + '-api:local', '--format', '{{.Architecture}}'])
    native['private_files'] = ['.env', 'data/config/runtime.env']
    native['private_modes'] = {p: oct((source / p).stat().st_mode & 0o777) for p in native['private_files']}
    native['runtime_sha_before'] = hashlib.sha256((source / 'data/config/runtime.env').read_bytes()).hexdigest()
    native['volumes_before_stop'] = volumes(state)
    save('native.json', native)
    print(json.dumps({'origin': state['origin_url'], 'project': project, 'healthy': native['healthy_services']}))


def restart():
    state = load('stack.json'); native = load('native.json')
    saved = configuration(state)
    assert saved['speech_profile'] == 'kokoro-controlled-v1', 'Save the test-owned choice through the normal configuration owner first'
    native['saved_configuration_sha256'] = saved['configuration_sha256']
    native['stop_exit'] = run(command(state, 'stop'), 'source-stop')
    native['volumes_while_stopped'] = volumes(state)
    assert native['volumes_before_stop'] == native['volumes_while_stopped']
    native['restart_exit'] = run(command(state, 'start'), 'source-restart')
    reopened = configuration(state); values = sql(state)
    native['reopened_configuration_sha256'] = reopened['configuration_sha256']
    native['reopened_speech_profile'] = reopened['speech_profile']
    for field in ['workspace_id', 'provider_receipts', 'exercise_count']:
        native[field + '_after'] = values[field]
    native['volumes_after_restart'] = volumes(state)
    native['runtime_secret_file_unchanged'] = native['runtime_sha_before'] == hashlib.sha256(
        (Path(state['source_root']) / 'data/config/runtime.env').read_bytes()).hexdigest()
    save('native.json', native)
    print(json.dumps({'restart_exit': native['restart_exit'], 'speech_profile': reopened['speech_profile'],
                      'model_calls': values['provider_receipts']}))


def missing_inputs():
    # Literal damaged distributions exercise the real launcher with actual Docker
    # preflight. The missing-source rejection happens before build/state mutation.
    required = ['.env.example', 'LICENSE', 'services/api/Dockerfile', 'services/api/go.mod',
                'services/api/go.sum', 'services/web/Dockerfile', 'services/web/package-lock.json',
                'services/speech/Dockerfile', 'deploy/local/minio.Dockerfile', 'deploy/local/compose.yaml']
    before = set(output(['docker', 'ps', '-aq']).splitlines()); rows = []
    for removed in ['LICENSE', 'services/web/package-lock.json', 'services/api/Dockerfile']:
        with tempfile.TemporaryDirectory(prefix='damaged-source-', dir=DATA) as directory:
            root = Path(directory)
            (root / 'scripts').mkdir(); (root / 'data/config').mkdir(parents=True)
            for script in ['tangerine', 'workspace-env']:
                shutil.copy2(ROOT / 'scripts' / script, root / 'scripts' / script)
            for name in required:
                path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text('source placeholder\n')
            private = [root / '.env', root / 'data/config/runtime.env']
            for path in private:
                path.write_text('# Constructed operator state; preserve on damaged source\n')
            (root / removed).unlink()
            result = subprocess.run(['sh', 'scripts/tangerine', 'start'], cwd=root,
                                    env=dict(os.environ, COMPOSE_PROJECT_NAME='tangerine-i30-damaged'),
                                    capture_output=True, text=True, timeout=60)
            rows.append(dict(removed=removed, exit=result.returncode, stderr=result.stderr,
                             private_state_unchanged=all(p.read_text() == '# Constructed operator state; preserve on damaged source\n' for p in private)))
    after = set(output(['docker', 'ps', '-aq']).splitlines())
    save('launcher-negative.json', {'missing_inputs': rows, 'created_containers': sorted(after - before)})
    print({'damaged_sources': len(rows), 'all_rejected': all(r['exit'] != 0 for r in rows)})


def cleanup():
    state = load('stack.json')
    run(compose(state, 'down', '--volumes', '--remove-orphans'), 'owned-cleanup', check=False)
    run(['docker', 'rm', '-f', state.get('gateway', state['proxy']), state['proxy'], state['runner']], 'runner-cleanup', check=False)


if __name__ == '__main__':
    {'start': start, 'resume-start': resume_start, 'restart': restart,
     'negative': missing_inputs, 'cleanup': cleanup}[sys.argv[1]]()
