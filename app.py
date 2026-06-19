import streamlit as st
from datetime import datetime
import json

st.set_page_config(
    page_title="충남119 복무AI",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# 세션 상태 초기화
# ========================================
if "users" not in st.session_state:
    st.session_state.users = {
        "qhtjd0611": {"password": "119", "role": "superadmin", "name": "최고관리자"},
        "admin": {"password": "119", "role": "admin", "name": "관리자"}
    }

if "login_user" not in st.session_state:
    st.session_state.login_user = None

if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

if "faq_counts" not in st.session_state:
    st.session_state.faq_counts = {
        "병가": 0,
        "공가": 0,
        "초과근무": 0,
        "e사람": 0,
        "온나라": 0,
        "e호조": 0,
        "법령": 0,
        "조례": 0,
    }

# ========================================
# 119 공식 색상 & 스타일
# ========================================
PRIMARY_RED = "#C41E3A"      # 소방 빨강
DARK_RED = "#A01830"        # 진한 빨강
NAVY = "#1A3A52"            # 신뢰감 있는 네이비
LIGHT_BG = "#F5F7FA"        # 밝은 배경
WHITE = "#FFFFFF"           # 흰색
TEXT_DARK = "#2D3436"       # 진한 텍스트
TEXT_MUTED = "#636E72"      # 회색 텍스트
SUCCESS = "#27AE60"         # 초록
WARNING = "#F39C12"         # 주황
DANGER = "#E74C3C"          # 빨강

# ========================================
# CSS 스타일 정의
# ========================================
st.markdown(f"""
<style>
    * {{
        font-family: 'Segoe UI', 'Roboto', '본고딕', sans-serif;
    }}

    .stApp {{
        background: linear-gradient(135deg, {LIGHT_BG} 0%, #EEF2F7 100%);
    }}

    /* ===== 헤더/네비게이션 ===== */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {NAVY} 0%, {DARK_RED} 100%);
    }}

    section[data-testid="stSidebar"] * {{
        color: {WHITE} !important;
    }}

    section[data-testid="stSidebar"] .stRadio > label {{
        color: {WHITE} !important;
        font-weight: 700;
        padding: 12px 8px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }}

    section[data-testid="stSidebar"] .stRadio > label:hover {{
        background-color: rgba(255, 255, 255, 0.1);
    }}

    /* ===== 상단 배너 ===== */
    .header-banner {{
        background: linear-gradient(135deg, {PRIMARY_RED} 0%, {DARK_RED} 100%);
        color: {WHITE};
        padding: 36px 40px;
        border-radius: 16px;
        margin-bottom: 32px;
        box-shadow: 0 8px 24px rgba(196, 30, 58, 0.2);
        border-left: 6px solid {WHITE};
    }}

    .header-title {{
        font-size: 48px;
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .header-subtitle {{
        font-size: 16px;
        opacity: 0.95;
        margin-top: 8px;
        font-weight: 500;
    }}

    /* ===== 카드 ===== */
    .card {{
        background: {WHITE};
        border: 1px solid #E8EBED;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(45, 52, 54, 0.08);
        transition: all 0.3s ease;
    }}

    .card:hover {{
        box-shadow: 0 8px 24px rgba(45, 52, 54, 0.12);
        transform: translateY(-2px);
    }}

    .card-title {{
        color: {PRIMARY_RED};
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 12px;
        border-bottom: 3px solid {PRIMARY_RED};
        padding-bottom: 12px;
    }}

    /* ===== 정보박스 ===== */
    .info-box {{
        background: {WHITE};
        border-left: 6px solid {PRIMARY_RED};
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(196, 30, 58, 0.1);
    }}

    .info-box b {{
        color: {PRIMARY_RED};
        font-size: 16px;
    }}

    /* ===== 경고/주의박스 ===== */
    .warning-box {{
        background: rgba(243, 156, 18, 0.1);
        border-left: 6px solid {WARNING};
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 24px;
        color: {TEXT_DARK};
    }}

    .success-box {{
        background: rgba(39, 174, 96, 0.1);
        border-left: 6px solid {SUCCESS};
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 24px;
        color: {TEXT_DARK};
    }}

    /* ===== 입력 필드 ===== */
    div[data-testid="stTextInput"] input {{
        border-radius: 10px !important;
        border: 2px solid #E8EBED !important;
        padding: 14px 20px !important;
        font-size: 16px !important;
        background-color: {WHITE} !important;
        color: {TEXT_DARK} !important;
        transition: all 0.3s ease;
    }}

    div[data-testid="stTextInput"] input:focus {{
        border-color: {PRIMARY_RED} !important;
        box-shadow: 0 0 0 3px rgba(196, 30, 58, 0.1) !important;
    }}

    div[data-testid="stTextArea"] textarea {{
        border-radius: 10px !important;
        border: 2px solid #E8EBED !important;
        font-family: inherit;
    }}

    div[data-testid="stTextArea"] textarea:focus {{
        border-color: {PRIMARY_RED} !important;
        box-shadow: 0 0 0 3px rgba(196, 30, 58, 0.1) !important;
    }}

    /* ===== 버튼 ===== */
    .stButton > button {{
        width: 100%;
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, {PRIMARY_RED} 0%, {DARK_RED} 100%);
        color: {WHITE};
        padding: 14px 24px;
        font-weight: 800;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(196, 30, 58, 0.15);
    }}

    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(196, 30, 58, 0.25);
    }}

    .stButton > button:active {{
        transform: translateY(0);
    }}

    /* ===== 탭 ===== */
    .stTabs [data-baseweb="tab-list"] button {{
        font-weight: 700;
        border-bottom: 3px solid transparent;
        color: {TEXT_MUTED};
        transition: all 0.3s ease;
    }}

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        color: {PRIMARY_RED};
        border-bottom-color: {PRIMARY_RED};
    }}

    /* ===== 상태 표시 ===== */
    .status-badge {{
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
    }}

    .status-pending {{
        background: rgba(243, 156, 18, 0.2);
        color: #E67E22;
    }}

    .status-approved {{
        background: rgba(39, 174, 96, 0.2);
        color: #27AE60;
    }}

    .status-rejected {{
        background: rgba(231, 76, 60, 0.2);
        color: #E74C3C;
    }}

    .status-hold {{
        background: rgba(52, 152, 219, 0.2);
        color: #3498DB;
    }}

    /* ===== FAQ 태그 ===== */
    .faq-pill {{
        display: inline-block;
        background: {WHITE};
        border: 2px solid {PRIMARY_RED};
        border-radius: 20px;
        padding: 10px 20px;
        margin: 8px 8px 8px 0;
        font-weight: 700;
        color: {PRIMARY_RED};
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(196, 30, 58, 0.1);
    }}

    .faq-pill:hover {{
        background: {PRIMARY_RED};
        color: {WHITE};
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(196, 30, 58, 0.2);
    }}

    /* ===== 메타정보 ===== */
    .meta-info {{
        color: {TEXT_MUTED};
        font-size: 14px;
        font-weight: 500;
    }}

    .divider {{
        border: none;
        border-top: 2px solid #E8EBED;
        margin: 32px 0;
    }}

    /* ===== 테이블 ===== */
    .stDataFrame {{
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(45, 52, 54, 0.08) !important;
    }}

    /* ===== 셀렉트박스 ===== */
    div[data-testid="stSelectbox"] > div {{
        border-radius: 10px;
    }}

    /* ===== 반응형 그리드 ===== */
    .grid-2 {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 24px;
    }}

    /* ===== 애니메이션 ===== */
    @keyframes slideIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    .slide-in {{
        animation: slideIn 0.3s ease-out;
    }}

    /* ===== 사용자 정보 배지 ===== */
    .user-badge {{
        background: {WHITE};
        border-left: 4px solid {PRIMARY_RED};
        padding: 12px 16px;
        border-radius: 8px;
        font-weight: 700;
        color: {TEXT_DARK};
    }}
</style>
""", unsafe_allow_html=True)

# ========================================
# 공통 함수
# ========================================
def show_header(title: str, subtitle: str = ""):
    """119 스타일 헤더 표시"""
    st.markdown(f"""
    <div class="header-banner">
        <div class="header-title">🚒 {title}</div>
        <div class="header-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def show_info_box(title: str, content: str):
    """정보 박스 표시"""
    st.markdown(f"""
    <div class="info-box">
        <b>{title}</b><br>
        {content}
    </div>
    """, unsafe_allow_html=True)


def show_warning_box(title: str, content: str):
    """경고 박스 표시"""
    st.markdown(f"""
    <div class="warning-box">
        <b>⚠️ {title}</b><br>
        {content}
    </div>
    """, unsafe_allow_html=True)


def get_role():
    user = st.session_state.login_user
    return st.session_state.users[user]["role"]


def is_admin():
    return get_role() in ["admin", "superadmin"]


def is_superadmin():
    return get_role() == "superadmin"


def role_name(role):
    roles = {
        "superadmin": "👑 최고관리자",
        "admin": "👔 관리자",
        "user": "👤 일반사용자"
    }
    return roles.get(role, "사용자")


def status_badge(status):
    """상태 배지 HTML 반환"""
    badges = {
        "승인대기": f'<span class="status-badge status-pending">🟡 승인대기</span>',
        "승인완료": f'<span class="status-badge status-approved">🟢 승인완료</span>',
        "반려": f'<span class="status-badge status-rejected">🔴 반려</span>',
        "보류": f'<span class="status-badge status-hold">🔵 보류</span>'
    }
    return badges.get(status, status)


def classify_question(q: str):
    """사용자 질문 카테고리 분류"""
    q = q.lower()
    
    categories = {
        "병가": ["병가"],
        "공가": ["공가"],
        "초과근무": ["초과", "시간외"],
        "e사람": ["e사람", "이사람"],
        "온나라": ["온나라"],
        "e호조": ["e호조", "이호조", "예산", "지출"],
        "법령": ["법", "법령"],
        "조례": ["조례"]
    }
    
    for category, keywords in categories.items():
        if any(keyword in q for keyword in keywords):
            return category
    
    return "기타"


# ========================================
# 로그인 페이지
# ========================================
def login_page():
    col1, col2 = st.columns([1, 2])
    
    with col2:
        show_header("충남119 복무AI", "충남 소방공무원을 위한 복무·행정 안내 서비스")
    
    with col1:
        st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/docs/static/img/streamlit_logo_secondary_colormark.svg", 
                width=100)
    
    show_info_box(
        "🔐 로그인 안내",
        "개인정보 최소화를 위해 아이디와 비밀번호만 사용합니다. 안전한 접속 환경을 보장합니다."
    )
    
    tab1, tab2 = st.tabs(["🔑 로그인", "📝 회원가입"])
    
    with tab1:
        st.markdown("### 로그인")
        user_id = st.text_input("아이디", key="login_id", placeholder="사용자 아이디 입력")
        password = st.text_input("비밀번호", type="password", key="login_pw", placeholder="비밀번호 입력")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("로그인", use_container_width=True, key="btn_login"):
                if user_id in st.session_state.users and \
                   st.session_state.users[user_id]["password"] == password:
                    st.session_state.login_user = user_id
                    st.success("✅ 로그인 성공! 페이지를 새로고침합니다.")
                    st.rerun()
                else:
                    st.error("❌ 아이디 또는 비밀번호가 일치하지 않습니다.")
        
        st.markdown("---")
        st.caption("**테스트 계정**")
        st.caption("• 관리자: `admin` / `119`")
        st.caption("• 최고관리자: `qhtjd0611` / `119`")
    
    with tab2:
        st.markdown("### 회원가입")
        new_id = st.text_input("새 아이디", key="new_id", placeholder="생성할 아이디")
        new_pw = st.text_input("새 비밀번호", type="password", key="new_pw", placeholder="생성할 비밀번호")
        new_name = st.text_input("이름", key="new_name", placeholder="사용자 이름")
        
        if st.button("회원가입", use_container_width=True, key="btn_signup"):
            if not new_id or not new_pw:
                st.warning("⚠️ 아이디와 비밀번호를 모두 입력하세요.")
            elif new_id in st.session_state.users:
                st.error("❌ 이미 존재하는 아이디입니다.")
            else:
                st.session_state.users[new_id] = {
                    "password": new_pw,
                    "role": "user",
                    "name": new_name or "사용자"
                }
                st.success("✅ 회원가입이 완료되었습니다. 로그인해주세요.")


# ========================================
# 상단 정보바
# ========================================
def top_bar():
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        user_info = st.session_state.users[st.session_state.login_user]
        st.markdown(f"""
        <div class="user-badge">
            👤 {st.session_state.login_user} ({user_info.get('name', '사용자')}) 
            <br>
            {role_name(get_role())}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.login_user = None
            st.success("로그아웃되었습니다.")
            st.rerun()


# ========================================
# 홈 페이지
# ========================================
def home_page():
    show_header("복무·행정 안내", "복무규정, 병가, 공가 등 궁금한 사항을 물어보세요")
    
    show_info_box(
        "🤖 119 복무AI란?",
        "복무, 병가, 공가, 초과근무, e사람, 온나라, e호조 등 일상 업무 중 필요한 정보를 AI가 제공합니다. "
        "편하게 질문해주시면 정확한 답변과 함께 관련 법령을 안내합니다."
    )
    
    # 질문 입력
    st.markdown("### 💬 질문하기")
    question = st.text_input(
        "무엇이 궁금하신가요?",
        placeholder="예: 당직근무 중 15시에 병가를 쓰면 어떻게 처리해?",
        label_visibility="collapsed"
    )
    
    if question:
        category = classify_question(question)
        
        if category in st.session_state.faq_counts:
            st.session_state.faq_counts[category] += 1
        
        # 응답
        st.markdown("""
        <div class="card">
            <div class="card-title">✅ 답변</div>
            <p><strong>카테고리:</strong> {}</p>
            <p style="color: #636E72; font-size: 14px;">
                🔄 현재 <strong>Gemini API 연동 작업 중</strong>입니다.<br>
                다음 업데이트에서 실시간 AI 답변이 제공될 예정입니다.
            </p>
        </div>
        """.format(category), unsafe_allow_html=True)
        
        # 근거 조항
        st.markdown("### 📚 근거 조항")
        st.markdown(f"""
        <div class="card">
            <p><strong>분류:</strong> {category}</p>
            <ul>
                <li>공무원 복무규정</li>
                <li>지방공무원 복무규정</li>
                <li>충청남도 공무원 복무 조례</li>
            </ul>
            <p style="color: #636E72; font-size: 14px;">
                💾 모든 답변은 공식 법령과 최신 조례를 기반으로 제공됩니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 주의사항
        show_warning_box(
            "주의사항",
            "기관별 운영 차이가 있을 수 있으므로 최종 확인은 소속 복무담당자와 협의하시기 바랍니다."
        )
    
    # FAQ 순위
    st.markdown("---")
    st.markdown("### 🔥 인기 질문 TOP 5")
    
    sorted_faq = sorted(
        st.session_state.faq_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    faq_html = ""
    for i, (name, count) in enumerate(sorted_faq[:5], start=1):
        if count > 0:
            faq_html += f'<span class="faq-pill">#{i} {name} ({count})</span>'
    
    if faq_html:
        st.markdown(faq_html, unsafe_allow_html=True)
    else:
        st.info("아직 질문이 없습니다. 첫 번째 질문을 시작해보세요! 🎯")


# ========================================
# 법령·조례 페이지
# ========================================
def law_page():
    show_header("📚 법령·조례·매뉴얼", "충남119 복무AI의 참고 자료 목록")
    
    show_info_box(
        "📖 자료 안내",
        "현재 시스템이 참고하는 공식 법령, 조례, 매뉴얼을 확인하실 수 있습니다. "
        "각 자료의 최신 버전을 유지하고 있습니다."
    )
    
    st.markdown("### 등록된 자료 목록")
    
    data = {
        "구분": ["법령", "법령", "조례", "매뉴얼", "매뉴얼", "매뉴얼"],
        "자료명": [
            "공무원 복무규정",
            "지방공무원 복무규정",
            "충청남도 공무원 복무 조례",
            "e사람 사용 매뉴얼",
            "온나라 사용 매뉴얼",
            "e호조 사용 매뉴얼"
        ],
        "상태": ["📋 준비중", "📋 준비중", "📋 준비중", "📋 준비중", "📋 준비중", "📋 준비중"]
    }
    
    st.dataframe(data, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.info(
        "💡 **자료 업데이트 계획**\n\n"
        "• 법령: 매년 4월, 10월 갱신\n"
        "• 조례: 공포 즉시 업로드\n"
        "• 매뉴얼: 시스템 변경 시 즉시 반영"
    )


# ========================================
# 건의사항 페이지
# ========================================
def suggestion_page():
    show_header("💬 건의·신청", "필요한 자료를 신청해주세요")
    
    show_info_box(
        "📮 건의사항 안내",
        "누락된 법령, 조례, 매뉴얼, 업무자료를 신청하실 수 있습니다. "
        "신청하신 자료는 관리자가 검토하여 승인·반려·보류 처리합니다."
    )
    
    with st.form("suggestion_form", clear_on_submit=True):
        st.markdown("### 새로운 자료 신청")
        
        title = st.text_input("자료 제목", placeholder="신청할 자료의 제목")
        category = st.selectbox(
            "자료 종류",
            ["법령", "조례", "지침", "매뉴얼", "감사사례", "기타"],
            index=0
        )
        content = st.text_area("신청 사유", placeholder="자료가 필요한 이유를 설명해주세요", height=120)
        file = st.file_uploader("참고 파일 (선택)", type=["pdf", "doc", "docx", "hwp"])
        
        submitted = st.form_submit_button("📤 신청 제출", use_container_width=True)
        
        if submitted:
            if not title:
                st.error("❌ 자료 제목을 입력하세요.")
            else:
                st.session_state.suggestions.append({
                    "id": len(st.session_state.suggestions) + 1,
                    "title": title,
                    "category": category,
                    "content": content,
                    "file_name": file.name if file else "첨부 없음",
                    "status": "승인대기",
                    "user": st.session_state.login_user,
                    "user_name": st.session_state.users[st.session_state.login_user]["name"],
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("✅ 신청이 완료되었습니다. 관리자가 검토할 예정입니다.")
    
    st.markdown("---")
    st.markdown("### 📋 내 신청 목록")
    
    my_items = [x for x in st.session_state.suggestions if x["user"] == st.session_state.login_user]
    
    if not my_items:
        st.info("아직 신청한 자료가 없습니다. 위에서 첫 신청을 해보세요! 🎯")
    else:
        for item in my_items:
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <b style="font-size: 18px;">{item['title']}</b><br>
                        <span style="color: #636E72; font-size: 14px;">
                            📁 {item['category']} | 📎 {item['file_name']}
                        </span>
                    </div>
                    <div>{status_badge(item['status'])}</div>
                </div>
                <p style="color: #636E72; margin-top: 12px; font-size: 13px;">
                    📅 {item['date']}
                </p>
            </div>
            """, unsafe_allow_html=True)


# ========================================
# 관리자 페이지
# ========================================
def admin_page():
    show_header("🔐 관리자 페이지", "자료 승인 및 사용자 권한 관리")
    
    if not is_admin():
        st.error("❌ 이 페이지에 접근할 권한이 없습니다.")
        return
    
    tab1, tab2 = st.tabs(["📋 자료 신청 관리", "👥 사용자 권한 관리"])
    
    with tab1:
        show_info_box(
            "📊 신청 관리",
            f"총 {len(st.session_state.suggestions)}건의 신청 중 "
            f"{len([x for x in st.session_state.suggestions if x['status'] == '승인대기'])}건이 대기 중입니다."
        )
        
        if not st.session_state.suggestions:
            st.info("신청 자료가 없습니다.")
        else:
            pending_count = len([x for x in st.session_state.suggestions if x['status'] == '승인대기'])
            
            if pending_count > 0:
                st.warning(f"⚠️ 대기 중인 신청: {pending_count}건")
            
            for i, item in enumerate(st.session_state.suggestions):
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between;">
                        <div style="flex: 1;">
                            <b style="font-size: 18px; color: #2D3436;">{item['title']}</b><br>
                            <span style="color: #636E72; font-size: 14px;">
                                신청자: {item['user_name']} ({item['user']}) | 
                                분류: {item['category']} | 
                                파일: {item['file_name']}
                            </span><br>
                            <p style="margin-top: 8px; color: #636E72;">{item['content']}</p>
                        </div>
                        <div>{status_badge(item['status'])}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("✅ 승인완료", key=f"approve_{i}", use_container_width=True):
                        st.session_state.suggestions[i]["status"] = "승인완료"
                        st.success("승인 완료!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ 반려", key=f"reject_{i}", use_container_width=True):
                        st.session_state.suggestions[i]["status"] = "반려"
                        st.warning("반려 처리되었습니다.")
                        st.rerun()
                
                with col3:
                    if st.button("⏸️ 보류", key=f"hold_{i}", use_container_width=True):
                        st.session_state.suggestions[i]["status"] = "보류"
                        st.info("보류 처리되었습니다.")
                        st.rerun()
                
                with col4:
                    if st.button("⚪ 대기", key=f"pending_{i}", use_container_width=True):
                        st.session_state.suggestions[i]["status"] = "승인대기"
                        st.rerun()
    
    with tab2:
        if is_superadmin():
            show_info_box(
                "👥 권한 관리",
                f"총 {len(st.session_state.users)}명의 사용자 권한을 관리합니다."
            )
            
            st.markdown("### 사용자 목록")
            
            for user_id, info in st.session_state.users.items():
                col1, col2, col3 = st.columns([2, 1.5, 1.5])
                
                with col1:
                    st.markdown(f"**{user_id}** ({info.get('name', '사용자')})")
                
                with col2:
                    st.markdown(f"{role_name(info['role'])}")
                
                with col3:
                    if user_id == "qhtjd0611":
                        st.markdown("🔒 고정", unsafe_allow_html=True)
                    elif info["role"] == "user":
                        if st.button("👔 관리자 부여", key=f"make_admin_{user_id}", use_container_width=True):
                            st.session_state.users[user_id]["role"] = "admin"
                            st.success("관리자 권한 부여 완료!")
                            st.rerun()
                    elif info["role"] == "admin":
                        if st.button("👤 일반사용자 변경", key=f"make_user_{user_id}", use_container_width=True):
                            st.session_state.users[user_id]["role"] = "user"
                            st.warning("권한이 변경되었습니다.")
                            st.rerun()
                
                st.divider()
        else:
            st.error("❌ 권한 관리는 최고관리자만 이용할 수 있습니다.")


# ========================================
# 메인 실행
# ========================================
if st.session_state.login_user is None:
    login_page()
else:
    # 상단 정보바
    with st.container():
        top_bar()
    
    st.markdown("---")
    
    # 네비게이션 메뉴
    menu_list = ["🏠 홈", "📚 법령·조례·매뉴얼", "💬 건의·신청"]
    
    if is_admin():
        menu_list.append("🔐 관리자")
    
    selected_menu = st.sidebar.radio(
        "메뉴",
        menu_list,
        index=0
    )
    
    # 페이지 라우팅
    if selected_menu == "🏠 홈":
        home_page()
    elif selected_menu == "📚 법령·조례·매뉴얼":
        law_page()
    elif selected_menu == "💬 건의·신청":
        suggestion_page()
    elif selected_menu == "🔐 관리자":
        admin_page()
    
    # 하단 정보
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #636E72; font-size: 13px; padding: 20px 0;">
        <p>🚒 <b>충남119 복무AI</b> v1.0</p>
        <p>충남소방본부 | 최종 업데이트: {datetime.now().strftime('%Y년 %m월 %d일')}</p>
        <p>개인정보보호방침 | 이용약관 | 문의: 119</p>
    </div>
    """, unsafe_allow_html=True)
