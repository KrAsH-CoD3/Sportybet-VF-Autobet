import ast
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

    sporty_tab.set_default_navigation_timeout(default_timeout)
    sporty_tab.set_default_timeout(default_timeout)

    # Login into Sportybet using loginPage 
    # await sporty_tab.goto("https://www.sportybet.com/ng/lite/login")
    # await sporty_tab.locator('//input[@name="username"]').fill(username)
    # await sporty_tab.locator('//input[@name="password"]').fill(password)
    # await sporty_tab.get_by_role('button', name='Log In').click()

    # Login into Sportybet using Cookie 
    my_cookie = ast.literal_eval(env_variable.get('my_cookie'))  # Convert string literal to list
    await context.clear_cookies()
    await context.add_cookies(my_cookie)
    await sporty_tab.goto("https://www.sportybet.com/ng/lite")
    logged_in = await sporty_tab.locator('a.m-balance').is_visible()
    print("Logged in successfully using Cookie.")

    if logged_in:
        while True:
            try: 
                await sporty_tab.goto("https://www.sportybet.com/ng/virtual")
                await sporty_tab.frame_locator("iframe").nth(0).get_by_text('England League').nth(1).click()
                break
            except TimeoutError: ...
    iframe = sporty_tab.frame_locator("iframe").nth(0)
    await expect(iframe.locator('//div[@id="Over_Under_2_5-selector"]')).to_be_visible(timeout=20 * 1000)
    await iframe.locator('//div[@id="Over_Under_2_5-selector"]').click()


    # Opens Realnaps
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
    
    async def get_mth_timer():
        return await iframe.locator(sportybet_mth_cntdown_xpath).inner_text()
    
    weekday: str = await pred_day()
    if weekday == '...':
        print("Waiting for preditions...")
        await expect(realnaps_tab.locator('//span[@id="day"]')
                     ).not_to_contain_text('...', timeout=default_timeout)
        weekday: int = int(await pred_day())

    sportybet_mth_cntdown_xpath: str = f'//span[@class="text--uppercase" and contains(text(), "Week {weekday}")]/following-sibling::*'
    print("Prediction displayed.")
    print(await get_mth_timer())

    # Select predicted team
    # current_season_dot_pos: int = randint(0, 2)  # 0=1, 1=2, 2=3
    # print(f"We are working with team {current_season_dot_pos + 1}")
    # team = await dot_position(current_season_dot_pos) 
    # await team.click()
    
    # homeTeam: str = await get_homeTeam()
    # awayTeam: str = await get_awayTeam()
    
    # print(f"Day {day}: {homeTeam} vs. {awayTeam}")




    
    
    
    
    
    
    
    
    # with open("sportybet_cookie.json", "w") as file:
    #     file.write(await context.cookies("https://sportybet.com"))
    
    
    input("Enter something here: ")
    await context.close()

    
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
