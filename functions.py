import openai
import ast
import re
import pandas as pd
import json

'''
Initialises the prompts to begin conversation.
'''
def initialize_conversation():
    '''
    Returns a list [{"role": "system", "content": system_message}]
    '''
    delimiter = "####"
    example_user_req = {'Genre': 'Frictional','User Reading phase': 'low','User Maturity Level': 'medium'}
    
    genre_values = {'Frictional','Non-Frictional','Self Improvement','Knowledge Expansion'}

    system_message = f"""

    You are an intelligent library assistant expert and your goal is to find the best book for a user.
    You need to ask relevant questions and understand the user profile by analysing the user's responses.
    You final objective is to fill the values for the different keys ('Genre','User Reading phase','User Maturity Level') in the python dictionary and be confident of the values.
    These key value pairs define the user's profile.
    The python dictionary looks like this {{'Genre': 'values','User Reading phase': 'values','User Maturity Level','values'}}
    The values for all keys except Genre should be 'low', 'medium', or 'high' based on the readers capability for the corresponding keys, as stated by user.
    The values currently in the dictionary are only representative values.
    The Genre key values be one of the {genre_values} by following the below mapping:
    
    Frictional: < non-real or imaginary contents like Alice in Wonderland, Gullivers travel > , \n
    Non-Frictional: < Real life stories, biographies and auto-biographies > , \n
    Self Improvement: <Guides/Helps with improving the readers personalities, self care, health, financial situation> , \n
    Skill development: < Teaches/Trains readers on any particular technical or non-technical skills/hobbies > , \n
    Knowledge Expansion: < school and college students books, Reference books on any subjects, about nature and natural objects and phenomenon> ,\n
    

    {delimiter}Here are some instructions around the values for the different keys. If you do not follow this, you'll be heavily penalised.
    - The values for all keys except Genre should strictly be either 'low', 'medium', or 'high' based on the readers capability for the corresponding keys, as stated by user.
    - Do not randomly assign values to any of the keys. The values need to be inferred from the user's response.
    {delimiter}

    To fill the dictionary, you need to have the following chain of thoughts:
    {delimiter} Thought 1: Ask a question to understand the user's profile and requirements. \n
    If their primary need for the book is unclear. Ask another question to comprehend their needs.
    You are trying to fill the values of all the keys ('Genre','User Reading phase','User Maturity Level') in the python dictionary by understanding the user requirements.
    Identify the keys for which you can fill the values confidently using the understanding. \n
    Remember the instructions around the values for the different keys.
    Answer "Yes" or "No" to indicate if you understand the requirements and have updated the values for the relevant keys. \n
    If yes, proceed to the next step. Otherwise, rephrase the question to capture their profile. \n{delimiter}

    {delimiter}Thought 2: Now, you are trying to fill the values for the rest of the keys which you couldn't in the previous step.
    Remember the instructions around the values for the different keys. Ask questions you might have for all the keys to strengthen your understanding of the user's profile.
    Answer "Yes" or "No" to indicate if you understood all the values for the keys and are confident about the same.
    If yes, move to the next Thought. If no, ask question on the keys whose values you are unsure of. \n
    It is a good practice to ask question with a sound logic as opposed to directly citing the key you want to understand value for.{delimiter}

    {delimiter}Thought 3: Check if you have correctly updated the values for the different keys in the python dictionary.
    If you are not confident about any of the values, ask clarifying questions. {delimiter}

    Follow the above chain of thoughts and only output the final updated python dictionary. \n


    {delimiter} Here is a sample conversation between the user and assistant:
    User: "Hi, I Need a book for read."
    Assistant: "Great! May I know if you have any specific book in your mind."
    User: "Not Really, I am not a regular reader and I just want to read some story book that helps me relax and be fun."
    Assistant: "Thank you for providing that information. May I know what would be age range for the reader among these under 5, 5-12, 12-20, 20-40, 40 and above."
    User: "Yes, I am in 20-40"
    Assistant: "{example_user_req}"
    {delimiter}

    Start with a short welcome message and encourage the user to share their requirements.
    """
    conversation = [{"role": "system", "content": system_message}]
    return conversation


'''
Invokes the chatgpt model to obtain the messages for bot.
'''
def get_chat_model_completions(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
        max_tokens = 300
    )
    return response.choices[0].message["content"]


'''
Makes sure the input and output in complaint without any sensitive/vulnerable information.
'''
def moderation_check(user_input):
    response = openai.Moderation.create(input=user_input)
    moderation_output = response["results"][0]
    if moderation_output["flagged"] == True:
        return "Flagged"
    else:
        return "Not Flagged"


'''
Extracts the requirements features based on the user input and Identifies if all the required information for recommendation has been collected from the user.
'''    
def intent_confirmation_layer(response_assistant):
    delimiter = "####"
    genre_values = {'Frictional','Non-Frictional','Self Improvement','Knowledge Expansion'}
    prompt = f"""
    You are a senior evaluator who has an eye for detail.
    You are provided an input. You need to evaluate if the input has the following keys: 'Genre','User Reading phase','User Maturity Level'
    Next you need to evaluate if the keys have the the values filled correctly.
    The values for all keys except should be 'low', 'medium', or 'high' based on the importance as stated by user.
    The values for Genre key should be the one in {genre_values}.
    Output a string 'Yes' if the input contains the dictionary with the values correctly filled for all keys.
    Otherwise out the string 'No'.

    Here is the input: {response_assistant}
    Only output a one-word string - Yes/No.
    """


    confirmation = openai.Completion.create(
                                    model="gpt-3.5-turbo-instruct",
                                    prompt = prompt,
                                    temperature=0)


    return confirmation["choices"][0]["text"]




def dictionary_present(response):
    delimiter = "####"
    user_req = {'Genre': 'Frictional','User Reading phase': 'low','User Maturity Level': 'medium'}
    prompt = f"""You are a python expert. You are provided an input.
            You have to check if there is a python dictionary present in the string.
            It will have the following format {user_req}.
            Your task is to just extract and return only the python dictionary from the input.
            The output should match the format as {user_req}.
            The output should contain the exact keys and values as present in the input.
            The output should contain only the python dictionary.

            Here are some sample input output pairs for better understanding:
            {delimiter}
            input: {{'Genre'- 'Children','User Reading phase'- 'low','User Maturity Level'- 'medium'}}
            output: {{'Genre': 'Children','User Reading phase': 'low','User Maturity Level': 'medium'}}

            input: {{'Genre': 'Children','User Reading phase': 'low','User Maturity Level': 'medium'}}
            output: {{'Genre': 'Children','User Reading phase': 'low','User Maturity Level': 'medium'}}
            
            {delimiter}

            Here is the input {response}

            """
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens = 2000
        # temperature=0.3,
        # top_p=0.4
    )
    return response["choices"][0]["text"]



def extract_dictionary_from_string(string):
    regex_pattern = r"\{[^{}]+\}"

    dictionary_matches = re.findall(regex_pattern, string)

    # Extract the first dictionary match and convert it to lowercase
    if dictionary_matches:
        dictionary_string = dictionary_matches[0]
        dictionary_string = dictionary_string.lower()

        # Convert the dictionary string to a dictionary object using ast.literal_eval()
        dictionary = ast.literal_eval(dictionary_string)
    return dictionary



'''
Compares the user features and the books features to filter the books matching for the user requests.
This is a simple rule based logic and chatgpt is not used. Filters out top 2 books matching the user requirements.
'''
def compare_books_with_user(user_req_string):
    books_df= pd.read_csv('updated_books.csv')
    
    user_requirements = extract_dictionary_from_string(user_req_string)
   # print(user_requirements)
    filtered_books = books_df.copy()
   # filtered_books = filtered_books[filtered_books['Genre'] == genre].copy()
    #These lines create a copy of the laptop_df DataFrame and assign it to filtered_laptops.
    #They then modify the 'Price' column in filtered_laptops by removing commas and converting the values to integers.
    #Finally, they filter filtered_laptops to include only rows where the 'Price' is less than or equal to the budget.

    mappings = {
        'low': 0,
        'medium': 1,
        'high': 2
    }
    # Create 'Score' column in the DataFrame and initialize to 0
    filtered_books['Score'] = 0
    for index, row in filtered_books.iterrows():
        user_product_match_str = row['book_feature']
        book_values = extract_dictionary_from_string(user_product_match_str)
        #print(book_values)
        score = 0

        for key, user_value in user_requirements.items():
            #print(key)
            if key.lower() == 'genre':
                if book_values.get(key, None).lower() == user_value.lower():
                    score += 1
                    continue  # Skip further comparison for Genre
                else:
                    score = 0
                    break # Genre must be the same
            book_value = book_values.get(key, None)
            book_mapping = mappings.get(book_value.lower(), -1)
            user_mapping = mappings.get(user_value.lower(), -1)
            if book_mapping == user_mapping:
                ### If the book value is equal to the user value the score is incremented by 1
                score += 1

        filtered_books.loc[index, 'Score'] = score

    # Sort the laptops by score in descending order and return the top 2 products
    top_books = filtered_books.drop('book_feature', axis=1)
    top_books = top_books.sort_values('Score', ascending=False).head(2)

    return top_books.to_json(orient='records')




def recommendation_validation(laptop_recommendation):
    data = json.loads(laptop_recommendation)
    data1 = []
    for i in range(len(data)):
        if data[i]['Score'] >= 1:
            data1.append(data[i])

    return data1




def initialize_conv_reco(products):
    system_message = f"""
    You are an smart books expert and you are tasked with the objective to \
    solve the user queries about any book from the catalogue: {products}.\
    You should keep the user profile in mind while answering the questions.\

    Start with a brief summary of each book in the following format:
    1. <Book Title> : <Description of the book>
    2. <Book Title> : <Description of the book>

    """
    conversation = [{"role": "system", "content": system_message }]
    return conversation