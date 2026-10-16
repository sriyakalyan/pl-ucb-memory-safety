ARG BASE_IMAGE=ubuntu:22.04
FROM ${BASE_IMAGE}

# Extra apt packages students should have, space separated (e.g. "git nano gdb")
ARG PACKAGES=""

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-venv ${PACKAGES} && \
    rm -rf /var/lib/apt/lists/*

# Terminal server lives outside the student's home and is not readable by them
WORKDIR /terminal_runtime
RUN python3 -m venv /opt/venv
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY server.py index.html ./
RUN chmod -R go-rwx /terminal_runtime

RUN useradd -m -s /bin/bash student

# Optional behaviour, override with `docker build --build-arg` or in info.json
ENV TERMINAL_PROGRAM="bash"
ENV TERMINAL_SETUP=""

ENTRYPOINT ["/opt/venv/bin/python", "-u", "server.py", "--port", "8080", "--user", "student", "--workdir", "/home/student"]
