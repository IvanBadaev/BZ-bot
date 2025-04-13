def is_valid_time_format(time: str):
    import re
    pattern = r"^([01]?[0-9]|2[0-3]):([0-5]?[0-9])$"  # Regex for HH:MM format
    return bool(re.match(pattern, time))

