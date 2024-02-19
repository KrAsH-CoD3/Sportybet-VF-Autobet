import asyncio, os
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
        # is_mobile= True,  # This make the bot detectable
        # has_touch= True,  # This make the bot detectable
    )

        
    page = await context.new_page()
    if len(context.pages) > 0: await context.pages[0].close()

    # page.set_default_navigation_timeout(30 * 1000)
    page.set_default_timeout(30 * 1000)
    await page.goto("https://www.sportybet.com/ng/lite/login")
    await page.locator('//input[@name="username"]').fill(username)
    await page.locator('//input[@name="password"]').fill(password)
    await page.get_by_role('button', name='Log In').click()
    await expect(page.locator('a.m-balance')).to_be_visible()
    input("Enter something here: ")


    await context.close()

    
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
