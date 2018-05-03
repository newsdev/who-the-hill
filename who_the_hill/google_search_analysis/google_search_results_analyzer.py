import ast

mismatches = {}
total_images = 0
total_matches = 0

with open('search_results.txt', 'r') as f:
    for line in f:
        total_images += 3
        try:
            name, results = line.split('[', 1)
            name = name[:-2]
        except ValueError:
            print(line)
        results_array = ast.literal_eval('[' + results.strip())
        for result in results_array:
            if name != result:
                if name not in mismatches:
                    mismatches[name] = []
                mismatches[name].append(result)
            else:
                total_matches += 1

with open('mismatches.txt', 'w') as g:
    for ref_name in mismatches.keys():
        g.write("{}, {}\n".format(ref_name.strip(), str(mismatches[ref_name])))

print(float(total_matches)/float(total_images))