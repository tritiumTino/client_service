import subprocess


def ping_hosts(hosts):
    for host in hosts:
        subproc_ping = subprocess.Popen(['ping', host], stdout=subprocess.PIPE)
        for line in subproc_ping.stdout:
            line = line.decode('cp866').encode('utf-8')
            print(line.decode('utf-8'))


def main():
    hosts = ('yandex.ru', 'youtube.com')
    ping_hosts(hosts)


if __name__ == '__main__':
    main()
