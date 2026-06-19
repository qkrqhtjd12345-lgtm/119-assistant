import streamlit as st
from datetime import datetime
from collections import Counter
import hashlib
import hmac
import html
import json
import os
import re
from urllib.parse import urlparse
try:
    import pandas as pd
except Exception:
    pd = None
# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(
    page_title="충남119 복무AI",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded",
)APP_NAME = "충남119 복무AI"
APP_VERSION = "v5.1 안정화본"
DATA_FILE = "data_store.json"
PRIMARY = "#1F6F78"
PRIMARY_DARK = "#14545C"
ACCENT = "#F28C6B"
LIGHT_BG = "#F7F8F5"
WHITE = "#FFFFFF"
TEXT_DARK = "#263238"
TEXT_GRAY = "#667085"
BORDER = "#D9E0E3"
DANGER = "#B42318"
WARNING = "#B54708"
SUCCESS = "#027A48"
RESOURCE_CATEGORIES = ["법령", "조례", "규칙", "훈령", "예규", "지침", "매뉴얼", "감사사례", "기타"]
RESOURCE_SCOPES = ["Private", "User", "Public", "Admin", "Prohibited"]
SCOPE_LABELS = {
    "Public": "공개",
    "User": "로그인 사용자",
    "Admin": "관리자 전용",
    "Private": "비공개",
    "Prohibited": "등록 금지",
}CATEGORY_KEYWORDS = {
    "연가": ["연가", "연차", "휴가", "휴가일수"],
    "병가": ["병가", "진단서", "병원", "공상", "질병", "부상"],
    "공가": ["공가", "예비군", "민방위", "건강검진", "투표"],
    "출장": ["출장", "여비", "관외", "교육출장", "출장비"],
    "초과근무": ["초과", "시간외", "야근", "휴일근무", "대체휴무", "수당"],
    "당직": ["당직", "숙직", "일직", "비번", "주주야야"],
    "예산": ["예산", "품의", "지출", "계약", "집행", "구매", "물품"],
    "복무": ["복무", "근무상황", "지각", "조퇴", "외출", "근무", "결재"],
    "인사": ["인사", "전보", "승진", "평정", "성과", "호봉"],
    "교육": ["교육", "훈련", "사이버교육", "상시학습", "강의"],
    "온나라": ["온나라", "문서", "공문", "기안", "결재"],
    "e사람": ["e사람", "인사랑", "급여", "수당", "복지"],
    "법령": ["법령", "법", "시행령", "시행규칙", "규정"],
    "조례": ["조례", "규칙", "훈령", "예규"],
}BLOCK_PATTERNS = [
    (r"\b\d{6}\s*[-]?\s*\d{7}\b", "주민등록번호로 보이는 정보"),
    (r"\b01[016789][-\s]?\d{3,4}[-\s]?\d{4}\b", "휴대전화번호로 보이는 정보"),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "이메일 주소로 보이는 정보"),
    (r"\b\d{2,4}[-\s]?\d{3,4}[-\s]?\d{4}\b", "전화번호로 보이는 정보"),
    (r"대외비|비공개|보안자료|비밀|수사자료|민감정보|개인정보", "보안·비공개·개인정보 관련 표현"),
]# ============================================================
# 공통 유틸
# ============================================================
def safe_text(value):
    return html.escape(str(value), quote=True)
def now_str(fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.now().strftime(fmt)
def get_secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default
def hash_password(password, salt=None):
    """비밀번호 저장용 PBKDF2 해시. 실서비스에서는 bcrypt/argon2도 가능."""
    if salt is None:
        salt = os.urandom(16)
    iterations = 260000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(iterations, salt.hex(), digest.hex())
def verify_password(password, stored_hash):
    try:
        algorithm, iterations, salt_hex, hash_hex = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        expected = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations)).hex()
        return hmac.compare_digest(expected, hash_hex)
    except Exception:
        return False
def valid_url(url):
    try:
        parsed = urlparse((url or "").strip())
        return parsed.scheme in ["http", "https"] and bool(parsed.netloc)
    except Exception:
        return False
def detect_block_reason(text):
    text = text or ""
    for pattern, reason in BLOCK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return reason
    return None
def classify_question(question):
    q = (question or "").lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in q:
                return category
    return "기타"
def make_question_title(question):
    cleaned = " ".join((question or "").split())
    if not cleaned:
        return "제목 없음"
    if len(cleaned) <= 36:
        return cleaned
    return cleaned[:36] + "..."
def safe_user_id(user_id):
    if not re.match(r"^[A-Za-z0-9_\-]{6,24}$", user_id or ""):
        return False
    if detect_block_reason(user_id):
        return False
    return True
def scope_label(scope):
    return SCOPE_LABELS.get(scope, scope)
def create_user(password, role="user", name=None):
    return {
        "password_hash": hash_password(password),
        "role": role,
        "name": name or "사용자",
        "created_at": now_str(),
        "terms_accepted": False,
        "terms_accepted_at": "",
        "is_active": True,
    }
def default_data():
    default_admin_id = get_secret("ADMIN_ID", "admin119")
    default_admin_pw = get_secret("ADMIN_PASSWORD", "admin1234!")
    data = {
        "users": {
            default_admin_id: create_user(default_admin_pw, role="admin", name="최고관리자")
        },
        "resources": [],
        "suggestions": [],
        "question_logs": [],
        "admin_requests": [],
        "audit_logs": [],
        "using_default_admin": default_admin_pw == "admin1234!",
    }
    data["users"][default_admin_id]["terms_accepted"] = True
    data["users"][default_admin_id]["terms_accepted_at"] = now_str()
    return data
def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        base = default_data()
        for key in base:
            if key not in loaded:
                loaded[key] = base[key]
        return loaded
    except Exception:
        return default_data()
def save_data():
    data = {
        "users": st.session_state.users,
        "resources": st.session_state.resources,
        "suggestions": st.session_state.suggestions,
        "question_logs": st.session_state.question_logs,
        "admin_requests": st.session_state.admin_requests,
        "audit_logs": st.session_state.audit_logs,
        "using_default_admin": st.session_state.using_default_admin,
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
def init_state():
    if "_loaded" not in st.session_state:
        data = load_data()
        st.session_state.users = data.get("users", {})
        st.session_state.resources = data.get("resources", [])
        st.session_state.suggestions = data.get("suggestions", [])
        st.session_state.question_logs = data.get("question_logs", [])
        st.session_state.admin_requests = data.get("admin_requests", [])
        st.session_state.audit_logs = data.get("audit_logs", [])
        st.session_state.using_default_admin = data.get("using_default_admin", False)
        st.session_state.login_user = None
        st.session_state.menu = "홈"
        st.session_state._loaded = True
init_state()
def current_user_id():
    return st.session_state.get("login_user")
def current_user():
    uid = current_user_id()
    if not uid:
        return None
    return st.session_state.users.get(uid)
def get_role():
    user = current_user()
    if not user:
        return "guest"
    return user.get("role", "guest")
def is_admin():
    return get_role() == "admin"
def add_audit(action, target="", detail=""):
    st.session_state.audit_logs.append({
        "일시": now_str(),
        "수행자": current_user_id() or "system",
        "기능": action,
        "대상": target,
        "세부내용": detail,
    })
    save_data()
def can_view_resource(resource):
    scope = resource.get("공개범위", "Private")
    if scope == "Public":
        return True
    if scope == "User":
        return current_user_id() is not None
    if scope == "Admin":
        return is_admin()
    return False
def to_dataframe(rows):
    if pd is None:
        return rows
    return pd.DataFrame(rows)
def counter_to_rows(counter, name_col="분야", count_col="건수"):
    return [{name_col: key, count_col: count} for key, count in counter.most_common()]
# ============================================================
# CSS
# ============================================================
CSS = """
<style>
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Noto Sans KR', sans-serif;
    }
    .stApp {
        background-color: __LIGHT_BG__;
        color: __TEXT_DARK__;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, __PRIMARY__ 0%, __PRIMARY_DARK__ 100%);
        min-width: 390px !important;
        width: 390px !important;
        overflow-x: hidden !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 390px !important;
        overflow-x: hidden !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    section[data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 0px !important;
        height: 0px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] {
        width: 100% !important;
    }
    section[data-testid="stSidebar"] label[data-baseweb="radio"] {
        width: 100% !important;
        padding: 13px 16px !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        background: rgba(255,255,255,0.10) !important;
    }
    section[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
        background: rgba(255,255,255,0.18) !important;
    }
    div[data-testid="collapsedControl"] {
        z-index: 999999 !important;
        left: 10px !important;
        top: 10px !important;
    }
    div[data-testid="collapsedControl"] button,
    button[kind="header"] {
        width: 56px !important;
        height: 56px !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.18) !important;
        background: __WHITE__ !important;
    }
    .hero {
        background: linear-gradient(135deg, #E6F4F1 0%, #FFFFFF 100%);
        border: 1px solid __BORDER__;
        border-radius: 22px;
        padding: 28px 30px;
        margin-bottom: 18px;
        box-shadow: 0 2px 12px rgba(16,24,40,0.05);
    }
    .hero-title {
        font-size: 31px;
        font-weight: 900;
        color: __TEXT_DARK__;
        margin-bottom: 8px;
    }
    .hero-sub {
        font-size: 16px;
        color: __TEXT_GRAY__;
        line-height: 1.6;
    }
    .card {
        background: __WHITE__;
        border: 1px solid __BORDER__;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 10px rgba(16,24,40,0.04);
    }
    .card-title {
        font-size: 18px;
        font-weight: 900;
        color: __TEXT_DARK__;
        margin-bottom: 8px;
    }
    .muted {
        color: __TEXT_GRAY__;
        font-size: 13px;
        line-height: 1.55;
    }
    .notice {
        border-radius: 14px;
        padding: 14px 16px;
        margin: 12px 0;
        line-height: 1.6;
        font-size: 14px;
    }
    .notice.warning {
        background: #FFF7ED;
        border: 1px solid #FED7AA;
        color: #7C2D12;
    }
    .notice.info {
        background: #EFF8FF;
        border: 1px solid #B2DDFF;
        color: #184E77;
    }
    .notice.danger {
        background: #FEF3F2;
        border: 1px solid #FECDCA;
        color: #7A271A;
    }
    .question-wrap {
        max-width: 920px;
        margin: 0 auto;
    }
    div[data-testid="stTextArea"] textarea {
        min-height: 210px !important;
        border-radius: 18px !important;
        border: 2px solid #B9D7D9 !important;
        font-size: 18px !important;
        line-height: 1.6 !important;
        padding: 20px !important;
        background: #FFFFFF !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: __PRIMARY__ !important;
        box-shadow: 0 0 0 4px rgba(31,111,120,0.12) !important;
    }
    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 800 !important;
        border: 1px solid __BORDER__ !important;
    }
    .question-wrap div.stButton > button {
        background: __ACCENT__ !important;
        color: white !important;
        border: 0 !important;
        height: 54px !important;
        font-size: 17px !important;
    }
    .question-wrap div.stButton > button:hover {
        background: #E17957 !important;
        color: white !important;
    }
    .sidebar-box {
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.20);
        padding: 13px;
        border-radius: 15px;
        margin: 12px 0;
    }
</style>
"""
CSS = (
    CSS.replace("__LIGHT_BG__", LIGHT_BG)
    .replace("__TEXT_DARK__", TEXT_DARK)
    .replace("__TEXT_GRAY__", TEXT_GRAY)
    .replace("__PRIMARY__", PRIMARY)
    .replace("__PRIMARY_DARK__", PRIMARY_DARK)
    .replace("__WHITE__", WHITE)
    .replace("__BORDER__", BORDER)
    .replace("__ACCENT__", ACCENT)
)st.markdown(CSS, unsafe_allow_html=True)
# ============================================================
# 공통 표시
# ============================================================
def render_ai_disclaimer():
    st.markdown(
        """
        <div class="notice warning">
            ⚠ 본 답변은 업무 참고용 AI 정보입니다. 등록 자료 및 AI 답변의 정확성, 완전성, 최신성 또는 특정 업무처리의 적법성을 보증하지 않습니다.<br>
            본 서비스는 공식 유권해석, 행정처분, 법률자문 또는 인사결정을 대신하지 않습니다. 최종 판단 및 업무처리 책임은 사용자와 소속 기관에 있습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
def render_terms_text():
    st.markdown(
        """
        <div class="notice danger">
            <b>⚠ 이용 전 필수 확인사항</b><br><br>
            1. 본 서비스는 소방 업무 참고를 돕기 위한 비공식 AI 보조 도구이며, 공식 유권해석·법률자문·행정처분·인사결정·감사 판단을 대신하지 않습니다.<br>
            2. 운영자 및 관리자는 AI 답변, 등록 자료, 외부 출처 자료의 정확성·완전성·최신성·적법성·저작권 상태를 보증하지 않습니다.<br>
            3. 사용자는 주민등록번호, 전화번호, 주소, 건강정보, 징계·수사자료, 대외비, 비공개 문서 등 개인정보·민감정보·보안자료를 입력해서는 안 됩니다.<br>
            4. 질문 내용은 AI 응답 생성을 위해 외부 AI 서비스로 전달될 수 있으며, 민감정보 입력으로 발생하는 책임은 입력자에게 있습니다.<br>
            5. 자료 등록 요청은 자료명·발행기관·공식 출처 URL·요청 사유만 제출할 수 있고, 일반 사용자는 원본 파일을 업로드할 수 없습니다.<br>
            6. 관리자는 자료의 법적 정확성이나 최신성을 검토하는 사람이 아니라, 공식 출처 존재 여부와 공개 가능 여부만 제한적으로 확인합니다.<br>
            7. 최종 업무처리, 결재, 복무 판단, 법령 적용, 보고서 제출 책임은 사용자와 소속 기관에 있습니다.<br>
            8. 위 내용에 동의하지 않는 경우 회원가입 및 서비스 이용이 제한됩니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
def page_header(title, subtitle=""):
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">{}</div>
            <div class="hero-sub">{}</div>
        </div>
        """.format(safe_text(title), safe_text(subtitle)),
        unsafe_allow_html=True,
    )
# ============================================================
# 로그인 / 회원가입
# ============================================================
def login_page():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown(
            """
            <div class="hero" style="text-align:center;">
                <div style="font-size:52px;">🚒</div>
                <div class="hero-title">{}</div>
                <div class="hero-sub">
                    현장과 행정을 연결하는 업무 참고 시스템<br>
                    복무·법령·조례·행정자료를 더 빠르게 찾기 위한 AI 보조 도구
                </div>
            </div>
            """.format(APP_NAME),
            unsafe_allow_html=True,
        )
        if st.session_state.get("using_default_admin"):
            st.warning("배포 전 Streamlit secrets에 ADMIN_ID, ADMIN_PASSWORD를 반드시 설정하세요. 현재 기본 테스트 관리자 비밀번호가 적용됩니다.")
        tab_login, tab_signup = st.tabs(["로그인", "회원가입"])
        with tab_login:
            login_id = st.text_input("아이디", key="login_id")
            login_pw = st.text_input("비밀번호", type="password", key="login_pw")
            if st.button("로그인", use_container_width=True):
                user = st.session_state.users.get(login_id)
                if not login_id or not login_pw:
                    st.error("아이디와 비밀번호를 입력하세요.")
                elif not user:
                    st.error("존재하지 않는 아이디입니다.")
                elif not user.get("is_active", True):
                    st.error("비활성화되었거나 삭제된 계정입니다.")
                elif not verify_password(login_pw, user.get("password_hash", "")):
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.session_state.login_user = login_id
                    add_audit("로그인", login_id)
                    st.rerun()
        with tab_signup:
            st.info("아이디에는 실명, 사번, 전화번호, 이메일 등 개인을 식별할 수 있는 정보를 넣지 마세요.")
            sid = st.text_input("새 아이디", key="signup_id", placeholder="영문/숫자/_/- 조합 6~24자")
            spw = st.text_input("새 비밀번호", type="password", key="signup_pw", placeholder="8자 이상 권장")
            spw2 = st.text_input("비밀번호 확인", type="password", key="signup_pw2")
            render_terms_text()
            agree_1 = st.checkbox("개인정보·민감정보·보안자료를 입력하지 않겠습니다.", key="signup_agree_1")
            agree_2 = st.checkbox("본 서비스가 공식 판단이 아닌 업무 참고용 AI 보조 도구임을 확인했습니다.", key="signup_agree_2")
            agree_3 = st.checkbox("운영자와 관리자가 AI 답변 및 등록 자료의 정확성·최신성·적법성을 보증하지 않음을 확인했습니다.", key="signup_agree_3")
            agree_4 = st.checkbox("최종 업무처리 책임은 사용자와 소속 기관에 있음을 확인했습니다.", key="signup_agree_4")
            agree_radio = st.radio("위 내용에 동의하십니까?", ["동의", "비동의"], horizontal=True, key="signup_agree_radio")
            if st.button("회원가입", use_container_width=True):
                if agree_radio != "동의":
                    st.error("비동의 시 회원가입 및 서비스 이용이 불가합니다.")
                elif not all([agree_1, agree_2, agree_3, agree_4]):
                    st.error("필수 확인사항을 모두 체크해야 회원가입할 수 있습니다.")
                elif not sid or not spw or not spw2:
                    st.warning("모든 항목을 입력하세요.")
                elif not safe_user_id(sid):
                    st.error("아이디는 영문/숫자/_/- 6~24자로 만들고, 개인정보로 보이는 값은 사용할 수 없습니다.")
                elif len(spw) < 8:
                    st.warning("비밀번호는 8자 이상으로 설정하세요.")
                elif spw != spw2:
                    st.error("비밀번호 확인이 일치하지 않습니다.")
                elif sid in st.session_state.users:
                    st.error("이미 사용 중인 아이디입니다.")
                else:
                    st.session_state.users[sid] = create_user(spw, role="user", name=sid)
                    st.session_state.users[sid]["terms_accepted"] = True
                    st.session_state.users[sid]["terms_accepted_at"] = now_str()
                    save_data()
                    add_audit("회원가입", sid, "동의 완료")
                    st.success("회원가입이 완료되었습니다. 로그인하세요.")
def terms_gate_page():
    st.markdown("### 최초 이용 동의")
    render_terms_text()
    agree_1 = st.checkbox("개인정보·민감정보·보안자료 입력 금지를 확인했습니다.")
    agree_2 = st.checkbox("본 서비스가 업무 참고용 AI 보조 도구임을 확인했습니다.")
    agree_3 = st.checkbox("AI 답변과 등록 자료의 정확성·최신성·적법성이 보장되지 않음을 확인했습니다.")
    agree_4 = st.checkbox("최종 판단 및 업무처리 책임은 사용자와 소속 기관에 있음을 확인했습니다.")
    choice = st.radio("동의 여부", ["동의", "비동의"], horizontal=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("동의 후 이용", use_container_width=True):
            if choice != "동의" or not all([agree_1, agree_2, agree_3, agree_4]):
                st.error("모든 항목에 동의해야 이용할 수 있습니다.")
            else:
                uid = current_user_id()
                st.session_state.users[uid]["terms_accepted"] = True
                st.session_state.users[uid]["terms_accepted_at"] = now_str()
                save_data()
                add_audit("이용약관 동의", uid)
                st.rerun()
    with col2:
        if st.button("비동의 및 로그아웃", use_container_width=True):
            add_audit("이용약관 비동의 로그아웃", current_user_id())
            st.session_state.login_user = None
            st.rerun()
# ============================================================
# 사이드바 / 페이지
# ============================================================
def sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style="font-size:28px;font-weight:900;margin-bottom:4px;">🚒 {}</div>
            <div style="font-size:13px;opacity:.85;margin-bottom:14px;">{} · 업무 참고용</div>
            <div class="sidebar-box">
                <b>운영 원칙</b><br>
                <span style="font-size:13px;line-height:1.6;">
                파일 업로드 금지 · 공식 출처 확인 · 최종 판단은 소속 기관 기준
                </span>
            </div>
            <div class="sidebar-box">
                <b>현재 사용자</b><br>{}<br>
                <span style="font-size:12px;opacity:.85;">권한: {}</span>
            </div>
            """.format(APP_NAME, APP_VERSION, safe_text(current_user_id()), safe_text(get_role())),
            unsafe_allow_html=True,
        )
        menus = ["홈", "질문하기", "법령·조례 자료", "자료 등록 요청"]
        if is_admin():
            menus.append("관리자")
        current_menu = st.session_state.get("menu", "홈")
        if current_menu not in menus:
            current_menu = "홈"
        st.session_state.menu = st.radio("메뉴", menus, index=menus.index(current_menu))
        st.markdown("---")
        st.markdown(
            """
            <div class="sidebar-box">
                <b>관리자 권한신청</b><br>
                <span style="font-size:12px;">업무상 필요 시 신청하세요.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("관리자 권한 신청", use_container_width=True):
            uid = current_user_id()
            exists = any(req.get("아이디") == uid and req.get("상태") == "신청대기" for req in st.session_state.admin_requests)
            if is_admin():
                st.info("이미 관리자 권한입니다.")
            elif exists:
                st.info("이미 신청대기 중입니다.")
            else:
                st.session_state.admin_requests.append({
                    "신청일시": now_str(),
                    "아이디": uid,
                    "상태": "신청대기",
                    "처리일시": "",
                    "처리자": "",
                })
                save_data()
                add_audit("관리자 권한 신청", uid)
                st.success("관리자 권한 신청이 접수되었습니다.")
        if st.button("로그아웃", use_container_width=True):
            add_audit("로그아웃", current_user_id())
            st.session_state.login_user = None
            st.rerun()
def home_page():
    page_header(
        "현장과 행정을 연결하는 복무 참고 시스템",
        "질문 내용은 홈 화면에 노출하지 않고, 질문 분야 통계만 표시합니다. 개인정보·민감정보는 입력하지 마세요.",
    )
    total_users = len([u for u in st.session_state.users.values() if u.get("is_active", True)])
    total_questions = len(st.session_state.question_logs)
    total_resources = len(st.session_state.resources)
    pending_suggestions = len([s for s in st.session_state.suggestions if s.get("상태") == "출처확인대기"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("가입자 수", total_users)
    c2.metric("누적 질문", total_questions)
    c3.metric("등록 자료", total_resources)
    c4.metric("자료 요청 대기", pending_suggestions)
    category_counts = Counter(log.get("분야", "기타") for log in st.session_state.question_logs if log.get("상태") == "정상")
    top5 = category_counts.most_common(5)
    st.markdown("### 질문 분야 TOP 5")
    if not top5:
        st.info("아직 질문 통계가 없습니다. 질문 내용은 홈에 표시하지 않습니다.")
    else:
        cols = st.columns(len(top5))
        for idx, (category, count) in enumerate(top5):
            with cols[idx]:
                st.markdown(
                    """
                    <div class="card" style="text-align:center;">
                        <div style="font-size:22px;font-weight:900;color:{};">{}</div>
                        <div class="card-title">{}</div>
                        <div class="muted">{}건</div>
                    </div>
                    """.format(PRIMARY, idx + 1, safe_text(category), count),
                    unsafe_allow_html=True,
                )
    st.markdown("### 이용 안내")
    st.markdown(
        """
        <div class="notice info">
            질문은 업무 참고용으로만 사용하세요. 주민등록번호, 전화번호, 주소, 건강정보, 징계·수사자료, 비공개 문서 등은 입력하지 마세요.<br>
            복무·법령·조례 판단은 최종적으로 소속 기관, 담당 부서, 공식 법령·조례·예규를 확인해야 합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
def ask_page():
    page_header("질문하기", "질문창을 크게 배치했습니다. 질문은 관리자 화면에 아이디·일시·분야·소제목과 함께 기록됩니다.")
    st.markdown('<div class="question-wrap">', unsafe_allow_html=True)
    question = st.text_area(
        "업무 관련 질문을 입력하세요",
        placeholder="예: 15시에 병가를 사용했는데 주간/야간 중 어떻게 올려야 하나요?\n※ 개인정보·민감정보·보안자료는 입력하지 마세요.",
        key="question_input",
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        ask_clicked = st.button("질문하기", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if ask_clicked:
        if not question.strip():
            st.warning("질문을 입력하세요.")
            return
        block_reason = detect_block_reason(question)
        category = classify_question(question)
        title = make_question_title(question)
        if block_reason:
            st.session_state.question_logs.append({
                "일시": now_str(),
                "아이디": current_user_id(),
                "분야": category,
                "소제목": "자동차단된 질문",
                "질문": "저장 안 함",
                "상태": "자동차단",
                "차단사유": block_reason,
            })
            save_data()
            add_audit("질문 자동차단", current_user_id(), block_reason)
            st.error("질문에 {}가 포함된 것으로 감지되어 처리하지 않았습니다. 해당 정보를 제거하고 다시 질문하세요.".format(block_reason))
            return
        st.session_state.question_logs.append({
            "일시": now_str(),
            "아이디": current_user_id(),
            "분야": category,
            "소제목": title,
            "질문": question.strip(),
            "상태": "정상",
            "차단사유": "",
        })
        save_data()
        add_audit("질문 등록", current_user_id(), "{} / {}".format(category, title))
        st.markdown("### AI 답변 영역")
        st.info("현재 버전은 화면·권한·기록 구조를 잡은 안정화본입니다. 실제 Gemini/OpenAI API 연동은 이 위치에 연결하면 됩니다.")
        st.markdown("**분류된 질문 분야:** {}".format(safe_text(category)))
        render_ai_disclaimer()
def resources_page():
    page_header("법령·조례 자료", "자료명, 발행기관, 공식 출처 URL, 등록일, 최종 확인일을 함께 표시합니다.")
    visible = [r for r in st.session_state.resources if can_view_resource(r)]
    if not visible:
        st.info("현재 열람 가능한 등록 자료가 없습니다.")
        return
    for idx, r in enumerate(visible, start=1):
        st.markdown(
            """
            <div class="card">
                <div class="card-title">{}. {}</div>
                <div class="muted">
                    분야: {} · 발행기관: {}<br>
                    등록일: {} · 최종 확인일: {} · 공개범위: {}<br>
                    출처 URL: {}
                </div>
            </div>
            """.format(
                idx,
                safe_text(r.get("자료명", "")),
                safe_text(r.get("분야", "")),
                safe_text(r.get("발행기관", "")),
                safe_text(r.get("등록일", "")),
                safe_text(r.get("최종확인일", "")),
                safe_text(scope_label(r.get("공개범위", "Private"))),
                safe_text(r.get("출처URL", "")),
            ),
            unsafe_allow_html=True,
        )
def suggestion_page():
    page_header("자료 등록 요청", "일반 사용자는 원본 파일을 업로드할 수 없습니다. 자료명·발행기관·공식 출처 URL·요청 사유만 제출하세요.")
    st.markdown(
        """
        <div class="notice warning">
            본 서비스는 자료 등록 요청 기능만 제공합니다. 관리자는 자료의 내용, 정확성, 적법성, 최신성 또는 저작권 상태를 보증하지 않습니다.<br>
            관리자는 공식 출처 존재 여부와 공개 가능 여부만 제한적으로 확인합니다. 자료 등록 요청 및 이용에 따른 책임은 해당 자료의 제출자와 이용자에게 있습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("suggestion_form"):
        category = st.selectbox("자료 분야", RESOURCE_CATEGORIES)
        name = st.text_input("자료명")
        publisher = st.text_input("발행기관")
        source_url = st.text_input("공식 출처 URL", placeholder="https://...")
        reason = st.text_area("등록 요청 사유", placeholder="왜 필요한 자료인지 간단히 작성하세요. 개인정보·민감정보는 입력하지 마세요.")
        submitted = st.form_submit_button("자료 등록 요청")
    if submitted:
        combined = "{}\n{}\n{}\n{}".format(name, publisher, source_url, reason)
        block_reason = detect_block_reason(combined)
        if not name or not publisher or not source_url or not reason:
            st.warning("모든 항목을 입력하세요.")
        elif not valid_url(source_url):
            st.error("공식 출처 URL 형식이 올바르지 않습니다.")
        elif block_reason:
            st.session_state.suggestions.append({
                "요청일시": now_str(),
                "요청자": current_user_id(),
                "분야": category,
                "자료명": name,
                "발행기관": publisher,
                "출처URL": source_url,
                "요청사유": "저장 제한",
                "상태": "자동차단",
                "차단사유": block_reason,
            })
            save_data()
            add_audit("자료 요청 자동차단", current_user_id(), block_reason)
            st.error("{}가 포함된 것으로 감지되어 관리자 검토 없이 차단했습니다.".format(block_reason))
        else:
            st.session_state.suggestions.append({
                "요청일시": now_str(),
                "요청자": current_user_id(),
                "분야": category,
                "자료명": name,
                "발행기관": publisher,
                "출처URL": source_url,
                "요청사유": reason,
                "상태": "출처확인대기",
                "차단사유": "",
            })
            save_data()
            add_audit("자료 등록 요청", current_user_id(), name)
            st.success("자료 등록 요청이 접수되었습니다. 관리자는 공식 출처 존재 여부와 공개 가능 여부만 확인합니다.")
# ============================================================
# 관리자 기능
# ============================================================
def admin_dashboard_tab():
    st.markdown("### 관리자 통계")
    active_users = [uid for uid, u in st.session_state.users.items() if u.get("is_active", True)]
    normal_questions = [q for q in st.session_state.question_logs if q.get("상태") == "정상"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("가입자 수", len(active_users))
    c2.metric("질문 수", len(st.session_state.question_logs))
    c3.metric("정상 질문", len(normal_questions))
    c4.metric("자동차단", len([q for q in st.session_state.question_logs if q.get("상태") == "자동차단"]))
    category_counts = Counter(q.get("분야", "기타") for q in normal_questions)
    title_counts = Counter(q.get("소제목", "제목 없음") for q in normal_questions)
    left, right = st.columns(2)
    with left:
        st.markdown("#### 질문 분야 비율")
        if category_counts:
            rows = counter_to_rows(category_counts, "분야", "건수")
            df = to_dataframe(rows)
            if pd is not None:
                st.bar_chart(df.set_index("분야"))
                st.dataframe(df, use_container_width=True)
            else:
                st.write(rows)
        else:
            st.info("질문 통계가 없습니다.")
    with right:
        st.markdown("#### 비슷한 질문 소제목 TOP")
        if title_counts:
            rows2 = counter_to_rows(title_counts, "소제목", "건수")
            df2 = to_dataframe(rows2)
            if pd is not None:
                st.bar_chart(df2.set_index("소제목"))
                st.dataframe(df2, use_container_width=True)
            else:
                st.write(rows2)
        else:
            st.info("소제목 통계가 없습니다.")
def admin_questions_tab():
    st.markdown("### 질문 이력 관리")
    st.caption("관리자만 질문자 아이디, 질문 소제목, 질문 내용, 일자 및 시간을 볼 수 있습니다. 개인정보·민감정보가 감지된 질문은 원문을 저장하지 않습니다.")
    if not st.session_state.question_logs:
        st.info("질문 이력이 없습니다.")
        return
    df = to_dataframe(st.session_state.question_logs)
    if pd is not None:
        st.dataframe(df, use_container_width=True)
    else:
        st.write(df)
    with st.expander("질문 이력 삭제"):
        st.warning("삭제하면 현재 저장소의 질문 이력이 사라집니다. 실제 운영에서는 감사로그와 보존 정책을 별도로 두세요.")
        if st.button("전체 질문 이력 삭제"):
            st.session_state.question_logs = []
            save_data()
            add_audit("질문 이력 전체 삭제")
            st.success("질문 이력을 삭제했습니다.")
            st.rerun()
def admin_suggestions_tab():
    st.markdown("### 자료 등록 요청 관리")
    st.info("관리자는 자료의 정확성·최신성·법적 적법성을 보증하지 않고, 공식 출처 존재 여부와 공개 가능 여부만 확인합니다.")
    if not st.session_state.suggestions:
        st.info("자료 등록 요청이 없습니다.")
        return
    blocked = [s for s in st.session_state.suggestions if s.get("상태") == "자동차단"]
    if blocked:
        with st.expander("자동차단 요청 {}건".format(len(blocked))):
            df_blocked = to_dataframe(blocked)
            if pd is not None:
                st.dataframe(df_blocked, use_container_width=True)
            else:
                st.write(df_blocked)
    for i, item in enumerate(st.session_state.suggestions):
        if item.get("상태") != "출처확인대기":
            continue
        with st.expander("{} / {} / {}".format(item.get("자료명"), item.get("요청자"), item.get("요청일시"))):
            st.write("분야: {}".format(item.get("분야")))
            st.write("발행기관: {}".format(item.get("발행기관")))
            st.write("출처 URL: {}".format(item.get("출처URL")))
            st.write("요청 사유: {}".format(item.get("요청사유")))
            c1, c2, c3 = st.columns(3)
            with c1:
                official = st.checkbox("공식 출처 존재 확인", key="official_{}".format(i))
            with c2:
                public_ok = st.checkbox("공개 가능 자료 확인", key="public_{}".format(i))
            with c3:
                not_secret = st.checkbox("보안자료 아님 확인", key="secret_{}".format(i))
            scope = st.selectbox("공개범위", RESOURCE_SCOPES, index=0, format_func=scope_label, key="scope_{}".format(i))
            reviewer_note = st.text_input("관리자 메모", key="memo_{}".format(i))
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("승인", key="approve_{}".format(i)):
                    if not all([official, public_ok, not_secret]):
                        st.error("세 가지 확인사항을 모두 체크해야 승인할 수 있습니다.")
                    else:
                        st.session_state.resources.append({
                            "자료명": item.get("자료명"),
                            "분야": item.get("분야"),
                            "발행기관": item.get("발행기관"),
                            "출처URL": item.get("출처URL"),
                            "등록일": now_str("%Y-%m-%d"),
                            "최종확인일": now_str("%Y-%m-%d"),
                            "공개범위": scope,
                            "등록자": current_user_id(),
                            "관리자메모": reviewer_note,
                        })
                        st.session_state.suggestions[i]["상태"] = "승인완료"
                        st.session_state.suggestions[i]["처리일시"] = now_str()
                        st.session_state.suggestions[i]["처리자"] = current_user_id()
                        save_data()
                        add_audit("자료 요청 승인", item.get("자료명"), "scope={}".format(scope))
                        st.success("승인 및 자료 등록 완료")
                        st.rerun()
            with b2:
                if st.button("반려", key="reject_{}".format(i)):
                    st.session_state.suggestions[i]["상태"] = "반려"
                    st.session_state.suggestions[i]["처리일시"] = now_str()
                    st.session_state.suggestions[i]["처리자"] = current_user_id()
                    save_data()
                    add_audit("자료 요청 반려", item.get("자료명"))
                    st.rerun()
            with b3:
                if st.button("등록 금지", key="prohibit_{}".format(i)):
                    st.session_state.suggestions[i]["상태"] = "등록금지"
                    st.session_state.suggestions[i]["처리일시"] = now_str()
                    st.session_state.suggestions[i]["처리자"] = current_user_id()
                    save_data()
                    add_audit("자료 요청 등록금지", item.get("자료명"))
                    st.rerun()
def admin_resource_register_tab():
    st.markdown("### 관리자 직접 자료 등록")
    st.caption("자료 기본값은 비공개입니다. 공개범위를 명시적으로 바꿔야 사용자에게 보입니다.")
    with st.form("admin_resource_form"):
        category = st.selectbox("분야", RESOURCE_CATEGORIES, key="admin_res_category")
        name = st.text_input("자료명", key="admin_res_name")
        publisher = st.text_input("발행기관", key="admin_res_publisher")
        url = st.text_input("공식 출처 URL", key="admin_res_url")
        scope = st.selectbox("공개범위", RESOURCE_SCOPES, index=0, format_func=scope_label, key="admin_res_scope")
        last_checked = st.date_input("최종 확인일", key="admin_res_last_checked")
        memo = st.text_area("관리자 메모", key="admin_res_memo")
        submitted = st.form_submit_button("자료 등록")
    if submitted:
        combined = "{}\n{}\n{}\n{}".format(name, publisher, url, memo)
        block_reason = detect_block_reason(combined)
        if not name or not publisher or not url:
            st.warning("자료명, 발행기관, 출처 URL을 입력하세요.")
        elif not valid_url(url):
            st.error("URL 형식이 올바르지 않습니다.")
        elif block_reason:
            st.error("{}가 포함된 것으로 감지되어 등록할 수 없습니다.".format(block_reason))
            add_audit("관리자 자료 등록 차단", name, block_reason)
        else:
            st.session_state.resources.append({
                "자료명": name,
                "분야": category,
                "발행기관": publisher,
                "출처URL": url,
                "등록일": now_str("%Y-%m-%d"),
                "최종확인일": str(last_checked),
                "공개범위": scope,
                "등록자": current_user_id(),
                "관리자메모": memo,
            })
            save_data()
            add_audit("관리자 직접 자료 등록", name, "scope={}".format(scope))
            st.success("자료가 등록되었습니다.")
    st.markdown("#### 등록 자료 목록")
    if st.session_state.resources:
        df = to_dataframe(st.session_state.resources)
        if pd is not None:
            st.dataframe(df, use_container_width=True)
        else:
            st.write(df)
    else:
        st.info("등록 자료가 없습니다.")
def admin_users_tab():
    st.markdown("### 회원·권한 관리")
    st.markdown("#### 관리자 권한 신청")
    if st.session_state.admin_requests:
        df_req = to_dataframe(st.session_state.admin_requests)
        if pd is not None:
            st.dataframe(df_req, use_container_width=True)
        else:
            st.write(df_req)
        pending_ids = [r.get("아이디") for r in st.session_state.admin_requests if r.get("상태") == "신청대기"]
        if pending_ids:
            selected_req = st.selectbox("처리할 신청자", pending_ids)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("관리자 승인"):
                    st.session_state.users[selected_req]["role"] = "admin"
                    for r in st.session_state.admin_requests:
                        if r.get("아이디") == selected_req and r.get("상태") == "신청대기":
                            r["상태"] = "승인"
                            r["처리일시"] = now_str()
                            r["처리자"] = current_user_id()
                    save_data()
                    add_audit("관리자 권한 승인", selected_req)
                    st.success("관리자 권한을 부여했습니다.")
                    st.rerun()
            with c2:
                if st.button("관리자 신청 반려"):
                    for r in st.session_state.admin_requests:
                        if r.get("아이디") == selected_req and r.get("상태") == "신청대기":
                            r["상태"] = "반려"
                            r["처리일시"] = now_str()
                            r["처리자"] = current_user_id()
                    save_data()
                    add_audit("관리자 권한 반려", selected_req)
                    st.rerun()
    else:
        st.info("관리자 권한 신청이 없습니다.")
    st.markdown("#### 가입자 목록")
    rows = []
    for uid, user in st.session_state.users.items():
        rows.append({
            "아이디": uid,
            "권한": user.get("role"),
            "가입일시": user.get("created_at"),
            "동의일시": user.get("terms_accepted_at"),
            "활성": user.get("is_active", True),
        })
    df_users = to_dataframe(rows)
    if pd is not None:
        st.dataframe(df_users, use_container_width=True)
    else:
        st.write(df_users)
    st.markdown("#### 가입자 아이디 삭제")
    deletable_ids = [uid for uid in st.session_state.users.keys() if uid != current_user_id()]
    if not deletable_ids:
        st.info("삭제 가능한 사용자가 없습니다. 자기 자신은 삭제할 수 없습니다.")
        return
    target = st.selectbox("삭제할 아이디", deletable_ids)
    confirm = st.text_input("삭제 확인을 위해 아이디를 그대로 입력하세요", key="delete_confirm")
    hard_delete = st.checkbox("완전 삭제하기", value=False, help="체크하지 않으면 비활성화 처리합니다. 실제 운영에서는 비활성화를 권장합니다.")
    if st.button("선택 아이디 삭제/비활성화"):
        active_admins = [uid for uid, u in st.session_state.users.items() if u.get("role") == "admin" and u.get("is_active", True)]
        if confirm != target:
            st.error("확인 아이디가 일치하지 않습니다.")
        elif st.session_state.users[target].get("role") == "admin" and len(active_admins) <= 1:
            st.error("마지막 관리자 계정은 삭제할 수 없습니다.")
        else:
            if hard_delete:
                del st.session_state.users[target]
                action = "가입자 완전 삭제"
            else:
                st.session_state.users[target]["is_active"] = False
                action = "가입자 비활성화"
            save_data()
            add_audit(action, target)
            st.success("{} 처리 완료".format(target))
            st.rerun()
def admin_audit_tab():
    st.markdown("### 관리자 감사로그")
    if not st.session_state.audit_logs:
        st.info("감사로그가 없습니다.")
    else:
        df_logs = to_dataframe(st.session_state.audit_logs)
        if pd is not None:
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.write(df_logs)
def admin_page():
    if not is_admin():
        st.error("관리자만 접근할 수 있습니다.")
        st.stop()
    page_header("관리자", "질문 이력, 가입자, 자료 요청, 공개범위, 감사로그를 관리합니다.")
    tabs = st.tabs(["통계", "질문 이력", "자료 요청", "자료 직접 등록", "회원·권한", "감사로그"])
    with tabs[0]:
        admin_dashboard_tab()
    with tabs[1]:
        admin_questions_tab()
    with tabs[2]:
        admin_suggestions_tab()
    with tabs[3]:
        admin_resource_register_tab()
    with tabs[4]:
        admin_users_tab()
    with tabs[5]:
        admin_audit_tab()
# ============================================================
# 실행
# ============================================================
def main():
    if not current_user_id():
        login_page()
        return
    user = current_user()
    if not user or not user.get("is_active", True):
        st.session_state.login_user = None
        st.error("계정이 비활성화되었거나 삭제되었습니다.")
        return
    if not user.get("terms_accepted", False):
        terms_gate_page()
        return
    sidebar()
    menu = st.session_state.get("menu", "홈")
    if menu == "홈":
        home_page()
    elif menu == "질문하기":
        ask_page()
    elif menu == "법령·조례 자료":
        resources_page()
    elif menu == "자료 등록 요청":
        suggestion_page()
    elif menu == "관리자":
        admin_page()
    else:
        home_page()
if __name__ == "__main__":
    main()
