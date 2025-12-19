import streamlit as st
from google import genai
from google.genai import types
import random

# --- [프로 버전] 페이지 설정 ---
st.set_page_config(
    page_title="Pro AI Studio",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 스타일 설정 ---
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        padding: 15px;
        font-weight: bold;
        font-size: 18px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 세션 관리 ---
if 'seed_value' not in st.session_state:
    st.session_state.seed_value = random.randint(0, 999999)

# ===========================
# 1. API 키 인증 (신형 SDK)
# ===========================
client = None
api_status = "⚠️ 연결 대기 중"

try:
    if "GOOGLE_API_KEY" in st.secrets:
        # [핵심] 신형 라이브러리 초기화 방식
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        api_status = "✅ 인증됨 (New GenAI SDK)"
    else:
        api_status = "⚠️ API 키 없음"
except Exception as e:
    api_status = f"❌ 인증 오류: {e}"

# ===========================
# 2. 사이드바
# ===========================
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    st.info(f"상태: {api_status}")
    st.caption("Powered by Google GenAI SDK 1.0")

# ===========================
# 3. 메인 스튜디오
# ===========================
st.title("🎨 Pro AI Studio")
st.caption("Imagen 3 최신 모델 구동 중")

st.divider()

# [A] 시드 설정
col1, col2 = st.columns([1, 2])
with col1:
    if st.button("🎲 시드 변경"):
        st.session_state.seed_value = random.randint(0, 999999)
        st.rerun()
with col2:
    st.number_input("Seed Code", value=st.session_state.seed_value, disabled=True)

# [B] 프롬프트 설정
style_map = {
    "📸 실사 (Photorealistic)": "Photorealistic, highly detailed, 8k, realistic lighting",
    "✨ 웹툰 (Anime)": "Anime style, studio ghibli inspired, vibrant colors",
    "🎨 수채화 (Watercolor)": "Watercolor painting, soft edges, artistic",
}
selected_style = st.radio("화풍 선택", list(style_map.keys()), horizontal=True)
user_prompt = st.text_area("장면 묘사", placeholder="예: 우산을 쓴 20대 여성, 비 내리는 도시", height=100)

# [C] 생성 버튼
st.divider()
if st.button("✨ 고화질 생성 (Generate)", type="primary"):
    if not client:
        st.error("API 키 오류: Secrets 설정을 확인해주세요.")
    else:
        try:
            with st.spinner("Imagen 3 모델이 그리는 중... (약 10초)"):
                full_prompt = f"{style_map[selected_style]}, {user_prompt}"
                
                # [핵심] 신형 라이브러리 이미지 생성 코드
                response = client.models.generate_images(
                    model='imagen-3.0-generate-001',
                    prompt=full_prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        seed=st.session_state.seed_value,
                        aspect_ratio="9:16"
                    )
                )
                
                # 결과 표시
                if response.generated_images:
                    image = response.generated_images[0].image
                    st.image(image, use_container_width=True)
                    st.success("완성!")
                    
        except Exception as e:
            st.error(f"생성 실패: {e}")
            if "403" in str(e) or "quota" in str(e):
                st.warning("팁: 구글 클라우드 결제 정보가 없거나 무료 한도가 초과되었을 수 있습니다.")
