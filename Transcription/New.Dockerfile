ARG FUNCTION_DIR="/function"

FROM python:3.10 AS build

ARG FUNCTION_DIR

# copy code 
RUN mkdir -p ${FUNCTION_DIR}
COPY aws_helpers.py ${FUNCTION_DIR}
COPY midi_program_mapping.py ${FUNCTION_DIR}
COPY model.py ${FUNCTION_DIR}
COPY requirements.txt ${FUNCTION_DIR}
COPY runner.py ${FUNCTION_DIR}
COPY SGM-v2.01-Sal-Guit-Bass-V1.3.sf2 ${FUNCTION_DIR}


# install pip requirements to function_dir 
RUN pip install --no-cache-dir --target ${FUNCTION_DIR} jax[cuda11_local] nest-asyncio pyfluidsynth==1.3.0 -f https://storage.googleapis.com/jax-releases/
RUN pip install --no-cache-dir --target ${FUNCTION_DIR} git+https://github.com/jalal-elzein/t5x.git@6b02d25cd67a397c6cfffe90ad2cca4b343535ae#egg=t5x
RUN pip install --no-cache-dir --target ${FUNCTION_DIR} git+https://github.com/google/flax#egg=flax
RUN pip install --no-cache-dir -r ${FUNCTION_DIR}/requirements.txt --target ${FUNCTION_DIR}
RUN pip install --no-cache-dir --target ${FUNCTION_DIR} boto3

# Install Google Cloud SDK and gsutil
RUN apt-get update && apt-get install -y gnupg curl && rm -rf /var/lib/apt/lists/*
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && \
    apt-get install -y google-cloud-sdk && \
    rm -rf /var/lib/apt/lists/*
# Download files from Google Cloud Storage
RUN gsutil -m cp -r gs://mt3/checkpoints ${FUNCTION_DIR}

# create new image 
FROM python:3.10-slim AS final
ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}

COPY --from=build ${FUNCTION_DIR} ${FUNCTION_DIR}

# Install system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        libfluidsynth3 \
        libasound2-dev \
        libjack-dev \
        software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# Download MT3 codebase
RUN git clone --branch=main https://github.com/magenta/mt3
RUN mv mt3 mt3_tmp; mv mt3_tmp/* .; rm -r mt3_tmp

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

RUN apt-get update && \
    apt-get install -y xvfb && \
    rm -rf /var/lib/apt/lists/*

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

# Pass the name of the function handler as an argument to the runtime
CMD [ "runner.lambda_handler" ]
