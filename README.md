# MOEV OCPP charging system

This project is based on OCPP protocol to build up a environment to test the MOEV.inc smart charging algorithm. 

## 目录

- [Quick Start](#Quick)
  - [Python Version requirement](#Python)
  - [Operating Procedure](#operating)
- [文件目录说明](#文件目录说明)
- [开发的架构](#开发的架构)
- [部署](#部署)
- [使用到的框架](#使用到的框架)
- [贡献者](#贡献者)
  - [如何参与开源项目](#如何参与开源项目)
- [版本控制](#版本控制)

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
