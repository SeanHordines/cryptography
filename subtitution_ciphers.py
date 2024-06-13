import textwrap
from typing import Callable, Optional

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class Cipher:
    @staticmethod
    def normalizeText(func: Callable) -> Callable:
        def wrapper(self, text: str, *args, **kwargs) -> str:
            normalText = ""
            for char in text:
                if char.isalpha():
                    char = char.upper()
                    normalText += char

            return func(self, normalText, *args, **kwargs)
        return wrapper

    @staticmethod
    def constructFilePath(func: Callable) -> Callable:
        def wrapper(self, inputFilePath: str, outputFilePath: str = None, *args, **kwargs) -> str:
            if not outputFilePath:
                temp = inputFilePath.split('.')
                cipherName = self.__class__.__name__.lower()
                funcName = func.__name__.lower()
                outputFilePath = f"{temp[0]}.{cipherName}.{funcName}.{temp[-1]}"

            return func(self, inputFilePath, outputFilePath, *args, **kwargs)
        return wrapper

    @normalizeText
    def encryptText():
        raise NotImplementedError

    @normalizeText
    def decryptText():
        raise NotImplementedError

    @constructFilePath
    def encryptFile(self, inputFilePath: str, outputFilePath: Optional[str] = None) -> str:
        with open(inputFilePath, 'r', encoding='utf-8') as inputFile, \
            open(outputFilePath, 'w', encoding='utf-8') as outputFile:
            text = inputFile.read()
            newText = self.encryptText(text)
            newText = textwrap.wrap(newText, width=80)
            outputFile.write('\n'.join(newText))

        return outputFilePath

    @constructFilePath
    def decryptFile(self, inputFilePath: str, outputFilePath: Optional[str] = None) -> str:
        with open(inputFilePath, 'r', encoding='utf-8') as inputFile, \
            open(outputFilePath, 'w', encoding='utf-8') as outputFile:
            text = inputFile.read()
            newText = self.decryptText(text)
            newText = textwrap.wrap(newText, width=80)
            outputFile.write('\n'.join(newText))

        return outputFilePath

class Atbash(Cipher):
    def __init__(self):
        self.alpha = ALPHABET[::-1]

    @Cipher.normalizeText
    def encryptText(self, text: str) -> str:
        newText = ""
        for char in text:
            index = ALPHABET.index(char)
            newChar = self.alpha[index]
            newText += newChar
        return newText

    @Cipher.normalizeText
    def decryptText(self, text: str) -> str:
        return self.encryptText(text)

class Caesar(Cipher):
    def __init__(self, shift: int = 13):
        shift = shift % len(ALPHABET)
        self.alpha = ALPHABET[shift:] + ALPHABET[:shift]

    @Cipher.normalizeText
    def encryptText(self, text: str) -> str:
        newText = ""
        for char in text:
            index = ALPHABET.index(char)
            newChar = self.alpha[index]
            newText += newChar
        return newText

    @Cipher.normalizeText
    def decryptText(self, text: str) -> str:
        newText = ""
        for char in text:
            index = self.alpha.index(char)
            newChar = ALPHABET[index]
            newText += newChar
        return newText

class TabulaRecta(Cipher):
    def __init__(self):
        self.alpha = ALPHABET


if __name__ == "__main__":
    test1 = Atbash()
    encryptedFileName = test1.encryptFile("text/sample_message.txt")
    test1.decryptFile(encryptedFileName)

    test2 = Caesar()
    encryptedFileName = test2.encryptFile("text/the_raven.txt")
    test2.decryptFile(encryptedFileName)
