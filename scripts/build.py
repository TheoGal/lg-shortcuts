#!/usr/bin/env python3
"""Build the LG Shortcuts packages for an LG webOS TV.

  python3 scripts/build.py

Writes one .ipk per tile into dist/. Never contacts a TV.
Needs: pip install -r requirements.txt (the Zig C compiler for the TV's ARM CPU).
"""
import argparse
import gzip
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
MTIME = 1704067200  # webOS rejects epoch-zero tar dates

# Each tile opens one of LG's own apps. The first app id webOS accepts is used:
# the ids differ between webOS versions.
SHORTCUTS = {
    'lgsettings': ['com.palm.app.settings', 'com.webos.app.settings'],
    'lgquicksettings': ['com.webos.app.quicksettings'],
    'lgnotifications': ['com.webos.app.notificationcenter'],
    'lglivetv': ['com.webos.app.livetv'],
}


# ---- IPK format: an ar archive of debian-binary, control.tar.gz, data.tar.gz ----

def ar(parts):
    out = bytearray(b'!<arch>\n')
    for name, data in parts.items():
        out += f'{name + "/":<16}{0:<12}{0:<6}{0:<6}{"100644":<8}{len(data):<10}`\n'.encode()
        out += data
        if len(data) % 2:
            out += b'\n'
    return bytes(out)


def tgz(files, executable=()):
    dirs = set()
    for name in files:
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts:
            raise ValueError('Unsafe path: ' + name)
        dirs.update(str(d) for d in p.parents if str(d) != '.')
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        for name in sorted(dirs):
            entry = tarfile.TarInfo(name)
            entry.mtime, entry.type, entry.mode = MTIME, tarfile.DIRTYPE, 0o755
            archive.addfile(entry)
        for name, data in sorted(files.items()):
            entry = tarfile.TarInfo(name)
            entry.mtime, entry.size = MTIME, len(data)
            entry.mode = 0o755 if name in executable else 0o644
            archive.addfile(entry, io.BytesIO(data))
    out = io.BytesIO()
    with gzip.GzipFile(filename='', fileobj=out, mode='wb', compresslevel=9, mtime=0) as packed:
        packed.write(raw.getvalue())
    return out.getvalue()


def ipk(app, version, files, executable=(), arch='all'):
    control = f'Package: {app}\nVersion: {version}\nArchitecture: {arch}\nMaintainer: Ted\nDescription: LG Shortcuts\n'
    control_tgz = tgz({'control': control.encode()})
    return ar({'debian-binary': b'2.0\n', 'control.tar.gz': control_tgz, 'data.tar.gz': tgz(files, executable)})


# ---- Build steps ----

def read_tree(folder):
    base = ROOT / folder
    return {p.relative_to(base).as_posix(): p.read_bytes() for p in sorted(base.rglob('*'))
            if p.is_file() and not p.is_symlink()}


def arm_cc(work, name, sources, *flags):
    """Compile a static ARM binary for the TV with the pinned Zig toolchain."""
    try:
        import ziglang
    except ImportError:
        raise SystemExit('Missing C compiler: pip install -r requirements.txt')
    zig = Path(ziglang.__file__).parent / ('zig.exe' if os.name == 'nt' else 'zig')
    env = dict(os.environ, ZIG_GLOBAL_CACHE_DIR=str(work / 'zig-global'), ZIG_LOCAL_CACHE_DIR=str(work / 'zig-local'))
    target = work / name
    subprocess.run([str(zig), 'cc', '-target', 'arm-linux-musleabi', '-Os', '-static', '-s',
                    *flags, *sources, '-o', str(target)], cwd=ROOT, env=env, check=True)
    return target.read_bytes()


def build_shortcut(work, folder, targets):
    files = read_tree('apps/' + folder)
    info = json.loads(files['appinfo.json'])
    app, version = info['id'], info['version']
    define = '-DTARGETS=' + ','.join('"%s"' % t for t in targets)
    files['launch'] = arm_cc(work, folder + '-launch', ['src/launch.c'], define)
    out = {'usr/palm/applications/' + app + '/' + n: b for n, b in files.items()}
    out['usr/palm/packages/' + app + '/packageinfo.json'] = json.dumps(
        {'id': app, 'version': version, 'app': app}).encode()
    return app, version, ipk(app, version, out, {'usr/palm/applications/' + app + '/launch'}, 'arm')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    work = ROOT / 'build'
    work.mkdir(exist_ok=True)
    for folder, targets in SHORTCUTS.items():
        app, version, data = build_shortcut(work, folder, targets)
        path = args.output / f'{app}_{version}_arm.ipk'
        path.write_bytes(data)
        print('Shortcut:', path)


if __name__ == '__main__':
    main()
