import pyttsx3
import os
import sys


github_link = "https://github.com/shubham-namdev/Prometheus-Stress-Tester"


def talk(text):
    # initialisation
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id) 
    engine.setProperty('rate', 150)
    # running
    engine.say(text)
    engine.runAndWait()


def clear():
    os.system('cls')



def clear_input_buffer():
    try:
        while sys.stdin.read(1) != '':
            pass
    except KeyboardInterrupt:
        pass

def print_br(ch='=') -> None:
    terminal_size = os.get_terminal_size()
    width = terminal_size.columns
    print(ch*width)


def print_message(message, color='white', centered=False, italic=False, end="\n"):
    colors = {
        'green': '\033[92m',    # green
        'red': '\033[91m',      # red
        'yellow': '\033[93m',   # yellow
        'blue': '\033[94m',     # blue
        'magenta': '\033[95m',  # magenta
        'cyan': '\033[96m',     # cyan
        'orange': '\033[33m',    # orange
        'white': '\033[0m'      # white
    }

    styles = {
        'italic': '\033[3m',
        'reset_italic': '\033[23m'
    }

    color_code = colors.get(color, colors['white'])
    reset_code = colors['white']

    if italic:
        message = styles['italic'] + message + styles['reset_italic']

    if centered:
        terminal_size = os.get_terminal_size()
        width = terminal_size.columns
        padding = (width - len(message)) // 2
        print(" " * padding + color_code + message + reset_code, end=end)
    else:
        print(color_code + message + reset_code, end=end)



