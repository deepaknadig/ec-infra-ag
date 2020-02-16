FROM python:3.8
LABEL maintainer="deepnadig@gmail.com"

ENV APP /app

RUN mkdir $APP
WORKDIR $APP

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# We copy the rest of the codebase into the image
COPY . .

CMD [ "python", "app/sensor_db_app.py" ]
