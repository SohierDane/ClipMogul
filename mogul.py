
import json
import re


from random import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, time


CLEANED_SOURCE_PATH = 'game_page.html'


def id_buttons_in_source():
    # 61 buttons in the source code, looks like more are loaded by scripts
    # see the special project buttons for example of latter
    # initial buttons seem to use less standardized format than those that appear later
    with open(CLEANED_SOURCE_PATH) as f_open:
        page_source = f_open.read()
    button_pattern = '(?<=button class="button2" id=")\w+(?=")'
    return re.findall(button_pattern, page_source)


class ClipMogul:
    def __init__(self):
        # constants
        self.GAME_LAUNCH_URL = 'http://www.decisionproblem.com/paperclips/'
        self.MAX_CLICKS_PER_SECOND = 100  # unclear how many of these even register. More than 40.
        self.TARGET_SECONDS_INVENTORY = 10

        # internals
        self.config = json.load(open('.config'))
        if 'CHROME_PATH' in self.config:
            self.driver = webdriver.Chrome(self.config['CHROME_PATH'])
        else:
            self.driver = webdriver.Chrome()
        self.click_delay = 1 / self.MAX_CLICKS_PER_SECOND

        # game metrics
        self.clip_count = 0
        self.funds = 0
        self.unsold_clips = 0
        self.clip_price = 0
        self.demand = 0
        self.console_log = []
        self.clipper_cost = float('inf')
        self.wire_amount = 0
        self.launch_time = 0

    def wait_for_id(self, element_id, seconds_to_wait=10):
        WebDriverWait(self.driver, seconds_to_wait).until(
            EC.element_to_be_clickable((By.ID, element_id)))

    def launch_game(self):
        self.driver.get(self.GAME_LAUNCH_URL)
        launcher_xpath = '//img[@alt="Universal Paperclips"]'
        self.driver.find_element_by_xpath(launcher_xpath).click()
        print('Waiting for game page to load.')
        self.wait_for_id('btnMakePaperclip')
        self.launch_time = time()
        print('Game page loaded.')

    def make_paperclip(self):
        self.driver.find_element_by_id('btnMakePaperclip').click()

    def make_many_paperclips(self, n):
        for i in range(n):
            self.make_paperclip()
            sleep(self.click_delay)

    def buy_auto_clipper(self):
        self.update_funds()
        # first clipper might take a while to appear
        self.wait_for_id('btnMakeClipper', 100)
        while self.funds < self.clipper_cost:
            self.update_clipper_cost()
            sleep(1 + random())
        self.driver.find_element_by_id('btnMakeClipper').click()

    def get_value_for_id(self, element_id):
        text = self.driver.find_element_by_id(element_id).text.replace(',', '')
        return float(text)

    def update_paperclip_count(self):
        self.clip_count = self.get_value_for_id('clips')

    def update_funds(self):
        self.funds = self.get_value_for_id('funds')

    def update_unsold_clips(self):
        self.unsold_clips = self.get_value_for_id('unsoldClips')

    def update_clip_price(self):
        self.clip_price = self.get_value_for_id('margin')

    def update_demand(self):
        self.demand = self.get_value_for_id('demand')

    def update_clipper_cost(self):
        self.clipper_cost = self.get_value_for_id('clipperCost')

    def update_wire(self):
        self.wire_amount = self.get_value_for_id('wire')

    def update_console_log(self):
        current_log = self.driver.find_element_by_id('readout1').text
        if not self.console_log:
            self.console_log.append(current_log)
        elif current_log != self.console_log[-1]:
            self.console_log.append(current_log)

    def log_milestone(self, milestone):
        seconds_to_milestone = int(time() - self.launch_time)
        print(f'{milestone} after {seconds_to_milestone} seconds.')

    def start_clipping(self):
        auto_clipper_button = self.driver.find_element_by_id('btnMakeClipper')
        while not auto_clipper_button.is_enabled():
            self.make_many_paperclips(10)
        self.update_console_log()
        self.buy_auto_clipper()
        self.log_milestone('First auto clipper purchased')

    # def update_project_list(self):
        # proj_button = self.driver.find_element_by_id('projectListTop')


if __name__ == '__main__':
    my_mogul = ClipMogul()
    my_mogul.launch_game()
    my_mogul.start_clipping()
