FROM python:3.8

WORKDIR /app

RUN pip install --upgrade pip

# Avoid rebuilding this step if no changes to requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy everything in the container
# This expects the models submodule to be present
COPY . .

EXPOSE 5000
ENTRYPOINT [ "python", "main.py", "--host", "0.0.0.0" ]
