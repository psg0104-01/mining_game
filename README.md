# 광산 게임 데이터 및 JS 유틸

이 저장소는 `kkkkkk.txt`에 적힌 광산 게임 스펙을 기반으로 생성된 JSON 데이터(`data.json`)와 함수형 JavaScript(`script.js`)입니다.

파일
- `data.json`: 상자, 조합 레시피, 곡괭이 목록과 확률을 JSON으로 정리한 파일
- `script.js`: 데이터 로드 및 상자 개봉 시뮬레이션 등 유틸 함수들을 제공합니다

주요 함수
- `listBoxes(section)` - 상자 목록을 가져옵니다. section은 `all|mystery|random|craft|shop`.
- `openBox(boxName)` - 상자 이름으로 개봉을 시뮬레이션합니다. `???상자`(mystery)를 입력하면 내부에서 어떤 상자가 나오는지도 처리합니다.
- `getPickaxeList(grade)` - 등급별 곡괭이 목록을 반환합니다.
- `getRecipe(boxName)` - 조합상자 레시피를 반환합니다.

간단 사용 예 (Windows PowerShell)

- 상자 목록 보기:

```powershell
node .\script.js list
```

- ???상자 개봉 시뮬레이션:

```powershell
node .\script.js open "???상자"
```

- 특정 상자 개봉 예:

```powershell
node .\script.js open "왕의상자"
```

직접 코드에서 사용하기 (Node.js 모듈 방식)

```js
const { openBox, listBoxes, getRecipe } = require('./script');
console.log(openBox('용사의상자'));
console.log(listBoxes('random'));
console.log(getRecipe('창세조합상자'));
```

다음 단계 제안
- 게임 서버나 봇에 붙일 경우, 플레이어 데이터를 파일(`players.json`) 또는 DB로 관리하는 기능 추가
- 확률 검증을 위한 단위 테스트 추가
- 상자 보상에 골드/아이템 혼합 로직 추가

간단한 변경이나 원하는 추가 기능이 있으면 알려주세요.