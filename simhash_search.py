from __future__ import division, unicode_literals

import sys
import re
import hashlib
import logging
import collections
from itertools import groupby

if sys.version_info[0] >= 3:
    basestring = str
    unicode = str
    long = int
else:
    range = xrange


class Simhash(object):

    def __init__(self, value="$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", f=64, reg=r'[\w\u4e00-\u9fcc]+', hashfunc=None):
        """
        `f` is the dimensions of fingerprints

        `reg` is meaningful only when `value` is basestring and describes
        what is considered to be a letter inside parsed string. Regexp
        object can also be specified (some attempt to handle any letters
        is to specify reg=re.compile(r'\w', re.UNICODE))

        `hashfunc` accepts a utf-8 encoded string and returns a unsigned
        integer in at least `f` bits.
        """

        self.f = f
        self.reg = reg
        self.value = None
        self.all_sentences_hash = []

        if hashfunc is None:
            def _hashfunc(x):
                return int(hashlib.md5(x).hexdigest(), 16)

            self.hashfunc = _hashfunc
        else:
            self.hashfunc = hashfunc

        if isinstance(value, Simhash):
            self.value = value.value
        elif isinstance(value, basestring):
            self.build_by_text(unicode(value))
        elif isinstance(value, collections.Iterable):
            self.build_by_features(value)
        elif isinstance(value, long):
            self.value = value
        else:
            raise Exception('Bad parameter with type {}'.format(type(value)))

    def _slide(self, content, width=4):
        return [content[i:i + width] for i in range(max(len(content) - width + 1, 1))]

    def _tokenize(self, content):
        content = content.lower()
        content = ''.join(re.findall(self.reg, content))
        ans = self._slide(content)
        return ans

    def build_by_text(self, content):
        features = self._tokenize(content)
        features = {k:sum(1 for _ in g) for k, g in groupby(sorted(features))}
        return self.build_by_features(features)

    def build_by_features(self, features):
        """
        `features` might be a list of unweighted tokens (a weight of 1
                   will be assumed), a list of (token, weight) tuples or
                   a token -> weight dict.
        """
        v = [0] * self.f
        masks = [1 << i for i in range(self.f)]
        if isinstance(features, dict):
            features = features.items()
        for f in features:
            if isinstance(f, basestring):
                h = self.hashfunc(f.encode('utf-8'))
                w = 1
            else:
                assert isinstance(f, collections.Iterable)
                h = self.hashfunc(f[0].encode('utf-8'))
                w = f[1]
            for i in range(self.f):
                v[i] += w if h & masks[i] else -w
        ans = 0
        for i in range(self.f):
            if v[i] >= 0:
                ans |= masks[i]
        self.value = ans

    def distance(self, another):
        assert self.f == another.f
        x = (self.value ^ another.value) & ((1 << self.f) - 1)
        ans = 0
        while x:
            ans += 1
            x &= x - 1
        return ans
    # changed
    def distance1(self, value):
        #assert self.f == another.f
        x = (self.value ^ value) & ((1 << self.f) - 1)
        ans = 0
        while x:
            ans += 1
            x &= x - 1
        return ans

    # changed: init_load_sentences
    def init_load_sentence(self, sentences=[]):
        for sent in sentences:
            self.all_sentences_hash.append(Simhash(sent).value)

    # changed: get top near sentence idx
    def search_top(self, sentence, threshold=50):
        # return threshold near all_sentences index.
        if self.all_sentences_hash==[]: return
        resultTop = {}
        cur_simhash = Simhash(sentence)
        for idx in range(len(self.all_sentences_hash)):
            cur_distance = cur_simhash.distance1(self.all_sentences_hash[idx])
            if cur_distance<threshold:
                resultTop[idx] = cur_distance
            #print(cur_simhash.distance1(self.all_sentences_hash[idx]))
        resultTop = sorted(resultTop.items(), key=lambda x:x[1]) # (idx, score)
        res=resultTop[0]
        conf=1-res[1]/64.0
        res=[res[0],conf]
        return res

# test:

if __name__ == "__main__":
    sents = ["i love you", "i like you", "i do not love you"]
    simh = Simhash()
    simh.init_load_sentence(sents)
    while True:
        sentence=raw_input("Your input: ")
        res = simh.search_top(sentence)
        print res
