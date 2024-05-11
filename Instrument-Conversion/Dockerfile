# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.10 as build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}

# Install the function's dependencies
RUN pip install -r ${FUNCTION_DIR}/requirements.txt --target ${FUNCTION_DIR}

# Use a slim version of the base Python image to reduce the final image size
FROM python:3.10-slim

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

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
    && curl -L http://ftp.uk.debian.org/debian/pool/main/m/musescore2/musescore_2.3.2+dfsg4-15_arm64.deb -o musescore.deb \
    && dpkg -i musescore.deb \
    && apt-get install -f -y \
    && rm musescore.deb \
    && rm -rf /var/lib/apt/lists/*

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

# Pass the name of the function handler as an argument to the runtime
CMD [ "runner.lambda_handler" ]
