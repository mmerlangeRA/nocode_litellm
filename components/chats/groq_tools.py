
from groq import Groq
import os
import json
from settings.settings import settings

api_key = settings().model_keys.groqai
print(api_key)
client = Groq(api_key =api_key)
MODEL = 'mixtral-8x7b-32768'
MODEL= 'llama3-8b-8192'
MODEL='llama3-70b-8192'


# Example dummy function hard coded to return the score of an NBA game
def get_game_score(team_name):
    print("get_game_score of ",team_name)
    """Get the current score for a given NBA game"""
    if "warriors" in team_name.lower():
        return json.dumps({"game_id": "401585601", "status": 'Final', "home_team": "Los Angeles Lakers", "home_team_score": 121, "away_team": "Golden State Warriors", "away_team_score": 128})
    elif "lakers" in team_name.lower():
        return json.dumps({"game_id": "401585601", "status": 'Final', "home_team": "Los Angeles Lakers", "home_team_score": 121, "away_team": "Golden State Warriors", "away_team_score": 128})
    elif "nuggets" in team_name.lower():
        return json.dumps({"game_id": "401585577", "status": 'Final', "home_team": "Miami Heat", "home_team_score": 88, "away_team": "Denver Nuggets", "away_team_score": 100})
    elif "heat" in team_name.lower():
        return json.dumps({"game_id": "401585577", "status": 'Final', "home_team": "Miami Heat", "home_team_score": 88, "away_team": "Denver Nuggets", "away_team_score": 100})
    else:
        return json.dumps({"team_name": team_name, "score": "unknown"})

def run_conversation_no_tools(user_prompt):
    print("run_conversation_no_tools "+user_prompt)
    # Step 1: send the conversation and available functions to the model
    messages=[
        {
            "role": "system",
            "content": "You are a function calling LLM that uses the data extracted from the get_game_score function to answer questions around NBA game scores. Include the team and their opponent in your response."
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_game_score",
                "description": "Get the score for a given NBA game",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "team_name": {
                            "type": "string",
                            "description": "The name of the NBA team (e.g. 'Golden State Warriors')",
                        }
                    },
                    "required": ["team_name"],
                },
            },
        }
    ]

    print(tools)
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",  
        max_tokens=4096
    )
    print("response", response)
    response_message = response.choices[0].message
    print(response_message)
    
    tool_calls = response_message.tool_calls
    print("tool_calls", tool_calls)
    print("**************************************************************")
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_game_score": get_game_score,
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                team_name=function_args.get("team_name")
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        print(messages)
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )  # get a new response from the model where it can see the function response
        return second_response.choices[0].message.content
    
def run_conversation(messages, tools):
    print("run_conversation "+MODEL)

    tools_modified = [
{
    "type": "function",
    "function": {
        "name": "get_reference_info",
        "description": "Get information about Cyrus products.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "title": "Query",
                    "description": "The question you need to answer."
                }
            },
            "required": ["query"]
        }
    }
}
]
    print("messages are ",messages)
    print("tools_modified",tools_modified)
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools_modified,
        tool_choice="auto",  
        max_tokens=4096
    )
    print("response", response)
    return response
    response_message = response.choices[0].message
    print("response_message",response_message)
    tool_calls = response_message.tool_calls
    print("tool_calls", tool_calls)
    print("**************************************************************")
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_game_score": get_game_score,
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                team_name=function_args.get("team_name")
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        
        print(messages)
        return messages
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )  # get a new response from the model where it can see the function response
        return second_response.choices[0].message.content
   
user_prompt = "What was the score of the Warriors game?"
#print(run_conversation_no_tools(user_prompt))

messages=[
    {
        "role": "system",
        "content": "You are a function calling LLM that uses the data extracted from the get_reference_info function to answer"+
        " questions around Cyrus products in your response. Pierval Santé is one of Cyrus products."
    },
    {
        "role": "user",
        "content": "Summarize the advantages of Pierval Santé in 20 words",
    }
]
    
tools = [
{
    "type": "function",
    "function": {
        "name": "get_reference_info",
        "description": "Get information about Cyrus products.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "title": "Query",
                    "description": "The question you need to answer."
                }
            },
            "required": ["query"]
        }
    }
}
]



#print(run_conversation(messages,tools))

