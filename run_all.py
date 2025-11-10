import json
import random
from pathlib import Path

ROOT = Path(__file__).parent
DATA_FILE = ROOT / 'data.json'
OUT_FILE = ROOT / 'outputs_full.txt'

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)


def weighted_pick(mapping):
    items = [(k, v) for k, v in mapping.items() if v and v > 0]
    if not items:
        return None
    total = sum(v for _, v in items)
    r = random.random() * total
    acc = 0
    for k, v in items:
        acc += v
        if r <= acc:
            return k
    return items[-1][0]


def rand_int(a,b):
    return random.randint(a,b)


def open_box(box_name):
    if box_name == data['boxes']['mysteryBox']['name'] or box_name == '???상자':
        picked = weighted_pick(data['boxes']['mysteryBox']['contains'])
        return {'opened': box_name, 'yieldedBox': picked, 'result': open_box(picked)}
    all_boxes = data['boxes']['randomBoxes'] + data['boxes']['craftBoxes'] + data['boxes']['shopBoxes']
    box = next((x for x in all_boxes if x['name']==box_name), None)
    if not box:
        return {'error':'Box not found','boxName':box_name}
    grade = weighted_pick(box.get('pickaxeGradeProbabilities',{}))
    if not grade:
        return {'opened':box_name,'result':'No pickaxe awarded'}
    picks = data['pickaxes'].get(grade,[])
    if not picks:
        return {'opened':box_name,'grade':grade,'result':'No pickaxe entries for grade'}
    pick = random.choice(picks)
    drops = rand_int(pick['dropRange'][0], pick['dropRange'][1])
    return {'opened':box_name,'grade':grade,'pickaxe':pick['name'],'speedReductionPercent':pick.get('speedReductionPercent'),'drops':drops}


def format_open(res):
    # Include probability information when available
    if 'error' in res:
        return f"오류: {res['error']} (상자: {res.get('boxName','-')})"

    # If this was a mystery box yielding another box, show the spawn probability
    if 'yieldedBox' in res:
        yielded = res['yieldedBox']
        spawn_prob = data['boxes']['mysteryBox']['contains'].get(yielded, None)
        spawn_info = f"등장 확률: {spawn_prob}%" if spawn_prob is not None else ''
        inner = format_open(res['result'])
        return f"개봉한 상자: {res['opened']}\n→ 등장한 상자: {yielded} {spawn_info}\n{inner}"

    # Normal box open with a pickaxe
    box_entry = None
    for b in data['boxes']['randomBoxes'] + data['boxes']['craftBoxes'] + data['boxes']['shopBoxes']:
        if b['name'] == res.get('opened'):
            box_entry = b
            break

    grade = res.get('grade')
    pick = res.get('pickaxe')
    pick_info_lines = []
    if box_entry and grade:
        grade_probs = box_entry.get('pickaxeGradeProbabilities', {})
        grade_prob = grade_probs.get(grade, 0)
        pickaxes_in_grade = data['pickaxes'].get(grade, [])
        count_in_grade = len(pickaxes_in_grade)
        per_pick_prob = 0
        if count_in_grade > 0:
            per_pick_prob = grade_prob / count_in_grade
        pick_info_lines.append(f"획득 등급: {grade} (등급 확률: {grade_prob}%)")
        pick_info_lines.append(f"획득 곡괭이: {pick} (해당 등급 내 개별 확률: {per_pick_prob:.2f}%)")
    else:
        if grade:
            pick_info_lines.append(f"획득 등급: {grade}")
        pick_info_lines.append(f"획득 곡괭이: {pick}")

    pick_info_lines.append(f"채굴 속도 감소: {res.get('speedReductionPercent')}%")
    pick_info_lines.append(f"드롭 개수: {res.get('drops')}")
    return '\n'.join(pick_info_lines)


def wrap(cmd,out):
    return f"명령어입력: {cmd}\n출력:\n{out}"

outs = []
# ㅇ상자목록
lines = []
lines.append('=== 상자 목록 ===')
lines.append('\n[미스터리 상자]')
lines.append(f"이름: {data['boxes']['mysteryBox']['name']}")
lines.append(f"설명: {data['boxes']['mysteryBox'].get('note','')}")
lines.append('\n[랜덤 상자]')
for b in data['boxes']['randomBoxes']:
    lines.append(f"- {b['name']}")
lines.append('\n[조합 상자]')
for b in data['boxes']['craftBoxes']:
    lines.append(f"- {b['name']}")
lines.append('\n[상점 상자]')
for b in data['boxes']['shopBoxes']:
    lines.append(f"- {b['name']}")
outs.append(wrap('ㅇ상자목록','\n'.join(lines)))

# ㅇ채굴
if random.random() < 0.10:
    outs.append(wrap('ㅇ채굴','???상자 1개를 획득했습니다!'))
else:
    gold = random.randint(50,500)
    minerals = random.randint(1,4)
    outs.append(wrap('ㅇ채굴',f'채굴 성공: 골드 {gold} 획득, 광물 {minerals}개 획득'))

# ㅇ열기 ???상자
r = open_box('???상자')
outs.append(wrap('ㅇ열기 "???상자"',format_open(r)))

# collect picked pickaxes for ㅇ장착
picked = []
def extract_pickinfo(res, origin_spawn_prob=None):
    # traverse nested result to find pickaxe
    cur = res
    spawned_prob = origin_spawn_prob
    if 'yieldedBox' in cur:
        # if mystery yielded a box, get its spawn prob
        y = cur['yieldedBox']
        spawned_prob = data['boxes']['mysteryBox']['contains'].get(y, None)
        cur = cur['result']
    # now cur should be a normal box result or error
    if 'pickaxe' in cur:
        return (cur.get('opened'), cur.get('grade'), cur.get('pickaxe'), spawned_prob)
    return (None, None, None, spawned_prob)

# ㅇ열기 random
for b in data['boxes']['randomBoxes']:
    r = open_box(b['name'])
    outs.append(wrap(f'ㅇ열기 "{b["name"]}"',format_open(r)))
    ob, gr, pk, sp = extract_pickinfo(r)
    if pk:
        picked.append((ob, gr, pk, sp))

# ㅇ열기 craft + recipe
for b in data['boxes']['craftBoxes']:
    r = open_box(b['name'])
    outs.append(wrap(f'ㅇ열기 "{b["name"]}"',format_open(r)))
    ob, gr, pk, sp = extract_pickinfo(r)
    if pk:
        picked.append((ob, gr, pk, sp))
    outs.append(wrap(f'ㅇ레시피 "{b["name"]}"',json.dumps(b.get('recipe',{}),ensure_ascii=False)))

# ㅇ열기 shop
for b in data['boxes']['shopBoxes']:
    r = open_box(b['name'])
    outs.append(wrap(f'ㅇ열기 "{b["name"]}"',format_open(r)))
    ob, gr, pk, sp = extract_pickinfo(r)
    if pk:
        picked.append((ob, gr, pk, sp))

# ㅇ곡괭이목록
pk_lines=[]
for grade,picks in data['pickaxes'].items():
    pk_lines.append(f'== 등급: {grade} ==')
    for p in picks:
        pk_lines.append(f"- {p['name']} : 채굴 속도 -{p.get('speedReductionPercent','?')}%, 드롭 {p.get('dropRange')}개")
    pk_lines.append('')
outs.append(wrap('ㅇ곡괭이목록','\n'.join(pk_lines)))

# ㅇ상점
shop_lines=[]
for b in data['boxes']['shopBoxes']:
    shop_lines.append(f"- {b['name']} : 가격 {b.get('price','N/A')}골드, 설명: {b.get('features','')}")
outs.append(wrap('ㅇ상점','\n'.join(shop_lines)))

# ㅇ인벤토리
inv_lines=['=== 인벤토리 ===','상자:','- ???상자: 2개','- 초심자의상자: 1개','아이템:','- 루비: 1개']
outs.append(wrap('ㅇ인벤토리','\n'.join(inv_lines)))

# ㅇ내정보
outs.append(wrap('ㅇ내정보','이름: 테스트유저\n골드: 100000\n장착 곡괭이: 초보곡괭이'))

# ㅇ명령어
cmds=[
    ('ㅇ채굴','채굴을 시도합니다. 10%로 ???상자 획득 가능'),
    ('ㅇ열기 [상자이름]','상자를 엽니다.'),
    ('ㅇ상자목록','상자 목록을 표시합니다.'),
    ('ㅇ곡괭이목록','곡괭이 전체 리스트를 봅니다.'),
    ('ㅇ레시피 [상자이름]','조합 레시피 확인'),
    ('ㅇ상점','상점에서 판매하는 상자 목록'),
    ('ㅇ인벤토리','플레이어 인벤토리 보기'),
    ('ㅇ내정보','플레이어 정보 보기'),
    ('ㅇ명령어','사용 가능한 명령어 목록'),
]
outs.append(wrap('ㅇ명령어','\n'.join([f"{c} - {d}" for c,d in cmds])))

# ㅇ레시피 (전체)
rec=[]
for b in data['boxes']['craftBoxes']:
    rec.append(f"{b['name']}: {json.dumps(b.get('recipe',{}),ensure_ascii=False)}")
outs.append(wrap('ㅇ레시피','\n'.join(rec)))

# ㅇ장착 (equip) - equip first picked pickaxe if any
if picked:
    ob, gr, pk, sp = picked[0]
    # compute approximate overall probability if possible
    overall = None
    per_pick = None
    if ob:
        # find box entry
        be = next((x for x in data['boxes']['randomBoxes'] + data['boxes']['craftBoxes'] + data['boxes']['shopBoxes'] if x['name']==ob), None)
        if be and gr:
            grade_prob = be.get('pickaxeGradeProbabilities', {}).get(gr, 0)
            picks_in_grade = data['pickaxes'].get(gr, [])
            if picks_in_grade:
                per_pick = grade_prob / len(picks_in_grade)
                if sp is not None:
                    overall = (sp * per_pick) / 100.0
                else:
                    overall = per_pick
    prob_str = ''
    if per_pick is not None:
        prob_str = f"등급내 개별확률: {per_pick:.2f}%"
    if overall is not None:
        prob_str += (" | " if prob_str else "") + f"전체획득추정확률: {overall:.4f}%"
    outs.append(wrap(f'ㅇ장착 "{pk}"', f'장착 완료: {pk} (등급: {gr})\n{prob_str}'))

OUT_FILE.write_text('\n\n'.join(outs),encoding='utf-8')
print(f"출력이 '{OUT_FILE}'에 저장되었습니다.")
