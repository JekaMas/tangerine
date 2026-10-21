"""Verify actual running image architectures without reading container secrets."""
import argparse
import json
import subprocess


def inspect(project, expected):
    if not project or expected not in {'amd64', 'arm64'}:
        raise ValueError('Select the actual Compose project and supported architecture.')
    results = []
    for service in ['postgres', 'minio', 'speech', 'api', 'web']:
        containers = subprocess.check_output(['docker','ps','-q','--filter','label=com.docker.compose.project='+project,'--filter','label=com.docker.compose.service='+service], text=True, timeout=15).split()
        if len(containers) != 1:
            raise ValueError('Select one actual running container per required service.')
        container = containers[0]
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
