FROM ubuntu:eoan
LABEL author="Deepak Nadig" \
      version="1.2" \
      description="ERGO Edge Computing APIs."

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install \
    -y --no-install-recommends build-essential python3-dev python3-virtualenv \
    python3-venv python3-pip libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev python3-setuptools \
    libblas-dev liblapack-dev libatlas3-base gfortran cython3 \
    && apt-get -y autoremove \
    && apt-get -y autoclean \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV STAGE /staging

RUN mkdir $STAGE
WORKDIR $STAGE

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install numpy --no-cache-dir --extra-index-url=https://www.piwheels.org/simple
RUN pip3 install -r requirements.txt --no-cache-dir --extra-index-url=https://www.piwheels.org/simple
RUN pip3 install redis celery flower --no-cache-dir --extra-index-url=https://www.piwheels.org/simple

# Copy the codebase
COPY app app

ENV FLASK_APP app
ENV FLASK_ENVIRONMENT development
ENV FLASK_DEBUG=1
ENV DEBUG_METRICS=false

CMD ["flask", "run", "--host=0.0.0.0"]
