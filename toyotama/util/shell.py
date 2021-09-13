import subprocess


def execute(*command):
    p = []
    for i, c in enumerate(command):
        if i == 0:
            p.append(subprocess.Popen(c, stdout=subprocess.PIPE))
        else:
            p.append(subprocess.Popen(c, stdin=p[-1].stdout, stdout=subprocess.PIPE))

    return p[-1].communicate()
