FROM python:3.11-bullseye

WORKDIR /app

# no chromium-driver
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends chromium 
    
COPY . ./

RUN python -m pip install -rrequirements.txt

CMD ["python",  "-m", "coffeescraper"]
