# Edge Computing Infrastructure for Ag-IoT

A wiki is under development [HERE](https://git.deepaknadig.com/deepak/ec-infra-ag/-/wikis/home).

### Docker image
To build the docker image, run:
```shell script
docker build -t flask-app:latest .
``` 
To run the docker image locally:
```shell script
docker run -p 5000:5000 flask-app
``` 

### API Documentation
The API documentation is available at `<flask_endpoint>/api/v1/doc`

### Using the APIs
An example GET:
```shell script
curl --request GET \
  --url http://127.0.0.1:5000/api/v1/devices/device
```
Another GET example:
```shell script
curl --request GET \
  --url 'http://127.0.0.1:5000/api/v1/devices/2'
```
An example POST:
```shell script
curl --request POST \
  --url http://127.0.0.1:5000/api/v1/devices/device \
  --header 'content-type: application/json' \
  --data '{
  "device-id": "sens03",
  "timestamp": "1581108249.445857",
  "temperature": "54.2",
  "unit": "Fahrenheit"
}'
```
