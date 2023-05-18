import time
from lib.database import featurebase_query

start = time.time()

try:
    query = "CREATE TABLE IF NOT EXISTS collatz_flotz (_id INT, prev_set INT, next_set INT);"
    result = featurebase_query({"sql": query})
except Exception as ex:
    print(ex)

values = []
existing_numbers = {}  # Dictionary to store already processed numbers

for x in range(1, 30000):
    # the proof is we foolishly believe this will exit
    while True:
        # set what we are, currently
        prev_set = x

        # check if we are odd or even
        is_odd = x % 2

        # run the algo and update our number
        if is_odd:
            x = (x * 3) + 1
        else:
            x = int(x / 2)

        # check if we have the newly calculated number already
        if x in existing_numbers:
            _next_set = existing_numbers[x]

            values.append((x, prev_set, _next_set))
            break
        else:
            # we don't have the next number, so we set it
            is_odd = x % 2

            if is_odd:
                next_set = (x * 3) + 1
            else:
                next_set = int(x / 2)

            values.append((x, prev_set, next_set))

        if x == 1:
            break

    if len(values) >= 1000:  # Adjust the batch size as per your needs
        query = "INSERT INTO collatz_flotz (_id, prev_set, next_set) VALUES (%s, %s, %s);" % (
            "%s", "%s", "%s"
        )
        result = featurebase_query({"sql": query, "values": values})
        values = []

# Insert any remaining values
if values:
    query = "INSERT INTO collatz_flotz (_id, prev_set, next_set) VALUES (%s, %s, %s);" % (
        "%s", "%s", "%s"
    )
    result = featurebase_query({"sql": query, "values": values})

end = time.time()
print("Execution time:", end - start)
