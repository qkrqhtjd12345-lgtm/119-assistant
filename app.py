
import streamlit as st
from datetime import datetime
from collections import Counter
from urllib.parse import urlparse
import base64
import hashlib
import hmac
import html
import json
import os
import re
import secrets
import time

try:
    import pandas as pd
except Exception:
    pd = None

# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(
    page_title="충남119행정비서",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "충남119행정비서"
APP_VERSION = "v6.0"
DATA_FILE = "data_store.json"
AUTO_LOGOUT_SECONDS = 10 * 60

# 업로드된 소방 상징 이미지 Base64 내장
LOGO_B64 = "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"
DEFAULT_ADMIN_ID = "qhtjd0611"
DEFAULT_ADMIN_PASSWORD_HASH = "pbkdf2_sha256$260000$11911911911911911911911911911911$b8bd3fe75cec000358b1b69964f55cb1bee81ba23bbc103c83fac3e7a26915a7"

# 색상: 네이비 중심 + 포인트 오렌지
PRIMARY = "#23364A"
PRIMARY_DARK = "#162536"
PRIMARY_SOFT = "#31465E"
ACCENT = "#F28C6B"
ACCENT_DARK = "#D97350"
LIGHT_BG = "#F5F6F8"
WHITE = "#FFFFFF"
TEXT_DARK = "#263238"
TEXT_GRAY = "#667085"
BORDER = "#D8DEE6"
DANGER = "#B42318"
SUCCESS = "#027A48"
WARNING = "#B54708"
INFO = "#184E77"

RESOURCE_CATEGORIES = ["법령", "조례", "규칙", "훈령", "예규", "지침", "매뉴얼", "감사사례", "기타"]
RESOURCE_SCOPES = ["Private", "User", "Public", "Admin", "Prohibited"]
SCOPE_LABELS = {
    "Public": "공개",
    "User": "로그인 사용자",
    "Admin": "관리자 전용",
    "Private": "비공개",
    "Prohibited": "등록 금지",
}

QUESTION_CATEGORIES = [
    "복무", "연가", "병가", "공가", "출장", "초과근무", "당직", "예산", "계약", "교육", "인사", "온나라", "e사람", "법령", "조례", "기타"
]

CATEGORY_KEYWORDS = {
    "연가": ["연가", "연차", "휴가", "휴가일수"],
    "병가": ["병가", "진단서", "병원", "공상", "질병", "부상"],
    "공가": ["공가", "예비군", "민방위", "건강검진", "투표"],
    "출장": ["출장", "여비", "관외", "교육출장", "출장비"],
    "초과근무": ["초과", "시간외", "야근", "휴일근무", "대체휴무", "수당"],
    "당직": ["당직", "숙직", "일직", "비번", "주주야야", "야간"],
    "예산": ["예산", "품의", "지출", "집행", "구매", "물품", "회계"],
    "계약": ["계약", "입찰", "수의계약", "견적", "나라장터"],
    "교육": ["교육", "훈련", "사이버교육", "상시학습", "강의"],
    "인사": ["인사", "전보", "승진", "평정", "성과", "호봉", "전입"],
    "온나라": ["온나라", "문서", "공문", "기안", "결재"],
    "e사람": ["e사람", "인사랑", "급여", "수당", "복지"],
    "법령": ["법령", "법", "시행령", "시행규칙", "규정"],
    "조례": ["조례", "규칙", "훈령", "예규"],
    "복무": ["복무", "근무상황", "지각", "조퇴", "외출", "근무", "결재"],
}

BLOCK_PATTERNS = [
    (r"\b\d{6}\s*[-]?\s*\d{7}\b", "주민등록번호로 보이는 정보"),
    (r"\b01[016789][-\s]?\d{3,4}[-\s]?\d{4}\b", "휴대전화번호로 보이는 정보"),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "이메일 주소로 보이는 정보"),
    (r"\b\d{2,4}[-\s]?\d{3,4}[-\s]?\d{4}\b", "전화번호로 보이는 정보"),
    (r"대외비|비공개|보안자료|비밀|수사자료|민감정보|개인정보|주민등록|징계자료", "보안·비공개·개인정보 관련 표현"),
]

# ============================================================
# 저장소
# ============================================================
def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def now_display():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def h(value):
    return html.escape(str(value), quote=True)


def get_secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.environ.get(name, default)


def new_id(prefix="id"):
    return f"{prefix}_{int(time.time() * 1000)}_{secrets.token_hex(4)}"


def default_store():
    return {
        "users": {},
        "questions": [],
        "resources": [],
        "suggestions": [],
        "admin_requests": [],
        "audit_logs": [],
    }


def load_store():
    if not os.path.exists(DATA_FILE):
        return default_store()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = default_store()
        for key in base:
            data.setdefault(key, base[key])
        return data
    except Exception:
        return default_store()


def save_store():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.store, f, ensure_ascii=False, indent=2)


def init_session():
    if "store" not in st.session_state:
        st.session_state.store = load_store()
    if "login_user" not in st.session_state:
        st.session_state.login_user = None
    if "login_at" not in st.session_state:
        st.session_state.login_at = None
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = time.time()
    if "menu" not in st.session_state:
        st.session_state.menu = "홈"
    if "session_nonce" not in st.session_state:
        st.session_state.session_nonce = secrets.token_hex(8)


def ensure_admin():
    admin_id = get_secret("ADMIN_ID", DEFAULT_ADMIN_ID)
    admin_hash = get_secret("ADMIN_PASSWORD_HASH", DEFAULT_ADMIN_PASSWORD_HASH)
    users = st.session_state.store["users"]
    if admin_id not in users:
        users[admin_id] = {
            "user_id": admin_id,
            "password_hash": admin_hash,
            "role": "admin",
            "created_at": now_iso(),
            "terms_accepted": True,
            "terms_accepted_at": now_iso(),
            "is_active": True,
            "force_logout_after": "",
            "last_login_at": "",
        }
        save_store()
    else:
        users[admin_id]["role"] = "admin"
        users[admin_id].setdefault("password_hash", admin_hash)
        users[admin_id].setdefault("force_logout_after", "")
        users[admin_id].setdefault("is_active", True)
        save_store()


init_session()
ensure_admin()

# ============================================================
# 인증 / 권한
# ============================================================
def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    iterations = 260000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password, stored_hash):
    try:
        algorithm, iterations, salt_hex, digest_hex = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        expected = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)).hex()
        return hmac.compare_digest(expected, digest_hex)
    except Exception:
        return False


def current_user_id():
    return st.session_state.login_user


def users():
    return st.session_state.store["users"]


def current_user():
    uid = current_user_id()
    if not uid:
        return None
    return users().get(uid)


def get_role(uid=None):
    if uid is None:
        user = current_user()
    else:
        user = users().get(uid)
    if not user:
        return "guest"
    return user.get("role", "user")


def is_admin(uid=None):
    return get_role(uid) == "admin"


def role_label(role):
    return "관리자" if role == "admin" else "일반사용자"


def logout(reason="로그아웃"):
    if current_user_id():
        add_audit(reason, current_user_id())
    st.session_state.login_user = None
    st.session_state.login_at = None
    st.session_state.last_activity = time.time()


def add_audit(action, target="", detail=""):
    st.session_state.store["audit_logs"].append({
        "일시": now_iso(),
        "수행자": current_user_id() or "system",
        "기능": action,
        "대상": target,
        "세부내용": detail,
    })
    save_store()


def safe_user_id(user_id):
    if not re.match(r"^[A-Za-z0-9_\-]{6,24}$", user_id or ""):
        return False
    if detect_block_reason(user_id):
        return False
    return True


def create_user(user_id, password, role="user"):
    users()[user_id] = {
        "user_id": user_id,
        "password_hash": hash_password(password),
        "role": role,
        "created_at": now_iso(),
        "terms_accepted": False,
        "terms_accepted_at": "",
        "is_active": True,
        "force_logout_after": "",
        "last_login_at": "",
    }
    save_store()


def parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def login_required_guard():
    if not current_user_id():
        return
    user = current_user()
    if not user or not user.get("is_active", True):
        logout("비활성 계정 자동 로그아웃")
        st.warning("계정이 비활성화되었거나 삭제되어 로그아웃되었습니다.")
        st.rerun()

    # 관리자가 강제 로그아웃한 경우
    force_dt = parse_iso(user.get("force_logout_after", ""))
    login_dt = parse_iso(st.session_state.login_at)
    if force_dt and login_dt and force_dt >= login_dt:
        logout("관리자 강제 로그아웃 적용")
        st.warning("관리자에 의해 로그아웃되었습니다.")
        st.rerun()

    # 서버 기준 10분 미사용 로그아웃
    elapsed = time.time() - st.session_state.last_activity
    if elapsed > AUTO_LOGOUT_SECONDS:
        logout("10분 미사용 자동 로그아웃")
        st.warning("10분 동안 사용이 없어 자동 로그아웃되었습니다.")
        st.rerun()


def mark_activity():
    if current_user_id():
        st.session_state.last_activity = time.time()


def inject_inactivity_timer():
    # 브라우저에서도 10분간 마우스/키보드/스크롤 입력이 없으면 새로고침하여 서버 로그아웃 검사 실행
    st.components.v1.html(
        f"""
        <script>
        (function() {{
          const LIMIT = {AUTO_LOGOUT_SECONDS * 1000};
          let timer = null;
          function resetTimer() {{
            if (timer) clearTimeout(timer);
            timer = setTimeout(function() {{ window.parent.location.reload(); }}, LIMIT);
          }}
          ['click','mousemove','keydown','scroll','touchstart'].forEach(function(evt) {{
            window.addEventListener(evt, resetTimer, true);
            window.parent.addEventListener(evt, resetTimer, true);
          }});
          resetTimer();
        }})();
        </script>
        """,
        height=0,
    )

# ============================================================
# 검사/분류
# ============================================================
def detect_block_reason(text):
    text = text or ""
    for pattern, reason in BLOCK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return reason
    return None


def valid_url(url):
    try:
        parsed = urlparse((url or "").strip())
        return parsed.scheme in ["http", "https"] and bool(parsed.netloc)
    except Exception:
        return False


def classify_question(question):
    q = (question or "").lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword.lower() in q for keyword in keywords):
            return category
    return "기타"


def make_question_title(question):
    cleaned = " ".join((question or "").split())
    if not cleaned:
        return "제목 없음"
    return cleaned[:34] + ("..." if len(cleaned) > 34 else "")


def can_view_resource(resource):
    scope = resource.get("공개범위", "Private")
    if scope == "Public":
        return True
    if scope == "User":
        return current_user_id() is not None
    if scope == "Admin":
        return is_admin()
    return False


def scope_label(scope):
    return SCOPE_LABELS.get(scope, scope)


def to_df(rows):
    if pd is None:
        return rows
    return pd.DataFrame(rows)

# ============================================================
# CSS / 화면 공통
# ============================================================
def apply_css():
    css = """
    <style>
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
    }
    .stApp {
        background: __LIGHT_BG__;
        color: __TEXT_DARK__;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, __PRIMARY__ 0%, __PRIMARY_DARK__ 100%);
        min-width: 330px !important;
        width: 330px !important;
        overflow-x: hidden !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 330px !important;
        overflow-x: hidden !important;
        padding: 20px 18px !important;
    }
    section[data-testid="stSidebar"]::-webkit-scrollbar,
    section[data-testid="stSidebar"] *::-webkit-scrollbar {
        width: 0px !important;
        height: 0px !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #FFFFFF;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
        gap: 8px;
    }
    section[data-testid="stSidebar"] label[data-baseweb="radio"] {
        width: 100% !important;
        min-height: 48px !important;
        padding: 12px 14px !important;
        margin-bottom: 6px !important;
        border-radius: 13px !important;
        background: rgba(255,255,255,0.10) !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
    }
    section[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
        background: rgba(255,255,255,0.20) !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        min-height: 48px !important;
        border-radius: 13px !important;
        border: 1px solid rgba(255,255,255,0.28) !important;
        font-weight: 900 !important;
        color: __PRIMARY_DARK__ !important;
        background: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #F4F7FA !important;
        color: __PRIMARY_DARK__ !important;
        border-color: rgba(255,255,255,0.55) !important;
    }
    div[data-testid="collapsedControl"] {
        z-index: 999999 !important;
        left: 12px !important;
        top: 12px !important;
    }
    div[data-testid="collapsedControl"] button,
    button[kind="header"] {
        width: 52px !important;
        height: 52px !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.20) !important;
        background: #FFFFFF !important;
    }

    .sidebar-logo-card {
        width: 100%;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 20px;
        padding: 18px 16px;
        text-align: center;
        margin-bottom: 14px;
    }
    .sidebar-logo-card img {
        width: 88px;
        height: auto;
        margin-bottom: 10px;
    }
    .sidebar-title {
        font-size: 23px;
        font-weight: 950;
        letter-spacing: -0.5px;
        color: #FFFFFF;
    }
    .sidebar-sub {
        font-size: 12px;
        opacity: 0.85;
        margin-top: 4px;
        color: #FFFFFF;
    }
    .sidebar-box {
        width: 100%;
        background: rgba(255,255,255,0.11);
        border: 1px solid rgba(255,255,255,0.20);
        border-radius: 16px;
        padding: 15px 14px;
        margin: 12px 0;
        box-sizing: border-box;
    }
    .sidebar-box .label {
        font-size: 12px;
        opacity: 0.82;
        margin-bottom: 5px;
    }
    .sidebar-box .value {
        font-size: 15px;
        font-weight: 850;
    }

    /* 카드/히어로 */
    .hero {
        background: linear-gradient(135deg, #FFFFFF 0%, #EDF1F5 100%);
        border: 1px solid __BORDER__;
        border-radius: 24px;
        padding: 26px 30px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(22,37,54,0.07);
    }
    .hero-flex {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
    }
    .hero-title {
        font-size: 32px;
        font-weight: 950;
        letter-spacing: -0.8px;
        color: __TEXT_DARK__;
        margin-bottom: 8px;
    }
    .hero-sub {
        font-size: 15px;
        line-height: 1.6;
        color: __TEXT_GRAY__;
    }
    .hero-logo {
        width: 92px;
        min-width: 92px;
        opacity: 0.96;
    }
    .card {
        background: #FFFFFF;
        border: 1px solid __BORDER__;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 3px 12px rgba(16,24,40,0.045);
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
        border-radius: 15px;
        padding: 14px 16px;
        margin: 12px 0;
        line-height: 1.65;
        font-size: 14px;
    }
    .notice.info { background:#EFF6FF; border:1px solid #BBD7FF; color:#173B68; }
    .notice.warning { background:#FFF7ED; border:1px solid #FED7AA; color:#7C2D12; }
    .notice.danger { background:#FEF3F2; border:1px solid #FECDCA; color:#7A271A; }
    .notice.success { background:#ECFDF3; border:1px solid #ABEFC6; color:#054F31; }
    .pill {
        display:inline-block;
        padding:5px 10px;
        border-radius:999px;
        background:#EEF2F6;
        color:__PRIMARY__;
        font-size:12px;
        font-weight:900;
    }
    .rank-card {
        text-align:center;
        min-height: 118px;
    }
    .rank-no {
        color: __ACCENT__;
        font-size: 24px;
        font-weight: 950;
    }
    .rank-name {
        font-size: 18px;
        font-weight: 950;
        color: __TEXT_DARK__;
        margin: 5px 0;
    }
    .rank-count {
        color: __TEXT_GRAY__;
        font-size: 13px;
    }
    .question-wrap {
        max-width: 960px;
        margin: 0 auto 18px auto;
    }
    div[data-testid="stTextArea"] textarea {
        min-height: 190px !important;
        border-radius: 18px !important;
        border: 2px solid #C9D3DD !important;
        font-size: 17px !important;
        line-height: 1.65 !important;
        padding: 18px !important;
        background: #FFFFFF !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: __PRIMARY__ !important;
        box-shadow: 0 0 0 4px rgba(35,54,74,0.13) !important;
    }
    div.stButton > button {
        border-radius: 13px !important;
        font-weight: 850 !important;
        border: 1px solid __BORDER__ !important;
        min-height: 42px !important;
    }
    .question-wrap div.stButton > button {
        background: __ACCENT__ !important;
        color: #FFFFFF !important;
        border: 0 !important;
        min-height: 54px !important;
        font-size: 17px !important;
    }
    .question-wrap div.stButton > button:hover {
        background: __ACCENT_DARK__ !important;
        color: #FFFFFF !important;
    }
    .topbar {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap: 12px;
        margin-bottom: 12px;
    }
    @media (max-width: 900px) {
        .hero-flex { flex-direction: column; align-items: flex-start; }
        .hero-title { font-size: 26px; }
        .hero-logo { width: 76px; }
    }
    </style>
    """
    for key, value in {
        "__LIGHT_BG__": LIGHT_BG,
        "__TEXT_DARK__": TEXT_DARK,
        "__TEXT_GRAY__": TEXT_GRAY,
        "__PRIMARY__": PRIMARY,
        "__PRIMARY_DARK__": PRIMARY_DARK,
        "__ACCENT__": ACCENT,
        "__ACCENT_DARK__": ACCENT_DARK,
        "__BORDER__": BORDER,
    }.items():
        css = css.replace(key, value)
    st.markdown(css, unsafe_allow_html=True)


def logo_data_uri():
    return f"data:image/webp;base64,{LOGO_B64}"


def page_header(title, subtitle="", show_logo=True):
    logo_html = f'<img class="hero-logo" src="{logo_data_uri()}" alt="소방 상징">' if show_logo else ""
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-flex">
            <div>
              <div class="hero-title">{h(title)}</div>
              <div class="hero-sub">{h(subtitle)}</div>
            </div>
            {logo_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def top_logout_area():
    c1, c2 = st.columns([7, 1.2])
    with c1:
        pass
    with c2:
        if st.button("로그아웃", key="top_logout", use_container_width=True):
            logout("화면 상단 로그아웃")
            st.rerun()


def render_terms_text():
    st.markdown(
        """
        <div class="notice danger">
            <b>⚠ 이용 전 필수 확인사항</b><br><br>
            1. 본 서비스는 소방 행정·복무 업무 참고를 돕는 비공식 AI 보조 도구이며, 공식 유권해석·법률자문·행정처분·인사결정·감사 판단을 대신하지 않습니다.<br>
            2. 운영자 및 관리자는 AI 답변, 등록 자료, 외부 출처 자료의 정확성·완전성·최신성·적법성·저작권 상태를 보증하지 않습니다.<br>
            3. 주민등록번호, 전화번호, 주소, 건강정보, 징계·수사자료, 대외비, 비공개 문서 등 개인정보·민감정보·보안자료를 입력해서는 안 됩니다.<br>
            4. 질문 내용은 AI 응답 생성을 위해 외부 AI 서비스로 전달될 수 있으므로, 민감정보 입력으로 발생하는 책임은 입력자에게 있습니다.<br>
            5. 일반 사용자는 원본 파일을 업로드할 수 없고, 자료명·발행기관·공식 출처 URL·등록 요청 사유만 제출할 수 있습니다.<br>
            6. 관리자는 자료의 법적 정확성이나 최신성을 검토·보증하는 사람이 아니라, 공식 출처 존재 여부와 공개 가능 여부만 제한적으로 확인합니다.<br>
            7. 최종 업무처리, 결재, 복무 판단, 법령 적용, 보고서 제출 책임은 사용자와 소속 기관에 있습니다.<br>
            8. 위 내용에 동의하지 않는 경우 회원가입 및 서비스 이용이 제한됩니다.
        </div>
        """,
        unsafe_allow_html=True,
    )


def ai_disclaimer():
    st.markdown(
        """
        <div class="notice warning">
            ⚠ 본 답변은 업무 참고용 AI 정보입니다. 등록 자료 및 AI 답변의 정확성, 완전성, 최신성 또는 특정 업무처리의 적법성을 보증하지 않습니다.<br>
            최종 판단 및 업무처리 책임은 사용자와 소속 기관에 있습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 로그인/회원가입
# ============================================================
def login_page():
    apply_css()
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown(
            f"""
            <div class="hero" style="text-align:center; padding-top:30px;">
                <img src="{logo_data_uri()}" alt="소방 상징" style="width:112px; height:auto; margin-bottom:12px;">
                <div class="hero-title">{APP_NAME}</div>
                <div class="hero-sub">
                    현장과 행정을 연결하는 소방 행정 보조 시스템<br>
                    복무·법령·조례·행정자료를 더 빠르게 찾기 위한 업무 참고용 AI
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        tab_login, tab_signup = st.tabs(["로그인", "회원가입"])

        with tab_login:
            uid = st.text_input("아이디", key="login_id")
            pw = st.text_input("비밀번호", type="password", key="login_pw")
            if st.button("로그인", use_container_width=True):
                user = users().get(uid)
                if not uid or not pw:
                    st.error("아이디와 비밀번호를 입력하세요.")
                elif not user:
                    st.error("존재하지 않는 아이디입니다.")
                elif not user.get("is_active", True):
                    st.error("비활성화되었거나 삭제된 계정입니다.")
                elif not verify_password(pw, user.get("password_hash", "")):
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.session_state.login_user = uid
                    st.session_state.login_at = now_iso()
                    st.session_state.last_activity = time.time()
                    user["last_login_at"] = now_iso()
                    save_store()
                    add_audit("로그인", uid)
                    st.rerun()

        with tab_signup:
            st.info("아이디에는 실명, 사번, 전화번호, 이메일 등 개인을 식별할 수 있는 정보를 넣지 마세요.")
            sid = st.text_input("새 아이디", key="signup_id", placeholder="영문/숫자/_/- 조합 6~24자")
            spw = st.text_input("새 비밀번호", type="password", key="signup_pw", placeholder="8자 이상 권장")
            spw2 = st.text_input("비밀번호 확인", type="password", key="signup_pw2")
            render_terms_text()
            agree1 = st.checkbox("개인정보·민감정보·보안자료를 입력하지 않겠습니다.", key="agree1")
            agree2 = st.checkbox("본 서비스가 공식 판단이 아닌 업무 참고용 AI 보조 도구임을 확인했습니다.", key="agree2")
            agree3 = st.checkbox("운영자와 관리자가 AI 답변 및 등록 자료의 정확성·최신성·적법성을 보증하지 않음을 확인했습니다.", key="agree3")
            agree4 = st.checkbox("최종 업무처리 책임은 사용자와 소속 기관에 있음을 확인했습니다.", key="agree4")
            choice = st.radio("위 내용에 동의하십니까?", ["동의", "비동의"], horizontal=True, key="signup_choice")

            if st.button("회원가입", use_container_width=True):
                if choice != "동의":
                    st.error("비동의 시 회원가입 및 서비스 이용이 불가합니다.")
                elif not all([agree1, agree2, agree3, agree4]):
                    st.error("필수 확인사항을 모두 체크해야 회원가입할 수 있습니다.")
                elif not sid or not spw or not spw2:
                    st.warning("모든 항목을 입력하세요.")
                elif not safe_user_id(sid):
                    st.error("아이디는 영문/숫자/_/- 6~24자로 만들고, 개인정보로 보이는 값은 사용할 수 없습니다.")
                elif len(spw) < 8:
                    st.warning("비밀번호는 8자 이상으로 설정하세요.")
                elif spw != spw2:
                    st.error("비밀번호 확인이 일치하지 않습니다.")
                elif sid in users():
                    st.error("이미 사용 중인 아이디입니다.")
                else:
                    create_user(sid, spw, role="user")
                    users()[sid]["terms_accepted"] = True
                    users()[sid]["terms_accepted_at"] = now_iso()
                    save_store()
                    add_audit("회원가입", sid, "동의 완료")
                    st.success("회원가입이 완료되었습니다. 로그인하세요.")


def terms_gate_page():
    apply_css()
    page_header("최초 이용 동의", "서비스 이용 전 필수 확인사항에 동의해야 합니다.")
    render_terms_text()
    a1 = st.checkbox("개인정보·민감정보·보안자료 입력 금지를 확인했습니다.")
    a2 = st.checkbox("본 서비스가 업무 참고용 AI 보조 도구임을 확인했습니다.")
    a3 = st.checkbox("AI 답변과 등록 자료의 정확성·최신성·적법성이 보장되지 않음을 확인했습니다.")
    a4 = st.checkbox("최종 판단 및 업무처리 책임은 사용자와 소속 기관에 있음을 확인했습니다.")
    choice = st.radio("동의 여부", ["동의", "비동의"], horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("동의 후 이용", use_container_width=True):
            if choice != "동의" or not all([a1, a2, a3, a4]):
                st.error("모든 항목에 동의해야 이용할 수 있습니다.")
            else:
                user = current_user()
                user["terms_accepted"] = True
                user["terms_accepted_at"] = now_iso()
                save_store()
                add_audit("이용약관 동의", current_user_id())
                st.rerun()
    with c2:
        if st.button("비동의 및 로그아웃", use_container_width=True):
            logout("이용약관 비동의")
            st.rerun()

# ============================================================
# 사이드바
# ============================================================
def sidebar():
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-logo-card">
                <img src="{logo_data_uri()}" alt="소방 상징">
                <div class="sidebar-title">{APP_NAME}</div>
                <div class="sidebar-sub">{APP_VERSION} · 업무 참고용</div>
            </div>
            <div class="sidebar-box">
                <div class="label">이용자</div>
                <div class="value">{h(current_user_id())}</div>
                <div class="label" style="margin-top:8px;">권한</div>
                <div class="value">{role_label(get_role())}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        menu_items = ["홈", "법령·조례 자료", "자료 등록 요청"]
        if is_admin():
            menu_items.append("관리자")
        if st.session_state.menu not in menu_items:
            st.session_state.menu = "홈"
        st.session_state.menu = st.radio("메뉴", menu_items, index=menu_items.index(st.session_state.menu))

        st.markdown("<div class='sidebar-box'><div class='label'>세션</div><div class='value'>10분 미사용 시 자동 로그아웃</div></div>", unsafe_allow_html=True)

        if not is_admin():
            st.markdown("<div class='sidebar-box'><div class='label'>권한</div><div class='value'>관리자 권한 신청</div></div>", unsafe_allow_html=True)
            if st.button("관리자 권한 신청", use_container_width=True):
                uid = current_user_id()
                exists = any(r.get("아이디") == uid and r.get("상태") == "신청대기" for r in st.session_state.store["admin_requests"])
                if exists:
                    st.info("이미 신청대기 중입니다.")
                else:
                    st.session_state.store["admin_requests"].append({
                        "신청일시": now_iso(),
                        "아이디": uid,
                        "상태": "신청대기",
                        "처리일시": "",
                        "처리자": "",
                    })
                    save_store()
                    add_audit("관리자 권한 신청", uid)
                    st.success("관리자 권한 신청이 접수되었습니다.")

        if st.button("로그아웃", use_container_width=True):
            logout("사이드바 로그아웃")
            st.rerun()

# ============================================================
# 사용자 홈: 질문하기 + TOP5 + 내 질문
# ============================================================
def question_form_home():
    st.markdown('<div class="question-wrap">', unsafe_allow_html=True)
    st.markdown("### 질문하기")
    question = st.text_area(
        "질문 입력",
        placeholder="예: 15시에 병가를 사용했는데 주간/야간 중 어떻게 복무 처리해야 하나요?\n※ 개인정보·민감정보·보안자료는 절대 입력하지 마세요.",
        key="home_question_input",
        label_visibility="collapsed",
    )
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        clicked = st.button("질문하기", use_container_width=True, key="home_ask_button")
    st.markdown('</div>', unsafe_allow_html=True)

    if clicked:
        if not question.strip():
            st.warning("질문을 입력하세요.")
            return
        block_reason = detect_block_reason(question)
        category = classify_question(question)
        title = make_question_title(question)
        if block_reason:
            st.session_state.store["questions"].append({
                "id": new_id("q"),
                "일시": now_iso(),
                "아이디": current_user_id(),
                "분야": category,
                "소제목": "자동차단된 질문",
                "질문": "저장 안 함",
                "상태": "자동차단",
                "차단사유": block_reason,
                "사용자삭제": False,
                "관리자삭제": False,
            })
            save_store()
            add_audit("질문 자동차단", current_user_id(), block_reason)
            st.error(f"질문에 {block_reason}가 포함된 것으로 감지되어 처리하지 않았습니다. 해당 정보를 제거하고 다시 질문하세요.")
            return

        st.session_state.store["questions"].append({
            "id": new_id("q"),
            "일시": now_iso(),
            "아이디": current_user_id(),
            "분야": category,
            "소제목": title,
            "질문": question.strip(),
            "상태": "정상",
            "차단사유": "",
            "사용자삭제": False,
            "관리자삭제": False,
        })
        save_store()
        add_audit("질문 등록", current_user_id(), f"{category} / {title}")
        st.success("질문이 저장되었습니다. 실제 AI API 연동 시 이 위치에서 답변이 생성됩니다.")
        st.markdown(f"**분류된 질문 분야:** {category}")
        ai_disclaimer()


def top5_categories():
    normal = [q for q in st.session_state.store["questions"] if q.get("상태") == "정상" and not q.get("관리자삭제")]
    counts = Counter(q.get("분야", "기타") for q in normal)
    top5 = counts.most_common(5)
    st.markdown("### 사용자 질문 분야 TOP 5")
    st.caption("타인의 질문 내용은 절대 표시하지 않고, 분야별 건수만 표시합니다.")
    if not top5:
        st.info("아직 질문 통계가 없습니다.")
        return
    cols = st.columns(len(top5))
    for idx, (category, count) in enumerate(top5):
        with cols[idx]:
            st.markdown(
                f"""
                <div class="card rank-card">
                    <div class="rank-no">{idx + 1}</div>
                    <div class="rank-name">{h(category)}</div>
                    <div class="rank-count">{count}건</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def my_questions():
    st.markdown("### 내 질문 이력")
    st.caption("본인이 작성한 질문만 볼 수 있으며, 필요하면 삭제할 수 있습니다.")
    my_rows = [q for q in reversed(st.session_state.store["questions"]) if q.get("아이디") == current_user_id() and not q.get("사용자삭제") and not q.get("관리자삭제")]
    if not my_rows:
        st.info("아직 작성한 질문이 없습니다.")
        return
    for q in my_rows:
        with st.expander(f"{q.get('일시', '')} · {q.get('분야', '기타')} · {q.get('소제목', '제목 없음')}"):
            if q.get("상태") == "자동차단":
                st.warning(f"자동차단: {q.get('차단사유', '')}")
            else:
                st.write(q.get("질문", ""))
            if st.button("이 질문 삭제", key=f"delete_my_{q.get('id')}"):
                q["사용자삭제"] = True
                q["사용자삭제일시"] = now_iso()
                save_store()
                add_audit("본인 질문 삭제", q.get("id", ""))
                st.success("질문을 삭제했습니다.")
                st.rerun()


def home_page():
    top_logout_area()
    if is_admin():
        page_header("관리자 홈", "질문 통계와 운영 현황은 관리자에게만 표시됩니다.")
        admin_summary_cards()
    else:
        page_header("홈", "질문은 이 화면에서 바로 입력합니다. 타인의 질문 내용은 누구에게도 공개되지 않습니다.")
    st.markdown(
        """
        <div class="notice info">
            개인정보·민감정보·보안자료는 입력하지 마세요. 질문 내용은 본인과 관리자만 확인할 수 있고, 홈의 TOP 5에는 분야별 건수만 표시됩니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    question_form_home()
    top5_categories()
    my_questions()

# ============================================================
# 법령/조례 자료
# ============================================================
def resources_page():
    top_logout_area()
    page_header("법령·조례 자료", "등록일, 최종 확인일, 출처 URL을 함께 표시합니다.")
    st.markdown(
        """
        <div class="notice warning">
            <b>저작권 및 공개 제한 안내</b><br>
            법령·조례처럼 공개 출처가 명확한 자료는 출처 URL 중심으로 안내합니다. 다만 각종 내부 매뉴얼, 교육자료, 책자, 유료 자료, 기관 내부문서 등은 저작권·보안·공개범위 문제로 원문을 공개하지 않을 수 있습니다.<br>
            본 서비스는 자료의 정확성·최신성·적법성·저작권 상태를 보증하지 않으며, 최종 확인은 공식 출처와 담당 부서를 통해 해야 합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    visible = [r for r in st.session_state.store["resources"] if can_view_resource(r)]
    if not visible:
        st.info("현재 열람 가능한 등록 자료가 없습니다.")
        return
    for idx, r in enumerate(visible, start=1):
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">{idx}. {h(r.get('자료명', ''))}</div>
                <div class="muted">
                    분야: {h(r.get('분야', ''))} · 발행기관: {h(r.get('발행기관', ''))}<br>
                    등록일: {h(r.get('등록일', ''))} · 최종 확인일: {h(r.get('최종확인일', ''))} · 공개범위: {h(scope_label(r.get('공개범위', 'Private')))}<br>
                    출처 URL: {h(r.get('출처URL', ''))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# 자료 등록 요청
# ============================================================
def suggestion_page():
    top_logout_area()
    page_header("자료 등록 요청", "일반 사용자는 원본 파일을 업로드할 수 없습니다. 공식 출처 URL만 제출하세요.")
    st.markdown(
        """
        <div class="notice warning">
            본 서비스는 자료 등록 요청 기능만 제공합니다. 관리자는 자료의 내용, 정확성, 적법성, 최신성 또는 저작권 상태를 보증하지 않습니다.<br>
            관리자는 공식 출처 존재 여부와 공개 가능 여부만 제한적으로 확인합니다.
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
        combined = f"{name}\n{publisher}\n{source_url}\n{reason}"
        block_reason = detect_block_reason(combined)
        if not name or not publisher or not source_url or not reason:
            st.warning("모든 항목을 입력하세요.")
        elif not valid_url(source_url):
            st.error("공식 출처 URL 형식이 올바르지 않습니다.")
        elif block_reason:
            st.session_state.store["suggestions"].append({
                "id": new_id("s"),
                "요청일시": now_iso(),
                "요청자": current_user_id(),
                "분야": category,
                "자료명": name,
                "발행기관": publisher,
                "출처URL": source_url,
                "요청사유": "저장 제한",
                "상태": "자동차단",
                "차단사유": block_reason,
            })
            save_store()
            add_audit("자료 요청 자동차단", current_user_id(), block_reason)
            st.error(f"{block_reason}가 포함된 것으로 감지되어 관리자 검토 없이 차단했습니다.")
        else:
            st.session_state.store["suggestions"].append({
                "id": new_id("s"),
                "요청일시": now_iso(),
                "요청자": current_user_id(),
                "분야": category,
                "자료명": name,
                "발행기관": publisher,
                "출처URL": source_url,
                "요청사유": reason,
                "상태": "출처확인대기",
                "차단사유": "",
            })
            save_store()
            add_audit("자료 등록 요청", current_user_id(), name)
            st.success("자료 등록 요청이 접수되었습니다.")

# ============================================================
# 관리자
# ============================================================
def admin_summary_cards():
    active_users = [u for u in users().values() if u.get("is_active", True)]
    normal_questions = [q for q in st.session_state.store["questions"] if q.get("상태") == "정상" and not q.get("관리자삭제")]
    pending = [s for s in st.session_state.store["suggestions"] if s.get("상태") == "출처확인대기"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("가입자 수", len(active_users))
    c2.metric("누적 질문", len(st.session_state.store["questions"]))
    c3.metric("정상 질문", len(normal_questions))
    c4.metric("자료 요청 대기", len(pending))


def admin_dashboard_tab():
    st.markdown("### 운영 통계")
    admin_summary_cards()
    normal_questions = [q for q in st.session_state.store["questions"] if q.get("상태") == "정상" and not q.get("관리자삭제")]
    category_counts = Counter(q.get("분야", "기타") for q in normal_questions)
    title_counts = Counter(q.get("소제목", "제목 없음") for q in normal_questions)
    left, right = st.columns(2)
    with left:
        st.markdown("#### 질문 분야 비율")
        if category_counts:
            rows = [{"분야": k, "건수": v} for k, v in category_counts.most_common()]
            df = to_df(rows)
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
            rows = [{"소제목": k, "건수": v} for k, v in title_counts.most_common(10)]
            df = to_df(rows)
            if pd is not None:
                st.bar_chart(df.set_index("소제목"))
                st.dataframe(df, use_container_width=True)
            else:
                st.write(rows)
        else:
            st.info("소제목 통계가 없습니다.")


def admin_questions_tab():
    st.markdown("### 질문 이력 관리")
    st.caption("관리자는 질문자 아이디, 일자·시간, 분야, 소제목, 질문 내용을 확인할 수 있습니다.")
    rows = [q for q in st.session_state.store["questions"] if not q.get("관리자삭제")]
    if not rows:
        st.info("질문 이력이 없습니다.")
        return
    if pd is not None:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.write(rows)
    st.markdown("#### 개별 질문 삭제")
    q_options = [f"{q.get('id')} | {q.get('일시')} | {q.get('아이디')} | {q.get('소제목')}" for q in rows]
    selected = st.selectbox("삭제할 질문", q_options)
    if st.button("선택 질문 관리자 삭제"):
        qid = selected.split(" | ")[0]
        for q in st.session_state.store["questions"]:
            if q.get("id") == qid:
                q["관리자삭제"] = True
                q["관리자삭제일시"] = now_iso()
                q["관리자삭제자"] = current_user_id()
                break
        save_store()
        add_audit("관리자 질문 삭제", qid)
        st.success("질문을 삭제했습니다.")
        st.rerun()


def admin_suggestions_tab():
    st.markdown("### 자료 등록 요청 관리")
    st.info("관리자는 공식 출처 존재 여부, 공개 가능 여부, 보안자료 아님만 확인합니다.")
    rows = st.session_state.store["suggestions"]
    if not rows:
        st.info("자료 등록 요청이 없습니다.")
        return
    for item in rows:
        if item.get("상태") != "출처확인대기":
            continue
        with st.expander(f"{item.get('자료명')} / {item.get('요청자')} / {item.get('요청일시')}"):
            st.write(f"분야: {item.get('분야')}")
            st.write(f"발행기관: {item.get('발행기관')}")
            st.write(f"출처 URL: {item.get('출처URL')}")
            st.write(f"요청 사유: {item.get('요청사유')}")
            c1, c2, c3 = st.columns(3)
            with c1:
                official = st.checkbox("공식 출처 존재 확인", key=f"official_{item.get('id')}")
            with c2:
                public_ok = st.checkbox("공개 가능 자료 확인", key=f"public_{item.get('id')}")
            with c3:
                not_secret = st.checkbox("보안자료 아님 확인", key=f"secret_{item.get('id')}")
            scope = st.selectbox("공개범위", RESOURCE_SCOPES, index=0, format_func=scope_label, key=f"scope_{item.get('id')}")
            memo = st.text_input("관리자 메모", key=f"memo_{item.get('id')}")
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("승인", key=f"approve_{item.get('id')}"):
                    if not all([official, public_ok, not_secret]):
                        st.error("세 가지 확인사항을 모두 체크해야 승인할 수 있습니다.")
                    else:
                        st.session_state.store["resources"].append({
                            "id": new_id("r"),
                            "자료명": item.get("자료명"),
                            "분야": item.get("분야"),
                            "발행기관": item.get("발행기관"),
                            "출처URL": item.get("출처URL"),
                            "등록일": today_str(),
                            "최종확인일": today_str(),
                            "공개범위": scope,
                            "등록자": current_user_id(),
                            "관리자메모": memo,
                        })
                        item["상태"] = "승인완료"
                        item["처리일시"] = now_iso()
                        item["처리자"] = current_user_id()
                        save_store()
                        add_audit("자료 요청 승인", item.get("자료명"), f"scope={scope}")
                        st.success("승인 및 자료 등록 완료")
                        st.rerun()
            with b2:
                if st.button("반려", key=f"reject_{item.get('id')}"):
                    item["상태"] = "반려"
                    item["처리일시"] = now_iso()
                    item["처리자"] = current_user_id()
                    save_store()
                    add_audit("자료 요청 반려", item.get("자료명"))
                    st.rerun()
            with b3:
                if st.button("등록 금지", key=f"prohibit_{item.get('id')}"):
                    item["상태"] = "등록금지"
                    item["처리일시"] = now_iso()
                    item["처리자"] = current_user_id()
                    save_store()
                    add_audit("자료 요청 등록금지", item.get("자료명"))
                    st.rerun()

    st.markdown("#### 전체 요청 목록")
    if pd is not None:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.write(rows)


def admin_resources_tab():
    st.markdown("### 관리자 직접 자료 등록")
    st.caption("기본 공개범위는 비공개입니다.")
    with st.form("admin_resource_form"):
        category = st.selectbox("분야", RESOURCE_CATEGORIES)
        name = st.text_input("자료명")
        publisher = st.text_input("발행기관")
        url = st.text_input("공식 출처 URL")
        scope = st.selectbox("공개범위", RESOURCE_SCOPES, index=0, format_func=scope_label)
        last_checked = st.date_input("최종 확인일")
        memo = st.text_area("관리자 메모")
        submitted = st.form_submit_button("자료 등록")
    if submitted:
        combined = f"{name}\n{publisher}\n{url}\n{memo}"
        block_reason = detect_block_reason(combined)
        if not name or not publisher or not url:
            st.warning("자료명, 발행기관, 출처 URL을 입력하세요.")
        elif not valid_url(url):
            st.error("URL 형식이 올바르지 않습니다.")
        elif block_reason:
            st.error(f"{block_reason}가 포함된 것으로 감지되어 등록할 수 없습니다.")
        else:
            st.session_state.store["resources"].append({
                "id": new_id("r"),
                "자료명": name,
                "분야": category,
                "발행기관": publisher,
                "출처URL": url,
                "등록일": today_str(),
                "최종확인일": str(last_checked),
                "공개범위": scope,
                "등록자": current_user_id(),
                "관리자메모": memo,
            })
            save_store()
            add_audit("관리자 직접 자료 등록", name, f"scope={scope}")
            st.success("자료가 등록되었습니다.")
    st.markdown("#### 등록 자료 목록")
    rows = st.session_state.store["resources"]
    if rows:
        if pd is not None:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        else:
            st.write(rows)
    else:
        st.info("등록 자료가 없습니다.")


def admin_users_tab():
    st.markdown("### 회원·권한 관리")
    st.markdown("#### 관리자 권한 신청")
    requests = st.session_state.store["admin_requests"]
    pending = [r for r in requests if r.get("상태") == "신청대기"]
    if requests:
        if pd is not None:
            st.dataframe(pd.DataFrame(requests), use_container_width=True)
        else:
            st.write(requests)
    else:
        st.info("관리자 권한 신청이 없습니다.")
    if pending:
        selected_req = st.selectbox("처리할 신청자", [r["아이디"] for r in pending])
        c1, c2 = st.columns(2)
        with c1:
            if st.button("관리자 승인", use_container_width=True):
                users()[selected_req]["role"] = "admin"
                for r in requests:
                    if r.get("아이디") == selected_req and r.get("상태") == "신청대기":
                        r["상태"] = "승인"
                        r["처리일시"] = now_iso()
                        r["처리자"] = current_user_id()
                save_store()
                add_audit("관리자 권한 승인", selected_req)
                st.rerun()
        with c2:
            if st.button("관리자 신청 반려", use_container_width=True):
                for r in requests:
                    if r.get("아이디") == selected_req and r.get("상태") == "신청대기":
                        r["상태"] = "반려"
                        r["처리일시"] = now_iso()
                        r["처리자"] = current_user_id()
                save_store()
                add_audit("관리자 권한 반려", selected_req)
                st.rerun()

    st.markdown("#### 가입자 목록")
    user_rows = []
    for uid, user in users().items():
        user_rows.append({
            "아이디": uid,
            "권한": role_label(user.get("role", "user")),
            "가입일시": user.get("created_at", ""),
            "최근로그인": user.get("last_login_at", ""),
            "활성": user.get("is_active", True),
            "강제로그아웃기준": user.get("force_logout_after", ""),
        })
    if pd is not None:
        st.dataframe(pd.DataFrame(user_rows), use_container_width=True)
    else:
        st.write(user_rows)

    st.markdown("#### 사용자 관리")
    targets = [uid for uid in users().keys() if uid != current_user_id()]
    if not targets:
        st.info("관리 가능한 다른 사용자가 없습니다.")
        return
    target = st.selectbox("대상 아이디", targets)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("강제 로그아웃", use_container_width=True):
            users()[target]["force_logout_after"] = now_iso()
            save_store()
            add_audit("사용자 강제 로그아웃", target)
            st.success("강제 로그아웃 처리했습니다. 해당 사용자는 다음 화면 갱신 시 로그아웃됩니다.")
    with c2:
        if st.button("일반사용자 전환", use_container_width=True):
            users()[target]["role"] = "user"
            save_store()
            add_audit("권한 일반사용자 전환", target)
            st.rerun()
    with c3:
        if st.button("관리자 전환", use_container_width=True):
            users()[target]["role"] = "admin"
            save_store()
            add_audit("권한 관리자 전환", target)
            st.rerun()
    with c4:
        if st.button("비활성화", use_container_width=True):
            active_admins = [u for u in users().values() if u.get("role") == "admin" and u.get("is_active", True)]
            if users()[target].get("role") == "admin" and len(active_admins) <= 1:
                st.error("마지막 관리자 계정은 비활성화할 수 없습니다.")
            else:
                users()[target]["is_active"] = False
                users()[target]["force_logout_after"] = now_iso()
                save_store()
                add_audit("가입자 비활성화", target)
                st.rerun()

    st.markdown("#### 가입자 아이디 완전 삭제")
    st.warning("실제 운영에서는 완전 삭제보다 비활성화를 권장합니다. 완전 삭제 시 해당 계정 정보가 사라집니다.")
    confirm = st.text_input("완전 삭제하려면 대상 아이디를 그대로 입력하세요")
    if st.button("대상 아이디 완전 삭제"):
        if confirm != target:
            st.error("확인 아이디가 일치하지 않습니다.")
        else:
            active_admins = [uid for uid, u in users().items() if u.get("role") == "admin" and u.get("is_active", True)]
            if target in active_admins and len(active_admins) <= 1:
                st.error("마지막 관리자 계정은 삭제할 수 없습니다.")
            else:
                del users()[target]
                save_store()
                add_audit("가입자 완전 삭제", target)
                st.success("삭제했습니다.")
                st.rerun()


def admin_audit_tab():
    st.markdown("### 감사로그")
    rows = st.session_state.store["audit_logs"]
    if not rows:
        st.info("감사로그가 없습니다.")
    else:
        if pd is not None:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        else:
            st.write(rows)


def admin_page():
    if not is_admin():
        st.error("관리자만 접근할 수 있습니다.")
        st.stop()
    top_logout_area()
    page_header("관리자", "일반사용자와 관리자를 구분하고, 질문·회원·자료·감사로그를 관리합니다.")
    tabs = st.tabs(["통계", "질문 이력", "자료 요청", "자료 직접 등록", "회원·권한", "감사로그"])
    with tabs[0]:
        admin_dashboard_tab()
    with tabs[1]:
        admin_questions_tab()
    with tabs[2]:
        admin_suggestions_tab()
    with tabs[3]:
        admin_resources_tab()
    with tabs[4]:
        admin_users_tab()
    with tabs[5]:
        admin_audit_tab()

# ============================================================
# 메인
# ============================================================
def main():
    apply_css()
    if not current_user_id():
        login_page()
        return
    login_required_guard()
    user = current_user()
    if not user:
        st.session_state.login_user = None
        st.rerun()
    if not user.get("terms_accepted", False):
        terms_gate_page()
        return
    inject_inactivity_timer()
    sidebar()
    menu = st.session_state.menu
    if menu == "홈":
        home_page()
    elif menu == "법령·조례 자료":
        resources_page()
    elif menu == "자료 등록 요청":
        suggestion_page()
    elif menu == "관리자":
        admin_page()
    mark_activity()


if __name__ == "__main__":
    main()
