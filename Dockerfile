FROM python:3.9.6
WORKDIR /app
COPY auditor.py .
CMD ["python", "auditor.py"]
