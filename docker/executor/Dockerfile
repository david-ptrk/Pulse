# Compile Pulse's native libraries separately so GCC is not included
# in the final execution image.
FROM python:3.14-slim AS native-builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/pulse/native

COPY native/ ./

RUN sh build.sh


# Runtime image
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/pulse

COPY docker/executor/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY . /opt/pulse

COPY --from=native-builder /opt/pulse/bin/ /opt/pulse/bin/

# Unprivileged execution identity.
USER 65534:65534

CMD ["python", "--version"]
