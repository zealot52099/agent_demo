def generate_prompt_template(query, skill_descriptions):
    """
    Generates a prompt template based on the user query and relevant skill descriptions.

    Parameters:
    - query (str): The user query to be processed.
    - skill_descriptions (list): A list of skill descriptions relevant to the query.

    Returns:
    - str: A formatted prompt template.
    """
    skills_info = "\n".join(skill_descriptions)
    prompt_template = f"User Query: {query}\n\nRelevant Skills:\n{skills_info}\n\nPlease provide a detailed response based on the above skills."
    return prompt_template


def inject_skills_into_prompt(query, skill_registry):
    """
    Injects relevant skills into the prompt based on the user query.

    Parameters:
    - query (str): The user query to be processed.
    - skill_registry (SkillRegistry): An instance of SkillRegistry to retrieve skills.

    Returns:
    - str: A prompt with injected skills.
    """
    relevant_skills = skill_registry.search_skills(query)
    skill_descriptions = [skill.description for skill in relevant_skills]
    return generate_prompt_template(query, skill_descriptions)