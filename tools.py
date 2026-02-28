def calculate(expression: str):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {str(e)}"


def search(query: str):
    # Simulated search result
    if "india gdp growth" in query.lower():
        return "India GDP growth in 2024 is approximately 7 percent."
    return "No relevant results found."
