from random import shuffle


def datasplit(data, ratios=[.7, .15, .15]):
    indices = range(len(data))
    shuffle(indices)
    training = ratios[0] * len(data)
    test = ratios[1] * len(data)
    valid = ratios[2] * len(data)
    training_indices = indices[:training]
    valid_indices = indices[training:training + valid]
    test_indices = indices[training+valid:training+valid+test]
    return data[training_indices], data[test_indices], data[valid_indices]
