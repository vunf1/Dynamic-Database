def generate_folder_patterns(brand, model, device_type):
    '''
    Folder Pattern Generator '#   _'
    Generates various folder naming patterns based on brand, model, and device type.
    '''
    folder_patterns = []

    # Basic combinations
    base_patterns = [
        f"{brand} {model} {device_type}",
        f"{brand}_{model}_{device_type}",
        f"{brand}{model}{device_type}",
        f"{brand} {model}_{device_type}",
        f"{brand}_{model} {device_type}",
        f"{brand} {model}",
        f"{brand}_{model}",
        f"{brand}{model}",
        f"{model} {device_type}",
        f"{model}_{device_type}",
        f"{model}{device_type}",
        f"{model}{device_type}",
        f"{model}"
    ]

    # Add patterns with underscores at the end
    for pattern in base_patterns:
        folder_patterns.append(pattern)
        folder_patterns.append(f"{pattern}_")

    # Add hash-prefixed versions
    for pattern in base_patterns:
        folder_patterns.append(f"#{pattern}")
        folder_patterns.append(f"#{pattern}_")

    # Add additional brand-model combinations
    extended_patterns = [
        f"{brand} {model}{device_type}",
        f"{brand}_{model}{device_type}",
        f"{brand}{model} {device_type}",
        f"{brand}{model}_{device_type}",
    ]

    for pattern in extended_patterns:
        folder_patterns.append(pattern)
        folder_patterns.append(f"{pattern}_")
        folder_patterns.append(f"#{pattern}")
        folder_patterns.append(f"#{pattern}_")

    return folder_patterns
