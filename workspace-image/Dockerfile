# syntax=docker/dockerfile:1
# Build for PrairieLearn with:  docker build --platform linux/amd64 ...
ARG BASE_IMAGE=ubuntu:22.04

############ stage 1: compile the programs students will debug ############
FROM ${BASE_IMAGE} AS build
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev make && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/challenge
COPY challenge/ .
# Edit to match your sources (Checkpoint's runtime.setup_commands equivalent,
# but run once at build time instead of on every start).
RUN gcc -g -O0 -o demo demo.c

############ stage 2: the runtime image (no compiler, no editor) ############
FROM ${BASE_IMAGE}
ENV DEBIAN_FRONTEND=noninteractive
# gdb-minimal is built without Python scripting, so gdb's `python` command is absent.
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-venv gdb-minimal util-linux && \
    rm -rf /var/lib/apt/lists/*

# PrairieLearn runs workspaces as UID 1001 in production, so everything the
# server needs must be readable by "other" and nothing may require root.
RUN useradd -m -u 1001 -s /usr/sbin/nologin student && chmod 755 /home/student
WORKDIR /opt/terminal
RUN python3 -m venv /opt/venv
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY server.py launcher.py index.html ./
COPY gdb/ /opt/gdb/
COPY --from=build /opt/challenge /opt/challenge
RUN chown -R root:root /opt/terminal /opt/gdb /opt/challenge /opt/venv && \
    chmod -R a+rX,go-w /opt/terminal /opt/gdb /opt/challenge /opt/venv && \
    find / -xdev -perm /6000 -type f -exec chmod a-s {} + 2>/dev/null || true

# What PrairieLearn needs to know about a custom workspace image
LABEL com.prairielearn.workspace.port="8080" \
      com.prairielearn.workspace.rewrite-url="true" \
      com.prairielearn.workspace.home="/home/student"

# Checkpoint's runtime.program_args: what gdb opens (a JSON list).
ENV PROGRAM_ARGS='["/opt/challenge/demo"]'
# 0 = start the debuggee without a shell (strict). Set to 1 if your lab needs
# `run < input.txt` or `run $(python3 -c ...)`; see README.
ENV GDB_RUN_USES_SHELL=0

EXPOSE 8080
ENTRYPOINT ["/opt/venv/bin/python", "-u", "server.py", "--port", "8080", "--uid", "1001", "--gid", "1001", "--home", "/home/student", "--gdb-scripts", "/opt/gdb"]
