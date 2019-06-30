import os
import sys

import gui


def mountDir(path):
    from tkinter import Tk, messagebox as mssgbox
    import attawin

    win = Tk()
    win.state('withdrawn')
    win.iconbitmap('icon.ico')

    path = attawin.normpath(path)
    free_drive = attawin.get_free_drive()

    if not os.path.isdir(path):
        mssgbox.showerror('Invalid Folder Path.',
                          'Wrong path: %s\nCheck folder ' % path +
                          'path for errors.')

    elif attawin.get_path_drive(path):
        mssgbox.showerror('Folder Already Mounted.',
                          'You can not mount a folder under ' +
                          'more than one drive letter.\nDismount ' +
                          'the folder under the drive letter.')
    elif not free_drive:
        mssgbox.showerror('No Free Drive Letters.',
                          'It is not possible to ' +
                          'automatically select a drive ' +
                          'letter for mounting, since there ' +
                          'are no free disks.\nRelease one ' +
                          'of drive letters.')
    else:
        attawin.mount(path, free_drive[0])


def main():
    os.chdir(os.path.dirname(sys.argv[0]))

    if '-m' in sys.argv:
        mountDir(sys.argv[2])
    else:
        app = gui.MainWin()
        app.mainloop()


if __name__ == '__main__':
    main()


# Relur 72.
