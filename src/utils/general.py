def add_arabic_word(text: str) -> str:
    text = text.replace("ی", "ي")
    text = text.replace("ک", "ك")
    text = text.replace("ه", "ة")
    text = text.replace("و", "ؤ")
    return text
