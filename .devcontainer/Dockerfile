FROM mcr.microsoft.com/azure-functions/python:4-python3.9-core-tools

COPY code/requirements.txt /tmp/conda-tmp/

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r /tmp/conda-tmp/requirements.txt
