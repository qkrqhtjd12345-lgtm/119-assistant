import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="충남119 복무AI",
    page_icon="🚒",
    layout="wide"
)

# -------------------------
# 임시 저장소
# 나중에는 DB로 바꿀 예정
# -------------------------
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "119", "role": "admin"}
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
    }


# -------------------------
# 디자인
# -------------------------
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #d71920;
}
.sub-title {
    font-size: 18px;
    color: #555;
    margin-bottom: 25px;
}
.card {
    padding: 18px;
    border-radius: 14px;
    background-color: #f8f9fa;
    border: 1px solid #e5e5e5;
    margin-bottom: 15px;
}
.status-pending {color:#d99a00; font-weight:700;}
.status-approved {color:#16803c; font-weight:700;}
.status-rejected {color:#d71920; font-weight:700;}
.status-hold {color:#0066cc; font-weight:700;}
</style>
""", unsafe_allow_html=True)


# -------------------------
# 로그인 / 회원가입
# -------------------------
def login_page():
    st.markdown('<div class="main-title">🚒 충남119 복무AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">충남 소방공무원을 위한 복무·행정 AI 안내 서비스</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["로그인", "회원가입"])

    with tab1:
        user_id = st.text_input("아이디", key="login_id")
        password = st.text_input("비밀번호", type="password", key="login_pw")

        if st.button("로그인"):
            if user_id in st.session_state.users and st.session_state.users[user_id]["password"] == password:
                st.session_state.login_user = user_id
                st.success("로그인 성공")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 맞지 않습니다.")

    with tab2:
        new_id = st.text_input("새 아이디", key="new_id")
        new_pw = st.text_input("새 비밀번호", type="password", key="new_pw")

        if st.button("가입하기"):
            if not new_id or not new_pw:
                st.warning("아이디와 비밀번호를 입력하세요.")
            elif new_id in st.session_state.users:
                st.error("이미 존재하는 아이디입니다.")
            else:
                st.session_state.users[new_id] = {
                    "password": new_pw,
                    "role": "user"
                }
                st.success("가입 완료. 로그인해주세요.")


def get_role():
    user = st.session_state.login_user
    return st.session_state.users[user]["role"]


def logout_button():
    col1, col2 = st.columns([8, 1])
    with col1:
        st.write(f"👤 로그인 사용자: **{st.session_state.login_user}** / 권한: **{get_role()}**")
    with col2:
        if st.button("로그아웃"):
            st.session_state.login_user = None
            st.rerun()


# -------------------------
# 질문 분류
# -------------------------
def classify_question(q):
    q = q.lower()

    if "병가" in q:
        return "병가"
    if "공가" in q:
        return "공가"
    if "초과" in q or "시간외" in q:
        return "초과근무"
    if "e사람" in q or "이사람" in q:
        return "e사람"
    if "온나라" in q:
        return "온나라"
    if "e호조" in q or "이호조" in q or "예산" in q or "지출" in q:
        return "e호조"

    return "기타"


def status_text(status):
    if status == "승인대기":
        return '<span class="status-pending">🟡 승인대기</span>'
    if status == "승인완료":
        return '<span class="status-approved">🟢 승인완료</span>'
    if status == "반려":
        return '<span class="status-rejected">🔴 반려</span>'
    if status == "보류":
        return '<span class="status-hold">🔵 보류</span>'
    return status


# -------------------------
# 홈
# -------------------------
def home_page():
    st.markdown('<div class="main-title">🚒 충남119 복무AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">충남 소방공무원을 위한 복무·행정 AI 안내 서비스</div>', unsafe_allow_html=True)

    st.info("홈 화면입니다. 복무, 병가, 공가, 초과근무, e사람, 온나라, e호조 사용법을 질문할 수 있습니다.")

    question = st.text_input(
        "무엇이 궁금하신가요?",
        placeholder="예) 당비비 근무 중 15시에 병가를 사용하면 어떻게 처리하나요?"
    )

    if question:
        category = classify_question(question)

        if category in st.session_state.faq_counts:
            st.session_state.faq_counts[category] += 1

        st.markdown("### ✅ 답변")
        st.write("아직 AI 연결 전입니다. 다음 단계에서 Gemini API를 연결하면 실제 답변이 생성됩니다.")

        st.markdown("### 📚 근거 조항")
        st.warning("현재는 테스트 단계입니다. 실제 운영 시 법령명, 조문, 시행일을 반드시 표시하도록 설정할 예정입니다.")

        st.markdown("### ⚠ 주의사항")
        st.write("기관별 운영 차이가 있을 수 있으므로 최종 확인은 소속 복무담당자에게 필요합니다.")

    st.markdown("---")
    st.markdown("### 🔥 자주 묻는 질문 TOP 5")

    sorted_faq = sorted(
        st.session_state.faq_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for i, (name, count) in enumerate(sorted_faq[:5], start=1):
        st.write(f"{i}. **{name}**")


# -------------------------
# 법령·조례·매뉴얼
# -------------------------
def law_page():
    st.header("📚 법령·조례·매뉴얼")
    st.info("현재 충남119 복무AI가 참고하는 법령, 조례, 지침, 매뉴얼 목록을 확인하는 공간입니다.")

    st.markdown("### 현재 등록된 자료")

    data = [
        ["법령", "공무원 복무규정", "준비중"],
        ["법령", "지방공무원 복무규정", "준비중"],
        ["조례", "충청남도 공무원 복무 조례", "준비중"],
        ["매뉴얼", "e사람 사용 매뉴얼", "준비중"],
        ["매뉴얼", "온나라 사용 매뉴얼", "준비중"],
        ["매뉴얼", "e호조 사용 매뉴얼", "준비중"],
    ]

    st.table(data)


# -------------------------
# 건의사항
# -------------------------
def suggestion_page():
    st.header("💬 건의사항")
    st.info("누락된 법령, 조례, 매뉴얼, 업무자료를 등록 요청하는 공간입니다. 관리자 승인 후 사이트에 반영됩니다.")

    title = st.text_input("자료 제목")
    category = st.selectbox("자료 종류", ["법령", "조례", "지침", "매뉴얼", "감사사례", "기타"])
    content = st.text_area("요청 내용")
    file = st.file_uploader("PDF 파일 첨부", type=["pdf"])

    if st.button("등록 요청"):
        if not title:
            st.warning("자료 제목을 입력하세요.")
        else:
            st.session_state.suggestions.append({
                "title": title,
                "category": category,
                "content": content,
                "file_name": file.name if file else "첨부 없음",
                "status": "승인대기",
                "user": st.session_state.login_user,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success("등록 요청이 완료되었습니다.")

    st.markdown("---")
    st.markdown("### 내 요청 목록")

    for item in st.session_state.suggestions:
        if item["user"] == st.session_state.login_user:
            st.markdown(
                f"""
                <div class="card">
                <b>{item['title']}</b><br>
                종류: {item['category']}<br>
                파일: {item['file_name']}<br>
                상태: {status_text(item['status'])}<br>
                등록일: {item['date']}
                </div>
                """,
                unsafe_allow_html=True
            )


# -------------------------
# 관리자
# -------------------------
def admin_page():
    st.header("🔐 관리자")
    st.info("관리자 전용 공간입니다. 자료 승인, 반려, 보류 처리와 사용자 권한 관리를 할 수 있습니다.")

    if get_role() != "admin":
        st.error("관리자 권한이 없습니다.")
        return

    st.markdown("### 자료 승인 관리")

    if not st.session_state.suggestions:
        st.write("승인 요청 자료가 없습니다.")

    for i, item in enumerate(st.session_state.suggestions):
        st.markdown(
            f"""
            <div class="card">
            <b>{item['title']}</b><br>
            요청자: {item['user']}<br>
            종류: {item['category']}<br>
            파일: {item['file_name']}<br>
            내용: {item['content']}<br>
            상태: {status_text(item['status'])}<br>
            등록일: {item['date']}
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("승인완료", key=f"approve_{i}"):
                st.session_state.suggestions[i]["status"] = "승인완료"
                st.rerun()

        with col2:
            if st.button("반려", key=f"reject_{i}"):
                st.session_state.suggestions[i]["status"] = "반려"
                st.rerun()

        with col3:
            if st.button("보류", key=f"hold_{i}"):
                st.session_state.suggestions[i]["status"] = "보류"
                st.rerun()

        with col4:
            if st.button("승인대기", key=f"pending_{i}"):
                st.session_state.suggestions[i]["status"] = "승인대기"
                st.rerun()

    st.markdown("---")
    st.markdown("### 사용자 권한 관리")

    for user_id, info in st.session_state.users.items():
        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            st.write(user_id)

        with col2:
            st.write(info["role"])

        with col3:
            if user_id != "admin":
                if info["role"] == "user":
                    if st.button("관리자 부여", key=f"make_admin_{user_id}"):
                        st.session_state.users[user_id]["role"] = "admin"
                        st.rerun()
                else:
                    if st.button("일반사용자 변경", key=f"make_user_{user_id}"):
                        st.session_state.users[user_id]["role"] = "user"
                        st.rerun()


# -------------------------
# 실행
# -------------------------
if st.session_state.login_user is None:
    login_page()
else:
    logout_button()

    menu_list = ["🏠 홈", "📚 법령·조례·매뉴얼", "💬 건의사항"]

    if get_role() == "admin":
        menu_list.append("🔐 관리자")

    menu = st.sidebar.radio("메뉴", menu_list)

    if menu == "🏠 홈":
        home_page()
    elif menu == "📚 법령·조례·매뉴얼":
        law_page()
    elif menu == "💬 건의사항":
        suggestion_page()
    elif menu == "🔐 관리자":
        admin_page()
