import ast
import asyncio, os
import contextlib
from random import randint
from dotenv import load_dotenv
from os import environ as env_variable
from datetime import datetime, timedelta
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
        user_agent = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.57 Mobile Safari/537.36',
        viewport = {'width': 400, 'height': 590},
        device_scale_factor = 2.625,
        # viewport = {'width': 412, 'height': 839}
        # **device,
    )

    default_timeout: int = 30 * 1000
    
    sporty_tab = await context.new_page()
    if len(context.pages) > 0: await context.pages[0].close()

    sporty_tab.set_default_navigation_timeout(default_timeout)
    sporty_tab.set_default_timeout(default_timeout)


    # Login into Sportybet using Cookie 
    my_cookie: list = ast.literal_eval(env_variable.get('my_cookie'))  # Convert string literal to list
    await context.clear_cookies()
    await context.add_cookies(my_cookie)
    await sporty_tab.goto("https://www.sportybet.com/ng/lite")
    logged_in = await sporty_tab.locator('a.m-balance').is_visible()

    if not logged_in:
        # Login into Sportybet using loginPage 
        await sporty_tab.goto("https://www.sportybet.com/ng/lite/login")
        await sporty_tab.locator('//input[@name="username"]').fill(username)
        await sporty_tab.locator('//input[@name="password"]').fill(password)
        await sporty_tab.get_by_role('button', name='Log In').click()
        print("Logged in successfully using Login Page.")
    else:
        print("Logged in successfully using Cookie.")
    while True:
        with contextlib.suppress(TimeoutError):
            await sporty_tab.goto("https://www.sportybet.com/ng/virtual")
            await expect(sporty_tab.locator('//div[@class="m-login-balance"]')).to_be_visible(timeout=default_timeout)
            iframe = sporty_tab.frame_locator("iframe").nth(0)
            await iframe.get_by_text('England League').nth(1).click()
            await expect(iframe.locator('//div[@id="Over_Under_2_5-selector"]')).to_be_visible(timeout=30 * 1000)
            await iframe.locator('//div[@id="Over_Under_2_5-selector"]').click()
            break


    # Opens Realnaps
    realnaps_tab = await context.new_page()
    await realnaps_tab.goto("https://realnaps.com/signal/premium/ultra/sportybet-england-league.php")
    
    async def get_team() -> list:
        hometeam: str = await realnaps_tab.inner_text('//div[@id="homeTxt" and @class="col"]')
        awayteam: str = await realnaps_tab.inner_text('//div[@id="awayTxt" and @class="col"]')
        return [hometeam, awayteam] 
    
    async def dot_position(position):
        if position == 0: return realnaps_tab.locator(f'//a[@class="swift bg-dark" and @name="{position}"]')
        return realnaps_tab.locator(f'//a[@class="swift" and @name="{position}"]')

    async def str_mth_timer() -> str: return str(await get_mth_timer())[1:]
    
    async def pred_day() -> str: return await realnaps_tab.inner_text('//span[@id="day"]')
    
    async def get_mth_timer(): return await iframe.locator(sportybet_mth_cntdown_xpath).inner_text()
    

    weekday: str = await pred_day()
    if weekday == '...':
        print("Waiting for preditions...")
        await expect(realnaps_tab.locator('//span[@id="day"]')
                     ).not_to_contain_text('...', timeout=default_timeout)
        weekday: int = int(await pred_day())

    sportybet_mth_cntdown_xpath: str = f'//span[@class="text--uppercase" and contains(text(), "Week {weekday}")]/following-sibling::*'
    print(f"Prediction displayed.")
    
    while True:
        # Randomly select 1 of 3 slides every season 
        current_season_dot_pos: int = randint(0, 2)  # 0=1, 1=2, 2=3
        print(f"We are working with team {current_season_dot_pos + 1} this season.")
        team = await dot_position(current_season_dot_pos) 
        await team.click()
        
        while True:
            # Get predicted team
            team: list = await get_team()
            print(f"Day {weekday}: {team[0]} vs. {team[1]}")
            await realnaps_tab.close()

            # await sporty_tab.bring_to_front()
            won: bool = True
            mthTimer: datetime = datetime.strptime(await str_mth_timer(), "%M:%S").time()
            timeout: datetime = datetime.strptime("00:00", "%M:%S").time()
            rem_time: timedelta = timedelta(hours=mthTimer.hour, minutes=mthTimer.minute, seconds=mthTimer.second) - timedelta(
                hours=timeout.hour, minutes=timeout.minute, seconds=timeout.second)
            str_rem_time: str = str(rem_time)
            if str_rem_time.split(":")[1] == "00":
                print(f'Countdown time is {str_rem_time.split(":")[2]} seconds.')
            else:
                print(f'Countdown time is {str_rem_time.split(":")[1]}:{str_rem_time.split(":")[2]}')
            # await realnaps_tab.close()
            
            numpad_done_xpath: str = '//div[@class="col grid grid-middle grid-center keypad__done"]'
            rem_odds_xpath: str = "/../../../../following-sibling::div//over-under-market//odd-box//span"
            numpad_xpath: str = '//div[@class="col grid grid-middle grid-center keypad__number ng-star-inserted"]'
            # odds = await iframe.locator(f'//div[contains(text(), "{team[0]}")]{rem_odds_xpath}').all_inner_texts()
            await iframe.locator(f'//div[contains(text(), "{team[0]}")]{rem_odds_xpath}').nth(0).click()
            await iframe.locator('//dynamic-footer-quick-bet[@id="quick-bet-button"]').click()
            await iframe.locator('//input[@class="col col-4 system-bet system-bet__stake"]').click()
            num1 = iframe.locator(numpad_xpath).nth(0)
            num2 = iframe.locator(numpad_xpath).nth(1)
            num3 = iframe.locator(numpad_xpath).nth(2)
            num4 = iframe.locator(numpad_xpath).nth(3)
            num5 = iframe.locator(numpad_xpath).nth(4)
            num6 = iframe.locator(numpad_xpath).nth(5)
            num7 = iframe.locator(numpad_xpath).nth(6)
            num8 = iframe.locator(numpad_xpath).nth(7)
            num9 = iframe.locator(numpad_xpath).nth(8)
            num0 = iframe.locator(numpad_xpath).nth(9)

            if won:
                await num1.click()
                await num0.click()
                await num0.click()
                # await asyncio.sleep(1)
                await iframe.locator(numpad_done_xpath).click()
                await iframe.locator('//div[contains(text(), "Place bet")]').click()
                await expect(iframe.locator('//div[contains(text(), "Sending Ticket")]')).to_be_visible(timeout=10 * 1000)
                print("Sending ticket")
                await expect(iframe.locator('//div[contains(text(), "Ticket Sent")]')).to_be_visible(timeout=10 * 1000)
                print("Sending ticket")
                await expect(iframe.locator('//span[@class="icon icon-circle-checkmark ng-tns-c92-4"]')).to_be_visible(timeout=10 * 1000)
                print("Bet Placed.")
            break
        break




    
    
    
    
    
    
    
    
    # with open("sportybet_cookie.json", "w") as file:
    #     file.write(await context.cookies("https://sportybet.com"))
    
    
    input("Enter something here: ")
    await context.close()

    
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
