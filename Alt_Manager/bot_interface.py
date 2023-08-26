import os
import sys
import time
import pickle
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common import action_chains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
import math
from Screenshot_Analysis import make_dict_files


class SwarmPlaceBot:
    def __init__(self, username, password, client, template='template_img.png'):
        with open('Dictionaries/button_pos.pickle', 'rb') as fi:  # Read in button pos dictionary
            self.color_to_pos = pickle.loads(fi.read())
        with open('Dictionaries/movement_pos.pickle', 'rb') as fi:  # Read in button pos dictionary
            self.offset_to_pos = pickle.loads(fi.read())
        self.client_dat = client.send({'pos': (0, 0), 'target': (0, 0), 'bad_blocks': [], 'pix_ready': False,
                                       'reboot': False})
        self.client = client
        self.corner_pos = client.corner_pos
        self.ignore_color = client.ignore
        self.user = username
        self.screenshot = os.getcwd() + f'/screenshots/{self.user}.png'
        self.pwd = password
        options = Options()
        options.add_argument("--width=800")
        options.add_argument("--height=600")
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        self.driver = driver
        self.window_size = list(self.driver.get_window_size().values())
        self.wait = WebDriverWait(driver, 10)
        self.target = self.client_dat['target']
        self.pos = self.client_dat['target']
        self.expected_pos = self.pos
        self.ref_image = Image.open(os.getcwd() + f'/templates/{template}').convert('RGB')
        self.image_size = self.ref_image.size
        self.move_function = ['right', 'down']
        self.ready = False  # Ready to place
        self.placed = 0

        self.login()
        time.sleep(2)
        self.open_place()
        time.sleep(1)
        self.check_ready()
        # Consider adding a test of movement as well
        if not self.get_pos():
            sys.exit('Built in test failed: \n' +
                     ' - look at the screenshots as it boots to see the fault\n' +
                     ' - recompute the movement_pos dictionary(follow instructions)')

    def login(self):
        # Go to login page and fill in info and submit
        self.driver.get('https://www.reddit.com/login/')
        login_box = self.driver.find_element(value="loginUsername")
        login_box.send_keys(self.user)
        login_pwd = self.driver.find_element(value="loginPassword")
        login_pwd.send_keys(self.pwd)
        login_pwd.submit()

    def open_place(self):
        # Go to place location and get through annoying popups
        self.driver.get(f'https://www.reddit.com/r/place/?screenmode=fullscreen&cx={self.target[0]}&cy='
                            f'{self.target[1]}&px=10')  # consider changing zoom settings
        # self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Close"]'))).click()
        time.sleep(1.5)
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(100, 100)
        action.pointer_action.click()
        action.perform()

    def update(self):
        pos_good = self.get_pos()
        if not pos_good:
            self.client_dat['reboot'] = True
        self.client_dat['pos'] = self.pos
        self.check_ready()
        self.client_dat['pix_ready'] = self.ready
        bad_pixels = self.get_bad_pixels()  # Get all bad pixels in view
        self.client_dat['bad_blocks'] = bad_pixels
        if self.pos == self.target and self.ready and self.pos in bad_pixels:  # Check to see if a placing is needed
            ref_color = self.get_ref_pixel(self.pos)
            self.pick_color(ref_color)
            self.place_color()
            self.client_dat['ready'] = False
            self.client_dat['bad_blocks'].remove(self.pos)
            self.placed += 1
            print(f'{self.user} has placed {self.placed} pixels')
            self.client_dat = self.client.send(self.client_dat)
            time.sleep(2)
        else:
            self.move_toward_target()
            self.client_dat = self.client.send(self.client_dat)
        self.target = self.client_dat['target']

    def check_ready(self):
        img = Image.open(self.screenshot)
        img.convert('RGB')
        self.ready = img.getpixel((1550, 1191)) == (255, 255, 255, 255)  # Ready to place
        if self.ready:
            for key in self.color_to_pos.keys():
                if img.getpixel(self.color_to_pos[key])[:3] != key and key != 'place':
                    print(img.getpixel(self.color_to_pos[key])[:3], key, self.color_to_pos[key])
                    print('Problem with the button positions')
                    make_dict_files(img)
                    with open('Dictionaries/button_pos.pickle', 'rb') as fi:
                        self.color_to_pos = pickle.loads(fi.read())

    def get_bad_pixels(self):
        bad_pixels = []
        img = Image.open(self.screenshot)
        img.convert('RGB')
        for offset in self.offset_to_pos:
            if offset != 'border_moves':
                pos = (offset[0] + self.pos[0], offset[1]+self.pos[1])
                ref_color = self.get_ref_pixel(pos)
                color = self.get_screen_color(offset, img)
                if ref_color != 'ignore' and ref_color != color:
                    bad_pixels.append(pos)
        return bad_pixels

    def get_closest_color(self, color):
        min_diff = 10000
        ref_color = color
        for key in self.color_to_pos.keys():
            if key != 'place':
                diff = sum((abs(color[0] - key[0]), abs(color[1] - key[1]), abs(color[2] - key[2])))
                if diff < min_diff:
                    ref_color = key
                    min_diff = diff
        return ref_color

    def get_ref_pixel(self, pos):
        try:
            rel_pos = (pos[0] - self.corner_pos[0], pos[1] - self.corner_pos[1])
            color = self.ref_image.getpixel(rel_pos)
            color = list(color[:3])
            color = tuple(color)
            if color == self.ignore_color:  # See if its outside the pattern but in the image
                return 'ignore'
            ref_color = self.get_closest_color(color)
            return ref_color
        except IndexError:
            return 'ignore'

    def get_screen_color(self, offset, img):
        color = img.getpixel(self.offset_to_pos[offset])  # Wrong?
        color = self.get_closest_color(color)
        return color

    def pick_color(self, color):
        location = self.color_to_pos[color]  # Wrong?
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(location[0], location[1])
        action.pointer_action.double_click()
        action.perform()

    def place_color(self):
        location = self.color_to_pos['place']  # Wrong?
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(location[0], location[1])
        action.pointer_action.click()
        action.perform()

    def move_toward_target(self):
        difference = (self.target[0]-self.pos[0], self.target[1]-self.pos[1])
        if difference in self.offset_to_pos:
            self.move_by_offset(difference)
        else:
            border_moves = self.offset_to_pos['border_moves']
            theta = math.atan2(difference[1], difference[0])
            min_theta = 100
            best_move = (0, 0)
            for move in border_moves:
                dtheta = abs(theta - math.atan2(move[1], move[0]))
                if dtheta < min_theta:
                    min_theta = dtheta
                    best_move = move
            self.move_by_offset(best_move)

    def move_by_offset(self, offset):
        location = self.offset_to_pos[offset]  # Wrong ?
        self.expected_pos = (offset[0] + self.expected_pos[0], offset[1] + self.expected_pos[1])
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(location[0], location[1])
        action.pointer_action.click()
        action.perform()

    def get_pos(self):
        url = self.driver.current_url
        coord = [int(url.split('=')[2].split('&')[0]), int(url.split('=')[3].split('&')[0])]
        self.pos = coord
        if self.pos == self.expected_pos:
            return True
        else:
            return False


class FakeSwarmPlaceBot:
    def __init__(self, username, password, client, template='template_img.png'):
        with open('Dictionaries/button_pos.pickle', 'rb') as fi:  # Read in button pos dictionary
            self.color_to_pos = pickle.loads(fi.read())
        with open('Dictionaries/movement_pos.pickle', 'rb') as fi:  # Read in button pos dictionary
            self.offset_to_pos = pickle.loads(fi.read())
        self.client_dat = client.send({'pos': (0, 0), 'target': (0, 0), 'bad_blocks': [], 'pix_ready': False,
                                       'reboot': False})
        self.client = client
        self.corner_pos = client.corner_pos
        self.ignore_color = client.ignore
        self.user = 'game_board'  # Use fake_user for testing of screenshot_Analysis
        self.screenshot = os.getcwd() + f'/screenshots/{self.user}.png'
        self.pwd = password
        self.target = self.client_dat['target']
        self.pos = self.client_dat['target']
        self.expected_pos = self.pos
        self.ref_image = Image.open(os.getcwd() + '/' + template).convert('RGB')
        self.image_size = self.ref_image.size
        self.window_size = (800, 600)
        self.ready = False  # Ready to place
        self.placed = 0

        self.selected_color = (0, 0, 0)  # Default will be changed(since no screenshot will be taken)
        self.last_place = 0  # Time since last placed pixel
        self.frequency = 10  # how often it will consider itself ready(since no screenshot is present)
        self.login()  # Logged in
        time.sleep(2)
        self.open_place()
        time.sleep(1)
        self.check_ready()

    def login(self):
        # Go to login page and fill in info and submit
        pass
        # self.driver.get('https://www.reddit.com/login/')
        # login_box = self.driver.find_element(value="loginUsername")
        # login_box.send_keys(self.user)
        # login_pwd = self.driver.find_element(value="loginPassword")
        # login_pwd.send_keys(self.pwd)
        # login_pwd.submit()

    def open_place(self):
        pass
        # self.driver.get(f'https://www.reddit.com/r/place/?screenmode=fullscreen&cx={self.target[0]}&cy='
        #                 f'{self.target[1]}&px=10')
        # # self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Close"]'))).click()
        # time.sleep(1.5)
        # action = action_chains.ActionBuilder(self.driver)
        # action.pointer_action.move_to_location(100, 100)
        # action.pointer_action.click()
        # action.perform()

    def update(self):
        pos_good = self.get_pos()
        if not pos_good:
            self.client_dat['reboot'] = True
        self.client_dat['pos'] = self.pos
        self.check_ready()
        self.client_dat['pix_ready'] = self.ready
        bad_pixels = self.get_bad_pixels()  # Get all bad pixels in view
        self.client_dat['bad_blocks'] = bad_pixels
        if self.pos == self.target and self.ready and self.pos in bad_pixels:  # Check to see if a placing is needed
            ref_color = self.get_ref_pixel(self.pos)
            self.pick_color(ref_color)
            self.place_color()
            self.client_dat['ready'] = False
            self.client_dat['bad_blocks'].remove(self.pos)
            self.placed += 1
            print(f'{self.user} has placed {self.placed} pixels')
            self.client_dat = self.client.send(self.client_dat)
            time.sleep(2)
        else:
            self.move_toward_target()
            self.client_dat = self.client.send(self.client_dat)
        self.target = self.client_dat['target']
        print(f'Target = {self.target}')

    def check_ready(self):  # Fake
        # img = Image.open(self.screenshot)
        # img.convert('RGB')
        if self.last_place+self.frequency < time.time():  # FAKE
            self.ready = True
        else:
            self.ready = False


    def get_bad_pixels(self):
        bad_pixels = []
        img = Image.open(self.screenshot)  # open screeenshot for performance
        img.convert('RGB')
        for offset in self.offset_to_pos:
            if offset != 'border_moves':
                pos = (offset[0] + self.pos[0], offset[1]+self.pos[1])
                ref_color = self.get_ref_pixel(pos)
                color = self.get_screen_color(offset, img)
                if ref_color != 'ignore' and ref_color != color:
                    bad_pixels.append(pos)
        return bad_pixels

    def get_closest_color(self, color):
        min_diff = 10000
        ref_color = color
        for key in self.color_to_pos.keys():
            if key != 'place':
                diff = sum((abs(color[0] - key[0]), abs(color[1] - key[1]), abs(color[2] - key[2])))
                if diff < min_diff:
                    ref_color = key
                    min_diff = diff
        return ref_color

    def get_ref_pixel(self, pos):
        try:
            rel_pos = (pos[0] - self.corner_pos[0], pos[1] - self.corner_pos[1])
            color = self.ref_image.getpixel(rel_pos)
            color = list(color[:3])
            color = tuple(color)
            if color == self.ignore_color:  # See if its outside the pattern but in the image
                return 'ignore'
            ref_color = self.get_closest_color(color)
            return ref_color
        except IndexError:
            return 'ignore'

    def get_screen_color(self, offset, img):  # Fake
        # Fake
        pos = (offset[0] + self.pos[0], offset[1]+self.pos[1])
        color = img.getpixel(pos)
        color = self.get_closest_color(color)
        return color

    def pick_color(self, color):
        # location = self.color_to_pos[color]
        self.selected_color = color
        # action = action_chains.ActionBuilder(self.driver)
        # action.pointer_action.move_to_location(location[0], location[1])
        # action.pointer_action.double_click()
        # action.perform()

    def place_color(self):  # Fake
        img = Image.open(self.screenshot)  # This is just a fake game board
        img.convert('RGB')
        img.putpixel(self.pos, self.selected_color)
        self.last_place = time.time()
        img.save(self.screenshot)
        # action = action_chains.ActionBuilder(self.driver)
        # action.pointer_action.move_to_location(self.color_to_pos['place'])
        # action.pointer_action.click()
        # action.perform()

    def move_toward_target(self):
        difference = (self.target[0]-self.pos[0], self.target[1]-self.pos[1])
        if difference in self.offset_to_pos:
            self.move_by_offset(difference)
        else:
            border_moves = self.offset_to_pos['border_moves']
            theta = math.atan2(difference[1], difference[0])
            min_theta = 100
            best_move = (0, 0)
            for move in border_moves:
                dtheta = abs(theta - math.atan2(move[1], move[0]))
                if dtheta < min_theta:
                    min_theta = dtheta
                    best_move = move
            self.move_by_offset(best_move)

    def move_by_offset(self, offset):
        # location = self.offset_to_pos[offset]
        self.expected_pos = (offset[0] + self.expected_pos[0], offset[1] + self.expected_pos[1])
        # action = action_chains.ActionBuilder(self.driver)
        # action.pointer_action.move_to_location(location)
        # action.pointer_action.click()
        # action.perform()

    def get_pos(self):
        # url = self.driver.current_url
        # coord = [int(url.split('=')[2].split('&')[0]), int(url.split('=')[3].split('&')[0])]
        self.pos = self.expected_pos
        if self.pos == self.expected_pos:
            return True
        else:
            return False
