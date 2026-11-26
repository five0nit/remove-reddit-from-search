"""Load the packaged extension into disposable Chromium against an offline fixture."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import ssl
import subprocess
import tempfile
import threading
import time
from urllib.parse import urlencode
from urllib.request import urlopen
from zipfile import ZipFile

from websockets.sync.client import connect


class SearchFixture(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'<!doctype html><title>Offline search fixture</title>')

    def log_message(self, *args):
        pass


def check(ws, url, expected):
    counter = 0

    def call(method, **params):
        nonlocal counter
        counter += 1
        ws.send(json.dumps({'id': counter, 'method': method, 'params': params}))
        while True:
            message = json.loads(ws.recv(timeout=5))
            if message.get('id') == counter:
                assert 'error' not in message, message
                return message['result']

    nav = call('Page.navigate', url=url)
    assert not nav.get('errorText'), nav
    target = [expected, 'Offline search fixture']
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        state = call('Runtime.evaluate', expression='[location.href, document.title]', returnByValue=True)
        if state.get('result', {}).get('value') == target:
            break
        time.sleep(0.05)
    time.sleep(0.3)
    state = call('Runtime.evaluate', expression='[location.href, document.title]', returnByValue=True)
    assert state['result']['value'] == target, state
    print(f'PASS {url} -> {expected}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('chromium')
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='no-reddit-search-browser-', ignore_cleanup_errors=True) as temp:
        root = Path(temp)
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-subj', '/CN=offline-test',
                        '-days', '1', '-keyout', str(root / 'key.pem'), '-out', str(root / 'cert.pem')],
                       check=True, capture_output=True)
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls.load_cert_chain(root / 'cert.pem', root / 'key.pem')
        unpacked = root / 'unpacked'
        with ZipFile(args.archive) as archive:
            archive.extractall(unpacked)
        candidates = [unpacked / 'manifest.json', *unpacked.glob('*/manifest.json')]
        manifests = [path for path in candidates if path.is_file()]
        if len(manifests) != 1:
            raise ValueError('Expected exactly one manifest at the ZIP root or in a top-level folder')
        extension = manifests[0].parent
        profile = root / 'profile'
        with ThreadingHTTPServer(('127.0.0.1', 0), SearchFixture) as server:
            server.socket = tls.wrap_socket(server.socket, server_side=True)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            flags = [args.chromium, '--headless', '--no-sandbox', '--disable-background-networking',
                     '--no-first-run', '--no-default-browser-check', '--remote-debugging-port=0',
                     f'--user-data-dir={profile}', f'--disable-extensions-except={extension}',
                     f'--load-extension={extension}', '--no-proxy-server', '--ignore-certificate-errors',
                     f'--host-resolver-rules=MAP * 127.0.0.1:{server.server_port}', 'about:blank']
            with (root / 'chromium.log').open('w+') as log, subprocess.Popen(flags, stdout=log, stderr=log) as chrome:
                try:
                    port_file = profile / 'DevToolsActivePort'
                    deadline = time.monotonic() + 8
                    while not port_file.exists() and chrome.poll() is None and time.monotonic() < deadline:
                        time.sleep(0.05)
                    if not port_file.exists():
                        log.seek(0)
                        raise RuntimeError(log.read())
                    port = port_file.read_text().splitlines()[0]
                    with urlopen(f'http://127.0.0.1:{port}/json/list', timeout=2) as response:
                        pages = json.load(response)
                    with connect(next(p['webSocketDebuggerUrl'] for p in pages if p['type'] == 'page')) as ws:
                        for host, path, q, filters in [
                            ('www.google.com', 'search', 'mechanical keyboards', True),
                            ('www.google.com.au', 'search', 'van repair', True),
                            ('www.google.com', 'search', 'van repair -site:reddit.com', False),
                            ('www.google.com', 'searching', 'van repair', False),
                            ('example.com', 'search', 'van repair', False),
                        ]:
                            base = f'https://{host}/{path}?'
                            original = base + urlencode({'q': q, 'start': '10'})
                            expected = base + urlencode({'q': q + ' -site:reddit.com', 'start': '10'}) if filters else original
                            check(ws, original, expected)
                finally:
                    chrome.terminate()
                    try:
                        chrome.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        chrome.kill()
                        chrome.wait()
                    server.shutdown()


if __name__ == '__main__':
    main()
