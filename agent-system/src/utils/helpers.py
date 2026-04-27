def get_skill_descriptions(skills):
    descriptions = {}
    for skill in skills:
        descriptions[skill['name']] = skill['description']
    return descriptions

def format_prompt(query, skill_descriptions):
    prompt = f"User query: {query}\n\nAvailable skills:\n"
    for name, description in skill_descriptions.items():
        prompt += f"- {name}: {description}\n"
    return prompt

def extract_api_info(api_catalog):
    api_info = {}
    for api in api_catalog:
        api_info[api['name']] = {
            'description': api['description'],
            'endpoint': api['endpoint']
        }
    return api_info

def prepare_payload(query, history, skill_descriptions, api_info):
    prompt_part_1 = format_prompt(query, skill_descriptions)
    prompt_part_2 = "Please provide the relevant API information based on the user query."
    
    return {
        "temperature": 0,
        "seed": 42,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_part_1
                    },
                    {
                        "type": "text",
                        "text": prompt_part_2
                    }
                ]
            }
        ]
    }