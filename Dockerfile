FROM python:3.13-slim

# 设置国内pip镜像源
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /app

# 设置时区
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 复制requirements文件并安装依赖 - 完全无需系统依赖
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/_manage/health || exit 1

CMD ["sh", "-c", "sleep 5 && python init_db.py && python run.py"]
