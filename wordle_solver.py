import streamlit as st
import random
from collections import defaultdict
from nltk.corpus import words

st.header('Wordle Solver')
words_list = [word.lower() for word in words.words() if len(word) == 5]

word_string = ''.join(words_list)
alpha = 'abcdefghijklmnopqrstuvwxyz'
counts = {}

# create a dictionary of probabilities for each letter 
for letter in alpha:
    counts[letter] = word_string.count(letter)
probs = {}
for letter in alpha:
    probs[letter] = counts[letter]/len(word_string)

# assign probability to each word given its letter
word_probs = []
for word in words_list:
    probability = 1
    for letter in word:
        probability *= probs[letter]
    word_probs.append((word, probability))

# sort the list of all 5 letter words based on probabilities
overall_probs = sorted(word_probs, key = lambda x: x[1], reverse = True)

# randomly choose first word from 50 most probable
first_word = random.choice(overall_probs[:50])[0]


class Rule:
    def __init__(self, letter, i=None):
        self.letter, self.i = letter, i


class RuleMatch(Rule):
    code = '='
    def apply(self, words, matched_counts):
        words = [word for word in words if word[self.i] == self.letter]
        return words


class RuleContainsElsewhere(Rule):
    code = '+'
    def apply(self, words, matched_counts):
        # Only keep words which contain letter (not in position i, or else
        # it would be an exact match (= not +) and which don't contain the
        # letter more often than the number of counted matches.
        words = [word for word in words if self.letter in word
                    and word[self.i] != self.letter
                    and matched_counts[self.letter] <= word.count(self.letter)]
        return words


class RuleExcludedLetter(Rule):
    code = '-'
    def apply(self, words, matched_counts):
        _words = []
        for word in words:
            if not matched_counts[self.letter] and self.letter in word:
                # letter has not been matched anywhere in the word:
                # don't include any words which have this letter.
                continue
            if matched_counts[self.letter] > word.count(self.letter):
                # letter has been matched n times: we can't include
                # words that don't include it at least as many times.
                continue
            _words.append(word)
        words = _words[:]
        return words

RuleCls = {'=': RuleMatch, '+': RuleContainsElsewhere, '-': RuleExcludedLetter}


class Wordle:
    def __init__(self, target_word=None, word_length=5):
        self.target_word = target_word
        self.word_length = word_length
        if target_word:
            self.word_length = len(target_word)

        self.words = [word.lower() for word in words.words() if len(word) == 5]


    def assess_word(self, test_word):

        target = list(self.target_word)
        matched_counts = defaultdict(int)
        rules = [None] * self.word_length
        # Test test_word for the "exact match" and "excluded letter" rules.
        for i, letter in enumerate(test_word):
            if letter == target[i]:
                rules[i] = RuleMatch(letter, i)
                target[i] = '*'
                matched_counts[letter] += 1
            elif letter not in target:
                rules[i] = RuleExcludedLetter(letter, i)

        for i, letter in enumerate(test_word):
            if rules[i]:
                continue
            if letter in target:
                # NB exact matches have already been filtered out.
                rules[i] = RuleContainsElsewhere(letter, i)
                target[target.index(letter)] = '*'
                matched_counts[letter] += 1
            else:
                rules[i] = RuleExcludedLetter(letter, i)

        rule_str = ''.join(rule.code for rule in rules)
        return rules, matched_counts, rule_str


    def parse_rule_codes(self, rule_codes, test_word):
        rules = []
        matched_counts = defaultdict(int)
        for i, letter in enumerate(test_word):
            rules.append(RuleCls[rule_codes[i]](letter, i))
            if rule_codes[i] in '+=':
                matched_counts[letter] += 1
        return rules, matched_counts

    def apply_rules(self, rules, matched_counts):
        for rule in rules:
            self.words = rule.apply(self.words, matched_counts)


    def get_test_word(self):
        k = random.choice(range(len(self.words)))
        return self.words[k], k


    def get_rules_input(self, test_word):
        rule_codes = st.text_input("Input the colors for test word "+ str(test_word))
        return rule_codes


    def interactive(self):
        j = 0
        init = first_word, self.words.index(first_word)
        while len(self.words) > 1:
            test_word, k = self.get_test_word() if j >= 1 else init
            j += 1
            rule_codes = self.get_rules_input(test_word)
            if rule_codes:
                rules, matched_counts = self.parse_rule_codes(rule_codes,test_word)
                self.apply_rules(rules, matched_counts)

                if len(self.words) == 0:
                    st.write('error')
                elif len(self.words) == 1:
                    break
                if test_word in self.words:
                    del self.words[self.words.index(test_word)]
        st.write('the final word is: ' + str(test_word) +', found in ' + str(j)+' attempts.')
wordle = Wordle()
wordle.interactive()
