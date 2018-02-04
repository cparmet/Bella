from titlecase import titlecase
import re
import pandas as pd


def format_authors(record):
    # Note: the rstrip('.') calls are to clean up any author names that ended with period, like in PMID 17545397.

    try:
        num_authors = len(record['AuthorList'])
    except:
        num_authors = 0

    if num_authors == 0:
        authors = ''
        return authors

    # Cases that get this far have at least 1 author.

    # Fix author names that are all uppercase, like 28827379: COMMITTEE ON ADOLESCENCE
    author_list = record['AuthorList']
    for i, author in enumerate(author_list):
        if author.isupper():
            author_list[i] = titlecase(author)

    # Grab the first author
    authors = author_list[0].rstrip('.')  # Strip any trailing period, e.g., 22187473

    # Two authors: add the second author, so it formats "First author, second author."
    if num_authors == 2:
        authors = authors + ', ' + author_list[1].rstrip('.')  # Strip any trailing period.

    # Three or more authors: "First author, et al"
    if num_authors > 2:
        authors = authors + ', et al.'

    return authors
