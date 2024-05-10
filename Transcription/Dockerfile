# Build stage
FROM python:3.10-slim AS build

# Install system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        libfluidsynth3 \
        libasound2-dev \
        libjack-dev \
        software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# Install Google Cloud SDK
RUN apt-get update && \
    apt-get install -y curl apt-transport-https ca-certificates gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && \
    apt-get install -y google-cloud-sdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment and install Python packages
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir jax[cuda11_local] nest-asyncio pyfluidsynth==1.3.0 -e . -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
RUN pip install git+https://github.com/jalal-elzein/t5x.git@6b02d25cd67a397c6cfffe90ad2cca4b343535ae#egg=t5x
RUN pip install music21

# Final stage
FROM python:3.10-slim AS final

# Install AWS Lambda Runtime Interface Client
RUN pip install awslambdaric

# Copy the virtual environment from the build stage
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Download MT3 codebase
RUN git clone --branch=main https://github.com/magenta/mt3
RUN mv mt3 mt3_tmp; mv mt3_tmp/* .; rm -r mt3_tmp

# gs://magentadata/soundfonts/SGM-v2.01-Sal-Guit-Bass-V1.3.sf2 is downloaded locally

# Download files from Google Cloud Storage
RUN gsutil -q -m cp -r gs://mt3/checkpoints .

# Install MuseScore
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:mscore-ubuntu/mscore-stable -y && \
    apt-get install -y musescore && \
    rm -rf /var/lib/apt/lists/*

# Install Xvfb
RUN apt-get update && \
    apt-get install -y xvfb && \
    rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .

# Set runtime interface client as default command for the container runtime
ENTRYPOINT ["/usr/local/bin/python", "-m", "awslambdaric"]

# Point to Lambda function handler
CMD [ "runner.lambda_handler" ]
