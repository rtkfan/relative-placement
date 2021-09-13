# rp_calc.py
# calculates aggregate ranking of a set of candidates from judges' rankings
# using the Relative Placement method

import pandas as pd;
import numpy as np;
import math;
import sys;

def find_majority_candidates(indata, therank, threshold):
# takes in a working copy of the data, rank at which to check, and threshold for a majority
# returns a dataframe of candidates who satisfy the majority criteria, along with the number
# of judges that makes up the majority as well as the sum of ordinals that make up the majority
# (to handle simple tiebreak scenarios)
    at_rank = indata[indata['rank']<=therank].groupby('candidate').agg(num_judges = pd.NamedAgg(column='judge',aggfunc=(lambda x: x.count())),
                                                                       rank_ordinals = pd.NamedAgg(column='rank',aggfunc=sum))
    at_rank = at_rank[at_rank['num_judges'] >= threshold]
    return at_rank

def tiebreaks(indata, fulldata):
# takes in a dataframe of tiebreak participants, the dataframe of the original data,
# and the ranking level that caused the tiebreak.
# returns a sorted list of tiebreak participants
    return indata.index.values.tolist()
    pass

# Judges rank the top N candidates only; if it's 0 then judges rank all candidates.
RANK_TOP_N = 0;

# Read in CSV data
rawdata = pd.read_csv(sys.stdin);


num_judges = rawdata["judge"].nunique()
num_candidates = rawdata["candidate"].nunique()
max_rank = rawdata["rank"].max()
majority = math.floor(num_judges/2.0 + 1)

# output array; populated in order as results are computed
final_rankings = []

workingcopy = rawdata.copy()

next_rank = 1
working_rank = 1

while (workingcopy.size > 0) and ((next_rank <= RANK_TOP_N) or (RANK_TOP_N == 0)):
    print('working copy size ',workingcopy.size)
    print('Determining rank ',next_rank, ' looking at judge rankings ',working_rank,' or better')
    ranked_candidates = []
    #determine how many candidates have a majority rank at least N or better
    at_rank = find_majority_candidates(workingcopy, working_rank, majority)
    num_at_max = len(at_rank[at_rank['num_judges'] == at_rank['num_judges'].max()].index.values)
    if num_at_max == 0:
        #no candidates have a majority at this working_rank
        pass
    elif num_at_max == 1:
        #the candidate with the solitary max majority gets the rank
        ranked_candidates.append(at_rank[at_rank['num_judges'] == at_rank['num_judges'].max()].index[0])
    else:
        #else if highest majority is a tie, go to tiebreaks (sum of ordinals, then next ranking, then showdown)
        ranked_candidates.extend(tiebreaks(at_rank[at_rank['num_judges'] == at_rank['num_judges'].max()],rawdata))
    if len(ranked_candidates) == 0:
        working_rank += 1
    else:
        final_rankings.extend(ranked_candidates)
        print(final_rankings)
        next_rank = len(final_rankings) + 1
        working_rank = next_rank
        workingcopy = workingcopy[~workingcopy['candidate'].isin(final_rankings)]
