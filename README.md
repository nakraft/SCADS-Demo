# Evaluation of OCCAMS 

In the creation of a TLDR for Intelligence Analysts, there is a purported value in developing multi-document summarization techniques to support the synthesis and identification of new, relevant information. One such technology, OCCAMS (an Optimal Combinatorial Covering Algorithm for Multi-document Summarization), aims to do just this using statistical techniques with simplistic hyperparameters to define what ‘relevant’ information is.

This repo looks to evaluate the summarization package and explore possible implementation improvements into an [LAS SCADS Demo](https://commander.ncsu-las.net/commander/project/0000017f-0d34-d974-0a00-10e600000013) prototype. 

## OCCAMS 

OCCAMS has continued to be developed at SCADS 2022. The repo can be found at https://github.ncsu.edu/SCADS/Occams. 

Key System Components 

OCCAMS takes a selection of text bodies that form a corpus and summarizes them based on a user designated scheme. Within the corpus, 1 to n **documents** can be present, each comprising of **sentences** to be evaluated for relevance. After tokenizing the corpus, an **Incidence Structure** is generated to hold the listing of sentences in the corpus and their associated term weights. Summaries are extractive; thus, the algorithm ranks sentences based on the scheme provided and then selects the highest weighted sentences for use in a summary. Summaries can then be generated from the Incidence Structure into **Extracts**. These extracts are built using a particular scheme which acts as a heuristic to judge relevance of a sentence. Details regarding the full algorithm are described here: https://ieeexplore.ieee.org/document/6406475. 

Practical support for utilizing OCCAMS and understanding the integrated heuristics can be found [here](OCCAMS_user_guide.md). 

## Summarization Results 

__Single Document Summarization__ 

For the SCADS recommender system demo, single document summarizations (aka highlights) were generated to show an additional aspect of development that occurred during SCADS. 

![](docs/img/SCADSDemoHomePage.png)

Each of these highlights are ranked by their 'relevance' in summarizing the information within the document. However, they are noticeably non-sequitur when displayed in a paragraph format. This tends to be the case throughout most generated extractive summaries in produced. OCCAMS doesn't reduce this problem any further. **Summarization for SCADS can be found [here](work.ipynb). 

__Multi-Document Summarization__ 

Despite this implementation, prioritization was placed on identifying if OCCAMS could produce summaries which effectively shared information across different documents. Ideally, corpuses could be clustered, and one summary could be produced that had high coverage of the entire corpus.  Use cases could include summarizing clusters of documents that were recommended or inverting the process to utilize high-scoring summaries as the recommender system’s input to selecting new documents. 

- An example of 3 clustered documents regarding the University of Connecticut's Women's Basketball Team can be found [here](out/uconn.txt)
- An example of 145 clustered documents regarding the basketball player Zion Williamson can be found [here](out/zion.txt). 


__Observations and Goals__

As the number of grouped documents increases, summarization generally declines (although this in part changes when utilizing different OCCAMS schemes as well) The goal was to maximize the size of the document’s clusters and the summarization quality. We looked to produce intuitive summarizations with high, non-duplicative information coverage.  While single document summarization produced less-than-human quality responses, the hope was that the density of the term weight matrix would increase when OCCAMS was provided with more input data. Thus, making multi-document summarization higher quality than single document summarization. 

To effectively identify an optimized corpus size, evaluation criteria were identified. These criteria could be utilized in the future to compare OCCAMS with additional novel summarization techniques. However, while measurements of information gain, coverage and novelty can be taken, no evaluation criteria have been identified to quantify the readability of a particular summary. Human evaluation would still be needed in this regard to identify if a summary of ‘highlights’ would appropriate qualify as a paragraph-based summary. This is hypothesized to be an unachievable goal utilizing extractive text summarization due to its non-generative nature. Abstractive methods can be appealing to overcome this challenge but are frequently disregarded due to hallucinogenic tendencies. 

## Evaluation Criteria 

Primitive evaluation metrics were developed to be used in determining OCCAMS usefulness and capability of being deployed to summarize large corpuses in real time. 

__Accuracy__ 

__Feasability & Scalability__ 


## Experimentation 

## Results 