import re

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

    return title
