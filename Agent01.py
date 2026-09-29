import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI


load_dotenv()

TEST_TYPES = ("Functional", "Positive", "Negative", "Boundary", "All")

SYSTEM_PROMPT = """You are a Senior QA Engineer who specializes in turning product requirements
into precise, traceable, and executable test cases.

Always use the analyze_requirement tool first, then use the generate_test_cases
tool with that analysis and the exact test type and case count from the user.
Do not invent product behavior that is not supported by the requirement. Make
assumptions explicit in the analysis. Return the generated cases with every
requested field, and verify that the requested number of cases is present.
"""


def build_agent(model: ChatOpenAI):
	@tool
	def analyze_requirement(requirement: str) -> str:
		"""Analyze a requirement into actors, behaviors, acceptance criteria, and gaps."""
		analysis_prompt = f"""Analyze this software requirement as a Senior QA Engineer.
Identify actors, preconditions, testable behaviors, observable outcomes, and
acceptance criteria. List ambiguities or missing details separately; do not
silently invent answers. Keep the analysis concise and useful for test design.

Requirement:
{requirement}
"""
		return str(model.invoke(analysis_prompt).content).strip()

	@tool
	def generate_test_cases(
		requirement: str,
		analysis: str,
		test_type: str,
		number_of_cases: int,
	) -> str:
		"""Generate the requested number and type of detailed QA test cases."""
		if number_of_cases < 1:
			return "The number of test cases must be at least 1."

		generation_prompt = f"""You are a Senior QA Engineer. Generate exactly
{number_of_cases} test cases for the selected test type: {test_type}.

Use only behaviors supported by the requirement and analysis. For "All", include
a sensible mix of functional, positive, negative, and boundary coverage when the
requirement supports those cases. Do not claim unspecified behavior as fact.

For every case, include all of these fields:
- Test Case ID (sequential IDs beginning with TC-001)
- Scenario
- Test Steps (numbered, actionable steps)
- Test Data
- Expected Result
- Priority (P1, P2, or P3)

Requirement:
{requirement}

Requirement analysis:
{analysis}

Return only the test cases, with a clear heading for each case.
"""
		return str(model.invoke(generation_prompt).content).strip()

	return create_agent(
		model=model,
		tools=[analyze_requirement, generate_test_cases],
		system_prompt=SYSTEM_PROMPT,
	)


def generate_qa_test_cases(
	requirement: str,
	test_type: str,
	number_of_cases: int,
	api_key: str | None = None,
) -> str:
	model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
	model = ChatOpenAI(model=model_name, temperature=0, api_key=api_key)
	agent = build_agent(model)
	user_prompt = f"""Analyze the requirement and generate the requested test cases.

Requirement:
{requirement}

Test type: {test_type}
Number of test cases: {number_of_cases}
"""
	result = agent.invoke({"messages": [{"role": "user", "content": user_prompt}]})
	return str(result["messages"][-1].content)


def prompt_for_test_type() -> str:
	choices = "/".join(TEST_TYPES)
	while True:
		selected = input(f"Test type ({choices}): ").strip().casefold()
		for test_type in TEST_TYPES:
			if selected == test_type.casefold():
				return test_type
		print(f"Please enter one of: {choices}.")


def prompt_for_case_count() -> int:
	while True:
		value = input("Number of test cases: ").strip()
		try:
			count = int(value)
		except ValueError:
			print("Enter a whole number greater than zero.")
			continue
		if count > 0:
			return count
		print("Enter a whole number greater than zero.")


def main() -> None:
	if not os.getenv("OPENAI_API_KEY"):
		print("Set the OPENAI_API_KEY environment variable before running this app.")
		return

	requirement = input("Requirement: ").strip()
	while not requirement:
		print("The requirement cannot be empty.")
		requirement = input("Requirement: ").strip()

	test_type = prompt_for_test_type()
	number_of_cases = prompt_for_case_count()
	try:
		generated_cases = generate_qa_test_cases(
			requirement,
			test_type,
			number_of_cases,
		)
		print("\nGenerated Test Cases\n")
		print(generated_cases)
	except Exception as error:
		print(f"Could not generate test cases: {error}")


if __name__ == "__main__":
	main()
