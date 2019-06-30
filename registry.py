import os
import sys


def addKey():
    exe_path = os.path.join(os.path.dirname(sys.argv[0]), 'Mounter.exe')
    reg_path = r'HKCR\Directory\shell\Mount Folder\command'
    cmd = 'reg add "{0}" /d "{1} -m ""%1""" /f'.format(reg_path,
                                                          exe_path)
    return os.system(cmd)


def delKey():
    reg_path = r'HKCR\Directory\shell\Mount Folder'
    cmd = 'reg delete "%s" /f' % reg_path

    return os.system(cmd)


def main():
    if '-in' in sys.argv:
        return addKey()

    elif '-un' in sys.argv:
        return delKey()


if __name__ == '__main__':
    sys.exit(main())


# Relur 72.
