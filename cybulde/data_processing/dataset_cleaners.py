
from abc import ABC, abstractmethod
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import string
from cybulde.utils.utils import SpellCorrectionModel

class DatasetCleaner(ABC):
    def __call__(self, text: str | list[str]) -> str | list[str]:
        if isinstance(text, str):
           return self.clean_text(text)
        return self.clean_words(text)
       

    @abstractmethod
    def clean_text(self, text:str) -> str:
        """
        Clean the given string
        """
    
    @abstractmethod
    def clean_words(self, words: list[str]) -> list[str]:
        """
        Cleans each word in a list of words
        """


class StopWordsDatasetCleaner(DatasetCleaner):
    def __init__(self) -> None:
        super().__init__()
        self.stopwords: set[str ]= set(stopwords.words("english"))

    def clean_text(self, text: str) -> str:
        cleaned_text = [word for word in word_tokenize(text) if word not in self.stopwords]
        #print(word_tokenize(text))
        return " ".join(cleaned_text)
    
    def clean_words(self, words: list[str]) -> list[str]:
        return [word for word in words if word not in self.stopwords]


class ToLowerCaseDatasetCleaner(DatasetCleaner):
    def clean_text(self, text: str) -> str:
        return text.lower()
    
    def clean_words(self, words: list[str]) -> list[str]:
        return [word.lower() for word in words]


class URLDatasetCleaner(DatasetCleaner):
    def clean_text(self, text: str) -> str:
        return re.sub(r"https\S+","", text,  flags=re.MULTILINE)
    
    def clean_words(self, words: list[str]) -> list[str]:
        return [self.clean_text(word) for word in word]


class PunctuationDatasetCleaner(DatasetCleaner):
    def __init__(self, punctuation: str = string.punctuation) -> None:
        super().__init__()
        self.table = str.maketrans("", "", punctuation)
    
    def clean_text(self, text: str) -> str:
        return " ".join(self.clean_words(text.split()))

    def clean_words(self, words: list[str]) -> list[str]:
        return [word.translate(self.table) for word in words if word.translate(self.table)]


class NonLettersDatasetCleaner(DatasetCleaner):
    def clean_text(self, text: str) -> str:
        return " ".join(self.clean_words(text.split()))
    
    def clean_words(self, words: list[str]) -> list[str]:
        return [word for word in words if word.isalpha()]


class NewLineCharacterDatasetCleaner(DatasetCleaner):
    def clean_text(self, text: str) -> str:
        return text.replace("\n", "")

    def clean_words(self, words: list[str]) -> list[str]:
        return [self.clean_text(word) for word in words]


class NonASCIIDatasetCleaner(DatasetCleaner):
    def clean_text(self, text: str) -> str:
        return " ".join(self.clean_words(text.split()))
    
    def clean_words(self, words: list[str]) -> list[str]:
        return [word for word in words if word.isascii()]


class ReferanceToAccountDatasetCleaner(DatasetCleaner):
    def clean_text(self, text: str) -> str:
        return re.sub(r"@\w+", "", text)
    
    def clean_words(self, words: list[str]) -> list[str]:
        text = " ".join(words)
        return self.clean_text(text.split())


class ReTweetDatasetCleaner(DatasetCleaner):
    def clean_text(self, text: str) -> str:
        return re.sub(r"\bRT\b","", text, flags=re.IGNORECASE)
    
    def clean_words(self, words: list[str]) -> list[str]:
        text = " ".join(words)
        return self.clean_text(text.split())


class SpellCorrectionDatasetCleaner(DatasetCleaner):
    def __init__(self, spell_correction_model: SpellCorrectionModel) -> None:
        super().__init__()
        self.spell_correction_model = spell_correction_model

    def clean_text(self, text: str) -> str:
        return self.spell_correction_model(text)

    def clean_words(self, words: list[str]) -> list[str]:
        text = " ".join(words)
        #print(type(self.clean_text(text)))
        return self.clean_text(text).split()
    

class DatasetCleanerManager:
    def __init__(self, dataset_cleaners: dict[str, DatasetCleaner]) -> None:
        self.dataset_cleaners = dataset_cleaners

    def __call__(self, text: str | list[str]) -> str | list[str]:
        for dataset_cleaner in self.dataset_cleaners.values():
            text = dataset_cleaner(text)
        return text
    


# JUST CODE TO USED TO CHECK THE INDIVIDUAL CLASSES
# print(StopWordsDatasetCleaner().stopwords)
# cleaner = StopWordsDatasetCleaner()
# text ="https://kingy.com I  RT am Kingster. \n Ruler of World! @Sacha number 666 ."
# print(text)
# words = text.split(" ")
# print(words)
# new_text = cleaner.clean_text(text)
# print(new_text)
# new_words =cleaner.clean_words(words)
# lc= ToLowerCaseDatasetCleaner()
# print(lc.clean_text(new_text))
# print(lc.clean_words(new_words))
# urldc = URLDatasetCleaner()
# print(urldc.clean_text(text))
# pun = PunctuationDatasetCleaner()
# words =pun.clean_words(text.split())
# print(words)
# text =pun.clean_text(text)
# print(text)
# nlc = NonLettersDatasetCleaner()
# print(nlc.clean_text(text))
# print(nlc.clean_words(text.split()))
# nl = NewLineCharacterDatasetCleaner()
# print(nl.clean_text(text))
# print(nl.clean_words(text.split()))
# nasci = NonASCIIDatasetCleaner()
# print(nasci.clean_text(text))
# print(nasci.clean_words(text.split()))
# rfc = ReferanceToAccountDatasetCleaner()
# print(rfc.clean_text(text))
#print(rfc.clean_words(text.split()))
# model = SpellCorrectionModel()
# print(model)
# cor = SpellCorrectionDatasetCleaner(model)
# text = "whereis th elove hehad dated forImuch of thepast who couqdn'tread in sixthgrade and ins pired him"
# print(text)
# print(cor(text))
# words = text.split()
# print(words)
# print(cor.clean_words(words))