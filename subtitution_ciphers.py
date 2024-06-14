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
        def wrapper(self, inputFilePath: str,
                    outputFilePath: str = None,
                    mode: str = 'E', *args, **kwargs) -> str:
            if not outputFilePath:
                # separate the name from the extension
                temp = inputFilePath.split('.')
                cipherName = self.__class__.__name__.lower()
                if mode == 'E':
                    funcName = "encrpyt"
                elif mode == 'D':
                    funcName = "decrpyt"
                else:
                    funcName = "unknown"
                # new file name includes the original name and file extension
                outputFilePath = f"{temp[0]}.{cipherName}.{funcName}.{temp[-1]}"

            return func(self, inputFilePath, outputFilePath, mode, *args, **kwargs)
        return wrapper

    @normalizeText
    def encryptText(self, text: str,  *args, **kwargs) -> str:
        """
        Function to be implemented by the subclass. Takes a plain text string
        and returns the encrypted text for the given cipher.
        """
        raise NotImplementedError

    @normalizeText
    def decryptText(self, text: str,  *args, **kwargs) -> str:
        """
        Function to be implemented by the subclass. Takes an encrypted text
        string and returns the plain text for the given cipher.
        """
        raise NotImplementedError

    @constructFilePath
    def processFile(self, inputFilePath: str,
                    outputFilePath: Optional[str] = None,
                    mode: str = 'E',
                    *args, **kwargs) -> str:
        """
        Handles the input and output for files during the encryption or
        decryption process determined by mode. Takes a filepath for the input
        and an optional filepath to the output, and returns the output filepath.
        Makes a call to encryptText() or decryptText() for interal logic.
        """
        with open(inputFilePath, 'r', encoding='utf-8') as inputFile, \
            open(outputFilePath, 'w', encoding='utf-8') as outputFile:
            # grabs input text, encrypts it, and writes it out with line wrapping
            text = inputFile.read()
            if mode == 'E':
                newText = self.encryptText(text, *args, **kwargs)
            elif mode == 'D':
                newText = self.decryptText(text, *args, **kwargs)
            else:
                print("invalid mode")
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
        Specific implementation of encryption for a Caesar cipher. This cipher
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
        self.offset(shift)
        self.defaultShift = shift

    def offset(self, shift: int = 0) -> None:
        """
        Used to set the initial rotation of the alphabet during init and at the
        beginning of encrypt or decrypt. Necessary for a successful decryption.
        A shift of 0 is the same as beginning with an ordinary alphabet.
        """
        # borrowed from Caesar
        shift = shift % len(ALPHABET)
        self.alpha = ALPHABET[shift:] + ALPHABET[:shift]

    def rotate(self, step: int = 1) -> None:
        """
        Used during encryption and decryption to obtain the next row or column
        in the table. Step represents the number of rows down or column over from
        the current row. Step can be any integer.
        """
        # adjusts the step to be in bounds
        # works with large and negative numbers
        step = step % len(ALPHABET)

        # step must be a non-zero integer
        if step != 0:
            newAlpha = self.alpha[step:] + self.alpha[:step]
            self.alpha = newAlpha

    @Cipher.normalizeText
    def encryptText(self, text: str, shift: int = 0, step: int = 1) -> str:
        """
        Specific implementation of encryption for an Tabula Recta. This cipher
        simply substitutes letters with the corresponding character current row
        or column. The alphabet begins at the shift and is rotated by the value
        of step after each use to get the next row or column in the table.
        """
        #set the initial position of the table
        self.offset(shift or self.defaultShift)

        newText = ""
        for char in text:
            # performs a simple substitution with the tabula row
            index = ALPHABET.index(char)
            newChar = self.alpha[index]
            newText += newChar
            # the alphabet is rotated by 1 after every letter
            # equivalent to 26 different Caesar ciphers
            self.rotate(step)

        # reset the cipher to its default state
        self.offset(self.defaultShift)
        return newText

    @Cipher.normalizeText
    def decryptText(self, text: str, shift: int = None, step: int = 1) -> str:
        """
        Specific implementation of decryption for an Tabula Recta. This cipher
        makes the opposite substituions made during encryption, and rotates in
        the reverse direction. The tabula recta must start in the inverse of the
        position as it was during encryption.
        """
        # encrypt but with opposite params
        return self.encryptText(text, -shift or -self.defaultShift, -step)

class AutoKey(Cipher):
    """
    Class to model an autokey cipher. The encryption incorporates a primer and
    the message into the key. Then each letter of the message is shifted by the
    index of the corresponding letter of the key.
    """
    def __init__(self):
        pass

    @Cipher.normalizeText
    def encryptText(self, text, primer):
        """
        Specific implementation of encryption for an autokey cipher. The key is
        determined by taking a short primer keyword and appending the plaintext
        message. The key is used to shift each letter of the message.
        """
        # key will be slightly longer than the message itself due to the primer
        key = primer + text
        newText = ""
        for char, k in zip(text, key):
            # get the character index of the message and the key
            index1 = ALPHABET.index(char)
            index2 = ALPHABET.index(k)
            # the new character is the original char shifted by the key char
            newChar = ALPHABET[(index1 + index2) % 26]
            newText += newChar
        return newText

    @Cipher.normalizeText
    def decryptText(self, text, primer):
        """
        Specific implementation of decryption for an autokey cipher. This simply
        reverses the shifts done during encrypting by subtracting the indexes
        instead of adding. The key is dynamically build from the decrypted text.
        """
        # full key must be built continuously as the text is decrypted
        key = primer
        newText = ""
        for i, char in enumerate(text):
            index1 = ALPHABET.index(char)
            index2 = ALPHABET.index(key[i])
            # subtract instead of add
            newChar = ALPHABET[(index1 - index2) % 26]
            # add the decrypted char to the end of the key
            key += newChar
            newText += newChar
        return newText

class Vigenere(Cipher):
    """
    Class to model an vigenere cipher. The message to be encrypted is shifted by
    the index of the corresponding letter in the key. If the key is shorter than
    the message, then the key is repeated until the messages ends.
    """
    def __init__(self):
        pass

    @Cipher.normalizeText
    def encryptText(self, text: str, key: str) -> str:
        """
        Specific implementation of encryption for an vigenere cipher. Takes in a
        key and shifts each letter of the message by the index of the next letter
        in the key. The key is repeated when it runs out of new characters.
        """
        newText = ""
        for i, char in enumerate(text):
            # get the character index of the message and the key
            index1 = ALPHABET.index(char)
            index2 = ALPHABET.index(key[i % len(key)])
            # add the indexes to encrypt
            newChar = ALPHABET[(index1 + index2) % 26]
            newText += newChar
        return newText

    @Cipher.normalizeText
    def decryptText(self, text: str, key: str) -> str:
        """
        Specific implementation of decryption for an vigenere cipher. This simply
        reverses the shifts done during encrypting by subtracting the indexes
        instead of adding. Again, the key is repeated as necessary.
        """
        newText = ""
        # essentially the same as encryption
        for i, char in enumerate(text):
            index1 = ALPHABET.index(char)
            index2 = ALPHABET.index(key[i % len(key)])
            # subtract instead of add to undo
            newChar = ALPHABET[(index1 - index2) % 26]
            newText += newChar
        return newText

if __name__ == "__main__":
    # unit tests for each implemented cipher
    test1 = Atbash()
    encryptedFileName = test1.processFile("text/sample_message.txt", mode='E')
    test1.processFile(encryptedFileName, mode='D')

    test2 = Caesar()
    encryptedFileName = test2.processFile("text/orders.txt", mode='E')
    test2.processFile(encryptedFileName, mode='D')

    test3 = TabulaRecta()
    encryptedFileName = test3.processFile("text/lorem_ipsum.txt", mode='E', shift=8, step=7)
    test3.processFile(encryptedFileName, mode='D', shift=8, step=7)

    test4 = AutoKey()
    encryptedFileName = test4.processFile("text/the_raven.txt", mode='E', primer="NEVERMORE")
    test4.processFile(encryptedFileName, mode='D', primer="NEVERMORE")

    test5 = Vigenere()
    encryptedFileName = test5.processFile("text/edict_of_nantes.txt", mode='E', key="HENRYQUATRE")
    test5.processFile(encryptedFileName, mode='D', key="HENRYQUATRE")
