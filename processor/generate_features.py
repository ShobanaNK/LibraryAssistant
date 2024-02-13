import os,json,ast
import openai
import pandas as pd

openai.api_key = open("../api_key.txt", "r").read().strip()

'''
Function that reads the books.csv and generates mapped_books.csv along with their feature mappings.
'''
def process():
    
    ##Run this code once to extract product info in the form of a dictionary
    books_df= pd.read_csv('books.csv')

    ## Create a new column "laptop_feature" that contains the dictionary of the product features
    books_df['book_feature'] = books_df['Description'].apply(lambda x: book_map_layer(x))
    print(books_df)

    books_df.to_csv("mapped_books.csv",index=False,header = True)

'''
Applies prompt to chatgpt to generate the required feature mappings from the book description.
'''
def book_map_layer(book_description):

  delimiter = "#####"
  #print(book_description)
  book_spec = {
      "Genre":"(The Genre of the book)",
      "User Reading phase":"(number of pages, literature/content complexity from reviews)",
      "User Maturity Level":"(Required Maturity Level of the target audience based on age groups, experience)",
  }

  range_values = {'low','medium','high'}

  genre_values = {'Frictional','Non-Frictional','Self Improvement','Knowledge Expansion'}

  prompt=f"""
  You are a Books Specifications Classifier whose job is to extract the key features of boks as per their requirements.
  To analyze each laptop, perform the following steps:
  Step 1: Extract the book's primary features from the description in {book_description}
  Step 2: Store the extracted features in {book_spec} \
  Step 3: Classify each of the items in {book_spec} except Genre into {range_values} and Genre into {genre_values} based on the following rules: \
  {delimiter}
  Genre: Frictional: < non-real or imaginary contents like Alice in Wonderland, Gullivers travel > , \n
  Non-Frictional: < Real life stories, biographies and auto-biographies > , \n
  Self Improvement: <Guides/Helps with improving the readers personalities, self care, health, financial situation> , \n
  Skill development: < Teaches/Trains readers on any particular technical or non-technical skills/hobbies > , \n
  Knowledge Expansion: < school and college students books, Reference books on any subjects, about nature and natural objects and phenomenon> ,\n

  User Reading phase: low: < Less than 50 pages, simple words, big fonts, contains many images, quick read> , \n
  medium: < More than 50 pages and less than 300 pages, medium size fonts with some images > , \n
  high: < More than 300 pages, small fonts with very few or no images, reference > \n

  User Maturity Level: low: < for children, easy to understand, no prior knowledge on subject requirements > , \n
  medium: < For teenagers and adults, straightforward explainations, suitable for non-working professionals as well, no complex terms and no prior knowledge on subject area > , \n
  high: < For adults, complex explainations, for working professionals, requires prior knowledged on the subject area> \n
  {delimiter}

  {delimiter}
  Here are some input output pairs for few-shot learning:
  input1: "Like a time bomb ticking away, hypertension builds quietly, gradually, placing unbearable strain on the body until it explodes--in heart attack, stroke, kidney failure, arterial disease, even death. But the disease does not have to progress that way. Here, in the third volume of the highly acclaimed Preventive Medicine Program, Dr. Kenneth H. Cooper, one of the nations foremost experts in the field of preventive medicine, presents a medically sound, reassuringly simple program that help you lower you blood pressure--and keep it down, often without drugs. Overcoming Hypertension gives you: --The latest facts on how cholesterol, cigarette smoking, obesity, and stress affect coronary risk levels. --Your high blood pressure risk profile, with newly devised charts for men and women. --A complete fitness program that lets you choose the sport that works for you. Plus a unique illustrated guide to aqua-aerobics. --Tips on talking to your doctor that will help you become an active participant in your own recovery. --A guide to anti-hypertensive drugs--the most up-to-date list of medications, their recommended daily doses, and ways to minimize side effects. --Three distinct dietary programs, complete with menus, recipes, nutritional charts, healthy cooking tips, and much more. --Take charge of your health and well-being with Overcoming Hypertension.."
  output1: {{'Genre':'Self Improvement', 'User Reading phase':'medium', 'User Maturity Level':'high'}}

  input2: "The classic children's story about a young boy, his toy castle, and a magical adventure that reveals the true meaning of courage When his beloved caretaker Mrs. Phillips tells him she's leaving, William is devastated. Not even her farewell gift of a model medieval castle helps him feel betterâ€”though he has to admit it's fascinating. From the working drawbridge and portcullis to the fully-furnished rooms, it's perfect in every detail. It almost seems magical. And when William looks at the silver knight, the tiny figure comes to life in his handâ€”and tells him a tale of a wicked sorcerer, a vicious dragon, and a kingdom in need of a hero. Hoping the castle's magic will help him find a way to make his friend stay, William embarks on a daring quest with Sir Simon, the Silver Knightâ€”but he will have to face his own doubts and regrets if he's going to succeed. William's story continues in The Battle for the Castle, available as a redesigned companion edition. An IRA-CBC Children's Choice A California Young Reader Medal Winner A Dorothy Canfield Fisher Children's Book Award Winner Nominated for 23 State Book Awards."
  output2: {{'Genre':'Frictional', 'User Reading phase':'medium', 'User Maturity Level':'low'}}

  input3: "The #1 introduction to J2SE 1.5 and enterprise/server-side development! An international bestseller for eight years, Just Javaâ„¢ 2 is the complete, accessible Java tutorial for working programmers at all levels. Fully updated and revised, this sixth edition is more than an engaging overview of Java 2 Standard Edition (J2SE 1.5) and its libraries: itâ€™s also a practical introduction to todayâ€™s best enterprise and server-side programming techniques. Just Javaâ„¢ 2, Sixth Edition, reflects both J2SE 1.5 and the latest Tomcat and servlet specifications. Extensive new coverage includes: New chapters on generics and enumerated types New coverage of Web services, with practical examples using Google and Amazon Web services Simplified interactive I/O with printf() Autoboxing and unboxing of primitive types Static imports, foreach loop construct, and other new language features Peter van der Linden delivers expert advice, clear explanations, and crisp sample programs throughoutâ€“including dozens new to this edition. Along the way, he introduces: The core language: syntax, objects, interfaces, nested classes, compiler secrets, and much more Key libraries: date and calendar, pattern matching, network software, mapped I/O, utilities and generic collections Server-side technology: network server systems, a complete tiny HTML Web server, and XML in Java Enterprise J2EE: Sql and JDBCâ„¢ tutorial, servlets and JSP and much more Client-side Java: fundamentals of JFC/Swing GUI development, new class data sharing details Companion Web Site All the bookâ€™s examples and sample programs are available at http://afu.com.."
  output3: {{'Genre':'Skill development', 'User Reading phase':'high', 'User Maturity Level':'high'}}
  {delimiter}

  Follow the above instructions step-by-step and output the dictionary {book_spec} for the following laptop {book_description}.
  """

#see that we are using the Completion endpoint and not the Chatcompletion endpoint

  response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt=prompt,
    max_tokens = 2000,
    # temperature=0.3,
    # top_p=0.4
    )
  return response["choices"][0]["text"]

if __name__ == "__main__":
    process()