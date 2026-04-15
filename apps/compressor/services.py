import subprocess
import logging

logger = logging.getLogger(__name__)

def compress_pdf(input_path, output_path):
    try:
        subprocess.run([
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/ebook',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_path}',
            input_path
        ], check=True)
        return output_path
    except FileNotFoundError:
        logger.error("Ghostscript is not installed.")
        raise RuntimeError("Ghostscript ('gs') command not found. You must install it on your system first (e.g. `sudo apt-get install ghostscript`).")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ghostscript failed: {e}")
        raise