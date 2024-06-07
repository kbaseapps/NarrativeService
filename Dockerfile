FROM python:3.12-slim
LABEL MAINTAINER="KBase Developer"
# -----------------------------------------
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
WORKDIR /kb/module

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

ENV PYTHONPATH="/kb/module/lib:$PYTHONPATH"

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
