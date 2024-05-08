FROM public.ecr.aws/lambda/python:3.10 AS builder

WORKDIR /app

# General (build-essential / libsound / libfluidsynth)
RUN apt-get update -qq && \
    apt-get install -qq libfluidsynth3 build-essential libasound2-dev libjack-dev

# Download MT3 codebase
RUN git clone --branch=main https://github.com/magenta/mt3
RUN mv mt3 mt3_tmp; mv mt3_tmp/* .; rm -r mt3_tmp

# Download MT3 dependencies
RUN python3 -m pip install jax[cuda11_local] nest-asyncio pyfluidsynth==1.3.0 -e . -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

# Fix T5X
RUN pip install git+https://github.com/jalal-elzein/t5x.git@6b02d25cd67a397c6cfffe90ad2cca4b343535ae#egg=t5x

RUN gsutil -q -m cp -r gs://mt3/checkpoints .
RUN gsutil -q -m cp gs://magentadata/soundfonts/SGM-v2.01-Sal-Guit-Bass-V1.3.sf2 .

# music21
RUN pip install music21

# MuseScore 3 & its dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:mscore-ubuntu/mscore-stable -y
RUN apt-get install musescore
RUN apt-get install xvfb

# clear the package lists cache after installing packages using the apt-get command
RUN rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .

# Run the thing??
CMD [ "runner.lambda_handler" ]