FROM python:3.8-slim

RUN apt-get -y update && \
    apt-get -y dist-upgrade && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


RUN adduser --disabled-password --gecos '' appuser
USER appuser

COPY src/ src/
RUN pip install -r src/requirements.txt


WORKDIR /src
CMD ["python", "main.py"]]
