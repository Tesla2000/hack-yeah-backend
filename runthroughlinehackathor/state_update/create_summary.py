from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.settings import settings


async def create_summary(current_state: State):
    response = await ChatOpenAI(
        name="gpt-4o-mini",
        api_key=settings.openai_api_key,
    ).ainvoke([HumanMessage("Summarize ")])
    response.content
