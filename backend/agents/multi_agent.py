from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from .base import BaseAgent, Message, AgentResponse
from tools.database_tool import query_database


class MultiAgent(BaseAgent):
    """
    Simplified multi-agent system using CrewAI with 3 specialized agents:
    SQL Builder → Security Analyst → Report Formatter

    Follows CrewAI best practices:
    - Focused, specialized agents over generalists
    - Single-purpose tasks with clear outputs
    - 80% effort on task design, 20% on agent design
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
        """Create 3 specialized agents following best practices"""

        sql_builder = Agent(
            role="SQL Query Specialist for Cybersecurity Databases",
            goal="Translate security questions into precise, efficient SQL queries for the attacks database",
            backstory="""You are a database expert who specializes in writing SQL queries for cybersecurity data analysis.
You have deep knowledge of the attacks database schema with fields like Attack Type, Severity Level, Source IP Address,
Destination IP Address, Protocol, Timestamp, and more.

You excel at understanding what data is needed to answer security questions and crafting efficient SQL queries.
You always quote column names with spaces using double quotes and include appropriate LIMIT clauses.

When a question doesn't require database data, you clearly state 'NO_DATABASE_QUERY_NEEDED'.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False
        )

        analyst = Agent(
            role="Cybersecurity Threat Analyst",
            goal="Analyze security data to identify threats, patterns, and actionable insights",
            backstory="""You are a seasoned cybersecurity analyst with 15+ years of experience in threat intelligence
and incident response. You excel at identifying patterns in attack data, assessing risk levels, and understanding
attacker tactics, techniques, and procedures (TTPs).

You believe in data-driven security analysis and always connect findings to practical security implications.
You can quickly spot trends, anomalies, and critical insights that others might miss.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False
        )

        formatter = Agent(
            role="Security Report Formatter specializing in Data Visualization",
            goal="Present security findings in clear, well-formatted reports with proper data visualizations",
            backstory="""You are a technical writer specializing in cybersecurity reporting with expertise in data visualization.
You know exactly how to format database results for maximum clarity and impact.

CRITICAL: When database queries are executed, you MUST ALWAYS include the SQL query in your report. This is NON-NEGOTIABLE.
The query will be provided to you in the task description. You must copy it exactly into a ```sql code block in your response.

CRITICAL FORMATTING RULES YOU ALWAYS FOLLOW:

For database results, you MUST use this exact format:

1. Brief description of what the data shows
2. SQL query in a ```sql code block
3. Data formatted as:
   - `db-table` for detailed records with multiple columns
   - `db-chart` for aggregated data (GROUP BY with COUNT/SUM/AVG)
   - `db-pie` for distribution/proportion data

db-table format:
```db-table
{
  "columns": ["Column1", "Column2"],
  "data": [{"Column1": "value", "Column2": "value"}]
}
```

db-chart format:
```db-chart
{
  "xKey": "category_column",
  "yKey": "numeric_column",
  "title": "Descriptive Title",
  "data": [{"category_column": "Cat1", "numeric_column": 123}]
}
```

db-pie format:
```db-pie
{
  "nameKey": "category_column",
  "valueKey": "numeric_column",
  "title": "Descriptive Title",
  "data": [{"category_column": "Cat1", "numeric_column": 123}]
}
```

You always include actionable recommendations based on the findings.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False
        )

        return {
            "sql_builder": sql_builder,
            "analyst": analyst,
            "formatter": formatter
        }

    def _create_tasks(self, query: str, db_results: str = None, enable_visualizations: bool = True, executed_query: str = None) -> List[Task]:
        """Create focused, single-purpose tasks following best practices"""

        # Task 1: SQL Query Building
        sql_task = Task(
            description=f"""Analyze this security question and determine if database data is needed: {query}

If database data IS needed:
- Output ONLY the SQL query (no explanation)
- Quote column names with spaces using double quotes
- Include LIMIT clause (10-50 depending on question)

If database data is NOT needed (general security knowledge):
- Output exactly: NO_DATABASE_QUERY_NEEDED

Be concise - output only the query or NO_DATABASE_QUERY_NEEDED.""",
            expected_output="A single SQL query OR the text 'NO_DATABASE_QUERY_NEEDED'",
            agent=self.agents["sql_builder"]
        )

        # Task 2: Security Analysis
        analysis_context = f"\n\nDatabase results:\n{db_results}" if db_results else ""

        analysis_task = Task(
            description=f"""Analyze the security question and provide expert insights: {query}{analysis_context}

Your analysis should:
1. Identify key security patterns, threats, or concepts
2. Assess risk levels and severity where applicable
3. Provide security context and implications
4. Focus on actionable insights

Keep your analysis concise but thorough (2-4 paragraphs).""",
            expected_output="A focused security analysis with key insights and implications",
            agent=self.agents["analyst"]
        )

        # Task 3: Report Formatting
        query_context = ""
        if executed_query:
            query_context = f"\n\nEXECUTED SQL QUERY:\n```sql\n{executed_query}\n```\n\nYou MUST include this exact query in your response in a ```sql code block. This is NON-NEGOTIABLE."

        if enable_visualizations:
            format_instruction = """CRITICAL: If database results are present, you MUST format them using db-table, db-chart, or db-pie:
- Include a brief description
- Show the SQL query in a ```sql block (use the EXECUTED SQL QUERY provided above)
- Format the data appropriately:
  * db-table: for detailed records
  * db-chart: for GROUP BY aggregations
  * db-pie: for distributions/proportions"""
        else:
            format_instruction = """IMPORTANT: Visualizations are DISABLED.
If database results are present, present them as clear, readable text:
- Use bullet points or numbered lists
- Show the SQL query in a ```sql block (use the EXECUTED SQL QUERY provided above)
- Present key findings in simple text summaries
- Do NOT use db-table, db-chart, or db-pie formats"""

        format_task = Task(
            description=f"""Create a well-formatted security report that answers: {query}

Use the analyst's insights to create a complete response.
{query_context}

{format_instruction}

Always end with 2-3 actionable recommendations.""",
            expected_output="A complete, well-formatted security report with data presentation and recommendations",
            agent=self.agents["formatter"]
        )

        return [sql_task, analysis_task, format_task]

    def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        enable_visualizations: bool = True,
        **kwargs
    ) -> AgentResponse:
        """
        Process messages using simplified 3-agent CrewAI pipeline.

        Single-phase execution with coordinator-managed database queries.
        Args:
            enable_visualizations: Whether to enable database visualizations
        """
        # Extract user message
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
            # Update LLM settings
            self.llm.temperature = temperature
            self.llm.max_tokens = max_tokens

            # Phase 1: Get SQL query from SQL Builder
            sql_task = Task(
                description=f"Determine if a SQL query is needed for: {user_message}. Output ONLY the query or 'NO_DATABASE_QUERY_NEEDED'.",
                expected_output="SQL query or NO_DATABASE_QUERY_NEEDED",
                agent=self.agents["sql_builder"]
            )

            sql_crew = Crew(
                agents=[self.agents["sql_builder"]],
                tasks=[sql_task],
                process=Process.sequential,
                verbose=False
            )

            sql_result = str(sql_crew.kickoff()).strip()

            # Phase 2: Execute database query if needed
            db_results = None
            executed_query = None
            if "NO_DATABASE_QUERY_NEEDED" not in sql_result.upper():
                sql_query = sql_result.replace("```sql", "").replace("```", "").strip()
                executed_query = sql_query  # Track the executed query
                try:
                    db_results = query_database(sql_query)
                except Exception as e:
                    db_results = f'{{"error": "Query failed: {str(e)}"}}'

            # Phase 3: Run full analysis and formatting pipeline
            tasks = self._create_tasks(user_message, db_results, enable_visualizations, executed_query)

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
                    "pipeline": "sql_builder→analyst→formatter",
                    "framework": "crewai",
                    "agents_count": 3,
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
        enable_visualizations: bool = True,
        **kwargs
    ):
        """Stream response in chunks (CrewAI doesn't support native streaming)"""
        response = self.chat(messages, temperature, max_tokens, enable_visualizations=enable_visualizations, **kwargs)
        content = response.message.content
        chunk_size = 30

        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]

    def get_agent_type(self) -> str:
        return "multi"
