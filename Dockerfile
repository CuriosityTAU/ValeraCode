# syntax=docker/dockerfile:1
FROM jupyter/scipy-notebook

USER root
RUN sudo apt-get update
RUN sudo apt-get install -y i2c-tools gpiod libgpiod-dev

RUN usermod -a -G root,video,i2c,sudo jovyan
USER 1000
RUN pip install gpiod smbus2 opencv-python solara pygame
#USER 1000
