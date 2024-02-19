import asyncio, os
from dotenv import load_dotenv
from os import environ as env_variable
from playwright.async_api import async_playwright, Playwright

load_dotenv()

async def run(playwright: Playwright):
    profile: str = "Sportybet-VF-profile"
    current_working_dir: str = os.getcwd()
    user_data_path: str = os.path.join(current_working_dir, profile)

    username, password = env_variable.get('username'), env_variable.get('password')
    device: dict = dict(playwright.devices["Pixel 7"])
    device_prop: dict = {key: value for key, value in device.items() if key not in ('has_touch', 'is_mobile', 'default_browser_type')}

    context = await playwright['chromium'].launch_persistent_context(
        args = ['--touch-events=enabled'],
        user_data_dir = user_data_path, 
        headless = False,
        color_scheme ='dark',
        channel= "chrome",
        **device_prop,

        # user_agent= device['user_agent'], 
        # viewport= device['viewport'], 
        # device_scale_factor= device['device_scale_factor'], 
        # default_browser_type= 'chrome', #'chromium'

        # is_mobile= True,  # This make the bot detectable
        # has_touch= True,  # This make the bot detectable
    )

        
    page = await context.new_page()
    if len(context.pages) > 0: await context.pages[0].close()

    # CODE GOES HERE
    await page.goto("https://sportybet.com/ng/virtual")
    input("Enter something here: ")

    
    await context.close()

    
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
