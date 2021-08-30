FROM gcr.io/dataflow-templates-base/python3-template-launcher-base

RUN mkdir -p /dataflow/template
WORKDIR /dataflow/template

COPY ./pipeline/main.py /dataflow/template/main.py

ENV FLEX_TEMPLATE_PYTHON_PY_FILE="/dataflow/template/main.py"

RUN pwd
RUN ls -a
RUN python -m pip install --upgrade pip
RUN pip install apache-beam[gcp]==2.31.0