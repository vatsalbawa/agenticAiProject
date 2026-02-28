def calculate(expression: str):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {str(e)}"


def search(query: str):
    
    query_lower = query.lower()

    if "gdp" in query_lower and "india" in query_lower:
        return "India GDP growth in 2024 is approximately 7 percent."

    if "current year" in query_lower:
        return "The current year is 2024."

    return "No relevant results found."
