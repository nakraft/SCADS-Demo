## OCCAMS user guide 

Full details regarding OCCAMS installation can be found within the [OCCAMS repo](https://github.ncsu.edu/SCADS/Occams). The following acts to identify key aspects of the system and provide details regarding potential use cases. 

### Pipeline

The typical pipeline for sentence generation follows as such: 

```
# generates a processors, evaluates texts in corpus to build Incidence Structure
docprocess = DocumentProcessor(TermOrder.BIGRAMS, language='english', download=True).process
documents = [docprocess(str(i)) for i in df[‘text’]]
doc_incidences = IncidenceStructure(documents)

# gathers term weights using a particular scheme/heuristic 
extractor = TermFrequencySummaryExtractor.from_documents(documents, units=SummaryUnits.WORDS, scheme=chosen_scheme)

# extracts sentences of relevance for summary based on a particular length
extractor.extract(budget=length)
```

For more examples on running summarization using OCCAMS visit https://github.ncsu.edu/SCADS/Occams/tree/master/notebooks. Additional notebooks with examples can be found in the LAS Data Science Image within the efs drive. (~/efs/home/pcorona_content)  


### Schemes – Heuristics of Relevance 

As mentioned, relevance is arbitrary and OCCAMS has developed 12 schemes defining how to evaluate which sentences to extract for a summary. The schemes include: 

-	Term Frequency Scheme: computed based on the normalized count of the terms throughout the full corpus of documents to be summarized. 
-	Positional First Scheme: increases term weights to prioritize terms present within the first sentence of any document in the corpus. 
-	Positional Dense Scheme: term weights higher for terms earlier in each document, logarithmic decline in weight as sentences get further toward the end of the document.    
-	Core Sentence Scheme: prioritizes terms that exist within sentences that have high coverage of the entire document. 
-	Core Term Scheme:  prioritizes terms that that exist within sentences that have high coverage of the entire document while still considering overall term counts. 
-	Logarithmic Counts Scheme: terms are logarithmically weighted based on their overall frequency within the corpus.
-	Counts Scheme: terms are equally weighted based on their overall frequency within the corpus. 
-	Entropy Scheme: probability distribution across terms within the corpus. 
-	Flat Scheme: all terms are given equal weight regardless of frequency or position. 
-	Fisher Scheme: utilizes Fisher Term Weights, computed based on comparing corpus against a background corpus for similarities. 
-	Positional Minimum/Maximum/Mean Scheme: NA **note: no intuitive rationale for these schemes have been determined.**

These schemes are designed and passed to the summary extractor in the term_weight_schemes.py file within the OCCAMS/summarize folder. 

### Observations 

While many of the schemes to calculate sentence relevance are independent from document or sentence ordering, it should be noted that the Incidence Structure has essentially collapsed the full corpus into one single text body to be summarized. The result is that summarization occurs as if the corpus is only one document, ignoring the relative clustering of information within documents. When using positional schemes, term weight may be adjusted based on their relative placement within the document, but no relevance is given to the fact that term A and B occurred at the beginning of one document while term C and D were placed in another. 

There is no user input to guide summarization mechanisms toward subjects of relevance. Fisher term weights have been utilized to attempt to guide the mechanism in this way, but in general this produces summarizations more similar to known information rather than expanding the scope to include new information included within a corpus. 


