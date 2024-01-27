import logging
import threading
import tkinter as tk
from os import remove, rmdir, listdir
from os.path import isfile, isdir
from time import sleep
from tkinter import messagebox as mb
from tkinter.ttk import Progressbar, Spinbox

from requests import get, head


def delete(path: str):
    if isfile(path):
        remove(path)
    elif isdir(path):
        if listdir(path) != []:
            for i in listdir(path):
                delete(path + i)
        rmdir(path)


class Downloader:
    isClose=False
    def __init__(self, id, url, dir, filename, thread_num):
        global root
        threading.Thread.__init__(self)
        logging.basicConfig(filename=f'{dir}{filename}.log',
                            filemode='w',
                            encoding='utf-8',
                            format='[%(asctime)s]%(message)s',
                            datefmt='%Y/%m/%d %I:%M:%S %p',
                            level=logging.DEBUG)
        self.id = id
        self.url = url
        self.dir = dir
        self.filename = filename
        self.thread_num = thread_num
        self.lab1 = tk.Label(root, text=f'文件{filename}下载中')
        self.lab2 = tk.Label(root, text='?B/?B')
        self.lab_speed=tk.Label(root, text='?B/s')
        self.bar = Progressbar(root, length=800, mode="indeterminate")
        self.bar.grid(row=5 + id, column=1, sticky='w')
        self.lab1.grid(row=5 + id, column=0, sticky='w')
        self.lab2.grid(row=5 + id, column=2,sticky='w')
        self.lab_speed.grid(row=5 + id, column=3,sticky='w')
        self.bar['value'] = 0
        root.update()
        self.bar.start(5)
        root.update()
        self.r = head(url)
        self.bar.stop()
        root.update()
        if self.r.ok:
            self.size = self.r.headers['content-length']
            logging.info(f'文件{filename}已就绪')
        else:
            logging.warning(f'文件{filename}连接失败！')
            mb.showwarning(self.r.status_code, self.r.reason)
            self.bar.destroy()
            self.lab1.destroy()
            root.update()

    def run(self):
        global root
        logging.info(f'任务{self.filename}开始下载')
        self.size = int(self.r.headers['content-length'])
        self.bar['mode'] = 'determinate'
        self.bar['maximum'] = self.size
        self.bar['value'] = 0
        self.lab2['text'] = f'0B/{self.size}'
        self.lab_speed=f'0B/s'
        root.title('Downloader 0%')
        root.update()
        logging.info(f'任务{self.filename}进度条初始化成功')

        threads = []
        with open(self.dir + self.filename, 'wb') as self.file:
            if self.size % 4096 == 128:
                block = self.size // 4096
            else:
                block = self.size // 4096 + 1
                self.finished = 0
                self.finished_size = 0
                start = 0
            for i in range(1, block + 1):
                end = i * 4096
                t = threading.Thread(target=self.download, args=(i, start, end), name=f'文件{self.filename}的线程{i}')
                t.daemon = True
                t.start()
                threads.append(t)
                while len(threads) >= self.thread_num:
                    for k, v in enumerate(threads):
                        v.join()
                        logging.info(f'线程{k}已回收！')
                self.finished += 1
                start = end + 1
        for k, v in enumerate(threads):
            v.join()
            logging.info(f'线程{k}已回收！')
        speedThread.join()
        logging.info(f'文件{self.filename}下载成功')
        mb.showinfo('INFO', f'文件{self.filename}下载成功')
        self.close()

    def close(self):
        self.isClose=True
        self.bar.destroy()
        self.lab1.destroy()
        self.lab2.destroy()
        self.lab_speed.destroy()
        logging.shutdown()
        delete(self.dir + f'{self.filename}.log')

    def download(self, id: int, start, end):
        global root, lock
        logging.info(f'文件{self.filename}的线程{id}开始!')
        r = get(self.url, headers={f'Range': f'bytes={start}-{end}'}, stream=True)
        block = b''
        for i in r.iter_content(8):
            block += i
        while self.finished == id - 1: pass
        with lock:
            size = self.file.write(block)
            self.file.flush()
        del block
        self.bar.step(size)
        self.finished_size += size
        self.lab2['text'] = f'{self.finished_size}B/{self.size}B'
        root.title('Downloader %.3f%%'%(self.finished_size/self.size*100))
        root.update()
        logging.info(f'文件{self.filename}的线程{id}结束!')
        self.finished += 1
    def speed(self):
        global root
        while self.isClose:
            st=self.finished_size
            sleep(1)
            en=self.finished_size
            self.lab_speed['text']=f'{en-st}B/s'


def start():
    global root, en_url, en_url, en_url, spin_thread_num, btn_submit
    btn_submit.destroy()
    en_url.configure(state='readonly')
    en_dir.configure(state='readonly')
    en_fn.configure(state='readonly')
    spin_thread_num.configure(state='readonly')
    downloader = Downloader(1, en_url.get(), en_dir.get(), en_fn.get(), int(spin_thread_num.get()))
    t = threading.Thread(target=downloader.run, name='下载任务')
    t.daemon = True
    speedThread = threading.Thread(target=downloader.speed)
    speedThread.daemon = True

    speedThread.start()
    t.start()
    t.join()
    speedThread.join()


lock: threading.Lock = threading.Lock()

root = tk.Tk('Downloader')
root.title('Downloader')

lab_url = tk.Label(root, text='URL')
lab_dir = tk.Label(root, text='下载目录')
lab_fn = tk.Label(root, text='文件名')
lab_thread_num = tk.Label(root, text='线程数')
en_url = tk.Entry(root, width=100)
en_dir = tk.Entry(root, width=100)
en_fn = tk.Entry(root, width=100)
spin_thread_num = Spinbox(root, from_=1, to=256, format='%.0f')
mainThread = threading.Thread(target=start, name='GO')
btn_submit = tk.Button(root, text='开始', command=mainThread.start)

lab_url.grid(row=0, column=0, sticky='w')
lab_dir.grid(row=1, column=0, sticky='w')
lab_fn.grid(row=2, column=0, sticky='w')
lab_thread_num.grid(row=3, column=0, sticky='w')
en_url.grid(row=0, column=1, sticky='w')
en_dir.grid(row=1, column=1, sticky='w')
en_fn.grid(row=2, column=1, sticky='w')
spin_thread_num.grid(row=3, column=1, sticky='w')
btn_submit.grid(row=4, column=0)

root.mainloop()

try:
    mainThread.join()
except RuntimeError:
    pass
