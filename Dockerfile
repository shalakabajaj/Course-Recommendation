# 1. Use official Python image
FROM python:3.10-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Copy requirements file
COPY requirements.txt .

# 4. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy project files
COPY . .

# 6. Expose Streamlit default port
EXPOSE 8501

# 7. Run Streamlit app
CMD ["streamlit", "run", "frontend_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
