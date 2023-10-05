def optimize_aws_tags(data):
    # If the data is a dict, we can apply our optimization
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # We target the 'Tags' key specifically
            if key == "Tags" and isinstance(value, list):
                tag_dict = {}
                for item in value:
                    # The value should be a dict with 'Key' and 'Value'
                    if isinstance(item, dict) and "Key" in item and "Value" in item:
                        tag_dict[item["Key"]] = item["Value"]
                    else:
                        # If not in the expected format, return the original data without changes
                        return data
                new_dict[key] = tag_dict
            else:
                # For all other keys, we keep their values, potentially optimized if they're dicts too
                new_dict[key] = optimize_aws_tags(value)
        # The new dict has been fully constructed and is returned
        return new_dict
    # If the data is a list, we apply our function to all its elements and return a new list
    elif isinstance(data, list):
        return [optimize_aws_tags(i) for i in data]
    else:
        # If the data is neither a dict nor a list, we can't do anything with it and return it as it is
        return data
