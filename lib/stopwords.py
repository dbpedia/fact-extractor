#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import os


class StopWords(object):
    """ This module retrieves stop words for a given language
    """
    
    #Mapping between languages and the filenames containing stop words for those languages
    _language_to_file_mapping = {
        'bulgarian': 'stop-words_bulgarian.txt',
        'dutch': 'stop-words_dutch.txt',
        'english': 'stop-words_english.txt',
        'french': 'stop-words_french.txt',
        'german': 'stop-words_german.txt',
        'italian': 'stop-words_italian.txt',
        'portugese': 'stop-words_portugese.txt',
        'russian': 'stop-words_russian.txt',
        'spanish': 'stop-words_spanish.txt'
    }
    #directory containing the above files
    _stopword_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       '..', 'resources', 'stop-words')


    @classmethod
    def words(self, language):
        """ Returns a list of stop words for a specified language

        :param str language: the language whose stop words are required
        :return: Stop words if language is supported. Else an empty list
        :rtype: list
        """
        #Check if we have a list of stop words for the requested language.
        # If yes, read the corresponding file
        if language in self._language_to_file_mapping:
            stopWordFile = self._language_to_file_mapping[language]
            pathToStopWordFile = os.path.join(self._stopword_directory, stopWordFile)
            stopWordList = [word.strip() for word in codecs.open(pathToStopWordFile,
                                                                 "r", "utf-8")]
            return stopWordList
        #If we do not have a stop word list for the requested language,
        # return the stop words the user has specifically requested
        else:
            return []

