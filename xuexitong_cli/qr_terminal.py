def generate_terminal_qr(url_text):
    """
    轻量级无依赖终端二维码渲染（如果本地没有 qrcode 库）
    优先尝试 import qrcode，若无则输出字符提示并调用系统浏览器展示
    """
    try:
        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(url_text)
        qr.make(fit=True)
        # 用终端反白块打印
        lines = []
        matrix = qr.get_matrix()
        for row in matrix:
            line = "".join(["██" if not cell else "  " for cell in row])
            lines.append(line)
        return "\n".join(lines)
    except Exception:
        return None
