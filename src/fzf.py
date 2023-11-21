import subprocess
from dataclasses import dataclass, field
from subprocess import PIPE


def _get_listen(server_port):
    if server_port <= 0:
        return []
    else:
        return ["--listen", str(server_port)]


def _get_cmd_list_from_options(options):
    ls = []
    for k, v in options.items():
        if v is True:
            ls.append(k)
        else:
            ls.append(k)
            ls.append(v)
    return ls


@dataclass
class FzfTask():
    pass


@dataclass
class Fzf():
    task: FzfTask

    def async_start_with_list(self, ls):
        cmd = ["fzf", "--listen"] + _get_cmd_list_from_options(self.task.options)
        proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, text=True)
        assert proc.stdin is not None
        proc.stdin.write("\n".join(ls))
        return proc
