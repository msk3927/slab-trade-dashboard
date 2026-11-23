# 슬라브 수출 · 수입 대시보드

HS 720712 슬라브의 국가별 수출과 수입을 세계 지도에서 보는 Streamlit 앱입니다. 나라를 누르면 상대국과 물량이 선으로 연결됩니다.

## 실행

```bash
python -m pip install -r requirements.txt
python -m streamlit run slab_trade_dashboard.py
```

Windows에서는 `run_slab_dashboard.bat`을 실행해도 됩니다.

같은 열 구성의 엑셀을 화면에서 올리면 지도가 그 파일로 바뀝니다. 열은 `기준국가`, `수출/수입`, `YEAR`, `MONTH`, `TARIFF_CODE`, `TARIFF_DESCRIPTION`, `대상국가`, `Tonnes`입니다.

화면 왼쪽 위의 EN 버튼으로 한국어와 영어를 바꿀 수 있습니다.

## 웹 링크로 공유 (Python 없이 보기)

[Streamlit Community Cloud](https://share.streamlit.io/)에서 GitHub 저장소를 연결하면 `https://….streamlit.app` 주소로 공유할 수 있습니다.

1. [share.streamlit.io](https://share.streamlit.io/) 접속 → **Continue to sign-in** → **GitHub**로 로그인 (`msk3927` 계정 권장)
2. **Create app** (또는 **New app**)
3. **Repository**: `msk3927/slab-trade-dashboard` / **Branch**: `main`
4. **Main file path**: `streamlit_app.py` (또는 `slab_trade_dashboard.py`)
5. **Deploy** 클릭 → 몇 분 후 공개 URL이 생성됩니다

클라우드에는 엑셀·폰트 파일이 없습니다. 접속한 사람은 화면에서 **동일 양식 엑셀 업로드**로 자료를 올려야 지도가 보입니다.
