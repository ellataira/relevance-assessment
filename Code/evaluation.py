#!/usr/bin/python3

import sys, getopt

class Evaluation():
    def __init__(self, ranked_list_path, qrel_path, print_all_queries=False):
        self.ranked_list = {}
        self.qrel = {}
        self.ranked_list_to_dict(ranked_list_path)
        self.qrel_to_dict(qrel_path)
        self.eval_scores = {} # maps qid : (r_p, avg_p, ndcg, precision_at_k, recall_at_k, f1_at_k)
        self.num_rel = {}
        self.print_all_queries = print_all_queries
        self.k = [5,10, 20, 50, 100]
        self.recalls = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

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
                score = int(score)
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
                prec_list = []
                rec_list = []
                num_ret = 0
                num_rel_ret = 0
                sum_prec = 0

                for doc, score in doc_score_dict.items():
                    num_ret +=1
                    rel = self.qrel[qid][doc]

                    if rel > 0:
                        sum_prec += rel * (1 +num_rel_ret) / num_ret
                        num_rel_ret += rel

                    prec_list[num_ret] = num_rel_ret / num_ret
                    rec_list[num_ret] = num_rel_ret / self.num_rel[qid]

                avg_prec = sum_prec / self.num_rel[qid]
                final_recall = num_rel_ret / self.num_rel[qid]

                for i in range(num_ret +1, 1000): # TODO should it be 1000?
                    prec_list[i] = num_rel_ret / i
                    rec_list[i] = final_recall


                # calculate precisions@k
                prec_at_k = []

                for cutoff in self.k:
                    prec_at_k.append(prec_list[cutoff])


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

                prec_at_recalls = []

                i = 1
                for r in self.recalls:
                    while i < 1000 and rec_list[i] < r:
                        i += 1
                    if i <= 1000:
                        prec_at_recalls.append(prec_list[i])
                    else:
                        prec_at_recalls.append(0)

                if self.print_all_queries :
                    self.eval_print(qid, num_ret, self.num_rel[qid], num_rel_ret, prec_at_recalls, avg_prec, prec_at_k, r_prec)

                # update running sums for overall stats

                tot_num_ret += num_ret
                tot_num_rel += self.num_rel[qid]
                tot_num_rel_ret += num_rel_ret

                for i in range(len(self.k)):
                    sum_prec_at_cutoffs[i] += prec_at_k[i]


                for i in range(len(self.recalls)):
                    sum_prec_at_recalls[i] += prec_at_recalls[i]

                sum_avg_prec += avg_prec
                sum_r_prec += r_prec

        num_topics = len(self.ranked_list)
        print("Error due to {}\n".format(num_topics))
        for i in self.k:
            avg_prec_at_k[i] = sum_prec_at_cutoffs[i] / num_topics

        for r in self.recalls:
            avg_prec_at_recalls[r] = sum_prec_at_recalls[r] / num_topics

        mean_avg_prec = sum_avg_prec / num_topics
        avg_r_prec = sum_r_prec / num_topics

        self.eval_print(num_topics, tot_num_ret, tot_num_rel, tot_num_rel_ret, avg_prec_at_recalls, mean_avg_prec,
                        avg_prec_at_k, avg_r_prec)



        #     precision_at_k = []
        #     recall_at_k = []
        #     f1_at_k = []
        #
        #     for k_val in k:
        #         precision_at_k.append(self.compute_precision(k_val))
        #         recall_at_k.append(self.compute_recall(k_val))
        #         f1_at_k.append(self.compute_f1(k_val))
        #
        #     r_p = self.compute_r_precision(doc_score_dict qid)
        #     avg_p = self.compute_avg_precision()
        #     ndcg = self.compute_ndcg()
        #
        #     self.eval_scores[qid] = (r_p, avg_p, ndcg, precision_at_k, recall_at_k, f1_at_k)

    #
    # def compute_r_precision(self, doc_score_dict, qid):
    #     num_rel = len(self.qrel[qid])
    #     num_ret = len(doc_score_dict)
    #     if num_ret < num_rel:
    #         r_prec = len(doc_score_dict) / len(self.qrel[qid])
    #     else:
    #         frac_num_rel = num_rel - num_ret
    #         if frac_num_rel > 0:
    #             r_prec =  (1 - frac_num_rel) * prec_list[num_rel + 1]
    #         else:
    #             r_prec = prec_list[num_rel]


    def compute_avg_precision(self):
        pass

    def compute_ndcg(self):
        pass

    def compute_precision(self, k_val):
        pass

    def compute_recall(self, k_val):
        pass

    def compute_f1(self, k_val):
        pass

    def eval_print(self, qid, num_ret, num_rel, num_rel_ret, prec_at_recalls, avg_prec, prec_at_k, r_prec):
        print("\nQueryid (num: \t {} \n".format(str(qid)))
        print("Total number of documents over all queries\n")
        print("\t Retrieved: \t {}".format(str(num_ret)))
        print("\t Relevant: \t {}".format(str(num_rel)))
        print("\t Rel_ret: \t {}".format(str(num_rel_ret)))
        print("Interpolated Recall - Precision Averages:\n")

        s_time = 0.00
        for r in self.recalls:
            print(" \t at " + str(r) + " \t "+ str(prec_at_recalls[r]) + "\n")

        print("Average precision (non-interpolated) for all rel docs(averaged over queries)\n")
        print("\t \t {}\n".format(str(avg_prec)) )
        print("Precision:\n")

        for kval in self.k:
            print("\t At \t {} docs: \t {}\n".format(str(kval), str(prec_at_k[kval])))

        print("R-Precision (precision after R (= num_rel for a query) docs retrieved):\n")
        print("\t Exact: \t {}\n".format(str(r_prec)))

def main(argv):
    # python -q qrel ranks
    args = sys.argv[1:]

    if len(args) > 2:
        qrel = args[1]
        ranks = args[2]
        q = True
        eval = Evaluation(ranks, qrel, print_all_queries=True)
    else:
        qrel = args[0]
        ranks = args[1]
        q = False
        eval = Evaluation(ranks, qrel)

    eval.evaluate()






# if __name__ == "__main__":
#     qrel = "/Users/ellataira/Desktop/is4200/homework--5-ellataira/Results/qrels.adhoc.51-100.AP89.txt"
#     ranked = "/Users/ellataira/Desktop/is4200/homework--5-ellataira/Results/es_builtin6.txt"
#     eval = Evaluation(ranked, qrel)
#     eval.evaluate()
