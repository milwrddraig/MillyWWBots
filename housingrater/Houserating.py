import asyncio
import wizwalker
from random import randint
from wizwalker import WizWalker
from wizwalker.utils import XYZ

oldetowntp = XYZ(x = -24.212629318237305, y = 2150.9998779296875, z = 0.0)


async def rate(p):
    while len(await p.root_window.get_windows_with_name('Star4Button')) == 0:
        await p.mouse_handler.click_window_with_name('OpenCastleRatingWindow')
    while len(await p.root_window.get_windows_with_name('Star4Button')) == 1:
        rating = randint(3,4)
        await p.mouse_handler.click_window_with_name(f'Star{rating}Button')
        await p.mouse_handler.click_window_with_name('RateButton')
    


async def clickok(p):
    while len(await p.root_window.get_windows_with_name('MessageBoxModalWindow')) == 1:
        await p.mouse_handler.click_window_with_name('rightButton')



async def main(p):
    while True:
        if await p.zone_name() == 'Housing_WizardCommonsApt/House_WizardCommonsApt_Int':
            await p.teleport(oldetowntp)
            await asyncio.sleep(6)
        await rate(p)

        await asyncio.sleep(0.5)
        await p.mouse_handler.click_window_with_name('VisitAnotherCastleButton')
        await asyncio.sleep(5)
        await clickok(p)
        await asyncio.sleep(7)
        await clickok(p)
        await asyncio.sleep(2)


        

    



async def startup():
    client = WizWalker().get_new_clients()[0]
    await client.activate_hooks()
    await client.mouse_handler.activate_mouseless()
    try:
        await main(client)
    finally:
        await client.close()


if __name__ == '__main__':
    asyncio.run(startup())
