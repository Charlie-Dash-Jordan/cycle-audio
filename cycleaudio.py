# !/usr/bin/python
# cycleaudio.py, Charlie Jordan, 3/24/2025

from pathlib import Path
import subprocess
import traceback
from tkinter.messagebox import showerror
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='cycleaudio.log', level=logging.INFO, filemode='w')

logger.info('Import gi')
import gi

logger.info('Requiring versions')
gi.require_version("Gtk", "3.0")
gi.require_version("GLib", "2.0")
gi.require_version('AyatanaAppIndicator3', '0.1')
logger.info('Import Gtk')
from gi.repository import Gtk as gtk # type: ignore
logger.info('Import Glib')
from gi.repository import GLib as glib # type: ignore
logger.info('Import AppIndicator')
from gi.repository import AyatanaAppIndicator3 as appindicator # type: ignore

CUR_DIR = Path(__file__).parent
HEADPHONES_PATH = CUR_DIR / "headphones.png"
SPEAKER_PATH = CUR_DIR / "speaker.png"
QUESTION_PATH = CUR_DIR / "question.png"


class Prog:
    def __init__(self):
        logger.info('Build indicator')
        self.indicator = appindicator.Indicator.new(
            "cycleaudiotray",
            str(QUESTION_PATH),
            appindicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.make_menu())
        
        self.dev_name = ''
        self.set_icon_from_dev_name(self.get_audio_device())
        logger.info('Starting watch_swap listener')
        glib.timeout_add(100, self.watch_swap)
    
    def mainloop(self):
        logger.info('Starting Main Loop')
        gtk.main() # type: ignore

    def make_menu(self):
        logger.info('Building Menu')
        menu = gtk.Menu() # type: ignore
        
        logger.info('Making device menu')
        self.device_menu_item = gtk.MenuItem(label='???') # type: ignore
        self.device_menu_item.set_sensitive(False)
        menu.append(self.device_menu_item)
        
        logger.info('Making Swap and Remove Menu')
        menu.append(gtk.SeparatorMenuItem()) # type: ignore
        swap_menu = gtk.MenuItem(label='Swap Output') # type: ignore
        swap_menu.connect('activate', self.run_cycle_audio)
        menu.append(swap_menu)
        exit_item = gtk.MenuItem(label='Remove App Indicator') # type: ignore
        exit_item.connect('activate', self.close)
        menu.append(exit_item)
        
        logger.info('Show menu')
        menu.show_all()
        return menu
        
    def run_cycle_audio(self, _):
        logger.info('Start cycleaudio.sh')
        p = subprocess.Popen(
            str(CUR_DIR / "cycleaudio.sh"),
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if p.stdout == None:
            logger.info('p.stdout == None')
            return
        for line in iter(p.stdout.readline, ''):
            # print(line, end='', flush=True)
            logger.info("p.stdout: " + line.rstrip())
            if line.startswith('DEVNAME='):
                dev_name = line[8:-1]
                logger.info("DEVNAME found")
                self.set_icon_from_dev_name(dev_name)
                break
    
    def set_icon_from_dev_name(self, dev_name):
        logger.info("Setting icon from dev name")
        logger.info("dev_name: " + dev_name)
        if dev_name == 'Line Out':
            path = str(HEADPHONES_PATH)
            text =  "Headphones"
        elif dev_name == 'Speakers':
            path = str(SPEAKER_PATH)
            text =  "Speakers"
        else:
            path = str(QUESTION_PATH)
            text =  "Unknown"
        logger.info("path: " + path)
        logger.info("text: " + text)
        logger.info("text: " + text)
        self.indicator.set_icon_full(path, text)
        logger.info("Setting Label")
        self.device_menu_item.set_label(f"Device: {text}")
        self.dev_name = dev_name

    def get_audio_device(self, quiet=False):
        logger.info("Running getdevname.sh")
        p = subprocess.Popen(
            str(CUR_DIR / "getdevname.sh"),
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if p.stdout == None:
            logger.info("p.stdout == None")
            return
        for line in iter(p.stdout.readline, ''):
            if not quiet:
                logger.info("p.stdout: " + line.rstrip())
            if line.startswith('DEVNAME='):
                logger.info("DEVNAME found")
                dev_name = line[8:-1]
                return dev_name

    def watch_swap(self):
        new_dev_name = self.get_audio_device(quiet=True)
        if new_dev_name != self.dev_name:
            logger.info("dev_name difference, setting icon")
            self.set_icon_from_dev_name(new_dev_name)
        return True

    def close(self, _):
        logger.info("Closing...")
        gtk.main_quit() # type: ignore

if __name__ == "__main__":
    logger.info("Starting Program")
    try:
        p = Prog()
        p.mainloop()
    except Exception:
        logger.error("Exception found!")
        logger.error("=== Traceback Start")
        for line in traceback.format_exc().split('\n'):
            logger.error(line)
        logger.error("=== Traceback End")
        showerror(
            "Cycle Audio Error",
            "Cycle Audio encountered a fatal erorr. See cycleaudio.log for details.",
        )
    logger.info("Closing Program")
