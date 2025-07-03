def check_code_format(code: str) -> bool:
    if len(code) != 19:
        return True
    skeleton: tuple[str, str, str] = (code[4], code[9], code[14])
    for c in skeleton:
        if c != '-':
            return True
    return False