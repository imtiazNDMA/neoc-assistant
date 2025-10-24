from crewai import Agent, Task, Crew
from langchain_core.tools import tool
from document_processor import document_processor
from llm_service import llm_service
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom tools for the agents
@tool
def search_documents(query: str) -> str:
    """Search for relevant documents based on a query"""
    try:
        docs = document_processor.search_similar(query, k=3)
        return llm_service.format_context(docs)
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return "Error searching documents"

@tool
def generate_response(question: str, context: str) -> str:
    """Generate a response using the LLM with provided context"""
    try:
        return llm_service.generate_response(question, context)
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}"

class ChatbotCrew:
    def __init__(self):
        self.setup_agents()
        self.setup_crew()

    def setup_agents(self):
        """Set up CrewAI agents with different roles"""

        # Document Analyst - specializes in retrieving and analyzing documents
        self.document_analyst = Agent(
            role="Document Analyst",
            goal="Retrieve and analyze relevant information from documents to answer user queries",
            backstory="You are an expert at finding and synthesizing information from technical documents about environmental science, disaster prediction, and air quality monitoring.",
            tools=[search_documents],
            verbose=False,
            allow_delegation=False,
        )

        # Response Generator - specializes in creating coherent, helpful responses
        self.response_generator = Agent(
            role="Response Generator",
            goal="Create clear, accurate, and helpful responses to user questions using retrieved context",
            backstory="You are a skilled communicator who can explain complex technical concepts in an accessible way, drawing from scientific literature and research.",
            tools=[generate_response],
            verbose=False,
            allow_delegation=False,
        )

        # Query Analyzer - analyzes user queries to determine the best approach
        self.query_analyzer = Agent(
            role="Query Analyzer",
            goal="Analyze user queries to determine if they need document retrieval or can be answered directly",
            backstory="You are an expert at understanding user intent and determining what information or tools are needed to provide the best response.",
            verbose=False,
            allow_delegation=True,
        )

    def setup_crew(self):
        """Set up the Crew with agents and tasks"""
        self.crew = Crew(
            agents=[self.query_analyzer, self.document_analyst, self.response_generator],
            verbose=False
        )

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query through the crew"""
        try:
            # Define tasks for this query
            analyze_task = Task(
                description=f"Analyze this user query: '{query}'. Determine if document search is needed.",
                agent=self.query_analyzer,
                expected_output="Analysis of query type and whether document retrieval is needed"
            )

            search_task = Task(
                description=f"Search for relevant documents related to: '{query}'",
                agent=self.document_analyst,
                context=[analyze_task],
                expected_output="Relevant context from documents"
            )

            response_task = Task(
                description=f"Generate a comprehensive response to: '{query}' using the retrieved context",
                agent=self.response_generator,
                context=[analyze_task, search_task],
                expected_output="Final response to the user query"
            )

            # Execute the crew
            result = self.crew.kickoff(inputs={"query": query})

            return {
                "response": str(result),
                "success": True
            }

        except Exception as e:
            logger.error(f"Error processing query with crew: {str(e)}")
            # Fallback to direct LLM response
            try:
                context = search_documents.func(query)
                response = generate_response.func(query, context)
                return {
                    "response": response,
                    "success": True,
                    "fallback": True
                }
            except Exception as fallback_error:
                return {
                    "response": f"I apologize, but I encountered an error processing your query: {str(e)}",
                    "success": False,
                    "error": str(e)
                }

# Global instance
chatbot_crew = ChatbotCrew()