"""Compile every .po under locale/ to .mo using only the Python stdlib.

This avoids needing GNU gettext / msgfmt installed on Windows.
Run after editing any locale/<lang>/LC_MESSAGES/django.po:

    python scripts/compile_messages.py
"""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

LOCALE_DIR = Path(__file__).resolve().parent.parent / 'locale'

# ─── .po parser (handles msgid/msgstr, multi-line, escapes) ──────────────────
_ESCAPES = {'\\n': '\n', '\\t': '\t', '\\r': '\r', '\\"': '"', '\\\\': '\\'}


def _unescape(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            pair = s[i:i + 2]
            out.append(_ESCAPES.get(pair, pair[1]))
            i += 2
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def parse_po(path: Path) -> dict[str, str]:
    """Return msgid -> msgstr. Skips fuzzy entries and obsolete (#~) lines."""
    entries: dict[str, str] = {}
    msgid: list[str] | None = None
    msgstr: list[str] | None = None
    state: str | None = None  # 'id' or 'str'
    fuzzy = False

    text = path.read_text(encoding='utf-8')

    def flush() -> None:
        nonlocal msgid, msgstr, fuzzy
        if msgid is not None and msgstr is not None and not fuzzy:
            mid = ''.join(msgid)
            mstr = ''.join(msgstr)
            # Skip empty translations except the header (msgid "")
            if mstr or mid == '':
                entries[mid] = mstr
        msgid = msgstr = None
        fuzzy = False

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            flush()
            state = None
            continue
        if line.startswith('#'):
            if line.startswith('#~'):
                continue  # obsolete
            if line.startswith('#,') and 'fuzzy' in line:
                fuzzy = True
            continue

        m = re.match(r'msgid\s+"(.*)"$', line)
        if m:
            flush()
            msgid = [_unescape(m.group(1))]
            msgstr = None
            state = 'id'
            continue
        m = re.match(r'msgstr\s+"(.*)"$', line)
        if m:
            msgstr = [_unescape(m.group(1))]
            state = 'str'
            continue
        m = re.match(r'"(.*)"$', line)
        if m and state == 'id' and msgid is not None:
            msgid.append(_unescape(m.group(1)))
        elif m and state == 'str' and msgstr is not None:
            msgstr.append(_unescape(m.group(1)))

    flush()
    return entries


# ─── .mo writer (GNU gettext binary format, little-endian, no hash table) ───
def write_mo(entries: dict[str, str], path: Path) -> None:
    # Sort by msgid (gettext requires sorted) and filter empty translations,
    # but always include the header (msgid="") which carries metadata.
    keep = [(k, v) for k, v in entries.items() if v or k == '']
    keep.sort(key=lambda kv: kv[0])

    keys_b = [k.encode('utf-8') for k, _ in keep]
    vals_b = [v.encode('utf-8') for _, v in keep]
    n = len(keep)

    # 7 32-bit fields in the header.
    header_size = 7 * 4
    keys_table_offset = header_size
    vals_table_offset = keys_table_offset + n * 8
    strings_offset = vals_table_offset + n * 8

    keys_table: list[bytes] = []
    vals_table: list[bytes] = []
    strings_blob = bytearray()

    cursor = strings_offset
    for k in keys_b:
        keys_table.append(struct.pack('<II', len(k), cursor))
        strings_blob += k + b'\x00'
        cursor += len(k) + 1
    for v in vals_b:
        vals_table.append(struct.pack('<II', len(v), cursor))
        strings_blob += v + b'\x00'
        cursor += len(v) + 1

    header = struct.pack(
        '<IIIIIII',
        0x950412DE,           # magic (little-endian)
        0,                    # version
        n,                    # number of strings
        keys_table_offset,    # offset of msgid table
        vals_table_offset,    # offset of msgstr table
        0,                    # hash table size (0 = none)
        0,                    # hash table offset
    )
    path.write_bytes(header + b''.join(keys_table) + b''.join(vals_table) + bytes(strings_blob))


# ─── driver ──────────────────────────────────────────────────────────────────
def main() -> int:
    if not LOCALE_DIR.exists():
        print(f'no locale dir at {LOCALE_DIR}', file=sys.stderr)
        return 1

    pos = list(LOCALE_DIR.rglob('*.po'))
    if not pos:
        print('no .po files found')
        return 0

    for po in pos:
        entries = parse_po(po)
        translated = sum(1 for k, v in entries.items() if v and k != '')
        mo = po.with_suffix('.mo')
        write_mo(entries, mo)
        print(f'{po.relative_to(LOCALE_DIR.parent)} -> {mo.name}  ({translated} translated)')

    return 0


if __name__ == '__main__':
    sys.exit(main())
