#!/usr/bin/python3

import sys, getopt

class Evaluation():
    def __init__(self, ranked_list_path, qrel_path, print_all_queries=False):
        self.ranked_list = {}
        self.qrel = {}
        self.num_rel = {}
        self.print_all_queries = print_all_queries
        self.k = [5, 10, 20, 50, 100]
        self.recalls = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        self.ranked_list_to_dict(ranked_list_path)
        self.qrel_to_dict(qrel_path)

    """
    qrel file format: 
        queryID assessorID docID score
        
    ranked list format: 
        85 Q0 AP890108-0030 1 14.313693 Exp
        queryID [Q0] docID rank(x/N) score [Exp] 
    """
    def ranked_list_to_dict(self, ranked_list_path):
        with open(ranked_list_path, 'rb') as opened:
            for line in opened:
                split_line = line.split()
                queryID, q0, docID, rank, score, exp = split_line
                # init dict for qID if necessary
                if queryID not in self.ranked_list.keys():
                    self.ranked_list[queryID]= {}
                self.ranked_list[queryID][docID] = float(score) # qid: sorted{docid: score}

        opened.close()

        # sort by score, descending
        for query_no, doc_score_dict in self.ranked_list.items():
            sorted_doc_scores = sorted(doc_score_dict.items(), key=lambda item: item[1], reverse=True)
            self.ranked_list[query_no] = sorted_doc_scores


    def qrel_to_dict(self, qrel_path):
        with open(qrel_path, 'rb') as opened:
            for line in opened:
                split_line = line.split()
                qID, assessorID, docID, score = split_line
                score = float(score)
                if qID not in self.qrel.keys():
                    self.qrel[qID] = {}
                    self.num_rel[qID] = 0
                self.qrel[qID][docID] = score # self.qrel maps {qID : {docid: score}, ... {} }
                self.num_rel[qID] += score
        opened.close()

    def evaluate(self):
        tot_num_ret = 0
        tot_num_rel = 0
        tot_num_rel_ret = 0
        sum_prec_at_cutoffs = {i: 0 for i in self.k}
        sum_prec_at_recalls = {i: 0 for i in self.recalls}
        avg_prec_at_k = {i: 0 for i in self.k}
        avg_prec_at_recalls = {i: 0 for i in self.recalls}
        sum_avg_prec = 0
        sum_r_prec = 0

        for qid, doc_score_dict in self.ranked_list.items():
            if len(doc_score_dict) > 0:
                prec_list = {}
                rec_list = {}
                num_ret = 0
                num_rel_ret = 0
                sum_prec = 0
                for doc, score in doc_score_dict:
                    num_ret +=1
                    try:
                        rel = self.qrel[qid][doc]
                    except:
                        rel = 0 # if the doc isn't in the qrel file, then it is not relevant

                    sum_prec += rel * (1 +num_rel_ret) / num_ret
                    num_rel_ret += rel

                    prec_list[num_ret] = num_rel_ret / num_ret
                    rec_list[num_ret] = num_rel_ret / self.num_rel[qid]

                avg_prec = sum_prec / self.num_rel[qid]
                final_recall = num_rel_ret / self.num_rel[qid]

                for i in range(num_ret + 1, 1001): # TODO should it be 1000?
                    prec_list[i] = num_rel_ret / i
                    rec_list[i] = final_recall

                # calculate precisions@k
                prec_at_k = {}

                for cutoff in self.k:
                    prec_at_k[cutoff] = prec_list[cutoff]


                # calculate R precision
                if self.num_rel[qid] > num_ret:
                    r_prec = num_rel_ret / self.num_rel[qid]
                else:
                    int_num_rel = self.num_rel[qid]
                    frac_num_rel = self.num_rel[qid] - int_num_rel

                    if frac_num_rel > 0:
                        r_prec = (1 - frac_num_rel) * prec_list[int_num_rel] + frac_num_rel * prec_list[int_num_rel + 1]
                    else:
                        r_prec = prec_list[int_num_rel]


                # calculate interporlated precisions
                max_prec = 0

                for i in reversed(range(1, 1000)):
                    if prec_list[i] > max_prec:
                        max_prec = prec_list[i]
                    else:
                        prec_list[i] = max_prec

                # calculate precision at recall levels

                i = 1
                prec_at_recalls = {}
                for recall in self.recalls:
                    while i <= 1000 and rec_list[i] < recall:
                        i += 1
                    if i <= 1000:
                        prec_at_recalls[recall] = prec_list[i]
                    else:
                        prec_at_recalls[recall] = 0

                if self.print_all_queries :
                    self.eval_print(qid, num_ret, self.num_rel[qid], num_rel_ret, prec_at_recalls, avg_prec, prec_at_k, r_prec)

                # update running sums for overall stats

                tot_num_ret += num_ret
                tot_num_rel += self.num_rel[qid]
                tot_num_rel_ret += num_rel_ret

                for i in self.k:
                    sum_prec_at_cutoffs[i] += prec_at_k[i]

                for i in self.recalls:
                    sum_prec_at_recalls[i] += prec_at_recalls[i]

                sum_avg_prec += avg_prec
                sum_r_prec += r_prec

        num_topics = len(self.ranked_list)
        print("Error due to {}".format(num_topics))

        for i in self.k:
            avg_prec_at_k[i] = sum_prec_at_cutoffs[i] / num_topics

        for r in self.recalls:
            avg_prec_at_recalls[r] = sum_prec_at_recalls[r] / num_topics

        mean_avg_prec = sum_avg_prec / num_topics
        avg_r_prec = sum_r_prec / num_topics

        self.eval_print(num_topics, tot_num_ret, tot_num_rel, tot_num_rel_ret, avg_prec_at_recalls, mean_avg_prec,
                        avg_prec_at_k, avg_r_prec)

    def eval_print(self, qid, num_ret, num_rel, num_rel_ret, prec_at_recalls, avg_prec, prec_at_k, r_prec):
        print("Queryid (Num): \t {} ".format(int(qid)))
        print("Total number of documents over all queries")
        print("\t Retrieved: \t {}".format(int(num_ret)))
        print("\t Relevant: \t {}".format(int(num_rel)))
        print("\t Rel_ret: \t {}".format(int(num_rel_ret)))
        print("Interpolated Recall - Precision Averages:")

        s_time = 0.00
        for r in self.recalls:
            print(" \t at {} \t {:0.4f}".format(r, prec_at_recalls[r]) )

        print("Average precision (non-interpolated) for all rel docs(averaged over queries)")
        print("\t \t {:0.4f}".format(float(avg_prec)) )
        print("Precision:")

        for kval in self.k:
            print("\t At \t {:0.4f} docs: \t {:0.4f}".format(float(kval), float(prec_at_k[kval])))

        print("R-Precision (precision after R (= num_rel for a query) docs retrieved):")
        print("\t Exact: \t {:0.4f}".format(float(r_prec)))

def main(argv):
    # evalution.py -q qrel ranks

    args = sys.argv[1:]

    if len(args) == 3: # if -q
        qrel = args[1]
        ranks = args[2]
        q = True
        eval = Evaluation(ranks, qrel, print_all_queries=True)
        eval.evaluate()
    if len(args) == 2: # if not -q
        qrel = args[0]
        ranks = args[1]
        q = False
        eval = Evaluation(ranks, qrel)
        eval.evaluate()
    else:
        print("invalid input; Usage: evaluation.py [-q] <qrel_file> <trec_file>")
        sys.exit(1)



if __name__ == "__main__":
    ranked = "/Users/ellataira/Library/Mobile Documents/com~apple~CloudDocs/Desktop/is4200/homework--5-ellataira/Results/es_builtin6.txt"
    qrel = "/Users/ellataira/Library/Mobile Documents/com~apple~CloudDocs/Desktop/is4200/homework--5-ellataira/Results/qrels.adhoc.51-100.AP89.txt"
    # ranked=  "/Users/ellataira/Library/Mobile Documents/com~apple~CloudDocs/Desktop/is4200/homework--5-ellataira/Results/es_builtin.txt"
    # qrel = "/Users/ellataira/Library/Mobile Documents/com~apple~CloudDocs/Desktop/is4200/homework--5-ellataira/qrel.txt"
    eval = Evaluation(ranked, qrel, print_all_queries=False)
    eval.evaluate()
