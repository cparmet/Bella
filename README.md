# Bella

Takes a DOI or PubMed ID, uses PubMed API to output a citation in a particular format.

Uses natural language processing to make a best attempt at converting article titles from Title Case to Sentence case.

The Entrez code is a fork of the fabulous Biopython package. It allows the PubMed API wrapper to work on AWS Lambda and similar deployments. The main Biopython branch has since been updated with this capability (PR #1522).