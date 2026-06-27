from io import BytesIO
import qrcode


def generate_qr_bytes(data: str) -> bytes:
    """PNG QR-кода в виде bytes (для InputMediaBuffer)"""
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()