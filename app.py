import streamlit as st
import google.generativeai as genai
import random

# --- [프로 버전] 페이지 설정 ---
st.set_page_config(
    page_title="Pro AI Studio",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- [UI/UX] 모바일 최적화 CSS ---
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        padding: 15px;
        font-weight: bold;
        font-size: 18px;
        border-radius: 10px;
    }
    div[data-testid="stExpander"] details summary {
        font-weight: bold;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# --- 세션 관리 (시드값 유지) ---
if 'seed_value' not in st.session_state:
    st.session_state.seed_value = random.randint(0, 999999)

# ===========================
# 1. API 키 자동 인증 (핵심)
# ===========================
# Streamlit Cloud의 'Secrets'에서 키를 몰래 가져옵니다.
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        api_status = "✅ 인증됨 (Pro Mode)"
    else:
        api_status = "⚠️ API 키 설정 필요"
except Exception as e:
    api_status = "⚠️ 인증 오류"

# ===========================
# 2. 사이드바 (설정)
# ===========================
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    st.info(f"시스템 상태: {api_status}")
    st.divider()
    st.caption("Pro Version 1.0")

# ===========================
# 3. 메인 스튜디오
# ===========================
st.title("🎨 Pro AI Studio")
st.caption("Mobile-First Generative AI App")

st.divider()

# [A] 아이덴티티 컨트롤 (Identity Control)
st.subheader("1️⃣ 아이덴티티 (Identity Lock)")
col1, col2 = st.columns([1, 2])
with col1:
    if st.button("🎲 시드 변경"):
        st.session_state.seed_value = random.randint(0, 999999)
        st.rerun()
with col2:
    st.number_input("고유 식별 코드 (Seed)", value=st.session_state.seed_value, disabled=True)

# [B] 프롬프트 엔지니어링 (Prompting)
st.subheader("2️⃣ 디테일 설정")

# 스타일 프리셋
style_map = {
    "📸 실사 (Photorealistic)": "Photorealistic, highly detailed, 8k, realistic lighting, raw photo",
    "✨ 웹툰/애니 (Anime)": "Anime style, studio ghibli inspired, vibrant colors, clean lines",
    "🎨 수채화 (Watercolor)": "Watercolor painting, soft edges, artistic, dreamy atmosphere",
    "🌑 느와르 (Noir)": "Film noir style, high contrast, black and white, dramatic shadows"
}
selected_style_name = st.radio("화풍 선택", list(style_map.keys()), horizontal=True)

# 사용자 입력
user_prompt = st.text_area("장면 묘사 (한글 가능)", placeholder="예: 비 내리는 강남대로, 우산을 쓴 20대 여성", height=100)

# [C] 제너레이션 (Generation)
st.divider()
generate_btn = st.button("✨ 고화질 이미지 생성 (Generate)", type="primary")

if generate_btn:
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("🚨 치명적 오류: 클라우드 서버에 API 키가 설정되지 않았습니다.")
        st.info("Streamlit Cloud 설정 페이지의 [Secrets] 탭에 'GOOGLE_API_KEY'를 등록해주세요.")
    else:
        try:
            with st.spinner("AI 연산 처리 중... (GPU 가속)"):
                # 프롬프트 엔지니어링 자동화
                base_prompt = style_map[selected_style_name]
                full_prompt = f"{base_prompt}, {user_prompt}, masterpiece, best quality."
                
                # 모델 호출 (Imagen 3)
                model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                response = model.generate_images(
                    prompt=full_prompt,
                    number_of_images=1,
                    seed=st.session_state.seed_value,
                    aspect_ratio="9:16" # 모바일 최적화 비율
                )
                
                if response.images:
                    st.success("렌더링 완료!")
                    st.image(response.images[0], use_column_width=True)
                    
        except Exception as e:
            st.error(f"생성 실패: {e}")
            st.warning("팁: 구글 클라우드 결제 정보가 등록된 계정인지 확인하세요.")