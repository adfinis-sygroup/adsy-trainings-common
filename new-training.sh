#!/usr/bin/env bash

set -euf -o pipefail
trap fail SIGHUP SIGINT SIGTERM ERR

fail() {
    echo "Usage: $0 <training> <module> <id>" >&2
    exit 1
}

if [ $# -ne 3 ]; then
    fail
fi

TRAINING="$1"
MODULE="$2"
ID="$3"

DIR="${TRAINING}/${ID}_${MODULE}"
mkdir -p "$DIR"
cp skeleton/0000_skeleton/modul_skeleton_0000.yml "${DIR}/modul_${MODULE}_${ID}.yml"
cp skeleton/0000_skeleton/modul_skeleton_0000.md "${DIR}/modul_${MODULE}_${ID}.md"
cp -r skeleton/0000_skeleton/static "$DIR"

sed -i  -e "s/^Name: .*/Name: ${MODULE}/" \
        -e "s/^Area: .*/Area: ${TRAINING}/" \
        -e "s/^ID: .*/ID: ${ID}/" \
        -e "s/- Presentation: .*/- Presentation: modul_${MODULE}_${ID}_01_slides.html/" \
        -e "s/- Hands_On: .*/- Hands_On: modul_${MODULE}_${ID}_02_handson.html/" \
        "${DIR}/modul_${MODULE}_${ID}.yml"

exit 0
