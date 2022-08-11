#!/usr/bin/env python3

# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <http://unlicense.org/>

import sys
import subprocess
from os.path import isdir, join, basename, getsize, exists
from os import listdir
from datetime import datetime
import zlib

try:
    import tkinter as tk
    from tkinter import messagebox
    from tkinter import filedialog
    from tkinter import ttk
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
    import tkinter as tk
    from tkinter import messagebox
    from tkinter import filedialog
    from tkinter import ttk

backup_name = datetime.now().strftime('%Y-%m-%d_%H-%M')

max_file_size = 2147483648

directory = None
backup_directory = None

exclude_names = ['__pycache__', 'venv', '.venv', '_venv', '_venv2', '_venv3', '~bromium', 'bromium', '.iso',
                 '.iso.zip', 'virtualbox vms', 'vbox.log', 'vboxhardening.log', '$winreagent', 'Apps', 'onedrivetemp',
                 'programdata', 'program files', 'program files (x86)', 'swsetup', 'windows', 'system32', 'bin', 'dev',
                 'lib32', 'libx32', 'opt', 'recovery', 'run', 'srv', 'tmp', 'var', 'boot', 'lib', 'lib64',
                 'lost+found', 'proc', 'sbin', 'sys', 'usr', 'jars', 'libraries', '.bash_history', '.python_history',
                 '.local', '.config', '.cache', 'swap', '.swap']
exclude_extensions = ('.dat', '.ini', '.exe', '.dll', '.deb', '.dmg', '.app', '.asp', '.bat', '.com', '.gadget', '.inf',
                      '.ink', '.msi', '.prg', '.reg', '.scr', 'shs', 'vbs', '.bin', '.class', '.vxd', '.ocx', '.vmf',
                      '.pkg', '.ipa', '.rpm', '.apk', '.exe.zip', '.bc', 'blf', '.cache', '.crdownload', '.dmp',
                      '.download', '.part', '.partial', '.temp', '.tmp', '.dat', '.rsc', '.upd', '.upg', '.swap',
                      '.vbox', '.vbox-prev', '.vdi', '.iso', '.iso.zip', '.bromium', '.log', '.log.0', '.log.1',
                      '.log.2', '.log.3', '.log.4', '.log.5', '.log.6', '.log.7', '.log.8', '.log.9', '.log.10',
                      '.log.11', '.log.12', '.log.13', '.log.14', '.log.15', '.log0', '.log1', '.log2', '.log3',
                      '.log4', '.log5', '.log6', '.log7', '.log8', '.log9', '.log10', '.log11', '.log12', '.log13',
                      '.log14', '.log15', '.pyc', '.iso', '.iso.zip')


def update_progress_label(index, total, file_name):
    d['value'] = (index * 100) // total
    e['text'] = f"{d['value']}% fertig. Aktuelle Datei: {file_name}"


def int_to_bytes(n):
    r = b''
    x = n
    while x > 0:
        r = bytes([x % 256]) + r
        x //= 256
    return r


def bytes_to_int(n: bytes) -> int:
    """
    convert bytes into an integer

    :param n: the bytes
    :return: the integer
    """
    r = 0
    for p in n:
        r *= 256
        r += p
    return r


def write(data):
    global backup_directory, directory
    if (not isinstance(backup_directory, str)) or (not isinstance(directory, str)) or (not isinstance(data, bytes)):
        raise TypeError()
    for i in range(512):
        if len(data) == 0:
            return None
        cur_path = join(backup_directory, f"{backup_name}_{i}.backup")
        if exists(cur_path):
            if getsize(cur_path) + len(data) <= max_file_size:
                with open(cur_path, 'ab') as handler:
                    handler.write(data)
                return None
            else:
                free = max_file_size - getsize(cur_path)
                if free > 0:
                    with open(cur_path, 'ab') as handler:
                        handler.write(data[:free])
                    data = data[free:]
        else:
            if len(data) < max_file_size:
                with open(cur_path, 'ab') as handler:
                    handler.write(data)
                return None
            else:
                with open(cur_path, 'ab') as handler:
                    handler.write(data[:max_file_size])
                data = data[max_file_size:]
    raise RuntimeError()


def mass_read(path):
    r = b''
    for i in range(512):
        cur_path = f"{path}_{i}.backup"
        if exists(cur_path):
            with open(cur_path, 'rb') as f:
                r += f.read()
        else:
            return r


def get_indexed_files():
    global backup_directory, backup_name
    if not isinstance(backup_directory, str):
        raise TypeError()
    files = {}
    files2 = listdir(backup_directory)
    for i in files2:
        if not i.endswith('.backup'):
            files2.remove(i)
    files2.sort()
    files2.reverse()
    files3 = []
    for i in files2:
        if len(i) > len(backup_name):
            start = i[:len(backup_name)]
            if start not in files3:
                files3.append(start)
    for i in files3:
        content = mass_read(join(backup_directory, i))
        if content != b'':
            offset = 0
            while offset < len(content):
                name_length = bytes_to_int(content[offset:offset + 2])
                offset += 2
                name = content[offset:offset + name_length].decode('utf-8')
                offset += name_length
                data_length = bytes_to_int(content[offset:offset + 5])
                offset += 5
                data_hash = zlib.adler32(content[offset:offset + data_length])
                offset += data_length
                files[name] = data_hash
    return files


def btn_a():
    global directory
    directory = filedialog.askdirectory()


def btn_b():
    global backup_directory
    backup_directory = filedialog.askdirectory()


def btn_c():
    global backup_directory, directory, root
    if (not isinstance(backup_directory, str)) or (not isinstance(directory, str)):
        messagebox.showerror('Fehler', '')
        return None
    c.config(state=tk.DISABLED)
    e['text'] = 'bereits vorhandene Dateien werden gelistet'
    root.update()
    indexed = get_indexed_files()
    e['text'] = 'Dateien werden gezählt'
    root.update()
    files = []
    path = directory
    paths = listdir(path)
    while len(paths) > 0:
        path2 = join(path, paths[0])
        file = paths[0]
        del paths[0]
        if (basename(file).lower() not in exclude_names) and (not basename(file).lower().endswith(exclude_extensions)):
            if isdir(path2):
                for i in listdir(path2):
                    paths.append(join(file, i))
            else:
                files.append(file)
    total = len(files)
    for i, name in enumerate(files):
        update_progress_label(i, total, name)
        root.update()
        with open(join(directory, name), 'rb') as f:
            data = zlib.compress(f.read(), level=9)
        if name in indexed:
            if zlib.adler32(data) == indexed[name]:
                continue
        data_length = int_to_bytes(len(data))
        name_length = int_to_bytes(len(name.encode('utf-8')))
        if len(name_length) > 2:
            raise OverflowError()
        while len(name_length) < 2:
            name_length = b'\x00' + name_length
        write(name_length)
        write(name.encode('utf-8'))
        if len(data_length) > 5:
            raise OverflowError()
        while len(data_length) < 5:
            data_length = b'\x00' + data_length
        write(data_length)
        write(data)
    d['value'] = 100
    e['text'] = 'Backup abgeschlossen'
    root.update()
    c.config(state=tk.NORMAL)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Backuper')
    a = tk.Button(text='Ordner auswählen', command=btn_a)
    b = tk.Button(text='Speicherort auswählen', command=btn_b)
    c = tk.Button(text='Erstellen', command=btn_c)
    d = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=200)
    e = ttk.Label(root, text="Keine Prozesse laufen")
    a.pack()
    b.pack()
    c.pack()
    d.pack()
    e.pack()
    root.mainloop()
