import wizwalker
import asyncio
from threading import Event
from wizwalker import Keycode, HotkeyListener, ModifierKeys

xyz_list = []
run = True
async def startup():
    listener = HotkeyListener()


    
    p = wizwalker.WizWalker().get_new_clients()[0]
    

    async def add_xyz():
        global xyz_list
        print('Added a location')
        xyz_list += [await p.body.position()]
    async def end():
        global run
        print('Ending and writing')
        run = False
        
    await listener.add_hotkey(Keycode.K, add_xyz, modifiers=ModifierKeys.NOREPEAT)
    await listener.add_hotkey(Keycode.L, end, modifiers=ModifierKeys.NOREPEAT)
    listener.start()
    try:

        
        await p.activate_hooks()
        filename = await p.zone_name()
        # your program here
        global run
        while run:
            await asyncio.sleep(1)


    finally:
        global xyz_list
        await listener.stop()
        await p.close()
        with open(f'Zones\{filename}.txt'.replace('/','-'), 'w') as file:
            for xyz in xyz_list:
                line = str(xyz).replace('<XYZ (','').replace(')>','')
                file.write(f'{line}\n')

    
    





if __name__ == "__main__":
        asyncio.run(startup())


