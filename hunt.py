import time
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv
from langchain.llms import OpenAI


JOB_SEARCH_INPUTS_FILE = "inputs_summary.txt"
FOUND_JOBS_FILE = "found_jobs.txt"
NUM_JOBS_TO_FETCH = 20
NUM_JOBS_DISPLAYED = 5

MATCH_SCORE = "<score>"
JOB_OUTPUT_FORMAT = f"""
Match score: {MATCH_SCORE}
Job title and company: <title> - <company>
Location: <location>
URL: <job_details_url>
Why you should apply?: <why_you_should_apply>
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
  for job_info in raw_jobs:
    scored_job = score_search_results(job_info, input_summary)
    print(scored_job)
    scored_jobs.append(scored_job)

  #top_k_jobs = scored_jobs[:NUM_JOBS_DISPLAYED]
  #ranked_jobs = rank_jobs(scored_jobs)

  return scored_jobs

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
    "api_key": api_key
  }

  print(f"searching with params: {params}")

# TODO: Run multiple requests in parallel to match NUM_JOBS_TO_FETCH + concatenate results
  search = GoogleSearch(params)
  results = search.get_dict() # Get's first 10 results - use pagination to get more
  jobs_results = results["jobs_results"]

  print(f"found {len(jobs_results)} jobs")

def get_job_query(input_summary):
  prompt = f"""
  Take an input which is a summary of a job candidates skills, experience and job preferences and return a search query string to be used for a job search.
  The query should be a single string containing ONLY 'job title', 'location' and optionally 1-2 domain keywords.
  Example outputs are: 'iOS engineer, London UK, AI' and 'senior product manager, New York US, health'.
  Only return the query string in your response.

  The input summary is:
  {input_summary}
  """

  llm = OpenAI(temperature=0.0)
  query_string = llm(prompt)
  return query_string.strip()
  

def get_full_job_details(url):
  # Get full job details from job board
  pass


def score_search_results(job_info, input_summary):
  prompt = f"""
  Take two inputs: a job description and a job candidate summary.
  The job description is a JSON blob containing various details about the job.
  Use the two inputs to return a score between 0 and 10 indicating how well the job matches the job candidate.
  Pay close attention to the job title, location, salary, job type, job description and any other relevant details.
  As well as providing a matching score, you should also return a short summary of the job and a brief reasoning as to why you think the job is a good match for the job candidate.
  The output should have the following format:
  {JOB_OUTPUT_FORMAT}

  The job description is: {job_info}

  The job candidate summary is: {input_summary}
  """

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