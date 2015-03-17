import codecs
import os

class StopWords(object):

    #Mapping between languages and the filenames containing stop words for those languages
    _language_to_file_mapping = {
        'bulgarian': 'stop-words_bulgarian.txt',
        'chinese': 'stop-words_chinese.txt',
        'dutch': 'stop-words_dutch.txt',
        'english': 'stop-words_english.txt',
        'french': 'stop-words_french.txt',
        'german': 'stop-words_german.txt',
        'italian': 'stop-words_italian.txt',
        'polish': 'stop-words_polish.txt',
        'portugese': 'stop-words_portugese.txt',
        'russian': 'stop-words_russian.txt',
        'slovak': 'stop-words_slovak.txt',
        'spanish': 'stop-words_spanish.txt'
    }
    #directory containing the above files
    _stopword_directory = os.path.join('resources', 'stop-words')

    @classmethod
    def words(self,language, additional_stop_list = []):
        #Check if we have a list of stop words for the requested language. If yes, read the corresponding file
        if language in self._language_to_file_mapping:
            stopWordFile = self._language_to_file_mapping[language]
            pathToStopWordFile = os.path.join(self._stopword_directory, stopWordFile)
            stopWordList = [word.strip() for word in codecs.open(pathToStopWordFile, "r", "utf-8")]
            #Append the default stop word list to the stop words requested specifically by the user and return the new list
            stopWordList = stopWordList + additional_stop_list
            return stopWordList
        #If we do not have a stop word list for the requested language, return the stop words the user has specifically requested
        else:
            return additional_stop_list

