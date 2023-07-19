import subprocess
import sys
from typing import List, Tuple


class Executor:
    """
    Class that represents a running procedure
    """

    def __init__(self, arguments: List[str]):
        self.run_command = arguments
        python = self.find_python3_interpreter()
        if python is None:
            raise FileNotFoundError("No python3 interpreter could be found")
        self.run_command.insert(0, python)
        self.process = subprocess.Popen(
                self.run_command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True)

    def find_python3_interpreter(self):
        """
        Find the python 3 interpreter so that we can run the command with it.
        """
        # Check if the current Python executable is Python 3
        if sys.version_info[0] == 3:
            return sys.executable
        else:
            # Search for Python 3 in the system path
            for path in sys.path:
                python3_interpreter = path + "/python3"
                try:
                    subprocess.run([python3_interpreter, "--version"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
                    return python3_interpreter
                except FileNotFoundError:
                    pass
            print("Python 3 interpreter not found.")
            return None

    def is_done(self) -> bool:
        if self.process.poll() is not None:
            return True
        return False

    def get_output_line(self) -> Tuple[str, str]:
        if self.process.poll() is not None:
            stderr = self.process.stderr.read()
            if stderr is None:
                stderr = ""
            stdout = self.process.stdout.read()
            if stdout is None:
                stdout = ""
            return (stdout, stderr)
        else:
            return self.process.communicate()


