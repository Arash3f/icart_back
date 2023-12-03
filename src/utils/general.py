def add_arabic_word(text: str) -> str:
    text = text.replace("ی", "ي")
    text = text.replace("ک", "ك")
    text = text.replace("ا", "أ")
    return text
