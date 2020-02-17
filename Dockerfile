FROM python:3.8
LABEL maintainer="deepnadig@gmail.com"

ENV STAGE /staging

RUN mkdir $STAGE
WORKDIR $STAGE

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# We copy the rest of the codebase into the image
COPY . .

ENV FLASK_APP app
ENV FLASK_ENVIRONMENT development
ENV FLASK_DEBUG=1


CMD ["flask", "run", "--host=0.0.0.0"]