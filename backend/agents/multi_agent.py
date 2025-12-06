from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from .base import BaseAgent, Message, AgentResponse
from tools.database_tool import query_database


# Database formatting instructions to be appended to agent prompts
DATABASE_FORMAT_INSTRUCTIONS = """
CRITICAL: When presenting database results, you MUST ALWAYS follow this format:

1. **Description:** Start with a brief description of what you're showing and why it's relevant.

2. **Query:** Display the SQL query used:
   ```sql
   <the SQL query>
   ```

3. **Data View:** Present the results in a structured format. Choose the appropriate format based on the data:

   a) For detailed data or multiple columns, use a table format with `db-table`:
   ```db-table
   {
     "columns": ["Column1", "Column2", "Column3"],
     "data": [{"Column1": "Val1", "Column2": "Val2", "Column3": "Val3"}]
   }
   ```

   b) For grouped/aggregated data (e.g., counts, sums, averages by category), use a bar chart format with `db-chart`:
   ```db-chart
   {
     "xKey": "category_column",
     "yKey": "numeric_column",
     "title": "Descriptive Chart Title",
     "data": [{"category_column": "Category1", "numeric_column": 123}]
   }
   ```

   c) For distribution/proportion data showing parts of a whole, use a pie chart format with `db-pie`:
   ```db-pie
   {
     "nameKey": "category_column",
     "valueKey": "numeric_column",
     "title": "Descriptive Chart Title",
     "data": [{"category_column": "Category1", "numeric_column": 123}]
   }
   ```

Use charts for aggregated data (GROUP BY queries with COUNT, SUM, AVG, etc.) and tables for detailed records. Use pie charts when showing distribution/proportions.
"""


class MultiAgent(BaseAgent):
    """
    Multi-agent system using CrewAI with a sequential pipeline:
    Interpreter → Query Builder → Data Retrieval → Analysis → Reporter

    This implementation uses CrewAI 0.11.2 which doesn't support LangChain tools directly,
    so database queries are executed by the coordinator and passed through task context.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key, model)
        self.llm = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            temperature=0.7
        )
        self.agents = self._create_agents()

    def _create_agents(self) -> Dict[str, Agent]:
        """Create the 5-agent pipeline"""

        interpreter = Agent(
            role="Query Interpreter",
            goal="Understand and clarify the user's security question or request",
            backstory="""You are an expert at understanding security-related questions and breaking them down into clear, actionable components.

You specialize in identifying:
- Whether the question requires database queries or general security knowledge
- The specific type of data or analysis needed
- Key security concepts and terminology involved

Provide a concise interpretation that guides the next agents.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False
        )

        query_builder = Agent(
            role="Query Builder",
            goal="Build structured SQL queries to retrieve relevant security data from the attacks database",
            backstory="""You are skilled at translating security questions into specific SQL queries for the cybersecurity attacks database.

The database contains a table called 'attacks' with fields like:
- Timestamp, Source IP Address, Destination IP Address
- Attack Type (Malware, DDoS, Intrusion, etc.)
- Severity Level (Low, Medium, High, Critical)
- Protocol, Source Port, Destination Port
- Malware Indicators, Anomaly Scores
- And many more fields

IMPORTANT:
- Column names with spaces MUST be quoted with double quotes in SQL queries
- Example: SELECT "Attack Type", "Severity Level" FROM attacks
- Always include appropriate LIMIT clauses (e.g., LIMIT 10, LIMIT 50)

If the question requires database data, provide ONLY the SQL query to execute.
If the question is general security knowledge, state "NO DATABASE QUERY NEEDED".""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False
        )

        data_retrieval = Agent(
            role="Data Retrieval Specialist",
            goal="Present database query results in structured format",
            backstory="""You excel at organizing and presenting database query results.

When you receive database results, present them clearly with:
1. The SQL query that was executed
2. The number of results returned
3. The data in a clean, structured format

If no database query was needed, simply pass that information forward.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False
        )

        analyst = Agent(
            role="Security Analyst",
            goal="Analyze security data and identify threats, vulnerabilities, patterns, and insights",
            backstory="""You are a seasoned security analyst who can identify critical insights from security data and threat intelligence.

You specialize in:
- Identifying patterns and trends in attack data
- Assessing severity and risk levels
- Understanding attack vectors and techniques
- Providing context for security findings

Analyze the data provided and extract meaningful security insights.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False
        )

        reporter = Agent(
            role="Security Reporter",
            goal="Create clear, actionable security reports with properly formatted data visualizations",
            backstory=f"""You specialize in communicating security findings in a clear, structured way with actionable recommendations.

You are a cybersecurity expert assistant specializing in threat analysis and security best practices.

{DATABASE_FORMAT_INSTRUCTIONS}

When presenting database results, ALWAYS use the appropriate format (db-table, db-chart, or db-pie) based on the data type.
Provide accurate, practical, and actionable security guidance based on real data.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False
        )

        return {
            "interpreter": interpreter,
            "query_builder": query_builder,
            "data_retrieval": data_retrieval,
            "analyst": analyst,
            "reporter": reporter
        }

    def _create_tasks(self, query: str, db_results: str = None) -> List[Task]:
        """Create sequential tasks for the pipeline

        Args:
            query: User's question
            db_results: Database results from coordinator (if any)
        """

        task_interpret = Task(
            description=f"""Interpret this security question: {query}

Determine:
1. Is this a database query question or general security question?
2. What specific information is being requested?
3. What type of analysis is needed?

Keep your response concise (2-3 sentences).""",
            expected_output="A clear, concise interpretation of the question",
            agent=self.agents["interpreter"]
        )

        task_query_build = Task(
            description="""Based on the interpretation, determine if SQL queries are needed.

If database data is needed:
- Provide ONLY the SQL query to execute
- Quote column names with spaces using double quotes
- Include appropriate LIMIT clause

If no database is needed:
- Respond with exactly: "NO DATABASE QUERY NEEDED"

Be concise - only output the query or the "NO DATABASE QUERY NEEDED" message.""",
            expected_output="A SQL query OR 'NO DATABASE QUERY NEEDED'",
            agent=self.agents["query_builder"]
        )

        # If we have db_results, include them in the data retrieval task
        data_context = ""
        if db_results:
            data_context = f"\n\nDatabase query results:\n{db_results}"

        task_data_retrieval = Task(
            description=f"""Present the data retrieval results.{data_context}

If database results are provided above:
- Summarize what data was retrieved
- Note the number of records

If no database query was needed:
- State that general security knowledge will be used

Keep it brief (2-3 sentences).""",
            expected_output="Summary of data retrieval results",
            agent=self.agents["data_retrieval"]
        )

        task_analysis = Task(
            description="""Analyze the information and provide security insights.

If database results were provided:
- Identify patterns and trends
- Assess severity and risk levels
- Provide security context

If no database results:
- Provide general security expertise

Focus on actionable insights.""",
            expected_output="Security analysis with key findings and insights",
            agent=self.agents["analyst"]
        )

        task_report = Task(
            description=f"""Create a comprehensive security report answering the user's question.

CRITICAL: If database results are available, you MUST format them properly:
1. Include a description
2. Show the SQL query in a ```sql block
3. Format data as db-table, db-chart, or db-pie based on type:
   - Use db-table for detailed records
   - Use db-chart for aggregated data (GROUP BY with COUNT/SUM/AVG)
   - Use db-pie for distribution/proportion data

The original question was: {query}

Provide a complete, well-formatted answer with actionable recommendations.""",
            expected_output="A comprehensive, well-formatted security report",
            agent=self.agents["reporter"]
        )

        return [task_interpret, task_query_build, task_data_retrieval, task_analysis, task_report]

    def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AgentResponse:
        """
        Process messages using CrewAI sequential pipeline with database coordination.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            AgentResponse with the final report
        """
        # Extract the last user message
        user_message = None
        for msg in reversed(messages):
            if msg.role == "user":
                user_message = msg.content
                break

        if not user_message:
            return AgentResponse(
                message=Message(role="assistant", content="No user message found."),
                usage={},
                metadata={"agent_type": "multi", "error": "No user input"}
            )

        try:
            # Update LLM temperature
            self.llm.temperature = temperature
            self.llm.max_tokens = max_tokens

            # Step 1: Run interpreter and query builder to determine if DB query is needed
            initial_tasks = [
                Task(
                    description=f"Interpret this security question: {user_message}",
                    expected_output="Interpretation of the question",
                    agent=self.agents["interpreter"]
                ),
                Task(
                    description="Determine if a SQL query is needed. If yes, provide ONLY the SQL query. If no, respond with 'NO DATABASE QUERY NEEDED'.",
                    expected_output="SQL query or 'NO DATABASE QUERY NEEDED'",
                    agent=self.agents["query_builder"]
                )
            ]

            initial_crew = Crew(
                agents=[self.agents["interpreter"], self.agents["query_builder"]],
                tasks=initial_tasks,
                process=Process.sequential,
                verbose=False
            )

            initial_result = initial_crew.kickoff()
            query_builder_output = str(initial_result).strip()

            # Step 2: Execute database query if needed
            db_results = None
            if "NO DATABASE QUERY NEEDED" not in query_builder_output.upper():
                # Extract SQL query from the output
                sql_query = query_builder_output

                # Clean up the query
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

                # Execute the query
                try:
                    db_results = query_database(sql_query)
                except Exception as e:
                    db_results = f"Error executing query: {str(e)}"

            # Step 3: Run the full pipeline with database results
            tasks = self._create_tasks(user_message, db_results)

            crew = Crew(
                agents=list(self.agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=False
            )

            result = crew.kickoff()
            final_output = str(result)

            return AgentResponse(
                message=Message(role="assistant", content=final_output),
                usage={},
                metadata={
                    "agent_type": "multi",
                    "pipeline": "interpreter→query_builder→data_retrieval→analyst→reporter",
                    "framework": "crewai",
                    "database_query_executed": db_results is not None
                }
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return AgentResponse(
                message=Message(
                    role="assistant",
                    content=f"I encountered an error while processing your request: {str(e)}"
                ),
                usage={},
                metadata={"agent_type": "multi", "error": str(e)}
            )

    def chat_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        Process messages using CrewAI pipeline with simulated streaming.
        Note: CrewAI doesn't support true streaming, so we'll return the result in chunks.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Yields:
            Chunks of the response
        """
        # Get the complete response
        response = self.chat(messages, temperature, max_tokens, **kwargs)

        # Stream it in chunks
        content = response.message.content
        chunk_size = 30

        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]

    def get_agent_type(self) -> str:
        return "multi"
