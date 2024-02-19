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
    device_browser_type: str = device.pop("default_browser_type")

    context = await playwright['chromium'].launch_persistent_context(
        args=['--touch-events=enabled'],
        user_data_dir= user_data_path, 
        headless= False,
        color_scheme='dark',
    )

        
    page = await context.new_page()
    if len(context.pages) > 0: await context.pages[0].close()

    # CODE GOES HERE
    await page.goto("sportybet.com/ng/virtual")
    await context.close()

    
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
