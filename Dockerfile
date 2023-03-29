FROM python:3.9-slim-buster
LABEL maintainer="Nicole Guittari"
LABEL version="0.2.0"
LABEL description="A Docker image for running the Python version of ndio with RAMON Updates"
RUN apt-get update
RUN apt-get -y install gcc
WORKDIR /app
RUN pip install poetry
COPY poetry.lock .
COPY pyproject.toml .
RUN poetry install
RUN pip install numpy 
RUN pip install blosc 
RUN pip install ndio
RUN pip install git+https://github.com/aplbrain/mossDB
COPY . .
EXPOSE 8000
CMD ["poetry", "run", "flask", "-A", "ndio.main:app", "run", "--host=0.0.0.0"]