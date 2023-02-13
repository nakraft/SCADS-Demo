# Experiment Parameters for OCCAMS 

## Install

1) Install OCCAMS locally using rust. Detailed instructuctions can be found (here)[https://github.ncsu.edu/SCADS/Occams#installation].    

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

## Notes 

- To run the summarizer on the abstracts (rather than the full text themselves), use the -a parameter. To utilize this feature, ensure the pickle file has a 'abstract' column. 
- The only schemes available for running the experiment on are: Positional_Dense, Core_Terms, Core_Sentences, Counts, Entropy, or Fisher. 