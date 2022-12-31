import wizwalker
import asyncio
from wizwalker.utils import XYZ
from wizwalker.constants import Keycode
import glob




reagents = ["Wood","Stone","Mushroom","Ore","Cattail"
,"Mandrake","Parchment","Scraplron","Black Lotus","LavaLilly",
"Frost Flower","Kelp","Pearl","Sandstone","Shell",
"Agave","CometTail","Stardust","Antiquitie","Fulgurite"
,"AetherDust","AetherOre","Artifacts","Polygons"]
currentrealm = [6,6]

async def azothchk(p):
    if len(await p.root_window.get_windows_with_name('NPCRangeTxtMessage')) == 1:
        return True
    else:
        return False

async def portallst(client):
    lst = await client.get_base_entity_list()
    portlst = []
    for f in lst:
        try:
            if await f.object_name() in reagents:
                print(await f.object_name(),await f.location())
                loc = await f.location()
                loc.z -= 200
                portlst.append(loc)
            
            
        except:
            await asyncio.sleep(0)
            
    return portlst

async def collect_reagent(client):
    while not await azothchk(client):
        await asyncio.sleep(0.1)
    while await azothchk(client):
        await client.send_key(Keycode.X, 0.2)
        await asyncio.sleep(0.1)
def remslashtxt(txt):
    txt = txt.replace('<center>','')
    txt = txt.replace('/6</center>','')
    return txt
async def realmswitch(p):
    await p.mouse_handler.activate_mouseless()

    while len(await p.root_window.get_windows_with_name('QuitButton')) == 0:
        await p.send_key(Keycode.ESC, 0.2)
    while len(await p.root_window.get_windows_with_name('txtTransferTimerArea')) == 0:
        await p.mouse_handler.click_window_with_name('RealmsButton') 
    while await (await p.root_window.get_windows_with_name('txtTransferTimerArea'))[0].is_visible() :
        await asyncio.sleep(1)
    run = False
    while not run:
        try:
            int(remslashtxt(await (await p.root_window.get_windows_with_name('txtRealmPage'))[0].maybe_text()))
            run = True
        except:
            pass
    realmselected = False
    while  not realmselected:
        while int(remslashtxt(await (await p.root_window.get_windows_with_name('txtRealmPage'))[0].maybe_text())) != currentrealm[0]:
            if int(remslashtxt(await (await p.root_window.get_windows_with_name('txtRealmPage'))[0].maybe_text())) > currentrealm[0]:
                await p.mouse_handler.click_window_with_name('btnRealmLeft') 
            else:
                await p.mouse_handler.click_window_with_name('btnRealmRight')
        if await (await p.root_window.get_windows_with_name(f"txtRealm{currentrealm[1]}Population"))[0].maybe_text() != '' and await (await p.root_window.get_windows_with_name(f"txtRealm{currentrealm[1]}Name"))[0].maybe_text() !=  await (await p.root_window.get_windows_with_name("txtYourRealmName"))[0].maybe_text():
            realmselected = True
            try:
                while await (await p.root_window.get_windows_with_name(f"txtRealm{currentrealm[1]}Population"))[0].is_visible():
                    try:
                        await p.mouse_handler.click_window_with_name(f"txtRealm{currentrealm[1]}Population")
                        await asyncio.sleep(1)
                        await p.mouse_handler.click_window_with_name("btnGoToRealm")
                    except:
                        break
            except:
                break
                
        else:
            currentrealm[1] -= 1
            if currentrealm[1] == -1:
                currentrealm[1] = 6
                currentrealm[0] -= 1
                if currentrealm[0] == 1:
                    currentrealm[0] = 6
    await p.mouse_handler.deactivate_mouseless()
    await asyncio.sleep(8)


async def portentities(client):
    await client.hook_handler.activate_all_hooks()
    filelst = glob.glob('**/*.txt')
    filelst = [s.replace('Zones\\', '') for s in filelst]
    if  str(await client.zone_name()).replace('/','-') + '.txt' in filelst:
        with open(f'Zones\{str(await client.zone_name())}.txt'.replace('/','-'), 'r') as file:
            temp = file.read()
            tellst = (temp.split('\n'))[:-1]
            temp = []
            for x in tellst:
                xyztemp = (x.replace(' ','')).split(',')
                xyz = XYZ(float(xyztemp[0]), float(xyztemp[1]), float(xyztemp[2]))
                xyz.z -= 700
                temp += [xyz]




    tellst = temp
    while True:

        

        
        for f in tellst:
        
            await client.teleport(f)
            await asyncio.sleep(1.5)
            for reagent in await portallst(client):

                await client.teleport(reagent)
                try: 
                    await asyncio.wait_for(collect_reagent(client), 5) 
                except:
                    pass
        await realmswitch(client)

async def main():
    walker = wizwalker.WizWalker()
    clients = walker.get_new_clients()
    try:
        print("Preparing")
        asyncio.gather(portentities(client) for client in clients)
        
    finally:
        print("Closing")
        await walker.close()


if __name__ == "__main__":
    asyncio.run(main())
