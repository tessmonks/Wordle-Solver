import random
import streamlit as st


st.title('Wordle Solver')


wordlist_name = 'common-5-words.txt'
with open(wordlist_name) as fi:
    
    words_list = [word.strip() for word in fi]


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
first_word = random.choice(overall_probs[:20])[0]

st.header("First word: " + str(first_word))

class Guess:
    def __init__(self, letter, i=None):
        word_bank = [word.upper() for word in words.words() if len(word)==5]
        self.word_bank = word_bank
        self.letter, self.i = letter, i
    
class GreenLetter(Guess):
    # keep words from the word bank with letters matching in the position guessed
    code = 'G'
    def apply(self, word_bank, matched_counts):
        words = [word for word in word_bank if word[self.i] == self.letter]
        return words
    
class YellowLetter(Guess):
    code = 'Y'
    # keep words that contain the letter, but not in the position guessed
    def apply(self, word_bank, matched_counts):
        words = [word for word in word_bank if 
                 self.letter in word and
                word[self.i] != self.letter and 
                matched_counts[self.letter] <= word.count(self.letter)]
        return words
    
class NoMatch(Guess):
    code = 'B'
    def apply(self, word_bank, matched_counts):
        words = []
        for word in word_bank:
            # if the letter is not in the word at all
            if not matched_counts[self.letter] and self.letter in word:
                continue
            if matched_counts[self.letter] > word.count(self.letter):
                continue
            words.append(word)
        return words
        
Rule = {'G': GreenLetter, 'Y': YellowLetter, 'B': NoMatch}


class Wordle:
    def __init__(self, target_word=None, word_length=5):
        self.target_word = target_word
        self.word_length = word_length
        if target_word:
            self.word_length = len(target_word)

        self.words = [word.strip() for word in words.words() if len(word)==word_length]
    
    def test_word(self, guess):
        
        target = list(self.target_word)
        matched_letters = defaultdict(int)
        rules = [None] * self.word_length
        
        # check the letters in guess against the target word
        for i, letter in enumerate(guess):
            if letter == target[i]:
                rules[i] = GreenLetter(letter, i)
                target[i] = '*'
                matched_counts[letter] += 1
            elif letter not in target:
                rules[i] = NoMatch(letter, i)
                
        for i, letter in enumerate(guess):
            # check if letter is in word, just not in the current location
            if rules[i]:
                continue
                
            if letter in target:
                rules[i] = YellowLetter(letter, i)
                target[target.index(letter)] = '*'
                matched_counts[letter] += 1
            else:
                rules[i] = NoMatch(letter, i)

        rule_str = ''.join(rule.code for rule in rules)
        return rules, matched_counts, rule_str
    
    def rules(self, rule_codes, guess):
        rules = []
        matched_counts = defaultdict(int)
        for i, letter in enumerate(guess):
            rules.append(Rule[rule_codes[i]](letter, i))
            if rule_codes[i] in '+=':
                matched_counts[letter] += 1
        return rules, matched_counts
    
    def apply_rules(self, rules, matched_counts):
        for rule in rules:
            self.words = rule.apply(self.words, matched_counts)
            
    def choose_guess(self):
        k = random.choice(range(len(self.words)))
        return self.words[k], k
    
    def rules_input(self, guess):
        return input(f'{guess}')
    
    def play(self):
        j = 0
        init = first_word, self.words.index(first_word)
        while len(self.words) > 1:
            guess, k = self.choose_guess() if j else init
            j += 1
            rule_codes = self.rules_input(guess)
            rules, matched_counts = self.rules(rule_codes,guess)
            self.apply_rules(rules, matched_counts)

            if len(self.words) == 0:
                sys.exit('no match')
            elif len(self.words) == 1:
                break
            if guess in self.words:
                del self.words[self.words.index(guess)]
        st.header('The word is '+ str(Wordle.words[0]) +', found in ' + str(j) +' attempts.')
wordle = Wordle()
wordle.play()
        
