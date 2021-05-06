# MOEV OCPP charging system

This project is based on OCPP protocol to build up a environment to test the MOEV.inc smart charging algorithm. 

### Quick Start
1. Before run this server, you should:  import websockets, asyncio, json, os

2. set server ip address and port id in main function, for example :'132.148.83.34', 9000

3. server can reveive the command come from clients.

4. server can send command to clients. you can test all the functions

5. You could use http API to control the charging process.


###### Python Version requirement

Python 3.6 above is needed

###### **Operating Procedure**

1. Run the central system codes firstly
```python
python3 centralsystem.py
```
2. Run the charge points codes individually

```python
python3 chargepoint.py
```
3. If you want to run some specific functions while charging, use the api file.  [HTTP API](#API)

### Set IP address of central system
Find the create_websocket_server function in central system codes and change the ip address and port number you decided.
```python
async def create_websocket_server(csms: CentralSystem):
    handler = partial(on_connect, csms=csms)
    return await websockets.serve(handler, "0.0.0.0", 9000, subprotocols=["ocpp1.6"])
```
Also, because we use the HTTP API to control the charging process, also change the port number in create_http_server function:
```python
async def create_http_server(csms: CentralSystem):
    ...
    site = web.TCPSite(runner, "localhost", 8080)
    return site
```
Please remember that http_server and websocket_server should have different port number

### API 

Here is an example of a CSMS that can can be controlled using an HTTP API. The HTTP API has 2 endpoints:
 - POST / - to change configuration for all connected chargers. It excepts a JSON body with the fields key and value.
 - POST /disconnect - to disconnect a charger. It expects a JSON body with the field id that contains the charger ID.
 - POST /remotestart - to trigger remote_start_transcation function to control the begining of charging process. It expects a JSON body with the field id that contains the charger ID.
 - POST /remotestop - to trigger remote_stop_transcation function to control the end of charging process. It expects a JSON body with the field id that contains the charger ID.
 - POST /setmaxvalue - to set the maxmium value of charging power(unit:A, Watts). It expects a JSON body with the field id that contains the charger ID and max value. 

The HTTP server is running at port 8080. Here a few CURL examples:

**Change config**
```http
$ curl --header "Content-Type: application/json"\
  --request POST \ 
  --data '{"key":"MeterValueSampleInterval","value":"10"}'\
  http://localhost:8080/changeconfig
```
**Disconnect Charger**
```http
$ curl --header "Content-Type: application/json"\
  --request POST \ 
  --data '{"key":"MeterValueSampleInterval","value":"10"}'\
  http://localhost:8080/changeconfig
```
**Remote start charging**
```http
$ curl --header "Content-Type: application/json"\
  --request POST\
  --data '{"id":"CP_1"}'\
  http://localhost:8080/remotestart
```
**Remote stop charging**
```http
$ curl --header "Content-Type: application/json"\
  --request POST\
  --data '{"id":" CP_1"}'\
  http://localhost:8080/remotestop
```
**Set the maxmium value of charging power**
```http
$ curl --header "Content-Type: application/json"\
  --request POST\
  --data '{"id":" CP_1", "limit":"8"}'\
  http://localhost:8080/setmaxvalue
```


### File catalog
eg:

```
MOEV 
├── LICENSE.txt
├── README.md
├── /example/
│  ├── /centralsystem.py/
│  ├── /chargepoint.py/
│  ├── /chargepoint2.py/
│  ├── /httpapi.http/
├── /ocpp/
│  ├── /v16/
│  |  ├── /schemas/
│  |  ├── /__init__.py/
│  |  ├── /call_result.py/
│  |  ├── /call.py/
│  |  ├── /enums.py/
│  ├── /charge_point.py/
│  ├── /exceptions.py/
│  ├── /messaage.py/
│  ├── /routing.py.py/
└── /util/

```
