import streamlit as st
from datetime import datetime
import hashlib

st.set_page_config(
    page_title="충남119 복무AI",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# 🔐 보안: 비밀번호 해싱 함수
# ========================================
def hash_password(password: str) -> str:
    """비밀번호를 안전하게 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()


# ========================================
# 세션 상태 초기화
# ========================================
if "users" not in st.session_state:
    # 프로덕션: 실제 운영 시 데이터베이스 사용 필수
    st.session_state.users = {
        "admin001": {
            "password_hash": hash_password("119"),
            "role": "admin",
            "name": "관리자",
            "created_at": "2024-01-01"
        }
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
# 🎨 소방청 공식 색상
# ========================================
FIRE_ORANGE = "#FF8833"      # 소방청 주 색상
LIGHT_ORANGE = "#FFB84D"     # 밝은 오렌지
NAVY = "#1A3A52"             # 신뢰감 있는 네이비
DARK_NAVY = "#0F1B2E"        # 진한 네이비
LIGHT_BG = "#F5F7FA"         # 밝은 배경
WHITE = "#FFFFFF"            # 흰색
TEXT_DARK = "#2D3436"        # 진한 텍스트
TEXT_MUTED = "#636E72"       # 회색 텍스트
SUCCESS = "#27AE60"          # 초록
WARNING = "#E8A707"          # 황금색
DANGER = "#E74C3C"           # 빨강

# ========================================
# 🎨 CSS 스타일 (소방청 공식)
# ========================================
st.markdown(f"""
<style>
    * {{
        font-family: 'Segoe UI', 'Roboto', '본고딕', '나눔고딕', sans-serif;
    }}

    .stApp {{
        background: linear-gradient(135deg, {LIGHT_BG} 0%, #E8EEF5 100%);
    }}

    /* ===== 네비게이션 사이드바 ===== */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {DARK_NAVY} 0%, {NAVY} 100%);
        box-shadow: 2px 0 12px rgba(15, 27, 46, 0.3);
    }}

    section[data-testid="stSidebar"] * {{
        color: {WHITE} !important;
    }}

    section[data-testid="stSidebar"] .stRadio > label {{
        color: {WHITE} !important;
        font-weight: 700;
        padding: 14px 12px;
        border-radius: 8px;
        transition: all 0.3s ease;
        margin-bottom: 4px;
    }}

    section[data-testid="stSidebar"] .stRadio > label:hover {{
        background-color: rgba(255, 136, 51, 0.2);
        border-left: 4px solid {FIRE_ORANGE};
    }}

    section[data-testid="stSidebar"] .stRadio > label[aria-selected="true"] {{
        background-color: rgba(255, 136, 51, 0.3);
        border-left: 4px solid {FIRE_ORANGE};
    }}

    /* ===== 헤더 배너 ===== */
    .header-banner {{
        background: linear-gradient(135deg, {FIRE_ORANGE} 0%, #FF7722 100%);
        color: {WHITE};
        padding: 40px 42px;
        border-radius: 14px;
        margin-bottom: 32px;
        box-shadow: 0 12px 32px rgba(255, 136, 51, 0.25);
        border-left: 8px solid {LIGHT_ORANGE};
        position: relative;
        overflow: hidden;
    }}

    .header-banner::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 50%;
    }}

    .header-title {{
        font-size: 48px;
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.8px;
        display: flex;
        align-items: center;
        gap: 16px;
        position: relative;
        z-index: 1;
    }}

    .header-subtitle {{
        font-size: 16px;
        opacity: 0.95;
        margin-top: 10px;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }}

    /* ===== 카드 ===== */
    .card {{
        background: {WHITE};
        border: 1px solid #E8EBED;
        border-radius: 12px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(15, 27, 46, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .card:hover {{
        box-shadow: 0 12px 32px rgba(255, 136, 51, 0.15);
        transform: translateY(-4px);
        border-color: {FIRE_ORANGE};
    }}

    .card-title {{
        color: {FIRE_ORANGE};
        font-size: 22px;
        font-weight: 900;
        margin-bottom: 16px;
        border-bottom: 3px solid {FIRE_ORANGE};
        padding-bottom: 12px;
    }}

    /* ===== 정보박스 ===== */
    .info-box {{
        background: linear-gradient(135deg, rgba(255, 136, 51, 0.05) 0%, rgba(255, 184, 77, 0.05) 100%);
        border-left: 6px solid {FIRE_ORANGE};
        border-radius: 10px;
        padding: 22px 26px;
        margin-bottom: 28px;
        box-shadow: 0 4px 14px rgba(255, 136, 51, 0.1);
    }}

    .info-box b {{
        color: {FIRE_ORANGE};
        font-size: 16px;
    }}

    /* ===== 경고박스 ===== */
    .warning-box {{
        background: linear-gradient(135deg, rgba(232, 167, 7, 0.05) 0%, rgba(255, 193, 7, 0.05) 100%);
        border-left: 6px solid {WARNING};
        border-radius: 10px;
        padding: 22px 26px;
        margin-bottom: 28px;
        color: {TEXT_DARK};
    }}

    .success-box {{
        background: linear-gradient(135deg, rgba(39, 174, 96, 0.05) 0%, rgba(46, 204, 113, 0.05) 100%);
        border-left: 6px solid {SUCCESS};
        border-radius: 10px;
        padding: 22px 26px;
        margin-bottom: 28px;
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
        border-color: {FIRE_ORANGE} !important;
        box-shadow: 0 0 0 3px rgba(255, 136, 51, 0.15) !important;
    }}

    div[data-testid="stTextArea"] textarea {{
        border-radius: 10px !important;
        border: 2px solid #E8EBED !important;
        font-family: inherit;
        transition: all 0.3s ease;
    }}

    div[data-testid="stTextArea"] textarea:focus {{
        border-color: {FIRE_ORANGE} !important;
        box-shadow: 0 0 0 3px rgba(255, 136, 51, 0.15) !important;
    }}

    /* ===== 버튼 ===== */
    .stButton > button {{
        width: 100%;
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, {FIRE_ORANGE} 0%, #FF7722 100%);
        color: {WHITE};
        padding: 14px 24px;
        font-weight: 800;
        font-size: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 16px rgba(255, 136, 51, 0.2);
    }}

    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 28px rgba(255, 136, 51, 0.3);
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
        color: {FIRE_ORANGE};
        border-bottom-color: {FIRE_ORANGE};
    }}

    /* ===== 상태 배지 ===== */
    .status-badge {{
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        white-space: nowrap;
    }}

    .status-pending {{
        background: rgba(232, 167, 7, 0.2);
        color: #E8A707;
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
        border: 2px solid {FIRE_ORANGE};
        border-radius: 20px;
        padding: 10px 20px;
        margin: 8px 8px 8px 0;
        font-weight: 700;
        color: {FIRE_ORANGE};
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(255, 136, 51, 0.1);
    }}

    .faq-pill:hover {{
        background: {FIRE_ORANGE};
        color: {WHITE};
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255, 136, 51, 0.25);
    }}

    /* ===== 사용자 정보 배지 ===== */
    .user-badge {{
        background: linear-gradient(135deg, {FIRE_ORANGE} 0%, {LIGHT_ORANGE} 100%);
        border-left: 4px solid {WHITE};
        padding: 16px 20px;
        border-radius: 10px;
        font-weight: 700;
        color: {WHITE};
        box-shadow: 0 4px 16px rgba(255, 136, 51, 0.2);
    }}

    /* ===== 테이블 ===== */
    .stDataFrame {{
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(45, 52, 54, 0.08) !important;
    }}

    /* ===== 구분선 ===== */
    .divider {{
        border: none;
        border-top: 2px solid #E8EBED;
        margin: 32px 0;
    }}

    /* ===== 반응형 ===== */
    @media (max-width: 768px) {{
        .header-title {{
            font-size: 32px;
        }}
        .header-subtitle {{
            font-size: 14px;
        }}
    }}

    /* ===== 푸터 ===== */
    .footer {{
        text-align: center;
        color: {TEXT_MUTED};
        font-size: 13px;
        padding: 28px 20px;
        border-top: 2px solid #E8EBED;
        margin-top: 40px;
    }}
</style>
""", unsafe_allow_html=True)

# ========================================
# 공통 함수
# ========================================
def show_header(title: str, subtitle: str = ""):
    """소방청 스타일 헤더"""
    st.markdown(f"""
    <div class="header-banner">
        <div class="header-title">🚒 {title}</div>
        <div class="header-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def show_info_box(title: str, content: str):
    """정보 박스"""
    st.markdown(f"""
    <div class="info-box">
        <b>ℹ️ {title}</b><br>
        {content}
    </div>
    """, unsafe_allow_html=True)


def show_warning_box(title: str, content: str):
    """경고 박스"""
    st.markdown(f"""
    <div class="warning-box">
        <b>⚠️ {title}</b><br>
        {content}
    </div>
    """, unsafe_allow_html=True)


def get_role():
    """현재 사용자 역할"""
    user = st.session_state.login_user
    return st.session_state.users[user]["role"]


def is_admin():
    """관리자 권한 확인"""
    return get_role() == "admin"


def role_name(role):
    """역할 한글명"""
    roles = {"admin": "👔 관리자", "user": "👤 일반사용자"}
    return roles.get(role, "사용자")


def status_badge(status):
    """상태 배지"""
    badges = {
        "승인대기": '<span class="status-badge status-pending">🟡 승인대기</span>',
        "승인완료": '<span class="status-badge status-approved">🟢 승인완료</span>',
        "반려": '<span class="status-badge status-rejected">🔴 반려</span>',
        "보류": '<span class="status-badge status-hold">🔵 보류</span>'
    }
    return badges.get(status, status)


def classify_question(q: str):
    """질문 자동 분류"""
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
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, {FIRE_ORANGE} 0%, {LIGHT_ORANGE} 100%); border-radius: 12px; color: white;">
            <div style="font-size: 48px;">🦅</div>
            <div style="font-weight: 700; font-size: 14px; margin-top: 8px;">소방청</div>
        </div>
        """, unsafe_allow_html=True)
    
    show_info_box(
        "안전한 접속",
        "충남119 복무AI에 오신 것을 환영합니다. 안전한 인증 시스템으로 보호된 서비스입니다."
    )
    
    tab1, tab2 = st.tabs(["🔑 로그인", "📝 회원가입"])
    
    with tab1:
        st.markdown("### 로그인")
        user_id = st.text_input("아이디", key="login_id", placeholder="아이디 입력")
        password = st.text_input("비밀번호", type="password", key="login_pw", placeholder="비밀번호 입력")
        
        if st.button("로그인", use_container_width=True, key="btn_login"):
            if not user_id or not password:
                st.error("❌ 아이디와 비밀번호를 입력하세요.")
            elif user_id in st.session_state.users:
                stored_hash = st.session_state.users[user_id]["password_hash"]
                input_hash = hash_password(password)
                
                if stored_hash == input_hash:
                    st.session_state.login_user = user_id
                    st.success("✅ 로그인 성공!")
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 일치하지 않습니다.")
            else:
                st.error("❌ 존재하지 않는 아이디입니다.")
    
    with tab2:
        st.markdown("### 회원가입")
        new_id = st.text_input("새 아이디", key="new_id", placeholder="6자 이상의 아이디")
        new_pw = st.text_input("새 비밀번호", type="password", key="new_pw", placeholder="6자 이상의 비밀번호")
        new_name = st.text_input("이름", key="new_name", placeholder="실명 입력")
        
        if st.button("회원가입", use_container_width=True, key="btn_signup"):
            if not new_id or not new_pw or not new_name:
                st.warning("⚠️ 모든 항목을 입력하세요.")
            elif len(new_id) < 6:
                st.warning("⚠️ 아이디는 6자 이상이어야 합니다.")
            elif len(new_pw) < 6:
                st.warning("⚠️ 비밀번호는 6자 이상이어야 합니다.")
            elif new_id in st.session_state.users:
                st.error("❌ 이미 사용 중인 아이디입니다.")
            else:
                st.session_state.users[new_id] = {
                    "password_hash": hash_password(new_pw),
                    "role": "user",
                    "name": new_name,
                    "created_at": datetime.now().strftime("%Y-%m-%d")
                }
                st.success("✅ 회원가입이 완료되었습니다. 로그인해주세요.")


# ========================================
# 상단 정보 바
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
    show_header("복무·행정 안내", "업무 중 필요한 정보를 AI가 제공해드립니다")
    
    show_info_box(
        "119 복무AI 소개",
        "복무규정, 병가, 공가, 초과근무, 각종 시스템 사용 방법 등 일상 업무 중 궁금한 사항을 "
        "편하게 물어보세요. AI가 정확한 정보와 관련 법령을 안내해드립니다."
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
        
        st.markdown("""
        <div class="card">
            <div class="card-title">✅ 답변</div>
            <p><strong>분류:</strong> {}</p>
            <p style="color: #636E72; font-size: 14px; line-height: 1.6;">
                🔄 현재 <strong>Gemini API 연동 작업 중</strong>입니다.<br>
                다음 업데이트에서 실시간 AI 답변이 제공될 예정입니다.
            </p>
        </div>
        """.format(category), unsafe_allow_html=True)
        
        st.markdown("### 📚 근거 법령")
        st.markdown("""
        <div class="card">
            <ul style="margin: 0; padding-left: 24px;">
                <li><strong>공무원 복무규정</strong> - 국가공무원의 기본 복무 기준</li>
                <li><strong>지방공무원 복무규정</strong> - 지방공무원 구체 사항</li>
                <li><strong>충청남도 공무원 복무 조례</strong> - 충남의 세부 규정</li>
            </ul>
            <p style="color: #636E72; font-size: 13px; margin-top: 16px;">
                💾 모든 답변은 최신 공식 법령을 기반으로 제공됩니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
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
        st.info("📝 아직 질문이 없습니다. 첫 번째 질문을 시작해보세요!")


# ========================================
# 법령·조례 페이지
# ========================================
def law_page():
    show_header("📚 법령·조례·매뉴얼", "공식 참고 자료 목록")
    
    show_info_box(
        "자료 안내",
        "현재 시스템이 참고하는 공식 법령, 조례, 매뉴얼을 확인하실 수 있습니다. "
        "각 자료는 최신 버전으로 유지 관리됩니다."
    )
    
    st.markdown("### 등록된 자료")
    
    data = {
        "구분": ["법령", "법령", "조례", "매뉴얼", "매뉴얼", "매뉴얼"],
        "자료명": [
            "공무원 복무규정",
            "지방공무원 복무규정",
            "충청남도 공무원 복무 조례",
            "e사람 시스템 매뉴얼",
            "온나라 시스템 매뉴얼",
            "e호조 시스템 매뉴얼"
        ],
        "상태": ["📋 준비중", "📋 준비중", "📋 준비중", "📋 준비중", "📋 준비중", "📋 준비중"]
    }
    
    st.dataframe(data, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.info(
        "📅 **갱신 일정**\n\n"
        "• **법령**: 매년 4월, 10월 갱신\n"
        "• **조례**: 공포 즉시 업로드\n"
        "• **매뉴얼**: 시스템 변경 시 즉시 반영"
    )


# ========================================
# 건의사항 페이지
# ========================================
def suggestion_page():
    show_header("💬 건의·신청", "필요한 자료를 신청해주세요")
    
    show_info_box(
        "건의사항 안내",
        "누락된 법령, 조례, 매뉴얼, 업무자료를 신청하실 수 있습니다. "
        "신청하신 자료는 관리자가 검토하여 처리합니다."
    )
    
    with st.form("suggestion_form", clear_on_submit=True):
        st.markdown("### 자료 신청")
        
        title = st.text_input("자료 제목", placeholder="신청할 자료의 제목")
        category = st.selectbox(
            "자료 종류",
            ["법령", "조례", "지침", "매뉴얼", "감사사례", "기타"]
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
        st.info("아직 신청한 자료가 없습니다.")
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
    show_header("🔐 관리자", "자료 신청 관리")
    
    if not is_admin():
        st.error("❌ 이 페이지에 접근할 권한이 없습니다.")
        return
    
    show_info_box(
        "신청 관리",
        f"총 {len(st.session_state.suggestions)}건 중 "
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
                            신청자: {item['user_name']} | 
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
                if st.button("✅ 승인", key=f"approve_{i}", use_container_width=True):
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


# ========================================
# 메인 실행
# ========================================
if st.session_state.login_user is None:
    login_page()
else:
    # 상단 정보 바
    with st.container():
        top_bar()
    
    st.markdown("---")
    
    # 메뉴
    menu_list = ["🏠 홈", "📚 법령·조례·매뉴얼", "💬 건의·신청"]
    
    if is_admin():
        menu_list.append("🔐 관리자")
    
    selected_menu = st.sidebar.radio("메뉴", menu_list, index=0)
    
    # 페이지 라우팅
    if selected_menu == "🏠 홈":
        home_page()
    elif selected_menu == "📚 법령·조례·매뉴얼":
        law_page()
    elif selected_menu == "💬 건의·신청":
        suggestion_page()
    elif selected_menu == "🔐 관리자":
        admin_page()
    
    # 하단 푸터
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        <p>🚒 <b>충남119 복무AI</b> v2.0 | 소방청 공식 스타일</p>
        <p>충남소방본부 | 최종 업데이트: {datetime.now().strftime('%Y년 %m월 %d일')}</p>
        <p>
            <a href="#" style="color: {FIRE_ORANGE}; text-decoration: none;">개인정보보호방침</a> | 
            <a href="#" style="color: {FIRE_ORANGE}; text-decoration: none;">이용약관</a> | 
            <a href="#" style="color: {FIRE_ORANGE}; text-decoration: none;">문의</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
