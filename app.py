from dotenv import load_dotenv

from openinference.instrumentation.crewai import CrewAIInstrumentor
from openinference.instrumentation.litellm import LiteLLMInstrumentor
from phoenix.otel import register

tracer_provider = register(
    project_name="Math Problem Solver",
    endpoint="http://0.0.0.0:6006/v1/traces",
    verbose=True,
    set_global_tracer_provider=True,
)

CrewAIInstrumentor().instrument(tracer_provider=tracer_provider)
LiteLLMInstrumentor().instrument(tracer_provider=tracer_provider)

from crewai import Agent, Crew, Task
from crewai.flow.flow import Flow, listen, router, start, or_
from pydantic import BaseModel

load_dotenv()

math_solver = Agent(
    role="Math Problem Solver",
    goal="Solve mathematical challenges using Python",
    backstory="You are an expert in implementing mathematical solutions in Python",
    verbose=True,
    llm="azure/gpt-4o",
    allow_delegation=False,
    allow_code_execution=True,
)

solution_reviewer = Agent(
    role="Math Result Validator",
    goal="Verify mathematical results for accuracy and correctness",
    backstory="You are an expert mathematician who specializes in verifying mathematical solutions and their correctness",
    verbose=True,
    llm="azure/gpt-4o",
    allow_delegation=False,
    allow_code_execution=True,
)


def create_solving_task(math_challenge):
    return Task(
        description=f"""Compute the solution for this mathematical challenge:
        {math_challenge}
        
        IMPORTANT: Return ONLY the numerical result or solution without any explanation or additional text.
        Format your response as a single line containing just the answer.""",
        agent=math_solver,
        expected_output="Mathematical result only",
    )


def create_review_task(challenge, result):
    return Task(
        description=f"""Verify the mathematical correctness of the following solution:
        Original Challenge: {challenge}
        Solution Result: {result}
        
        IMPORTANT: Your response must start with exactly one of these single words:
        VALID
        INVALID
        
        If invalid, add a single brief reason after a colon.
        Do not include any other text or explanations.""",
        agent=solution_reviewer,
        expected_output="Single-line validation status",
    )


class MathSolverState(BaseModel):
    challenge: str = ""
    max_attempts: int = 3
    result: str = ""
    attempts: int = 0
    feedback: str = ""


class MathSolverFlow(Flow[MathSolverState]):
    model = "azure/gpt-4o"

    @start("solve")
    def solve_challenge(self):
        print("Solving the math challenge...")
        solving_task = create_solving_task(self.state.challenge)
        solver_crew = Crew(
            agents=[math_solver],
            tasks=[solving_task],
            verbose=True,
        )
        self.state.result = solver_crew.kickoff()
        return self.state.result

    @router(solve_challenge)
    def validate_solution(self):
        print("Validating the solution...")
        review_task = create_review_task(self.state.challenge, self.state.result)
        reviewer_crew = Crew(
            agents=[solution_reviewer],
            tasks=[review_task],
            verbose=True,
        )
        result = reviewer_crew.kickoff()
        self.state.feedback = str(result).strip()

        # Simplified validation check
        is_valid = self.state.feedback.startswith("VALID")

        if not is_valid:
            self.state.attempts += 1
            return (
                "solve" if self.state.attempts < self.state.max_attempts else "failed"
            )
        return "success"

    @listen(or_("success", "failed"))
    def handle_completion(self):
        print("Solution process completed!")
        return {
            "result": self.state.result,
            "feedback": self.state.feedback,
            "attempts": self.state.attempts,
            "status": (
                "success" if self.state.attempts < self.state.max_attempts else "failed"
            ),
        }


def solve_math_challenge(challenge, max_attempts=3):
    flow = MathSolverFlow()
    print(f"Solving math challenge: {challenge}")
    result = flow.kickoff(inputs={"challenge": challenge, "max_attempts": max_attempts})
    print("Solution process completed!")
    return result


if __name__ == "__main__":
    challenge = "Calculate the first 10 Fibonacci numbers"
    result = solve_math_challenge(challenge)
    print(result)
