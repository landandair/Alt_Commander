import PIL
import selenium

class RPlaceBot:
    interval = .3
    code_to_button = {'0,0': (72, 443),
                      '0,1': (116, 443),
                      '0,2': (160, 443),
                      '0,3': (204, 443),
                      '0,4': (248, 443),
                      '0,5': (292, 443),
                      '0,6': (336, 443),
                      '0,7': (380, 443),
                      '0,8': (424, 443),
                      '0,9': (468, 443),
                      '0,10': (512, 443),
                      '0,11': (556, 443),
                      '0,12': (600, 443),
                      '0,13': (644, 443),
                      '0,14': (688, 443),
                      '0,15': (732, 443),
                      '1,0': (72, 483),
                      '1,1': (116, 483),
                      '1,2': (160, 483),
                      '1,3': (204, 483),
                      '1,4': (248, 483),
                      '1,5': (292, 483),
                      '1,6': (336, 483),
                      '1,7': (380, 483),
                      '1,8': (424, 483),
                      '1,9': (468, 483),
                      '1,10': (512, 483),
                      '1,11': (556, 483),
                      '1,12': (600, 483),
                      '1,13': (644, 483),
                      '1,14': (688, 483),
                      '1,15': (732, 483)}
    color_to_code = {(255, 255, 255, 255): '1,15',  # white
                     (213, 215, 217, 255): '0,15',  # Light grey
                     (138, 141, 144, 255): '1,14',  # Dark grey
                     (0, 0, 0, 255): '1,13',  # Black
                     (150, 107, 52, 255): '1,12',  # Light brown
                     (242, 158, 171, 255): '1,11',  # light Pink
                     (167, 83, 187, 255): '1,9',  # Purple pink
                     (118, 42, 154, 255): '0,9',  # Purple
                     (125, 230, 242, 255): '0,7',  # Sky blue
                     (76, 144, 227, 255): '1,6',  # Blue
                     (44, 81, 159, 255): '0,6',  # Dark blue
                     (154, 234, 108, 255): '0,4',  # Lime green
                     (72, 160, 109, 255): '0,3',  # green
                     (250, 215, 89, 255): '0,2',  # Yellow
                     (244, 171, 60, 255): '1,1',  # Orange
                     (237, 85, 40, 255): '0,1',  # Red
                     (68, 63, 186, 255): '1,7',  # True dark blue
                     (100, 97, 246, 255): '0,8',  # Lighter blue
                     (49, 115, 111, 255): '1,4',  # Dark blue green
                     (236, 77, 129, 255): '0,11',  # PinK
                     (175, 36, 61, 255): '1,0',  # Dark red
                     (68, 156, 168, 255): '0,5',  # Light blue green
                     (92, 200, 128, 255): '1,3',  # Green light
                     (104, 74, 51, 255): '0,12'  # Dark brown
                     }

    def __init__(self, username, password, pos=(478, 44), template='template.png', defend=True):
        self.defend = defend
        self.user = username
        self.pwd = password
        options = Options()
        options.add_argument("--width=800")
        options.add_argument("--height=600")
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        self.driver = driver
        self.window_size = list(self.driver.get_window_size().values())
        self.wait = WebDriverWait(driver, 10)
        self.target = pos
        self.last_place = 0
        self.pos = pos
        self.ref_image = Image.open(os.getcwd() + f'/templates/{template}').convert('RGB')
        self.image_size = self.ref_image.size
        self.move_function = ['right', 'down']
        self.ready = False  # Ready to place
        self.placed = 0

        self.login()
        time.sleep(2)
        self.open_place()
        time.sleep(1)
        self.get_current_color()

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
        if self.defend == True:
            self.driver.get(f'https://www.reddit.com/r/place/?screenmode=fullscreen&cx={self.target[0]}&cy='
                            f'{self.target[1]+random.randint(0, self.image_size[1]-1)}&px=10')
        else:
            self.driver.get(f'https://www.reddit.com/r/place/?screenmode=fullscreen&cx={self.target[0]}&cy='
                            f'{self.target[1]}&px=10')
        # self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Close"]'))).click()
        time.sleep(1.5)
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(100, 100)
        action.pointer_action.click()
        action.perform()

    def update(self):
        if time.time() - self.last_place > self.interval:
            self.last_place = time.time()
            self.get_pos()
            color = ''
            while not color:
                color = self.get_current_color()
            ref_color = self.get_ref_pixel(self.pos)
            if color == ref_color or ref_color == 'ignore':
                self.scroll()
            elif self.ready:
                self.pick_color(ref_color)
                self.place_color()
                self.placed += 1
                print(f'{self.user} has placed {self.placed} pixels')
                time.sleep(2)
            else:
                self.click_center()

    def get_current_color(self):
        self.driver.save_screenshot(f'screenshots/{self.user}.png')
        cwd = os.getcwd()
        img = Image.open(cwd + f'/screenshots/{self.user}.png')
        img.convert('RGB')
        color = img.getpixel((800, 650))
        self.ready = img.getpixel((1550, 1191)) == (255, 255, 255, 255)  # Ready to place
        min_diff = 10000
        for key in self.color_to_code.keys():
            diff = sum((abs(color[0]-key[0]), abs(color[1]-key[1]), abs(color[2]-key[2]), abs(color[3]-key[3])))
            if diff<min_diff:
                min_diff = diff
                if diff < 15:
                    color = key
        if color in self.color_to_code:
            return self.color_to_code[color]
        else:
            print(color)
            return 'bad_color'

    def get_ref_pixel(self, pos):
        rel_pos = (pos[0] - self.target[0], pos[1] - self.target[1])
        color = self.ref_image.getpixel(rel_pos)
        color = list(color[:3])
        color.append(255)
        color = tuple(color)
        min_diff = 10000
        for key in self.color_to_code.keys():
            diff = sum((abs(color[0]-key[0]), abs(color[1]-key[1]), abs(color[2]-key[2]), abs(color[3]-key[3])))
            if diff < 15:
                color = key
            if diff<min_diff:
                min_diff = diff
        if color in self.color_to_code:
            return self.color_to_code[color]
        else:
            return 'ignore'

    def pick_color(self, color):
        self.click_center()
        location = self.code_to_button[color]
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(location[0], location[1])
        action.pointer_action.double_click()
        action.perform()

    def place_color(self):
        self.click_center()
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(526, 550)
        action.pointer_action.click()
        action.perform()

    def scroll(self):
        rel_pos = (-self.target[0] + self.pos[0], self.pos[1] - self.target[1])
        if rel_pos[0] < self.image_size[0]-1 and self.move_function[0] == 'right':
            self.click_right()
        elif rel_pos[0] > 0 and self.move_function[0] == 'left':
            self.click_left()
        elif 0 < rel_pos[1] < self.image_size[1]-1:
            if self.move_function[1] == 'down':
                self.click_down()
            else:
                self.click_up()
            if self.move_function[0] == 'right':
                self.move_function[0] = 'left'
            else:
                self.move_function[0] = 'right'
        else:
            if rel_pos[1] == 0:  # hit top of image
                self.move_function[1] = 'down'
                self.click_down()
            else:
                self.move_function[1] = 'up'
                self.click_up()
            if self.move_function[0] == 'right':
                self.move_function[0] = 'left'
            else:
                self.move_function[0] = 'right'

    def click_up(self):
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(392, 303)
        action.pointer_action.click()
        action.perform()

    def click_down(self):
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(400, 350)
        action.pointer_action.click()
        action.perform()

    def click_right(self):
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(427, 321)
        action.pointer_action.click()
        action.perform()

    def click_left(self):
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(375, 321)
        action.pointer_action.click()
        action.perform()

    def click_center(self):
        action = action_chains.ActionBuilder(self.driver)
        action.pointer_action.move_to_location(402, 321)
        action.pointer_action.click()
        action.perform()

    def get_pos(self):
        url = self.driver.current_url
        coord = [int(url.split('=')[2].split('&')[0]), int(url.split('=')[3].split('&')[0])]
        self.pos = coord