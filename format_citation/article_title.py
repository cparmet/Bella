import re

def capitalize_words_after_colons(title):
    ''' For every colon, capitalize the first word after the colon.
    Good example with two colons: PMID = 24778283
        Systematic review: efficacy and safety of medical marijuana in selected neurologic disorders: report of the
        Guideline Development Subcommittee of the American Academy of Neurology.
    Note: require a space between colon and word.
        Because some medical terms, like mutations, include : in the middle of the 'word'. We want to ignore those.
    '''
    # search for ": a"
    pattern = re.compile(r":\s(.)")

    for match in pattern.finditer(title):
        # Break up string into list, so we can change characters
        # Because strings are immutable
        title = list(title)
        index = match.start() + 2  # +2 because [0] : [1] space [2] letter
        title[index] = title[index].upper()

        # Turn list back into string.
        # Do this in each iteration because regex finditer works on full strings.
        title = "".join(title)

    return title

def format_title(record):
    try:
        title = record['Title']
    except:
        title = ''
        print("Bark: I couldn't find the title of the article.")

    # Strip out funny html tags from the Pubmed title e.g., see PMID 29266283
    funny_tags = ['<sup>', '</sup>', '<sub>', '</sub>', '<b>', '</b>', '<i>', '</i>', '<u>', '</u>']
    for tag in funny_tags:
        title = re.sub(tag, '', title)

    # Is the title in brackets because it's translated from a foreign language? like 26753416
    # If so, remove [ ]. Note right bracket is second to last character, because last should be a period.
    if (title[0] == '[') and (title[-2] == ']'):
        title = title[1:-2] + '.'

    # Capitalize first words after colons.
    title = capitalize_words_after_colons(title)

    return title
