FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV PYTHONUNBUFFERED=1
EXPOSE 7860
CMD ["python", "-c", "from src.suivi_pret.ui_gradio import lancer_application; lancer_application()"]
