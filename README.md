# SG Rate Finder

휴대폰에서 브랜드별 현재 SG율과 S행사 항목을 조회하는 Streamlit 앱입니다. Excel의 `①SG点数表`와 `③S活动` 탭을 읽으며 원본 Excel을 수정하지 않습니다.

## 로컬 실행

Python 3.11 이상이 필요합니다. 프로젝트 폴더에서:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

처음에는 데이터가 없다는 메시지가 나옵니다. 관리자 화면을 별도 터미널에서 실행하세요.

```powershell
$env:ADMIN_PASSWORD = "여기에_본인_비밀번호"
streamlit run admin.py --server.port 8502
```

관리자 주소는 `http://localhost:8502`입니다. 비밀번호 입력 후 Excel을 선택하고 **分析** → 검증 결과 확인 → **确认更新** 순서로 진행합니다. 공개 앱은 기본 `http://localhost:8501`입니다. 관리자 앱은 노트북에서만 실행합니다. 공개 앱에 관리자 기능을 포함하지 않습니다.

S행사 조회는 브랜드를 선택하거나 REF NO./AGING을 입력해 항목별 율을 찾습니다. 새 Excel을 관리자 화면에서 반영하면 `data/published_rates.json`에도 S행사 항목이 포함됩니다. 이 파일을 GitHub에 올려야 휴대폰 앱에 반영됩니다.

브랜드 분류 마스터는 선택 사항입니다. `data/brand_master.csv`에 UTF-8로 `brand_name,category` 헤더와 브랜드 분류를 넣으면 개별율이 없는 브랜드에 일반율을 자동 연결합니다. 분류를 모르면 사용자가 직접 선택합니다.

## 테스트

```powershell
python -m unittest discover -s tests -v
```

실제 회사 Excel 파일은 이 폴더에 제공되지 않았으므로 대표 값은 모의 통합문서로 검증합니다. 실제 파일을 관리자 화면에서 분석한 뒤 브랜드와 일반율 건수, 최신 적용일, 경고를 확인하세요. `data/sg_rate.db`, 백업, Excel 원본은 Git 추적에서 제외됩니다.

## PC가 꺼져도 열리는 고정 주소 배포

Streamlit Community Cloud의 로컬 파일 변경은 영구 보존되지 않습니다. 따라서 관리자 화면에서 검증한 로컬 DB를 **공개 조회용 JSON 스냅샷**으로 내보내고 GitHub에 게시합니다. 원본 Excel, 로컬 DB, 백업, 비밀번호는 게시하지 않습니다. 공개 스냅샷에는 브랜드명, 분류, 결제방식, 날짜별 율, 비고가 포함되므로 게시 전에 내용을 확인하세요.

1. 로컬 관리자 화면에서 Excel을 분석하고 업데이트합니다.
2. 관리자 화면에서 **确认更新**을 누르면 `data/published_rates.json`이 생성됩니다. 필요하면 프로젝트 폴더에서 `python publish_data.py`를 실행해 다시 생성할 수 있습니다.
3. GitHub 저장소를 만들고 프로젝트 코드를 업로드합니다. `.gitignore`가 제외한 Excel, `data/sg_rate.db`, `data/backups/`, `.env`, `.streamlit/secrets.toml`은 업로드하지 않습니다. `data/published_rates.json`은 포함합니다.
4. [Streamlit Community Cloud](https://share.streamlit.io/)에 GitHub 계정으로 로그인해 **Create app**에서 저장소와 `app.py`를 선택합니다. 원하는 `*.streamlit.app` 주소를 지정할 수 있습니다.
5. GitHub 저장소가 비공개라면 앱의 **Sharing** 설정에서 공개로 전환합니다. 이 경우에도 공개용 스냅샷 데이터는 앱 이용자가 조회할 수 있습니다.
6. 휴대폰에서 해당 `https://...streamlit.app` 주소를 엽니다. PC 전원을 꺼도 접속할 수 있습니다.

## 새 Excel 반영

1. 노트북에서 관리자 앱을 열고 새 Excel을 **分析**한 뒤 내용을 확인하고 **确认更新**을 누릅니다.
2. GitHub의 `Code0-MMM/SG-Rate_finder` 저장소에서 `data` 폴더를 열고 **Add file → Upload files**를 누릅니다.
3. 노트북의 프로젝트 폴더에 있는 `data/published_rates.json`을 선택하고 **Commit changes**를 누릅니다. 같은 이름의 기존 파일을 교체합니다.
4. Streamlit Community Cloud가 GitHub 변경을 반영한 뒤 휴대폰에서 앱을 새로고침합니다.

GitHub 토큰은 필요하지 않습니다. 노트북은 데이터를 갱신할 때만 켜면 됩니다. 원본 Excel과 로컬 DB는 GitHub에 올리지 않습니다.
