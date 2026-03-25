import streamlit as st
import requests
from datetime import datetime

# [1. 설정]
TELEGRAM_TOKEN = '8438716732:AAGLb4rhWyx-G2khyvcfio1-4aRRgBCyz1I'
CHAT_ID = '8479493770'

# [2. 데이터 구성] - 이미지 리스트 전체 반영
RAW_DATA = {
    "소스/가공/냉동": {
        "진간장": "쿠팡", "국간장": "쿠팡", "치킨파우더": "쿠팡", "고추맛기름": "쿠팡", "참기름": "쿠팡",
        "참깨드레싱": "쿠팡", "요리당": "쿠팡", "유자폰즈": "쿠팡", "들기름": "쿠팡", "트러플오일": "쿠팡",
        "케찹": "쿠팡", "마요네즈": "쿠팡", "식용유": "따봉 유통", "굴소스": "쿠팡", "두반장": "쿠팡",
        "습식빵가루": "오뚜기 유통", "건식빵가루": "오뚜기 유통", "우동면": "쿠팡", "오뎅": "쿠팡"
    },
    "신선/야채/수산": {
        "오이": "청량리", "당근": "청량리", "사과": "청량리", "양파": "쿠팡", "대파": "청량리",
        "무": "쿠팡", "청양고추": "청량리", "마늘": "청량리", "토마토": "청량리", "연어": "노량진",
        "광어": "노량진", "참치": "노량진", "도미": "노량진", "모시조개": "노량진", "전복": "노량진",
        "방어": "노량진", "단새우": "노량진", "메로": "우림유통", "타다끼 참치": "우림유통"
    },
    "육류/유제품": {
        "육회고기": "토방고기나라", "대창": "독산 우시장", "아롱사태": "독산 우시장", "우삼겹": "금천미트",
        "모짜렐라치즈": "쿠팡", "그라노파다노": "쿠팡", "크림치즈": "쿠팡", "스모크치즈": "코스트코"
    },
    "주류/음료": {
        "서울의밤": "고성주류", "문경바람": "고성주류", "만월": "고성주류", "화요25": "고성주류",
        "콜라": "휘샘", "사이다": "휘샘", "토닉워터": "쿠팡", "트레비": "롯데칠성"
    },
    "소모품/비품": {
        "부탄가스": "쿠팡", "니트릴장갑M": "쿠팡", "니트릴장갑L": "쿠팡", "물티슈": "쿠팡",
        "유니랩": "쿠팡", "바이오크린콜": "네이버", "오븐크리너": "쿠팡"
    }
}

LIQUORS = ["참이슬", "진로", "새로", "처음처럼", "카스", "테라", "켈리", "일품진로", "백화수복"]

# [3. 앱 설정 및 세션 초기화]
st.set_page_config(page_title="우물 통합 발주", layout="wide")

# CSS를 사용하여 폰트 크기 및 스타일 조정
st.markdown("""
    <style>
    .order-title { font-size: 24px !important; font-weight: bold; color: #1E88E5; }
    .vendor-name { font-size: 20px !important; font-weight: bold; color: #E64A19; margin-top: 15px; }
    .item-row { font-size: 18px !important; padding: 5px 0; border-bottom: 1px solid #f0f2f6; }
    .qty-text { color: #2E7D32; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'store' not in st.session_state: st.session_state.store = None
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'last_order_msg' not in st.session_state: st.session_state.last_order_msg = None
if 'last_order_data' not in st.session_state: st.session_state.last_order_data = None

# [4. 메인 로직]
if st.session_state.store is None:
    st.title("🌊 우물 재료 관리 시스템")
    col1, col2 = st.columns(2)
    if col1.button("📍 사당우물", use_container_width=True):
        st.session_state.store = "사당우물"; st.rerun()
    if col2.button("📍 서초우물", use_container_width=True):
        st.session_state.store = "서초우물"; st.rerun()
else:
    col_h1, col_h2 = st.columns([4, 1])
    col_h1.markdown(f"<p class='order-title'>🏠 {st.session_state.store} 발주판</p>", unsafe_allow_html=True)
    if col_h2.button("지점 변경"):
        st.session_state.store = None; st.session_state.cart = {}; st.rerun()

    st.divider()

    left_col, right_col = st.columns([1.6, 1.4], gap="large")

    with left_col:
        st.subheader("📋 재료 선택")
        cat_tabs = st.tabs(list(RAW_DATA.keys()) + ["🍶 일반주류"])
        for i, cat in enumerate(RAW_DATA.keys()):
            with cat_tabs[i]:
                items = RAW_DATA[cat]
                cols = st.columns(3)
                for idx, (name, vend) in enumerate(items.items()):
                    with cols[idx % 3]:
                        if st.button(name, key=f"add_{name}", use_container_width=True):
                            st.session_state.cart[name] = {"vendor": vend, "qty": ""}
                            st.rerun()

        with cat_tabs[-1]:
            cols = st.columns(3)
            for idx, name in enumerate(LIQUORS):
                with cols[idx % 3]:
                    if st.button(name, key=f"liq_{name}", use_container_width=True):
                        vend = "금호주류" if "사당" in st.session_state.store else "케이주류"
                        st.session_state.cart[name] = {"vendor": vend, "qty": ""}
                        st.rerun()

    with right_col:
        st.subheader("🛒 담긴 목록")
        if not st.session_state.cart:
            st.info("왼쪽에서 재료를 선택해 주세요.")
        else:
            for item, info in list(st.session_state.cart.items()):
                c1, c2, c3 = st.columns([1.2, 1.5, 0.4])
                c1.markdown(f"<p style='font-size:17px; margin-top:5px;'><b>{item}</b></p>", unsafe_allow_html=True)
                q = c2.text_input("수량", key=f"q_{item}", value=info['qty'], label_visibility="collapsed", placeholder="수량 입력")
                st.session_state.cart[item]['qty'] = q
                if c3.button("❌", key=f"del_{item}"):
                    del st.session_state.cart[item]; st.rerun()
            
            st.divider()
            memo = st.text_area("📝 추가 요청사항 (메모)", height=70)
            if st.button("🚀 발주 확정 및 전송", type="primary", use_container_width=True):
                now = datetime.now().strftime("%m/%d %H:%M")
                grouped = {}
                for itm, inf in st.session_state.cart.items():
                    v = inf['vendor']
                    if v not in grouped: grouped[v] = []
                    grouped[v].append({"name": itm, "qty": inf['qty']})
                
                # 텔레그램용 텍스트
                msg = f"🔔 *[{st.session_state.store}]* 발주 ({now})\n\n"
                for v, itms in grouped.items():
                    msg += f"📦 *[{v}]*\n"
                    msg += "\n".join([f" • {i['name']} {i['qty']}".strip() for i in itms]) + "\n\n"
                if memo: msg += f"──────────────\n📝 *메모*: {memo}"

                try:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                    st.session_state.last_order_msg = msg
                    st.session_state.last_order_data = grouped
                    st.session_state.cart = {}
                    st.success("발주 전송 완료!")
                    st.rerun()
                except: st.error("전송 실패")

    # [하단: 영수증 스타일의 요약 내역]
    if st.session_state.last_order_data:
        st.divider()
        st.markdown("<p class='order-title'>✅ 최근 발주 확인서</p>", unsafe_allow_html=True)
        
        # 영수증 스타일의 컨테이너
        with st.container():
            for vendor, items in st.session_state.last_order_data.items():
                st.markdown(f"<p class='vendor-name'>📦 {vendor}</p>", unsafe_allow_html=True)
                for item in items:
                    qty_val = item['qty'] if item['qty'] else "-"
                    st.markdown(f"""
                        <div class="item-row">
                            <span style="display:inline-block; width:200px;">• {item['name']}</span>
                            <span class="qty-text">{qty_val}</span>
                        </div>
                    """, unsafe_allow_html=True)
        
        if st.button("내역 닫기", use_container_width=True):
            st.session_state.last_order_data = None
            st.rerun()