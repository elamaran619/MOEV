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


from ocpp.v16 import call
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import RegistrationStatus
from datetime import datetime
from ocpp.v16 import call, call_result
from ocpp.v16.enums import *
from ocpp.routing import on, after

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):



    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charge_point_model="MOEV.CG.1",
            charge_point_vendor="MOEV_GUI"
        )

        response = await self.call(request)
        if response.status == RegistrationStatus.accepted:
            print("Connected to central system.")


    async def start_charging(self):
        request = call.StartTransactionPayload(
            connector_id = 1,
            id_tag = 'transaction1',
            meter_start = 0,
            timestamp = datetime.now().isoformat(),
            reservation_id = None
        )

        response = await self.call(request)
        
        print("Charging point start charing.")

    async def stop_charging(self):
        request = call.StopTransactionPayload(
            meter_stop = 100,
            timestamp = datetime.now().isoformat(),
            transaction_id = 1,
            reason = None,
            id_tag  = None,
            transaction_data = None
        )

        response = await self.call(request)
        print("Charging point Stop charing.")

    async def authorize(self):
        request = call.AuthorizePayload(
            id_tag = 'transaction1'
        )
        response = await self.call(request)

    

    @on(Action.RemoteStartTransaction)
    async def remote_start_transaction(self, id_tag):
        response =  call_result.RemoteStartTransactionPayload(
            status=RemoteStartStopStatus.accepted
        )
        return response

    @on(Action.RemoteStopTransaction)
    async def remote_stop_transaction(self, transaction_id):
        response =  call_result.RemoteStopTransactionPayload(
            status=RemoteStartStopStatus.accepted
        )
        return response

    @on(Action.SetChargingProfile)
    async def set_charging_profile(self, connector_id,cs_charging_profiles):
        response = call_result.SetChargingProfilePayload(
            status=ChargingProfileStatus.accepted
        )
        return response

    @on(Action.ChangeConfiguration)
    async def change_configuration(self, key:str, value:str):
        response = call_result.ChangeConfigurationPayload(
             status=ConfigurationStatus.accepted
        )
        return response

async def main():
    async with websockets.connect(
        'ws://localhost:9000/CP_1',
        subprotocols=["ocpp1.6"]
    ) as ws:

        cp = ChargePoint('CP_1', ws)

        await asyncio.gather(cp.start(),cp.send_boot_notification())


if __name__ == '__main__':
    try:
        # asyncio.run() is used when running this example with Python 3.7 and
        # higher.
        asyncio.run(main())
    except AttributeError:
        # For Python 3.6 a bit more code is required to run the main() task on
        # an event loop.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
