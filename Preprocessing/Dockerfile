ARG FUNCTION_DIR="/function"

FROM python:3.10 as preproc-build 

ARG FUNCTION_DIR

COPY lambda_function.py ${FUNCTION_DIR}/lambda_function.py

RUN pip install pedalboard boto3 awslambdaric --no-cache-dir --target ${FUNCTION_DIR}

FROM python:3.10-slim

ARG FUNCTION_DIR

WORKDIR ${FUNCTION_DIR}

COPY --from=preproc-build ${FUNCTION_DIR} ${FUNCTION_DIR}

RUN apt-get update && apt-get install ffmpeg -y

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

CMD [ "lambda_function.lambda_handler" ]