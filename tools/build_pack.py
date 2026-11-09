"""Build native league-free filters and views from user exports and game metadata."""
from pathlib import Path
from compression import zstd
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import csv, hashlib, json, os, re, struct, zipfile
import xml.etree.ElementTree as ET

BASE = Path(os.environ.get('FM27_PACK_PROJECT', Path(__file__).resolve().parents[1]))
GAME = Path(os.environ.get('FM27_USER_DIR', Path.home() / 'Documents' / 'Sports Interactive' / 'Football Manager 27'))
WORK = Path(os.environ.get('FM27_BUILD_INPUTS', BASE / 'private-inputs'))
NATIVE_SAMPLES = Path(os.environ.get('FM27_NATIVE_SAMPLES', WORK / 'native-samples'))
OUT = BASE / 'pack'

def string(value):
    value = value.encode('utf-8')
    return struct.pack('<I', len(value)) + value

def number(value):
    # Native compact integers are signed, including the one-byte representation.
    if -128 <= value <= 127:
        return b'\x01\x11' + struct.pack('<b', value)
    if -32768 <= value <= 32767:
        return b'\x01\x12' + struct.pack('<h', value)
    return b'\x01\x01' + struct.pack('<i', value)

def unarchive(data):
    footer_at = struct.unpack_from('<Q', data, 9)[0]
    manifest = zstd.decompress(data[footer_at + 18:])
    cursor = 0
    files = []
    def read_string():
        nonlocal cursor
        size = struct.unpack_from('<I', manifest, cursor)[0]
        cursor += 4
        value = manifest[cursor:cursor+size].decode('utf-8')
        cursor += size
        return value
    def directory(prefix=''):
        nonlocal cursor
        count = struct.unpack_from('<I', manifest, cursor)[0]
        cursor += 4
        for _ in range(count):
            name, ext = read_string(), read_string()
            offset, size, raw, _, _ = struct.unpack_from('<QQQqq', manifest, cursor)
            cursor += 40
            block = data[26+offset:26+offset+size]
            if data[2:6] == b'afe.':
                kl, il = struct.unpack_from('<II', block)
                dec = Cipher(algorithms.AES(block[8:8+kl]), modes.CTR(block[8+kl:8+kl+il])).decryptor()
                block = dec.update(block[8+kl+il:]) + dec.finalize()
            content = zstd.decompress(block)
            assert len(content) == raw
            files.append((prefix+name+ext, content))
        count = struct.unpack_from('<I', manifest, cursor)[0]
        cursor += 4
        for _ in range(count):
            directory(prefix+read_string()+'/')
    root = read_string()
    directory()
    assert cursor == len(manifest)
    return root, files, data[footer_at:footer_at+18]

sample = (NATIVE_SAMPLES/'Chase Sample WB.fmf').read_bytes()
_, native_files, FOOTER = unarchive(sample)
native = dict(native_files)
PFT = next(value for key, value in native_files if key.endswith('.pft'))
IMAGE = native['image.img']
DETAILS = native['_data/details.aom']
OLD_NAME = 'Chase Sample WB'
PREFIX = PFT[:PFT.index(b'rtfprdoP')]
assert PREFIX.count(b'\x01\x00\x01\x15\0\0\0') == 1
POSITION_TOKEN = b'lvlf\x01\x02\x20\0\0\0'
assert PREFIX.count(POSITION_TOKEN) == 1

metadata = {}
for rec in ET.parse(WORK/'person_filter_metadata.xml').findall('./list/record'):
    field, label = rec.find("integer[@id='id']"), rec.find("translation[@id='name']")
    kind = rec.find("record[@id='search_filter']/integer")
    if field is not None and label is not None and kind is not None:
        metadata[field.get('value')] = dict(name=re.split(r'\[', label.get('value'))[0],
            translation=int(label.get('translation_id')), kind=kind.get('value'))

def condition(field, threshold):
    item = metadata[field]
    percent = item['kind'] == 'pfpc'
    assert item['kind'] in ('pfpc', 'pftr')
    if percent:
        assert threshold % 10 == 0, ('Unsupported percentage option', field, threshold)
    scale = 1 if percent or field == 'POmi' else 100
    value = round(threshold * scale)
    maximum = 100 if percent else max(5000 if field == 'POmi' else 10000, value)
    props = (b'vnmf'+number(value) + b'lvlf'+number(value if percent else 0)
        + b'vxmf'+number(maximum) + b'diTR\x01\x02'+struct.pack('<I', item['translation'])
        + b'  di\x01\x02'+field[::-1].encode() + b'negm\x01\x03\x00')
    return item['kind'][::-1].encode()+field[::-1].encode()+b'\x01\x01'+struct.pack('<I', 4)+b'\x01'+struct.pack('<I', 6)+props

def archive(name, files):
    blocks, entries, offset = [], [], 0
    for path, raw in files:
        key, iv = os.urandom(16), os.urandom(16)
        enc = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
        block = struct.pack('<II',16,16)+key+iv+enc.update(zstd.compress(raw))+enc.finalize()
        p = Path(path)
        entry = string(p.stem)+string(p.suffix)+struct.pack('<QQQqq',offset,len(block),len(raw),0,0)
        entries.append((path,entry));blocks.append(block);offset += len(block)
    main = [entry for path,entry in entries if '/' not in path]
    sub = [entry for path,entry in entries if path.startswith('_data/')]
    manifest = (string(name)+struct.pack('<I',len(main))+b''.join(main)
        +struct.pack('<I',1)+string('_data')+struct.pack('<I',len(sub))+b''.join(sub)+struct.pack('<I',0))
    header = bytearray(sample[:26]);struct.pack_into('<Q',header,9,26+offset)
    packed = bytes(header)+b''.join(blocks)+FOOTER+zstd.compress(manifest)
    decoded_name, decoded_files, _ = unarchive(packed)
    assert decoded_name == name and decoded_files == files
    return packed

def details(name, handler='PLAYER_SEARCH_FILTER_TYPE_HANDLER'):
    data = DETAILS.replace(string(OLD_NAME),string(name))
    if handler != 'PLAYER_SEARCH_FILTER_TYPE_HANDLER':
        data = data.replace(string('PLAYER_SEARCH_FILTER_TYPE_HANDLER'),string(handler))
    return data

# Filter position masks differ from tactic masks. Corrected CB and central-position
# native exports establish the central flags; do not use the earlier guessed map.
POS = dict(GK=1, DR=4, DL=8, DC=16, WBR=32, WBL=64, DM=128,
           MR=256, ML=512, MC=1024, AMR=2048, AML=4096, AMC=8192, ST=16384)

# Core floors are conservative starting points, except the screenshot references.
# Additional metrics stay in the views, where they can be evaluated in context.
PROFILES = [
 ('GK Shot Stopper',['GK'],[('Pxg9',0.10)],['POs%','POx%','Popa'],'Own provisional'),
 ('CB Defensive',['DC'],[('POhr',60),('POHg',2),('POtr',70)],['POiG','POsb','POc9'],'Own provisional'),
 ('CB Ball Playing',['DC'],[('PGR9',3),('Popa',80),('POtr',60)],['POhr','POiG','POL9'],'Own provisional; tackle 60 is confirmed selectable in user export'),
 ('FB Defensive',['DL','DR'],[('POtr',70),('POiG',1),('POW9',3)],['Popa','POhr','POL9'],'Own provisional'),
 ('WB Attacking',['WBL','WBR'],[('Podr',1.5),('POSp',10),('POP9',1),('Pop9',1),('PxA9',0.10)],['POtr','POiG'],'User screenshot thresholds'),
 ('FB Inverted',['DL','DR','WBL','WBR'],[('PGR9',3),('Popa',80),('POiG',0.75)],['Podr','POW9','POL9'],'Own provisional'),
 ('DM Holding',['DM'],[('POiG',1),('POW9',3),('Popa',80)],['POtr','POL9','POhr'],'Own provisional'),
 ('DM CM Deep Playmaker',['DM','MC'],[('PGR9',4),('Popa',80),('POpc',30)],['Pop9','POL9','POiG'],'Own provisional'),
 ('DM CM Ball Winner',['DM','MC'],[('POW9',4),('POiG',1),('Prs9',2)],['POtr','Popa','Pofm'],'Own provisional'),
 ('CM Box to Box',['MC'],[('POSp',8),('POW9',3),('PGR9',2)],['PODr','PxG9','PxA9','Podr'],'Own provisional'),
 ('CAM Attacking',['AMC'],[('PxG9',0.20),('PxA9',0.10),('Pop9',1.50),('Podr',2),('POSp',8)],['Post','Popa','POL9'],'Earlier unlabeled central midfield screenshot; AMC selection is ours'),
 ('CAM Free Role',['AMC'],[('PxG9',0.20),('PxA9',0.10),('Pop9',1.50),('Podr',2),('Post',30),('POSp',8)],['Popa','POL9'],'User CAM FR guide screenshot'),
 ('W Touchline',['ML','MR','AML','AMR'],[('Podr',2),('PxA9',0.10),('POP9',1)],['Pop9','POCr','POSp'],'Own provisional; broader than historical FM26 winger floors'),
 ('W Inside Forward',['AML','AMR'],[('PNx9',0.20),('POsg',2),('Podr',1)],['Post','PxA9','POSp'],'Own provisional'),
 ('ST Goalscorer',['ST'],[('PNx9',0.30),('POsg',2),('POgg',0.30)],['Post','POgS','PxA9'],'Own provisional; xG-focused rather than historical conversion screen'),
 ('ST Target',['ST'],[('POHg',3),('POhr',50),('PNx9',0.20)],['POgg','Pop9','Popa'],'Own provisional'),
 ('ST Linking',['ST'],[('PxA9',0.10),('Pop9',0.75),('PNx9',0.20)],['POgg','Popa','POL9'],'Own provisional'),
 ('ST Pressing',['ST'],[('Prs9',2),('POW9',1.5),('PNx9',0.20)],['PRS9','POSp','POgg'],'Own provisional'),
]

def columns_from_game():
    factory = json.loads((WORK/'player-table-factory.json').read_text(encoding='utf-8'))
    rows = {row['m_id']:row for row in factory['m_rowData']}
    # Matching uses the game's own binding paths, not guessed displayed headings.
    bindings = {
      'Pxg9':'expectedgoalspreventedper90','POs%':'totalsavepercentage','POx%':'totalexpectedsavepercentage',
      'Popa':'passcompletionpercentage','POhr':'headercompletionpercentage','POHg':'headerscompletedper90',
      'POtr':'tacklecompletionpercentage','POiG':'interceptionsper90','POsb':'shotsblockeddefendingper90',
      'POc9':'clearancesper90','PGR9':'progressivepassesper90','POL9':'possessionlostper90',
      'POW9':'possessionwonper90','Podr':'dribblesmadeper90','POSp':'sprintsper90',
      'POP9':'openplaycrossesattemptedper90','Pop9':'openplaykeypassesper90','PxA9':'expectedassistsper90',
      'POpc':'passcompletedper90','Prs9':'pressurescompletedper90','Pofm':'foulsmade',
      'PODr':'distanceranper90','PxG9':'expectedgoalsper90','Post':'shotsontargetpercentage',
      'POCr':'openplaycrosscompletionpercentage','PNx9':'nonpenaltyexpectedgoalsper90',
      'POsg':'shotsper90','POgg':'goalsper90','POgS':'goalspershotpercentage','PRS9':'pressuresattemptedper90'}
    found = {}
    for field,path in bindings.items():
        candidates = [r['m_id'] for r in rows.values()
            if r.get('m_sortBinding',{}).get('m_path','').lower() == 'binding.'+path+'.propertyvalue']
        if not candidates and field=='POgS':
            candidates=[r['m_id'] for r in rows.values() if 'conversion' in r.get('m_sortBinding',{}).get('m_path','').lower()]
        assert candidates,(field,path)
        found[field]=candidates[0]
    return rows,found

def view(name, fields, collection, rows, field_columns):
    ids=['portrait-name','age','club','club-division','position','stats-minutes','apps']
    ids += list(dict.fromkeys(field_columns[f] for f in fields))
    ids += ['average-rating','wage','transfer-value','contract-expiry-date','recommendation-grade-only']
    configs=[]
    for cid in ids:
        assert cid in rows,cid
        width=200 if cid=='portrait-name' else 130 if cid in ('club','club-division') else 130 if cid=='position' else 110 if cid in ('wage','transfer-value','contract-expiry-date') else 65
        configs.append({'m_columnID':cid,'m_columnMetadata':{'m_required':False,'m_sortingDisabled':False,
            'm_widthOverride':float(width),'m_minWidthOverride':float(min(width,44)),
            'm_titleTranslationIdOverride':{'GameID':0},'m_applicableBreakpoints':2147483647,
            'm_optionalConfigConditions':[],'m_optionalConditions':[],'m_priority':0}})
    config={'m_viewName':{'GameID':0},'m_requirements':[],'m_optionalConditions':[],
        'm_optionalConfigConditions':[],'m_bindingExpect':[],'m_expectRemaps':[],
        'm_tableConfig':configs,'m_overwriteFooterSettings':False,'m_footerParameters':[],'m_footerColumns':[]}
    obj={'ViewSettingsCollectionName':collection,'SerialisedName':name,'Version':1,
         'ViewData':json.dumps(config,separators=(',',':'))}
    raw=json.dumps(obj,separators=(',',':')).encode()
    data=b'\x03\x01eiv.\0\0'+struct.pack('<I',len(raw))+raw
    return data,ids

def build():
    for folder in ['player search filters','views','guide']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    rows,field_columns=columns_from_game()
    manifest=[];guide=[]
    for title,positions,criteria,review,source in PROFILES:
        for field,_ in criteria:assert field in metadata
        mask=sum(POS[p] for p in positions)
        for season,minutes in [('Early',0),('Midseason',1000),('Full Season',2000)]:
            name=title+' - '+season
            filters=([('POmi',minutes)] if minutes else [])+criteria
            prefix=PREFIX.replace(string(OLD_NAME),string(name))
            prefix=prefix.replace(b'\x01\x00\x01\x15\0\0\0',b'\x01\x00\x01'+struct.pack('<I',20+len(filters)))
            prefix=prefix.replace(POSITION_TOKEN,b'lvlf\x01\x02'+struct.pack('<I',mask))
            raw=prefix+b''.join(condition(f,v) for f,v in filters)
            # Hard gate: no division condition is allowed in any master profile.
            assert b'Pbsd'[::-1] not in raw and b'Pdiv'[::-1] not in raw
            filename=name+'.fmf';files=[('image.img',IMAGE),(name+'.pft',raw),('_data/details.aom',details(name))]
            packed=archive(name,files);(OUT/'player search filters'/filename).write_bytes(packed)
            manifest.append({'file':'player search filters/'+filename,'sha256':hashlib.sha256(packed).hexdigest(),
                'positions':positions,'position_mask':mask,'minutes':minutes,'source':source,
                'criteria':[{'field':f,'stat':metadata[f]['name'],'minimum':v} for f,v in filters],
                'league_conditions':[],'native_import_status':'Pending; only original WB(R) v0.1 was user-verified'})
        fields=list(dict.fromkeys([f for f,_ in criteria]+review))
        for label,collection in [('Search','PlayerSearchResultsViewCollection'),('Shortlist','PlayerSearchShortlistViewCollection')]:
            name=title+' - '+label
            raw,ids=view(name,fields,collection,rows,field_columns)
            packed=archive(name,[('image.img',IMAGE),(name+'.view',raw),('_data/details.aom',details(name,'VIEW_TYPE_HANDLER'))])
            (OUT/'views'/(name+'.fmf')).write_bytes(packed)
            manifest.append({'file':'views/'+name+'.fmf','sha256':hashlib.sha256(packed).hexdigest(),
                'collection':collection,'columns':ids,'native_import_status':'Pending'})
        guide.append({'profile':title,'positions':positions,'source':source,
            'minimums':{metadata[f]['name']:v for f,v in criteria},
            'review_columns':[metadata[f]['name'] for f in review],
            'first_comparison_stat':metadata[criteria[0][0]]['name']})
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (OUT/'guide/profiles.json').write_text(json.dumps(guide,indent=2)+'\n',encoding='utf-8')
    lines=['# Profile criteria','','All thresholds are minimums joined by AND. Per-90 values are rates, percentages use percent units. Early omits minutes; Midseason requires 1000; Full Season requires 2000.','','The first comparison stat is a suggested sort column; views do not enforce a sort order. Other metrics provide context rather than extra hard requirements.','']
    for p in guide:
        lines += ['## '+p['profile'],'','Positions: '+', '.join(p['positions'])+'. Source: '+p['source']+'.','']
        lines += [f'- {k}: at least {v}' for k,v in p['minimums'].items()]
        lines += ['','Review columns: '+', '.join(p['review_columns'])+'.','','Start comparison with: '+p['first_comparison_stat']+'.','']
    (OUT/'guide/profiles.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'filters':sum('criteria' in x for x in manifest),'views':sum('columns' in x for x in manifest),'profiles':len(PROFILES),'round_trip_checks':len(manifest)}))
    return manifest

if __name__=='__main__':
    build()
