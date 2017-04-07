import json

def get_data(filename):
    with open(filename) as data_file:
        return json.load(data_file)

def get_results(filename):
    data = get_data(filename)
    # Backward compatability
    if type(data) != type(dict()):
        return data
    return data['results']

def get_flags(filename):
    data = get_data(filename)
    return data['flags']

def get_max_statistic(results, min_epoch, max_epoch, group, measure):
    if max_epoch < 0:
        print 'Invalid epoch: ', max_epoch
        exit()
    if min_epoch > max_epoch:
        print 'Invalid epoch range; {:d} to {:d}'.format(min_epoch, max_epoch)
        exit()
    if group not in ['train', 'dev', 'test'] or group not in results[0]:
        print 'Invalid group: ', group
        exit()
    if measure not in results[0][group].keys():
        print 'Invalid measure: ', measure
        exit()
    max_score = -float('inf')
    max_score_results = {}
    for i in range(min_epoch, max_epoch+1):
        result = results[i]
        score = result[group][measure]
        if score > max_score:
            max_score = score
            max_score_results = result
    return max_score, max_score_results
