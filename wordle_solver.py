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
first_word = overall_probs[20][0]

st.header("First word" + str(first_word))
