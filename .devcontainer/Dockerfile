FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

ENV PYTHONUNBUFFERED 1

# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

#[Optional] Uncomment this section to install additional OS packages.
# Note we do not install chromium-driver that is done by selenium on demand
# and we also remove the one installed by the chromium package
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends chromium \
    && rm /usr/bin/chromedriver

# RUN export CHROMEVER=$(chromium --product-version | awk "{print $2}") && \
#     wget -q --continue -P /tmp "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROMEVER/linux64/chromedriver-linux64.zip" && \
#     unzip /tmp/chromedriver* -d /tmp && \
#     mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/



