import streamlit as st
import os
import shutil
from scrape_insta import scrape_instagram

st.set_page_config(page_title="Instagram Downloader", page_icon="📸")

st.title("📸 Instagram Media Downloader")
st.markdown("输入 Instagram 帖子链接，提取并下载高清图片和视频。")

# Input URL
url = st.text_input("Instagram Post URL", placeholder="https://www.instagram.com/p/...")

# Options
col1, col2 = st.columns(2)
with col1:
    download_btn = st.button("开始提取", type="primary", use_container_width=True)
with col2:
    cleanup_btn = st.button("清理历史文件", use_container_width=True)

if cleanup_btn:
    if os.path.exists("downloads"):
        shutil.rmtree("downloads")
        os.makedirs("downloads")
        st.toast("已清理历史文件！", icon="🗑️")

if download_btn and url:
    if "instagram.com" not in url:
        st.error("请输入有效的 Instagram 链接")
    else:
        with st.status("正在提取中...", expanded=True) as status:
            st.write("启动浏览器...")
            try:
                # Call the scraper
                st.write("正在导航并解析媒体...")
                downloaded_files = scrape_instagram(url, download=True)
                
                if downloaded_files:
                    status.update(label="提取完成!", state="complete", expanded=False)
                    st.success(f"成功提取 {len(downloaded_files)} 个文件!")
                    
                    # Display files
                    st.divider()
                    st.subheader("预览与下载")
                    
                    cols = st.columns(min(3, len(downloaded_files)))
                    
                    for i, file_path in enumerate(downloaded_files):
                        file_name = os.path.basename(file_path)
                        col_idx = i % 3
                        
                        with cols[col_idx]:
                            if file_path.endswith(".jpg") or file_path.endswith(".png"):
                                st.image(file_path, use_container_width=True)
                            elif file_path.endswith(".mp4"):
                                st.video(file_path)
                            
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label=f"下载文件 {i+1}",
                                    data=f,
                                    file_name=file_name,
                                    mime="image/jpeg" if file_path.endswith(".jpg") else "video/mp4",
                                    key=f"dl_{i}"
                                )
                else:
                    status.update(label="提取失败", state="error")
                    st.warning("未找到媒体文件，或者帖子可能涉及隐私/限制。")
            
            except Exception as e:
                status.update(label="发生错误", state="error")
                st.error(f"Error: {str(e)}")

elif download_btn:
    st.warning("请输入链接")

# Footer
st.divider()
st.markdown("""
<small>
注意：本工具仅供学习交流使用。请尊重版权，不要下载或分发未经授权的内容。<br>
工具原理：使用 Playwright 模拟浏览器访问并拦截媒体流。
</small>
""", unsafe_allow_html=True)
