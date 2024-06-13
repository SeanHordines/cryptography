ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def substitute(line: str, alpha1: str, alpha2: str) -> str:
    newline = ""
    for char in line:
        if char.isalpha():
            char = char.upper()
            index = alpha1.index(char)
            char = alpha2[index]

        newline += char

    return newline

def processFile(inputFilePath: str, outputFilePath: str, alpha1: [str], alpha2: [str]):
        with open(inputFilePath, 'r', encoding='utf-8') as inputFile, \
            open(outputFilePath, 'w', encoding='utf-8') as outputFile:
            for line in inputFile:
                newline = substitute(line, alpha1, alpha2)
                outputFile.write(newline)


class Atbash:
    def __init__(self):
        self.alpha = ALPHABET[::-1]

    def encrypt(self, inputFilePath: str, outputFilePath: str = None) -> str:
        if not outputFilePath:
            temp = inputFilePath.split('.')
            outputFilePath = temp[0] + ".atbash_E." + temp[-1]

        processFile(inputFilePath, outputFilePath, ALPHABET, self.alpha)

        return outputFilePath

    def decrypt(self, inputFilePath: str, outputFilePath: str = None) -> str:
        if not outputFilePath:
            temp = inputFilePath.split('.')
            outputFilePath = temp[0] + ".atbash_D." + temp[-1]

        self.encrypt(inputFilePath, outputFilePath)

        return outputFilePath

class Caesar:
    def __init__(self, shift: int = 13):
        shift = shift % len(ALPHABET)
        self.alpha = ALPHABET[shift:] + ALPHABET[:shift]

    def encrypt(self, inputFilePath: str, outputFilePath: str = None) -> str:
        if not outputFilePath:
            temp = inputFilePath.split('.')
            outputFilePath = temp[0] + ".caesar_E." + temp[-1]

        processFile(inputFilePath, outputFilePath, ALPHABET, self.alpha)

        return outputFilePath

    def decrypt(self, inputFilePath: str, outputFilePath: str = None) -> str:
        if not outputFilePath:
            temp = inputFilePath.split('.')
            outputFilePath = temp[0] + ".caesar_D." + temp[-1]

        processFile(inputFilePath, outputFilePath, self.alpha, ALPHABET)

        return outputFilePath

if __name__ == "__main__":
    test1 = Atbash()
    test1.encrypt("text/sample_message.txt")
    test1.decrypt("text/sample_message.atbash_E.txt")

    test2 = Caesar()
    test2.encrypt("text/the_raven.txt")
    test2.decrypt("text/the_raven.caesar_E.txt")
