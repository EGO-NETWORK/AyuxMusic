from AyuXmusic.core.bot import Siddu
from AyuXmusic.core.dir import dirr
from AyuXmusic.core.git import git
from AyuXmusic.core.userbot import Userbot
from AyuXmusic.misc import dbb, heroku

from .logging import LOGGER

# Initialize directories and git
dirr()
git()

# Initialize misc services
dbb()
heroku()

# Core bot instances
app = Siddu()
userbot = Userbot()

# Platforms import
from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

# ✅ Export db so other files can use:
db = dbb
