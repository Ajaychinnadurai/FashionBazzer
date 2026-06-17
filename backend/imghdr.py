"""
Mock imghdr module for Python 3.13+ compatibility.
Provides the `what` function to detect image formats, replacing the standard library module
which was removed in Python 3.13.
"""

def what(file, h=None):
    """
    Detect image type from file content or header bytes.
    Matches standard library imghdr.what interface.
    """
    if h:
        if h.startswith(b'\xff\xd8\xff'):
            return 'jpeg'
        elif h.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'png'
        elif h.startswith(b'GIF87a') or h.startswith(b'GIF89a'):
            return 'gif'
        elif h.startswith(b'RIFF') and h[8:12] == b'WEBP':
            return 'webp'
    else:
        try:
            if hasattr(file, 'read'):
                pos = file.tell()
                header = file.read(32)
                file.seek(pos)
            else:
                with open(file, 'rb') as f:
                    header = f.read(32)
            return what(None, header)
        except Exception:
            pass
    return None
