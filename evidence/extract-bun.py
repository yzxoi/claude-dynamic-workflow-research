import hashlib
import json
import struct
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
binary = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'native-latest/package/claude'
destination = Path(sys.argv[2]) if len(sys.argv) > 2 else root / 'bun-files'
destination.mkdir(parents=True, exist_ok=True)
data = binary.read_bytes()
assert struct.unpack_from('<I', data)[0] == 0xFEEDFACF, 'Requires little-endian Mach-O64'
ncmds = struct.unpack_from('<I', data, 16)[0]
position = 32
section_offset = section_size = None
for _ in range(ncmds):
    command, command_size = struct.unpack_from('<II', data, position)
    assert command_size >= 8 and position + command_size <= len(data)
    if command == 0x19:
        nsects = struct.unpack_from('<I', data, position + 64)[0]
        for index in range(nsects):
            item = position + 72 + 80 * index
            name, segment, address, length, offset = struct.unpack_from('<16s16sQQI', data, item)
            if segment.rstrip(b'\0') == b'__BUN' and name.rstrip(b'\0') == b'__bun':
                section_offset, section_size = offset, length
    position += command_size
assert section_offset is not None
end = section_offset + section_size
assert data[end - 16:end] == b'\n---- Bun! ----\n'
byte_count, table_offset, table_bytes, entry, argv_offset, argv_bytes, flags = struct.unpack_from('<Q6I', data, end - 48)
base = section_offset + 8
assert table_bytes % 52 == 0
assert base + byte_count <= end - 48
manifest = []
for index in range(table_bytes // 52):
    fields = struct.unpack_from('<12I4B', data, base + table_offset + 52 * index)
    name_offset, name_bytes, contents_offset, contents_bytes, map_offset, map_bytes, cache_offset, cache_bytes, info_offset, info_bytes, origin_offset, origin_bytes, encoding, loader, module_format, side = fields
    assert name_offset + name_bytes <= byte_count and contents_offset + contents_bytes <= byte_count
    name = data[base + name_offset:base + name_offset + name_bytes].decode('utf8')
    assert name.startswith('/$bunfs/root/')
    relative = name.removeprefix('/$bunfs/root/')
    output = destination / relative
    assert relative and output.resolve().is_relative_to(destination.resolve())
    contents = data[base + contents_offset:base + contents_offset + contents_bytes]
    if contents_bytes:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(contents)
    manifest.append({'index': index, 'name': name, 'contents_offset': base + contents_offset, 'contents_bytes': contents_bytes, 'sha256': hashlib.sha256(contents).hexdigest(), 'sourcemap_bytes': map_bytes, 'bytecode_bytes': cache_bytes, 'encoding': encoding, 'loader': loader, 'format': module_format, 'path': str(output.relative_to(root)) if output.is_relative_to(root) else str(output)})
(root / 'bun-files-manifest.json').write_text(json.dumps(manifest, indent=2))
summary = {'binary': str(binary), 'binary_sha256': hashlib.sha256(data).hexdigest(), 'binary_bytes': len(data), 'section_offset': section_offset, 'section_size': section_size, 'payload_base': base, 'table_offset': table_offset, 'table_bytes': table_bytes, 'record_bytes': 52, 'files': len(manifest), 'entry_point': manifest[entry]['name'], 'flags': flags, 'source_maps': sum(x['sourcemap_bytes'] > 0 for x in manifest), 'contents_bytes': sum(x['contents_bytes'] for x in manifest)}
(root / 'bun-extraction.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary))
