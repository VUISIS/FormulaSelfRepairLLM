
from langchain.agents.agent_toolkits import create_python_agent
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from langchain.embeddings.openai import OpenAIEmbeddings
import json
from langchain.chains import ConversationalRetrievalChain
from langchain.agents.agent import AgentExecutor, BaseSingleActionAgent
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.agents.types import AgentType
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.schema.language_model import BaseLanguageModel
from langchain.schema.messages import SystemMessage
from langchain.tools.python.tool import PythonREPLTool
from langchain.memory import ConversationBufferMemory
from formula_tools import LoadFormulaCode, QueryFormulaCode, DecodeFormulaCodeLLM
from config import cfg
from prompts import FIX_CODE_PREFIX

os.environ["OPENAI_API_KEY"] = cfg["OPENAI_API_KEY"]

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "http://localhost:1984"



# chat = ChatOpenAI(temperature=0.0)
llm = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0)
embeddings = OpenAIEmbeddings()



system_message = SystemMessage(content=FIX_CODE_PREFIX)
_prompt = OpenAIFunctionsAgent.create_prompt(system_message=system_message)
memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

tools = [LoadFormulaCode(), QueryFormulaCode(), DecodeFormulaCodeLLM(llm=llm, memory=memory)]

agent = OpenAIFunctionsAgent(
    llm=llm,
    prompt=_prompt,
    tools=tools,
    memory=memory,
    verbose=True
    )

agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
    )

sample_query = """\

Can you explain why the following code delimited in ``` is not solvable?
Could you then try to fix the code?

Here is the code:
```
domain Mapping
{
  Component ::= new (id: Integer, utilization: Real).
  Processor ::= new (id: Integer).
  Mapping   ::= new (c: Component, p: Processor).

  // The utilization must be > 0
  invalidUtilization1 :- c is Component, c.utilization <= 0.
  invalidUtilization2 :- c is Component, c.utilization > 0.

  badMapping :- p is Processor,
    s = sum(0.0, { c.utilization |
              c is Component, Mapping(c, p) }), s > 100.

  conforms no badMapping, no invalidUtilization1, no invalidUtilization2.
}

partial model pm of Mapping
{
  c1 is Component(0, x).
  c2 is Component(1, y).
  p1 is Processor(0).
  Mapping(c1, p1).
  Mapping(c2, p1).
}
```

And here is what the FORMULA interpreter says:

```
[]> solve pm 1 Mapping.conforms
Parsing text took: 1
Visiting text took: 0
Started solve task with Id 0.
0.06s.
[]> ls

Environment variables

Programs in file root
 +-- /
 | tmp_file.4ml

Programs in env root
 +-- /

All tasks
 Id | Kind  | Status | Result |      Started      | Duration
----|-------|--------|--------|-------------------|----------
 0  | Solve |  Done  | false  | 7/14/2023 3:44 PM |  0.28s
0.02s.
[]> ex 0 1 out.4ml
Model not solvable. Unsat core terms below.
Conflicts: Mapping.invalidUtilization2
Conflicts: Mapping.invalidUtilization1

0.01s.
```

"""

agent_executor.run(sample_query)