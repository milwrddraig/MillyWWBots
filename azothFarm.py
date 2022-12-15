import subprocess

import asyncio
import wizwalker
import configparser
from time import time
from wizwalker.constants import Keycode
from wizwalker.utils import get_all_wizard_handles, start_instance, instance_login
from modulardungeon import before_entry, in_dungeon, dungeonlist
from wizwalker import Client

activetasks=[]
reagents = ["Wood","Stone","Mushroom","Ore","Cattail"
,"Mandrake","Parchment","Scraplron","Black Lotus","LavaLilly",
"Frost Flower","Kelp","Pearl","Sandstone","Shell",
"Agave","CometTail","Stardust","Antiquitie","Fulgurite"
,"AetherDust","AetherOre","Artifacts"]

#config:
config = configparser.ConfigParser()
config.read('config.ini')
rding = config['Settings']['Name or Level reading (N/L)']
if rding == 'l':
    rding = 'txtLevel'
else:
    rding = 'txtName'
delay = float(config['Settings']['Delay (0 for none)'])
tp = config['Settings']['Tp to reagent (t/f)']
if tp == 't':
    tp = True
else:
    tp = False
lgn = config['Settings']['Use auto logon(t/f)']
if lgn == 't':
    lgn = True
else:
    lgn = False

async def pet_power(p, delay=2):
    await p.mouse_handler.click_window_with_name('UsePetPowerButton')
    await p.mouse_handler.click_window_with_name('UsePetPowerButton')
    await asyncio.sleep(delay)
def remid(s):
    s = s.replace('<center>','')
    s = s.replace('</center>','')
    return s
def remtitle(s):
    s = s.replace('AzothFarm: ','')
    return s
async def portallst(client,title):
    lst = await client.get_base_entity_list()
    sort = []
    for f in lst:
        if await f.object_name() in reagents:
            print(f'[{remtitle(title)}] Reagent Detected:', await f.object_name())
            sort += [f]
            #return True , await f.location()
        await asyncio.sleep(0)
    if len(sort)== 0 :
        return False, None
    else: 
        dist = 999999999.0
        cloc = await client.body.position()
        for f in sort :
            floc = await f.location()
            fdist = (floc.x - cloc.x)*(floc.x- cloc.x) + (floc.y- cloc.y)*(floc.y- cloc.y) + (floc.z- cloc.z)*(floc.z- cloc.z)
            if fdist < dist:
                dist = fdist
                closest = floc
        return True, closest


async def logonload(p):
    while not await p.is_loading():
        print('waiting for loading screen')
        await asyncio.sleep(0.2)
    while await p.is_loading():
        print('waiting to get out of loading screen')
        await asyncio.sleep(0.2)

async def printentities(client):
    lst = await client.get_base_entity_list()
    for f in lst:
        print(await f.object_name())
        if await f.object_name() in reagents:
            print(f'[{client.title}] Reagent Detected:', await f.object_name()) 
            loc = await f.location()
            print(loc)
    for f in lst:
        if await f.object_name() == 'Player Object':
            for x in await f.children(): 
                print(await x.object_name())
                for y in await x.children():
                    print(await y.object_name())
                if await x.object_name() == 'PetObject':
                    print(dir(x))
                    pet = x

     
    print(await pet.location())
    print(await pet.maybe_read_type_name())
    print(await pet.read_value_from_offset(576,'bool'))
    await pet.write_value_to_offset(576, False, 'bool')
    while True:
        await pet.write_xyz(168, loc)

    

        
    return False
async def setup(client):
    print(f"[{remtitle(client.title)}] Activating Hooks")
    await client.activate_hooks(wait_for_ready = False)
    await client.mouse_handler.activate_mouseless()



async def petcheckvis(client):
    p = await client.root_window.get_windows_with_name('UsePetPowerButton') 
    pet = p[0]
    return await pet.is_visible()

async def coolcheckvis(client):
    p = await client.root_window.get_windows_with_name('PetPowerCooldownText') 
    pet = p[0]
    return await pet.is_visible()
async def coolno(client):
    p = await client.root_window.get_windows_with_name('PetPowerCooldownText') 
    pet = p[0]
    try:
        return int(remid(await pet.maybe_text()))
    except: return 999 # just so if i check a value ik it has come from here
async def cshopcheckvis(client):
    try:
        p = await client.root_window.get_windows_with_name('permanentShop') 
        pet = p[0]
        return await pet.is_visible()
    except: return False
    
async def diarun(client):
    while await client.is_in_dialog():
        await asyncio.sleep(0.1)
        await client.send_key(Keycode.SPACEBAR,0.3)
        await asyncio.sleep(0.1)
    

async def azoth_collect(p,length):
    while length == len(await p.root_window.get_windows_with_name('TipWindow')):
        await pet_power(p, 0.1)
        await diarun(p)
        await asyncio.sleep(0.1)

async def snackcheckvis(client):
    p = await client.root_window.get_windows_with_name('chkSnackCard0') 
    pet = p[0]
    return await pet.is_visible()

# list of valid locations:
loclist = ['<center>Kembaalung Village</center>','<center>Hollow Mountain</center>','<center>Castle Darkmoor</center>',"<center>Regent's Square</center>", "<center>Halley's Observatory</center>"]

async def azothfarm(p,slot):
    try:
        global Azoth_Count
        global dungeonlist
        count = 0
        await setup(p)
        title = p.title
        total = time()
        Total_Count = 0
        wizlst = []
        halleylst = [] # second list so i can check the wizard and edit the code manually later
        customlist = []
        await asyncio.sleep(1.5)
        cont = False
        while not cont:
            try:
                await p.send_key(Keycode.TAB, 0.1)
                loc = (await p.root_window.get_windows_with_name('txtLocation'))[0]
                cont = True
            except:
                continue
        
        while (not str(await loc.maybe_text()) in loclist) and (not str(await loc.maybe_text()) in dungeonlist) :
            await p.send_key(Keycode.TAB, 0.1)
        wiz  = (await p.root_window.get_windows_with_name(rding))[0]
        while not (await wiz.maybe_text() in wizlst):
            loc = (await p.root_window.get_windows_with_name('txtLocation'))[0]
            wiz = (await p.root_window.get_windows_with_name(rding))[0]
            if await loc.maybe_text() in loclist or await loc.maybe_text() in dungeonlist:
                wizlst += [str(await wiz.maybe_text())]
                if await loc.maybe_text() == "<center>Regent's Square</center>" or await loc.maybe_text() ==  "<center>Halley's Observatory</center>": #these are the two special locations 
                    halleylst += [str(await wiz.maybe_text())]
                if await loc.maybe_text() in dungeonlist:
                    customlist += [str(await wiz.maybe_text())]


            await p.send_key(Keycode.TAB, 0.1)
            await asyncio.sleep(0.3) 
        templst =[]    
        print(f'[{remtitle(title)}] Is using these wizards:')
        for x in wizlst:
            templst += [remid(x)]
        print(*templst, sep = ", ")
        await asyncio.sleep(0.5)
        failcheck = True
        while failcheck:
                
                if len(await p.root_window.get_windows_with_name('btnPlay')) == 1:
                    try:
                        await p.mouse_handler.click_window_with_name('btnPlay')
                    except:
                        continue
                    #print('clicking play')
                else: 
                    failcheck = False
                    #print('stopped clicking play')
                await asyncio.sleep(delay)

        if len(await p.root_window.get_windows_with_name('QuitButton')) == 1:
            await p.send_key(Keycode.ESC, 0.1)
        
        await asyncio.sleep(7)
        templst= []
        for x in range(len(wizlst)):
            templst += [[wizlst[x],'']]
        wizlst = templst
        totalwiz = len(wizlst)
        rnthr = 0
        while True:
            if len(wizlst) ==0:
                break
            for x in range(len(wizlst)):
                needswitch = False
                
                if rnthr == 0:
                    
                    while await cshopcheckvis(p):
                        await asyncio.sleep(1)
                        await p.send_key(Keycode.ESC, 0.3)
                        await asyncio.sleep(0.4)
                        await p.send_key(Keycode.ESC, 0.3)
                        await asyncio.sleep(1)
                    while len(await p.root_window.get_windows_with_name('FeedPetButton')) == 0:
                        while await cshopcheckvis(p):
                            await asyncio.sleep(1)
                            await p.send_key(Keycode.ESC, 0.3)
                            await asyncio.sleep(0.4)
                            await p.send_key(Keycode.ESC, 0.3)
                            await asyncio.sleep(1)
                        try:
                            await p.mouse_handler.click_window_with_name('PetSystemButton')
                            await asyncio.sleep(0.1)
                        except:
                            await asyncio.sleep(0.1)  
                    while not await (await p.root_window.get_windows_with_name('FeedPetButton'))[0].is_visible() :
                        await p.mouse_handler.click_window_with_name('PetSystemButton')
                        await asyncio.sleep(0.1)
                    while len(await p.root_window.get_windows_with_name('CloseFeedPetForHappinessWindow')) == 0:
                        await p.mouse_handler.click_window_with_name('FeedPetButton')
                        await asyncio.sleep(0.1)

                    pethappiness = (await p.root_window.get_windows_with_name('HappinessText'))[0]
                    wizlst[x][1] = remid(await pethappiness.maybe_text())
                    try:
                        
                        while await (await p.root_window.get_windows_with_name('CloseFeedPetForHappinessWindow'))[0].is_visible():
                            await p.mouse_handler.click_window_with_name('CloseFeedPetForHappinessWindow')
                            await asyncio.sleep(0.1)
                    except:
                        await asyncio.sleep(0.2)
                    while await (await p.root_window.get_windows_with_name('FeedPetButton'))[0].is_visible():
                        await p.mouse_handler.click_window_with_name('PetSystemButton')
                        await asyncio.sleep(0.1)
                while not needswitch:
                    if await cshopcheckvis(p):
                        await asyncio.sleep(1)
                        await p.send_key(Keycode.ESC, 0.3)
                        await asyncio.sleep(0.4)
                        await p.send_key(Keycode.ESC, 0.3)
                        await asyncio.sleep(0.5) 
                    lastazoth = time()
                    start = time()
                    print(f'[{remtitle(title)}]: {remid(wizlst[x][0])} has {wizlst[x][1]} happiness')
                    hapiness,full = ((wizlst[x][1]).split('/'))
                    kpchar = True
                    if  int(hapiness) < 5 :
                        await diarun(p)
                        print(f'[{remtitle(title)}] Feeding Pet')
                        kpchar = await refillhappiness(p)
                        hapiness = full
                    if kpchar:
                        # Entering Dungeon

                        await asyncio.sleep(delay)
                        if wizlst[x][0] in customlist:
                            await before_entry(p)
                        else:
                            location = await p.zone_name()
                            while location == await p.zone_name():
                                if await cshopcheckvis(p):
                                    await asyncio.sleep(1)
                                    await p.send_key(Keycode.ESC, 0.3)
                                    await asyncio.sleep(0.4)
                                    await p.send_key(Keycode.ESC, 0.3)
                                    await asyncio.sleep(1)
                                await p.send_key(Keycode.X, 0.3)
                                await asyncio.sleep(0.4)
                            while await p.is_loading():
                                await asyncio.sleep(0.3)
                                await p.send_key(Keycode.X, 0.3)
                        #t=0
                        #while await petcheckvis(p) and t <12: #increase this value maybe?
                        #        await asyncio.sleep(0.3)
                        #        t+=1
                        if wizlst[x][0] in halleylst:
                            #potentially change this to a hard code for a xyz to go to
                            await p.goto(-3224.598388671875, -1160.1627197265625)
                            #this is needed to get a 3rd spawn point
                        if wizlst[x][0] in customlist:
                            await in_dungeon(p, title)
                        collected = False
                        await asyncio.sleep(0.1)
                        rea, realoc = await portallst(p,title)
                        if rea and kpchar:
                            if tp:
                                bodloc = await p.body.position()
                                bodloc.z = bodloc.z -1000
                                await asyncio.sleep(0.2)
                                await p.teleport(bodloc)
                                if wizlst[x][0] in halleylst:
                                    realoc.z = realoc.z +25
                                else:
                                    realoc.z = realoc.z -1000
                                    
                                
                                await p.teleport(realoc)
                            needswitch = True
                            hapiness = str(int(hapiness)-5)

                            while not await petcheckvis(p):
                                await diarun(p)
                                await asyncio.sleep(0.2)
                            Total_Count += 1
                            Azoth_Count += 1

                            while await coolcheckvis(p):
                                await diarun(p)
                                await p.send_key(Keycode.D, 0.2)
                            tiplen = len(await p.root_window.get_windows_with_name('TipWindow'))
                            #If you set it to like 10-20 here
                            await asyncio.sleep(delay)
                            await diarun(p)
                            

                                

                            
                            while await petcheckvis(p):
                                await diarun(p)
                                await pet_power(p,delay)
                                await asyncio.sleep(delay)
                            collected =  True
                            try: 
                                await asyncio.wait_for(azoth_collect(p,tiplen), 8) 
                            except: 
                                print(print(f'[{remtitle(title)}]-Failsafe activated quit without azoth, DM this to milwr to ruin his day'))


                            #then stop it here it should get the benefit of the speed and none of the risk


                            await diarun(p)
                            lastazoth = time()
                    
                    
                    wizlst[x][1] =  hapiness +'/' + full

                    try:
                        nxtwiz = wizlst[(x+1)][0]
                    except IndexError:
                        nxtwiz = wizlst[0][0]
                    await asyncio.sleep(0.2)
                    if not kpchar:
                        needswitch =True

                    await logout_and_in(p,nxtwiz,needswitch,title)
                    if not kpchar:
                        break
                    
                    await asyncio.sleep(delay)
                    if collected:
                        count += 1
                        p.title = title + ' [Azoth Collected: ' + str(count) + ', Active Time: ' + str(round((time() - total) / 60, 2)) +', Using '+ str(len(wizlst)) +'/' + str(totalwiz)+ ' wizards' + ']'
                    activetasks[slot] = True
                    # Time
                    print("------------------------------------------------------")
                    print("The Total Amount of Azoth is: ", Azoth_Count)
                    print("Time Taken for run: ", round((time() - start) / 60, 2), "minutes")
                    print("Total time elapsed: ", round((time() - total) / 60, 2), "minutes")
                    print('Time since last azoth is: ', round((time() - lastazoth) / 60, 2))
        
                    print("------------------------------------------------------")
                
                if not kpchar:
                    print(f'[{remtitle(title)}] Removing Wizard From List: {remid(wizlst[x][0])}' )
                    if len(wizlst) != 1:
                        newfirst = wizlst[x:]
                        newlast = wizlst[:x]
                        wizlst = newfirst + newlast
                        wizlst.pop(x)
                    else:
                        wizlst.pop(x)
                        pass
                    break
            if kpchar:
                rnthr += 1
    finally:
        import traceback
        traceback.print_exc()
        raise RuntimeError (f'[{remtitle(title)}] is brokey')



async def azothchk(p):
    e = 0
    c = await p.root_window.get_windows_with_name('TipWindow')
    for x in c:
        try:
            for y in await x.children():
                if await y.name() == 'ControlSprite':
                    e+=1
        except:
            await asyncio.sleep(0)
    if e>0:
        return True
    else:
        return False


async def logout_and_in(client,nxtwiz,needswitch,title):
        #fail check is used multiple times as it is what i have called the variable that ends the button pressing loops
        failcheck = True
        print(f'[{remtitle(title)}] Logging out and in')
        await diarun(client)
        await asyncio.sleep(0.1)
        await client.send_key(Keycode.ESC, 0.1)
        await asyncio.sleep(0.1)

        while failcheck: 
            try:
                await client.mouse_handler.click_window_with_name('QuitButton')
                failcheck = False
            
            except ValueError:
                #await asyncio.sleep(0.5)
                await client.send_key(Keycode.ESC, 0.1) 
        
        await asyncio.sleep(delay)
        failcheck = True
        while failcheck:
            try:
                await client.mouse_handler.click_window_with_name('QuitButton')
                print('quitbtn')
            except ValueError:
                await asyncio.sleep(delay)

                failcheck = False
        failcheck = True 
        while failcheck:
            try:
                await client.mouse_handler.click_window_with_name('centerButton') 
                failcheck = False
                await asyncio.sleep(delay)
                await client.mouse_handler.click_window_with_name('centerButton') 
            except ValueError:
                await asyncio.sleep(delay)
                #print('noplaybtn')
                if len(await client.root_window.get_windows_with_name('btnPlay')) == 1:
                    #print('playbtn')
                    failcheck = False
                


        
                
            



                
        await asyncio.sleep(delay)
        failcheck =True
        f= True
        while failcheck:
            try:
                switch = True
                if needswitch and f :
                    print(f'[{remtitle(title)}] Switching Wizard To: {remid(nxtwiz)}' )
                    f= False
                p = await client.root_window.get_windows_with_name(rding) 
                a = p[0]
                while switch and needswitch:
                        if needswitch:
                            await client.send_key(Keycode.TAB, 0.1)
                            await asyncio.sleep((delay*3))
                        a = (await client.root_window.get_windows_with_name(rding))[0]
                        if await a.maybe_text() == nxtwiz:
                            switch = False
                    
                
                
                failcheck = False
            except ValueError :
                await asyncio.sleep(1)
            except IndexError :
                await asyncio.sleep(1)

        await asyncio.sleep(delay)
        failcheck = True
        while failcheck:
            
            if len(await client.root_window.get_windows_with_name('btnPlay')) == 1:
                try:
                    await client.mouse_handler.click_window_with_name('btnPlay')
                except:
                    continue
                #print('clicking play')
            else: 
                failcheck = False
                #print('stopped clicking play')
            await asyncio.sleep(delay)

        await client.wait_for_zone_change()
        await asyncio.sleep(0.5)
        await asyncio.sleep(delay)
        if len(await client.root_window.get_windows_with_name('QuitButton')) == 1:
            await client.send_key(Keycode.ESC, 0.1)

async def runmanager(p,slot):
    slot = slot - 1
    title = p.title
    global activetasks
    global acctlst
    while True:
        try:
            run = asyncio.create_task(azothfarm(p,slot))
            while True:
                cnt = 0
                activetasks[slot] = False
            #    try:
            #        run = asyncio.create_task(azothfarm(p))
            #    except:
            #        continue
                while activetasks[slot] == False:
                    await asyncio.sleep(1)
                    cnt+= 1
                    if cnt == 150:
                        print(f'[{remtitle(title)}] Has stopped producing azoth, restarting')
                        break
                if cnt == 150:
                    break
        except:
            print('running failed')
            import traceback
            traceback.print_exc()
            await asyncio.sleep(0)
        try:
            run.cancel()
        finally:
            await asyncio.sleep(0)
        await p.close()
        try:
            subprocess.call(f"taskkill /F /PID {p.process_id}",stdout=subprocess.DEVNULL)
        except:
            await asyncio.sleep(0)
        await asyncio.sleep(3)
        p = None
        if lgn:
            handles = get_all_wizard_handles()
            start_instance()
            await asyncio.sleep(6)
            while p == None:
                try:
                    handle = list(set(get_all_wizard_handles()).difference(handles))[0]
                    
                    instance_login(handle, acctlst[slot][0], acctlst[slot][1])
                    p = Client(handle)
                except:
                    await asyncio.sleep(0.5)
            
            
            p.title = 'AzothFarm: Bot ' + str(slot+1)
        else: break




acctlst=[]

async def main(sprinter):
    global activetasks
    global acctlst
    global Azoth_Count
    Azoth_Count = 0
    # Register clients
    print('Azoth Farm Bot AKA Milwrs emotional crisis')
    print("Credits: Hailtothethrone- the original bot, Nitsuj- discovery of Halley's observatory")
    print('Fix the azoth economy- Set ur price to 8 emp per azoth to try and bring the price back up to 7')
    print('15/16$ per stack for monetary sales (can go a bit lower since they are harder to do)')

    if lgn:
        with open("accounts.txt") as my_file:
            acctlst = [
                line.strip().split(":") for line in my_file.read().split("\n")
                ]
        async with asyncio.TaskGroup() as tg:
            for x in range(len(acctlst)):
                handles = get_all_wizard_handles()
                start_instance()
                await asyncio.sleep(10)
                rnthr = True
                while rnthr:
                    try:
                        handle = list(set(get_all_wizard_handles()).difference(handles))[0]
                        instance_login(handle, acctlst[x][0], acctlst[x][1])
                        p = Client(handle)
                        p.title = 'AzothFarm: Bot ' + str(x+1)
                        activetasks.append(False)
                        tg.create_task(runmanager(p,x+1))
                        
                        rnthr = False

                    except:
                        await asyncio.sleep(0.5)


            
    

    

    else:
        sprinter.get_new_clients()
        clients = sprinter.get_ordered_clients()
        non_hooked_clients = []
        for client in clients:
            if not "p" in client.title:
                non_hooked_clients.append(client)
        clients = non_hooked_clients

        await asyncio.sleep(1)


        for i, p in enumerate(clients, 1):
            p.title = 'AzothFarm: Bot ' + str(i)
            activetasks.append(False)

    
        await asyncio.gather(*[runmanager(p,i) for i, p in enumerate(clients, 1)])
    




async def refillhappiness(p):
        while len(await p.root_window.get_windows_with_name('FeedPetButton')) == 0:
            await p.mouse_handler.click_window_with_name('PetSystemButton')
            await asyncio.sleep(0.1)  
        while not await (await p.root_window.get_windows_with_name('FeedPetButton'))[0].is_visible() :
            await p.mouse_handler.click_window_with_name('PetSystemButton')


        while len(await p.root_window.get_windows_with_name('CloseFeedPetForHappinessWindow')) == 0:
            await p.mouse_handler.click_window_with_name('FeedPetButton')
            await asyncio.sleep(0.1)        


        happiness = remid(await ((await p.root_window.get_windows_with_name('HappinessText'))[0]).maybe_text())


        
        while eval(happiness) != 1:
            await p.mouse_handler.click_window_with_name('chkSnackCard0')
            await asyncio.sleep(0.2)
            await p.mouse_handler.click_window_with_name('FeedStackOfSnacksButton')
            await asyncio.sleep(0.2)
            happiness = remid(await ((await p.root_window.get_windows_with_name('HappinessText'))[0]).maybe_text())
            if not await snackcheckvis(p):
                while len(await p.root_window.get_windows_with_name('CloseFeedPetForHappinessWindow')) == 1:
                    await p.mouse_handler.click_window_with_name('CloseFeedPetForHappinessWindow')
                    await asyncio.sleep(0.1)
                while await (await p.root_window.get_windows_with_name('FeedPetButton'))[0].is_visible():
                    await p.mouse_handler.click_window_with_name('PetSystemButton')
                    await asyncio.sleep(0.1)
                return False
        while len(await p.root_window.get_windows_with_name('CloseFeedPetForHappinessWindow')) == 1:
            await p.mouse_handler.click_window_with_name('CloseFeedPetForHappinessWindow')
            await asyncio.sleep(0.1)
        while await (await p.root_window.get_windows_with_name('FeedPetButton'))[0].is_visible():
            await p.mouse_handler.click_window_with_name('PetSystemButton')
            await asyncio.sleep(0.1)
        return True
        
        

            
    # Error Handling
async def run():
        sprinter = wizwalker.WizWalker()
        try:
            await main(sprinter)
        except:
         import traceback
         traceback.print_exc()

        await sprinter.close()
        input('Pls ss this error')
if __name__ == "__main__":
        asyncio.run(run())
