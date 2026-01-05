# 使用官方 Python 基础镜像 (建议使用 slim 版本减小体积，但 Playwright 需要很多依赖)
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，防止 Python 生成 .pyc 文件，并让输出直接打印到日志
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统基础依赖 (Playwright 需要的一些底层库)
# 也可以直接使用 mcr.microsoft.com/playwright:v1.40.0-jammy 这样的官方镜像，那就不用自己安装了
# 这里为了演示完整过程，我们手动安装
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 的浏览器和系统依赖
# install-deps 会安装 Linux 缺少的库 (如 libgtk 等)
RUN playwright install chromium
RUN playwright install-deps chromium

# 复制项目代码
COPY . .

# 暴露 Streamlit 默认端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
