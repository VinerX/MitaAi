### main.py

from gui import ChatGUI
import os


# + кинуть просты рядом!
# pyinstaller  pyinstaller --onefile --add-data "Promts/*;Promts" --add-data "Promts/**/*;Promts" Main.py
def main():

    gui = ChatGUI()
    gui.run()



if __name__ == "__main__":
    main()