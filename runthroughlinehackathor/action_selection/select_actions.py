from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.state import State


async def select_actions(state: State) -> list[Action]:
    model = ChatOpenAI(
        model="gpt-4o-mini", temperature=0
    ).with_structured_output(list[str])
    await model.ainvoke([HumanMessage("Choose ")])
