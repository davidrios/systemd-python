#!/usr/bin/env python3
from configparser import RawConfigParser
from pathlib import Path
from shutil import chown


def main():
    econf = RawConfigParser()
    econf.read('/etc/uwsgi/emperor.ini')

    vdefconf = RawConfigParser()
    vdefconf.read(econf.get('uwsgi', 'vassals-include'))

    emperor_dir = econf.get('uwsgi', 'emperor')
    errors = []
    for fname in Path(emperor_dir).iterdir():
        if not (fname.is_file() and fname.suffix == '.ini'):
            continue

        vconf = RawConfigParser()
        vconf.read(fname)

        vname = fname.stem

        if not vconf.has_option('uwsgi', 'vassal-name'):
            errors.append('A "vassal-name" key is required in the uWSGI configuration for app "{}".'.format(vname))
            continue

        uid = vconf.get('uwsgi', 'uid')
        gid = vconf.get('uwsgi', 'gid')
        pidfile = vdefconf.get('uwsgi', 'pidfile')

        runpath = Path(pidfile.replace('%(vassal-name)', vname)).parent

        runpath.mkdir(parents=True, exist_ok=True)
        chown(str(runpath), uid, gid)

    if errors:
        raise Exception('\n'.join(errors))


if __name__ == '__main__':
    main()
