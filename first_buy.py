import datetime

def timestamp_to_utc(timestamp):
    """Converts a Unix timestamp to a UTC datetime object.

    Args:
        timestamp: An integer representing the number of seconds since the Unix epoch.

    Returns:
        A datetime object representing the UTC time, or None if the timestamp is invalid.
    """
    try:
        utc_datetime = datetime.datetime.utcfromtimestamp(timestamp)
        return utc_datetime
    except (TypeError, ValueError):
        return None

def format_utc_datetime(utc_datetime):
    """Formats a UTC datetime object into a readable string.

    Args:
        utc_datetime: A datetime object representing the UTC time.

    Returns:
        A formatted string representing the UTC time, or None if the input is invalid.
    """
    if not isinstance(utc_datetime, datetime.datetime):
        return None

    return utc_datetime.strftime('%Y-%m-%d %H:%M:%S UTC')


# Example useage:
timestamp = 1738717897  # Example timestamp (March 15, 2023, 00:00:00 UTC)
utc_datetime = timestamp_to_utc(timestamp)

if utc_datetime:
    formatted_datetime = format_utc_datetime(utc_datetime)
    print(f"UTC time: {formatted_datetime}")
else:
    print("Invalid timestamp")
    
array = [1, 2, 3, 4, 5]
for item in reversed(array):
    print(item)

