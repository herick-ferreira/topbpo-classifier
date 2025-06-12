FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivo de dependências primeiro (para cache do Docker)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p uploads processed

# Define permissões
RUN chmod -R 755 uploads processed

# Expõe a porta que a aplicação vai usar
EXPOSE 8080

# Define variáveis de ambiente
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Comando para iniciar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]