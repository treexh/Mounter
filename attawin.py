import os


subst_exe = 'subst.exe'


def call(argv=''):
    with os.popen('%s %s' % (subst_exe, argv)) as proc:
        out = proc.read().encode('cp1251').decode('cp866')
        if proc.close():
            raise RuntimeError()

        return [row for row in out.split('\n') if row]


def normpath(path):
    ''' Returns the normalized path (does not change case). '''
    if path:
        path = '%s\\' % path if path[-1:] != '\\' else path
        path = os.path.normpath(path)

    return path

def check_subst():
    ''' Returns True, if subst.exe subst.exe utility works correctly,
        therwise returns False. '''
    try:
        call()
    except:
        return False
    else:
        return True


def get_mount():
    ''' Returns a list of tuples(drive, path_folder),
        mounted  directory with subst.exe utility. '''
    return [(row[:1], row[8:]) for row in call()]


def get_mount_drive():
    ''' Returns a list of drives used for mount
        directory with subst.exe utility. '''
    return [row[:1] for row in call()]


def get_free_drive():
    ''' Returns a list of unused drive. '''
    used_drive = get_used_drive()
    return [chr(drive) for drive in range(65, 91)
            if chr(drive) not in used_drive]


def get_used_drive():
    ''' Returns a list of drives used by a System,
        and subst.exe utility. '''
    drives = ['%c' % drive for drive in range(65, 91)
              if os.path.exists('%c:' % drive)]

    drives.extend([drive for drive in get_mount_drive()
                   if drive not in drives])
    drives.sort()

    return drives


def get_path_drive(path):
    ''' Returns a list of drives used for mount the directory. '''
    path = normpath(path)
    return [mount[0] for mount in get_mount()
            if path.lower() == mount[1].lower()]


def mount(path, drive):
    ''' Mounts a directory. ValueError, if drive already used. '''
    if not os.path.isdir(path):
        raise FileNotFoundError('invalid folder name: "%s"' % path)

    if drive.upper() in get_used_drive():
        raise ValueError('drive already used: %s' % drive)

    path = normpath(path)
    call('%s: "%s"' % (drive, path))


def dismount(drive):
    ''' Detach given drive. ValueError, if drive is not mounted. '''
    if drive.upper() not in get_mount_drive():
        raise ValueError('drive is not used for mounting: %s' % drive)

    call('%s: /d' % drive)


def dismount_path(path):
    ''' Detach all drive which the directory 'path' is mounted.
        ValueError, if directory not mounted. '''
    path = normpath(path)
    drives = [mount[0] for mount in get_mount()
              if path.lower() in mount[1].lower()]

    if not drives:
        raise ValueError('directory not mounted: "%s"' % path)

    for drive in drives:
        call('%s: /d' %  drive)


# relur 72.
