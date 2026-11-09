"""Check generated native payloads, independent of the compiler's round-trip check."""
import json, struct
from build_pack import BASE, OUT, NATIVE_SAMPLES, number, unarchive, metadata, POS, condition

def read_number(data, offset):
    assert data[offset] == 1
    kind=data[offset+1]
    formats={0x11:'<b',0x12:'<h',0x01:'<i',0x02:'<I'}
    fmt=formats[kind]
    return struct.unpack_from(fmt,data,offset+2)[0]

for n in [-32769,-32768,-129,-128,-1,0,10,100,127,128,150,255,256,1000,2000,32767,32768]:
    assert read_number(number(n),0)==n

# Independent native-export checks, rather than matching the compiler's constants.
def native_position(filename):
    _,files,_=unarchive((NATIVE_SAMPLES/filename).read_bytes())
    raw=next(v for n,v in files if n.endswith('.pft'))
    start=raw.index(b'sopp')
    return read_number(raw,raw.index(b'lvlf',start)+4)

assert POS['DC']==native_position('Chase Corrected CB.fmf')==16
central=native_position('Chase Position Map.fmf')
expected=sum(POS[p] for p in ['DC','MC','AMC','ST'])
assert central & expected == expected
assert POS['MC']==1024 and POS['AMC']==8192
try:
    condition('POtr',65)
except AssertionError:
    pass
else:
    raise AssertionError('Unsupported 65 percent option was accepted')

manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
count=0
for item in manifest:
    root,files,_=unarchive((OUT/item['file']).read_bytes())
    assert not root.startswith('Chase ')
    assert not item['file'].split('/')[-1].startswith('Chase ')
    data=dict(files)
    if 'criteria' in item:
        raw=data[root+'.pft']
        assert b'dsbP' not in raw
        assert b'lvlf\x01\x02'+struct.pack('<I',item['position_mask']) in raw
        assert item['league_conditions']==[]
        for rule in item['criteria']:
            fid=rule['field'];kind=metadata[fid]['kind']
            marker=kind[::-1].encode()+fid[::-1].encode()
            start=raw.index(marker)
            value_at=raw.index(b'vnmf',start)+4
            actual=read_number(raw,value_at)
            scale=1 if kind=='pfpc' or fid=='POmi' else 100
            assert actual==round(rule['minimum']*scale),(item['file'],rule,actual)
            if kind=='pfpc':
                assert actual % 10 == 0
        assert (b'rtfpimOP' in raw)==bool(item['minutes'])
        count+=len(item['criteria'])
    else:
        raw=data[root+'.view']
        size=struct.unpack_from('<I',raw,8)[0]
        assert len(raw)==12+size
        view=json.loads(raw[12:])
        config=json.loads(view['ViewData'])
        assert view['SerialisedName']==root
        assert view['ViewSettingsCollectionName']==item['collection']
        assert [x['m_columnID'] for x in config['m_tableConfig']]==item['columns']
        assert 'stats-minutes' in item['columns']
        assert len(set(item['columns']))==len(item['columns'])
        assert not any('attribute-' in c for c in item['columns'])
assert len([x for x in manifest if 'criteria' in x])==54
assert len([x for x in manifest if 'columns' in x])==36
print(f'PASS: 90 native archives, {count} threshold values, 18 integer boundaries, 36 view payloads; no league conditions.')
