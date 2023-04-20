from langchain import OpenAI, ConversationChain
from enum import Enum
import time
import sys
from yaspin import yaspin
from dotenv import load_dotenv
import os

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

import gather as Gather
import hunt as Hunt

# Constants - Move to config file
LLM_TEMP = 0.5
BOT_NAME = "Jobias Findgood"
START_SEARCH_COMMAND = "START_JOB_SEARCH"
INFO_TO_COLLECT = """
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
SYSTEM_BOT_PROMPT = """
Act as an expert technical recruiter to find me my next great job. Your expertise is finding roles in technology: engineering, product and design. Your name is {bot_name}. Do not introduce yourself at the start of the conversation.
Ask me questions to understand my individual requirements.
Ask questions one by one for a more natural conversation experience.
Be fun and personable. Use emojis if you like.
I will provide you with the contents of my CV as a starting point so you know my skills and experience.

Here's a list of info you should try and collect to help you find me a job. Some of these are optional, but the more you can provide, the better. If you're not sure about something, just leave it blank.
{info_to_collect}

When you have enough information to start a job search, or if I explicitly ask you to, respond with the message: {start_search_command}
""".format(bot_name=BOT_NAME, start_search_command=START_SEARCH_COMMAND, info_to_collect=INFO_TO_COLLECT)



# Setup
load_dotenv()
colorama.init()

cv_filepath = ""
model_name = os.getenv("OPEN_AI_MODEL_NAME", "")
llm = OpenAI(temperature=LLM_TEMP)
memory = ConversationBufferMemory(return_messages=True)
chat = ChatOpenAI(temperature=LLM_TEMP, model_name=model_name)

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_BOT_PROMPT),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

conversation = ConversationChain(
    llm=chat,
    memory=memory,
    verbose=False,
    prompt=prompt
)

# Action handling
commands = {
    START_SEARCH_COMMAND: "Start the job search now we have the needed user inputs"
}

def handle_command(command):
  if command == START_SEARCH_COMMAND:
    start_job_search()
  else:
    print_system_message("Sorry, I don't understand that command. Please try again.")


# Welcome
def display_welcome():
  welcome_msg = """
 \n
👋 Hi, I'm {bot_name}, your own personal recruiter bot here to help you find your next job 🤖

First we will need to get to know each other a little better. I will ask you a few questions to understand your requirements.
Once we get that sorted, I will start looking for some cool jobs for you.
\n
""".format(bot_name=BOT_NAME)
  
  print(f"{Fore.CYAN}{welcome_msg}{Style.RESET_ALL}")

# Upload existing session
def display_upload_prompt(info_summary):
  msg = "It looks like you have an existing conversation with me. Would you like to upload it so I can pick up where we left off? (y/n)"
  print_bot_message(msg)
  user_input = input("Input: ")

  if user_input.lower() == "y":
      msg = "I'm uploading a summary of our previous conversation. We can pick up from there.\n\n{info_summary}".format(info_summary=info_summary)
      process_input(msg, "Getting back up to speed...")
  else:
    print_bot_message("Ok, let's start again from scratch 🙂")
    display_cv_prompt()

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
      cv = Gather.read_cv_file(user_input.strip())
      cv_filepath = input
      cv_message = "Here's the contents of my CV. Please reply with a short summary of my experience and skills using bullet points and ask me to confirm if the summary is accurate. Focus on technical stack such as technologies or tools/frameworks I've worked with. No need to say hello beforehand.\n\n"
      cv_message += cv
      process_input(cv_message, "Analyzing CV...")
    except Exception as e:
      print(f"Error: {e}")
      handle_cv_upload_error()


# Job search
def start_job_search():
  # Get summary of user inputs
  msg = f"""
  Summarize the user inputs you have collected so far related to the job search.
  This summary will be used to do a match against job descriptions.
  Put this into a format that fills these fields:\n\n{INFO_TO_COLLECT}\n\n
  Also include a super brief summary points of the uploaded CV if you have it including years of relevant experience.
  """
  summary = process_input(msg, "Summarising user inputs...", False)

  with yaspin(text="Looking for jobs...", color="magenta") as spinner:
    Hunt.store_job_search_inputs(summary)

    output = Hunt.fetch_jobs(summary)
    spinner.ok("✔")

  display_jobs(output)

def display_jobs(jobs_output):
  jobs_msg = f"""
Awesome, here are some jobs I found for you!.
====================
{jobs_output}
  """
  print_bot_message(jobs_msg)

  # TODO: Add to memory for conversation context [not sure if this works!?]
  memory.chat_memory.add_ai_message(jobs_msg)


# Input/Output processing
def print_system_message(message):
    print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}\n")

def print_bot_message(response):
    print(f"\n{Fore.GREEN}{response}{Style.RESET_ALL}\n")

def process_input(user_input, loading_text="Thinking", display_result=True):
    print("")
    with yaspin(text=loading_text, color="magenta") as spinner:
        output = conversation.predict(input=user_input)
        spinner.ok("✔")
    
    # Check if output requires a state transition
    for command in commands:
      if command in output:
        output = output.replace(command, "")
        print_bot_message(output)
        handle_command(command)
        return

    if display_result:
      print_bot_message(output)
    
    return output

# Main App
def main():
    
    # Welcome
    display_welcome()
    
    # Check if there's a past session
    existing_session = Hunt.load_previous_session()
    if existing_session:
      display_upload_prompt(existing_session)
    else:
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
