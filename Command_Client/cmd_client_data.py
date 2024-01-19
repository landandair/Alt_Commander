class CmdData:
    def __init__(self, local_mode=False):
        self.local = local_mode
        self.corner_pos = ()
        self.running = True
        self.booted = False
        self.bot_positions = {}
        self.remove_blocks = []
        self.new_blocks = []
        self.goto_range = ()
        self.moves = {}
        self.shuffle = False
        self.reboot = False
        self.health = 0  # % missing integer
