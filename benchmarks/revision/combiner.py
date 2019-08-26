import os
import json

prefixes = ["DEFAULT-", "PCA-", "x2-", "EPS-", "EUCLID-", "NODIST-"]

location = os.path.join(".")

matched = {}

for file in os.listdir(location):

    if not any(file.startswith(prefix) for prefix in prefixes):
        continue

    with open(os.path.join(location, file)) as f:
        print(file)
        data = json.load(f)

    for p in prefixes:
        file = file.replace(p, "")

    if file not in matched.keys():
        matched[file] = []

    matched[file].append(data)

for key in matched.keys():

    array = matched[key]
    first = array.pop(0)

    for other in array:
        for task in first.keys():
            first[task].update(other[task])

    with open(os.path.join(location, f"ALL-{key}"), "w") as f:
        json.dump(first, f)