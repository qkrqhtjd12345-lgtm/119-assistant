"""
충남119행정비서 Streamlit MVP
- 기본 비공개 자료 관리
- 타인 질문 비공개
- 개인정보 자동 차단 및 원문 미저장
- 관리자 질문 열람 감사로그
- 관리자 책임 최소화 문구 및 공개범위 확인 절차

실행:
    pip install -r requirements.txt
    streamlit run app.py

초기 관리자 계정:
    ID: admin
    PW: admin1234!
배포 전 반드시 변경하세요.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import html
import json
import os
import re
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

APP_NAME = "충남119행정비서"
APP_VERSION = "v0.9.0 MVP"
DATA_DIR = Path(__file__).parent / "data"
SESSION_TIMEOUT_SECONDS = 10 * 60

FILES = {
    "users": DATA_DIR / "users.json",
    "questions": DATA_DIR / "questions.json",
    "resources": DATA_DIR / "resources.json",
    "resource_requests": DATA_DIR / "resource_requests.json",
    "audit_logs": DATA_DIR / "audit_logs.json",
    "notices": DATA_DIR / "notices.json",
}

VISIBILITY_LABELS = {
    "Private": "비공개 Private — 기본값, 공개 여부 검토 전",
    "User": "로그인 사용자 User — 로그인 사용자에게만 공개",
    "Public": "공개 Public — 공식적으로 공개된 자료만 선택",
    "Admin": "관리자 전용 Admin — 관리자만 확인",
    "Prohibited": "등록 금지 Prohibited — 개인정보, 보안, 저작권 문제 자료",
}

VISIBLE_TO_USER = {"Public", "User"}
RESOURCE_CATEGORIES = ["법령", "조례", "훈령", "내부 지침", "기타"]
QUESTION_CATEGORIES = ["복무", "병가", "연가", "출장", "교육", "초과근무", "인사", "감사", "예산", "기타"]
QUESTION_STATUS = ["정상", "자동차단", "삭제요청", "비공개"]
ADMIN_VIEW_PURPOSES = ["오류 확인", "오남용 점검", "사용자 민원 대응", "개인정보·보안자료 신고 처리", "서비스 품질 개선"]
NON_PUBLIC_REASONS = [
    "저작권 확인 필요",
    "내부 매뉴얼로 공개 부적절",
    "보안자료 가능성",
    "개인정보 포함 가능성",
    "공식 출처 불명확",
    "최신성 확인 필요",
    "기관 내부자료",
    "원문 공개 불가",
    "링크만 제공 가능",
    "담당 부서 확인 필요",
]

AI_DISCLAIMER = (
    "본 답변은 업무 참고용 AI 정보입니다. 등록 자료 및 AI 답변의 정확성, 완전성, 최신성 또는 "
    "특정 업무처리의 적법성을 보증하지 않습니다. 최종 판단 및 업무처리 책임은 사용자와 소속 기관에 있습니다. "
    "정확한 내용은 반드시 담당 부서와 공식 자료를 확인하십시오."
)

COMMON_DISCLAIMER = """
본 서비스는 업무 참고용 AI 보조 도구이며, 공식 유권해석, 행정처분, 법률자문, 인사결정, 감사 판단을 대신하지 않습니다.  
운영자 및 관리자는 AI 답변, 등록 자료, 외부 출처 자료의 정확성, 완전성, 최신성, 적법성, 저작권 상태를 보증하지 않습니다.  
관리자는 공식 출처 존재 여부, 공개 가능 여부, 보안자료 여부, 공개범위 설정만 제한적으로 확인합니다.  
최종 업무처리, 결재, 복무 판단, 법령 적용, 보고서 제출 책임은 사용자와 소속 기관에 있습니다.  
정확한 내용은 반드시 소속 기관 담당 부서, 공식 법령·조례·예규·공문, 업무 담당자에게 최종 확인하시기 바랍니다.
"""


# -----------------------------------------------------------------------------
# 기본 유틸
# -----------------------------------------------------------------------------


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def uid(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{secrets.token_hex(3)}"


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def load_json(name: str, default: Any) -> Any:
    path = FILES[name]
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(name: str, data: Any) -> None:
    path = FILES[name]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def hash_password(password: str, *, salt: str | None = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 150_000)
    return f"pbkdf2_sha256${salt}${base64.b64encode(digest).decode('ascii')}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, salt, digest = encoded.split("$", 2)
        if algo != "pbkdf2_sha256":
            return False
        expected = hash_password(password, salt=salt).split("$", 2)[2]
        return hmac.compare_digest(expected, digest)
    except Exception:
        return False


def add_audit(actor: str, action: str, target: str = "", detail: str = "") -> None:
    logs = load_json("audit_logs", [])
    logs.append(
        {
            "id": uid("log"),
            "created_at": now_iso(),
            "actor": actor,
            "action": action,
            "target": target,
            "detail": detail,
        }
    )
    save_json("audit_logs", logs)


def current_user() -> dict[str, Any] | None:
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None
    users = load_json("users", [])
    for user in users:
        if user.get("user_id") == user_id:
            return user
    return None


def require_admin() -> bool:
    user = current_user()
    return bool(user and user.get("role") == "admin" and user.get("is_active", True))


# -----------------------------------------------------------------------------
# 개인정보·민감정보 감지
# -----------------------------------------------------------------------------


BLOCK_PATTERNS: list[tuple[str, str]] = [
    ("주민등록번호 형태", r"\b\d{6}\s*[-~]?\s*[1-4]\d{6}\b"),
    ("휴대전화번호 형태", r"\b01[016789][-\s]?\d{3,4}[-\s]?\d{4}\b"),
    ("이메일 형태", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    ("계좌번호 의심", r"\b\d{2,6}[-\s]\d{2,6}[-\s]\d{2,8}(?:[-\s]\d{1,4})?\b"),
    ("차량번호 의심", r"\b\d{2,3}[가-힣]\s?\d{4}\b"),
    ("상세 주소 의심", r"[가-힣A-Za-z0-9]+(?:시|군|구)\s+[가-힣A-Za-z0-9]+(?:로|길)\s*\d+"),
    ("특정 개인 실명과 소속 의심", r"[가-힣]{2,4}\s*(?:소방서|119안전센터|센터|구조대|구급대|과|팀|계)"),
]

BLOCK_KEYWORDS = [
    "진단서",
    "병명",
    "치료기록",
    "의무기록",
    "건강정보",
    "징계",
    "수사",
    "감사",
    "민원인",
    "대외비",
    "비공개",
    "보안자료",
    "주민등록번호",
    "전화번호",
    "주소",
    "계좌번호",
    "온나라",
    "내부 시스템",
]


def detect_sensitive_text(text: str) -> list[str]:
    reasons: list[str] = []
    normalized = text.strip()
    for label, pattern in BLOCK_PATTERNS:
        if re.search(pattern, normalized):
            reasons.append(label)
    for keyword in BLOCK_KEYWORDS:
        if keyword in normalized:
            reasons.append(f"금지 키워드: {keyword}")
    return sorted(set(reasons))


# -----------------------------------------------------------------------------
# 초기 데이터
# -----------------------------------------------------------------------------


def init_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    users = load_json("users", [])
    if not users:
        users = [
            {
                "user_id": "admin",
                "password_hash": hash_password("admin1234!"),
                "role": "admin",
                "created_at": now_iso(),
                "last_login": "",
                "last_active": "",
                "is_active": True,
                "force_logout": False,
                "admin_request_reason": "초기 관리자 계정",
                "memo": "배포 전 비밀번호 변경 필수",
            }
        ]
        save_json("users", users)

    if not FILES["questions"].exists():
        save_json("questions", [])
    if not FILES["resource_requests"].exists():
        save_json("resource_requests", [])
    if not FILES["audit_logs"].exists():
        save_json("audit_logs", [])
    if not FILES["notices"].exists():
        save_json(
            "notices",
            [
                {
                    "id": uid("notice"),
                    "title": "시범 운영 안내",
                    "body": "본 서비스는 업무 참고용 AI 보조 도구입니다. 개인정보·민감정보·보안자료는 입력하지 마십시오.",
                    "is_active": True,
                    "created_at": now_iso(),
                }
            ],
        )
    if not FILES["resources"].exists():
        save_json(
            "resources",
            [
                {
                    "id": uid("res"),
                    "title": "국가법령정보센터",
                    "category": "법령",
                    "agency": "법제처",
                    "source_url": "https://www.law.go.kr",
                    "summary": "공개 법령 확인용 공식 출처입니다.",
                    "visibility": "Public",
                    "non_public_reason": "",
                    "created_at": now_iso(),
                    "checked_at": today_str(),
                    "created_by": "system",
                    "updated_at": now_iso(),
                },
                {
                    "id": uid("res"),
                    "title": "자치법규정보시스템",
                    "category": "조례",
                    "agency": "행정안전부",
                    "source_url": "https://www.elis.go.kr",
                    "summary": "조례·규칙 확인용 공식 출처입니다.",
                    "visibility": "Public",
                    "non_public_reason": "",
                    "created_at": now_iso(),
                    "checked_at": today_str(),
                    "created_by": "system",
                    "updated_at": now_iso(),
                },
            ],
        )


# -----------------------------------------------------------------------------
# 스타일
# -----------------------------------------------------------------------------


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --main-navy: #1F2F3F;
            --deep-navy: #172635;
            --sub-navy: #2D4053;
            --coral: #F28C6B;
            --bg: #F7F8F5;
            --card: #FFFFFF;
            --text: #263238;
            --muted: #667085;
            --line: #D9E0E3;
            --danger: #B42318;
            --warning-bg: #FFF7ED;
            --info-bg: #EFF8FF;
        }
        .stApp { background: var(--bg); color: var(--text); }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #1F2F3F 0%, #172635 100%); }
        [data-testid="stSidebar"] * { color: #FFFFFF !important; }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 12px;
            padding: 8px 10px;
            margin: 4px 0;
        }
        [data-testid="stSidebar"] .stButton button {
            width: 100%;
            background: #F28C6B !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
        }
        h1, h2, h3 { color: var(--main-navy); letter-spacing: -0.02em; }
        .login-wrap {
            max-width: 520px;
            margin: 40px auto 0 auto;
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 28px;
            box-shadow: 0 14px 32px rgba(31,47,63,0.08);
        }
        .logo-mark {
            width: 64px; height: 64px; border-radius: 18px;
            background: linear-gradient(135deg, #1F2F3F, #F28C6B);
            display:flex; align-items:center; justify-content:center;
            font-size: 30px; color: white; margin-bottom: 12px;
        }
        .section-card, .metric-card, .resource-card, .notice-card {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: 0 8px 22px rgba(31,47,63,0.05);
            margin-bottom: 14px;
        }
        .metric-card .num { font-size: 28px; font-weight: 800; color: var(--main-navy); }
        .metric-card .label { font-size: 13px; color: var(--muted); }
        .info-box, .warn-box, .disclaimer-box {
            border-radius: 14px; padding: 15px 17px; margin: 12px 0;
        }
        .info-box { background: var(--info-bg); border-left: 5px solid #2D4053; color: #1F2F3F; }
        .warn-box { background: var(--warning-bg); border-left: 5px solid #B42318; color: #7A271A; }
        .disclaimer-box { background: #FFFFFF; border: 1px solid var(--line); color: #344054; }
        .disclaimer-box b { color: var(--main-navy); }
        .badge {
            display: inline-block; padding: 4px 9px; border-radius: 999px;
            font-size: 12px; font-weight: 700; border: 1px solid var(--line);
            background: #F2F4F7; color: #344054;
        }
        .badge-public { background: #EFF8FF; color: #175CD3; border-color: #B2DDFF; }
        .badge-user { background: #F9F5FF; color: #6941C6; border-color: #D6BBFB; }
        .badge-private { background: #F2F4F7; color: #344054; }
        .badge-admin { background: #FEF3F2; color: #B42318; border-color: #FECDCA; }
        .badge-prohibited { background: #7A271A; color: #FFFFFF; border-color: #7A271A; }
        .source-button {
            display: inline-block; background: #1F2F3F; color: #FFFFFF !important;
            padding: 9px 12px; border-radius: 10px; text-decoration: none; font-weight: 700;
            margin-top: 8px;
        }
        .muted { color: var(--muted); font-size: 13px; }
        .small { font-size: 12px; color: var(--muted); }
        .topbar {
            display:flex; align-items:center; justify-content:space-between;
            background:#FFFFFF; border: 1px solid var(--line); border-radius: 16px;
            padding: 12px 16px; margin-bottom: 14px;
        }
        .stButton button, .stFormSubmitButton button {
            border-radius: 10px !important;
            font-weight: 700 !important;
        }
        .stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {
            background: #1F2F3F !important;
            color: white !important;
            border: 1px solid #1F2F3F !important;
        }
        a { color: #1F2F3F; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def box(kind: str, title: str, body: str) -> None:
    class_name = {
        "info": "info-box",
        "warn": "warn-box",
        "disclaimer": "disclaimer-box",
    }.get(kind, "info-box")
    safe_body = "<br>".join(esc(line) for line in body.strip().splitlines() if line.strip())
    st.markdown(f"<div class='{class_name}'><b>{esc(title)}</b><br>{safe_body}</div>", unsafe_allow_html=True)


def badge(text: str, kind: str = "") -> str:
    suffix = f" badge-{kind}" if kind else ""
    return f"<span class='badge{suffix}'>{esc(text)}</span>"


def render_common_disclaimer() -> None:
    box("disclaimer", "공통 안내", COMMON_DISCLAIMER)


# -----------------------------------------------------------------------------
# 인증
# -----------------------------------------------------------------------------


def login_page() -> None:
    st.markdown(
        f"""
        <div class="login-wrap">
            <div class="logo-mark">🚒</div>
            <h1 style="margin-bottom:4px;">{APP_NAME}</h1>
            <div class="muted">소방공무원 행정·복무 업무 참고용 AI 보조 서비스</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        tab_login, tab_join = st.tabs(["로그인", "회원가입"])
        with tab_login:
            with st.form("login_form"):
                user_id = st.text_input("아이디", max_chars=30)
                password = st.text_input("비밀번호", type="password")
                submitted = st.form_submit_button("로그인", type="primary", use_container_width=True)
            if submitted:
                users = load_json("users", [])
                user = next((u for u in users if u.get("user_id") == user_id), None)
                if not user or not verify_password(password, user.get("password_hash", "")):
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
                    add_audit(user_id or "unknown", "LOGIN_FAIL", user_id, "로그인 실패")
                elif not user.get("is_active", True):
                    st.error("비활성화된 계정입니다. 관리자에게 문의하십시오.")
                else:
                    for item in users:
                        if item.get("user_id") == user_id:
                            item["last_login"] = now_iso()
                            item["last_active"] = now_iso()
                            item["force_logout"] = False
                    save_json("users", users)
                    st.session_state["user_id"] = user_id
                    st.session_state["last_active_ts"] = time.time()
                    add_audit(user_id, "LOGIN", user_id, "로그인 성공")
                    st.rerun()

        with tab_join:
            box(
                "info",
                "가입 안내",
                "개인정보 최소화를 위해 이름, 전화번호, 소속, 주소를 받지 않습니다. 아이디와 비밀번호만 입력하십시오.",
            )
            with st.form("join_form"):
                new_id = st.text_input("사용할 아이디", max_chars=30, help="영문, 숫자, _, - 조합 권장")
                new_pw = st.text_input("비밀번호", type="password")
                new_pw2 = st.text_input("비밀번호 확인", type="password")
                admin_request = st.checkbox("관리자 권한 신청")
                admin_reason = st.text_area("관리자 권한 신청 사유", disabled=not admin_request, max_chars=300)
                joined = st.form_submit_button("회원가입", type="primary", use_container_width=True)
            if joined:
                users = load_json("users", [])
                if not re.fullmatch(r"[A-Za-z0-9_-]{4,30}", new_id or ""):
                    st.error("아이디는 영문, 숫자, _, - 조합 4~30자로 입력하십시오.")
                elif len(new_pw) < 8:
                    st.error("비밀번호는 8자 이상으로 입력하십시오.")
                elif new_pw != new_pw2:
                    st.error("비밀번호 확인이 일치하지 않습니다.")
                elif any(u.get("user_id") == new_id for u in users):
                    st.error("이미 사용 중인 아이디입니다.")
                else:
                    users.append(
                        {
                            "user_id": new_id,
                            "password_hash": hash_password(new_pw),
                            "role": "user",
                            "created_at": now_iso(),
                            "last_login": "",
                            "last_active": "",
                            "is_active": True,
                            "force_logout": False,
                            "admin_request_reason": admin_reason.strip() if admin_request else "",
                            "memo": "",
                        }
                    )
                    save_json("users", users)
                    add_audit(new_id, "REGISTER", new_id, "회원가입")
                    st.success("가입이 완료되었습니다. 로그인하십시오.")

    render_common_disclaimer()


def logout(reason: str = "사용자 로그아웃") -> None:
    user_id = st.session_state.get("user_id", "unknown")
    add_audit(user_id, "LOGOUT", user_id, reason)
    st.session_state.clear()
    st.rerun()


def check_session() -> None:
    user = current_user()
    if not user:
        return
    if user.get("force_logout"):
        st.warning("관리자에 의해 로그아웃 처리되었습니다.")
        st.session_state.clear()
        st.rerun()
    last_ts = st.session_state.get("last_active_ts", time.time())
    if time.time() - last_ts > SESSION_TIMEOUT_SECONDS:
        st.warning("10분 이상 미사용으로 자동 로그아웃되었습니다.")
        logout("세션 타임아웃")
    st.session_state["last_active_ts"] = time.time()
    users = load_json("users", [])
    for item in users:
        if item.get("user_id") == user.get("user_id"):
            item["last_active"] = now_iso()
    save_json("users", users)


# -----------------------------------------------------------------------------
# 사용자 화면
# -----------------------------------------------------------------------------


def generate_ai_answer(category: str, question: str) -> str:
    """실제 AI/API 연결 전 임시 답변 생성기.

    운영 전에는 이 부분을 OpenAI API, RAG 검색, 내부 DB 검색으로 교체하십시오.
    """
    trimmed = question.strip()
    return (
        f"[{category}] 분야 질문으로 접수되었습니다.\n\n"
        "현재 MVP 버전에서는 공식 자료 DB/API와 연결되지 않은 임시 답변만 제공합니다. "
        "실제 운영 시에는 등록된 공개자료, 법령·조례 공식 출처, 기관 내부 검토 절차를 기반으로 답변하도록 연결해야 합니다.\n\n"
        "업무 적용 전 확인 순서:\n"
        "1. 국가법령정보센터 또는 자치법규정보시스템에서 최신 법령·조례 확인\n"
        "2. 소속 기관 복무·인사·감사 담당 부서 확인\n"
        "3. 필요한 경우 공식 공문 또는 내부 결재 절차 확인\n\n"
        f"질문 요약: {trimmed[:180]}{'...' if len(trimmed) > 180 else ''}\n\n"
        f"---\n{AI_DISCLAIMER}"
    )


def home_page() -> None:
    user = current_user()
    assert user is not None

    st.markdown(
        """
        <div class="section-card">
            <h2 style="margin:0 0 6px 0;">업무 참고 질문</h2>
            <div class="muted">복무·출장·병가·교육·예산 등 행정 업무를 질문할 수 있습니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    notices = [n for n in load_json("notices", []) if n.get("is_active")]
    for notice in notices[:3]:
        st.markdown(
            f"""
            <div class="notice-card">
                <b>📢 {esc(notice.get('title'))}</b><br>
                <span class="muted">{esc(notice.get('body'))}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    box(
        "warn",
        "질문 입력 전 확인",
        "질문 내용은 일반 사용자 화면에서 본인만 확인할 수 있습니다.\n"
        "타인의 질문 내용은 공개되지 않으며, TOP 5에는 분야별 건수만 표시됩니다.\n"
        "개인정보·민감정보·보안자료는 입력하지 마십시오.\n"
        "정확한 내용은 반드시 소속 기관 담당 부서 및 공식 자료로 확인하십시오.",
    )

    with st.form("question_form"):
        category = st.selectbox("질문 분야", QUESTION_CATEGORIES)
        question = st.text_area("질문 내용", height=160, placeholder="예: 병가 사용 시 증빙서류와 복무 처리는 어떻게 확인해야 하나요?")
        submitted = st.form_submit_button("질문하기", type="primary", use_container_width=True)

    if submitted:
        questions = load_json("questions", [])
        reasons = detect_sensitive_text(question)
        if not question.strip():
            st.error("질문 내용을 입력하십시오.")
        elif reasons:
            # 원문 저장 금지. 차단 사유만 저장.
            blocked_record = {
                "id": uid("q"),
                "user_id": user["user_id"],
                "category": category,
                "question": "",
                "answer": "",
                "status": "자동차단",
                "blocked": True,
                "blocked_reasons": reasons,
                "created_at": now_iso(),
                "deleted": False,
            }
            questions.append(blocked_record)
            save_json("questions", questions)
            add_audit(user["user_id"], "QUESTION_BLOCKED", blocked_record["id"], ", ".join(reasons))
            st.error("개인정보·민감정보·보안자료로 의심되는 내용이 있어 저장하지 않았습니다. 해당 내용을 제거하고 다시 질문하십시오.")
            st.caption("차단 사유: " + ", ".join(reasons))
        else:
            answer = generate_ai_answer(category, question)
            record = {
                "id": uid("q"),
                "user_id": user["user_id"],
                "category": category,
                "question": question.strip(),
                "answer": answer,
                "status": "정상",
                "blocked": False,
                "blocked_reasons": [],
                "created_at": now_iso(),
                "deleted": False,
            }
            questions.append(record)
            save_json("questions", questions)
            add_audit(user["user_id"], "QUESTION_CREATE", record["id"], category)
            st.success("질문이 등록되었습니다.")
            st.markdown("### AI 답변")
            st.text_area("답변", answer, height=280, disabled=True)

    st.markdown("### 사용자 질문 분야 TOP 5")
    questions = [q for q in load_json("questions", []) if not q.get("deleted") and not q.get("blocked")]
    if questions:
        top_df = pd.DataFrame(questions).groupby("category").size().reset_index(name="건수").sort_values("건수", ascending=False).head(5)
        st.bar_chart(top_df.set_index("category"))
    else:
        st.info("아직 누적 질문 통계가 없습니다. TOP 5에는 질문 내용 없이 분야별 건수만 표시됩니다.")

    st.markdown("### 내 최근 질문")
    my_questions = [q for q in questions if q.get("user_id") == user["user_id"]]
    if my_questions:
        for q in sorted(my_questions, key=lambda x: x.get("created_at", ""), reverse=True)[:5]:
            with st.expander(f"{q.get('created_at', '')} · {q.get('category', '')}"):
                st.write(q.get("question", ""))
                st.text_area("답변", q.get("answer", ""), height=180, disabled=True, key=f"recent_ans_{q['id']}")
    else:
        st.info("본인 질문 이력이 없습니다.")

    render_common_disclaimer()


def resources_page() -> None:
    st.markdown("# 법령·조례 자료")
    box(
        "info",
        "자료 공개 기준",
        "이 화면에는 공개 가능하거나 로그인 사용자에게 공개가 허용된 자료만 표시됩니다.\n"
        "비공개(Private), 관리자 전용(Admin), 등록 금지(Prohibited) 자료는 일반 사용자 화면에 표시되지 않습니다.\n"
        "각종 매뉴얼, 내부 교육자료, 업무처리 편람, 책자, 유료자료, 내부 공문, 시스템 캡처 등은 저작권·보안·공개범위 문제로 원문 공개가 제한될 수 있습니다.\n"
        "공개되지 않는 자료가 있다고 해서 자료가 존재하지 않는다는 의미는 아니며, 공개 가능 여부가 확인되지 않은 자료는 사용자에게 제공하지 않습니다.\n"
        "정확한 내용은 반드시 소속 기관 담당 부서, 공식 법령·조례·예규·공문, 업무 담당자에게 최종 확인하십시오.",
    )

    resources = [r for r in load_json("resources", []) if r.get("visibility") in VISIBLE_TO_USER]
    col1, col2 = st.columns([2, 1])
    with col1:
        keyword = st.text_input("자료 검색", placeholder="자료명, 발행기관, 분야, 키워드")
    with col2:
        category_filter = st.selectbox("분야 필터", ["전체"] + RESOURCE_CATEGORIES)

    filtered = []
    for r in resources:
        haystack = " ".join([str(r.get(k, "")) for k in ["title", "category", "agency", "summary"]]).lower()
        if keyword and keyword.lower() not in haystack:
            continue
        if category_filter != "전체" and r.get("category") != category_filter:
            continue
        filtered.append(r)

    if not filtered:
        st.info("표시 가능한 공개 자료가 없습니다. 비공개·관리자 전용·등록 금지 자료는 일반 사용자 화면에 표시되지 않습니다.")

    for r in filtered:
        visibility = r.get("visibility", "Private")
        kind = "public" if visibility == "Public" else "user"
        label = "공개자료" if visibility == "Public" else "로그인 사용자 공개"
        source_url = r.get("source_url", "")
        st.markdown(
            f"""
            <div class="resource-card">
                <div>{badge(esc(r.get('category', '기타')))} {badge(label, kind)}</div>
                <h3 style="margin:10px 0 4px 0;">{esc(r.get('title'))}</h3>
                <div class="muted">발행기관: {esc(r.get('agency'))} · 등록일: {esc(r.get('created_at', '')[:10])} · 최종 확인일: {esc(r.get('checked_at', ''))}</div>
                <p>{esc(r.get('summary'))}</p>
                <div class="small">공식 출처 확인 필요</div>
                {f'<a class="source-button" href="{esc(source_url)}" target="_blank" rel="noopener noreferrer">공식 출처 URL 열기</a>' if is_valid_url(source_url) else '<span class="small">유효한 공식 URL 없음</span>'}
                <div class="small" style="margin-top:10px;">본 자료는 업무 참고용이며, 정확한 내용은 공식 출처와 담당 부서에서 최종 확인하십시오.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_common_disclaimer()


def resource_request_page() -> None:
    user = current_user()
    assert user is not None
    st.markdown("# 자료 등록 요청")
    box(
        "warn",
        "파일 업로드 금지",
        "일반 사용자는 원본 파일을 업로드할 수 없습니다. 자료명, 발행기관, 공식 출처 URL, 요청 사유만 제출하십시오.\n"
        "내부 매뉴얼, 내부 공문, 시스템 화면 캡처, 유료자료, 개인정보 포함 자료는 등록 요청하지 마십시오.",
    )

    with st.form("resource_request_form"):
        title = st.text_input("자료명", max_chars=120)
        category = st.selectbox("분야", RESOURCE_CATEGORIES)
        agency = st.text_input("발행기관", max_chars=80)
        source_url = st.text_input("공식 출처 URL", placeholder="https://...")
        reason = st.text_area("요청 사유", max_chars=500)
        submitted = st.form_submit_button("자료 등록 요청", type="primary", use_container_width=True)

    if submitted:
        if not title.strip() or not agency.strip() or not source_url.strip() or not reason.strip():
            st.error("자료명, 발행기관, 공식 출처 URL, 요청 사유를 모두 입력하십시오.")
        elif not is_valid_url(source_url):
            st.error("공식 출처 URL 형식이 올바르지 않습니다.")
        else:
            requests = load_json("resource_requests", [])
            record = {
                "id": uid("req"),
                "user_id": user["user_id"],
                "title": title.strip(),
                "category": category,
                "agency": agency.strip(),
                "source_url": source_url.strip(),
                "reason": reason.strip(),
                "status": "대기",
                "admin_memo": "",
                "created_at": now_iso(),
                "processed_at": "",
                "processed_by": "",
            }
            requests.append(record)
            save_json("resource_requests", requests)
            add_audit(user["user_id"], "RESOURCE_REQUEST_CREATE", record["id"], title.strip())
            st.success("자료 등록 요청이 접수되었습니다. 관리자는 공개 가능 여부만 제한적으로 확인합니다.")

    st.markdown("### 내 요청 이력")
    mine = [r for r in load_json("resource_requests", []) if r.get("user_id") == user["user_id"]]
    if mine:
        view = pd.DataFrame(mine)[["created_at", "title", "category", "agency", "status", "admin_memo"]]
        st.dataframe(view.sort_values("created_at", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("자료 등록 요청 이력이 없습니다.")

    render_common_disclaimer()


def my_questions_page() -> None:
    user = current_user()
    assert user is not None
    st.markdown("# 내 질문 이력")
    box("info", "공개 원칙", "본인 질문만 열람할 수 있습니다. 타인의 질문 내용은 일반 사용자에게 공개되지 않습니다.")

    questions = [q for q in load_json("questions", []) if q.get("user_id") == user["user_id"] and not q.get("deleted")]
    if not questions:
        st.info("질문 이력이 없습니다.")
        return

    for q in sorted(questions, key=lambda x: x.get("created_at", ""), reverse=True):
        title = f"{q.get('created_at', '')} · {q.get('category', '')} · {q.get('status', '')}"
        with st.expander(title):
            if q.get("blocked"):
                st.warning("자동 차단된 질문입니다. 원문은 저장하지 않았습니다.")
                st.caption("차단 사유: " + ", ".join(q.get("blocked_reasons", [])))
            else:
                st.write(q.get("question", ""))
                st.text_area("AI 답변", q.get("answer", ""), height=220, disabled=True, key=f"my_ans_{q['id']}")
                if st.button("삭제 요청", key=f"delete_req_{q['id']}"):
                    all_questions = load_json("questions", [])
                    for item in all_questions:
                        if item.get("id") == q.get("id"):
                            item["status"] = "삭제요청"
                    save_json("questions", all_questions)
                    add_audit(user["user_id"], "QUESTION_DELETE_REQUEST", q["id"], "사용자 삭제 요청")
                    st.success("삭제 요청 상태로 변경했습니다. 운영 정책에 따라 처리하십시오.")
                    st.rerun()

    render_common_disclaimer()


# -----------------------------------------------------------------------------
# 관리자 화면
# -----------------------------------------------------------------------------


def admin_dashboard() -> None:
    users = load_json("users", [])
    questions = load_json("questions", [])
    resources = load_json("resources", [])
    requests = load_json("resource_requests", [])

    today = today_str()
    metrics = [
        ("가입자 수", len(users)),
        ("활성 사용자 수", sum(1 for u in users if u.get("is_active", True))),
        ("누적 질문 수", len(questions)),
        ("오늘 질문 수", sum(1 for q in questions if q.get("created_at", "").startswith(today))),
        ("자동차단 질문 수", sum(1 for q in questions if q.get("blocked"))),
        ("자료 요청 대기 수", sum(1 for r in requests if r.get("status") == "대기")),
        ("등록 자료 수", len(resources)),
        ("공개 자료 수", sum(1 for r in resources if r.get("visibility") in {"Public", "User"})),
        ("비공개 자료 수", sum(1 for r in resources if r.get("visibility") in {"Private", "Admin", "Prohibited"})),
    ]

    cols = st.columns(3)
    for idx, (label, value) in enumerate(metrics):
        with cols[idx % 3]:
            st.markdown(f"<div class='metric-card'><div class='num'>{value}</div><div class='label'>{esc(label)}</div></div>", unsafe_allow_html=True)

    if questions:
        df = pd.DataFrame(questions)
        if "category" in df:
            st.markdown("### 질문 분야 통계")
            st.bar_chart(df.groupby("category").size())


def admin_question_history() -> None:
    admin = current_user()
    assert admin is not None
    st.markdown("### 관리자 질문 이력")
    box(
        "warn",
        "관리자 열람 제한",
        "관리자는 서비스 운영, 보안 점검, 오남용 방지, 오류 확인 목적에 한해 질문 이력을 열람할 수 있습니다.\n"
        "관리자 열람 및 조작은 감사로그로 기록됩니다. 기본 화면에는 질문 원문 전체를 표시하지 않습니다.",
    )

    questions = load_json("questions", [])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        user_filter = st.text_input("사용자 아이디")
    with col2:
        category_filter = st.selectbox("질문 분야", ["전체"] + QUESTION_CATEGORIES)
    with col3:
        status_filter = st.selectbox("상태", ["전체"] + QUESTION_STATUS)
    with col4:
        blocked_filter = st.selectbox("자동차단", ["전체", "차단", "정상"])

    filtered = []
    for q in questions:
        if user_filter and user_filter.lower() not in q.get("user_id", "").lower():
            continue
        if category_filter != "전체" and q.get("category") != category_filter:
            continue
        if status_filter != "전체" and q.get("status") != status_filter:
            continue
        if blocked_filter == "차단" and not q.get("blocked"):
            continue
        if blocked_filter == "정상" and q.get("blocked"):
            continue
        filtered.append(q)

    if not filtered:
        st.info("조건에 맞는 질문 이력이 없습니다.")
        return

    summary = [
        {
            "일시": q.get("created_at"),
            "아이디": q.get("user_id"),
            "분야": q.get("category"),
            "상태": q.get("status"),
            "자동차단": "예" if q.get("blocked") else "아니오",
            "질문ID": q.get("id"),
        }
        for q in sorted(filtered, key=lambda x: x.get("created_at", ""), reverse=True)
    ]
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    st.markdown("### 원문 열람")
    for q in sorted(filtered, key=lambda x: x.get("created_at", ""), reverse=True)[:50]:
        with st.expander(f"{q.get('created_at')} · {q.get('user_id')} · {q.get('category')} · {q.get('id')}"):
            st.caption("기본 정보만 먼저 표시됩니다. 원문 보기 시 감사로그가 기록됩니다.")
            if q.get("blocked"):
                st.warning("자동차단 건입니다. 원문은 저장되지 않았으며 열람할 수 없습니다.")
                st.write("차단 사유: " + ", ".join(q.get("blocked_reasons", [])))
                continue
            purpose = st.selectbox("열람 목적", ADMIN_VIEW_PURPOSES, key=f"purpose_{q['id']}")
            reveal_key = f"reveal_{q['id']}"
            if st.button("질문 원문 보기", key=f"btn_{q['id']}"):
                st.session_state[reveal_key] = True
                add_audit(admin["user_id"], "QUESTION_ORIGINAL_VIEW", q["id"], f"목적: {purpose}")
            if st.session_state.get(reveal_key):
                st.text_area("질문 원문", q.get("question", ""), height=160, disabled=True, key=f"admin_q_{q['id']}")
                st.text_area("AI 답변", q.get("answer", ""), height=180, disabled=True, key=f"admin_a_{q['id']}")


def render_resource_guide() -> None:
    box(
        "info",
        "자료 공개 기준 안내",
        "공개 가능 자료\n"
        "- 국가법령정보센터에 공개된 법령\n"
        "- 자치법규정보시스템에 공개된 조례·규칙\n"
        "- 지자체 또는 기관 공식 홈페이지에 공개된 고시·공고·보도자료\n"
        "- 공식 홈페이지에서 누구나 열람 가능한 공개 매뉴얼\n"
        "- 출처 URL이 명확한 공개 행정자료\n"
        "- 관리자가 직접 작성한 요약문\n"
        "- 저작권 문제가 없거나 공개 이용 조건이 명확한 자료\n\n"
        "비공개 또는 제한 자료\n"
        "- 소방 내부 업무 매뉴얼, 내부 교육자료, 내부 PPT, 업무처리 편람, 내부 공문, 온나라 문서\n"
        "- 기관 내부 게시판 자료, 유료 교재, 유료 강의자료, 책자 스캔본\n"
        "- 공개 여부가 불명확하거나 최신성 확인이 필요한 자료\n\n"
        "등록 금지 자료\n"
        "- 개인정보·민감정보 포함 자료\n"
        "- 징계, 수사, 감사, 민원인 정보 포함 자료\n"
        "- 대외비, 비공개, 보안자료, 내부 시스템 화면 캡처\n"
        "- 무단 복제한 책자, 매뉴얼, 교육자료, 출처가 불명확한 파일",
    )


def admin_resource_register() -> None:
    admin = current_user()
    assert admin is not None
    st.markdown("### 관리자 자료 등록")

    left, right = st.columns([1.35, 1])
    with right:
        render_resource_guide()

    with left:
        box(
            "warn",
            "공개 전 확인",
            "공개 여부가 불명확한 자료는 공개하지 마십시오. 기본값은 비공개입니다.\n"
            "관리자는 자료의 정확성, 최신성, 적법성, 저작권 상태를 보증하지 않습니다.\n"
            "관리자는 공식 출처 존재 여부와 공개 가능 여부만 제한적으로 확인합니다.",
        )

        with st.form("resource_register_form"):
            title = st.text_input("자료명")
            category = st.selectbox("분야", RESOURCE_CATEGORIES)
            agency = st.text_input("발행기관")
            source_url = st.text_input("공식 출처 URL")
            summary = st.text_area("요약 또는 안내문", height=100)
            checked_at = st.date_input("최종 확인일", value=datetime.now())

            st.markdown("#### 공개범위 선택")
            visibility = st.radio(
                "공개범위",
                options=["Private", "User", "Public", "Admin", "Prohibited"],
                format_func=lambda x: VISIBILITY_LABELS[x],
                index=0,
            )

            checks_ok = True
            if visibility in {"Public", "User"}:
                st.markdown("##### 공개 전 필수 확인")
                c1 = st.checkbox("공식 출처 URL이 존재함을 확인했습니다.")
                c2 = st.checkbox("공개 가능한 자료임을 확인했습니다.")
                c3 = st.checkbox("개인정보·민감정보·보안자료가 아님을 확인했습니다.")
                c4 = st.checkbox("저작권 또는 내부자료 공개 문제가 낮다고 판단했습니다.")
                c5 = st.checkbox("사용자가 최종 업무처리는 담당 부서와 공식 자료로 확인해야 함을 안내합니다.")
                checks_ok = all([c1, c2, c3, c4, c5])
                non_public_reason = ""
            else:
                selected_reasons = st.multiselect("비공개 또는 등록 금지 사유", NON_PUBLIC_REASONS)
                reason_detail = st.text_area("사유 상세", height=70)
                non_public_reason = ", ".join(selected_reasons + ([reason_detail.strip()] if reason_detail.strip() else []))

            submitted = st.form_submit_button("자료 등록", type="primary", use_container_width=True)

        if submitted:
            if not title.strip() or not agency.strip() or not source_url.strip():
                st.error("자료명, 발행기관, 공식 출처 URL은 필수입니다.")
            elif not is_valid_url(source_url):
                st.error("공식 출처 URL 형식이 올바르지 않습니다.")
            elif visibility in {"Public", "User"} and not checks_ok:
                st.error("Public 또는 User 공개는 5개 확인 체크박스를 모두 선택해야 가능합니다.")
            else:
                resources = load_json("resources", [])
                record = {
                    "id": uid("res"),
                    "title": title.strip(),
                    "category": category,
                    "agency": agency.strip(),
                    "source_url": source_url.strip(),
                    "summary": summary.strip(),
                    "visibility": visibility,
                    "non_public_reason": non_public_reason,
                    "created_at": now_iso(),
                    "checked_at": checked_at.strftime("%Y-%m-%d"),
                    "created_by": admin["user_id"],
                    "updated_at": now_iso(),
                }
                resources.append(record)
                save_json("resources", resources)
                add_audit(admin["user_id"], "RESOURCE_CREATE", record["id"], f"{title.strip()} / {visibility}")
                st.success("자료가 등록되었습니다.")
                st.rerun()

        box(
            "disclaimer",
            "관리자 자료 등록 하단 문구",
            "자료 공개범위는 관리자가 반드시 직접 선택해야 합니다. 기본값은 비공개(Private)입니다. 관리자는 자료의 법적 정확성, 최신성, 완전성, 저작권 상태를 보증하지 않으며, 공식 출처 존재 여부와 공개 가능 여부만 제한적으로 확인합니다.\n"
            "공개 여부가 불명확한 자료는 공개하지 말고 비공개 또는 등록 금지로 처리하십시오.\n"
            "내부 매뉴얼, 교육자료, 책자, 유료자료, 내부 공문, 시스템 캡처 등은 저작권·보안·공개범위 문제가 있을 수 있으므로 원문 공개를 금지하거나 관리자 전용으로 제한하십시오.",
        )


def admin_resource_manage() -> None:
    admin = current_user()
    assert admin is not None
    st.markdown("### 자료 목록 및 공개범위 변경")
    resources = load_json("resources", [])

    col1, col2, col3 = st.columns(3)
    with col1:
        visibility_filter = st.selectbox("공개범위 필터", ["전체", "Public", "User", "Admin", "Private", "Prohibited"])
    with col2:
        category_filter = st.selectbox("분야 필터", ["전체"] + RESOURCE_CATEGORIES, key="res_manage_cat")
    with col3:
        keyword = st.text_input("검색", key="res_manage_search")

    filtered = []
    for r in resources:
        if visibility_filter != "전체" and r.get("visibility") != visibility_filter:
            continue
        if category_filter != "전체" and r.get("category") != category_filter:
            continue
        haystack = " ".join([str(r.get(k, "")) for k in ["title", "agency", "summary", "source_url"]]).lower()
        if keyword and keyword.lower() not in haystack:
            continue
        filtered.append(r)

    if filtered:
        table = pd.DataFrame(filtered)[
            ["created_at", "title", "category", "agency", "visibility", "checked_at", "created_by", "id"]
        ]
        st.dataframe(table.sort_values("created_at", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("자료가 없습니다.")

    for r in sorted(filtered, key=lambda x: x.get("created_at", ""), reverse=True):
        with st.expander(f"{r.get('title')} · {r.get('visibility')} · {r.get('id')}"):
            st.write("공식 출처:", r.get("source_url"))
            st.write("요약:", r.get("summary"))
            st.write("비공개/제한 사유:", r.get("non_public_reason", ""))
            new_visibility = st.selectbox(
                "공개범위 변경",
                ["Private", "User", "Public", "Admin", "Prohibited"],
                index=["Private", "User", "Public", "Admin", "Prohibited"].index(r.get("visibility", "Private")),
                format_func=lambda x: VISIBILITY_LABELS[x],
                key=f"vis_{r['id']}",
            )
            reason = st.text_input("변경 사유", key=f"vis_reason_{r['id']}")
            if st.button("공개범위 저장", key=f"save_vis_{r['id']}"):
                if new_visibility in {"Public", "User"}:
                    st.warning("Public/User 변경은 등록 화면의 5개 확인 절차를 거치는 것을 권장합니다. 이 변경도 감사로그에 기록됩니다.")
                old = r.get("visibility")
                all_resources = load_json("resources", [])
                for item in all_resources:
                    if item.get("id") == r.get("id"):
                        item["visibility"] = new_visibility
                        item["updated_at"] = now_iso()
                        if new_visibility in {"Private", "Admin", "Prohibited"} and reason.strip():
                            item["non_public_reason"] = reason.strip()
                save_json("resources", all_resources)
                add_audit(admin["user_id"], "RESOURCE_VISIBILITY_CHANGE", r["id"], f"{old} -> {new_visibility} / {reason}")
                st.success("공개범위가 변경되었습니다.")
                st.rerun()


def admin_resource_requests() -> None:
    admin = current_user()
    assert admin is not None
    st.markdown("### 자료 등록 요청 처리")
    requests = load_json("resource_requests", [])
    status_filter = st.selectbox("상태 필터", ["전체", "대기", "승인", "반려", "등록금지"])
    filtered = [r for r in requests if status_filter == "전체" or r.get("status") == status_filter]

    if filtered:
        table = pd.DataFrame(filtered)[["created_at", "user_id", "title", "category", "agency", "status", "id"]]
        st.dataframe(table.sort_values("created_at", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("자료 요청이 없습니다.")

    for req in sorted(filtered, key=lambda x: x.get("created_at", ""), reverse=True):
        with st.expander(f"{req.get('title')} · {req.get('status')} · {req.get('id')}"):
            st.write("요청자:", req.get("user_id"))
            st.write("발행기관:", req.get("agency"))
            st.write("공식 출처 URL:", req.get("source_url"))
            st.write("요청 사유:", req.get("reason"))
            memo = st.text_area("처리 메모", value=req.get("admin_memo", ""), key=f"memo_{req['id']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                approve = st.button("승인", key=f"approve_{req['id']}")
            with col2:
                reject = st.button("반려", key=f"reject_{req['id']}")
            with col3:
                prohibit = st.button("등록금지", key=f"prohibit_{req['id']}")

            if approve or reject or prohibit:
                new_status = "승인" if approve else "반려" if reject else "등록금지"
                all_requests = load_json("resource_requests", [])
                for item in all_requests:
                    if item.get("id") == req.get("id"):
                        item["status"] = new_status
                        item["admin_memo"] = memo.strip()
                        item["processed_at"] = now_iso()
                        item["processed_by"] = admin["user_id"]
                save_json("resource_requests", all_requests)
                add_audit(admin["user_id"], "RESOURCE_REQUEST_PROCESS", req["id"], f"{new_status} / {memo.strip()}")
                st.success(f"{new_status} 처리했습니다. 실제 자료 공개는 관리자 자료 등록 화면에서 기본 Private 기준으로 별도 등록하십시오.")
                st.rerun()


def admin_user_manage() -> None:
    admin = current_user()
    assert admin is not None
    st.markdown("### 회원 관리")
    users = load_json("users", [])
    keyword = st.text_input("사용자 검색")
    filtered = [u for u in users if not keyword or keyword.lower() in u.get("user_id", "").lower()]

    if filtered:
        table = pd.DataFrame(
            [
                {
                    "아이디": u.get("user_id"),
                    "권한": u.get("role"),
                    "활성": u.get("is_active"),
                    "강제로그아웃": u.get("force_logout"),
                    "가입일": u.get("created_at"),
                    "최근로그인": u.get("last_login"),
                    "관리자신청사유": u.get("admin_request_reason"),
                }
                for u in filtered
            ]
        )
        st.dataframe(table, use_container_width=True, hide_index=True)

    for u in filtered:
        with st.expander(f"{u.get('user_id')} · {u.get('role')}"):
            st.write("관리자 권한 신청 사유:", u.get("admin_request_reason", ""))
            new_role = st.selectbox("권한", ["user", "admin"], index=0 if u.get("role") == "user" else 1, key=f"role_{u['user_id']}")
            is_active = st.checkbox("활성 계정", value=u.get("is_active", True), key=f"active_{u['user_id']}")
            force_logout = st.checkbox("강제 로그아웃", value=u.get("force_logout", False), key=f"force_{u['user_id']}")
            memo = st.text_area("처리 메모", value=u.get("memo", ""), key=f"user_memo_{u['user_id']}")
            col1, col2 = st.columns(2)
            with col1:
                save = st.button("저장", key=f"save_user_{u['user_id']}")
            with col2:
                delete = st.button("완전 삭제", key=f"delete_user_{u['user_id']}")

            if save:
                all_users = load_json("users", [])
                for item in all_users:
                    if item.get("user_id") == u.get("user_id"):
                        item["role"] = new_role
                        item["is_active"] = is_active
                        item["force_logout"] = force_logout
                        item["memo"] = memo.strip()
                save_json("users", all_users)
                add_audit(admin["user_id"], "USER_UPDATE", u["user_id"], f"role={new_role}, active={is_active}, force_logout={force_logout}")
                st.success("사용자 정보가 저장되었습니다.")
                st.rerun()

            if delete:
                if u.get("user_id") == admin.get("user_id"):
                    st.error("현재 로그인한 관리자 계정은 삭제할 수 없습니다.")
                elif u.get("user_id") == "admin":
                    st.error("초기 관리자 계정은 이 화면에서 삭제하지 않는 것을 권장합니다.")
                else:
                    all_users = [item for item in load_json("users", []) if item.get("user_id") != u.get("user_id")]
                    save_json("users", all_users)
                    add_audit(admin["user_id"], "USER_DELETE", u["user_id"], "완전 삭제")
                    st.success("사용자를 삭제했습니다.")
                    st.rerun()


def admin_audit_logs() -> None:
    st.markdown("### 감사로그")
    box("info", "감사로그 원칙", "관리자 열람, 권한 변경, 자료 공개범위 변경 등 주요 작업은 감사로그로 기록됩니다. 감사로그는 관리자가 임의로 쉽게 삭제하지 못하게 설계해야 합니다.")
    logs = load_json("audit_logs", [])
    col1, col2, col3 = st.columns(3)
    with col1:
        actor = st.text_input("수행자")
    with col2:
        action = st.text_input("기능")
    with col3:
        target = st.text_input("대상")

    filtered = []
    for log in logs:
        if actor and actor.lower() not in log.get("actor", "").lower():
            continue
        if action and action.lower() not in log.get("action", "").lower():
            continue
        if target and target.lower() not in log.get("target", "").lower():
            continue
        filtered.append(log)

    if filtered:
        df = pd.DataFrame(sorted(filtered, key=lambda x: x.get("created_at", ""), reverse=True))
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("감사로그 CSV 다운로드", data=df.to_csv(index=False).encode("utf-8-sig"), file_name="audit_logs.csv", mime="text/csv")
    else:
        st.info("감사로그가 없습니다.")


def admin_notices() -> None:
    admin = current_user()
    assert admin is not None
    st.markdown("### 관리자 공지")
    with st.form("notice_form"):
        title = st.text_input("공지 제목")
        body = st.text_area("공지 내용")
        active = st.checkbox("활성", value=True)
        submitted = st.form_submit_button("공지 등록", type="primary")
    if submitted:
        if not title.strip() or not body.strip():
            st.error("제목과 내용을 입력하십시오.")
        else:
            notices = load_json("notices", [])
            record = {"id": uid("notice"), "title": title.strip(), "body": body.strip(), "is_active": active, "created_at": now_iso(), "created_by": admin["user_id"]}
            notices.append(record)
            save_json("notices", notices)
            add_audit(admin["user_id"], "NOTICE_CREATE", record["id"], title.strip())
            st.success("공지 등록 완료")
            st.rerun()

    notices = load_json("notices", [])
    for n in sorted(notices, key=lambda x: x.get("created_at", ""), reverse=True):
        with st.expander(f"{n.get('title')} · {'활성' if n.get('is_active') else '비활성'}"):
            st.write(n.get("body"))
            if st.button("활성/비활성 전환", key=f"toggle_notice_{n['id']}"):
                all_notices = load_json("notices", [])
                for item in all_notices:
                    if item.get("id") == n.get("id"):
                        item["is_active"] = not item.get("is_active")
                save_json("notices", all_notices)
                add_audit(admin["user_id"], "NOTICE_TOGGLE", n["id"], "활성 전환")
                st.rerun()


def admin_page() -> None:
    if not require_admin():
        st.error("관리자 권한이 필요합니다.")
        return

    st.markdown("# 관리자")
    tabs = st.tabs(["대시보드", "질문 이력", "자료 등록", "자료 관리", "자료 요청", "회원 관리", "감사로그", "공지"])
    with tabs[0]:
        admin_dashboard()
    with tabs[1]:
        admin_question_history()
    with tabs[2]:
        admin_resource_register()
    with tabs[3]:
        admin_resource_manage()
    with tabs[4]:
        admin_resource_requests()
    with tabs[5]:
        admin_user_manage()
    with tabs[6]:
        admin_audit_logs()
    with tabs[7]:
        admin_notices()

    render_common_disclaimer()


# -----------------------------------------------------------------------------
# 레이아웃
# -----------------------------------------------------------------------------


def sidebar_menu() -> str:
    user = current_user()
    assert user is not None

    st.sidebar.markdown(
        f"""
        <div style="padding: 8px 2px 18px 2px;">
            <div style="font-size:28px;">🚒</div>
            <div style="font-size:18px;font-weight:800;">{APP_NAME}</div>
            <div style="font-size:12px;opacity:.85;">{APP_VERSION}</div>
        </div>
        <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.16);border-radius:14px;padding:12px;margin-bottom:12px;">
            <b>{esc(user.get('user_id'))}</b><br>
            <span style="font-size:12px;">권한: {esc(user.get('role'))}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("로그아웃", key="sidebar_logout"):
        logout()

    base_menus = ["홈", "법령·조례 자료", "자료 등록 요청", "내 질문"]
    if user.get("role") == "admin":
        base_menus.append("관리자")
    menu = st.sidebar.radio("메뉴", base_menus, label_visibility="collapsed")

    st.sidebar.markdown(
        """
        <div style="margin-top:20px;background:rgba(255,255,255,0.06);border-left:4px solid #F28C6B;border-radius:10px;padding:12px;">
            <b>운영 안내</b><br>
            <span style="font-size:12px;">개인정보·민감정보·보안자료 입력 금지</span><br>
            <span style="font-size:12px;">정확한 업무처리는 담당 부서 확인</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return menu


def topbar() -> None:
    user = current_user()
    assert user is not None
    col1, col2 = st.columns([5, 1])
    with col1:
        role_label = "관리자" if user.get("role") == "admin" else "일반 사용자"
        st.markdown(
            f"""
            <div class="topbar">
                <div><b>{APP_NAME}</b> <span class="badge">{esc(role_label)}</span></div>
                <div class="muted">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("로그아웃", key="top_logout", use_container_width=True):
            logout()


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="🚒", layout="wide", initial_sidebar_state="expanded")
    init_storage()
    inject_css()

    if not current_user():
        login_page()
        return

    check_session()
    topbar()
    menu = sidebar_menu()

    if menu == "홈":
        home_page()
    elif menu == "법령·조례 자료":
        resources_page()
    elif menu == "자료 등록 요청":
        resource_request_page()
    elif menu == "내 질문":
        my_questions_page()
    elif menu == "관리자":
        admin_page()


if __name__ == "__main__":
    main()
