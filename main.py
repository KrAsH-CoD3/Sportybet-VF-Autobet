from random import randint
from dotenv import load_dotenv
import asyncio, os, contextlib, ast
from os import environ as env_variable
from datetime import datetime, timedelta
from playwright._impl._errors import TimeoutError
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
    )

    stakeAmt = 100
    default_timeout: int = 30 * 1000
    
    sporty_tab = await context.new_page()
    if len(context.pages) > 0: await context.pages[0].close()

    sporty_tab.set_default_navigation_timeout(default_timeout)
    sporty_tab.set_default_timeout(default_timeout)

    numpad_done_xpath: str = '//div[@class="col grid grid-middle grid-center keypad__done"]'
    rem_odds_xpath: str = "/../../../../following-sibling::div//over-under-market//odd-box//span"
    numpad_xpath: str = '//div[@class="col grid grid-middle grid-center keypad__number ng-star-inserted"]'
    
    # Login into Sportybet using Cookie 
    my_cookie: list = ast.literal_eval(env_variable.get('my_cookie'))  # Convert string literal to list
    await context.clear_cookies()
    await context.add_cookies(my_cookie)
    await sporty_tab.goto("https://www.sportybet.com/ng/lite")
    not_logged_in = await sporty_tab.locator('//a[@class="m-btn m-login-btn" and contains(text(), "Log In")]').is_visible()
    
    async def log_in_sporty():
        # Login into Sportybet using loginPage 
        await sporty_tab.goto("https://www.sportybet.com/ng/lite/login")
        await sporty_tab.locator('//input[@name="username"]').fill(username)
        await sporty_tab.locator('//input[@name="password"]').fill(password)
        await sporty_tab.get_by_role('button', name='Log In').click()
        print("Logged in successfully using Login Page.")

    if not_logged_in: await log_in_sporty()
    else: print("Logged in successfully using Cookie.")
        
    async def goto_vfPage():
        while True:
            with contextlib.suppress(TimeoutError, AssertionError):
                await sporty_tab.goto("https://www.sportybet.com/ng/virtual")
                # Waits for loadig icon not to be visible 
                await expect(sporty_tab.locator(
                    '//*[local-name()="svg" and @class="icon loading-icon"]')).not_to_be_visible(timeout=10 * 1000)
                iframe = sporty_tab.frame_locator("iframe").nth(0)
                await iframe.get_by_text('England League').nth(1).click()
                await expect(iframe.locator('//div[@id="Over_Under_2_5-selector"]')).to_be_visible(timeout=default_timeout)
                await iframe.locator('//div[@id="Over_Under_2_5-selector"]').click()
                break
    
    await goto_vfPage()
    iframe = sporty_tab.frame_locator("iframe").nth(0)
    
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

    async def mth_timer() -> str: 
        timer = await iframe.locator(sportybet_mth_cntdown_xpath).inner_text()
        return str(timer)[1:]
    
    async def pred_day() -> int: 
        weekday: str = await realnaps_tab.inner_text('//span[@id="day"]')
        if weekday == '...':
            print("Waiting for preditions...")
            await expect(realnaps_tab.locator('//span[@id="day"]')
                        ).not_to_contain_text('...', timeout=default_timeout * 2)
            print(f"Prediction displayed.")
            return int(await realnaps_tab.inner_text('//span[@id="day"]'))
        return int(weekday)
    
    async def place_bet(): 
        await iframe.locator(numpad_done_xpath).click()
        await iframe.locator('//div[contains(text(), "Place bet")]').click()
        await expect(iframe.locator('//span[contains(text(), "Sending Ticket")]')).to_be_visible(timeout=default_timeout)
        print("Sending Ticket.")
        await expect(iframe.locator('//span[contains(text(), "Ticket Sent")]')).to_be_visible(timeout=default_timeout)
        print("Ticket Sent, Bet Placed.")
    
    async def select_team_slide():
        # Randomly select 1 of 3 slides every season 
        current_season_dot_pos: int = randint(0, 2)  # 0=1, 1=2, 2=3
        team_slide = await dot_position(current_season_dot_pos) 
        await team_slide.click()
        print(f"We are working with team {current_season_dot_pos + 1} this season.")

    weekday = await pred_day()
    
    # SEASON GAMES
    while True:
        # await select_team_slide()

        # WEEKDAY GAMES
        while True:
            # Get predicted team
            # await realnaps_tab.bring_to_front()
            if weekday != await pred_day(): continue
            # print(f"{'-'*10}Week Day {weekday}{'-'*10}")
            team: list = await get_team()
            match_info: str = f"{'-'*10}Week Day {str(weekday)}{'-'*10}\nTeam: {team[0]} vs. {team[1]}"
            print(match_info)
            sportybet_mth_cntdown_xpath: str = f'//span[@class="text--uppercase" and contains(text(), "Week {str(weekday)}")]/following-sibling::*'

            await sporty_tab.bring_to_front()
            try: # FIRST CHECK: if live match is ongoing
                sporty_tab.set_default_timeout(1000)
                mthTimer: datetime = datetime.strptime(await mth_timer(), "%M:%S").time()
            except TimeoutError:
                print(f"Oops missed the match. Live match already ongoing.\nGetting new match data")
                weekday += 1
                continue
            finally: sporty_tab.set_default_timeout(default_timeout)
            timeout: datetime = datetime.strptime("00:00", "%M:%S").time()
            rem_time: timedelta = timedelta(hours=mthTimer.hour, minutes=mthTimer.minute, seconds=mthTimer.second) - timedelta(
                hours=timeout.hour, minutes=timeout.minute, seconds=timeout.second)
            str_rem_time: str = str(rem_time)
            odds: list = await iframe.locator(f'//div[contains(text(), "{team[0]}")]{rem_odds_xpath}').all_inner_texts()
            if str_rem_time.split(":")[1] == "00":
                print(f'Weekday {str(weekday)} odd: {odds[0]}\nCountdown time is {str_rem_time.split(":")[2]} seconds.')
            else:
                print(f'Weekday {str(weekday)} odd: {odds[0]}\nCountdown time is {str_rem_time.split(":")[1]}:{str_rem_time.split(":")[2]}')
            
            # Check if match isn't already began
            try:
                sporty_tab.set_default_timeout(1000)
                # SECOND CHECK: if live match has began before placing bet
                # Get live match day immediately(no timeout) in live match bar
                live_matchday: str = await iframe.locator('//gr-header[@class="ng-star-inserted live-status-playing"]//span[@class="text--uppercase"]').inner_text()
                if live_matchday.split(' ')[1] != str(weekday): 
                    print(f"Sorry, Match {live_matchday} already began.\nGetting new match data")
                    weekday = int(live_matchday.split(' ')[1]) + 1
                    continue
            except: ... # No live match ongoing
            finally: sporty_tab.set_default_timeout(default_timeout)

            await realnaps_tab.close()

            ## Select Odd and place bet
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
            num_dict = {1: num1, 2: num2, 3: num3, 4: num4, 5: num5, 6: num6, 7: num7, 8: num8, 9: num9, 0: num0}
            # Type the initial stake amount by clicking the corresponding elements
            for digit in str(stakeAmt):
                await num_dict[int(digit)].click()

            await place_bet()  # Place bet
            await goto_vfPage()  # Refresh the page because of sportybet logout bug

            live_mth_red = iframe.locator(f'//gr-header[@class="ng-star-inserted live-status-playing"]') # Does not check here
            print(f"Waiting for match to begin...")
            await expect(live_mth_red).to_be_visible(timeout=default_timeout * 5)  # Checks here
            print("Match started...")
            await live_mth_red.click()
            await asyncio.sleep(7)
            while True:
                try:
                    await expect(iframe.locator('//*[@class="status-icon won"]')).to_be_visible(timeout=1000)
                    print(f"Day {str(weekday)} won")
                    stakeAmt = 100  # Return back to initial stake amount
                    break
                except TimeoutError: 
                    try: # "Finished" text 
                        await expect(iframe.locator(
                            f'//div[@class="col-xs-2 valign-middle team-container ellipsis" and contains(text(), "{team[0]}")]/ancestor::div[@class="row text-center valign-wrapper title-width ng-star-inserted"]//span[@class="time-container__info ng-star-inserted" and contains(text(), "Finished")]')).to_be_visible(timeout=1000)
                        print(f"Day {str(weekday)} lost")
                        stakeAmt *= 2  # Double the previous stake amount
                        break
                    except TimeoutError: ...
            print("Match ended.")
            realnaps_tab = await context.new_page()
            await realnaps_tab.goto("https://realnaps.com/signal/premium/ultra/sportybet-england-league.php")
            if weekday != 38: weekday += 1
            else: weekday = 1; print(f"\n{'-'*10}NEW SEASON BEGINS{'-'*10}")

    
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
