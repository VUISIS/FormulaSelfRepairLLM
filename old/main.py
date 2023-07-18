from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import DeepLake
import os
from langchain.embeddings.openai import OpenAIEmbeddings
import json
from langchain.chains import ConversationalRetrievalChain


dataset_path = "hub://agarg/formula_manual"
os.environ["OPENAI_API_KEY"] = ''
os.environ['ACTIVELOOP_TOKEN'] = ""

# chat = ChatOpenAI(temperature=0.0)
chat = ChatOpenAI()
embeddings = OpenAIEmbeddings()

db = DeepLake(
    dataset_path=dataset_path,
    read_only=True,
    embedding_function=embeddings,
)
# data = [
#     {
#         "instruction": "What is the solution to this model?",
#         "input": "domain Chewy { Shy ::= new (w: Integer, Right: Integer). Piquant ::= (w: Integer, Right: Integer). Livid ::= (Integer, Integer). Livid(w, Right) :- Shy(w, Right), c = count({ t | t is Piquant, t.w <= t.Right}), c > -31. Piquant(w, Right) :- Shy(w, Right). Piquant(Right, w) :- Piquant(w, Right), w > Right. conforms Livid(a, b). } partial model plasticWrap of Chewy { Shy(a, b). }, Shy(0, 0), Piquant(0, 0), Livid(0, 0)",
#         "output": "This model is solvable because of the conformity of the following rules [Livid(a, b)].\nA solution exists for these constraints:\n\nLivid(w, Right) -> [Shy(w, Right), c = count({ t | t is Piquant, t.w <= t.Right}), c > -31]\nPiquant(w, Right) -> [Shy(w, Right)]\nPiquant(Right, w) -> [Piquant(w, Right), w > Right]\n",
#     },
#     {
#         "instruction": "Given a formula file, why is it solvable?",
#         "input": "domain Sparse { Knurled ::= new (w: Integer, Antique: Integer). Smoky ::= (w: Integer, Antique: Integer). emeraldTabby ::= (Integer, Integer). emeraldTabby(w, Antique) :- Knurled(w, Antique), c = count({ t | t is Smoky, t.w <= t.Antique}), c <= 10. Smoky(w, Antique) :- Knurled(w, Antique). Smoky(Antique, w) :- Smoky(w, Antique), w > Antique. conforms emeraldTabby(a, b). } partial model Binding of Sparse { Knurled(a, b). }, Knurled(0, 0), Smoky(0, 0), emeraldTabby(0, 0)",
#         "output": "This model is solvable because of the conformity of the following rules [emeraldTabby(a, b)].\nA solution exists for these constraints:\n\nemeraldTabby(w, Antique) -> [Knurled(w, Antique), c = count({ t | t is Smoky, t.w <= t.Antique}), c <= 10]\nSmoky(w, Antique) -> [Knurled(w, Antique)]\nSmoky(Antique, w) -> [Smoky(w, Antique), w > Antique]\n",
#     },
# ]

# read in data from file training.json
# with open('training.json') as f:
#     data = json.load(f)


template_string = """ \
We are creating a chatbot to assist in coding with FORMULA, \
which is a microsoft made programming language for Formal Specifications for Verification \
and Synthesis which is modeled after the programming language Prolog. \
Given the following FORMULA code (which is delimited in triple backticks) can you please explain {solvable}? \
FORMULA CODE: ```{code}```
"""

# prompt_template = ChatPromptTemplate.from_template(template_string)
# # fill in solvable with the word solvable and code with the code

# for every data point, generate a prompt and add it to the list of prompts
prompts = []
correct_outputs = []
prompt_template = ChatPromptTemplate.from_template(template_string)

# for d in data:
#     prompt = prompt_template.format_messages(
#         solvable=d["instruction"],
#         code=d["input"],
#     )[0]
#     prompts.append(prompt)
#     correct_outputs.append(d["output"])

retriever = db.as_retriever()
# retriever.search_kwargs["distance_metric"] = "cos"
# retriever.search_kwargs["fetch_k"] = 20
# retriever.search_kwargs["maximal_marginal_relevance"] = True
# retriever.search_kwargs["k"] = 20

qa = ConversationalRetrievalChain.from_llm(chat, retriever=retriever)

print(qa({"question" : """\
Can you please explain why this model is solvable? \
domain Sparse { Knurled ::= new (w: Integer, Antique: Integer). Smoky ::= (w: Integer, Antique: Integer). emeraldTabby ::= (Integer, Integer). emeraldTabby(w, Antique) :- Knurled(w, Antique), c = count({ t | t is Smoky, t.w <= t.Antique}), c <= 10. Smoky(w, Antique) :- Knurled(w, Antique). Smoky(Antique, w) :- Smoky(w, Antique), w > Antique. conforms emeraldTabby(a, b). } partial model Binding of Sparse { Knurled(a, b). }, Knurled(0, 0), Smoky(0, 0), emeraldTabby(0, 0)
""", "chat_history" : []}) )