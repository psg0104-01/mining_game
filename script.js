const fs = require('fs');
const path = require('path');
const data = require('./data.json');

function weightedPick(map) {
  const entries = Object.entries(map).filter(([, v]) => v > 0);
  const total = entries.reduce((s, [, v]) => s + v, 0);
  if (entries.length === 0) return null;
  const r = Math.random() * total;
  let acc = 0;
  for (const [k, v] of entries) {
    acc += v;
    if (r <= acc) return k;
  }
  return entries[entries.length - 1][0];
}

// Returns both selected key and its percentage (based on provided weights)
function weightedPickWithStats(map) {
  const entries = Object.entries(map).filter(([, v]) => v > 0);
  const total = entries.reduce((s, [, v]) => s + v, 0);
  if (entries.length === 0) return null;
  const pickedKey = weightedPick(map);
  const weight = map[pickedKey] || 0;
  const percent = total > 0 ? (weight / total) * 100 : 0;
  return { key: pickedKey, percent };
}

function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function listBoxes(section = 'all') {
  if (section === 'all') {
    return {
      mystery: data.boxes.mysteryBox,
      random: data.boxes.randomBoxes.map(b => b.name),
      craft: data.boxes.craftBoxes.map(b => b.name),
      shop: data.boxes.shopBoxes.map(b => b.name)
    };
  }
  if (section === 'mystery') return data.boxes.mysteryBox;
  if (section === 'random') return data.boxes.randomBoxes;
  if (section === 'craft') return data.boxes.craftBoxes;
  if (section === 'shop') return data.boxes.shopBoxes;
  return null;
}

function findBoxByName(name) {
  const all = [].concat(data.boxes.randomBoxes, data.boxes.craftBoxes, data.boxes.shopBoxes);
  return all.find(b => b.name === name) || null;
}

function getPickaxeList(grade) {
  return data.pickaxes[grade] || [];
}

function openBox(boxName) {
  // special handling for mystery box (???상자)
  if (boxName === data.boxes.mysteryBox.name || boxName === '???상자') {
    const pickedInfo = weightedPickWithStats(data.boxes.mysteryBox.contains);
    const picked = pickedInfo ? pickedInfo.key : null;
    const spawnPercent = pickedInfo ? pickedInfo.percent : 0;
    const inner = picked ? openBox(picked) : null;
    return { opened: boxName, yieldedBox: picked, spawnPercent, result: inner };
  }

  const box = findBoxByName(boxName);
  if (!box) return { error: 'Box not found', boxName };

  const gradeInfo = weightedPickWithStats(box.pickaxeGradeProbabilities || {});
  const grade = gradeInfo ? gradeInfo.key : null;
  const gradePercent = gradeInfo ? gradeInfo.percent : 0;
  if (!grade) return { opened: boxName, result: 'No pickaxe awarded' };

  const pickaxes = getPickaxeList(grade);
  if (!pickaxes || pickaxes.length === 0) return { opened: boxName, grade, result: 'No pickaxe entries for grade' };

  const pick = pickaxes[Math.floor(Math.random() * pickaxes.length)];
  const drops = randInt(pick.dropRange[0], pick.dropRange[1]);

  // estimate per-pickaxe percent within this grade
  const perPickPercent = pickaxes.length > 0 ? gradePercent / pickaxes.length : 0;

  return {
    opened: boxName,
    grade,
    gradePercent,
    pickaxe: pick.name,
    perPickPercent,
    speedReductionPercent: pick.speedReductionPercent,
    drops
  };
}

function getRecipe(boxName) {
  const box = data.boxes.craftBoxes.find(b => b.name === boxName);
  return box ? box.recipe : null;
}

module.exports = {
  listBoxes,
  openBox,
  getPickaxeList,
  getRecipe,
  // helpers for tests or cli
  _weightedPick: weightedPick
};

// 간단한 CLI 예시: node script.js open "???상자"
function _formatOpenResult(res) {
  if (!res) return '결과가 없습니다.';
  if (res.error) return `오류: ${res.error}`;

  // mystery box (???상자) 처리: 내부에서 다른 상자가 나옴
  if (res.yieldedBox && res.result) {
    const inner = _formatOpenResult(res.result);
    const spawnLine = typeof res.spawnPercent === 'number' ? ` → 등장 확률: ${res.spawnPercent.toFixed(2)}%` : '';
    return `개봉한 상자: ${res.opened}\n→ 등장한 상자: ${res.yieldedBox}${spawnLine}\n${inner}`;
  }

  if (res.pickaxe) {
    const gradePct = typeof res.gradePercent === 'number' ? `${res.gradePercent.toFixed(2)}%` : 'N/A';
    const perPick = typeof res.perPickPercent === 'number' ? `${res.perPickPercent.toFixed(2)}%` : 'N/A';
    return `개봉한 상자: ${res.opened}\n획득 등급: ${res.grade} (등급 확률: ${gradePct})\n획득 곡괭이: ${res.pickaxe} (해당 등급 내 개별 확률: ${perPick})\n채굴 속도 감소: ${res.speedReductionPercent}%\n드롭 개수: ${res.drops}`;
  }

  return `개봉한 상자: ${res.opened}\n결과: ${JSON.stringify(res)}`;
}

function _formatListAll(all) {
  const lines = [];
  lines.push('=== 상자 목록 ===');
  lines.push('\n[미스터리 상자]');
  lines.push(`이름: ${all.mystery.name}`);
  lines.push(`설명: ${all.mystery.note || ''}`);

  lines.push('\n[랜덤 상자]');
  all.random.forEach(n => lines.push(`- ${n}`));

  lines.push('\n[조합 상자]');
  all.craft.forEach(n => lines.push(`- ${n}`));

  lines.push('\n[상점 상자]');
  all.shop.forEach(n => lines.push(`- ${n}`));

  return lines.join('\n');
}

// CLI 및 플랜 실행 지원 (한글 명령어 포함)
function wrap(cmd, outStr) {
  return `명령어입력: ${cmd}\n출력:\n${outStr}`;
}

function runPlanAndSave() {
  const outputs = [];

  // list -> ㅇ상자목록
  const all = listBoxes('all');
  outputs.push(wrap('ㅇ상자목록', _formatListAll(all)));

  // mystery
  const myst = openBox('???상자');
  outputs.push(wrap('ㅇ열기 "???상자"', _formatOpenResult(myst)));

  // random boxes
  data.boxes.randomBoxes.forEach(b => {
    const cmd = `ㅇ열기 "${b.name}"`;
    const res = openBox(b.name);
    outputs.push(wrap(cmd, _formatOpenResult(res)));
  });

  // craft boxes + recipe
  data.boxes.craftBoxes.forEach(b => {
    const cmd = `ㅇ열기 "${b.name}"`;
    const res = openBox(b.name);
    outputs.push(wrap(cmd, _formatOpenResult(res)));
    const recipeCmd = `ㅇ레시피 "${b.name}"`;
    outputs.push(wrap(recipeCmd, JSON.stringify(b.recipe, null, 0)));
  });

  // shop boxes
  data.boxes.shopBoxes.forEach(b => {
    const cmd = `ㅇ열기 "${b.name}"`;
    const res = openBox(b.name);
    outputs.push(wrap(cmd, _formatOpenResult(res)));
  });

  const outPath = path.join(__dirname, 'outputs.txt');
  fs.writeFileSync(outPath, outputs.join('\n\n'), { encoding: 'utf8' });
  return outPath;
}

if (require.main === module) {
  const [, , cmd, ...rest] = process.argv;
  const command = cmd || '';

  if (command === 'open' || command === 'ㅇ열기') {
    const name = rest.join(' ');
    const res = openBox(name);
    console.log(_formatOpenResult(res));
  } else if (command === 'list' || command === 'ㅇ상자목록') {
    console.log(_formatListAll(listBoxes('all')));
  } else if (command === 'recipe' || command === 'ㅇ레시피') {
    const name = rest.join(' ');
    const recipe = getRecipe(name);
    console.log(recipe ? JSON.stringify(recipe, null, 2) : '레시피를 찾을 수 없습니다.');
  } else if (command === 'runplan' || command === '실행') {
    const outPath = runPlanAndSave();
    console.log(`출력이 '${outPath}'에 저장되었습니다.`);
  } else {
    console.log('사용법: node script.js ㅇ열기 "상자이름"  |  node script.js ㅇ상자목록  |  node script.js ㅇ레시피 "상자이름"  |  node script.js 실행(또는 runplan)');
  }
}
