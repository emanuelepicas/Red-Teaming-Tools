import os
from smolagents import CodeAgent,DuckDuckGoSearchTool, HfApiModel,load_tool,tool, LiteLLMModel
import datetime
import requests
import pytz
import yaml
import ollama
from tools.final_answer import FinalAnswerTool
from smolagents.models import OpenAIServerModel
from tools.launch_remote_console import launch_command_injection_console
from tools.command_injection_check import check_command_injection_via_useragent

from Gradio_UI import GradioUI

# Define a custom model class for Ollama
class OllamaModel:
    def __init__(self, model_name):
        self.model_name = model_name

    def __call__(self, prompt, stop_sequences=["Task"]) -> str:
        # Convert the list of prompts to a single string
        prompt_text = ""
        for item in prompt:
            if item['role'] == 'system':
                for content in item['content']:
                    if content['type'] == 'text':
                        prompt_text += content['text']
            elif item['role'] == 'user':
                for content in item['content']:
                    if content['type'] == 'text':
                        prompt_text += content['text']
        # Use Ollama's generate or chat API to handle prompts
        response = ollama.chat(model=self.model_name, messages=[{"role": "user", "content": prompt_text}], stream=False)
        return response.message

# Below is an example of a tool that does nothing. Amaze us with your creativity !
@tool
def my_cutom_tool(arg1:str, arg2:int)-> str: #it's import to specify the return type
    #Keep this format for the description / args / args description but feel free to modify the tool
    """A tool that does nothing yet 
    Args:
        arg1: the first argument
        arg2: the second argument
    """
    return "What magic will you build ?"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"

@tool
def analyze_domain_security(domain: str) -> str:
    """
    A tool that analyzes the cybersecurity posture of a given domain, specifically some headers.
    
    It performs a GET request to the domain and inspects the HTTP response for:
      - Status Code
      - Common security headers (Content-Security-Policy, Strict-Transport-Security, 
        X-Frame-Options, X-XSS-Protection, X-Content-Type-Options)
    
    Args:
        domain: The URL of the domain to analyze (e.g., "https://emanuelepicariello.com").
    """
    try:
        response = requests.get(domain, timeout=10)
        analysis = f"Cybersecurity Analysis for {domain}:\n"
        analysis += f"Status Code: {response.status_code}\n"
        headers = response.headers

        # Define the security headers to check
        security_headers = {
            "Content-Security-Policy": "Missing",
            "Strict-Transport-Security": "Missing",
            "X-Frame-Options": "Missing",
            "X-XSS-Protection": "Missing",
            "X-Content-Type-Options": "Missing"
        }

        # Check if each header is present in the response
        for header in security_headers:
            if header in headers:
                security_headers[header] = headers[header]

        analysis += "Security Headers:\n"
        for header, value in security_headers.items():
            analysis += f"  {header}: {value}\n"
            
        return analysis
    except Exception as e:
        return f"Error analyzing domain {domain}: {str(e)}"


final_answer = FinalAnswerTool()
"""model = HfApiModel(
max_tokens=2096,
temperature=0.5,
model_id='Qwen/Qwen2.5-Coder-32B-Instruct',  #Qwen/Qwen2.5-Coder-32B-Instruct', #https://wxknx1kg971u7k1n.us-east-1.aws.endpoints.huggingface.cloud',# it is possible that this model may be overloaded
custom_role_conversions=None,
)"""
model = OllamaModel(model_name="qwen2.5:14b")



# Import tool from Hub
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[final_answer, analyze_domain_security, check_command_injection_via_useragent, launch_command_injection_console],
    max_steps=3,
    verbosity_level=2,
    grammar=None,
    planning_interval=None,
    name="Red Team Agent",
    description="Specialized security testing agent for vulnerability assessment and command injection",
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()