from lib.database import featurebase_query
import random
def iterate_collatz_sequence(start_number):
    sequence = [start_number]

    while start_number != 1:
        # Query for the previous number in the chain
        query = "SELECT prev_set FROM collatz_flotz WHERE _id = %s;" % start_number
        result = featurebase_query({"sql": query, "values": [start_number]})

        try:
            foo = result[0][1]
            y = random.choice([0,1])
        except:
            y = 0

        if result.get('data'):
            print(y)
            prev_set = result.get('data')[0][y]
            sequence.append(prev_set)
            start_number = prev_set
        else:
            break

    return sequence

# Initialize variables
current_number = 1
longest_chain = []
max_chain_length = 0

while True:
    # Query for the next number in the chain
    query = "SELECT next_set FROM collatz_flotz WHERE _id = %s;" % current_number
    result = featurebase_query({"sql": query, "values": [current_number]})

    if result.get('data'):
        next_number_tuple = result.get('data')[0]
        next_number = next_number_tuple[0] if len(next_number_tuple) == 1 else next_number_tuple[1]
        print(next_number)
        # Iterate on the chain starting from current_number
        sequence = iterate_collatz_sequence(current_number)

        # Check if the chain is longer than the previous longest chain
        if len(sequence) > max_chain_length:
            max_chain_length = len(sequence)
            longest_chain = sequence

        current_number = next_number
    else:
        break

print("Longest Chain:")
print("Length:", max_chain_length)
print("Sequence:", longest_chain)
