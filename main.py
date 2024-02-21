import asyncio, os
from random import randint
from dotenv import load_dotenv
from os import environ as env_variable
from playwright.async_api import async_playwright, Playwright, expect

load_dotenv(override=True)
sportybet_mth_cntdown_xpath: str = '//span[@class="text--uppercase" and contains(text(), "Week 29")]/following-sibling::*'
async def run(playwright: Playwright):
    profile: str = "Sportybet-VF-profile"
    current_working_dir: str = os.getcwd()
    user_data_path: str = os.path.join(current_working_dir, profile)

    username, password = env_variable.get('username'), env_variable.get('password')
    device: dict = dict(playwright.devices["Pixel 7"])
    device: dict = {key: value for key, value in device.items() if key not in ('has_touch', 'is_mobile', 'default_browser_type')}

    context = await playwright['chromium'].launch_persistent_context(
        args = ['--touch-events=enabled', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled'],
        user_data_dir = user_data_path, 
        headless = False,
        color_scheme ='dark',
        channel= "chrome",
        **device,
    )

    default_timeout: int = 30 * 1000
    
    sporty_tab = await context.new_page()
    if len(context.pages) > 0: await context.pages[0].close()

    # Login into Sportybet 
    sporty_tab.set_default_navigation_timeout(default_timeout)
    sporty_tab.set_default_timeout(default_timeout)
    # await sporty_tab.goto("https://www.sportybet.com/ng/lite/login")
    # await sporty_tab.locator('//input[@name="username"]').fill(username)
    # await sporty_tab.locator('//input[@name="password"]').fill(password)
    # await sporty_tab.get_by_role('button', name='Log In').click()
    await expect(sporty_tab.locator('a.m-balance')).to_be_visible()
    # await asyncio.sleep(5)
    my_cookie: list = await context.cookies()
    await context.clear_cookies()
    await sporty_tab.goto("https://www.sportybet.com/ng/lite")
    input("Cleared Cookie ")
    await context.add_cookies(my_cookie)
    await sporty_tab.goto("https://www.sportybet.com/ng/lite")
    input("Added cookie ")
    # with open("sportybet_cookie.json", "w") as file:
    #     file.write(await context.cookies("https://sportybet.com"))
    my_cookie:list = [{'name': '_ntes_nnid', 'value': '19dff1333fcee1fe0dce705e93d0d255', 'domain': 'www.sportybet.com', 'path': '/', 'expires': 1743074846.393588, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'deviceId', 'value': '240221112724bdid56723499', 'domain': 'www.sportybet.com', 'path': '/', 'expires': -1, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'userId', 'value': '180814144749puid30184815', 'domain': 'www.sportybet.com', 'path': '/', 'expires': -1, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'accessToken', 'value': 'patron:id:accesstoken:8818af07c1c6d3c5c3a5b73371f1757be9NwF2f8CRAAl288HavXlWwydi03oXSay/e/m8Ztxhb3X6Vrh2ky9r+gvoeZoe6YmT+JHmUHcy7zg3NY7fJwxg==', 'domain': 'www.sportybet.com', 'path': '/', 'expires': -1, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'refreshToken', 'value': 'patron:id:refreshtoken:95a81cf486b849e3adf4437813a927a3', 'domain': 'www.sportybet.com', 'path': '/', 'expires': 1711106844.7118, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'phone', 'value': '9096866925', 'domain': 'www.sportybet.com', 'path': '/', 'expires': -1, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}]
    
    while True:
        try: 
            await sporty_tab.goto("https://www.sportybet.com/ng/lite")
            await expect(sporty_tab.locator('a.m-balance')).to_be_visible(timeout=3000)
            print("Logged In")
            # await sporty_tab.frame_locator("iframe").nth(0).get_by_text('England League').nth(1).click()
            break
        except AssertionError: 
            # for cookies in my_cookie:
            await context.clear_cookies()
            await context.add_cookies(my_cookie)
    
    
    # while True:
    #     try: 
    #         await sporty_tab.goto("https://www.sportybet.com/ng/virtual")
    #         await sporty_tab.frame_locator("iframe").nth(0).get_by_text('England League').nth(1).click()
    #         break
    #     except TimeoutError: ...
    # iframe = sporty_tab.frame_locator("iframe").nth(0)
    # await expect(iframe.locator('//div[@id="Over_Under_2_5-selector"]')).to_be_visible(timeout=20 * 1000)
    # await iframe.locator('//div[@id="Over_Under_2_5-selector"]').click()
    # print(await get_mth_timer())

    # Opens Realnaps
    # realnaps_tab = await context.new_page()
    # await realnaps_tab.goto("https://realnaps.com/signal/premium/ultra/sportybet-england-league.php")
    # # await expect(sporty_tab.locator('//div[@class="m-login-balance"]')).to_be_visible(timeout=default_timeout)
    
    # async def dot_position(position):
    #     if position == 0: return realnaps_tab.locator(f'//a[@class="swift bg-dark" and @name="{position}"]')
    #     return realnaps_tab.locator(f'//a[@class="swift" and @name="{position}"]')

    # async def pred_day():
    #     return await realnaps_tab.inner_text('//span[@id="day"]')

    # async def get_homeTeam():
    #     return await realnaps_tab.inner_text('//div[@id="homeTxt" and @class="col"]')
    
    # async def get_awayTeam():
    #     return await realnaps_tab.inner_text('//div[@id="awayTxt" and @class="col"]')
    
    async def get_mth_timer():
        return await iframe.locator(sportybet_mth_cntdown_xpath).inner_text()
    
    # day = await pred_day()
    
    # if day == '...':
    #     print("Waiting for preditions...")
    #     await expect(realnaps_tab.locator('//span[@id="day"]')
    #                  ).not_to_contain_text('...', timeout=default_timeout)
    #     day = await pred_day()

    # # print("Prediction displayed.")

    # current_season_dot_pos: int = randint(0, 2)  # 0=1, 1=2, 2=3
    # print(f"We are working with team {current_season_dot_pos + 1}")
    # team = await dot_position(current_season_dot_pos) 
    # await team.click()
    
    
    # homeTeam: str = await get_homeTeam()
    # awayTeam: str = await get_awayTeam()
    
    # print(f"Day {day}: {homeTeam} vs. {awayTeam}")




    
    
    
    
    
    
    
    
    
    
    
    input("Enter something here: ")
    await context.close()

    
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
