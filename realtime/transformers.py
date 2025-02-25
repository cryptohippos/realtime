"""
Converts the change Payload into native Python types.
"""
import json
from dateutil.parser import parse


"""
Takes an array of columns and an object of string values then converts each string value
to its mapped type.

:param columns:
:param records:
:param options: The map of various options that can be applied to the mapper

"""

def convert_change_data(columns, records, options={}):
    skip_types = options.get("skip_types") if options.get(
        "skip_types") == "undefined" else []
    return {
        key: convert_column(key, columns, records, skip_types)
        for key in records.keys()
    }


def convert_column(column_name, columns, records, skip_types):
    column = next(filter(lambda x: x.get("name") == column_name, columns))
    if not column or column.get("type") in skip_types:
        return noop(records[column_name])
    else:
        return convert_cell(column.get("type"), records[column_name])


def convert_cell(_type: str, string_value: str):
    try:
        if string_value is None:
            return None
        # If data type is an array
        if _type[0] == "_":
            array_value = _type[1:len(_type)]
            return to_array(string_value, array_value)
        # If it's not null then we need to convert it to the correct type
        if _type in list(conversion_map.keys()):
            conv_func = conversion_map[_type]
            return conv_func(string_value)
        else:
            return noop(string_value)
    except Exception as e:
        print(
            f"Could not convert cell of type {_type} and value {string_value}")
        print(f"This is the error {e}")
        return string_value


def noop(string_value: str):
    return string_value

def to_boolean(string_value: str):
    if string_value == "t":
        return True
    elif string_value == "f":
        return False
    else:
        return None

def to_date(string_value: str):
    return parse(string_value)

def to_date_range(string_value: str):
    arr = json.dumps(string_value)
    return [parse(arr[0]), parse(arr[1])]

def to_float(string_value):
    return float(string_value)

def to_int(string_value: str):
    return int(string_value)

def to_int_range(string_value: str):
    arr = json.loads(string_value)
    return [int(arr[0]), int(arr[1])]

def to_json(string_value: str):
    return json.loads(string_value)

def to_array(string_value: str, type: str):
    # this takes off the '{' & '}'
    string_enriched = string_value[1: len(string_value) - 1]

    # Converts the string into an array
    # if string is empty (meaning the array was empty), an empty array will be immediately returned
    string_array = string_enriched.split(
        ",") if len(string_enriched) > 0 else []
    return list(map(lambda string: convert_cell(type, string), string_array))

def to_timestamp_string(string_value: str):
    return string_value.replace(" ", "T")



conversion_map = {
    'abstime': noop, 'bool': to_boolean, 'date': noop, 'daterange': to_date_range,
    'float4': to_float, 'float8': to_float, 'int2': to_int, 'int4': to_int, 'int8': to_int,
    'int4range': to_int_range, 'int8range': to_int_range, 'json': to_json, 'jsonb': to_json,
    'money': to_float, 'numeric': to_float, 'oid': to_int, 'reltime': noop, 'time': noop,
    'timestamp': to_timestamp_string, 'timestamptz': parse, 'timetz': parse, 'tsrange': to_date_range,
    'tstzrange': to_date_range
}

