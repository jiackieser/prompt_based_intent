FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

#CMD ["python3", "-m", "src.core.pipeline"]
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "info"]