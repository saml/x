'''
pip install selenium
install: https://github.com/mozilla/geckodriver
rename the geckodriver binary to wires in PATH

xvfb-run venv/bin/python screenshot.py <url>
'''

import argparse
import os

import selenium.webdriver
from selenium.webdriver import firefox
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', default=os.path.join(os.path.expanduser('~'), '.mozilla/firefox/selenium'), help='Firefox Profile path [%(default)s]')
    parser.add_argument('--firefox', help='Path to firefox executable')
    parser.add_argument('--output', default='out.png', help='Screenshot output file [%(default)s]')
    parser.add_argument('url', help='URL of web page to take screenshot of.')
    args = parser.parse_args()

    caps = DesiredCapabilities.FIREFOX
    caps['marionette'] = True
    if args.firefox:
        caps['binary'] = args.firefox

    profile = selenium.webdriver.FirefoxProfile(args.profile)
    options = firefox.options.Options()
    options.add_argument('--new-instance')
    driver = selenium.webdriver.Firefox(firefox_profile=profile, firefox_options=options, capabilities=caps)
    driver.implicitly_wait(10)
    driver.get(args.url)
    height = driver.execute_script('return document.body.scrollHeight;')
    size = driver.get_window_size()
    driver.set_window_size(size['width'], max(size['height'], height))    
    driver.save_screenshot(args.output)
    driver.quit()
    
    
    
