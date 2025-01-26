def checkProfile(steps):
    if not isinstance(steps, list):
        return False

    if len(steps) != 8760:
        return False

    if not all(isinstance(item, (int, float)) for item in steps):
        return False

    return True
