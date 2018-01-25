from Bio import Entrez
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

    if num_authors > 0:
        authors = record['AuthorList'][0].rstrip('.')  # First author only. Strip any trailing period, e.g., 22187473

    if num_authors == 2:
        authors = authors + ', ' + record['AuthorList'][1].rstrip(
            '.')  # First and second authors. Strip any trailing period.

    if num_authors > 2:
        authors = authors + ', ' + record['AuthorList'][1].rstrip(
            '.') + ', et al.'  # First, second,  et al. Strip any trailing periods

    return authors
