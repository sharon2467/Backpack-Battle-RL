"""Pure fixed029 shared-callback window extraction. No I/O/model/schema imports."""
from collections import Counter
import hashlib
import json

UI_SITES = ['Items/Item.gd::respondToHover', 'Items/Item.gd::respondToHoverEnd', 'Items/Item.gd::_process:dragged', 'Items/Item.gd::_process:rigid', 'Items/Item.gd::activateDragParticles', 'Items/Item.gd::deactivateDragParticles', 'Items/Item.gd::onAddedToGridStorage', 'Items/Item.gd::deactivateParticles', 'Utility/AutoHideParticles.gd::activate', 'Utility/AutoHideParticles.gd::deactivate', 'Utility/AutoHideParticles.gd::startTimer', 'Utility/AutoHideParticles.gd::instantClear']
SOURCE_BASIS = {'candidate_freeze': {'path': '/workspace/python-original-engine/repo/data/phase580-captured-mixed-source/candidate-source-freeze.json', 'size': 4809, 'sha256': 'e332b765f3bd48c6df63c1ffd047f82654fe0c0465e9886275d287b42160a51b'}, 'observer_tuple': {'path': 'data/phase572-mixed-observer-source-v2/source-tuple.json', 'size': 2870, 'sha256': '7134099050c0847030bdf824f986cf95ab9258f222a866a898f57099610cf086'}, 'callback_slices': [{'function': '_physics_process', 'line_end': 4798, 'line_start': 4750, 'sha256': 'a53059d3b89b6d27cdef64858fe28775b2241c017799427878b78eb81bd5770c', 'size': 1079, 'wholefile': {'path': 'data/phase359-king-producer-source/after-source/Core/Game.gd', 'sha256': 'fafe9612858a25b95d8d6149531b50869dbd9709719bd5d2ab6b070b6b8283b1', 'size': 145943}}, {'function': '_process', 'line_end': 4737, 'line_start': 4736, 'sha256': 'e7200388f52f522c3de78cd1b934e14efcd0f7c427f527dc8cf6f9889ee04728', 'size': 59, 'wholefile': {'path': 'data/phase359-king-producer-source/after-source/Core/Game.gd', 'sha256': 'fafe9612858a25b95d8d6149531b50869dbd9709719bd5d2ab6b070b6b8283b1', 'size': 145943}}, {'function': '_process', 'line_end': 1937, 'line_start': 1791, 'sha256': '66e051694306fae459d6b58850797fa1e5772d10f49af5247165bc3a4c7caa0a', 'size': 5012, 'wholefile': {'path': 'data/phase572-mixed-observer-source-v2/after-source/Items/Item.gd', 'size': 178614, 'sha256': '11fb434eaa028eb965e10883d84ef7028ee96bdfbf2f53bdc71af64332ae0429'}}], 'rule_receipts': [{'path': 'data/phase444-independent-b2-review/review.json', 'sha256': '6fd0cee7140edd8771257d071a3cb92f24bf319ebd2abcc3175e758ebab73945', 'size': 5883}, {'path': 'data/phase444-root-b2-callee-supplement/source-argument.json', 'sha256': 'ad90cd5fd7e484947be5fb0ecdf5bde98d5634f5e8e85c504098da5d1a8fe2ec', 'size': 22238}], 'domain': 'Closed12 IDs1/5/11/14/22/32/162/164/231/233/234/385; ordinary Item/Bag/Food/ForestFriend/Wolper/Enchanted/fourWeapon. Independent finite Source applicability review and actual window mandatory; not all84.', 'finite_source_domain_argument': {'path': 'data/phase562-finite-mixed-source-design/source-pins.json', 'size': 8058, 'sha256': '36844a6cf790c3e6d1e37d3aefa9f8bc3ae85ed782a2d0266800829951e3770b'}}
INPUT_UI_PIN = None
INPUT_BUNDLE = None
INPUT_PROOF = None
INPUT_CANONICAL_SHA256 = None

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

def extract_shared_callback_guard(raw,bundle,pin_value,root_binding):
    assert type(root_binding) is dict and set(root_binding)=={'schema','input_bundle','input_proof','source_basis','input_bundle_canonical_sha256'} and root_binding['schema']=='phase582-B2-input-binding/1'
    equal(root_binding['source_basis'],SOURCE_BASIS)
    for name in ('input_bundle','input_proof'):
        p=root_binding[name];assert type(p) is dict and set(p)=={'path','size','sha256'} and type(p['path']) is str and type(p['size']) is int and p['size']>0 and type(p['sha256']) is str and len(p['sha256'])==64 and all(ch in '0123456789abcdef' for ch in p['sha256'])
    assert type(pin_value) is dict and set(pin_value)=={'path','size','sha256'} and type(pin_value['size']) is int and pin_value['size']>0 and type(pin_value['sha256']) is str and len(pin_value['sha256'])==64 and all(ch in '0123456789abcdef' for ch in pin_value['sha256']) and type(pin_value['path']) is str
    assert pin_value['path'].replace('\\','/').split('/')[-1]=='king-ui-authority.jsonl'
    assert type(raw) is bytes and len(raw)==pin_value['size'] and hashlib.sha256(raw).hexdigest()==pin_value['sha256']
    assert hashlib.sha256(json.dumps(bundle,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()==root_binding['input_bundle_canonical_sha256']
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
    assert o['case']=='MIXED-MODIFIERS-A-572' and o['window']=='before_selected_birth_to_final_preinternal'
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
    return {'input_bundle':root_binding['input_bundle'],'input_proof':root_binding['input_proof'],'source_basis':SOURCE_BASIS,'covered_last_clock_pair':[last['physics_frame'],last['idle_frame']],'close_clock_pair':[closed['physics_frame'],closed['idle_frame']],'full_FX_UI_gate_called':False,'schema':'phase582-actual030-B2-guard/1','status':'ACTUAL_FIXED29_WINDOW_MATCHES_SOURCE_GUARD',
            'raw_descriptor':pin_value,'raw_UI_reads':1,'other_original_INPUT_reads':0,'rows':len(rows),'role_bind_sequence':roles['sequence'],
            'selected_guards':guards,'open':o,'close':c,'entries_by_site':dict(by_site),'relevant_critical_entries':critical,
            'selected_item_entries':selected_item,'native_roles_verified':29,'model_noop_slots':31,
            'argument':'Accepted444 shared3callback/readonly-callee rule plus independently reviewed finite12 Source applicability and this actual complete window. Initialfalse or unchanged code alone is not proof. Squirrel tail RNG remains business; no GUI/global-generator equivalence.',
            'limits':['Conditional selected primitive Tape/business semantics only; no global/same-seed RNG or GUI equivalence.','No full-FX admission helper or107methods equality claim. Footer is coverage evidence only.','Ordinary G02 writer/dispatch, historical Source redaction and reconstructed-analysis limitations retained.']}
