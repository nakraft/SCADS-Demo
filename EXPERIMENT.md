# Experiment Parameters for OCCAMS 

## Install

1) Install OCCAMS locally using rust. Detailed instructuctions can be found [here](https://github.ncsu.edu/SCADS/Occams#installation).    

2) Create a virtual enviornment for your experimentation (Python 3.7 was utilized). Enable ipykernel to be able to run through jupyter notebooks. Install requirements.txt 

``` 
~$ source occams3.7/bin/activate 
(occams3.7) ~/SCADS-Demo$ pip install -r requirements.txt
```

## Experimentation 

1) Find your source of raw MIND data (either within LAS /efs drive on Data Science EC2 Image or through open source means). 
2) Rerun the categorize.ipynb to generate trial corpuses. (OCCAMS multi-corpus summarization is not scalable for large corpuses, choosing a corpus <50 for ideal experimentation summarization wait times.)
    a) If utilizing Fisher summary scheme, generate your background corpus bigrams in advance. You can also generate your full term weights in advance and pass those as a parameter to the summarizer. 
    b) Ensure any corpus generated is a .pickle file. The column to be summarized should be labelled as 'text'. 
3) The following options are available for use within the multisum.py experimentation file. 

```
usage: Occams Support [-h] [-f FILE] [-s SCHEME] [-l LENGTH] [-r] [-e]
                      [-a ABSTRACT]

Generating multidocument text summarization with OCCAMS

optional arguments:
  -h, --help            show this help message and exit
  -f FILE               Which multidocument corpus would you like to be
                        summarized?
  -s SCHEME             Which scheme would you like to use?
  -l LENGTH             What is your target corpus length?
  -r, --reorder         Do you want to reorder your corpus?
  -e, --experiment      Are you gathering statistics regarding your corpus to
                        run as an experiment?
  -a ABSTRACT, --abstract ABSTRACT
                        Do you want to generate summaries based on the
                        abstracts and not the texts?
```

### Examples

__Summarization Mode__ 
```
# generating a summary for the university of connecticut's basketball team, 
# with the position scheme and a target length of 300 characters
python3 multisum.py -f uconn_corp -s position -l 300

# output to stdout
Beginning Multi-Document Summarization:
Summary generated in 392779 ns

 -----summary------ 

 Now you’ve got Crystal in a situation where everybody she is passing to isn’t an All-American who is going to catch it and finish.                                                                                                                                                                          (Mike Anthony: The UConn women will be good if Crystal Dangerfield can be great, 69.38)
“It’s just taking a little bit more time, and I’m just trying to get back into the groove,” she said Monday, when she was honored with co-player of the year Kay Kay Wright of Central Florida.                                                                                     .... cont ... 

Similar by 30 ( 28 %) out of 108
Each document supported the summary with the following number of entities: [21, 9, 25]
This is an average of 18.333333333333332
Ending Multi-Document Summarization

```

__Experimentation Mode__ 
```
# running through combinations of lengths and schemes for all corpuses placed within the /data folder
# also generating coverage/scalability metrics for use in evaluation
python3 multisum.py -e

# output will be an excel sheet to /out folder 
```

## Experiment Output 

Runnning in experiment mode will produce an excel sheet as an output. The following column/definition pair describes the experiment metrics being taken. 

| variable | description | 
|----|-----|
| corpus | The name of the corpus being utilized in summarization | 
| doc_number | The number of documents in the corpus | 
| scheme | Summarization scheme being tested | 
| target length | Summary target length | 
| time load | OCCAMS preprocessing time - time it takes to load the corpus into an incidence structure for occams| 
| time build | Time utilizing the scheme to create term weight. This includes removing elements (sentences) from the Incidence Structure falling outside the set hyperparameters (too short, not enough valuable tokens, etc). | 
| time summarize | Time processing the term weights to develop a summary score, which is subsequently ranked and chosen from the Greedy Budgeted Maximal Coverage Algorithm (an NP-hard problem, thus a time consuming step in summarization as it is run after each sentence is selected for use until the budget (target length) is exhausted. | 
| Occams Summary | The summary produced by OCCAMS, in the order suggested. Listed in an array representation to be paired with the 'sentence_home'. | 
| sentance home | The document title for which this extracted sentence was pulled. An array representation of the originating location of the extracted sentence, to be paired with the actual summary column arrays. | 
| entity count | Number of unique entities within the chosen sentences. | 
| entity total | Number of unique entities within the full corpus. | 
| entity balance | An array, representing the number of entities in the summary pulled from each document in the corpus (the intuition being to look for equal coverage across the document set). | 
| entity balance average | Average entities pulled from each document in corpus. | 

## Notes 

- To run the summarizer on the abstracts (rather than the full text themselves), use the -a parameter. To utilize this feature, ensure the pickle file has a 'abstract' column. 
- The only schemes available for running the experiment on are: Positional_Dense, Core_Terms, Core_Sentences, Counts, Entropy, or Fisher. 