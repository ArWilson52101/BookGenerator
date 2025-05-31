import requests
from fpdf import FPDF
import re
import sys
from fpdf.enums import XPos, YPos
import os
from fpdf.errors import FPDFException
# ======== Configuration ========
API_KEY = "Bearer key"  # ← Replace with your OpenRouter key
MODEL = "deepseek/deepseek-r1-0528:free"       # ← Or another free/paid model you have access to. I would reccomend only free ones because the program isnt 100% consistent.
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

#===========Functioning Test===========
def FunctionTest(): #just a function to test fpdf before waiting hours only for it to fail (ask me how i know!)
    print("Testing fpdf")
    pdf=FPDF()
    pdf.compress=False
    pdf.add_page()
    pdf.add_font('DejaVuSans', '', 'DejaVuSans.ttf')
    pdf.set_font("DejaVuSans",'',10)
    pdf.ln(10) #line break of 10 height before any writing
    pdf.write(5, 'hello world')
    
    pdf.output('fpdftest.pdf')
    print("Test passed \n")
# ======== Chat Function ======== #function to send prompts to a LLM using openrouter. couldnt do this without it.
def chat_with_openrouter(prompt, model=MODEL):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(API_URL, headers=HEADERS, json=body)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("STATUS CODE:", response.status_code)
        print("RESPONSE JSON:", response.json())
        return None

# ======== Generation Functions ========
#These functions generate the title, genre, chapter outlines, and chapters using a LLM prompt input.
def generate_title_and_genre():
    prompt = (
        "Create an original book title and a matching genre. "
        "Return it in this format exactly: Title: [title] | Genre: [genre]"
        "Do not include any asterisks or explanations of the name/genre."
        
    )
    return chat_with_openrouter(prompt)

def generate_outline(title, genre):
    prompt = (
       f"Generate 15-25 related chapter names for a {genre} novel titled '{title}'. use only standard ASCII characters and do not bolden or italicize names/chapters. do not mention the use of standard ASCII characters. Do not include any text after the chapter names."
        "Only use digits for the chapter numbering. it should go Chapter 1: abcdefg Chapter 2: hijklmn Chatper 3:... and so on"
        "Generate an outline for each chapter seperated from the chapter name by a | for example Chapter 1: abc | James discovers the plot point of the book \n"
        "Ensure that the outline shows a clear plot starting with an exposition, then rising action, ending with a climax, falling action and resolution."
        )
    return chat_with_openrouter(prompt)

def generate_chapter(title, genre, chapter_summary):
    prompt = (
        
        
        f"Write a full chapter of a {genre} novel titled {title}. Base it on the following outline: \n {chapter_summary} \n use only standard ASCII characters and do not bolden or italicize names/chapters. Do not use en dashes or em dashes. Ensure all text output is rendered using only characters that exist in the Helvetica font. Restrict Unicode usage to the range U+0001 to U+0256 (Basic Latin to Latin Extended-A). No smart quotes, special dashes, or non-ASCII punctuation. do not mention the use of standard ASCII characters. Make it 750-1500 words per chapter and immersive and follow a continuity. " 
        f"If the book has the same title as a title mentioend before, assume it is the same book. dont mention this assumption. just write the chapter as if it is a continuation of the last chapter you wrote."
        f"Everything after the | in the outline is the outline of the chapter. "
         "Do NOT include any asterisks in the chapter text."
    )
    return chat_with_openrouter(prompt)
#=========================================#

    
if __name__ == "__main__":
    FunctionTest() #Tests fpdf before running to avoid any issues after waiting forever.

 
    print("Generating title + genre \n")
    parts = generate_title_and_genre().split('|')#Generates the title and genre and splits them at the |
    print(parts[0],parts[1],"\n\n")

    print("Printing outline")

    booktitle = parts[0].split(" ") # splits the book title by whitespaces
    splittitle=booktitle[1:-1] #final title variable stripped of unnecessary chars
    filename=(''.join(splittitle)+".pdf") #creates a filename for saving the book
    genre=parts[1].split(" ")#same as the title stuff. splits and strips.
    splitgenre=genre[2:]#final genre variable stripped of unncessary chars
    
    newoutline=generate_outline(splittitle,splitgenre)#Generates a multi-chapter outline for the newly splitted title and genre

    print(newoutline,"\n")
    splitoutline=newoutline.splitlines() #splits each outline by line to easily seperate chapters
    chapters=[] #chapters list. holds text for each chapter.

    for x in splitoutline:
    #for loop to generate chapters for each outline
        print("Generating chapter",x)
        chapters.append(generate_chapter(splittitle,splitgenre,x))
    print(f"Generation complete, enjoy your book at {filename}!")

    #fpdf exporting nonsense.
    book=FPDF()
    book.compress=False
    book.add_page()
    book.add_font('DejaVuSans', '', 'DejaVuSans.ttf')
    book.set_font("DejaVuSans",'',10)
    book.ln(1)
    for x in chapters:
        book.multi_cell(0,10,x)
        book.ln()
        book.add_page()
    book.output(filename)
    
