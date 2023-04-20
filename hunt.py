import time
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv
from langchain.llms import OpenAI
import concurrent.futures


JOB_SEARCH_INPUTS_FILE = "inputs_summary.txt"
FOUND_JOBS_FILE = "found_jobs.txt"
NUM_JOBS_TO_FETCH = 20 # Going too high here will start costing token 🤑
NUM_JOBS_DISPLAYED = 10

MATCH_SCORE = "<score>"
JOB_OUTPUT_FORMAT = f"""
Job: <title>
Company: <company> - <what_company_does>
Location: <location>
URL: <company_url>
Why is this a match?: 
  -<reason1>
  -<reason2>
  ...
Any concerns?:
  -<concern1>
  -<concern2>
  ...
Match score: {MATCH_SCORE}/10
"""

load_dotenv()

def store_job_search_inputs(text):
  # Store job search inputs
  with open(JOB_SEARCH_INPUTS_FILE, 'w') as file:
    file.write(text)
  pass
 

def fetch_jobs(input_summary):
  # Start job search

  raw_jobs = request_jobs(input_summary) # This is an array of job infos from the job board

  scored_jobs = []
  with concurrent.futures.ProcessPoolExecutor() as executor:
    # Map the parallel_score function to the raw_jobs list and retrieve the results
    scored_jobs = list(executor.map(score_search_results, raw_jobs, [input_summary] * len(raw_jobs)))

  top_k_jobs = scored_jobs[:NUM_JOBS_DISPLAYED]
  #ranked_jobs = rank_jobs(top_k_jobs)
  #print(ranked_jobs)

  ranked_jobs_string = '\n\n'.join(top_k_jobs)
  # print(ranked_jobs_string)
  return ranked_jobs_string

def request_jobs(input_summary):
  # Request jobs from job board
  api_key = os.getenv("SERP_API_KEY", "")
  query = get_job_query(input_summary)
  location = ""

  params = {
    "engine": "google_jobs",
    "q": query,
    "hl": "en",
    "location": location,
    "api_key": api_key,
    "start": 0,
  }

# TODO: Run multiple requests in parallel to match NUM_JOBS_TO_FETCH + concatenate results
  search = GoogleSearch(params)
  results = search.get_dict() # Get's first 10 results - use pagination to get more
  jobs_results = results["jobs_results"]
  return clean_fetch_results(jobs_results)

def clean_fetch_results(raw_jobs):
  # Clean up job results - remove unwanted fields etc. This will help the model reason and also reduce token usage
  for job in raw_jobs:
    job.pop("job_id", None)
    job.pop("detected_extensions", None)
    job.pop("via", None)
    if len(job['related_links']) > 1:
      job['related_links'].pop(1)
  return raw_jobs

def get_job_query(input_summary):
  prompt = f"""
  Take an input which is a summary of a job candidates skills, experience and job preferences and return a search query string to be used for a job search.
  The query should be a single string containing ONLY 'job title' and 'location'.
  Example outputs are: 'iOS engineer, London UK' and 'senior product manager, New York US'.
  Only return the query string in your response.

  The input summary is:
  {input_summary}
  """

  llm = OpenAI(temperature=0.0)
  query_string = llm(prompt)
  return query_string.strip()

def score_search_results(job_info, input_summary):
  prompt = f"""
  Take two inputs: a job description and a job candidate summary.
  The job description is a JSON blob containing various details about the job.
  Use the two inputs to return a score between 0 and 10 indicating how good the job matche is for me (the candidate).
  A score of 0 would mean a horrible match. A score of 10 would be the best possible match.
  When scoring, pay close attention to the job title, location, salary, job type, job description, past experience and skills, and any other relevant details.
  As well as providing a matching score, you should also return a brief summary of the job and a very brief bullet-point list as to why you think the job is a particularly good match for me personally.
  When describing why the match, refer to the candidate as 'you' and highlight any benefits from the candidates perspective but also mention any concerns or drawbacks from the candidates perspective.
  The output should have the following format:
  {JOB_OUTPUT_FORMAT}

  The job description is:
  {job_info}

  The job candidate summary is:
  {input_summary}
  """
  model_name = os.getenv("OPEN_AI_MODEL_NAME", "")
  llm = OpenAI(temperature=0.0)
  score = llm(prompt)
  return score.strip()

def rank_jobs(jobs_info):
  # Rank search results
  prompt = """
  Take an input of job opportunities which are scored based on candidate match.
  Return this list but sort it by score from highest to lowest.
  Return only the sorted job opportunities in your response.
  """

  llm = OpenAI(temperature=0.0)
  sorted_jobs = llm(prompt)
  return sorted_jobs.strip()


def load_previous_session():
  try:
    with open(JOB_SEARCH_INPUTS_FILE, 'r') as file:
      return file.read()
  except:
    return None
  

# Testing
if __name__ == "__main__":
  input_summary = load_previous_session()
  fetch_jobs(input_summary)