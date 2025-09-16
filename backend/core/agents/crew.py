"""
CartGenie AI Agent Orchestration

This module defines the CrewAI agents and tasks for cart optimization.
The system uses a sequential process where a Product Research Agent finds
the best prices, followed by a Savings Analyst Agent that provides recommendations.

Architecture:
- Research Agent: Uses vector search, knowledge graphs, and web scraping
- Analysis Agent: Processes research data to generate actionable savings recommendations
- Sequential workflow ensures context is properly passed between agents
"""

from crewai import Agent, Task, Crew, Process, LLM
from .tools import find_similar_products_in_qdrant, scrape_product_page, get_product_prices_from_neo4j
import dotenv
import os

dotenv.load_dotenv()


class CartGenieAgents:
    """
    Factory class for creating specialized AI agents for cart optimization.
    
    Each agent has specific tools and capabilities:
    - Product Research: Vector search, web scraping, knowledge graph queries
    - Savings Analysis: Data analysis and recommendation generation
    """
    
    def __init__(self, user_context: dict):
        """
        Initialize agents with user context for personalized recommendations.
        
        Args:
            user_context (dict): User location and preferences for targeted analysis
        """
        self.user_context = user_context
        
        # Configure LLM instances for different agent roles
        # Using Gemini for both agents to ensure consistent reasoning
        self.mistral_llm = LLM(
            model="gemini/gemini-2.5-flash",
            api_key=os.getenv("MISTRAL_API_KEY"),
            temperature=0,  # Deterministic responses for price comparisons
        )
        self.gemini_llm = LLM(
            model="gemini/gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0,  # Consistent analysis and recommendations
        )

    def product_research_agent(self) -> Agent:
        """
        Create a Product Research Specialist agent.
        
        This agent handles:
        - Product identification from user cart data
        - Vector similarity search for product matching
        - Real-time web scraping for current prices
        - Knowledge graph queries for historical price data
        
        Returns:
            Agent: Configured research agent with appropriate tools
        """
        return Agent(
            role="Product Research Specialist",
            goal="Identify products from user's cart and find their prices across different retailers. Use the knowledge graph for known data and web scraping for new or stale data.",
            backstory="An expert in online product identification and data retrieval, skilled in using vector databases for matching and web scraping for real-time data acquisition.",
            tools=[find_similar_products_in_qdrant, scrape_product_page, get_product_prices_from_neo4j],
            verbose=True,
            allow_delegation=False,
            llm=self.gemini_llm
        )

    def savings_analyst_agent(self) -> Agent:
        """
        Create a Savings Analyst agent.
        
        This agent handles:
        - Processing research data from the Product Research Agent
        - Calculating potential savings across different retailers
        - Generating structured recommendations
        - Formatting results according to API contract
        
        Returns:
            Agent: Configured analysis agent for recommendation generation
        """
        return Agent(
            role="Savings Analyst",
            goal="Analyze the price data collected by the Product Research Specialist to find the best possible savings for the user. Present a clear, actionable summary.",
            backstory="A meticulous analyst who excels at comparing prices, calculating savings, and presenting complex information in a simple, easy-to-understand format.",
            tools=[],  # Analysis agent focuses on data processing, not external tool usage
            verbose=True,
            allow_delegation=False,
            llm=self.gemini_llm
        )


class CartOptimizationCrew:
    """
    Orchestrates the cart optimization workflow using CrewAI.
    
    This class manages the end-to-end process:
    1. Sets up agents with user context
    2. Defines research and analysis tasks
    3. Executes the sequential workflow
    4. Returns structured optimization results
    """
    
    def __init__(self, user_cart_data: dict):
        """
        Initialize the crew with user cart data.
        
        Args:
            user_cart_data (dict): Complete cart data including context, retailer, and items
        """
        self.user_cart_data = user_cart_data
        self.agents = CartGenieAgents(user_context=self.user_cart_data.get('userContext', {}))

    def setup_crew(self) -> Crew:
        """
        Configure and return a CrewAI crew for cart optimization.
        
        The crew follows a sequential process:
        1. Research Task: Find best prices for each cart item
        2. Analysis Task: Generate savings recommendations
        
        Returns:
            Crew: Configured CrewAI crew ready for execution
        """
        # Initialize the specialized agents
        researcher = self.agents.product_research_agent()
        analyst = self.agents.savings_analyst_agent()

        # Prepare context string for both tasks
        task_context = f"""
        User Context: {self.user_cart_data.get('userContext')}
        Source Retailer: {self.user_cart_data.get('sourceRetailer')}
        Cart Items: {self.user_cart_data.get('items')}
        """

        # Define the research task - executed first
        research_task = Task(
            description=f"For each product in the user's cart, identify it and find the best price. The user's context and cart are as follows:\n{task_context}",
            expected_output="A detailed list of products with the best price found for each, including the retailer, URL, and currency.",
            agent=researcher,
        )

        # Define the analysis task - executed after research
        analysis_task = Task(
            description=f"Analyze the research findings to create a final savings report. The original cart data is:\n{task_context}",
            expected_output="A JSON object summarizing the total savings and providing a list of recommendations for each item, matching the API contract.",
            agent=analyst,
        )

        # Create and return the crew with sequential processing
        return Crew(
            agents=[researcher, analyst],
            tasks=[research_task, analysis_task],
            process=Process.sequential,  # Ensures research completes before analysis
            verbose=True  # Enable detailed logging for debugging
        )