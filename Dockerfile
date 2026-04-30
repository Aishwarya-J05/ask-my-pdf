FROM python:3.11-slim

WORKDIR /app

# Install CPU-only PyTorch first to prevent CUDA packages
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install sentence-transformers after torch is locked to CPU
RUN pip install --no-cache-dir sentence-transformers==3.4.1

# Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

COPY . .
RUN mkdir -p data/uploads data/vectorstore logs

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]