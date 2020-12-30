import subprocess
from shlex import split


class Shell:
    def __init__(self, env=None):
        self.__run = subprocess.run
        self.__pipe = subprocess.PIPE
        self.__devnull = subprocess.DEVNULL
        self.env = env

    def run(self, command, output=True):
        command = split(command)
        if not output:
            ret = self.__run(command, stdout=self.__devnull, stderr=self.__devnull, env=self.env)
        else:
            ret = self.__run(command, stdout=self.__pipe, stderr=self.__pipe, env=self.env)
        return ret
