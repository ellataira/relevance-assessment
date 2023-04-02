import math
import pickle

class Utils:

    """
        saves a given dictionary to a pickle files
        @input filename / path to save to
        @input dictionary to be saved """
    def save_dict(self, filename, dict):
        file = open(filename, "wb")
        pickle.dump(dict, file)
        file.close()
        print("saved dictionary to " + filename + "\n")

    # converts .pkl to dictionary
    def read_pickle(self, filepath):
        infile = open(filepath, 'rb')
        dict = pickle.load(infile)
        infile.close()
        return dict

# u = Utils()
# inlinks = u.read_pickle("/Users/ellataira/Desktop/is4200/homework-4-ellataira/Code/data/merged_inlinks.pkl")
# outlinks = u.read_pickle("/Users/ellataira/Desktop/is4200/homework-4-ellataira/Code/data/merged_outlinks.pkl")
# print(outlinks["https://en.wikipedia.org/wiki/Leftist"])
# print(inlinks["https://en.wikipedia.org/wiki/Leftist"])