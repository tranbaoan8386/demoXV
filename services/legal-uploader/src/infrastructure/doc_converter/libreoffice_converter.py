import os
import shutil
import subprocess
import tempfile
from typing import Optional


class LibreOfficeConverter:
    def __init__(self, soffice_cmd: Optional[str] = 'soffice'):
        self.soffice_cmd = soffice_cmd

    def convert_to_docx(self, path: str) -> str:
        # Convert using soffice headless; output to a dedicated converted directory
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        out_dir = os.path.dirname(path)
        # Use a stable temp converted area under the storage layout when possible.
        if 'incoming' in out_dir:
            converted_dir = os.path.join(os.path.dirname(out_dir), 'converted')
        else:
            converted_dir = out_dir
        os.makedirs(converted_dir, exist_ok=True)

        temp_dir = tempfile.mkdtemp(prefix='libreoffice_', dir=converted_dir)
        cmd = [self.soffice_cmd, '--headless', '--convert-to', 'docx', '--outdir', temp_dir, path]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        except subprocess.TimeoutExpired as ex:
            raise RuntimeError(f'LibreOffice conversion timed out after 30s: {ex}')
        if proc.returncode != 0:
            raise RuntimeError(f'LibreOffice conversion failed: {proc.stderr}\n{proc.stdout}')
        base = os.path.splitext(os.path.basename(path))[0]
        new_path = os.path.join(temp_dir, f"{base}.docx")
        if not os.path.exists(new_path):
            raise RuntimeError('Conversion succeeded but output file not found')
        final_path = os.path.join(converted_dir, f"{base}.docx")
        if os.path.exists(final_path):
            os.remove(final_path)
        shutil.move(new_path, final_path)
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
        return final_path
