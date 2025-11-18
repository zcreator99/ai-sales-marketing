import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="AI Data Analyst", page_icon="📊")
st.title("📊 Trợ lý Phân tích Sales & Marketing AI")

# --- CẤU HÌNH API KEY ---
# Thay thế 'YOUR_API_KEY' bằng API Key thực tế của bạn
# Tốt nhất là nên nhập trực tiếp trên giao diện để bảo mật
api_key = st.sidebar.text_input("", type="password")

def configure_ai(api_key):
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

# --- HÀM ĐỌC DỮ LIỆU ---
def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")
        return None

# --- HÀM GỌI AI PHÂN TÍCH ---
def analyze_data_with_ai(df, prompt_request):
    # Chuyển đổi 1 phần dữ liệu thành text để gửi cho AI (tránh gửi quá lớn)
    # Lấy 50 dòng đầu tiên và thông tin cột để tiết kiệm token
    data_preview = df.head(50).to_markdown(index=False)
    data_info = df.dtypes.to_markdown()
    
    full_prompt = f"""
    Bạn là một chuyên gia phân tích dữ liệu Sales & Marketing.
    Dưới đây là dữ liệu mẫu (50 dòng đầu) và cấu trúc dữ liệu:
    
    {data_preview}
    
    Thông tin kiểu dữ liệu:
    {data_info}
    
    Yêu cầu phân tích: {prompt_request}
    
    Hãy đưa ra các insight (nhận định) sâu sắc, xu hướng và đề xuất hành động cụ thể.
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Lỗi khi gọi AI: {e}"

# --- GIAO DIỆN CHÍNH ---
uploaded_file = st.file_uploader("Tải lên file CSV hoặc Excel đã clean", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # 1. Đọc và hiển thị dữ liệu
    df = load_data(uploaded_file)
    
    if df is not None:
        st.write("### 1. Xem trước dữ liệu")
        st.dataframe(df.head())
        st.write(f"Kích thước dữ liệu: {df.shape[0]} dòng, {df.shape[1]} cột")

        # 2. Khu vực nhập câu hỏi cho AI
        st.write("---")
        st.write("### 2. Phân tích với AI")
        
        user_question = st.text_area(
            "Bạn muốn AI phân tích điều gì?",
            "Hãy phân tích xu hướng doanh số theo thời gian và đề xuất các chiến dịch Marketing phù hợp cho các sản phẩm bán chạy nhất."
        )
        
        if st.button("🚀 Bắt đầu phân tích"):
            if not api_key:
                st.warning("Vui lòng nhập API Key ở thanh bên trái trước!")
            else:
                if configure_ai(api_key):
                    with st.spinner("AI đang đọc dữ liệu và suy nghĩ..."):
                        result = analyze_data_with_ai(df, user_question)
                        st.success("Phân tích hoàn tất!")
                        st.markdown(result)
