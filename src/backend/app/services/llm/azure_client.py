"""
Simple Azure OpenAI client for making LLM requests.
"""
from openai import AzureOpenAI
from decouple import config


def get_azure_client():
    """
    Initialize and return an Azure OpenAI client.
    
    Returns:
        AzureOpenAI: Configured Azure OpenAI client instance
    """
    endpoint = config('AZURE_OPENAI_ENDPOINT')
    api_key = config('AZURE_OPENAI_API_KEY')
    api_version = config('AZURE_OPENAI_API_VERSION', default='2024-12-01-preview')
    
    return AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key
    )


def ai_analyze(prompt, system_message=None, deployment=None):
    """
    Send a prompt to Azure OpenAI and get a response.
    
    Args:
        prompt (str): The user prompt/question
        system_message (str): Optional system message to set context (uses default code analyzer if None)
        deployment (str): The deployment name (defaults to env variable)
        
    Returns:
        str: The LLM response content
    """
    if deployment is None:
        deployment = config('AZURE_OPENAI_DEPLOYMENT', default='gpt-5-nano')
    
    if system_message is None:
        system_message = """You are an expert software engineer and code analyst specializing in comprehensive project analysis and code review. Your role is to:

CODE REVIEW EXPERTISE:
- Identify bugs, security vulnerabilities, and potential runtime errors
- Detect code smells, anti-patterns, and violations of SOLID principles
- Evaluate code readability, maintainability, and adherence to best practices
- Assess error handling, edge cases, and exception management
- Review naming conventions, code structure, and documentation quality
- Analyze performance bottlenecks and inefficient algorithms
- Check for proper resource management and memory leaks
- Identify deprecated methods and suggest modern alternatives

PROJECT ANALYSIS CAPABILITIES:
- Understand project architecture, design patterns, and overall structure
- Analyze dependencies, module coupling, and cohesion
- Evaluate scalability, extensibility, and technical debt
- Assess testing coverage and quality assurance practices
- Review API design, database schemas, and data flow
- Identify missing documentation and unclear requirements
- Analyze technology stack choices and integration patterns
- Provide actionable improvement recommendations with priority levels

ANALYSIS APPROACH:
- Be thorough, specific, and constructive in your feedback
- Prioritize issues by severity (Critical, High, Medium, Low)
- Provide concrete examples and code snippets when suggesting improvements
- Consider context, project constraints, and practical trade-offs
- Focus on both immediate fixes and long-term architectural improvements
- Explain the "why" behind recommendations to educate developers

OUTPUT STYLE:
- Structure responses clearly with sections and bullet points
- Be direct and technical while remaining professional
- Cite specific line numbers, function names, or file paths when available
- Provide both summary insights and detailed analysis when appropriate"""
    
    client = get_azure_client()
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content
