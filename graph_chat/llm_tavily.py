import os
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI

os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

# llm = ChatOpenAI(
#     model='gpt-4.1-mini-2025-04-14',
#     base_url="https://api.openai.com/v1",
#     temperature=0,
# )
api_key = os.getenv('GLM_API_KEY')

llm = ChatOpenAI(
    model='glm-4-0520',
    api_key=api_key,
    base_url='https://open.bigmodel.cn/api/paas/v4/',
    temperature=0.6
)

tavily_tool = TavilySearchResults(max_results=1)