from Election import Election
import pickle
import os

PARLIAMENT_SIZE = 120


def load_election_data(filename, data_path=None):
    """
    A function that loads the provided data.
    :param filename: the name of the file containing the data you wish to load, with extension.
    :param data_path: path to directory where data is stored. If None, the current directory will be used.
    :return: Loaded data (in a data container, may vary).
    """
    file_path = filename
    if data_path:
        file_path = os.path.join(data_path, file_path)
    with open(file_path, 'rb') as file:
        instance = pickle.load(file)
    return instance


def bader_ofer(election):
    """
    Function that allocates seats for Israeli parliament according to Bader-Ofer law.
    :param election: Election instance
    :return: mapping (=dict) of allocated seats/mandates for each party.
    """
    total_votes = election.total_votes
    votes_per_party = election.votes_per_party
    surplus_pairs = election.surplus_pairs
    electoral_threshold = election.electoral_threshold

    # remove parties that did not pass the electoral threshold
    parties_to_remove = [party for party in votes_per_party.keys() if votes_per_party[party] / total_votes < electoral_threshold]
    for party in parties_to_remove:
        del votes_per_party[party]
        for pair in surplus_pairs:
            if party in pair:
                surplus_pairs.remove(pair)

    valid_votes = sum(votes_per_party.values())

    # baseline seats
    votes_per_seat = valid_votes/PARLIAMENT_SIZE
    results = {party: int(votes//votes_per_seat) for party, votes in votes_per_party.items()}

    # surplus seats
    surplus_seats = PARLIAMENT_SIZE - sum(results.values())
    for _ in range(surplus_seats):
        # merge surplus parties together
        surplus_amounts = {party: (votes, results[party]) for party, votes in votes_per_party.items()}
        for pair in surplus_pairs:
            surplus_amounts[(pair[0], pair[1])] = (surplus_amounts[pair[0]][0] + surplus_amounts[pair[1]][0],
                                                   surplus_amounts[pair[0]][1] + surplus_amounts[pair[1]][1])
            del surplus_amounts[pair[0]]
            del surplus_amounts[pair[1]]

        # get and sort counts for surplus seat
        surplus_bid = {party: surplus_amounts[party][0] / (surplus_amounts[party][1] + 1) for party in surplus_amounts.keys()}
        top = max(surplus_bid, key=surplus_bid.get)

        # add the surplus seat to the results
        if isinstance(top, str):
            results[top] += 1
        else:
            # do internal surplus allocation
            first_score = votes_per_party[top[0]] / (results[top[0]] + 1)
            second_score = votes_per_party[top[1]] / (results[top[1]] + 1)
            if first_score > second_score:
                results[top[0]] += 1
            else:
                results[top[1]] += 1
    for party in parties_to_remove:
        results[party] = 0
    return results


def largest_remainders(election):
    """
    Function that allocates seats for parliament according to LR method with an electoral threshold.
    This is a bonus question.
    :param election: Election instance
    :return: mapping (=dict) of allocated seats/mandates for each party.
    """
    total_votes = election.total_votes
    votes_per_party = election.votes_per_party
    surplus_pairs = election.surplus_pairs
    electoral_threshold = election.electoral_threshold
    parties_to_remove = [party for party in votes_per_party.keys() if
                         votes_per_party[party] / total_votes < electoral_threshold]
    for party in parties_to_remove:
        del votes_per_party[party]

    valid_votes = sum(votes_per_party.values())
    # baseline seats
    votes_per_seat = valid_votes / PARLIAMENT_SIZE
    results = {party: int(votes // votes_per_seat) for party, votes in votes_per_party.items()}

    # surplus seats
    surplus_votes= {party: votes % votes_per_seat for party, votes in votes_per_party.items()}
    sorted_surplus_votes = sorted(surplus_votes.items(), key=lambda x: x[1], reverse=True)
    surplus_seats = PARLIAMENT_SIZE - sum(results.values())
    for i in range(surplus_seats):
        results[sorted_surplus_votes[i][0]] += 1

    for party in parties_to_remove:
        results[party] = 0

    return results



def main():
    election_results = load_election_data("ElectionResults.txt", "data")

    success = True

    for election_id in range(19, 26):
        election = load_election_data(f"Election{election_id}.txt", "data")
        predictions = bader_ofer(election)
        if predictions != election_results[election_id]:
            print("Error in election {}, predicted: {}, actual: {}".format(
                election_id, predictions, election_results[election_id]))
            success = False

    if success is True:
        print("Success! All elections 19-25 predicted correctly")

    # 2th question
    coalition = ["Likud", "ZionutDatit", "Shas", "YahadutTora"]
    # A. no surplus agreements
    election = load_election_data("Election25.txt", "data")
    election.surplus_pairs = []
    predictions = bader_ofer(election)
    coalition_mandates = sum([predictions[party] for party in coalition])
    print("without the surplus agreements the coalition has ", coalition_mandates, " mandates instead of 64")

    # B. threshold 3%
    election = load_election_data("Election25.txt", "data")
    election.electoral_threshold = 0.03
    predictions = bader_ofer(election)
    coalition_mandates= sum([predictions[party] for party in coalition])
    print("with the threshold of 3% the coalition has ", coalition_mandates, " mandates instead of 64")

    # C. threshold 2%
    election = load_election_data("Election25.txt", "data")
    election.electoral_threshold = 0.02
    predictions = bader_ofer(election)
    coalition_mandates = sum([predictions[party] for party in coalition])
    print("with the threshold of 2% the coalition has ", coalition_mandates, " mandates instead of 64")

    # D. threshold 1%
    election = load_election_data("Election25.txt", "data")
    election.electoral_threshold = 0.01
    predictions = bader_ofer(election)
    coalition_mandates = sum([predictions[party] for party in coalition])
    print("with the threshold of 1% the coalition has ", coalition_mandates, " mandates instead of 64")

    # D. "HaBait HaYehudi" joins the coalition
    election = load_election_data("Election25.txt", "data")
    election.electoral_threshold = 0.01
    coalition.append("BayitYehudi")
    coalition_mandates = sum([predictions[party] for party in coalition])
    print("the new coalition has ", coalition_mandates, " mandates")

    # bonus question
    election = load_election_data("Election25.txt", "data")
    election.electoral_threshold = 0.02
    coalition.remove("BayitYehudi")
    predictions = largest_remainders(election)
    coalition_mandates = sum([predictions[party] for party in coalition])
    print("according to largest remainders with the threshold of 2% the coalition has ", coalition_mandates, " mandates instead of 64")

if __name__ == "__main__":
    main()
