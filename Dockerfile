FROM python:3.7-slim
LABEL author="Deepak Nadig" \
      version="1.2" \
      description="ERGO Edge Computing APIs."

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y libatlas3-base libgfortran5 \
    libzstd1 libjbig0 libwebpdemux2 libwebpmux3 libtiff5 libopenjp2-7 libwebp6 liblcms2-2 \
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
RUN pip install -r requirements.txt --no-cache-dir --extra-index-url=https://www.piwheels.org/simple

# Copy the codebase
COPY app app

ENV FLASK_APP app
ENV FLASK_ENVIRONMENT development
ENV FLASK_DEBUG=1
ENV DEBUG_METRICS=false

CMD ["flask", "run", "--host=0.0.0.0"]
