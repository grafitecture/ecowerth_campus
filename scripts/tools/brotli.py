"""Minimaler Ersatz für das Python-Modul `brotli`, damit fontTools WOFF2 lesen und schreiben kann.

In dieser Umgebung lässt sich `brotli` nicht nachinstallieren. Node bringt Brotli in
`zlib` mit; dieses Modul reicht die Daten an Node weiter.
"""
import subprocess

MODE_GENERIC = 0
MODE_TEXT = 1
MODE_FONT = 2

_JS = r"""
const z = require('zlib');
const fs = require('fs');
const [op, mode, quality] = process.argv.slice(1);
const input = fs.readFileSync(0);
const out = op === 'c'
  ? z.brotliCompressSync(input, { params: {
      [z.constants.BROTLI_PARAM_MODE]: Number(mode),
      [z.constants.BROTLI_PARAM_QUALITY]: Number(quality),
      [z.constants.BROTLI_PARAM_SIZE_HINT]: input.length,
    } })
  : z.brotliDecompressSync(input);
process.stdout.write(out);
"""


class error(Exception):
    pass


def _run(args, data):
    try:
        return subprocess.run(['node', '-e', _JS, *args], input=data, capture_output=True, check=True).stdout
    except subprocess.CalledProcessError as exc:
        raise error(exc.stderr.decode('utf-8', 'replace')) from exc


def compress(data, mode=MODE_GENERIC, quality=11, lgwin=22, lgblock=0):
    return _run(['c', str(mode), str(quality)], bytes(data))


def decompress(data):
    return _run(['d'], bytes(data))
