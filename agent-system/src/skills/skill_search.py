def search_skills(query):
    """
    Searches for relevant skills based on the input query.

    Args:
        query (str): The user input query to search for skills.

    Returns:
        list: A list of skills that match the query.
    """
    from .registry import SkillRegistry

    # Initialize the skill registry
    registry = SkillRegistry()
    
    # Retrieve all skills from the registry
    all_skills = registry.get_all_skills()
    
    # Filter skills based on the query
    relevant_skills = [skill for skill in all_skills if query.lower() in skill['description'].lower()]
    
    return relevant_skills