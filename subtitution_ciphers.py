import textwrap
from typing import Callable, Optional

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class Cipher:
    """
    Base class for a generic cipher. Provides useful functions across multiple
    cipher types.
    """
    @staticmethod
    def normalizeText(func: Callable) -> Callable:
        """
        Decorator function to take plain text and return only the alphabetical
        characters in upper case. Used for the encrypt/decrypt Text methods.
        """
        def wrapper(self, text: str, *args, **kwargs) -> str:
            # transform each character in text to an uppercase letter
            normalText = ""
            for char in text:
                if char.isalpha(): # do not include non-letter characters
                    normalText += char.upper()

            # input text for the function is only capital letters
            return func(self, normalText, *args, **kwargs)
        return wrapper

    @staticmethod
    def constructFilePath(func: Callable) -> Callable:
        """
        Decorator function to supply an output filepath when none exists. The
        auto-generated file name indicates the class and function in use during
        creation. Used for encrypt/decrypt file methods.
        """
        def wrapper(self, inputFilePath: str, outputFilePath: str = None, *args, **kwargs) -> str:
            if not outputFilePath:
                # separate the name from the extension
                temp = inputFilePath.split('.')
                cipherName = self.__class__.__name__.lower()
                funcName = func.__name__.lower()
                # new file name includes the original name and file extension
                outputFilePath = f"{temp[0]}.{cipherName}.{funcName}.{temp[-1]}"

            return func(self, inputFilePath, outputFilePath, *args, **kwargs)
        return wrapper

    @normalizeText
    def encryptText(self, text: str) -> str:
        """
        Function to be implemented by the subclass. Takes a plain text string
        and returns the encrypted text for the given cipher.
        """
        raise NotImplementedError

    @normalizeText
    def decryptText(self, text: str) -> str:
        """
        Function to be implemented by the subclass. Takes an encrypted text
        string and returns the plain text for the given cipher.
        """
        raise NotImplementedError

    @constructFilePath
    def encryptFile(self, inputFilePath: str, outputFilePath: Optional[str] = None) -> str:
        """
        Handles the input and output for files during the encryption process.
        Takes a filepath for the input and an optional filepath to the output
        and returns the output filepath. Makes a call to encryptText() for
        interal logic.
        """
        with open(inputFilePath, 'r', encoding='utf-8') as inputFile, \
            open(outputFilePath, 'w', encoding='utf-8') as outputFile:
            # grabs input text, encrypts it, and writes it out with line wrapping
            text = inputFile.read()
            newText = self.encryptText(text)
            newText = textwrap.wrap(newText, width=80)
            outputFile.write('\n'.join(newText))

        return outputFilePath

    @constructFilePath
    def decryptFile(self, inputFilePath: str, outputFilePath: Optional[str] = None) -> str:
        """
        Handles the input and output for files during the decryption process.
        Takes a filepath for the input and an optional filepath to the output
        and returns the output filepath. Makes a call to decryptText() for
        interal logic.
        """
        with open(inputFilePath, 'r', encoding='utf-8') as inputFile, \
            open(outputFilePath, 'w', encoding='utf-8') as outputFile:
            # grabs input text, decrypts it, and writes it out with line wrapping
            text = inputFile.read()
            newText = self.decryptText(text)
            newText = textwrap.wrap(newText, width=80)
            outputFile.write('\n'.join(newText))

        return outputFilePath

class Atbash(Cipher):
    """
    Class to model a basic Atbash cipher. This cipher simply substitutes letters
    with the corresponding character in the reverse alphabet. A -> Z, B -> Y, etc.
    """
    def __init__(self):
        self.alpha = ALPHABET[::-1] # reverse alphabet

    @Cipher.normalizeText
    def encryptText(self, text: str) -> str:
        """
        Specific implementation of encryption for an Atbash cipher. This cipher
        simply corresponding letters with the equivalent character in the reverse
        alphabet.
        """
        newText = ""
        for char in text:
            index = ALPHABET.index(char) # find index in original alphabet
            newChar = self.alpha[index] # loolup character from the reverse
            newText += newChar
        return newText

    @Cipher.normalizeText
    def decryptText(self, text: str) -> str:
        """
        Specific implementation of decryption for an Atbash cipher. For Atbash,
        encryption and decryption are equivalent.
        """
        return self.encryptText(text) # encryption and decryption are the same

class Caesar(Cipher):
    """
    Class to model a basic Caesar cipher. This cipher simply substitutes letters
    with the corresponding character in a shifted alphabet. A shift of 3
    represents adding 3 to the index of each letter. A -> D, B -> E, etc.
    """
    def __init__(self, shift: int = 13):
        # adjusts the shifts to be in bounds
        # works with large and negative numbers
        # shift defaults to 13
        shift = shift % len(ALPHABET)
        # slice and rejoin at shift index
        # alphabet restarts with A after Z
        self.alpha = ALPHABET[shift:] + ALPHABET[:shift]

    @Cipher.normalizeText
    def encryptText(self, text: str) -> str:
        """
        Specific implementation of encryption for an Caesar cipher. This cipher
        simply substitutes letters with the corresponding character in a shifted
        alphabet. A shift of 3 represents adding 3 to the index of each letter.
        """
        newText = ""
        for char in text:
            # simple substitution between original and shifted alphabet
            index = ALPHABET.index(char)
            newChar = self.alpha[index]
            newText += newChar
        return newText

    @Cipher.normalizeText
    def decryptText(self, text: str) -> str:
        """
        Specific implementation of decryption for an Caesar cipher. This cipher
        simply unshifts the letters that were shifted during encryption.
        """
        newText = ""
        for char in text:
            # simple substitution back from shifted alphabet to original
            index = self.alpha.index(char)
            newChar = ALPHABET[index]
            newText += newChar
        return newText

class TabulaRecta(Cipher):
    """
    Class to model a Tabula Recta. This method involves creating a table of size
    26x26 where each letter is mapped to every letter including itself. Usually,
    the first character uses the first row/col, the second uses the second row/col
    and so forth.
    """
    def __init__(self, shift: int = 0):
        self.set(shift)

    def set(self, shift: int = 0) -> None:
        """
        Used to set the initial rotation of the alphabet during init and before
        calling encrypt or decrypt. Necessary for a successful decryption. A
        shift of 0 is the same as beginning with an ordinary alphabet.
        """
        # borrowed from Caesar
        shift = shift % len(ALPHABET)
        self.alpha = ALPHABET[shift:] + ALPHABET[:shift]

    @Cipher.normalizeText
    def encryptText(self, text: str) -> str:
        """
        Specific implementation of encryption for an Tabula Recta. This cipher
        simply substitutes letters with the corresponding character current row
        or column. The alphabet is rotated after each use to get the next row or
        column in the table.
        """
        newText = ""
        for char in text:
            # performs a simple substitution with the tabula row
            index = ALPHABET.index(char)
            newChar = self.alpha[index]
            newText += newChar
            # the alphabet is rotated by 1 after every letter
            # equivalent to 26 different Caesar ciphers
            self.alpha = self.alpha[1:] + self.alpha[0]
        return newText

    @Cipher.normalizeText
    def decryptText(self, text: str) -> str:
        """
        Specific implementation of decryption for an Tabula Recta. This cipher
        makes the opposite substituions made during encryption, and rotates in
        the reverse direction. The tabula recta must start in the inverse of the
        position as it was during encryption.
        """
        newText = ""
        # exact same as encyption except for the rotation
        for char in text:
            index = ALPHABET.index(char)
            newChar = self.alpha[index]
            newText += newChar
            # rotates the back character to the front
            self.alpha = self.alpha[-1] + self.alpha[:-1]
        return newText

if __name__ == "__main__":
    # unit tests for each implemented cipher
    test1 = Atbash()
    encryptedFileName = test1.encryptFile("text/sample_message.txt")
    test1.decryptFile(encryptedFileName)

    test2 = Caesar()
    encryptedFileName = test2.encryptFile("text/the_raven.txt")
    test2.decryptFile(encryptedFileName)

    test3 = TabulaRecta(8)
    encryptedFileName = test3.encryptFile("text/lorem_ipsum.txt")
    test3.set(-8)
    test3.decryptFile(encryptedFileName)
