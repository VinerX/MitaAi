### main.py

from gui import ChatGUI
import os

# pyinstaller --add-data "Promts/*;Promts" --add-data "Promts/**/*;Promts" Main.py
def main():

    gui = ChatGUI()
    gui.run()

if __name__ == "__main__":
    main()