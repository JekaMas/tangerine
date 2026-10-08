"""Verify actual running image architectures without reading container secrets."""
import argparse
import json
import subprocess

from backup import COMPOSE


def inspect(project, expected):
    if project not in {'tangerine', 'tangerine-amd64'} or expected not in {'amd64', 'arm64'}:
        raise ValueError('Select the exact local foundation project and supported architecture.')
    results = []
    for service in ['postgres', 'minio', 'speech', 'api', 'web']:
        container = subprocess.check_output(COMPOSE + ['--project-name', project, 'ps', '-q', service], text=True, timeout=15).strip()
        if not container:
            raise ValueError('A required runtime container is absent.')
        image = subprocess.check_output(['docker', 'inspect', '--format', '{{.Image}}', container], text=True, timeout=15).strip()
        raw = subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{json .Architecture}}', image], text=True, timeout=15)
        arch = json.loads(raw)
        if arch != expected:
            raise ValueError('Runtime architecture mismatch.')
        results.append({'service': service, 'image_id': image, 'architecture': arch})
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--expected', required=True)
    args = parser.parse_args()
    print(json.dumps({'project': args.project, 'images': inspect(args.project, args.expected)}))
