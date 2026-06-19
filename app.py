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
# 🔐 보안: 비밀번호 해싱
# ========================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ========================================
# 세션 초기화
# ========================================
if "users" not in st.session_state:
    st.session_state.users = {
        "qhtjd0611": {
            "password_hash": hash_password("kyn04228@@"),
            "role": "admin",
            "name": "최고관리자",
            "created_at": "2024-01-01"
        }
    }

if "login_user" not in st.session_state:
    st.session_state.login_user = None

if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

if "faq_counts" not in st.session_state:
    st.session_state.faq_counts = {
        "병가": 0, "공가": 0, "초과근무": 0,
        "e사람": 0, "온나라": 0, "e호조": 0,
        "법령": 0, "조례": 0,
    }

# ========================================
# 🎨 색상 (남색 + 아이보리)
# ========================================
NAVY = "#1C3A5C"
LIGHT_BG = "#F8F8F6"
WHITE = "#FFFFFF"
TEXT_DARK = "#333333"
TEXT_GRAY = "#666666"
BORDER_GRAY = "#DDDDDD"

# ========================================
# CSS 스타일
# ========================================
st.markdown(f"""
<style>
    * {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', '나눔고딕', sans-serif;
    }}

    .stApp {{
        background-color: {LIGHT_BG};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {NAVY};
    }}

    section[data-testid="stSidebar"] * {{
        color: {WHITE} !important;
    }}

    section[data-testid="stSidebar"] .stRadio > label {{
        color: {WHITE} !important;
        font-weight: 600;
        padding: 12px 14px;
        border-radius: 8px;
        transition: all 0.2s ease;
        margin-bottom: 6px;
    }}

    section[data-testid="stSidebar"] .stRadio > label:hover {{
        background-color: rgba(255, 255, 255, 0.1);
    }}

    section[data-testid="stSidebar"] .stRadio > label[aria-selected="true"] {{
        background-color: rgba(255, 255, 255, 0.2);
        font-weight: 700;
    }}

    .info-box {{
        background: {WHITE};
        border: 1px solid {BORDER_GRAY};
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}

    .info-box-title {{
        color: {NAVY};
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid {NAVY};
    }}

    .info-box-content {{
        color: {TEXT_DARK};
        font-size: 14px;
        line-height: 1.6;
    }}

    .stButton > button {{
        background-color: {NAVY};
        color: {WHITE};
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }}

    .stButton > button:hover {{
        background-color: #162844;
        box-shadow: 0 2px 6px rgba(28, 58, 92, 0.3);
    }}

    div[data-testid="stTextInput"] input {{
        border: 1px solid {BORDER_GRAY} !important;
        border-radius: 6px !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
    }}

    div[data-testid="stTextInput"] input:focus {{
        border-color: {NAVY} !important;
        box-shadow: 0 0 0 2px rgba(28, 58, 92, 0.1) !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        border-bottom: 1px solid {BORDER_GRAY};
    }}

    .stTabs [data-baseweb="tab-list"] button {{
        font-weight: 600;
        color: {TEXT_GRAY};
        border-bottom: 2px solid transparent;
    }}

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        color: {NAVY};
        border-bottom-color: {NAVY};
    }}

    .badge {{
        display: inline-block;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }}

    .badge-pending {{
        background: #FFF3CD;
        color: #856404;
    }}

    .badge-approved {{
        background: #D4EDDA;
        color: #155724;
    }}

    .user-info {{
        background: {WHITE};
        border: 1px solid {BORDER_GRAY};
        border-radius: 8px;
        padding: 16px;
        margin-top: 20px;
    }}

    .user-info-label {{
        color: {TEXT_GRAY};
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 4px;
    }}

    .user-info-value {{
        color: {TEXT_DARK};
        font-weight: 700;
        font-size: 15px;
    }}
</style>
""", unsafe_allow_html=True)

# ========================================
# 로그인 페이지
# ========================================
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 40px 0;">
            <img src="file:///mnt/user-data/outputs/chungnam_logo.png" style="max-width: 300px; margin-bottom: 20px;">
            <div style="font-size: 20px; font-weight: 700; color: {TEXT_DARK}; margin-bottom: 8px;">
                충남119 복무AI
            </div>
            <div style="font-size: 14px; color: {TEXT_GRAY};">
                충남 소방공무원을 위한 업무 정보 안내 서비스
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["로그인", "회원가입"])
        
        with tab1:
            st.markdown("### 로그인")
            user_id = st.text_input("아이디", placeholder="아이디 입력", key="login_id")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력", key="login_pw")
            
            if st.button("로그인", use_container_width=True, key="btn_login"):
                if not user_id or not password:
                    st.error("아이디와 비밀번호를 입력하세요.")
                elif user_id in st.session_state.users:
                    stored_hash = st.session_state.users[user_id]["password_hash"]
                    input_hash = hash_password(password)
                    
                    if stored_hash == input_hash:
                        st.session_state.login_user = user_id
                        st.success("로그인 성공!")
                        st.rerun()
                    else:
                        st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.error("존재하지 않는 아이디입니다.")
        
        with tab2:
            st.markdown("### 회원가입")
            new_id = st.text_input("새 아이디", placeholder="6자 이상", key="new_id")
            new_pw = st.text_input("새 비밀번호", type="password", placeholder="6자 이상", key="new_pw")
            
            if st.button("회원가입", use_container_width=True, key="btn_signup"):
                if not new_id or not new_pw:
                    st.warning("모든 항목을 입력하세요.")
                elif len(new_id) < 6 or len(new_pw) < 6:
                    st.warning("아이디와 비밀번호는 6자 이상이어야 합니다.")
                elif new_id in st.session_state.users:
                    st.error("이미 사용 중인 아이디입니다.")
                else:
                    st.session_state.users[new_id] = {
                        "password_hash": hash_password(new_pw),
                        "role": "user",
                        "name": new_id,
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.success("회원가입이 완료되었습니다. 로그인해주세요.")


# ========================================
# 함수들
# ========================================
def get_role():
    user = st.session_state.login_user
    return st.session_state.users[user]["role"]


def is_admin():
    return get_role() == "admin"


def classify_question(q: str):
    q = q.lower()
    categories = {
        "병가": ["병가"], "공가": ["공가"], "초과근무": ["초과", "시간외"],
        "e사람": ["e사람", "이사람"], "온나라": ["온나라"],
        "e호조": ["e호조", "이호조", "예산", "지출"],
        "법령": ["법", "법령"], "조례": ["조례"]
    }
    
    for category, keywords in categories.items():
        if any(keyword in q for keyword in keywords):
            return category
    return "기타"


# ========================================
# 홈 페이지
# ========================================
def home_page():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-box-title">질문하기</div>
            <div class="info-box-content">
                복무규정, 병가, 공가, 초과근무 등 일상 업무 중 궁금한 사항을 편하게 물어보세요.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        question = st.text_input(
            "무엇이 궁금하신가요?",
            placeholder="예: 당직근무 중 병가를 쓰면 어떻게 처리해?",
            label_visibility="collapsed"
        )
        
        if question:
            category = classify_question(question)
            if category in st.session_state.faq_counts:
                st.session_state.faq_counts[category] += 1
            
            st.markdown(f"""
            <div class="info-box">
                <div class="info-box-title">✅ 답변</div>
                <div class="info-box-content">
                    <strong>분류:</strong> {category}<br><br>
                    🔄 현재 <strong>Gemini API 연동 작업 중</strong>입니다.<br>
                    다음 업데이트에서 실시간 AI 답변이 제공될 예정입니다.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="info-box">
                <div class="info-box-title">📚 관련 법령</div>
                <div class="info-box-content">
                    • 공무원 복무규정<br>
                    • 지방공무원 복무규정<br>
                    • 충청남도 공무원 복무 조례
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="info-box" style="border-left: 4px solid #FF6B6B;">
                <div style="color: #FF6B6B; font-weight: 700;">⚠️ 주의</div>
                기관별 운영 차이가 있을 수 있으므로 최종 확인은 소속 복무담당자와 협의하시기 바랍니다.
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-box-title">인기 질문</div>
            <div class="info-box-content">
        """, unsafe_allow_html=True)
        
        sorted_faq = sorted(st.session_state.faq_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (name, count) in enumerate(sorted_faq[:5], 1):
            if count > 0:
                st.markdown(f"#{i} {name} ({count})")
        
        st.markdown("</div></div>", unsafe_allow_html=True)


# ========================================
# 법령·조례 페이지
# ========================================
def law_page():
    st.markdown(f"""
    <div class="info-box">
        <div class="info-box-title">📚 법령·조례·매뉴얼</div>
        <div class="info-box-content">
            현재 시스템이 참고하는 공식 자료들입니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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


# ========================================
# 건의사항 페이지
# ========================================
def suggestion_page():
    st.markdown(f"""
    <div class="info-box">
        <div class="info-box-title">💬 자료 신청</div>
        <div class="info-box-content">
            필요한 법령, 조례, 매뉴얼을 신청하실 수 있습니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("suggestion_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("자료 제목")
        with col2:
            category = st.selectbox("자료 종류", ["법령", "조례", "지침", "매뉴얼", "기타"])
        
        content = st.text_area("신청 사유", height=100)
        file = st.file_uploader("파일 첨부 (선택)", type=["pdf", "doc", "docx"])
        
        if st.form_submit_button("신청 제출", use_container_width=True):
            if not title:
                st.error("제목을 입력하세요.")
            else:
                st.session_state.suggestions.append({
                    "id": len(st.session_state.suggestions) + 1,
                    "title": title,
                    "category": category,
                    "content": content,
                    "file_name": file.name if file else "첨부 없음",
                    "status": "승인대기",
                    "user": st.session_state.login_user,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("신청이 완료되었습니다.")
    
    st.markdown("---")
    st.markdown("### 내 신청 목록")
    
    my_items = [x for x in st.session_state.suggestions if x["user"] == st.session_state.login_user]
    
    if not my_items:
        st.info("신청한 자료가 없습니다.")
    else:
        for item in my_items:
            st.markdown(f"""
            <div class="info-box">
                <strong>{item['title']}</strong><br>
                <span style="color: {TEXT_GRAY}; font-size: 13px;">
                    {item['category']} | {item['file_name']} | {item['date']}
                </span><br>
                <span class="badge badge-{'approved' if item['status'] == '승인완료' else 'pending' if item['status'] == '승인대기' else 'rejected'}">
                    {item['status']}
                </span>
            </div>
            """, unsafe_allow_html=True)


# ========================================
# 관리자 페이지
# ========================================
def admin_page():
    st.markdown(f"""
    <div class="info-box">
        <div class="info-box-title">🔐 자료 신청 관리</div>
        <div class="info-box-content">
            총 {len(st.session_state.suggestions)}건 중 {len([x for x in st.session_state.suggestions if x['status'] == '승인대기'])}건이 대기 중입니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.suggestions:
        st.info("신청 자료가 없습니다.")
        return
    
    for i, item in enumerate(st.session_state.suggestions):
        st.markdown(f"""
        <div class="info-box">
            <strong>{item['title']}</strong><br>
            <span style="color: {TEXT_GRAY}; font-size: 13px;">
                신청자: {item['user']} | {item['category']} | {item['date']}
            </span><br>
            <span class="badge badge-{'approved' if item['status'] == '승인완료' else 'pending' if item['status'] == '승인대기' else 'rejected'}">
                {item['status']}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("승인", key=f"approve_{i}", use_container_width=True):
                st.session_state.suggestions[i]["status"] = "승인완료"
                st.rerun()
        
        with col2:
            if st.button("반려", key=f"reject_{i}", use_container_width=True):
                st.session_state.suggestions[i]["status"] = "반려"
                st.rerun()
        
        with col3:
            if st.button("보류", key=f"hold_{i}", use_container_width=True):
                st.session_state.suggestions[i]["status"] = "보류"
                st.rerun()
        
        with col4:
            if st.button("대기", key=f"pending_{i}", use_container_width=True):
                st.session_state.suggestions[i]["status"] = "승인대기"
                st.rerun()


# ========================================
# 메인 실행
# ========================================
if st.session_state.login_user is None:
    login_page()
else:
    # 상단 헤더
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 16px 0; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 20px;">
            <img src="file:///mnt/user-data/outputs/chungnam_logo.png" style="max-width: 200px;">
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div style="padding: 16px 28px; background: {WHITE}; border-bottom: 1px solid {BORDER_GRAY}; margin: -16px -16px 28px -16px;">
            <div style="font-size: 18px; font-weight: 700; color: {TEXT_DARK};">
                충남119 복무AI
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("로그아웃", use_container_width=True):
            st.session_state.login_user = None
            st.rerun()
    
    # 네비게이션
    menu_list = ["홈", "법령·조례", "건의·신청"]
    if is_admin():
        menu_list.append("관리자")
    
    selected_menu = st.sidebar.radio("메뉴", menu_list, index=0)
    
    # 페이지 라우팅
    if selected_menu == "홈":
        home_page()
    elif selected_menu == "법령·조례":
        law_page()
    elif selected_menu == "건의·신청":
        suggestion_page()
    elif selected_menu == "관리자":
        admin_page()
    
    # 우측 사이드바 (로그인 정보)
    st.sidebar.markdown("---")
    user_info = st.session_state.users[st.session_state.login_user]
    st.sidebar.markdown(f"""
    <div class="user-info">
        <div class="user-info-label">현재 사용자</div>
        <div class="user-info-value">{st.session_state.login_user}</div>
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid {BORDER_GRAY};">
            <div class="user-info-label">권한</div>
            <div class="user-info-value">{'관리자' if is_admin() else '일반사용자'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 푸터
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: {TEXT_GRAY}; font-size: 12px; padding: 20px 0;">
        <p><strong>충남119 복무AI</strong> v3.0</p>
        <p>충남소방본부 | {datetime.now().strftime('%Y년 %m월 %d일')}</p>
    </div>
    """, unsafe_allow_html=True)
