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

# Create a virtual environment and install Python packages
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install --no-cache-dir jax[cuda11_local] nest-asyncio pyfluidsynth==1.3.0 -f https://storage.googleapis.com/jax-releases/
RUN pip install --no-cache-dir git+https://github.com/jalal-elzein/t5x.git@6b02d25cd67a397c6cfffe90ad2cca4b343535ae#egg=t5x
RUN pip install --no-cache-dir music21 awslambdaric

# Final stage
FROM python:3.10-slim AS final

# Copy the virtual environment from the build stage
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        libfluidsynth3 \
        libasound2-dev \
        libjack-dev \
        software-properties-common && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Download MT3 codebase
RUN git clone --branch=main https://github.com/magenta/mt3
RUN mv mt3 mt3_tmp; mv mt3_tmp/* .; rm -r mt3_tmp

# Install Google Cloud SDK and gsutil
RUN apt-get update && apt-get install -y gnupg curl && rm -rf /var/lib/apt/lists/*
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && \
    apt-get install -y google-cloud-sdk && \
    rm -rf /var/lib/apt/lists/*

# Download files from Google Cloud Storage
RUN gsutil -q -m cp -r gs://mt3/checkpoints .

# Sync time
RUN apt-get update && apt-get install -y tzdata \
    && dpkg-reconfigure tzdata \
    && apt-get install -y curl 

# Install required packages for adding repositories
RUN apt-get update && apt-get install -y software-properties-common

# Install required dependencies
RUN apt-get update && apt-get install -y \
    libasound2 \
    libfreetype6 \
    libportaudio2 \
    libportmidi0 \
    libpulse0 \
    libqt5core5a \
    libqt5gui5 \
    libqt5help5 \
    libqt5network5 \
    libqt5printsupport5 \
    libqt5qml5 \
    libqt5quick5 \
    libqt5svg5 \
    libqt5widgets5 \
    libqt5xml5 \
    libqt5xmlpatterns5 \
    libsndfile1 \
    libvorbisfile3 \
    desktop-file-utils \
    fonts-freefont-ttf \
    qml-module-qtquick-controls \
    qml-module-qtquick-dialogs \
    qml-module-qtquick-layouts \
    qml-module-qtquick2 \
    xdg-utils \
    musescore-common \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Add the repository and install musescore
RUN apt-get update && apt-get install -y curl \
    && curl -L http://ftp.uk.debian.org/debian/pool/main/m/musescore2/musescore_2.3.2+dfsg4-15_amd64.deb -o musescore.deb \
    && dpkg -i musescore.deb \
    && apt-get install -f -y \
    && rm musescore.deb \
    && rm -rf /var/lib/apt/lists/*

# Install Xvfb
RUN apt-get update && \
    apt-get install -y xvfb && \
    rm -rf /var/lib/apt/lists/*

RUN pip install awslambdaric
RUN python -c "import awslambdaric; print('awslambdaric module is installed')" 

COPY . .

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

# Point to Lambda function handler
CMD [ "runner.lambda_handler" ]