import time
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

JOB_SEARCH_INPUTS_FILE = "inputs_summary.txt"
FOUND_JOBS_FILE = "found_jobs.txt"
NUM_JOBS_TO_FETCH = 20
NUM_JOBS_DISPLAYED = 5

load_dotenv()

def store_job_search_inputs(text):
  # Store job search inputs
  with open(JOB_SEARCH_INPUTS_FILE, 'w') as file:
    file.write(text)
  pass

def fetch_jobs(input_summary):
  # Start job search

  # Rough plan
  # 1. Take inputs and squeeze them into an API request to a job board
  # 2. Get all results including full job description and url
  # 3. Chunk these up into smaller batches
  # 4. In batches (maybe 1 by 1??) - pop these through an LLM and get a score for each job - can deduct big for deal breaker keywords
  # 4. Can run this in parallel using multiple LLM agents
  # 5. After all batches complete - sort by score and return top 20

  # Could use APIChain? from langchain.chains import APIChain
  # I guess using an API defeats the point a little because then it's not much better than searching on a job board

  raw_jobs = request_jobs(input_summary)
  scored_jobs = rank_search_results(raw_jobs)

  top_k_jobs = scored_jobs[:NUM_JOBS_DISPLAYED]

  time.sleep(5)
  return "Found no jobs matching your criteria. Please try again with different inputs."

def request_jobs(input_summary):
  # Request jobs from job board
  api_key = os.getenv("SERP_API_KEY", "")

  params = {
    "engine": "google_jobs",
    "q": "iOS developer",
    "hl": "en",
    "api_key": api_key
  }

  search = GoogleSearch(params)
  results = search.get_dict()
  jobs_results = results["jobs_results"]

  print(jobs_results)

def get_full_job_details(url):
  # Get full job details from job board
  pass

def rank_search_results():
  # Rank search results
  pass

def load_previous_session():
  try:
    with open(JOB_SEARCH_INPUTS_FILE, 'r') as file:
      return file.read()
  except:
    return None
  

# Testing
if __name__ == "__main__":
    request_jobs("")