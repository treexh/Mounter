import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mssgbox
import tkinter.filedialog as fdialog
import threading
import os

import pyperclip

import attawin


class Contex_lsbox:

    def __init__(self, root):
        self.__root = root
        self.__lsbox = None

        self.__menu = tk.Menu(root, tearoff=0)
        self.__menu.add_command(label='Copy Path',
                                command=self.__copy_path_press)

    def show(self, event):
        self.__lsbox = event.widget

        if self.__lsbox.curselection():
            if len(self.__lsbox.selection_get()) > 4:
                self.__menu.post(event.x_root, event.y_root)

    def __copy_path_press(self):
        pyperclip.copy(self.__lsbox.selection_get()[6:])


class Context_ent:

    def __init__(self, root):
        self.__root = root
        self.__ent = None
        self.__menu = tk.Menu(root, tearoff=0)

        self.__menu.add_command(label='Cut',
                                command=self.__cut_press)
        self.__menu.add_command(label='Copy',
                                command=self.__copy_press)
        self.__menu.add_command(label='Paste',
                                command=self.__paste_press)
        self.__menu.add_separator()
        self.__menu.add_command(label='Select All',
                                command=self.__select_all_press)

    def show(self, event):
        self.__ent = event.widget

        if self.__ent.selection_present():
            self.__menu.entryconfig(0, state='normal')
            self.__menu.entryconfig(1, state='normal')
        else:
            self.__menu.entryconfig(0, state='disabled')
            self.__menu.entryconfig(1, state='disabled')

        if pyperclip.paste():
            self.__menu.entryconfig(2, state='normal')
        else:
            self.__menu.entryconfig(2, state='disabled')

        self.__menu.post(event.x_root, event.y_root)

    def __cut_press(self):
        txt = self.__ent.get()
        sel_txt = self.__ent.selection_get()
        cur = self.__ent.index('insert')
        sel_len = len(sel_txt)

        first = last = None

        left_txt = txt[:cur]
        right_txt = txt[cur:]

        if not left_txt:
            first = 0
            last = sel_len

        if not right_txt:
            last = cur
            first = len(txt) - sel_len
        else:
            if txt[cur: cur + sel_len] == sel_txt:
                first = cur
                last = cur + sel_len

            elif txt[cur - sel_len: cur] == sel_txt:
                first = cur - sel_len
                last = cur

        self.__ent.delete(first, last)

    def __copy_press(self):
        pyperclip.copy(self.__ent.selection_get())

    def __paste_press(self):
        clipboard = pyperclip.paste()
        if len(clipboard) < 1000:
            self.__ent.insert('insert', clipboard)

    def __select_all_press(self):
        self.__ent.selection_range(0, 'end')


class MainWin:

    def __init__(self, openf):
        self.__initUI__()

        self.__mount_openf(openf)

    def __initUI__(self):
        self.root = tk.Tk()

        self.__config()
        self.__widget()

        self.browse['command'] = self.browse_press
        self.mount['command'] = self.mount_press
        self.quit['command'] = self.quit_press

        self.combox.bind('<Button-3>', Context_ent(self.root).show)
        self.lsbox.bind('<Button-3>', Contex_lsbox(self.root).show)

        #  close child(sync()) thread.
        self.root.protocol("WM_DELETE_WINDOW", self.quit_press)
        self.root.bind('<F1>', self.reference)

        # mount button change to dismount button, when select mount row.
        self.root.bind('<Button-1>', self.root_press)

        # mount button chage to dismount button, when press Up, Down key.
        self.root.bind('<Up>', self.root_press)
        self.root.bind('<Down>', self.root_press)

        self.free_last = []
        self.mount_last = []
        self.is_running = True
        self.lsbox_drive = lambda: [row[2:3]
                                    for row in self.lsbox.get(0, 'end')]
        self.sync()

    def __mount_openf(self, dirs):
        error_dirs = []
        for dir in dirs:
            drives = attawin.get_free_drive()
            if drives:
                try:
                    attawin.mount(dir, drives[0])
                except:
                    error_dirs.append(dir)
            else:
                error_dirs.append(dir)

        if error_dirs:
            dir_list = ''
            for dir in dir_list:
                dir_list += ' %s\n' % dir

            mssgbox.showwarning('Automounting Error.',
                              'Failed to mount the following ' +
                              'directories:\n' + dir_list)

    def sync(self):
        free = attawin.get_free_drive()
        mount = attawin.get_mount()
        mount_drive = attawin.get_mount_drive()

        if len(mount) > len(self.mount_last):
            new_mount = [drive for drive in mount
                         if drive not in self.mount_last]
            for new_m in new_mount:
                rows = self.lsbox_drive()
                if new_m[0] in rows:
                    i = rows.index(new_m[0])
                    self.lsbox.delete(i)
                    self.lsbox.insert(i, '  %s:  %s' % new_m)
                else:
                    self.lsbox.insert('end', '  %s:  %s' % new_m)

        elif len(mount) < len(self.mount_last):
            new_mount = [drive for drive in self.mount_last
                         if drive not in mount]
            for new_m in new_mount:
                rows = self.lsbox_drive()
                if new_m[0] in rows:
                    self.lsbox.delete(rows.index(new_m[0]))

        free = [drive for drive in free
                if drive not in mount_drive]

        if len(free) > len(self.free_last):
            new_free = [drive for drive in free
                        if drive not in self.free_last]
            for drive in new_free:
                rows = self.lsbox_drive()
                if drive not in rows:
                    rows.extend(drive)
                rows.sort()
                self.lsbox.insert(rows.index(drive), '  %s:' % drive)

        elif len(free) < len(self.free_last):
            new_free = [drive for drive in self.free_last
                        if drive not in free]
            for drive in new_free:
                rows = self.lsbox_drive()
                if drive not in mount_drive:
                    self.lsbox.delete(rows.index(drive))

        self.free_last = free
        self.mount_last = mount

        if self.is_running:
            threading.Timer(1.0, self.sync).start()

    def reference(self, event):
        os.startfile('doc.html')

    def browse_press(self):
        path = fdialog.askdirectory()
        if path:
            self.combox.delete(0, 'end')
            self.combox.insert(0, path)

    def root_press(self, event):
        if self.lsbox.curselection() and \
                len(self.lsbox.selection_get()) > 4:
            self.mount.config(text='Dismount',
                              command=self.dismount_press)
        else:
            self.mount.config(text='Mount', command=self.mount_press)

    def mount_press(self):
        path = attawin.normpath(self.combox.get())

        if not os.path.isdir(path):
            mssgbox.showerror('Directory Not Found.',
                              'Wrong path: %s\nCheck the ' % path +
                              'directory path for errors and try again.')
            return

        if attawin.get_path_drive(path):
            mssgbox.showerror('The Directory Already Mounted.',
                              'You cannot mount a directory under ' +
                              'more than one drive letter. Dismount ' +
                              'the directory under the last letter ' +
                              'and try again.')
            return

        if not self.lsbox.curselection():
            free_drive = attawin.get_free_drive()
            if not free_drive:
                mssgbox.showerror('No Free Drive Letters.',
                                  'It is not possible to ' +
                                  'automatically select a drive ' +
                                  'letter for mounting, since there ' +
                                  'are no free disks.\nRelease one ' +
                                  'of drive letters and try again.')
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

    def dismount_press(self):
        drive = self.lsbox.get(self.lsbox.curselection())[2:3]
        if drive in attawin.get_mount_drive():
            attawin.dismount(drive)
            self.mount.config(text='Mount', command=self.mount_press)

    def quit_press(self):
        self.is_running = False  # close child thread.
        self.root.destroy()

    def __config(self):
        self.root.title('Mounter                             Help[F1]')
        self.root.resizable(False, False)
        self.root.iconbitmap(r'icon.ico')

    def __widget(self):
        self.frame = tk.LabelFrame()
        self.frame.grid(columnspan=3, padx=(5, 3), pady=5)

        self.lsbox = tk.Listbox(self.frame, width=58, bd=0,
                                activestyle='none', height=11,
                                exportselection=True)
        self.lsbox.grid()

        self.scroll = tk.Scrollbar(self.frame, width=15)
        self.scroll.grid(row=0, column=1, sticky='ns')

        self.scroll.config(command=self.lsbox.yview)
        self.lsbox.config(yscrollcommand=self.scroll.set)

        self.frame1 = tk.LabelFrame()
        self.frame1.grid(columnspan=3, padx=(5, 3))

        self.combox = ttk.Entry(self.frame1, width=49)
        self.combox.grid(row=1, padx=(3, 2), pady=3)

        self.browse = tk.Button(self.frame1, text='Browse', width=7, bd=1)
        self.browse.grid(row=1, column=1, padx=(1, 3), pady=3)

        self.mount = tk.Button(self.root, text='Mount', width=12, bd=1)
        self.mount.grid(row=2, padx=5, pady=4, sticky='w')

        self.version = tk.Label(text='v0.4', state='disabled')
        self.version.grid(row=2, column=1)

        self.quit = tk.Button(self.root, text='Quit', width=12, bd=1)
        self.quit.grid(row=2, column=2, padx=5, pady=4, sticky='e')

    def mainloop(self):
        self.root.mainloop()


# relur 72.
