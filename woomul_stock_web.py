import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# [1. 설정]
TELEGRAM_TOKEN = '8438716732:AAGLb4rhWyx-G2khyvcfio1-4aRRgBCyz1I'
CHAT_ID = '8479493770'

# [2. 데이터 구성]
# 일반 식자재 (공통)
RAW_DATA = {
    "소스/조미료": {
        "진간장": "쿠팡", "국간장": "쿠팡", "치킨파우더": "쿠팡", "고추맛기름": "쿠팡", "참기름": "쿠팡",
        "육회 참기름": "쿠팡", "참깨드레싱": "쿠팡", "요리당": "쿠팡", "시오다래": "쿠팡", "유자폰즈": "쿠팡",
        "들기름": "쿠팡", "트러플오일": "쿠팡", "매실청": "쿠팡", "유자청": "쿠팡", "스모키얼그레이": "쿠팡",
        "사양벌꿀": "쿠팡", "케찹": "쿠팡", "마요네즈": "쿠팡", "식초": "쿠팡", "미원": "쿠팡",
        "미원맛소금": "쿠팡", "설탕": "쿠팡", "참깨": "쿠팡", "통후추": "쿠팡", "크러쉬레드페퍼": "쿠팡",
        "백후추": "쿠팡", "쿠라콘시오콘부": "쿠팡", "소고기다시다": "쿠팡", "멸치다시다": "쿠팡", "굴소스": "쿠팡",
        "두반장": "쿠팡", "깻잎페스토": "우물 제작", "짬뽕다데기": "우물 제작", "대창다데기": "우물 제작",
        "와사비": "네이버", "회간장": "쿠팡", "고춧가루": "직접 구매", "염지제": "쿠팡", "풍미왕": "네이버"
    },
    "야채/신선": {
        "오이": "청량리", "당근": "청량리", "사과": "청량리", "양배추": "쿠팡", "적채": "청량리",
        "팽이버섯": "쿠팡", "깻잎": "청량리", "미나리": "청량리", "시소": "오뚜기 유통", "무순": "오뚜기 유통",
        "쪽파": "청량리", "대파": "청량리", "청양고추": "청량리", "꽈리고추": "청량리", "양파": "쿠팡",
        "무": "쿠팡", "쌀": "쿠팡", "간마늘": "청량리", "배추": "쿠팡", "부추": "쿠팡", "두부": "쿠팡",
        "레몬": "쿠팡", "아보카도": "롯데슈퍼", "토마토": "청량리", "안동마": "네이버", "표고버섯고추냉이": "네이버"
    },
    "수산/육류/유제품": {
        "연어": "노량진", "광어": "노량진", "참치": "노량진", "도미": "노량진", "삼치": "노량진",
        "모시조개": "노량진", "전복": "노량진", "가리비관자": "노량진", "방어": "노량진", "단새우": "노량진",
        "메로": "우림유통(문자)", "타다끼 참치": "우림유통(문자)", "명란젓": "노량진", "안키모": "네이버",
        "육회고기": "토방고기나라", "아롱사태": "독산 우시장", "대창": "독산 우시장", "우삼겹": "금천미트",
        "닭다리": "쿠팡", "함박스테이크": "우물 제작", "모짜렐라치즈": "쿠팡", "그라노파다노": "쿠팡", 
        "크림치즈": "쿠팡", "스모크치즈": "코스트코", "미니브리치즈": "코스트코", "브라운치즈": "네이버"
    },
    "비품/소모품": {
        "부탄가스": "쿠팡", "니트릴장갑M": "쿠팡", "니트릴장갑L": "쿠팡", "물티슈": "쿠팡",
        "유니랩": "쿠팡", "바이오크린콜": "네이버", "오븐크리너": "쿠팡", "네프킨": "주문 제작",
        "마스크": "쿠팡", "대나무잎": "네이버", "크린백": "다이소", "액체세제": "다이소", "앞치마": "쿠팡"
    }
}

# 주류 데이터
LIQUORS_COMMON = ["참이슬", "진로", "새로", "처음처럼", "카스", "테라", "켈리", "일품진로", "화요25", "화요41", "백화수복"]

# 전통주 및 기타 주류 (누락분 추가)
TRADITIONAL_VENDORS = {
    "고성주류": ["서울의밤25", "서울의밤40", "문경바람25", "문경바람40", "만월24", "만월40", "화랑", "서설", "안동소주", "토끼소주23", "토끼소주40", "고흥유자주", "우렁이쌀주", "두레앙", "매실원주", "사랑할때", "니모메", "빙탄복", "서울고량주", "동해", "복순도가", "추사", "부자막걸리", "경주법주 초특선", "한스오차드", "그랑꼬또로제"],
    "부국주류": ["독도", "느린마을소주", "나루생막걸리", "느린마을막걸리", "조선주조사"],
    "음료/기타": ["콜라", "사이다", "제로콜라", "트레비", "토닉워터", "진저에일"]
}

# 위스키 및 사케 (서초 전용)
WHISKEY_SAKE_VENDORS = {
    "케이주류(위스키)": ["조니워커블루", "맥켈란15Y", "맥켈란12Y", "발렌타인17Y", "달모어12Y", "글렌피딕15Y", "글렌피딕12Y", "발베니12Y", "아드벡10Y", "탈리스커10Y", "헤네시VSOP", "몽키숄더", "메이커스마크"],
    "일로사케": ["사와야 마츠모토 울트라", "자쿠 미야비노토모", "아키토라 준마이다이긴조", "키쿠노츠카사 이노센트", "후쿠쵸 준마이 시후도", "킷도 준마이다이긴조", "스모노 준마이긴조", "쿠보타 센쥬", "도쿠리(아카부 준마이)"]
}

# [3. 앱 설정]
st.set_page_config(page_title="우물 통합 발주", layout="wide")

st.markdown("""
    <style>
    .stButton>button { height: 28px !important; padding: 0px 5px !important; font-size: 12px !important; margin-bottom: -5px; }
    .order-title { font-size: 20px !important; font-weight: bold; color: #0D47A1; }
    .section-box { padding: 12px; border-radius: 8px; background-color: #fcfcfc; border: 1px solid #e0e0e0; }
    .item-label { font-size: 13px; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

if 'store' not in st.session_state: st.session_state.store = None
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'order_history' not in st.session_state: st.session_state.order_history = None

# [4. 메인 로직]
if st.session_state.store is None:
    st.title("🌊 우물 통합 발주 시스템")
    c1, c2 = st.columns(2)
    if c1.button("📍 사당우물 (금호주류)", use_container_width=True): st.session_state.store = "사당우물"; st.rerun()
    if c2.button("📍 서초우물 (케이주류)", use_container_width=True): st.session_state.store = "서초우물"; st.rerun()
else:
    h_col1, h_col2 = st.columns([5, 1])
    h_col1.markdown(f"<p class='order-title'>🏠 {st.session_state.store} 모드</p>", unsafe_allow_html=True)
    if h_col2.button("지점 변경"): st.session_state.store = None; st.session_state.cart = {}; st.rerun()

    st.divider()
    search_q = st.text_input("🔍 재료 및 주류 빠른 검색", placeholder="이름을 입력하세요...")

    left_col, right_col = st.columns([2, 1.2], gap="medium")

    with left_col:
        # 검색 필터링
        if search_q:
            found = []
            for cat, items in RAW_DATA.items():
                for name, vend in items.items():
                    if search_q in name: found.append((name, vend))
            
            # 주류 검색 포함 (지점별 로직 반영)
            main_v = "금호주류" if "사당" in st.session_state.store else "케이주류"
            for n in LIQUORS_COMMON:
                if search_q in n: found.append((n, main_v))
            for v, ilist in TRADITIONAL_VENDORS.items():
                for n in ilist:
                    if search_q in n: found.append((n, v))
            if "서초" in st.session_state.store:
                for v, ilist in WHISKEY_SAKE_VENDORS.items():
                    for n in ilist:
                        if search_q in n: found.append((n, v))

            if found:
                st.caption(f"🔎 '{search_q}' 검색 결과")
                scols = st.columns(5)
                for idx, (n, v) in enumerate(found):
                    with scols[idx % 5]:
                        if st.button(n, key=f"src_{n}", use_container_width=True):
                            st.session_state.cart[n] = {"vendor": v, "qty": ""}
                            st.rerun()
            st.divider()

        # 메인 탭
        tabs = st.tabs(["🛒 식자재/비품", "🍶 주류/음료"])
        
        with tabs[0]:
            for cat, items in RAW_DATA.items():
                with st.expander(f"📦 {cat}", expanded=(cat == "소스/조미료")):
                    cols = st.columns(5)
                    for idx, (name, vend) in enumerate(items.items()):
                        with cols[idx % 5]:
                            if st.button(name, key=f"btn_{name}", use_container_width=True):
                                st.session_state.cart[name] = {"vendor": vend, "qty": ""}
                                st.rerun()

        with tabs[1]:
            # 1. 일반주류 (사당=금호, 서초=케이)
            main_v = "금호주류" if "사당" in st.session_state.store else "케이주류"
            st.markdown(f"**🟢 {main_v} (일반)**")
            lcols = st.columns(5)
            for idx, name in enumerate(LIQUORS_COMMON):
                with lcols[idx % 5]:
                    if st.button(name, key=f"lq_{name}", use_container_width=True):
                        st.session_state.cart[name] = {"vendor": main_v, "qty": ""}
                        st.rerun()
            
            # 2. 전통주/음료
            st.markdown("**🔵 전통주/음료**")
            for v, ilist in TRADITIONAL_VENDORS.items():
                st.caption(f"📍 {v}")
                icols = st.columns(5)
                for idx, name in enumerate(ilist):
                    with icols[idx % 5]:
                        if st.button(name, key=f"tr_{name}", use_container_width=True):
                            st.session_state.cart[name] = {"vendor": v, "qty": ""}
                            st.rerun()

            # 3. 위스키/사케 (서초 전용)
            if "서초" in st.session_state.store:
                st.markdown("**🥃 위스키/프리미엄 사케 (서초 전용)**")
                for v, ilist in WHISKEY_SAKE_VENDORS.items():
                    st.caption(f"📍 {v}")
                    icols = st.columns(5)
                    for idx, name in enumerate(ilist):
                        with icols[idx % 5]:
                            if st.button(name, key=f"pr_{name}", use_container_width=True):
                                st.session_state.cart[name] = {"vendor": v, "qty": ""}
                                st.rerun()

    with right_col:
        st.markdown("<div class='section-box'><b>🛒 현재 발주 목록</b>", unsafe_allow_html=True)
        if not st.session_state.cart:
            st.write("품목을 선택하세요.")
        else:
            for item, info in list(st.session_state.cart.items()):
                c1, c2, c3 = st.columns([1.5, 1, 0.4])
                c1.markdown(f"<span class='item-label'>{item}</span>", unsafe_allow_html=True)
                q = c2.text_input("수량", key=f"q_{item}", value=info['qty'], label_visibility="collapsed", placeholder="수량")
                st.session_state.cart[item]['qty'] = q
                if c3.button("×", key=f"del_{item}"): del st.session_state.cart[item]; st.rerun()
            
            st.divider()
            memo = st.text_area("📝 추가 메모", height=60)
            if st.button("🚀 발주 전송", type="primary", use_container_width=True):
                now = datetime.now().strftime("%m/%d %H:%M")
                table_rows = []
                grouped = {}
                for itm, inf in st.session_state.cart.items():
                    v, q = inf['vendor'], inf['qty']
                    if v not in grouped: grouped[v] = []
                    grouped[v].append(f" • {itm} {q}")
                    table_rows.append({"구매처": v, "품목": itm, "수량": q})

                msg = f"🔔 *[{st.session_state.store}]* 발주 ({now})\n\n"
                for v, itms in grouped.items():
                    msg += f"📦 *[{v}]*\n" + "\n".join(itms) + "\n\n"
                if memo: msg += f"──────────────\n📝 *메모*: {memo}"

                try:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                    st.session_state.order_history = pd.DataFrame(table_rows)
                    st.session_state.cart = {}
                    st.success("전송 성공!")
                    st.rerun()
                except: st.error("전송 실패")
        st.markdown("</div>", unsafe_allow_html=True)

    # 최근 내역 표 정리
    if st.session_state.order_history is not None:
        st.divider()
        st.markdown("<p class='order-title'>📊 최근 발주 요약 표</p>", unsafe_allow_html=True)
        st.table(st.session_state.order_history)
        if st.button("내역 닫기", use_container_width=True):
            st.session_state.order_history = None; st.rerun()
