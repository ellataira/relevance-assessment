# Relevance Assessments 

The objective of this assignment is to implement a script to score information retrieval relevance, comparing a retrieval model's scores on a set of
documents to a file of manually assessed scores for the same documents. 

## Manual Assessment 
`qrel.txt` contains the manually assessed relevance scores of crawled documents for a set of queries. Scores of [0,1,2] indicate, respectively, 
not relevant, relevant, and highly relevant. The documents being assessed are from the merged index of crawled documents from the Crawler project. 

## `evaluation`

The `evaluation` script has a similar functionality to `trec_eval.pl`, but includes additional relevance measures. 

The script sorts each query's documents by score. It then calculates R-precision, Average Precision, nDCG, precision@k and recall@k and F1@k (k=5,10, 20, 50, 100). 
These scores are then averaged across all queries. 

To run the script, enter: `./Code/evaluation [-q] [QREL] [SCORES]` 

`-q` will display the measures for each individual query along with the cumulative averages. 

The QREL document is formatted as: 
`[query ID] [Assessor] [document ID] [score]`

The SCORES document is formatted as: 
`[query ID] Q0 [document ID] [rank] [score] Exp`

For example, this is the result of running `./Code/evaluation qrel.txt es_results.txt`

```
Error due to 4
Queryid (Num):   4 
Total number of documents over all queries
         Retrieved:      800
         Relevant:       732
         Rel_ret:        732
         nDCG:   161.8052
Interpolated Recall - Precision Averages:
         at 0    1.6250
         at 0.1          1.1807
         at 0.2          1.1611
         at 0.3          1.1312
         at 0.4          1.0973
         at 0.5          1.0569
         at 0.6          1.0477
         at 0.7          1.0178
         at 0.8          0.9625
         at 0.9          0.9513
         at 1.0          0.9172

Average PRECISION (non-interpolated) for all rel docs(averaged over queries)
                 1.0340
Precision:
         At      5.0000 docs:    1.0500
         At      10.0000 docs:   1.1250
         At      20.0000 docs:   1.0125
         At      50.0000 docs:   1.0700
         At      100.0000 docs:          1.0125

Average RECALL for all rel docs(averaged over queries)
                 0.5060
Recall: 
         At      5.0000 docs:    0.0267
         At      10.0000 docs:   0.0567
         At      20.0000 docs:   0.1033
         At      50.0000 docs:   0.3055
         At      100.0000 docs:          0.5541

Average F1 for all rel docs(averaged over queries)
                 0.5772
F1: 
         At      5.0000 docs:    0.0514
         At      10.0000 docs:   0.1059
         At      20.0000 docs:   0.1812
         At      50.0000 docs:   0.4393
         At      100.0000 docs:          0.6626

R-Precision (precision after R (= num_rel for a query) docs retrieved):
         Exact:          0.8279
```


