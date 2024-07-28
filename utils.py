import json
from TCPSegment import TCPSegment

def encode_segment(segment, encoding_format='utf-8'):
    segment_dict = {
        'sourcePort': segment.sourcePort,
        'destPort': segment.destPort,
        'sequenceNum': segment.sequenceNum,
        'ACKBit': segment.ACKBit,
        'ACKNum': segment.ACKNum,
        'SYNBit': segment.SYNBit,
        'FINBit': segment.FINBit,
        'rwnd': segment.rwnd,
        'data': segment.data,
        'checksum': segment.checksum
    }
    segment_str = str(segment_dict)
    return segment_str.encode(encoding_format)

def decode_segment(encoded_data, encoding_format='utf-8'):
    """
    Decodes an encoded byte string into a TCPSegment object.
    
    :param encoded_data: Encoded byte string of the TCPSegment.
    :param encoding_format: The encoding format to use (default is 'utf-8').
    :return: Decoded TCPSegment object.
    """
    segment_json_str = encoded_data.decode(encoding_format)
    segment_dict = json.loads(segment_json_str)
    return TCPSegment(**segment_dict)