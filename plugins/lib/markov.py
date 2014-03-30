# -*- coding: utf-8 -*-

import re
import random


class Markov():
    """Implements a basic Markov model of order 1, for generating
    funny random sentences constructed from a pool of pre-feeded
    sentences."""

    # We need to be able to build sentences forward *and* backward
    # from a given word.
    dico = {}
    backward_dico = {}
    begin_word = '|BEGIN|'
    end_word = '|END|'
    cut_chars = '[,;:]'
    end_chars = '[.!?]'
    blacklist = set()

    def default_data(self):
        return ({}, {})

    def load(self, chan, data):
        """Loads data, coming from instance from a pickled file."""
        # Compatibility with older versions
        if isinstance(data, dict):
            self.dico[chan] = data
            self.backward_dico[chan] = self.build_backward_dico(chan)
        else:
            self.dico[chan] = data[0]
            self.backward_dico[chan] = data[1]

    def dump(self, chan):
        """Dumps the internal dictionary, for instance to be fed to pickle."""
        return (self.dico[chan], self.backward_dico[chan])

    def add_sentence(self, chan, sentence):
        """Feed a sentence to the Markov engine."""
        # We don't want to keep empty sentences
        sentences = [s for s in re.split(self.end_chars, sentence) if s]
        for sentence in sentences:
            current_word = 1
            words = sentence.split()
            words.insert(0, self.begin_word)
            words.append(self.end_word)
            for word in words[1:]:
                self._add_relation(chan,
                                   self.dico,
                                   words[current_word-1],
                                   word)
                self._add_relation(chan,
                                   self.backward_dico,
                                   word,
                                   words[current_word-1])
                current_word += 1

    def get_sentence(self, chan, seed=None):
        """Build a sentence from the graph of learned words. If a seed
        (single word for now) is provided, we try to build a sentence
        including it."""
        if seed is None:
            seed = self.begin_word
        else:
            seed = self._get_key_nocase(seed, self.dico[chan])
            if seed is None:
                return 'Je ne connais pas ce mot.'
        # Build the start of the sentence (backward from seed).
        sentence = self._extend_backward(chan, [seed])
        # Build the end of the sentence (forward).
        sentence = self._extend_forward(chan, sentence)
        return ' '.join(sentence[1:-1])

    def get_stats(self, chan):
        """Number of known words."""
        return len(self.dico[chan])

    def _build_backward_dico(self, chan):
        """Rebuilds self.backward_dico[chan] from self.dico[chan].
        Only used for compatibility with older versions of the plugin."""
        res = {}
        for word, next_words in self.dico[chan].items():
            for next_word, weight in next_words.items():
                if next_word not in res:
                    res[next_word] = {}
                try:
                    res[next_word][word] += weight
                except KeyError:
                    res[next_word][word] = weight
        return res

    def _get_key_nocase(self, word, dico):
        """Search for a key matching the given word (ignoring case).
        Returns the key found, or 'None' is none is found."""
        for k in dico:
            if k.lower() == word.lower():
                return k
        return None

    def _add_relation(self, chan, dico, word, related):
        if word not in dico[chan]:
            dico[chan][word] = {}
        if related in dico[chan][word]:
            dico[chan][word][related] += 1
        else:
            dico[chan][word][related] = 1

    def _extend_forward(self, chan, sentence):
        """Extends the given list of words by adding words to the
        end. The list we return always contains the special 'end'
        symbol as its last element."""
        current_word = sentence[-1]
        while current_word != self.end_word:
            current_word = self._extend_oneword(self.dico[chan], current_word)
            sentence.append(current_word)
        return sentence

    def _extend_backward(self, chan, sentence):
        """Extends the given list of words by adding words to the
        start. The list we return always contains the special 'begin'
        symbol as its head."""
        current_word = sentence[0]
        extension = []
        while current_word != self.begin_word:
            current_word = self._extend_oneword(self.backward_dico[chan],
                                                current_word)
            extension.append(current_word)
        extension.reverse()
        extension.extend(sentence)
        return extension

    def _extend_oneword(self, dico, word):
        word_list = []
        for key, weight in dico[word].items():
            for i in range(0, weight):
                word_list.append(key)
        result = random.choice(word_list)
        return result
