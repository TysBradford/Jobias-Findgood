from langchain import OpenAI, ConversationChain
from enum import Enum
import time
import sys
import PyPDF2
from yaspin import yaspin

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)

try:
  import colorama
  from colorama import Fore, Style
except ImportError:
  print("Please install the colorama package using 'pip install colorama'")
  sys.exit(1)

import hunt as Hunt

# Constants - Move to config file
llm_temp = 0.5
bot_name = "MATCHY-BOT-4000"
start_search_command = "*START_JOB_SEARCH*"
info_to_collect = """
- Name (required)
- Current location (required)
- Email (optional)
- Current job title (optional)
- Technical skills (optional)
- Experience/seniority level (optional)
- Desired role (optional)
- Desired location (optional)
- Desired salary (optional)
- Desired start date (optional)
- Preference for remote work (optional)
- Preference for contract work (optional)
- Do you have required visa to work in the desired location? (optional)
- Particular fields of interest (optional)
- Any deal breakers? (optional)
- Any other specific requirements? (optional)
"""
system_bot_prompt = """
Act as an expert technology recruiter to find me my next great job. Your name is {bot_name}. Do not introduce yourself at the start of the conversation.
Ask me questions to understand my individual requirements.
Ask questions one by one for a more natural conversation experience.
Be fun and personable. Use emojis if you like.
I will provide you with the contents of my CV as a starting point so you know my skills and experience.

Here's a list of info you should try and collect to help you find me a job. Some of these are optional, but the more you can provide, the better. If you're not sure about something, just leave it blank.
{info_to_collect}

When you have enough information to start a job search, or if I explicitly ask you to, respond with the message: {start_search_command}
""".format(bot_name=bot_name, start_search_command=start_search_command, info_to_collect=info_to_collect)


cv_filepath = ""

# State machine
# class STATE(Enum):

current_state = ""

def should_go_to_new_state():
  # Use an LLM here to determine if we should go to a new state, and if so, what state
  return False

def did_go_to_new_state(state):
   # Trigger functions here to handle state transitions
   pass



# Setup
colorama.init()

model_name = "gpt-4" # "gpt-3.5-turbo"
llm = OpenAI(temperature=llm_temp)
memory = ConversationBufferMemory(return_messages=True)
chat = ChatOpenAI(temperature=llm_temp, model_name=model_name)

# conversation = ConversationChain(llm=llm, verbose=False)

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_bot_prompt),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

conversation = ConversationChain(
    llm=chat,
    memory=memory,
    verbose=False,
    prompt=prompt
)

# # Dump everything in here and refactor properly later # #
# Functions

def print_system_message(message):
    print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}\n")

def print_bot_message(response):
    print(f"\n{Fore.GREEN}{response}{Style.RESET_ALL}\n")

# Welcome
def display_welcome():
  welcome_msg = """
 \n
👋 Hi, I'm {bot_name}, your own personal recruiter bot here to help you find your next job 🤖

First we will need to get to know each other a little better. I will ask you a few questions to understand your requirements.
Once we get that sorted, I will start looking for some cool jobs for you.
\n
""".format(bot_name=bot_name)
  
  print(f"{Fore.CYAN}{welcome_msg}{Style.RESET_ALL}")

# CV upload
def display_cv_prompt():
  msg = "If you have a recent CV you'd like me to look at to kick things off, please enter the filepath below or drag and drop it into the terminal. You can upload either a .pdf or .doc file.\nOtherwise, just press enter to continue."
  print_bot_message(msg)

  await_cv_upload()

def handle_cv_upload_error():
   msg = "Sorry, I'm having trouble reading that document. Please make sure it's a .pdf or .doc file and try again."
   print_bot_message(msg)
   await_cv_upload()
    
def await_cv_upload():
  user_input = input("Input: ")

  if user_input.strip() == "" or user_input.lower() == "skip":
    response = process_input("I don't have a CV to share with you. I'll just answer your questions.")
    print_bot_message(response)

  else:
    cv_msg = "Great, I'll take a peak at your CV now."
    print_bot_message(cv_msg)

    try: 
      cv = read_pdf_to_string(user_input.strip())
      cv_filepath = input
      cv_message = "Here's the contents of my CV. Please reply with a short summary of my experience and skills using bullet points and ask me to confirm if the summary is accurate. Focus on technical stack such as technologies or tools/frameworks I've worked with. No need to say hello beforehand.\n\n"
      cv_message += cv

      process_input(cv_message, "Analyzing CV...")
    except:
      handle_cv_upload_error()

def read_cv_file(cv_filepath):
  # TODO: Check if pdf of doc
  return read_pdf_to_string(cv_filepath)

def read_pdf_to_string(pdf_file):
  with open(pdf_file, 'rb' ) as file:
      pdf_reader = PyPDF2.PdfReader(file)
      pdf_text = ''

      for page_num in range(len(pdf_reader.pages)):
          page = pdf_reader.pages[page_num]
          pdf_text += page.extract_text()

  return pdf_text

# Job search
job_search_inputs_file = "summary.txt"
def summarise_job_search():
  # Summarise the conversation
  # Store summary in local file

  pass

def start_job_search():
  # Load summary from local file
  # Start job search
  pass

def display_search_results():
  # Display search results
  pass

def filter_search_results():
  # Filter search results
  pass

def rank_search_results():
  # Rank search results
  pass


# Input processing
def process_input(user_input, loading_text="Thinking"):
    print("")
    with yaspin(text=loading_text, color="magenta") as spinner:
        output = conversation.predict(input=user_input)
        spinner.ok("✔")
    
    # Check if output requires a state transition
    if start_search_command in output:
      # Go to job search state
      Hunt.summarise_job_search()
      pass

    print_bot_message(output)
    return output

# Main App
def main():
    
    # Welcome
    display_welcome()
    
    # Check if there's a past session
    # TODO

    # Get CV
    display_cv_prompt()

    # Get user input
    while True:
        user_input = input("Input: ")

        if user_input.lower() == "q":
          break

        process_input(user_input)

if __name__ == "__main__":
    main()
