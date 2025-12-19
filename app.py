import streamlit as st
from google import genai
from google.genai import types

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

# ===========================
# 1. API 키 인증
# ===========================
client = None
api_status = "⚠️ 연결 대기 중"

try:
    if "GOOGLE_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        api_status = "✅ 인증됨 (Pro Mode)"
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
    st.divider()
    st.caption("Imagen 3 Model (Public API)")

# ===========================
# 3. 메인 스튜디오
# ===========================
st.title("🎨 Pro AI Studio")
st.caption("터치로 만드는 고화질 이미지")

st.divider()

# [A] 프롬프트 및 스타일 설정
st.subheader("1️⃣ 스타일 선택")

style_map = {
    "📸 실사 (Photorealistic)": "Photorealistic, highly detailed, 8k, realistic lighting, raw photo",
    "✨ 웹툰 (Anime)": "Anime style, studio ghibli inspired, vibrant colors, clean lines",
    "🎨 수채화 (Watercolor)": "Watercolor painting, soft edges, artistic, dreamy atmosphere",
}
selected_style = st.radio("화풍을 선택하세요", list(style_map.keys()), horizontal=True)

st.subheader("2️⃣ 장면 묘사")
user_prompt = st.text_area("그림 내용을 입력하세요 (한글 가능)", placeholder="예: 우산을 쓴 20대 여성, 비 내리는 도시", height=100)

# [B] 생성 버튼
st.divider()
if st.button("✨ 고화질 생성 (Generate)", type="primary"):
    if not client:
        st.error("API 키 오류: Secrets 설정을 확인해주세요.")
    else:
        try:
            with st.spinner("이미지를 생성하고 있습니다... (약 10초)"):
                # 프롬프트 조합
                full_prompt = f"{style_map[selected_style]}, {user_prompt}"
                
                # [수정됨] seed 옵션을 제거하여 에러 방지
                response = client.models.generate_images(
                    model='imagen-3.0-generate-001',
                    prompt=full_prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio="9:16" # 모바일 비율
                    )
                )
                
                # 결과 표시
                if response.generated_images:
                    image = response.generated_images[0].image
                    st.image(image, use_container_width=True)
                    st.success("완성! 이미지를 길게 눌러 저장하세요.")
                    
        except Exception as e:
            st.error(f"생성 실패: {e}")
            if "403" in str(e):
                st.warning("결제 정보가 등록되지 않았거나, 무료 사용량이 초과되었습니다.")
