import asyncio
from kasa import SmartPlug
from kasa_secrets import KASA_DEVICE_IP_ADDRESS

'''
This program controls a Kasa SmartPlug on the local 
network in order to turn it off (if ON) and vice versa. 
'''

def flip_switch():
    asyncio.run(main())
    
async def main():
    # initialize plug 
    plug = SmartPlug(KASA_DEVICE_IP_ADDRESS)
    # connect to plug and access its data
    await plug.update()
    # if plug is ON, turn OFF and vice versa
    if plug.is_on:
        await plug.turn_off()
    else:
        await plug.turn_on()
        