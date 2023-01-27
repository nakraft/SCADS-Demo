import os
import time
import pandas as pd
import pickle as pi 
from collections import Counter
import argparse
import nltk
import spacy
import en_core_web_sm
from tqdm import tqdm

from occams.summarize import SummaryUnits, TermFrequencyScheme, extract_summary, SummaryExtractor, TermFrequencySummaryExtractor,IncidenceStructure, Extract
from occams.termweights import fisher_term_weights as ftw 
from occams.nlp import DocumentProcessor, TermOrder, Document, Sentence, T
from sort import sorter as st

"""
Occams documentation: 
https://drive.google.com/file/d/1xg-fx5R6cWRZdxhZnzai1CwiodNpClLU/view
Occams Repo: https://github.ncsu.edu/SCADS/Occams/blob/master/occams/occamslib.pyx
"""

def load_data(file_path): 
    """read in a pickle file for use in summarization. these were pre-computed bigrams of documents to improve runtime"""
    return pd.read_pickle(file_path)

def aggregate_bg(bigrams): 
    """aggregate the calculated bigrams from a corpus into one counter"""
    bg = Counter() 
    for ele in bigrams: 
        bg.update(ele)
    return bg

def determine_scheme(scheme): 
    """determine the correct scheme to utilize in summarization"""
    # scheme options can be found here: 
    # https://github.ncsu.edu/SCADS/Occams/blob/master/occams/summarize/term_weight_schemes.py
    # or within the repo's OCCAMS_user_guide.md
    schemes = {
        'position' : TermFrequencyScheme.POSITIONAL_DENSE, 
        'terms' : TermFrequencyScheme.CORE_TERMS,
        'sentances' : TermFrequencyScheme.CORE_SENTENCES,
        'counts' : TermFrequencyScheme.COUNTS,
        'entropy' : TermFrequencyScheme.ENTROPY,
        'fisher' : 'fisher', 
    }

    return schemes[scheme]

def reorder(df): 
    """transforms the dataframe to be from end to start to test reorder affect on summarization"""
    temp_df = pd.DataFrame()
    for i in range(len(df) - 1, -1, -1):
        temp_df = temp_df.append(df.iloc[[i]])

    return temp_df.reset_index()


def compute_sentance_score(extractor, sentences): 
    """
    To evaluate whether (or not) a sentence should be shared, we recompute the sentence score. 
    This is a simplist measure according to OccamsV5/misc.c and is the sum of the term weigths included in the sentence. 
    
    IMPORTANT
    Summary weight is computed by a "linear objective function" to maximize the "sum of the weights of the terms covered."
    Sentences are chosen by "maximizing the normalized marginal weight" out of all the sentences that the length budget can fit. 
    """
    # Can get the term_weights of the function TODO: Try customization efforts with these positional weights rather than fisher
    term_weights = extractor.term_weights_mapping()

    def get_term(terms): 
        try: 
            return term_weights[terms]
        except: 
            return 0

    summed = []
    for i, v in enumerate(sentences): 
        summed.append(sum([(get_term(t)) for t in v.terms]))

    return summed

def coverage_heuristic(sum_arr, extractor, experiment): 
    """
    heuristic to evaluate the coverage of the summary.
    heuristics include general coverage of entities and their distribution amongst corpus documents.
    """
    nlp = en_core_web_sm.load()

    # extracting entities from summary
    sum_doc = nlp(" ".join([s.text for s in sum_arr]))
    sum_df = pd.DataFrame()
    sum_df['label'] = [i.label_ for i in sum_doc.ents]
    sum_df['text'] = [i.text for i in sum_doc.ents]
    sum_set = set(zip(sum_df['label'], sum_df['text']))

    # extracting entities from each document
    corp_df = pd.DataFrame(columns=['label', 'text', 'doc_num'])
    doc_balance = []
    for doc_num in range(0, extractor.num_documents()): 
        sentences = extractor.sentences_from_document(doc_num)
        corp_sentences = " ".join([s.text for s in sentences])
        corp_doc = nlp(corp_sentences)

        temp_df = pd.DataFrame()
        temp_df['label'] = [i.label_ for i in corp_doc.ents]
        temp_df['text'] = [i.text for i in corp_doc.ents]
        temp_df['doc_num'] = doc_num
        doc_set = set(zip(temp_df['label'], temp_df['text']))
        doc_balance.append((doc_num, doc_set.intersection(sum_set)))

        corp_df = corp_df.append(temp_df, ignore_index = True)

    # drop numbers 
    corp_df = corp_df.loc[(corp_df['label'] != 'CARDINAL') & (corp_df['label'] != 'ORDINAL')].drop_duplicates(subset=['label', 'text'])

    similar = set(zip(corp_df['label'], corp_df['text'])).intersection(sum_set)
    doc_balance_score = [len(doc_balance[i][1]) for i in range(0, len(doc_balance))]
    if not experiment: 
        print("Similar by", len(similar), "(", round(len(similar)*100/len(corp_df)), "%) out of", len(corp_df) )
        print("Each document supported the summary with the following number of entities:", doc_balance_score)
        print("This is an average of", sum(doc_balance_score) / len(doc_balance_score))

    return len(similar), len(corp_df), doc_balance_score, sum(doc_balance_score) / len(doc_balance_score)

def determine_doc(doc_sep_arr, sentence_arr): 
    """determines which document a sentence originated from"""
    iden = st(arr = doc_sep_arr)
    doc_number = []
    for i in sentence_arr: 
        doc_number.append(iden.find_position(i))

    return doc_number

def load_corpus(df, abstract): 
    """loads the corpus into an incidence structure for occams to use in summarization"""
    start_load = time.time()
    docprocess = DocumentProcessor(TermOrder.BIGRAMS, language='english', download=True).process
    documents = [docprocess(str(i)) for i in df[abstract]]
    doc_incidences = IncidenceStructure(documents)
    end_load = time.time() 

    return documents, doc_incidences, end_load - start_load

def summarize_pretending_one(df_as_one, target_length, scheme):
    """
    proxy summarizer for occams. 
    this just gathers all the documents as one text and summarizes them as if they are one document.
    """
    chosen_scheme = determine_scheme(scheme)

    text = " ".join(df_as_one['Text'])

    docparser = DocumentProcessor(TermOrder.BIGRAMS, language='english', download=True).process
    document = docparser(text)
    extract = extract_summary(documents = [document], budget=target_length, units=SummaryUnits.WORDS, scheme=chosen_scheme)
    summary = extract.summary()

    return summary

def summarize(df, target_length, abstract): 
    """summarizes each document independently"""
    docparser = DocumentProcessor(TermOrder.BIGRAMS, language='english', download=True).process
    documents = [docparser(text) for text in df[abstract]]

    scheme = TermFrequencyScheme.POSITIONAL_DENSE # utilizes area of document to weight relevance
    extracts = [extract_summary(documents=[doc], budget=target_length, units=SummaryUnits.WORDS, scheme=scheme)
            for doc in documents]

    df['individual_summary'] = [i.summary() for i in extracts]

def summarize_collect(df, documents, doc_incidences, scheme, length, experiment):
    """
    summarize a collection of documents.
    user can input a particular scheme to utilize. 
    if run in experiment mode, statistics are calculated for easier use in comparison. 
    """

    chosen_scheme = determine_scheme(scheme)
    document_titles = df['Title']

    # if not experiment: 
    #     print("-------------------")
    #     print("\nSummarizing", doc_incidences.num_documents(), "documents under scheme", scheme)

    start_time = None
    if chosen_scheme == 'fisher': 
        to_summarize_bg = aggregate_bg(df['bigrams'])
        with open('data_grams/backcorp_bigrams.pickle', 'rb') as inputfile:
            back_bg = pi.load(inputfile)

        back_bg = back_bg - to_summarize_bg

        # extracting term weights through Fisher calculation against back bg 
        start_time = time.time()
        term_weights = ftw(doc_incidences.term_counts(), back_bg) 
        extractor = SummaryExtractor.from_documents(documents, units=SummaryUnits.WORDS, term_weights=term_weights)
    
    else: 
        # extracting term weights through a particular scheme
        start_time = time.time()
        extractor = TermFrequencySummaryExtractor.from_documents(documents, units=SummaryUnits.WORDS, scheme=chosen_scheme)
    
    max_s = round(extractor._m.num_sentences() * .9)
    extractor.reduce_incidence_structure(max_sentences = max(max_s, 1), min_length = .3) # removeing too short sentances and duplicate statements
    build_time = time.time() - start_time

    start_time = time.time()
    extract = extractor.extract(budget=int(length))

    # set to False if you want to use the order the algorithm chooses, True will keep it in sorted document order 
    alg_priority = True

    sentences = extract.sentences(document_order=alg_priority)
    sentence_i = extract.indices(sort=alg_priority)        # extractor._m.get_sentence(55)) can be used to identify the sentance in the listing
    # if not experiment: 
    #     print("Summary time:", time.time() - start_time)
    doc_sep = []
    for ele, value in enumerate(extract._m.document_spans()):
        doc_sep.append(value[1])
    
    doc_i = determine_doc(doc_sep, sentence_i)
    doc_titles = [document_titles[i] for i in doc_i]
    sentence_weights = compute_sentance_score(extractor, sentences)

    if not experiment: 
        print("Summary generated in", extract.time(), "ns")
        print("\n", "-----summary------", "\n")
        print("".join([sentences[i].text.ljust(max(125, int(length)), " ") +
         "(" + doc_titles[i] + ", " + str(round(sentence_weights[i], 2)) +
          ")\n" for i in range(0, len(sentences))] ))
        coverage_heuristic(sentences, extractor, False) # If interested in scores... uncomment!

    return build_time, extract.time(), sentences, doc_titles, extractor, sentence_weights

def run_experiment(abstract): 
    """
    Assumes a user wants to collect all statistics and compute all 
    values from the corpuses listed in the data folder. 
    Output will be sent to an excel sheet, and each subsequent run of the experiment will generate a new tab. 
    """

    files = os.listdir("data")

    # creates the table to store experiment results 
    df = pd.DataFrame(columns=['corpus', 'doc_num', 'scheme', 'target_length', 
                                'time_load', 'time_build', 'time_summarize', 'occams_summary', 'sentence_home',
                                'sentence_weights', 'summary_score', 
                                'entity_count', 'entity_total', 'entity_balance', 'entity_balance_average'])
    for f in files: 
        print("Running trials for", f)
        corp = load_data("data/" + f)
        corp = corp[~corp[abstract].isna()].reset_index()
        documents, doc_incidences, load_time = load_corpus(corp, abstract)
        corp_df = {'corpus' : f.split(".")[0], 'doc_num' : len(corp), 'time_load' : load_time}
        for length in tqdm([100, 150, 250]):
            for scheme in ['position', 'terms', 'sentances', 'counts', 'entropy', 'fisher']:   
                if (f != 'sports_corp.pickle') | (scheme == 'sentances'): 
                    time_build, time_summarize, sentences, doc_home, extractor, sentence_weights  = summarize_collect(corp, documents, doc_incidences, scheme, length, True)
                    entity_count, entity_total, doc_balance_score, balance_average = coverage_heuristic(sentences, extractor, True)
                    corp_df.update({'target_length': length, 'scheme' : scheme, 
                                    'time_build' : time_build, 'time_summarize' :time_summarize, 
                                    'occams_summary' : "".join([i.text + "\n" for i in sentences]), 
                                    'sentence_home' : "".join([i + "\n" for i in doc_home]), 
                                    'sentence_weights' : sentence_weights,
                                    'summary_score' : sum(sentence_weights),
                                    'entity_count' : entity_count, 'entity_total' : entity_total, 
                                    'entity_balance' : doc_balance_score, 
                                    'entity_balance_average' : balance_average})
                    df = df.append(corp_df, ignore_index=True)
    
        df.to_excel("out/experiment.xlsx")

if __name__ == "__main__": 

    parser = argparse.ArgumentParser(prog='Occams Support', 
                        description='Generating multidocument text summarization with OCCAMS')
    parser.add_argument("-f", dest='file', type=str, default = "uconn_corp",  
                        help='Which multidocument corpus would you like to be summarized?')
    parser.add_argument("-s", dest='scheme', type=str, default = "all",  
                        help='Which scheme would you like to use?')
    parser.add_argument("-l", dest='length', type=str, default = 100,  
                        help='What is your target corpus length?')
    parser.add_argument("-r", '--reorder', action = "store_true",  
                        help='Do you want to reorder your corpus?')
    parser.add_argument("-e", '--experiment', action = "store_true",  
                        help='Are you gathering statistics regarding your corpus to run as an experiment?')
    parser.add_argument("-a", '--abstract', default = 'Text',  
                        help='Do you want to generate summaries based on the abstracts and not the texts?')
    args = parser.parse_args()

    if args.experiment: 
        print("Running Multi-Document Summarization Experiment")
        run_experiment(args.abstract)
    else: 
        print("Beginning Multi-Document Summarization:")
        # load in data file 
        doc_loc = "data/" + args.file + ".pickle"
        df = load_data(doc_loc)

        if args.reorder: 
            df = reorder(df)

        documents, doc_incidences, load_time = load_corpus(df, args.abstract) 
        if args.scheme == 'all': 
            summarize_collect(df, documents, doc_incidences, 'fisher', args.length, False)
            summarize_collect(df, documents, doc_incidences, 'position', args.length, False)
            summarize_collect(df, documents, doc_incidences, 'terms', args.length, False)
            summarize_collect(df, documents, doc_incidences, 'sentances', args.length, False)
            summarize_collect(df, documents, doc_incidences, 'counts', args.length, False)
            summarize_collect(df, documents, doc_incidences, 'entropy', args.length, False)
        else: 
            summarize_collect(df, documents, doc_incidences, args.scheme, args.length, False)

    print("Ending Multi-Document Summarization")