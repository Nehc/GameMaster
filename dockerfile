FROM ubuntu:focal

ENV DEBIAN_FRONTEND noninteractive

LABEL maintainer="Nehcy <cibershaman@gmail.com>"
ARG NB_USER="wald"
ARG NB_UID="1000"
ARG NB_GID="100"
ARG NB_DIR="g_master"

RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends \
    python3-dev \
    python3-pip \
    build-essential \
    python-is-python3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create NB_USER with name NB_USER user with UID=1000 and in the 'users' group
#chmod g+w /etc/passwd && \

RUN useradd -l -m -s /bin/bash -N -u "${NB_UID}" "${NB_USER}" # && \
    chown "${NB_USER}:${NB_GID}" "/home/${NB_USER}/" 
 
USER "${NB_UID}"

WORKDIR "/home/${NB_USER}/"

ENV PATH="$PATH:/home/wald/.local/bin"

COPY requirements.txt ./

RUN python -m pip install --upgrade pip wheel && \
    pip install --user -r requirements.txt && \
    python -m pip cache purge

WORKDIR "./${NB_DIR}"

COPY ./g_master/ ./ 

ARG TG_TOKEN=""
ENV TG_TOKEN="${TG_TOKEN}" 

# Configure container startup: if not use compose
# if use doker standalone uncomemnt next 
#ENTRYPOINT ["python", "main.py"]
