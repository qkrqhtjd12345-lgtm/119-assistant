import streamlit as st
from datetime import datetime
from collections import Counter
import hashlib
import hmac
import html
import json
import os
import re
import time
import uuid
from urllib.parse import urlparse

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
APP_VERSION = "v6.0 (요구사항 정리본 반영)"
DATA_FILE = "data_store.json"
IDLE_TIMEOUT_SECONDS = 600  # 10분 자동 로그아웃

PRIMARY = "#1C3A5C"
PRIMARY_DARK = "#13283F"
ACCENT = "#2F5C82"
LIGHT_BG = "#F8F8F6"
WHITE = "#FFFFFF"
TEXT_DARK = "#263238"
TEXT_GRAY = "#667085"
BORDER = "#D9E0E3"
DANGER = "#B42318"
WARNING = "#B54708"
SUCCESS = "#027A48"

LOGO_BADGE_B64 = "__BADGE_B64__"
LOGO_EMBLEM_B64 = "__EMBLEM_B64__"

RESOURCE_CATEGORIES = ["법령", "조례", "규칙", "훈령", "예규", "지침", "매뉴얼", "감사사례", "기타"]
RESOURCE_SCOPES = ["Private", "User", "Public", "Admin", "Prohibited"]
SCOPE_LABELS = {
    "Public": "공개",
    "User": "로그인 사용자",
    "Admin": "관리자 전용",
    "Private": "비공개",
    "Prohibited": "등록 금지",
}

CATEGORY_KEYWORDS = {
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
}

BLOCK_PATTERNS = [
    (r"\b\d{6}\s*[-]?\s*\d{7}\b", "주민등록번호로 보이는 정보"),
    (r"\b01[016789][-\s]?\d{3,4}[-\s]?\d{4}\b", "휴대전화번호로 보이는 정보"),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "이메일 주소로 보이는 정보"),
    (r"\b\d{2,4}[-\s]?\d{3,4}[-\s]?\d{4}\b", "전화번호로 보이는 정보"),
    (r"대외비|비공개|보안자료|비밀|수사자료|민감정보|개인정보", "보안·비공개·개인정보 관련 표현"),
]

# ============================================================
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
