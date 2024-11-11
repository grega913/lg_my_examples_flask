import random
from faker import Faker
from datetime import datetime, timedelta
from icecream import ic
import os
import sys

import logging
from dotenv import load_dotenv
import time



src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ic(src_path)
sys.path.append(src_path)



from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import chromadb

load_dotenv()

data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(data_dir)
#ic(sys.path)

parent_dir = os.path.dirname(os.path.abspath(__file__))
fileName = os.path.join(parent_dir, "data", "umbrella_corp_policies.pdf")
persitence_path = os.path.join(parent_dir, "data", "vectorstore")



fake = Faker()

def generate_employee_data(num_employees=5):
    employees = []
    for _ in range(num_employees):

        employee = {
            "employee_id": fake.uuid4(),
            "name": fake.first_name(),
            "lastname": fake.last_name(),
            "email": fake.email(),
            "phone_number": fake.phone_number(),
            "position": random.choice([
                "Research Scientist", 
                "Software Engineer", 
                "Operations Manager", 
                "HR Specialist", 
                "Security Officer"
            ]),
            "department": random.choice([
                "R&D", 
                "IT", 
                "Operations", 
                "HR", 
                "Security"
            ]),
            "skills": random.sample([
                "Python", "Project Management", "Data Analysis", 
                "Genetic Research", "Cybersecurity", "Machine Learning",
                "Leadership", "Database Management", "Public Speaking"
            ], k=random.randint(2, 5)),
            "location": random.choice([
                "Raccoon City HQ", 
                "Umbrella Europe", 
                "Umbrella Asia", 
                "Umbrella North America", 
                "Umbrella South America"
            ]),
            "hire_date": (
                datetime.now() - timedelta(days=random.randint(1, 365 * 10))
            ).strftime("%Y-%m-%d"),
            "supervisor": fake.name(),
            "salary": round(random.uniform(40000, 120000), 2),
        }

        employees.append(employee)

    return employees


def get_user_data():
    ic("def get_user_data")
    return generate_employee_data(1)[0]


    #serialized version of results is stored in the cache
    # this cache is copying the results from the function and hashing them using pickle
    @st.cache_data(ttl=3600, show_spinner="Loading Employee data . . . ")
    def get_user_data():
        return generate_employee_data(1)[0]
    

# we are not returning a serializable object, but are returning a mutable object, which is DB Client
# this one is not copying anything, just storing it as is

def init_vector_store(pdf_path, persistent_path=""):
    ic("def init_vector_store")
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap = 200)
        splits = text_splitter.split_documents(docs)


        parent_dir = os.path.dirname(os.path.abspath(__file__))
        persistent_path_path = os.path.join(parent_dir, "vectorstore")

        embedding_function = OpenAIEmbeddings()
        # persistent_path = "./data/vectorstore" # persist vectors locally
        persistent_path = persistent_path_path



        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embedding_function,
            persist_directory=persistent_path
        )

        

        return vectorstore
    
    except Exception as e:
        logging.error(f" Error initializing vector store: { str(e)}")
        return None
    

def init_vector_store_2(pdf_path, persistent_path=""):
    ic("def init_vector_store_2")
    ic(pdf_path)
    ic(persistent_path)

    embedding_function = OpenAIEmbeddings()

    # check if persist_directory is Not None
    if os.path.exists(persistent_path) and os.listdir(persistent_path):
        ic("Directory exists and is not empty, meaning we should access vectorstore")
        ic(persistent_path)

        client = chromadb.PersistentClient(path=persistent_path)
        ic(client)

        vectorstore = Chroma(embedding_function=embedding_function, client=client)
        ic(vectorstore)


        ic("here we should get vectorstore from persistent_path")
        
    else:
        ic("Directory does not exist or is empty")

        try:
            ic("we are in try statement, will load data and all that other stuff")
            ic("this should only run first time we run this function, as we eant to load, chunk, . . . to only happens once")
            ic("other times we will define vectorstore with PersistenceClient")

            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap = 200)
            splits = text_splitter.split_documents(docs)

            embedding_function = OpenAIEmbeddings()
                
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=embedding_function,
                persist_directory=persistent_path
            )
        
    
        except Exception as e:
            logging.error(f" Error initializing vector store: { str(e)}")
            return None
        
    return vectorstore



def appendMessageToSessionMessages(role, message, session):
    ic(f"def appendMessageToSessionMesages: ${role}, ${message}")

    messages = session["messages"]
    messages.append({"role": role, "content": message})

    session['messages'] = messages

    return messages


class OnboardingAssistant:
    def __init__(
        self,
        system_prompt,
        llm,
        message_history=[],
        vector_store=None,
        employee_information=None,
        persist_directory = None,
        session = None

    ):
        
        ic("init OnboardingAssistant")

        self.system_prompt = system_prompt
        self.llm = llm
        self.messages = message_history
        self.vector_store = vector_store
        self.employee_information = employee_information
        self.vector_store = init_vector_store_2(pdf_path=fileName, persistent_path=persist_directory)
        self.chain = self._get_conversation_chain(session=session)


    def get_response(self, user_input, session):
        ic(f"def get_response for user_input: ${user_input}")

        appendMessageToSessionMessages(role = "user", message=user_input, session=session)
                
        return self.chain.stream(user_input)

    def _get_conversation_chain(self, session):
        ic("def get_converstation_chain")
        prompt = ChatPromptTemplate(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder("conversation_history"),
                ("human", "{user_input}"),
            ]
        )

        llm = self.llm

        output_parser = StrOutputParser()

        chain = (
            {
                "retrieved_policy_information": self.vector_store.as_retriever(),
                #"employee_information": lambda x: self.employee_information, #Runnable Parallel takes a Runnable as a value
                "employee_information": lambda x: session["user"], #this is store in sesssion
                "user_input": RunnablePassthrough(),
                #"conversation_history": lambda x: self.messages, # since messages are stored in session, we should define them accordingly
                "conversation_history": lambda x: session["messages"]
            }
            | prompt
            | llm
            | output_parser
        )
        return chain


    def getNameFromSession(self, session):
        return session["user"]
    
    def getNumberOfCalls(self, session):
        return session["calls"]



# this is a little cleaned up version
# since we'll be storing messages and employee infromation in session, do not need those 2 at init
class OnboardingAssistant_2:
    def __init__(
        self,
        system_prompt,
        llm,
        persist_directory = None,
        session = None
    ):
        
        ic("init OnboardingAssistant_2")

        self.system_prompt = system_prompt
        self.llm = llm
        self.vector_store = init_vector_store_2(pdf_path=fileName, persistent_path=persist_directory)
        self.chain = self._get_conversation_chain(session=session)

    def get_response(self, user_input, session):
        ic(f"def get_response for user_input: ${user_input}")
        return self.chain.stream(user_input)

    def _get_conversation_chain(self, session):
        ic("def get_converstation_chain")
        prompt = ChatPromptTemplate(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder("conversation_history"),
                ("human", "{user_input}"),
            ]
        )

        llm = self.llm

        output_parser = StrOutputParser()

        chain = (
            {
                "retrieved_policy_information": self.vector_store.as_retriever(),
                #"employee_information": lambda x: self.employee_information, #Runnable Parallel takes a Runnable as a value
                "employee_information": lambda x: session["user"], #this is store in sesssion
                "user_input": RunnablePassthrough(),
                #"conversation_history": lambda x: self.messages, # since messages are stored in session, we should define them accordingly
                "conversation_history": lambda x: session["messages"]
            }
            | prompt
            | llm
            | output_parser
        )
        return chain







if __name__ == "__main__":
    ic("name = main in al_helperz.py")
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    

    #vectorstore = init_vector_store_2(pdf_path=fileName, persistent_path=persitence_path)
