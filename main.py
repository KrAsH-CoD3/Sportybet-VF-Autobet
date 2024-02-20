import asyncio, os
from random import randint
from dotenv import load_dotenv
from os import environ as env_variable
from playwright.async_api import async_playwright, Playwright, expect

load_dotenv(override=True)

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

    # sporty_tab.set_default_navigation_timeout(default_timeout)
    # sporty_tab.set_default_timeout(default_timeout)
    # await sporty_tab.goto("https://www.sportybet.com/ng/lite/login")
    # await sporty_tab.locator('//input[@name="username"]').fill(username)
    # await sporty_tab.locator('//input[@name="password"]').fill(password)
    # await sporty_tab.get_by_role('button', name='Log In').click()
    # await expect(sporty_tab.locator('a.m-balance')).to_be_visible()
    # while True:
    #     try: 
    #         await sporty_tab.goto("https://www.sportybet.com/ng/virtual")
    #         await sporty_tab.frame_locator("iframe").nth(0).get_by_text('England League').nth(1).click()
    #         break
    #     except TimeoutError: ...
    # iframe = sporty_tab.frame_locator("iframe").nth(0)
    # await expect(iframe.locator('//div[@id="Over_Under_2_5-selector"]')).to_be_visible(timeout=20 * 1000)
    # await iframe.locator('//div[@id="Over_Under_2_5-selector"]').click()

    realnaps_tab = await context.new_page()
    await realnaps_tab.goto("https://realnaps.com/signal/premium/ultra/sportybet-england-league.php")
    # await expect(sporty_tab.locator('//div[@class="m-login-balance"]')).to_be_visible(timeout=default_timeout)
    
    async def dot_position(position):
        if position == 0: return realnaps_tab.locator(f'//a[@class="swift bg-dark" and @name="{position}"]')
        return realnaps_tab.locator(f'//a[@class="swift" and @name="{position}"]')

    async def pred_day():
        return await realnaps_tab.inner_text('//span[@id="day"]')

    async def get_homeTeam():
        return await realnaps_tab.inner_text('//div[@id="homeTxt" and @class="col"]')
    
    async def get_awayTeam():
        return await realnaps_tab.inner_text('//div[@id="awayTxt" and @class="col"]')
    
    day = await pred_day()
    
    if day == '...':
        print("Waiting for preditions...")
        await expect(realnaps_tab.locator('//span[@id="day"]')
                     ).not_to_contain_text('...', timeout=default_timeout)

    print("Prediction displayed.")

    current_season_dot_pos: int = randint(0, 2)
    print(f"We are working with team {current_season_dot_pos}")
    dot = await dot_position(current_season_dot_pos)  #0=1, 1=2, 2=3
    await dot.click()
    
    
    homeTeam: str = await get_homeTeam()
    awayTeam: str = await get_awayTeam()
    
    print(f"Predicted match at match day {await pred_day()} is {homeTeam} vs. {awayTeam}")

    # await asyncio.sleep(5)
    # print("clicked the 3rd prediction")


    input("Enter something here: ")
    await context.close()

    
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
