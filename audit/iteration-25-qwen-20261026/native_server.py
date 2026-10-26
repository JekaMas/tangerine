"""Test/development binding of the unchanged native foreground HTTP owner."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'services/speech'))
from server import Handler, ThreadingHTTPServer

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8091)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print('Native speech owner listening on loopback port '+str(server.server_port), flush=True)
    server.serve_forever()
