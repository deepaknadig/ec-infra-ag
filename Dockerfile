FROM python:3.8-slim
LABEL author="Deepak Nadig" \
      version="1.2" \
      description="ERGO Edge Computing APIs."

ENV STAGE /staging

RUN mkdir $STAGE
WORKDIR $STAGE

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Copy the codebase
COPY app app

ENV FLASK_APP app
ENV FLASK_ENVIRONMENT development
ENV FLASK_DEBUG=1
ENV DEBUG_METRICS=false

CMD ["flask", "run", "--host=0.0.0.0"]
