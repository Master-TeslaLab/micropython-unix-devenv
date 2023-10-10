# micropython-unix-devenv

Micropython Unix Development Environment Docker Image

## Description
This docker image is a development environment for latest Micropython at unix machines. It is based on Ubuntu 22.04 and contain all the tools needed to build and run Micropython unix port. It also contains latest official Micropython libaries that are not builtin. In case of test or develop & deboug code for embeded devices easily, this image will be useful. 

## Alternative
Micropython unix port is also available as a snap package. The official micropython libaries are also available with mip Micropython builtin module. When your target device is connected to the internet, you can use mip.install() to install any official libary. https://docs.micropython.org/en/latest/reference/packages.html

## Files
    Dockerfile              Dockerfile to build the image
    sample.py               Sample code to test Micropython execution
    README.md               This file
    sample_lib_build.log    Sample log file generated during build. 
                            When libaries are not functioning properly, this file can be used to debug the issue.

## Installation
    Install Docker
    docker pull masterteslalab/micropython-unix-devenv

## Usage examples 

### Micropython REPL
Micropython supports REPL. REPL is started by default when no arguments are passed to docker run command. To exit REPL press `Ctrl+D` or type `exit()`

    docker run -it --rm masterteslalab/micropython-unix-devenv

### Sample Code execution
    docker run -it --rm masterteslalab/micropython-unix-devenv ../micropython-unix-devenv/sample.py

### User defined code execution
    docker run -it --rm -v {LOCAL WORKSPACE}:/workspace masterteslalab/micropython-unix-devenv {main.py or user .py file}

### User defined code execution with REPL
    docker run -it --rm -v {LOCAL WORKSPACE}:/workspace masterteslalab/micropython-unix-devenv -i {main.py or user .py file}

### Attach to container
    docker run -it --rm --entrypoint /bin/bash masterteslalab/micropython-unix-devenv
