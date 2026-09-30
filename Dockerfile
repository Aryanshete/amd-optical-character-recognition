FROM rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:$PYTHONPATH

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ocr /app/ocr
COPY app.py /app/app.py

RUN mkdir -p /app/output /app/input /models && chmod -R 777 /app/output

CMD ["python3", "/app/app.py"]
