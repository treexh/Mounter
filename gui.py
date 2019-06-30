import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mssgbox
import tkinter.filedialog as fdialog
import threading
import os
import pyperclip

import attawin


class ContexListbox:

    def __init__(self, win):
        self.__menu = tk.Menu(win, tearoff=0)
        self.__menu.add_command(label='Copy Path',
                                command=self.__copyPress)

    def show(self, event):
        self.__lsbox = event.widget

        if self.__lsbox.curselection() and \
                len(self.__lsbox.selection_get()) > 4:
            self.__menu.post(event.x_root, event.y_root)

    def __copyPress(self):
        pyperclip.copy(self.__lsbox.selection_get()[6:])


class ContextEntry:

    def __init__(self, win):
        self.__menu = tk.Menu(win, tearoff=0)

        self.__menu.add_command(label='Select All',
                                command=self.__selectAllPress)
        self.__menu.add_command(label='Cut                   Ctrl + X',
                                command=self.__cutPress)
        self.__menu.add_command(label='Copy                Ctrl + C',
                                command=self.__copyPress)
        self.__menu.add_command(label='Paste                Ctrl + V',
                                command=self.__pastePress)

    def show(self, event):
        self.__ent = event.widget

        if self.__ent.selection_present():
            self.__menu.entryconfig(1, state='normal')
            self.__menu.entryconfig(2, state='normal')
        else:
            self.__menu.entryconfig(1, state='disabled')
            self.__menu.entryconfig(2, state='disabled')

        if pyperclip.paste():
            self.__menu.entryconfig(3, state='normal')
        else:
            self.__menu.entryconfig(3, state='disabled')

        self.__menu.post(event.x_root, event.y_root)

    def __cutPress(self):
        text = self.__ent.get()
        selText = self.__ent.selection_get()
        cursor = self.__ent.index('insert')

        first = last = None

        if not text[:cursor]:
            first = 0
            last = len(selText)
        if not text[cursor:]:
            last = cursor
            first = len(text) - len(selText)
        else:
            if text[cursor: cursor + len(selText)] == selText:
                first = cursor
                last = cursor + len(selText)
            elif text[cursor - len(selText): cursor] == selText:
                first = cursor - len(selText)
                last = cursor

        self.__ent.delete(first, last)

    def __copyPress(self):
        pyperclip.copy(self.__ent.selection_get())

    def __pastePress(self):
        clipboard = pyperclip.paste()
        if len(clipboard) < 1000:
            self.__ent.insert('insert', clipboard)

    def __selectAllPress(self):
        self.__ent.selection_range(0, 'end')


class AboutWin:

    def __init__(self):
        self.__initUI__()

    def __initUI__(self):
        self.win = tk.Tk()

        self.config()
        self.widget()

        self.text.insert(1.0,
            'Mounter v0.3.8 by 3xh.\n\nAn application with a GUI for ' +
            'mounting | dismounting a folder under a drive letter ' +
            'using the Subst.exe utility. Through the context menu ' +
            'of the folder or via UI. All folders are automatically ' +
            'dismounted after turning off the computer.\n\n' +
            'Note:\n ● To be able to mount the folder via the ' +
            'context menu, you need to run the installer with ' +
            'administrator rights or run EnableContextMenu.bat ' +
            'located in the application folder with administrator ' +
            'rights.'
            '\n ● Application consumes CPU resources to display actual ' +
            'information about drive letters. The list is updated at' +
            ' 1 second intervals.\n ● Widgets list and input field ' +
            'support context menu.\n\nContacts:\n' +
            ' ● https://vk.com/kormiliz | vk.com\n' +
            ' ● https://github.com/treexh/Mounter | github.com\n' +
            ' ● xh3xh@yandex.ru | mail.yandex.ru')
        self.text.config(state='disabled')

    def config(self):
        self.win.title('About Mounter')
        self.win.iconbitmap('icon.ico')
        self.win.resizable(False, False)
        self.win.wm_attributes('-topmost', True)

    def widget(self):
        self.text = tk.Text(self.win, font=('Tahoma', 10), wrap='word',
                            width=64, height=18, bd=0, bg='#f0f0f0')
        self.text.pack(padx=7, pady=7)

    def mainloop(self):
        self.win.mainloop()


class MainWin:

    def __init__(self):
        self.__initUI__()

    def __initUI__(self):
        self.win = tk.Tk()

        self.config()
        self.widget()
        self.event()

        self.is_running = True
        self.sync()

    def config(self):
        self.win.title('Mounter')
        self.win.resizable(False, False)
        self.win.iconbitmap('icon.ico')

    def widget(self):
        self.frame = tk.LabelFrame()
        self.frame.grid(columnspan=3, padx=(5, 3), pady=5)

        self.lsbox = tk.Listbox(self.frame, activestyle='none',
                                width=58, bd=0, height=11)
        self.lsbox.grid()

        self.scroll = tk.Scrollbar(self.frame, width=15)
        self.scroll.grid(row=0, column=1, sticky='ns')

        self.scroll.config(command=self.lsbox.yview)
        self.lsbox.config(yscrollcommand=self.scroll.set)

        self.frame1 = tk.LabelFrame()
        self.frame1.grid(columnspan=3, padx=(5, 3))

        self.ent = ttk.Entry(self.frame1, width=50)
        self.ent.grid(row=1, padx=(3, 2), pady=3)

        self.browse = tk.Button(self.frame1, text='Browse', bd=1)
        self.browse.grid(row=1, column=1, padx=(2, 3), pady=3)

        self.mount = tk.Button(self.win, text='Mount', width=11, bd=1)
        self.mount.grid(row=2, padx=5, pady=4, sticky='w')

        self.version = tk.Label(text='v0.3.8', state='disabled')
        self.version.grid(row=2, column=1)

        self.quit = tk.Button(self.win, text='Quit', width=11, bd=1)
        self.quit.grid(row=2, column=2, padx=5, pady=4, sticky='e')

    def event(self):
        self.browse['command'] = self.browsePress
        self.mount['command'] = self.mountPress
        self.quit['command'] = self.quitPress

        self.ent.bind('<Button-3>', ContextEntry(self.win).show)
        self.lsbox.bind('<Button-3>', ContexListbox(self.win).show)
        self.version.bind('<Button-1>', self.versionPress)

        self.win.protocol("WM_DELETE_WINDOW", self.quitPress)
        self.win.bind('<Button-1>', self.rootPress)
        self.win.bind('<Up>', self.rootPress)
        self.win.bind('<Down>', self.rootPress)

    def getLsboxDrive(self):
        rows = self.lsbox.get(0, 'end')
        state = []
        for row in rows:
            if len(row) != 4:
                state.append((row[2:3], row[6:]))
            else:
                state.append((row[2:3], ''))

        return state

    def sync(self):
        lsboxState = self.getLsboxDrive()
        sysState = attawin.get_drives_state()

        if len(lsboxState) > len(sysState):
            for i in range(len(lsboxState)):
                if lsboxState[i] not in sysState:
                    self.lsbox.delete(i)

        elif len(lsboxState) < len(sysState):
            for i in range(len(sysState)):
                if sysState[i] not in lsboxState:
                    if sysState[i][1]:
                        self.lsbox.insert(i, '  %s:  %s' % sysState[i])
                    else:
                        self.lsbox.insert(i, '  %s:' % sysState[i][0])
        else:
            for i in range(len(sysState)):
                if sysState[i] != lsboxState[i]:
                    self.lsbox.delete(i)
                    if sysState[i][1]:
                        self.lsbox.insert(i, '  %s:  %s' % sysState[i])
                    else:
                        self.lsbox.insert(i, '  %s:' % sysState[i][0])

        if self.is_running:
            threading.Timer(1.0, self.sync).start()

    def browsePress(self):
        path = fdialog.askdirectory()
        if path:
            self.ent.delete(0, 'end')
            self.ent.insert(0, path)

    def rootPress(self, event):
        if self.lsbox.curselection() and \
                len(self.lsbox.selection_get()) > 4:
            self.mount.config(text='Dismount',
                              command=self.dismountPress)
        else:
            self.mount.config(text='Mount',
                              command=self.mountPress)

    def mountPress(self):
        path = attawin.normpath(self.ent.get())
        if not path:
            mssgbox.showerror('Mount Folder not Specified.',
                              'Folder path is\'nt specified in the ' +
                              'input field.\nSpecify path to the ' +
                              'folder by clicking the "Browse" ' +
                              'button and selecting the desired ' +
                              'folder, or by entering path manually.')

        elif not os.path.isdir(path):
            mssgbox.showerror('Invalid Folder Path.',
                              'Wrong path: %s\nCheck folder' % path +
                              ' path for errors.')

        elif attawin.get_path_drive(path):
            mssgbox.showerror('Folder Already Mounted.',
                              'You can not mount a folder under ' +
                              'more than one drive letter. Dismount ' +
                              'the folder under the drive letter')

        elif not self.lsbox.curselection():
            free_drive = attawin.get_free_drive()
            if not free_drive:
                mssgbox.showerror('No Free Drive Letters.',
                                  'It is not possible to ' +
                                  'automatically select a drive ' +
                                  'letter for mounting, since there ' +
                                  'are no free disks.\nRelease one ' +
                                  'of drive letters.')
            else:
                attawin.mount(path, free_drive[0])

        else:
            row = self.lsbox.selection_get()
            if len(row) == 4:
                if row[2:3] in attawin.get_used_drive():
                    mssgbox.showerror('The Drive Letter Already Used.',
                                      'Free the drive ' +
                                      'letter: %s ' % row[2:3] +
                                      'and try again.\nYou can also ' +
                                      'choose a different drive ' +
                                      'letter to mounted.')
                else:
                    attawin.mount(path, row[2:3])

    def dismountPress(self):
        drive = self.lsbox.get(self.lsbox.curselection())[2:3]
        if drive in attawin.get_mount_drive():
            attawin.dismount(drive)
            self.mount.config(text='Mount', command=self.mountPress)

    def quitPress(self):
        self.is_running = False  # close child thread.
        self.win.destroy()

    def versionPress(self, event):
        AboutWin().mainloop()

    def mainloop(self):
        self.win.mainloop()


# Relur 72.
