# SG Rate Finder 데이터 갱신 및 `git pull` 안내

이 문서는 **새 SG 율표 Excel을 반영**하고, 다른 컴퓨터에서 GitHub의 최신 파일을 가져오는 순서입니다.

## 1. 노트북에서 새 Excel 반영

1. PowerShell에서 관리자 프로젝트 폴더로 이동합니다.

   ```powershell
   cd 'C:\Users\jinzh\Desktop\SG율확인\_외부용'
   ```

2. 관리자 비밀번호를 설정하고 관리자 화면을 실행합니다. 이미 실행 중이면 이 단계는 건너뜁니다.

   ```powershell
   $env:ADMIN_PASSWORD = '본인이_정한_비밀번호'
   streamlit run admin.py --server.port 8502
   ```

3. 브라우저에서 `http://localhost:8502`를 열고 로그인합니다. 새 Excel 파일을 선택한 뒤 **分析**을 누릅니다.
4. 파일명, 브랜드 건수, 일반율 건수, 최신 적용일과 경고를 확인합니다. 올바르면 **确认更新**을 누릅니다.
5. 관리자 화면이 로컬 DB와 공개용 `data/published_rates.json`을 갱신합니다. **이 단계만으로 GitHub나 휴대폰 앱은 바뀌지 않습니다.**

`streamlit` 명령을 찾지 못하면 프로젝트의 가상환경에서 아래처럼 실행합니다.

```powershell
.\.venv\Scripts\streamlit.exe run admin.py --server.port 8502
```

## 2. GitHub에 공개용 파일 업로드

1. GitHub의 [`SG-Rate_finder/data` 폴더](https://github.com/Code0-MMM/SG-Rate_finder/tree/main/data)를 엽니다.
2. **Add file → Upload files**를 누릅니다.
3. 노트북의 `C:\Users\jinzh\Desktop\SG율확인\_외부용\data\published_rates.json`을 선택합니다. GitHub 화면에서 대상 경로가 **`data/published_rates.json`**인지 확인합니다.
4. **Commit changes**를 누릅니다. 같은 이름의 기존 파일을 새 내용으로 교체합니다.
5. GitHub에서 `published_rates.json`의 갱신 시각을 확인한 뒤 휴대폰 앱을 새로고침합니다. 배포 반영에는 잠시 시간이 걸릴 수 있습니다.

원본 Excel, `sg_rate.db`, `data/backups` 폴더, 관리자 비밀번호는 GitHub에 올리지 않습니다. `published_rates.json`에는 조회에 쓰는 브랜드명, 율, 날짜, 비고 등이 담기므로 공개 가능한 내용인지 확인합니다.

## 3. 회사 컴퓨터에서 `git pull`

회사 컴퓨터의 프로젝트가 이미 Git 저장소로 복제되어 있다면, 그 프로젝트 폴더에서 실행합니다.

```powershell
git pull origin main
```

이 명령은 **GitHub `main` 브랜치에 올라온 변경 사항을 회사 컴퓨터의 현재 폴더로 가져와 반영**합니다. GitHub에 파일을 올리는 명령은 아닙니다. `Already up to date.`가 나오면 가져올 새 커밋이 없는 상태입니다.

처음 가져오는 컴퓨터라면 `git pull` 대신 아래 명령으로 복제합니다.

```powershell
git clone https://github.com/Code0-MMM/SG-Rate_finder.git
```

ZIP 파일로 내려받은 폴더에는 `.git` 정보가 없어 `git pull`을 사용할 수 없습니다. 그 경우 `git clone`으로 새 폴더를 만듭니다. `git pull`은 GitHub에 게시된 파일만 가져오며, 노트북의 로컬 DB, 원본 Excel, 관리자 비밀번호는 가져오지 않습니다.

## 갱신이 보이지 않을 때

- GitHub의 `data/published_rates.json`이 새 커밋으로 바뀌었는지 확인합니다.
- GitHub 파일이 예전 내용이면 2단계 업로드와 **Commit changes**를 다시 확인합니다.
- GitHub 파일은 새것인데 휴대폰 앱이 예전 내용이면 잠시 기다렸다가 앱을 새로고침합니다.
- 관리자 화면에서 JSON 생성 오류가 났다면 프로젝트 폴더에서 `python publish_data.py`를 실행한 뒤 2단계를 진행합니다.
