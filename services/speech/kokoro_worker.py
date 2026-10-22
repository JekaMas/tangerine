"""Reuse local model memory; each foreground caller still owns cancellation."""
import atexit
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import sys
import threading
import time


class KokoroWorker:
    def __init__(self, command=None):
        self.command = command or [sys.executable, '-B', str(Path(__file__).with_name('backends.py')), '--kokoro-worker']
        self.lock = threading.Lock()
        self.process = None

    def close(self):
        process, self.process = self.process, None
        if process is None:
            return
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.wait(timeout=5)
        for stream in (process.stdin, process.stdout):
            stream.close()

    def execute(self, packet, timeout, disconnected):
        deadline = time.monotonic() + timeout

        def active():
            if disconnected():
                raise ConnectionAbortedError()
            if time.monotonic() >= deadline:
                raise subprocess.TimeoutExpired(self.command, timeout)

        while not self.lock.acquire(timeout=.1):
            active()
        reader = None
        try:
            active()
            if self.process is None or self.process.poll() is not None:
                self.close()
                self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                stderr=subprocess.DEVNULL, start_new_session=True)
            process = self.process
            complete = queue.Queue()

            def exchange():
                try:
                    process.stdin.write(json.dumps(packet, ensure_ascii=False).encode() + b'\n')
                    process.stdin.flush()
                    complete.put(json.loads(process.stdout.readline()))
                except (OSError, ValueError) as error:
                    complete.put(error)

            reader = threading.Thread(target=exchange, daemon=True)
            reader.start()
            while True:
                try:
                    result = complete.get(timeout=.1)
                    if isinstance(result, Exception):
                        self.close()
                        return {'error': 'SYNTHESIS_FAILED'}
                    return result
                except queue.Empty:
                    active()
        except (OSError, subprocess.TimeoutExpired):
            self.close()
            raise
        finally:
            if reader is not None:
                reader.join(timeout=5)
            self.lock.release()


KOKORO = KokoroWorker()
atexit.register(KOKORO.close)
