import asyncio
from wizwalker.constants import Keycode
from wizwalker.utils import XYZ
import wizwalker



dungeonlist = ['<center>Baobab Crossroads</center>'] #add the name inside and outside the dungeon between <center> and </center> e.g: ['<center>Kembaalung Village</center>','<center>Hollow Mountain</center>']

async def before_entry(p): #code to execute before entry
    pass #(doesnt need anything for baobab)



async def in_dungeon(p, title): #code to execute in dungeon (this is before collection and detection of reagents. you do not need to put collection functions)
    #example code from halleys:
    pos1 = XYZ(3483.041015625, 4618.98046875, -1571.1602783203125)
    await p.teleport(pos1)
    await asyncio.sleep(0.3)
    # if you need it to check 2 locations for reagents use {reagent_detected, reagent_location = await portallst(p)} then check if reagent_detected ==True , to check a location for azoth
