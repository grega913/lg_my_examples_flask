from langchain_community.tools.tavily_search import TavilySearchResults
from pprint import pprint
from icecream import ic

tavily_search = TavilySearchResults(max_results=3)



if __name__=="__main__":

    search_docs = tavily_search.invoke("Whatr are some crypto currencies that are hot today?")

    for doc in search_docs:
        ic(doc)