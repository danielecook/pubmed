#!/usr/bin/python
# encoding: utf-8

import sys

from workflow import Workflow

from Bio import Entrez,Medline
import re
import random

__version__ = '0.1'



def slug(q):
    return re.sub(r'[^a-z0-9]+', '-', q).strip('-')

def get_individual_pub():
    # Retrieve results from individual search on pubmed
    args = ' '.join(wf.args)
    handle = Entrez.efetch("pubmed", id=args.split(":")[1], retmode="text",rettype="medline")
    return Medline.parse(handle).next()

def get_search_results():
    # Searches pubmed
    args = ' '.join(wf.args)
    handle = Entrez.esearch(db="pubmed", retmax=10, term=args)
    record = Entrez.read(handle)
    if len(record["IdList"]) > 0:
        handle = Entrez.efetch("pubmed", id=','.join(record["IdList"]), retmode="text",rettype="medline")
        pubs = Medline.parse(handle)
        pub_set = list()
        for p in pubs:
            pub_set.append(p)
        return pub_set
    else:
        return []


def main(wf):
    args = ' '.join(wf.args)
    Entrez.email = "noreply@danielecook.com"

    # See if user is searching for a pub or has selected one.
    log.debug(wf.args[0:4])
    if args.startswith("PMID") == False:
        pubs = wf.cached_data(slug(args), get_search_results, max_age=100000)
        if len(pubs) > 0:
            for p in pubs:
                #doi = [x[:-6] for x in p["AID"] if x.endswith("[doi]")][0]
                if "AU" not in p:
                    p["AU"] = [""]

                wf.add_item(p['TI'], 
                ', '.join(p["AU"]), # Authors
                copytext=p["TI"],
                valid=False,
                autocomplete="PMID:" + p["PMID"])
        else:
            wf.add_item("No results found.", 
            valid=False,
            icon="error.png")
    else:
        p = wf.cached_data(slug(args), get_individual_pub, max_age=100000)

        # Split title up:
        wf.add_item(p["TI"], p["TI"], "Title", icon="T.png")
        authors = ', '.join(p["AU"])
        wf.add_item(authors,"Authors", icon=str(random.choice([1,2])) + ".png")
        try:
            doi = [x[:-6] for x in p["AID"] if x.endswith("[doi]")][0]
            doi_url = "https://dx.doi.org/" + doi
            wf.add_item("Resolve DOI",doi_url, copytext = doi, arg = doi_url, valid=True, icon="paper.png")
            scholar_url = "https://scholar.google.com/scholar?hl=en&q=" + doi
        except:
            scholar_url = "https://scholar.google.com/scholar?hl=en&q=" + p["TI"]
        pubmed_url = "http://www.ncbi.nlm.nih.gov/pubmed/" + p["PMID"]
        wf.add_item("Pubmed","Open in pubmed", copytext=p["PMID"], arg = pubmed_url, valid=True, icon="pubmed.png")
        paperlink_url = "http://www.thepaperlink.com/?q=" + p["PMID"]
        wf.add_item("PDF","Fetch PDF from the Paper Link", arg = paperlink_url, valid=True,icon="pdf.png")
        wf.add_item("Google Scholar","Open in google scholar", arg = scholar_url, valid=True,icon="scholar.png")




 

    #cmd, ctrl, shift, alt

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow(update_settings={'version': __version__,'github_slug':""})
    #wf.cache_serializer = 'pickle'
    #wf.store_data('cached_results', ["test"], serializer='json')
    # Assign Workflow logger to a global variable, so all module
    # functions can access it without having to pass the Workflow
    # instance around
    log = wf.logger
    sys.exit(wf.run(main))
