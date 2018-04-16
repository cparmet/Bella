import nltk
from nltk.tokenize.moses import MosesDetokenizer
import Entrez
from Bio import Medline
import pandas as pd
# from titlecase import titlecase
# import numpy as np
import re
from flask import current_app as app

def is_sentence_case(title, debug=False):
    '''
    Do I think this title is in Sentence case?
    Returns: a confidence from 0 to 1. The closer to 1, more confident.
        >0: I think it's Sentence case (aggressive)
        > or >=0.2: In early tests, I like this performance.
        >=0.5: Could include titles where 1 of 2 candidate words was lowercase (0.5). A little risky.
        >=0.6: Could include titles with only 1 candidate word, but it was lowercase.
    '''

    ## First, exclude titles that are ALL UPPERCASE, like old or weird article titles.
    if title.isupper():
        return 0

    ## Second tokenize the title into a series of sentences
    title_sentences = nltk.sent_tokenize(title)
    # Tokenize each sentence into a series of words
    title_sentences = [nltk.word_tokenize(sent) for sent in title_sentences]
    # Drop first word in each sentence. It'll be capitalized no matter what.
    for i in range(len(title_sentences)):
        title_sentences[i] = title_sentences[i][1:]  # Deleting index 0, i.e. first word

    # Set the filler words we'll ignore, like prepositions, articles, conjunctions that sometimes go Up and sometimes down.
    # They might be lowercase, or uppercase if in a proper noun, or a silly Title Case style that capitalizes 'Of'.
    # V3B: added: as, for, in, vs, vs., with
    # V3C: added 'via', 'via.'
    fillers = ['a', 'according', 'an', 'as', 'and', 'at', 'but', 'by', 'for', 'from',
               'of', 'on', 'or', 'in', 'the', 'to', 'with', 'via', 'via.', 'vs', 'vs.']

    candidates = 0
    lowercase = 0
    lowercase_words = []  # For debug
    capitalized_words = []  # For debug

    # For every sentence in title
    for sentence in title_sentences:
        # For every word in that sentence
        for i, word in enumerate(sentence):

            # 1. Skip words that are all caps. This will also skip acronyms like 'U.K.'
            if word.isupper():
                if debug: print('Upper: ', word)
                continue

            # 2. Skip words with any numbers or symbols in them: punctuation, " 's " tokens, gene/mutation names, etc.
            # V3B: kept hyphenated words in the algorithm UNLESS the word has another number or symbol.
            # V3C: Converted the hyphen exclusion to a hyphenless_word method. Prevents algo from keeping
            #   "12-lead", upon which is_lower() returns false, so this algorithm thinks it's uppercase
            hyphenless_word = word.replace("-", "")
            if not hyphenless_word.isalpha():
                if debug: print('Not alpha: ', word)
                continue

            # 3. Skip camel case words.
            # My logic: since we've ruled out all caps words, a camel case word here remaining at this point
            # would be a word with 1+ uppercase letter AFTER the first letter.
            # After first letter [1:] because word could be initial capped.
            if sum([letter.isupper() for letter in word[1:]]) != 0:
                if debug: print('Camel: ', word)
                continue

                # 4. Skip filler words. Casing of these words isn't informative.
            if word in fillers:
                if debug: print('Filler: ', word)
                continue

            # 5. Skip words following a punctuation mark. Some styles capitalize first word after colon, some don't.
            # Updated: after adding feature to tokenize sentences and dropping first word of each sentence, I
            # removed ['.','?','!'] from this set.
            # V3B: Only skip capitalized words after :.
            # - If it's lowercase after colon, that counts in the calculation.
            if (sentence[(i - 1)] in [':']) and (word[0].isupper()):
                if debug: print('Appears after a "', sentence[(i - 1)], '": ', word)
                continue

            # Remaining!
            candidates += 1  # This is a candidate word that COULD be capitalized.
            if word[0].islower():
                lowercase += 1  # If this word is lowercase, add 1 to our running numerator.
                if debug: lowercase_words.append(word)
            else:
                if debug: capitalized_words.append(word)

    if debug:
        print('SUMMARY: ', lowercase, 'lowercase words out of ', candidates, ' candidates.')
        print(lowercase_words)
        print('Capitalized words: ', capitalized_words)
        print('---------------')

    # Avoid div by zero
    if candidates == 0:
        confidence = 0
    # If I only found one candidate word, but it was lowercase, lower confidence from 1 to 0.6.
    elif (candidates == 1) and (lowercase == 1):
        confidence = 0.6
    else:
        confidence = lowercase / candidates

    return confidence

# Remember to grab email from config file

def retrieve_abstract_and_title(PMID):
    Entrez.email = app.config['EMAIL']
    handle = Entrez.efetch(db="pubmed",rettype="medline", retmode="text", id=PMID)

    record = Medline.read(handle)
    handle.close()
    try:
        abstract = record['AB']
    except:
        abstract = ''
    try:
        title = record['TI']
    except:
        title = ''
    return abstract, title

def retrieve_abstract(PMID):
    Entrez.email = app.config['EMAIL']
    handle = Entrez.efetch(db="pubmed",rettype="medline", retmode="text", id=PMID)

    record = Medline.read(handle)
    handle.close()
    try:
        abstract = record['AB']
    except:
        abstract = ''
    return abstract

def create_word_list():
    # 1. Grab excel files from public S3/
    s3_url= 'https://s3.amazonaws.com/bella_zappa_S3bucket/static/'

    medical_societies = pd.read_excel(s3_url + 'medical_societies.xlsx')['name']
    places = pd.read_excel(s3_url + 'places.xlsx')['name']
    pathogens = pd.read_excel(s3_url + 'pathogens.xlsx')['name']
    diseases = pd.read_excel(s3_url + 'diseases.xlsx')['name']
    word_list = medical_societies.append(places).append(pathogens).append(diseases)
    return word_list

def check_word_list(title, debug = False):
    ## V4D: scan for terms in my word lists of medical societies, places, pathogens, and diseases
    # that should ALWAYS be capitalized.
    searches = create_word_list()
    for term in searches:
        if term.lower() in title:
            try:
                title = title.replace(term.lower(), term)
            #       print('Word list match: Term = ', term, '. title = ', title_sc)
            except:
                if debug: print('Word list error: Term = ', term, '. title = ', title)
    return title


def title_case_to_sentence_case(title, abstract, threshold=0.8, debug=False):
    ## Can't process the title if the abstract is blank or uselessly short
    # V2: Let's punt if abstract is shorter than title. Includes empty abstract.
    # And the "try" construction also lets us bow out gracefully if abstract isn't a string.
    try:
        if len(abstract) <= len(title):
            if debug: print('Bad/no abstract: ', abstract)
            return title
    except:
        if debug: print('Bad/no abstract: ', abstract)
        return title

    ############
    ## Pre-process title
    ############

    # V3: Add dummies with spacers where hyphens are.
    # That way tokenizer will separate parts of the hyphen into their own words.
    pattern = r'\b-\b'  # a hypehn inside a word. Also works for words with >1 hyphen. Backup: r'.-.'
    title = re.sub(pattern, ' *****-***** ', str(title))
    if debug: print('Dehyphenated: ', title)

    # Tokenize title into words and symbols
    title_tc = nltk.word_tokenize(title)
    # V2: Clean up quotation marks. the word_tokenize function mutates "" into `` or '' [29418122]
    # See bottom of function for a related fix to quotation marks.
    # We'll see over time if this screws up any titles that we don't want it to, as well.
    title_tc = [word.replace("``", '"') for word in title_tc]

    # Create a lowercase version of title-case title. This is our baseline.
    # We'll replace with original words from TC as needed
    title_lower = [w.lower() for w in title_tc]

    ############
    ## Prepare abstract
    ############

    # Tokenize abstract into a series of sentences
    abstract_sentences = nltk.sent_tokenize(abstract)
    # Tokenize each sentence into a series of words
    abstract_sentences = [nltk.word_tokenize(sent) for sent in abstract_sentences]
    # Drop first word in each sentence. It'll be capitalized no matter what.
    for i in range(len(abstract_sentences)):
        abstract_sentences[i] = abstract_sentences[i][1:]  # Deleting index 0, i.e. first word

        # V2: And if that leaves a : as the first token drop that
        if abstract_sentences[i][0] in (':'):
            abstract_sentences[i] = abstract_sentences[i][1:]
            # V2: And if next word after : was capitalized, drop that
            # Because if abstract begins "BACKGROUND: Bilateral..."
            # at this point we'll have ':', 'Background'

            if abstract_sentences[i][0][0].isupper():  # Note the extra [0] for first letter of string
                abstract_sentences[i] = abstract_sentences[i][1:]

                ############
    ## Walk through words in the Title
    ############
    # For every word in the Title
    # (skipping first word, which will be initial capped no matter what).
    for i in range(1, len(title_tc)):

        title_word = title_tc[i]

        #####
        # Skip non-informative words
        #####

        # Is the word from title ALL caps? Ignore it.
        if title_word.isupper():
            title_lower[i] = title_word
            if debug: print('CAPS: ', title_word)
            continue

        # V2: Is the word from title in CaMel CaSe? Skip it
        # My logic: since we've ruled out all caps words, a camel case word here
        # remaining at this point would be a word with 1+ uppercase letter AFTER
        # the first letter [1:], because word could be initial capped.
        if sum([letter.isupper() for letter in title_word[1:]]) != 0:
            title_lower[i] = title_word
            if debug: print('Camel: ', title_word)
            continue

            # V2: Does the word have a number or symbol in it? Includes punctuation marks, " 's " tokens, gene/mutation names, etc.
        # V3: Remove special handling of hyphenated words, which should be split into words now

        if not title_word.isalpha():
            title_lower[i] = title_word
            if debug: print('Not alpha: ', title_word)
            continue

        #####
        # Use abstract to capitalize title words.
        #####

        lower_count = 0
        upper_count = 0

        title_lower_word = title_lower[i]

        # For every sentence in Abstract
        for s in abstract_sentences:
            # For every word in that sentence of the Abstract
            for abstract_word in s:
                # Is the word (lowercase) in a lowercase version of this sentence in the Abstract?
                if title_lower_word == abstract_word.lower():
                    # If so, are first letters the same? Then it's lowercase in Abstract
                    if title_lower_word[0] == abstract_word[0]:
                        lower_count += 1
                    # If first letters differ, it's uppercase in Abstract
                    else:
                        upper_count += 1

        # Did the word from title appear at all in Abstract?
        if (lower_count + upper_count) > 0:
            # Were enough instances upper case?
            if upper_count / (lower_count + upper_count) > threshold:
                # If so, capitalize it
                title_lower[i] = title_lower_word.capitalize()

        if debug: print(title_lower_word + ': ', lower_count, ' lowers, ', upper_count, ' uppers')

    #################
    ## Postprocessing
    #################

    # Return first word to original case. Could be all caps, who knows.
    title_lower[0] = title_tc[0]

    # Convert tokenized sentence to string.
    # Use Moses Detokenizer instead of " ".join(title_lower) to handle spacing around punctuation.
    detokenizer = MosesDetokenizer()
    if debug: print('Before detokenizer: ', title_lower)
    title_sc = detokenizer.detokenize(title_lower, return_str=True)

    ## V3: Put hyphens back in where the dummies are
    title_sc = title_sc.replace(' *****-***** ', '-')
    if debug: print('Rehyphenated: ', title_sc)

    ## V2: Clean up
    # (a) Sometimes the Moses Detokenizer leaves "( words)". Fix it to "(words)"
    if title.find("( ") == -1:  # If that (_ pattern DOESN'T appear in the original title, it's an artifact, it's not on purpose
        title_sc = title_sc.replace("( ", "(")  # So get rid of any instances in the converted title.

    # (b) Sometimes the original tokenizer changes " to #'': an extra space with a . [29418122]
    # Check: Is that #'' pattern found in my converted version (with extra space)
    #  and there WASN'T a #'' in the original title (before it got tokenized)? Maybe '' was deliberate.
    if (title_sc.find(" ''") != -1) and (title.find(" ''") == -1):
        title_sc = title_sc.replace(" ''", '"')

    ## V4D: scan for terms in my word lists of medical societies, places, pathogens, and diseases
    # that should ALWAYS be capitalized.
    title_sc = check_word_list(title_sc)

    return title_sc

def capitalize_words_of_new_sentences(title):
    # search for the first letter of a word after a !  ? or .
    # https://regex101.com/r/Ri6m0M/2
    pattern = re.compile(r"(\?|\!|\.)\s(\w)")

    for match in pattern.finditer(title):
        # Break up string into list, so we can change characters
        # Because strings are immutable
        title = list(title)
        index = match.start() + 2
        title[index] = title[index].upper()

        # Turn list back into string.
        # Do this in each iteration because regex finditer works on full strings.
        title = "".join(title)
    return title

# For cases when I don't have an abstract
def simple_sentence_case(title):
    title_sc = title.capitalize()
    title_sc = capitalize_words_of_new_sentences(title_sc)

    ## V4D: scan for terms in my word lists of medical societies, places, pathogens, and diseases
    # that should ALWAYS be capitalized.
    title_sc = check_word_list(title_sc)
    return title

def sentence_caser(PMID, title, comments, detect_threshold = 0.2, caser_threshold = 0.8, debug = False):
    # If it's all uppercase, like 28487907, covert to basic capitalize
    if title.isupper():
        if debug: print('All upper case detected.')
        title_sc = simple_sentence_case(title)
        comments.append("I've tried to convert the title from Title Case to Sentence case. Please double check me!")
        comments.append("Original title:" + title)

    # Is this in sentence case?
    if is_sentence_case(title) >= detect_threshold:
        # Nope, TC. Convert
        if debug: print('Title case detected.')
        # Try to get an abstract.
        abstract = retrieve_abstract(PMID)

        # Was there a real abstract?
        if len(abstract) > len(title):
            # Mine the abstract to convert cases.
            if debug: print('Abstract found. Using it to convert to sentence case.')
            title_sc = title_case_to_sentence_case(title, abstract, threshold=caser_threshold)
        else:
            # Can't use the abstract. But do my best.
            if debug: print('No real abstract. Using simple method to convert to basic sentence case.')
            title_sc = simple_sentence_case(title)

        comments.append("I've tried to convert the title from Title Case to Sentence case. Please double check me!")
        comments.append("Original title:" + title)

    else:
        # Already in sentence case.
        if debug: print('Article is already in sentence case.')
        title_sc = title

    return title_sc, comments