from ubuntu:22.04
MAINTAINER Youngjin Song

RUN apt update -y \
    && apt install -y git build-essential libffi-dev pkg-config python3.10-dev \
    && ln -s /usr/bin/python3.10 /usr/bin/python3

WORKDIR /
RUN git clone https://github.com/micropython/micropython.git
RUN git clone https://github.com/Master-TeslaLab/micropython-unix-devenv.git

# Build micropython for unix
WORKDIR /micropython/ports/unix
RUN latestTag=$(git describe --tags --abbrev=0) && git reset --hard $latestTag
RUN make submodules && make
RUN ln -s /micropython/ports/unix/micropython /usr/bin/micropython

# Build micropython-lib for unix
WORKDIR /micropython-unix-devenv
RUN python3 lib_build.py

RUN mkdir /workspace
WORKDIR /workspace

ENTRYPOINT ["./micropython"]