# Build stage
FROM public.ecr.aws/lambda/python:3.10 as download-build-stage

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install Python packages
RUN python3 -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Install system packages
RUN yum install -y gcc gcc-c++ make automake cmake git && \
    git clone https://git.ffmpeg.org/ffmpeg.git && \
    cd ffmpeg && \
    ./configure --disable-yasm && \
    make && \
    make install && \
    cd .. && \
    rm -rf ffmpeg && \
    yum remove -y gcc gcc-c++ make automake cmake git && \
    yum clean all

# Final stage
FROM public.ecr.aws/lambda/python:3.10

# Copy the installed packages from the build stage
COPY --from=download-build-stage ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD ["lamdbda_function.lambda_handler"]