def get_api_key(filename="poligon-api-key.txt"):
    try:
        with open(f"secrets/{filename}", 'r') as file:
            api_key = file.read().strip()
        return api_key
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None
