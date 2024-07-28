import pickle

def encode_segment(segment):
    return pickle.dumps(segment)


def decode_segment(encoded_data):
    return pickle.loads(encoded_data)