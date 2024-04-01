import os
from clippy_qt.agent import Agent


AGENTS_ROOT = os.getenv('CLIPPY_QT_AGENTS',
                        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'agents')))


class Clippy(Agent):
    """ Good old Clippy, our Superstar! """
    def __init__(self):
        config_path = os.path.join(AGENTS_ROOT, 'Clippy', 'config.json')
        sprite_path = os.path.join(AGENTS_ROOT, 'Clippy', 'map.png')
        sounds_path = os.path.join(AGENTS_ROOT, 'Clippy', 'sounds')
        super(Clippy, self).__init__(config_path, sprite_path, sounds_path)
