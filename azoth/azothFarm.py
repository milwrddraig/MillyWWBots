import subprocess
import asyncio
import wizwalker
import copy
from time import time
from wizwalker.constants import Keycode
from wizwalker.utils import get_all_wizard_handles, start_instance, instance_login
from wizwalker import Client, XYZ
from wizwalker.memory import Window



class clientInfo: #contains all information needed for a client to run
    def __init__(self, username: str, password: str, handle, title: str, wizLst: list, totalAzothCollected: int, timeSinceBotAction: int):
        self.username = username
        self.password = password
        self.handle = handle
        self.title = title
        self.wizLst = wizLst
        self.totalAzothCollected = totalAzothCollected
        self.timeSinceBotAction = timeSinceBotAction

class wizardInfo: #contains all information of a wizard needed for differentiation and logic of the run
    def __init__(self, wizardName: str, wizardLevel: str, wizardLocation: str, currentHappiness: int, totalHappiness: int):
        self.Name = wizardName
        self.Level = wizardLevel
        self.Location = wizardLocation
        self.Happiness = currentHappiness
        self.totalHappiness = totalHappiness
    def __str__(self):
        return f'{removeTags(self.Name)} the {removeTags(self.Level)} in {removeTags(self.Location)}'
    def __eq__(self, other) : 
        return self.Name == other.Name and self.Level == other.Level



#list that will contain every client
activeClients=[]

#list of all reagents names to allow for detection
reagents = ["Wood","Stone","Mushroom","Ore","Cattail"
,"Mandrake","Parchment","Scraplron","Black Lotus","LavaLilly",
"Frost Flower","Kelp","Pearl","Sandstone","Shell",
"Agave","CometTail","Stardust","Antiquitie","Fulgurite"
,"AetherDust","AetherOre","Artifacts", 'Polygons']


#paths for clicking and checking
snackCard0 = ['WorldView', 'PetFeedForHappinessWindow', 'wndBkgBottom', 'wndCards', 'chkSnackCard0']
petSystem = ['WorldView', 'windowHUD', 'PetSystemButton']
closeFeedPetWindow = ['WorldView', 'PetFeedForHappinessWindow', 'CloseFeedPetForHappinessWindow']
feedStack = ['WorldView', 'PetFeedForHappinessWindow', 'FeedStackOfSnacksButton']
happinessText = ['WorldView', 'PetFeedForHappinessWindow', 'HappinessText']
feedPet = ['WorldView', 'windowHUD', 'PetSystemButton', 'PetButtonLayout', 'FeedPetButton']
petPowerButton = ['WorldView', 'windowHUD', 'PetSystemButton', 'PetButtonLayout', 'UsePetPowerButton']
petPowerCooldown = ['WorldView', 'windowHUD', 'PetSystemButton', 'PetButtonLayout', 'UsePetPowerButton', 'PetPowerCooldownText']
quitButton = ['WorldView', 'DeckConfiguration', 'SettingPage', 'QuitButton']
logOutConfirm = ['MessageBoxModalWindow', 'messageBoxBG', 'messageBoxLayout', 'AdjustmentWindow', 'Layout', 'centerButton']
txtLocation  = ['WorldView', 'mainWindow', 'sprSubBanner', 'txtLocation']
txtLevel = ['WorldView', 'mainWindow', 'sprSubBanner', 'txtLevel']
txtName  = ['WorldView', 'mainWindow', 'sprBanner', 'txtName']
playButton = ['WorldView', 'mainWindow', 'btnPlay']




locationList = []
baseLocationList = [] #just includes the location name for simplicity
import os
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'Locations.txt')) as file:
    lines = file.readlines()
    for line in lines:
        line = str(line)
        locNames,farmtype,teleportXYZs = line.split('|')
        for loc in locNames.split(':'):
             
            try: #have fun reading this, it creates a list of XYZs based on the string teleportXYZs
                xyzTemp = [ XYZ(float(x.replace(' ','').split(',')[0]), float(x.replace(' ','').split(',')[1]), float(x.replace(' ','').split(',')[2])) for x in teleportXYZs.split(':')]
            except:#if this throws up an error its likely there is no XYZ in the list which is valid, hence None
                xyzTemp = [None]
            
            
            locationList += [[loc,farmtype,xyzTemp]] #packs everything back into the lists
            baseLocationList += [loc]
            


# Returns a window, given a path 
async def window_from_path(base_window:Window, path:list[str]) -> Window:
    # Credit to SirOlaf for the original function; I'm modifying it - credit ultimate314;  and now me i have stolen this mwah haha
    if not path:
        return base_window
    for child in await base_window.children():
        if await child.name() == path[0]:
            if found_window := await window_from_path(child, path[1:]):
                return found_window
    return False

async def is_visible_by_path(base_window:Window, path: list[str]):
    # Credit to SirOlaf for the original function; I'm modifying it - credit ultimate314;  and now me i have stolen this mwah haha
    if window := await window_from_path(base_window, path):
        return await window.is_visible()
    return False

async def click_window_from_path(mouse_handler, base_window, path): #credit ultimate314
    try:
        await mouse_handler.click_window(await window_from_path(base_window, path))
    except:
        pass

async def click_window_until_gone(client, path): #i did this im very cool
    while (window := await window_from_path(client.root_window, path)) and await is_visible_by_path(client.root_window, path):
            await client.mouse_handler.click_window(window)
            await asyncio.sleep(0.1)
        



async def petPower(client, delay=2): #clicks the power button
    await click_window_from_path(client.mouse_handler, client.root_window, petPowerButton)

    


def removeTags(string):
    return string.replace('</center>','').replace('<center>','')


def removeTitle(string):
    return string.replace('AzothFarm: ','')



async def nearestReagent(client,title): #returns a boolean for whether a reagent was detected and the reagents location
    entityList = await client.get_base_entity_list()
    reagentList = []
    for entity in entityList:
        if await entity.object_name() in reagents:
            print(f'[{removeTitle(title)}] Reagent Detected:', await entity.object_name())
            reagentList += [entity]
        await asyncio.sleep(0)
    if len(reagentList)== 0 :
        return False, None
    else: 
        smallestDistance = 999999999.0
        clientLocation = await client.body.position()
        for reagent in reagentList :
            reagentLocation = await reagent.location()
            currentDistance = clientLocation - reagentLocation
            if currentDistance < smallestDistance:
                smallestDistance = currentDistance
                closest = reagentLocation
        return True, closest


'''async def logonload(p):
    while not await p.is_loading():
        print('waiting for loading screen')
        await asyncio.sleep(0.2)
    while await p.is_loading():
        print('waiting to get out of loading screen')
        await asyncio.sleep(0.2)
''' #didnt work the way I wanted it to, may use later

async def setup(client): #activates all hooks that it can for a client
    print(f"[{removeTitle(client.title)}] Activating Hooks")
    await client.activate_hooks(wait_for_ready = False)
    await client.mouse_handler.activate_mouseless()



async def petPowerVisibility(client): #returns if the petpower button is visible
    return await is_visible_by_path(client.root_window, petPowerButton)

async def cooldownVisibility(client): #returns if the cooldown text is visible
    return await is_visible_by_path(client.root_window, petPowerCooldown)


async def crownshopVisibilty(client): #returns if crownshop is visible
    try: return await ((await client.root_window.get_windows_with_name('permanentShop'))[0]).is_visible()
    except: return False
    
async def skipDialogue(client): #skips dialogue boxes if any opened
    while True:
        await asyncio.sleep(0.2)
        while await client.is_in_dialog():
            await client.send_key(Keycode.SPACEBAR,0)
        while await crownshopVisibilty(client):
            await asyncio.sleep(1)
            await client.send_key(Keycode.ESC, 0.3)
            await asyncio.sleep(0.4)
            await client.send_key(Keycode.ESC, 0.3)
            await asyncio.sleep(1)
    

async def azothCollect(client,tipAmount): #collects azoth, uses the number of TipWindows to check if azoth is collected >>> TO BE REPLACED WITH DROP LOGGER
    while await petPowerVisibility(client):
        await petPower(client,0.05)
    while tipAmount == len(await client.root_window.get_windows_with_name('TipWindow')):
        await petPower(client, 0.1)
        await asyncio.sleep(0.1)

async def snackVisibility(client): #checks if a snack is visible in the first snack slot
    return await is_visible_by_path(client.root_window, snackCard0)



async def azothFarmer(p,listPosition):
    try:
        
        await setup(p)
        try:
            dialogueChecker = asyncio.create_task(skipDialogue(p))
        finally:
            pass
        startTime = time()
        
        while not await is_visible_by_path(p.root_window, playButton):
            await p.send_key(Keycode.TAB, 0.1)
        
        while not removeTags(str(await (await window_from_path(p.root_window, txtLocation)).maybe_text())) in baseLocationList :
            await p.send_key(Keycode.TAB, 0)
        
        wizard  = wizardInfo(await (await window_from_path(p.root_window, txtName)).maybe_text(),
                             await (await window_from_path(p.root_window, txtLevel)).maybe_text(),
                             await (await window_from_path(p.root_window, txtLocation)).maybe_text(),0,0)
        
        while not wizard in [wiz for wiz in activeClients[listPosition].wizLst]:                     
            
            if removeTags(wizard.Location) in baseLocationList :
                activeClients[listPosition].wizLst += [copy.deepcopy(wizard)]
                


            await p.send_key(Keycode.TAB, 0)
            wizard  = wizardInfo(await (await window_from_path(p.root_window, txtName)).maybe_text(),
                                await (await window_from_path(p.root_window, txtLevel)).maybe_text(),
                                await (await window_from_path(p.root_window, txtLocation)).maybe_text(),0,0)
              
        print(f'[{activeClients[listPosition].title}] Is using these wizards:')
        for x in activeClients[listPosition].wizLst:
            print(x)
        
        
        await click_window_until_gone(p, playButton)
        

                

        
        
        await asyncio.sleep(8.5)
        
        if await is_visible_by_path(p.root_window, quitButton):
            await p.send_key(Keycode.ESC, 0)
        
        
        originalWizards = len(activeClients[listPosition].wizLst)
        
        runthrough = 0 #counter of how many times it has gone through the for loop
        while True:
            if len(activeClients[listPosition].wizLst) ==0: #if there are no wizards left stop the script
                break
            for position , wizard in enumerate(activeClients[listPosition].wizLst,0):
                needSwitch = False #True if the wizard needs to be switched (this is if a reagent is detected)
                
                if runthrough == 0:
                    #this checks pet happiness
                    while await crownshopVisibilty(p):
                        await asyncio.sleep(1)
                        await p.send_key(Keycode.ESC, 0.3)
                        await asyncio.sleep(0.4)
                        await p.send_key(Keycode.ESC, 0.3)
                        await asyncio.sleep(1)
                    
                    while not await is_visible_by_path(p.root_window, feedPet):
                        await click_window_from_path(p.mouse_handler, p.root_window, petSystem)
                          
                    
                    while not await is_visible_by_path(p.root_window, closeFeedPetWindow):
                        await p.mouse_handler.click_window_with_name('FeedPetButton')

                    petHappinessText = (await window_from_path(p.root_window, happinessText))
                    Happiness, totalHappiness = ((removeTags(await petHappinessText.maybe_text())).split('/')) #assign pet happiness to wizard object in the main list
                    wizard.Happiness, wizard.totalHappiness = int(Happiness), int(totalHappiness)
                    
                    await click_window_until_gone(p,closeFeedPetWindow)
                    

                    while await is_visible_by_path(p.root_window, feedPet):
                        await click_window_from_path(p.mouse_handler, p.root_window, petSystem)
                #end of checking pet happiness
                
                
                while not needSwitch:
                    if await crownshopVisibilty(p):
                        await asyncio.sleep(1)
                        await p.send_key(Keycode.ESC, 0.3)
                        await asyncio.sleep(0.4)
                        await p.send_key(Keycode.ESC, 0.3)
                        await asyncio.sleep(0.5) 
                        
                    
                    print(f'[{activeClients[listPosition].title}]: {removeTags(wizard.Name)} has {wizard.Happiness} happiness')
                    keepWizard = True #defines whether a wizard should be kept
                    
                    
                    if  int(wizard.Happiness) < 5 :
                        print(f'[{activeClients[listPosition].title}] Feeding Pet')
                        keepWizard = await refillhappiness(p)
                        wizard.Happiness = wizard.totalHappiness 
                    
                    if keepWizard:
                        # Entering Dungeon

                        
                        locationIndex = baseLocationList.index(removeTags(wizard.Location)) #find the index of the location fo the character
                        
                        if not locationList[locationIndex][1] == 'Dungeon': #used to check if the character needs to enter 
                            await asyncio.sleep(0.3)
                            
                        
                        else: #presses x while waiting to load into dungeon
                            location = await p.zone_name()
                            while location == await p.zone_name():
                                if await crownshopVisibilty(p):
                                    await asyncio.sleep(1)
                                    await p.send_key(Keycode.ESC, 0.3)
                                    await asyncio.sleep(0.4)
                                    await p.send_key(Keycode.ESC, 0.3)
                                    await asyncio.sleep(1)
                                await p.send_key(Keycode.X, 0)
                            while await p.is_loading():
                                await p.send_key(Keycode.X, 1)
                                
                                
                        
                        for tpLocation in locationList[locationIndex][2]: #runs check for each location in list
                            
                            bodyPosition = await p.body.position()
                            bodyPosition.z = bodyPosition.z -1000 
                            await asyncio.sleep(0.2)
                            await p.teleport(bodyPosition) #teleports wizard down
                            
                            if tpLocation == None: #tps to specified location or not depending on whats in .txt
                                pass
                            else:
                                await asyncio.sleep(0.2)
                                await p.teleport(XYZ(tpLocation.x, tpLocation.y, tpLocation.z - 1000))
                                await asyncio.sleep(0.2)
                            while True:
                                try:
                                    reagentDetected, reagentLocation = await nearestReagent(p,activeClients[listPosition].title)
                                    break
                                except:
                                    pass
                                
                            
                            
                            if reagentDetected and keepWizard:
                        
                                reagentLocation.z = reagentLocation.z - 750         
                                await p.teleport(reagentLocation)
                                
                                #updating values
                                
                                needSwitch = True
                                activeClients[listPosition].totalAzothCollected += 1
                                wizard.Happiness -= 5
                                
                                

                                while not await petPowerVisibility(p): #waits for the pet power button to be visible
                                    await asyncio.sleep(0.2)
                                
                                

                                while await cooldownVisibility(p): #waits for the cooldown to dissapear
                                    await asyncio.sleep(0.2)
                                
                                tiplen = len(await p.root_window.get_windows_with_name('TipWindow')) #number of tip windows so it can be detected if that number increases

                                    

                                

                                    
                                try: 
                                    await asyncio.wait_for(azothCollect(p,tiplen), 8) #waits for 8 seconds for the azoth to be collected
                                except: 
                                    print(print(f'[{activeClients[listPosition].title}]-Failsafe activated quit without azoth, DM this to milwr to ruin his day'))




                                break
                    
                    

                    try:  #logic for picking next wizard
                        nextWizard = activeClients[listPosition].wizLst[position+1] 
                    except IndexError:
                        nextWizard = activeClients[listPosition].wizLst[0]
                    await asyncio.sleep(0.2)
                    
                    if not keepWizard: #if we arent keeping the wizard we need it to switch
                        needSwitch =True

                    await logout_and_in(p,nextWizard,needSwitch,activeClients[listPosition].title)
                    
                    if not keepWizard: #breaks out of for loop to restart it
                        break
                    
                    
                    p.title = activeClients[listPosition].title + ' [Azoth Collected: ' + str(activeClients[listPosition].totalAzothCollected) + ', Active Time: ' + str(round((time() - startTime) / 60, 2)) +', Using '+ str(len(activeClients[listPosition].wizLst)) +'/' + str(originalWizards)+ ' wizards' + ']'
                    
                    # Time
                    print("------------------------------------------------------")
                    print("The Total Amount of Azoth is: ", sum([x.totalAzothCollected for x in activeClients]))
                    print("Time Taken for run: ", activeClients[listPosition].timeSinceBotAction, "seconds")
                    print("Total time elapsed: ", round((time() - startTime) / 60, 2), "minutes")
                    print("------------------------------------------------------")
                    
                    #update BotAction
                    activeClients[listPosition].timeSinceBotAction = 0
                
                
                
                if not keepWizard:
                    activeClients[listPosition].timeSinceBotAction = 0
                    print(f'[{activeClients[listPosition].title}] Removing Wizard From List: {wizard}' )
                    
                    
                    if len(activeClients[listPosition].wizLst) != 1:  #changes list to start from current next wizard then remove the wizard
                        newFirst = activeClients[listPosition].wizLst[position:]
                        newLast = activeClients[listPosition].wizLst[:position]
                        activeClients[listPosition].wizLst = newFirst + newLast
                        activeClients[listPosition].wizLst.pop(position)
                    else:
                        activeClients[listPosition].wizLst.pop(position)
                        pass
                    break
            if keepWizard:
                runthrough += 1
    finally:
        dialogueChecker.cancel()
        await p.send_key(Keycode.ESC, 0.1)


        #basic idea here is it will keep pressing the button until it detects something that means it can move onto the next part in logging out
        await click_window_until_gone(p, quitButton)
        
        while not await is_visible_by_path(p.root_window, logOutConfirm):
            await asyncio.sleep(0.1)
            if await is_visible_by_path(p.root_window, playButton):
                break 
        await click_window_until_gone(p, logOutConfirm)           
        while not(await is_visible_by_path(p.root_window, playButton)): pass

        import traceback
        traceback.print_exc()
        raise RuntimeError (f'[{activeClients[listPosition].title}] is brokey')



async def azothCheck(p): #checks how many tip windows there are
    e = 0
    c = await p.root_window.get_windows_with_name('TipWindow')
    for x in c:
        try:
            for y in await x.children():
                if await y.name() == 'ControlSprite':
                    e+=1
        except:
            await asyncio.sleep(0.1)
    if e>0:
        return True
    else:
        return False


async def logout_and_in(client,nextWizard,needSwitch,title):
        #fail check is used multiple times as it is what i have called the variable that ends the button pressing loops
        
        print(f'[{title}] Logging out and in')
        await client.send_key(Keycode.ESC, 0.1)


        #basic idea here is it will keep pressing the button until it detects something that means it can move onto the next part in logging out
        await click_window_until_gone(client, quitButton)
        
        
        while not (needConfirm := await is_visible_by_path(client.root_window, logOutConfirm)):
            await asyncio.sleep(0.1)
            if await is_visible_by_path(client.root_window, playButton):
                break
        
        if needConfirm: await click_window_until_gone(client, logOutConfirm)        

        
                
        while not(await is_visible_by_path(client.root_window, playButton)): await asyncio.sleep(0.1)

                
        
        
                    
                
        if needSwitch: print(f'[{title}] Switching Wizard To: {nextWizard}' )
            
        switch = True        
        while switch and needSwitch:
                await client.send_key(Keycode.TAB, 0.05)
                try:        
                    wizard  = wizardInfo(await (await window_from_path(client.root_window, txtName)).maybe_text(),
                             await (await window_from_path(client.root_window, txtLevel)).maybe_text(),
                             await (await window_from_path(client.root_window, txtLocation)).maybe_text(),0,0)
                except:
                    pass
                        
                
                if wizard == nextWizard:
                    switch = False
                    
                

        await click_window_until_gone(client, playButton)

            

        await client.wait_for_zone_change()
        await asyncio.sleep(0.5)

        if await is_visible_by_path(client.root_window, quitButton):
            await client.send_key(Keycode.ESC, 0.1)

async def runmanager(listPosition):
    
    p = Client(activeClients[listPosition].handle)
    
    
    
    while True:
        try:
            run = asyncio.create_task(azothFarmer(p,listPosition))
            while True:
                
                while activeClients[listPosition].timeSinceBotAction < 150: #basic counter waits 150 seconds 
                    await asyncio.sleep(1)
                    activeClients[listPosition].timeSinceBotAction += 1
                
                
                print(f'[{activeClients[listPosition].title}] Has stopped producing azoth, restarting')
                break
        except:
            print(f'[{activeClients[listPosition].title}] Has failed during farming, printing error')
            import traceback
            traceback.print_exc()
            await asyncio.sleep(0)
        try:
            run.cancel()
            noProcesses = len(asyncio.all_tasks())
            while noProcesses == len(asyncio.all_tasks()):
                await asyncio.sleep(0.3)
        finally:
            await asyncio.sleep(6)
            pass
        await p.close()

        try:
            subprocess.call(f"taskkill /F /PID {p.process_id}",stdout=subprocess.DEVNULL) #kills the current wizard client
        except:
            await asyncio.sleep(0)
        await asyncio.sleep(3)
        p = None
        handles = get_all_wizard_handles()
        start_instance()
        await asyncio.sleep(6)
        while p == None:
                try:
                    activeClients[listPosition].handle = list(set(get_all_wizard_handles()).difference(handles))[0]
                    
                    instance_login(activeClients[listPosition].handle, activeClients[listPosition].username, activeClients[listPosition].password)
                    p = Client(activeClients[listPosition].handle)
                    
                except:
                    await asyncio.sleep(0.5)
            
        activeClients[listPosition].timeSinceBotAction = 0    
        p.title = 'AzothFarm: ' + activeClients[listPosition].title





async def main():
    # Register clients
    print('Azoth Farm Bot AKA Milwrs emotional crisis')
    print("""Credits: Hailtothethrone- the original bot,
          Nitsuj- discovery of Halley's observatory,
          Ultimate- fuck you, thanks for the help""")
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"accounts.txt")) as my_file:
            accountList = [
                line.strip().split(":") for line in my_file.read().split("\n") #reads account list and puts into into a list
                ]
    async with asyncio.TaskGroup() as tg: #so it waits for every client to finish
            for x in range(len(accountList)):
                handles = get_all_wizard_handles()
                start_instance()
                await asyncio.sleep(10)
                runthrough = True
                while runthrough:
                    try:
                        handle = list(set(get_all_wizard_handles()).difference(handles))[0] #finds the new handle made by start_instance()
                        instance_login(handle, accountList[x][0], accountList[x][1])
                        p = Client(handle) #defines a client
                        p.title = 'AzothFarm: Bot ' + str(x+1)
                        
                        activeClients.append( clientInfo(username = accountList[x][0],
                                                        password = accountList[x][1],
                                                        handle = handle, wizLst = [],
                                                        title = f'Bot {str(x+1)}',
                                                        totalAzothCollected = 0,
                                                        timeSinceBotAction = 0)) #setting up client info
                        
                        tg.create_task(runmanager(x))
                        
                        runthrough = False

                    except:
                        await asyncio.sleep(0.5)


            
    

    




async def refillhappiness(p):
        while not await is_visible_by_path(p.root_window, feedPet):
            await click_window_from_path(p.mouse_handler, p.root_window, petSystem)
                          
                    
        while not await is_visible_by_path(p.root_window, closeFeedPetWindow):
            await p.mouse_handler.click_window_with_name('FeedPetButton')

        happiness = removeTags(await (await window_from_path(p.root_window, happinessText)).maybe_text())    


        
        while eval(happiness) != 1:
            await click_window_from_path(p.mouse_handler, p.root_window, snackCard0)
            await click_window_from_path(p.mouse_handler, p.root_window, feedStack)

            happiness = removeTags(await (await window_from_path(p.root_window, happinessText)).maybe_text())
            
            if not await snackVisibility(p):
                
                await click_window_until_gone(p, closeFeedPetWindow)

                while await is_visible_by_path(p.root_window, feedPet):
                    await click_window_from_path(p.mouse_handler, p.root_window, petSystem)
                    
                return False
            
        await click_window_until_gone(p, closeFeedPetWindow)

        while await is_visible_by_path(p.root_window, feedPet):
            await click_window_from_path(p.mouse_handler, p.root_window, petSystem)
        return True
        
        

            
    # Error Handling
async def run():
        try:
            await main()
        except:
         import traceback
         traceback.print_exc()

        input('Pls ss this error')
if __name__ == "__main__":
        asyncio.run(run())
