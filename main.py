import os
import sys

import submount
import gui


def main():
    openf = [path for path in sys.argv[1:] if os.path.isdir(path)]

    gui.MainWin(openf).mainloop()


if __name__ == '__main__':
    main()
    

# relur 72.