from os import system
from os.path import exists
from sys import argv, exit
from threading import Thread
from time import perf_counter, sleep

import requests
from termcolor import colored


def download(url, path):
    is_conected = False
    t = Thread(target=loading)
    t.daemon = True
    t.start()
    r = requests.get(URL, stream=True)
    is_conected = True
    t.join()
    LENGTH = int(r.headers['content-size'])
    _LENGTH = trans_bytes(LENGTH)

    with open(FN, 'wb') as f:
        finished = 0
        st = perf_counter()
        for ch in r:
            finished += f.write(ch)
            rate = finished / LENGTH
            et = perf_counter()
            print('下载进度：', colored('{:.4f}%'.format(rate * 100), 'yellow'),
                  '[',
                  colored(f'{round(rate * 50) * "-"}', 'green').ljust(50, '-'),
                  ']',
                  colored('{} /{}'.format(trans_bytes(finished), _LENGTH), 'blue'),
                  '  ',
                  '用时',
                  colored('{}'.format(trans_time(et - st))),
                  end='        \r', sep='')


def trans_bytes(b):
    '''将b字节转换成更高等级的单位'''
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if b / 1024 >= 1:
            b /= 1024
        else:
            return '{:.3f}{}'.format(b, unit)
    return '{:.3f}{}'.format(b, unit)


def trans_time(s):
    '''将s秒转换成“时:分:秒”的形式'''
    s = round(s)
    second = s % 60
    minute = (s // 60) % 60
    hour = minute // 60
    return f'{hour}:{minute}:{second}'


def loading():
    global is_conected
    while True:
        for i in r'-\|/':
            print(colored('连接资源' + i, 'yellow'), end='\r')
            sleep(0.2)
            if is_conected: break
        if is_conected: break


if argv[1] == 'help':
    print('''download <URL> [<保存地址>] [-S,-s,-h]
-S,--shutdown\t完成后关机
-s,--sleep\t完成后睡眠
-h,--hibernation\t完成后休眠''')
    exit()

URL = argv[1]
try:
    FN = argv[2]
except IndexError:
    l = []
    v1 = 0
    v2 = 0
    for k, v in enumerate(URL):
        if v == '/':
            v1 = k
        elif v == '?':
            v2 = k
    if v2 == 0:
        FN = URL[v1:]
    else:
        FN = URL[v1:v2]
    del l, v1, v2, k, v

if exists(FN):
    match input(colored('文件已存在，是否覆盖？(y/n)', 'yellow')):
        case 'y' | 'Y' | 'yes' | 'YES':
            pass
        case 'n' | 'N' | 'no' | 'NO':
            print(colored('下载失败！'.center(100, '*'), 'gray'))
            exit()
        case _:
            print(colored('？？？？？', 'red'))

download(URL, FN)

print()
print(colored('下载成功！'.center(100, '='), 'blue'))

match argv[3]:
    case '-S' | '--shutdown':
        system('shutdown /p')
    case 's' | '--sleep':
        system('powercfg /H OFF')
        system('rundll32.exe powrprof.dll,SetSuspendState sleep')
        system('powercfg /H ON')
    case '-h' | '-hibernation':
        system('shutdown -h')
