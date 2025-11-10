import json
import random
from pathlib import Path

ROOT = Path(__file__).parent
DATA_FILE = ROOT / 'data.json'
OUT_FILE = ROOT / 'outputs.txt'

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
            import json
            import random
            from pathlib import Path

            ROOT = Path(__file__).parent
            DATA_FILE = ROOT / 'data.json'
            OUT_FILE = ROOT / 'outputs.txt'

            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)


            # --- Helpers ---

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


            def rand_int(minv, maxv):
                return random.randint(minv, maxv)


            def list_boxes_all():
                return {
                    'mystery': data['boxes']['mysteryBox'],
                    'random': [b['name'] for b in data['boxes']['randomBoxes']],
                    'craft': [b['name'] for b in data['boxes']['craftBoxes']],
                    'shop': [b['name'] for b in data['boxes']['shopBoxes']],
                }


            def find_box_by_name(name):
                all_list = data['boxes']['randomBoxes'] + data['boxes']['craftBoxes'] + data['boxes']['shopBoxes']
                for b in all_list:
                    if b.get('name') == name:
                        return b
                return None


            def get_pickaxe_list(grade):
                return data['pickaxes'].get(grade, [])


            def open_box(box_name):
                # mystery box handling
                if box_name == data['boxes']['mysteryBox']['name'] or box_name == '???상자':
                    picked = weighted_pick(data['boxes']['mysteryBox']['contains'])
                    return {'opened': box_name, 'yieldedBox': picked, 'result': open_box(picked)}

                box = find_box_by_name(box_name)
                if not box:
                    return {'error': 'Box not found', 'boxName': box_name}

                grade = weighted_pick(box.get('pickaxeGradeProbabilities', {}))
                if not grade:
                    return {'opened': box_name, 'result': 'No pickaxe awarded'}

                pickaxes = get_pickaxe_list(grade)
                if not pickaxes:
                    return {'opened': box_name, 'grade': grade, 'result': 'No pickaxe entries for grade'}

                pick = random.choice(pickaxes)
                drops = rand_int(pick['dropRange'][0], pick['dropRange'][1])
                return {
                    'opened': box_name,
                    'grade': grade,
                    'pickaxe': pick['name'],
                    'speedReductionPercent': pick.get('speedReductionPercent'),
                    'drops': drops,
                }


            def format_open_result(res):
                if not res:
                    return '결과가 없습니다.'
                if 'error' in res:
                    return f"오류: {res['error']} (상자: {res.get('boxName','-')})"

                if 'yieldedBox' in res and 'result' in res:
                    inner = format_open_result(res['result'])
                    return f"개봉한 상자: {res['opened']}\n→ 등장한 상자: {res['yieldedBox']}\n{inner}"

                if 'pickaxe' in res:
                    return (f"개봉한 상자: {res['opened']}\n"
                            f"획득 등급: {res.get('grade')}\n"
                            f"획득 곡괭이: {res.get('pickaxe')}\n"
                            f"채굴 속도 감소: {res.get('speedReductionPercent')}%\n"
                            f"드롭 개수: {res.get('drops')}")

                return f"개봉한 상자: {res.get('opened')}\n결과: {res}"


            def format_list_all(all_boxes):
                lines = []
                lines.append('=== 상자 목록 ===')
                lines.append('\n[미스터리 상자]')
                lines.append(f"이름: {all_boxes['mystery']['name']}")
                lines.append(f"설명: {all_boxes['mystery'].get('note','')}")

                lines.append('\n[랜덤 상자]')
                for n in all_boxes['random']:
                    lines.append(f"- {n}")

                lines.append('\n[조합 상자]')
                for n in all_boxes['craft']:
                    lines.append(f"- {n}")

                lines.append('\n[상점 상자]')
                for n in all_boxes['shop']:
                    lines.append(f"- {n}")

                return '\n'.join(lines)


            def wrap(cmd, out_str):
                return f"명령어입력: {cmd}\n출력:\n{out_str}"


            # --- Additional command simulations ---


            def simulate_mine():
                if random.random() < 0.10:
                    return '???상자 1개를 획득했습니다!'
                gold = random.randint(50, 500)
                minerals = random.randint(1, 4)
                return f'채굴 성공: 골드 {gold} 획득, 광물 {minerals}개 획득'


            def format_pickaxe_list():
                lines = []
                for grade, picks in data['pickaxes'].items():
                    lines.append(f'== 등급: {grade} ==')
                    for p in picks:
                        lines.append(f"- {p['name']} : 채굴 속도 -{p.get('speedReductionPercent','?')}%, 드롭 {p.get('dropRange')}개")
                    lines.append('')
                return '\n'.join(lines)


            def format_shop_list():
                lines = []
                lines.append('=== 상점 상자 목록 ===')
                for b in data['boxes']['shopBoxes']:
                    price = b.get('price', 'N/A')
                    lines.append(f"- {b['name']} : 가격 {price}골드, 설명: {b.get('features','')}")
                return '\n'.join(lines)


            def format_commands_list():
                cmds = [
                    ('ㅇ채굴', '채굴을 시도합니다. 10%로 ???상자 획득 가능'),
                    ('ㅇ열기 [상자이름]', '상자를 엽니다.'),
                    ('ㅇ상자목록', '상자 목록을 표시합니다.'),
                    ('ㅇ곡괭이목록', '곡괭이 전체 리스트를 봅니다.'),
                    ('ㅇ레시피 [상자이름]', '조합 레시피 확인'),
                    ('ㅇ상점', '상점에서 판매하는 상자 목록'),
                    ('ㅇ인벤토리', '플레이어 인벤토리 보기'),
                    ('ㅇ내정보', '플레이어 정보 보기'),
                    ('ㅇ명령어', '사용 가능한 명령어 목록'),
                    ('실행', '플랜을 실행하고 outputs.txt에 저장'),
                ]
                return '\n'.join([f"{c} - {d}" for c, d in cmds])


            def format_inventory_sample():
                inv = {
                    'boxes': {'???상자': 2, '초심자의상자': 1, '용사의상자': 0},
                    'items': {'루비': 1, '미스릴': 0},
                }
                lines = []
                lines.append('=== 인벤토리 ===')
                lines.append('상자:')
                for k, v in inv['boxes'].items():
                    lines.append(f"- {k}: {v}개")
                lines.append('아이템:')
                for k, v in inv['items'].items():
                    lines.append(f"- {k}: {v}개")
                return '\n'.join(lines)


            def format_myinfo_sample():
                info = {'name': '테스트유저', 'gold': 100000, 'pickaxe': '초보곡괭이'}
                return f"이름: {info['name']}\n골드: {info['gold']}\n장착 곡괭이: {info['pickaxe']}"


            # --- Execute plan ---
            outputs = []

            # ㅇ상자목록
            all_boxes = list_boxes_all()
            outputs.append(wrap('ㅇ상자목록', format_list_all(all_boxes)))

            # ㅇ채굴 (한 번)
            outputs.append(wrap('ㅇ채굴', simulate_mine()))

            # ㅇ열기 ???상자
            res_myst = open_box('???상자')
            outputs.append(wrap('ㅇ열기 "???상자"', format_open_result(res_myst)))

            # ㅇ열기 각 랜덤 상자 1회
            for b in data['boxes']['randomBoxes']:
                cmd = f'ㅇ열기 "{b["name"]}"'
                res = open_box(b['name'])
                outputs.append(wrap(cmd, format_open_result(res)))

            # ㅇ열기 각 조합 상자 1회 + ㅇ레시피
            for b in data['boxes']['craftBoxes']:
                cmd = f'ㅇ열기 "{b["name"]}"'
                res = open_box(b['name'])
                outputs.append(wrap(cmd, format_open_result(res)))
                outputs.append(wrap(f'ㅇ레시피 "{b["name"]}"', json.dumps(b.get('recipe', {}), ensure_ascii=False)))

            # ㅇ열기 각 상점 상자 1회
            for b in data['boxes']['shopBoxes']:
                cmd = f'ㅇ열기 "{b["name"]}"'
                res = open_box(b['name'])
                outputs.append(wrap(cmd, format_open_result(res)))

            # 추가 명령어: ㅇ곡괭이목록, ㅇ상점, ㅇ인벤토리, ㅇ내정보, ㅇ명령어, ㅇ레시피(전체)
            outputs.append(wrap('ㅇ곡괭이목록', format_pickaxe_list()))
            outputs.append(wrap('ㅇ상점', format_shop_list()))
            outputs.append(wrap('ㅇ인벤토리', format_inventory_sample()))
            outputs.append(wrap('ㅇ내정보', format_myinfo_sample()))
            outputs.append(wrap('ㅇ명령어', format_commands_list()))

            recipes_lines = []
            for b in data['boxes']['craftBoxes']:
                recipes_lines.append(f"{b['name']}: {json.dumps(b.get('recipe', {}), ensure_ascii=False)}")
            outputs.append(wrap('ㅇ레시피', '\n'.join(recipes_lines)))

            # 저장
            OUT_FILE.write_text('\n\n'.join(outputs), encoding='utf-8')
            print(f"출력이 '{OUT_FILE}'에 저장되었습니다.")
