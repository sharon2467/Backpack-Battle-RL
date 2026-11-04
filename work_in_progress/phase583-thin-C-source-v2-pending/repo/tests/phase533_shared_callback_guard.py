"""Pure fixed029 shared-callback window extraction. No I/O/model/schema imports."""
from collections import Counter
import hashlib
import json

UI_SITES = ['Items/Item.gd::respondToHover', 'Items/Item.gd::respondToHoverEnd', 'Items/Item.gd::_process:dragged', 'Items/Item.gd::_process:rigid', 'Items/Item.gd::activateDragParticles', 'Items/Item.gd::deactivateDragParticles', 'Items/Item.gd::onAddedToGridStorage', 'Items/Item.gd::deactivateParticles', 'Utility/AutoHideParticles.gd::activate', 'Utility/AutoHideParticles.gd::deactivate', 'Utility/AutoHideParticles.gd::startTimer', 'Utility/AutoHideParticles.gd::instantClear']
SOURCE_BASIS = {'candidate_freeze': {'path': 'data/phase505-captured-nonking-source-v3/candidate-source-freeze.json', 'sha256': 'e3f2a86713ef097cae77858f0868fdd70b7487cdeadeaa7fcf11ebb184d550ad', 'size': 4729}, 'observer_tuple': {'path': 'data/phase502-whelp-observer-source-v4/source-tuple.json', 'sha256': '026877626166fe632c08bd3cba28aec191561373b2167f3c6d15d1f1fac86658', 'size': 2001}, 'callback_slices': [{'function': '_physics_process', 'line_end': 4798, 'line_start': 4750, 'sha256': 'a53059d3b89b6d27cdef64858fe28775b2241c017799427878b78eb81bd5770c', 'size': 1079, 'wholefile': {'path': 'data/phase359-king-producer-source/after-source/Core/Game.gd', 'sha256': 'fafe9612858a25b95d8d6149531b50869dbd9709719bd5d2ab6b070b6b8283b1', 'size': 145943}}, {'function': '_process', 'line_end': 4737, 'line_start': 4736, 'sha256': 'e7200388f52f522c3de78cd1b934e14efcd0f7c427f527dc8cf6f9889ee04728', 'size': 59, 'wholefile': {'path': 'data/phase359-king-producer-source/after-source/Core/Game.gd', 'sha256': 'fafe9612858a25b95d8d6149531b50869dbd9709719bd5d2ab6b070b6b8283b1', 'size': 145943}}, {'function': '_process', 'line_end': 1937, 'line_start': 1791, 'sha256': '66e051694306fae459d6b58850797fa1e5772d10f49af5247165bc3a4c7caa0a', 'size': 5012, 'wholefile': {'path': 'data/phase359-king-producer-source/after-source/Items/Item.gd', 'sha256': '2fc1d658db352a7ecae8c2bfb60640a019284992a9c5f9a14c87baea50721631', 'size': 178363}}], 'rule_receipts': [{'path': 'data/phase444-independent-b2-review/review.json', 'sha256': '6fd0cee7140edd8771257d071a3cb92f24bf319ebd2abcc3175e758ebab73945', 'size': 5883}, {'path': 'data/phase444-root-b2-callee-supplement/source-argument.json', 'sha256': 'ad90cd5fd7e484947be5fb0ecdf5bde98d5634f5e8e85c504098da5d1a8fe2ec', 'size': 22238}], 'domain': 'Fixed9IDs ordinary Item/Bag/Food/Goobert/Weapon/ForestFriend Source dispatch; independent Source review required, not arbitrary scripts'}
INPUT_UI_PIN = {'path': '/workspace/native-combat-20261013/runs/original029-whelp-family-A-single-001/output/capture/king-ui-authority.jsonl', 'sha256': '466317b74494e8055f827ce3fca0efccf6ec3e1c69b7d3df8c7cf374a906ddce', 'size': 595770}
INPUT_BUNDLE = {'path': 'data/phase511-case029-actual-input-repaired-001/input-bundle.json', 'sha256': 'a065e481a8ea3d0d145a68ab4fcc945a923a51c75159f289af74083c15dfe5ab', 'size': 287000}
INPUT_PROOF = {'path': 'data/phase511-case029-actual-input-repaired-001/input-proof.json', 'sha256': '2a08a12c8573a1b596cc39293000b11140bc7a3fe4e783dc0dca5c1e8e65b7ea', 'size': 205581}
INPUT_CANONICAL_SHA256 = 'f975cd71337e3c06b76a3d6d1e2652318184f96d41f74e2acf59e4cf02e66eb7'

def strict(raw):
    def pairs(rows):
        result = {}
        for k,v in rows:
            if k in result: raise ValueError('duplicate JSON key '+k)
            result[k] = v
        return result
    def invalid(x): raise ValueError('nonfinite JSON '+x)
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)

def equal(a,b):
    assert json.dumps(a,sort_keys=True,separators=(',',':'),allow_nan=False) == json.dumps(b,sort_keys=True,separators=(',',':'),allow_nan=False)

def extract_shared_callback_guard(raw,bundle,pin_value):
    assert type(raw) is bytes and pin_value==INPUT_UI_PIN and len(raw)==pin_value['size'] and hashlib.sha256(raw).hexdigest()==pin_value['sha256']
    assert hashlib.sha256(json.dumps(bundle,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()==INPUT_CANONICAL_SHA256
    assert raw.endswith(b'\n') and len(raw)<=8388608
    lines=raw.splitlines();assert 1<=len(lines)<=65536
    rows=[]
    for index,line in enumerate(lines):
        assert line and len(line)<=16384
        row=strict(line)
        assert set(row)=={'schema','sequence','kind','site','physics_frame','idle_frame','in_physics','payload'}
        assert row['schema']=='phase355-king-ui-authority/1' and type(row['sequence']) is int and row['sequence']==index
        assert type(row['physics_frame']) is int and type(row['idle_frame']) is int and type(row['in_physics']) is bool
        assert row['physics_frame']>=0 and row['idle_frame']>=0 and type(row['payload']) is dict
        if rows:assert row['physics_frame']>=rows[-1]['physics_frame'] and row['idle_frame']>=rows[-1]['idle_frame']
        rows.append(row)
    def one(kind):
        found=[r for r in rows if r['kind']==kind];assert len(found)==1;return found[0]
    opened,roles,closed=one('open'),one('roles'),one('close')
    assert opened is rows[0] and closed is rows[-1] and opened['sequence']<roles['sequence']<closed['sequence']
    o,c,r=opened['payload'],closed['payload'],roles['payload']
    assert o['case']=='WHELP-FAMILY-A-502' and o['window']=='before_selected_birth_to_final_preinternal'
    equal(o['sites'],UI_SITES);equal(c['sites'],UI_SITES)
    assert o['drop_mouse_setting'] is True and c['completed'] is True and c['failed'] is False and c['overflow'] is False
    assert type(c['dropped']) is int and c['dropped']==0 and c['phase']=='idle_pre_internal_flush'
    assert c['king_clock_closed'] is True and type(c['active_buff_calls']) is int and c['active_buff_calls']==0
    assert type(c['rows_before_close']) is int and c['rows_before_close']==len(rows)-1
    nodes={n['role']:n for n in bundle['runtime']['processing_nodes']}
    root_id=nodes['root_viewport']['native_id']
    for controls in (o['after'],c['controls']):
        assert controls['root_id']==root_id and controls['disable_input'] is True and controls['physics_object_picking'] is False
    assert o['before']['root_id']==root_id and r['using_controller'] is False
    expected={i['instance_id']:nodes['item:'+i['instance_id']]['native_id'] for side in bundle['fixture']['sides'] for i in side['items']}
    guards=r['selected_guards'];assert type(guards) is list and len(guards)==29 and len({g['role'] for g in guards})==29
    assert {g['role']:g['item_id'] for g in guards}==expected
    for g in guards:
        assert all(g[k] is False for k in ('focus','hovered','dragged'))
        assert type(g['mode']) is int and g['mode']==1 and g['viewport_id']==root_id
    equal(r['kings'],[])
    stack=[];entries=[];by_site=Counter();critical=[];selected_item=[]
    for row in rows:
        if row['kind']=='entry':
            p=row['payload'];assert row['site'] in UI_SITES and type(p['token']) is int and p['token']==row['sequence']
            assert type(p['receiver_id']) is str
            stack.append((p['token'],row['site'],p['receiver_id']));entries.append(row);by_site[row['site']]+=1
            if row['site'] in UI_SITES[:4]:critical.append({'sequence':row['sequence'],'site':row['site'],'receiver_id':p['receiver_id']})
            if row['site'].startswith('Items/Item.gd::') and p['receiver_id'] in expected.values():selected_item.append({'sequence':row['sequence'],'site':row['site'],'receiver_id':p['receiver_id']})
        elif row['kind']=='exit':
            p=row['payload'];assert stack and stack.pop()==(p['token'],row['site'],p['receiver_id'])
    assert not stack and type(c['entries']) is int and c['entries']==len(entries)
    assert not critical,('RELEVANT_HOVER_DRAG_RIGID_ENTRY',critical)
    assert not selected_item,('SELECTED_ITEM_UI_ENTRY_REQUIRES_SOURCE_CLASSIFICATION',selected_item)
    last=bundle['runtime']['frame_clock']['passes'][-1]
    assert (closed['physics_frame']>=last['physics_frame'] and closed['idle_frame']>=last['idle_frame'])
    assert (opened['physics_frame']<=bundle['runtime']['frame_clock']['checkpoint']['physics_frame'] and opened['idle_frame']<=bundle['runtime']['frame_clock']['checkpoint']['idle_frame'])
    return {'input_bundle':INPUT_BUNDLE,'input_proof':INPUT_PROOF,'source_basis':SOURCE_BASIS,'covered_last_clock_pair':[last['physics_frame'],last['idle_frame']],'close_clock_pair':[closed['physics_frame'],closed['idle_frame']],'full_FX_UI_gate_called':False,'schema':'phase533-actual029-B2-guard/1','status':'ACTUAL_FIXED29_WINDOW_MATCHES_SOURCE_GUARD',
            'raw_descriptor':pin_value,'raw_UI_reads':1,'other_original_INPUT_reads':0,'rows':len(rows),'role_bind_sequence':roles['sequence'],
            'selected_guards':guards,'open':o,'close':c,'entries_by_site':dict(by_site),'relevant_critical_entries':critical,
            'selected_item_entries':selected_item,'native_roles_verified':29,'model_noop_slots':31,
            'argument':'Accepted444 shared3callback/readonly-callee rule plus independently reviewed fixed502 nineID dispatch and this actual complete window. Per-clock/write controls and positive-writer branch guards; initialfalse or unchanged code alone is not proof. Squirrel PetORFood and Whelp/Basic queries stay in the admitted read-only domain.',
            'limits':['Conditional selected primitive Tape/business semantics only; no global/same-seed RNG or GUI equivalence.','No full-FX admission helper or107methods equality claim. Footer is coverage evidence only.','Ordinary G02 writer/dispatch, historical Source redaction and reconstructed-analysis limitations retained.']}
