from flask import Flask, redirect, url_for, render_template, request
from functions import initialize_conversation, initialize_conv_reco, get_chat_model_completions, moderation_check,intent_confirmation_layer,dictionary_present,compare_books_with_user,recommendation_validation

import openai
import ast
import re
import pandas as pd
import json
import time

# Sets the api key for processing with chatgpt
openai.api_key = open("api_key.txt", "r").read().strip()

app = Flask(__name__)

# Initialises chat bot conversations
conversation_bot = []
conversation = initialize_conversation()
introduction = get_chat_model_completions(conversation)
conversation_bot.append({'bot':introduction})
top_2_books = None

# Routes to the default page
@app.route("/")
def default_func():
    global conversation_bot, conversation, top_2_books
    return render_template("index_bookAssistant.html", name_xyz = conversation_bot)

# routes to the default page after end conversation
@app.route("/end_conv", methods = ['POST','GET'])
def end_conv():
    global conversation_bot, conversation, top_2_books
    conversation_bot = []
    conversation = initialize_conversation()
    introduction = get_chat_model_completions(conversation)
    conversation_bot.append({'bot':introduction})
    top_2_books = None
    return redirect(url_for('default_func'))

'''
Handles the conversation with the chat bot.

Invoked whenever user inputs message.
takes the user input message, extracts the features of books user looking for from the conversation
and suggests recommended books.
All input and output messages goes through moderation check to make sure the conversations aligns with books.
'''
@app.route("/assistant", methods = ['POST'])
def assistant():
    global conversation_bot, conversation, top_2_books, conversation_reco
    user_input = request.form["user_input_message"]
    prompt = 'Remember your system message and that you are an intelligent book assistant. So, you only help with questions around book.'
    moderation = moderation_check(user_input)
    if moderation == 'Flagged':
        return redirect(url_for('end_conv'))

    if top_2_books is None:
        # Identify the matching books for user profile by engaging with user
        conversation.append({"role": "user", "content": user_input + prompt})
        conversation_bot.append({'user':user_input})

        response_assistant = get_chat_model_completions(conversation)

        moderation = moderation_check(response_assistant)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))

        # checks if all required features are obtained
        confirmation = intent_confirmation_layer(response_assistant)

        moderation = moderation_check(confirmation)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))

        if "No" in confirmation:
            # Engage in further conversation with user to obtain the missing feature.
            conversation.append({"role": "assistant", "content": response_assistant})
            conversation_bot.append({'bot':response_assistant})
        else:
            # Proceed with extracting the matching books.
            response = dictionary_present(response_assistant)

            moderation = moderation_check(response)
            if moderation == 'Flagged':
                return redirect(url_for('end_conv'))

            conversation_bot.append({'bot':"Thank you for providing all the information. Kindly wait, while I fetch the books: \n"})
            top_2_books = compare_books_with_user(response)

            validated_reco = recommendation_validation(top_2_books)

            if len(validated_reco) == 0:
                conversation_bot.append({'bot':"Sorry, we do not have books that match your requirements. Connecting you to a human expert. Please end this conversation."})

            conversation_reco = initialize_conv_reco(validated_reco)
            recommendation = get_chat_model_completions(conversation_reco)

            moderation = moderation_check(recommendation)
            if moderation == 'Flagged':
                return redirect(url_for('end_conv'))

            conversation_reco.append({"role": "user", "content": "This is my user profile" + response})

            conversation_reco.append({"role": "assistant", "content": recommendation})
            conversation_bot.append({'bot':recommendation})

            print(recommendation + '\n')

    else:
        # Engage in conversation with the user recommending the matched books and any details further requested.
        conversation_reco.append({"role": "user", "content": user_input})
        conversation_bot.append({'user':user_input})

        response_asst_reco = get_chat_model_completions(conversation_reco)

        moderation = moderation_check(response_asst_reco)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))

        conversation.append({"role": "assistant", "content": response_asst_reco})
        conversation_bot.append({'bot':response_asst_reco})
    return redirect(url_for('default_func'))

if __name__ == '__main__':
    app.run(debug=True, host= "0.0.0.0")