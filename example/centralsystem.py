import asyncio
import logging

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)

import asyncio   
import json
import os
import sys
sys.path.append('..')
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from aiohttp import web
from functools import partial
from datetime import datetime

from ocpp.v16 import call
from ocpp.v16 import call_result
from ocpp.v16.enums import (Action, AuthorizationStatus, AvailabilityType,
                   ChargingProfileKindType, ChargingProfilePurposeType,
                   ChargingRateUnitType, ClearCacheStatus, DataTransferStatus,
                   RecurrencyKind, RegistrationStatus, RemoteStartStopStatus,
                   ResetType, UpdateType)
from ocpp.routing import after, on
logging.basicConfig(level=logging.INFO)

class ChargePoint(cp):                     # chargePoint class

    # 1
    @on(Action.BootNotification)           #  BootNotification function
    def on_boot_notification(self, **kwargs):
        response = call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )

        return response


    # 2
    @on(Action.Authorize)  #
    def on_authorize_notification(self, **kwargs):
        response = call_result.AuthorizePayload(
            id_tag_info={'expiryDate': datetime.utcnow().isoformat(),
                         'parentIdTag': 'MOEV.inc',                  # Optional. This contains the parent-identifier.
                         'status': AuthorizationStatus.accepted    # Required. This contains whether the idTag has been accepted or not by the Central System.
                         }
        )
        return response


    # 3
    @on(Action.Heartbeat)  #
    def on_heartbeat_notification(self, **kwargs):
        response= call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
        )
        return response


    # 4
    @on(Action.StartTransaction)  #
    def on_start_transaction_notification(self, **kwargs):

        response = call_result.StartTransactionPayload(
            transaction_id=1,  # Required. This contains the transaction id supplied by the Central System.
            id_tag_info={'expiryDate': datetime.now().isoformat(),  #Required. This contains information about authorization status, expiry and parent id.
                         'parentIdTag': 'MOEV.inc',
                         'status': AuthorizationStatus.accepted}
        )
        return response


    # 5
    @on(Action.StopTransaction)  
    def on_stop_transaction_notification(self, **kwargs):
        response = call_result.StopTransactionPayload(

            id_tag_info={'expiryDate': datetime.utcnow().isoformat(),
                         'parentIdTag': 'MOEV,inc',
                         'status': AuthorizationStatus.accepted}
        )

        return response

    # 6
    @on(Action.MeterValues)  
    def on_meter_values_notification(self, **kwargs):
        response = call_result.MeterValuesPayload(
        )
        return response

    # 7
    @on(Action.StatusNotification)  
    def on_status_notification(self, **kwargs):
        response = call_result.StatusNotificationPayload(
        )
        return response


    # 8   from GUI / special cp
    @on(Action.DataTransfer)
    async def on_data_transfer_notification(self, **kwargs):
        vendor_id = kwargs["vendor_id"]
        # print(vendor_id)
        message_id = kwargs["message_id"]
        # print(message_id)
        data = kwargs["data"]               # data type is <class 'str'>

        data_dict = json.loads(data)           #  <class 'dict'>


        cp_id = max_watts = cp_select = None
        if vendor_id == "MOEV_GUI":
            print("EVSE_dict is ", EVSE_dict)
            # get the cp instance
            if data_dict.get("cp_id"):
                cp_id = data_dict["cp_id"]
                # print("cp_id from GUI is", cp_id)
                cp_select = EVSE_dict[cp_id]
                # print("cp_select is", cp_select)
            if data_dict.get("max_watts"):
                max_watts = data_dict["max_watts"]
                # print("max_watts is", max_watts)
            if data_dict.get("max_current"):
                max_current = data_dict["max_current"]
                # print("max_current is", max_current)


            ######## different command different function
            if message_id == "show current evses":
                response = call_result.DataTransferPayload(
                    status=DataTransferStatus.accepted,
                    data=str(EVSE_dict.keys())
                )
                return response

            elif message_id == "start remote transaction":

                await cp_select.send_remote_start_transaction()

                response = call_result.DataTransferPayload(
                    status=DataTransferStatus.accepted,
                    data="we accepted the start remote transaction request, the evse is: %s" % cp_id
                )
                return response

            elif message_id == "stop remote transaction":
                await cp_select.send_remote_stop_transaction()

                response = call_result.DataTransferPayload(
                    status=DataTransferStatus.accepted,
                    data="we accepted the stop remote transaction request, the evse is: %s" % cp_id
                )
                return response

            elif message_id == "clear charging profile":
                await cp_select.clear_charging_profile()

                response = call_result.DataTransferPayload(
                    status=DataTransferStatus.accepted,
                    data="we accepted the clear charging profile request"
                )
                return response

            elif message_id == "change max_watts":
                limit = max_watts

                await cp_select.set_charging_profile(limit)

                response = call_result.DataTransferPayload(
                    status=DataTransferStatus.accepted,
                    data="we accepted the change max watts request"
                )
                return response

        elif vendor_id == "< MOEV_MANUFACTURER >":
            connector_id = data_dict["connectorId"]
            print(connector_id)
            pay_session_id = data_dict["paySessionId"]
            print(pay_session_id)
            auth_data = data_dict["authData"]
            print(auth_data)
            timestamp = data_dict["timestamp"]
            print(timestamp)

            if message_id =="AuthorizedPayment.req":

                response = call_result.DataTransferPayload(
                    status=DataTransferStatus.accepted,
                    data=str({"status": "CreditCardAuthorizationStatus"})
                )
                return response


#   send from server :
    # 1
    async def send_clear_cache_request(self):
        request = call.ClearCachePayload(

        )
        response = await self.call(request)
        print(response.__dict__)


        if response.status == ClearCacheStatus.accepted:
            print("3.we can Clear cache")
        elif response.status == ClearCacheStatus.rejected:
            print("3.client rejected to clear cache")

    # 2
    async def send_remote_start_transaction(self):
        print("1.hello, remote start transaction request send to client")
        request = call.RemoteStartTransactionPayload(
            id_tag="transaction1"
        )
        response = await self.call(request)

        if response.status == RemoteStartStopStatus.accepted:
            print("3.we can remote start transaction")
            print("cp -> server, send_remote_start_transaction is:\n", response, "\n")
            await self.set_charging_profile(limit=100)
        elif response.status == RemoteStartStopStatus.rejected:
            print("3.client rejected remote start transaction")
        

    # 3
    async def send_remote_stop_transaction(self):
        print("1.hello, remote stop transaction request send to client")
        request = call.RemoteStopTransactionPayload(
            transaction_id=111
        )
        print("server -> cp , send_remote_stop_transaction: \n", request, "\n")

        response = await self.call(request)

        print("cp -> server, send_remote_stop_transaction: \n", response, "\n")
        if response.status == RemoteStartStopStatus.accepted:
            print("3.we can remote stop transaction")
        elif response.status == RemoteStartStopStatus.rejected:
            print("3.client rejected remote stop transaction")

    # 4
    async def set_charging_profile(self, limit):  #after "start transcation" or "remote start transcation"
        request = call.SetChargingProfilePayload(
            connector_id=1,            # The connector to which the charging profile applies. If connectorId = 0, the message contains an overall limit for the Charge Point.
            cs_charging_profiles={
                "chargingProfileId": 1,
                "transactionId":1,      #Optional
                "stackLevel":1,
                "chargingProfilePurpose": ChargingProfilePurposeType.chargepointmaxprofile,
                "chargingProfileKind": ChargingProfileKindType.absolute,
                "recurrencyKind": RecurrencyKind.daily,   # optional
                "chargingSchedule":{
                    "duration":600,                       # Optional. Duration of the charging schedule in seconds
                    "startSchedule": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z",
                    "chargingRateUnit": ChargingRateUnitType.amps,
                    "chargingSchedulePeriod":[{
                        "startPeriod": 0 ,
                        "limit": limit,    #  Charging rate limit during the schedule period, in the applicable chargingRateUnit, for example in Amperes or Watts. Accepts at most one digit fraction (e.g. 8.1).
                        "numberPhases":3
                    }],
                    "minChargingRate":2.1,
                }
            }
        )
        response = await self.call(request)
        print(response.status)


        


    # 5
    async def clear_charging_profile(self):
        request = call.ClearChargingProfilePayload(
            id=1,                        # Optional. The ID of the charging profile to clear.
            connector_id= 1,    # Optional. Specifies the ID of the connector for which to clear
                                # charging profiles. A connectorId of zero (0) specifies the charging
                                # profile for the overall Charge Point. Absence of this parameter
                                # means the clearing applies to all charging profiles that match the
                                # other criteria in the request.
            charging_profile_purpose = ChargingProfilePurposeType.txdefaultprofile,   #Optional. Specifies to purpose of the charging profiles that will be
                                                                                      #cleared, if they meet the other criteria in the request.
            stack_level=1,    #Optional. specifies the stackLevel for which charging profiles will be cleared, if they meet the other criteria in the request
        )

        response = await self.call(request)
        print("clear_charging_profile response is ", response)

    # 6
    async def cancel_reservation(self):
        request = call.CancelReservationPayload(
            reservation_id=1,  #Required. Id of the reservation to cancel
        )

        response = await self.call(request)
        print("cancel_reservation response is ", response)

    #7
    async def change_availability(self):
        request = call.ChangeAvailabilityPayload(
            connector_id=0 ,   #Required. The id of the connector for which availability needs to change. Id '0'
                               # (zero) is used if the availability of the Charge Point and all its connectors needs
                               # to change.
            type= AvailabilityType.inoperative   # Required. This contains the type of availability change that the Charge Point should perform.
        )

        response = await self.call(request)
        print("change available response is", response)

    #8
    async def get_configuration(self):
        request = call.GetConfigurationPayload(
            key= ["max_current", "min_current", "max_power", "min_power"]      #Optional. List of keys for which the configuration value is requested.
        )
        response = await self.call(request)
        print("get configuration response is", response)

    #9
    async def change_configuration(self, key_set:str , value_set:str ):
        request = call.ChangeConfigurationPayload(
            key= key_set,  #Required. The name of the configuration setting to change. See for standard configuration key names and associated values
            value = value_set,      #Required. The new value as string for the setting. See for standard configuration key names and associated values
        )
        response = await self.call(request)
        print("change configuration response is", response)

    #10
    async def data_transfer(self):
        request =call.DataTransferPayload(
            vendor_id="MOEV",   #Required. This identifies the Vendor specific implementation
            message_id= "001",  #Optional. Additional identification field
            data = "hi???????", #Optional. Data without specified length or format.
        )
        response = await self.call(request)
        print("data transfer response is ", response)

    #11
    async def get_local_list_version(self):
        request = call.GetLocalListVersionPayload(
        )

        response = await self.call(request)
        print("get local list version response is ", response)

    #12
    async def send_local_list(self):
        request = call.SendLocalListPayload(
            list_version=2,     #Required. In case of a full update this is the version number of the full list.
                                # In case of a differential update it is the version number of the list after the update has been applied.
            local_authorization_list=[
                {"idTag":"001",
                 "idTagInfo":{
                     "expiryDate": "2020-12-12T00:00:00.792735",  #Optional. This contains the date at which idTag should be removed from the Authorization Cache.
                     "parentIdTag": "002",                        #Optional. This contains the parent-identifier.
                     "status":AuthorizationStatus.accepted,       #Required. This contains whether the idTag has been accepted or not by the Central System.
                    }
                 },
                {"idTag": "003",
                 "idTagInfo": {
                     "expiryDate": "2020-12-12T00:00:00.792735",
                     "parentIdTag": "004",
                     "status": AuthorizationStatus.accepted,
                    }
                 },
            ],
            update_type= UpdateType.full  #Required. This contains the type of update (full or differential) of this request.
        )
        response = await self.call(request)
        print("send local list response is ",response)

    #13
    async def reset(self):
        request = call.ResetPayload(
            type= ResetType.hard   #Required. This contains the type of reset that the Charge Point should perform
        )

        response = await self.call(request)
        print("reset response is ",response)

    #14
    async def unlock_connector(self):
        request =call.UnlockConnectorPayload(
            connector_id= 1,   #Required. This contains the identifier of the connector to be unlocked.
        )

        response = await self.call(request)
        print("unlock connector is",response)

    #15
    async def update_firmware(self):
        request = call.UpdateFirmwarePayload(
            location="anyURI",    #Required. This contains a string containing a URI pointing to a location from which to retrieve the firmware.
            retries=3,            #Optional. This specifies how many times Charge Point must try to download the
                                  #firmware before giving up. If this field is not present, it is left to Charge Point to
                                  #decide how many times it wants to retry.
            retrieve_date=datetime.utcnow().isoformat(),    #Required. This contains the date and time after which the Charge Point is allowed to retrieve the (new) firmware.
            retry_interval=1800,  #Optional. The interval in seconds after which a retry may be attempted. If this
                                  #field is not present, it is left to Charge Point to decide how long to wait between attempts.
        )

        response = await self.call(request)
        print("update firmware is", response)


    async def authorized_payment(self,auth_data):
        print(auth_data)
        return True


class CentralSystem:
    def __init__(self):
        self._chargers = {}

    def register_charger(self, cp: ChargePoint) -> asyncio.Queue:
        """ Register a new ChargePoint at the CSMS. The function returns a
        queue.  The CSMS will put a message on the queue if the CSMS wants to
        close the connection. 
        """
        queue = asyncio.Queue(maxsize=1)

        # Store a reference to the task so we can cancel it later if needed.
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.start_charger(cp, queue))
        self._chargers[cp] = task

        return queue

    async def start_charger(self, cp, queue):
        """ Start listening for message of charger. """
        try:
            await cp.start()
        except Exception as e:
            print(f"Charger {cp.id} disconnected: {e}")
        finally:
            # Make sure to remove referenc to charger after it disconnected.
            del self._chargers[cp]

            # This will unblock the `on_connect()` handler and the connection
            # will be destroyed.
            await queue.put(True)

    async def change_configuration(self, key: str, value: str):
        for cp in self._chargers:
            await cp.change_configuration(key, value)

    def disconnect_charger(self, id: str):
        for cp, task in self._chargers.items():
            if cp.id == id:
                task.cancel()
                return 
        raise ValueError(f"Charger {id} not connected.")

    async def send_remote_start_transaction(self, id:str):
        for cp, task in self._chargers.items():
            if cp.id == id:
                await cp.send_remote_start_transaction()
                return        
        raise ValueError(f"Charger {id} not connected.")

    async def send_remote_stop_transaction(self, id:str):
        for cp, task in self._chargers.items():
            if cp.id == id:
                await cp.send_remote_stop_transaction()
                return        
        raise ValueError(f"Charger {id} not connected.") 

    async def send_limitation(self, id:str, limit:int):
        for cp, task in self._chargers.items():
            if cp.id == id:
                await cp.set_charging_profile(limit)
                return        
        raise ValueError(f"Charger {id} not connected.")
    
    
async def set_limitation(request):
    """ HTTP handler for changing charging value limitation. """
    data = await request.json()
    csms = request.app["csms"]

    try:
        await csms.send_limitation(data["id"], data["limit"])
    except ValueError as e:
        print(f"Failed to remote start charging: {e}")
        return web.Response(status=404)

    return web.Response()

async def change_config(request):
    """ HTTP handler for changing configuration of all charge points. """
    data = await request.json()
    csms = request.app["csms"]

    await csms.change_configuration(data["key"], data["value"])

    return web.Response()

async def send_remote_start_transaction(request):
    """ HTTP handler for remote start charging. """
    data = await request.json()
    csms = request.app["csms"]

    try:
        await csms.send_remote_start_transaction(data["id"])
    except ValueError as e:
        print(f"Failed to remote start charging: {e}")
        return web.Response(status=404)

    return web.Response()

async def send_remote_stop_transaction(request):
    """ HTTP handler for remote start charging. """
    data = await request.json()
    csms = request.app["csms"]

    try:
        await csms.send_remote_stop_transaction(data["id"])
    except ValueError as e:
        print(f"Failed to remote stop charging: {e}")
        return web.Response(status=404)

    return web.Response()

async def disconnect_charger(request):
    """ HTTP handler for disconnecting a charger. """
    data = await request.json()
    csms = request.app["csms"]

    try:
        csms.disconnect_charger(data["id"])
    except ValueError as e:
        print(f"Failed to disconnect charger: {e}")
        return web.Response(status=404)

    return web.Response()


async def on_connect(websocket, path, csms):
    """ For every new charge point that connects, create a ChargePoint instance
    and start listening for messages.

    The ChargePoint is registered at the CSMS.

    """
    charge_point_id = path.strip("/")
    cp = ChargePoint(charge_point_id, websocket)

    print(f"Charger {cp.id} connected.")

    # If this handler returns the connection will be destroyed. Therefore we need some
    # synchronization mechanism that blocks until CSMS wants to close the connection.
    # An `asyncio.Queue` is used for that.
    queue = csms.register_charger(cp)
    await queue.get()


async def create_websocket_server(csms: CentralSystem):
    handler = partial(on_connect, csms=csms)
    return await websockets.serve(handler, "0.0.0.0", 9000, subprotocols=["ocpp1.6"])


async def create_http_server(csms: CentralSystem):
    app = web.Application()
    app.add_routes([web.post("/changeconfig", change_config)])
    app.add_routes([web.post("/disconnect", disconnect_charger)])
    app.add_routes([web.post("/remotestart", send_remote_start_transaction)])
    app.add_routes([web.post("/remotestop", send_remote_stop_transaction)])
    app.add_routes([web.post("/setmaxvalue", set_limitation)])
    # Put CSMS in app so it can be accessed from request handlers.
    # https://docs.aiohttp.org/en/stable/faq.html#where-do-i-put-my-database-connection-so-handlers-can-access-it
    app["csms"] = csms

    # https://docs.aiohttp.org/en/stable/web_advanced.html#application-runners
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "localhost", 8080)
    return site


async def main():
    loop = asyncio.get_event_loop()
    csms = CentralSystem()

    websocket_server = await create_websocket_server(csms)
    http_server = await create_http_server(csms)

    await asyncio.wait([websocket_server.wait_closed(), http_server.start()])


if __name__ == '__main__':

    EVSE_dict = {}  # store all the EVSEs connected

    # try:
    #     asyncio.run(main())
    # except AttributeError:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
