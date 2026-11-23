def checkProfile(steps):
    if not isinstance(steps, list):
        return False

    if len(steps) != 8760:
        return False

    return all(isinstance(item, (int, float)) for item in steps)
