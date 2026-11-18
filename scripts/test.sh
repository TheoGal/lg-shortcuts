#!/bin/sh
# Host test for the tile launcher: it falls through to the next app id when
# webOS refuses one, and fails when every id is refused.
# Needs a C compiler (gcc or cc). Run from the repository root.
set -e
CC=${CC:-cc}
tmp=build/test
mkdir -p "$tmp"
cat > "$tmp/fake-luna" <<'FAKE'
#!/bin/sh
printf '%s\n' "$*" >> "$(dirname "$0")/calls.log"
case "$*" in *first.app*) echo '{"returnValue":false}';; *) echo '{"returnValue":true}';; esac
FAKE
chmod +x "$tmp/fake-luna"
rm -f "$tmp/calls.log"
"$CC" -w -o "$tmp/launch" '-DTARGETS="first.app","second.app"' src/launch.c
SHORTCUT_LUNA_SEND="$tmp/fake-luna" "$tmp/launch"
grep -q 'second.app' "$tmp/calls.log"
if SHORTCUT_LUNA_SEND=/bin/false "$tmp/launch"; then echo "a tile must fail when every id is refused"; exit 1; fi
echo "ok launcher fallback"
