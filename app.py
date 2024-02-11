from flask import Flask, redirect, url_for, render_template, request
from functions import initialize_conversation, initialize_conv_reco, get_chat_model_completions, moderation_check,intent_confirmation_layer,dictionary_present,compare_books_with_user,recommendation_validation

import openai
import ast
import re
import pandas as pd
import json
import time

openai.api_key = open("api_key.txt", "r").read().strip()

app = Flask(__name__)

conversation_bot = []
conversation = initialize_conversation()
introduction = get_chat_model_completions(conversation)
conversation_bot.append({'bot':introduction})
top_2_books = None


@app.route("/")
def default_func():
    global conversation_bot, conversation, top_2_books
    return render_template("index_bookAssistant.html", name_xyz = conversation_bot)

@app.route("/end_conv", methods = ['POST','GET'])
def end_conv():
    global conversation_bot, conversation, top_2_books
    conversation_bot = []
    conversation = initialize_conversation()
    introduction = get_chat_model_completions(conversation)
    conversation_bot.append({'bot':introduction})
    top_2_books = None
    return redirect(url_for('default_func'))

@app.route("/assistant", methods = ['POST'])
def assistant():
    global conversation_bot, conversation, top_2_books, conversation_reco
    user_input = request.form["user_input_message"]
    prompt = 'Remember your system message and that you are an intelligent book assistant. So, you only help with questions around book.'
    moderation = moderation_check(user_input)
    if moderation == 'Flagged':
        return redirect(url_for('end_conv'))

    if top_2_books is None:
        conversation.append({"role": "user", "content": user_input + prompt})
        conversation_bot.append({'user':user_input})

        response_assistant = get_chat_model_completions(conversation)

        moderation = moderation_check(response_assistant)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))

        confirmation = intent_confirmation_layer(response_assistant)

        moderation = moderation_check(confirmation)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))

        if "No" in confirmation:
            conversation.append({"role": "assistant", "content": response_assistant})
            conversation_bot.append({'bot':response_assistant})
        else:
            print ("If - Please wait for 20 secs...")
            time.sleep(21)
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
        print ("If - Please wait for 20 secs...")
        time.sleep(21)
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