from langchain.agents import initialize_agent, Tool
from langchain_google_genai import GoogleGenerativeAI

from dotenv import load_dotenv
import os
load_dotenv()

class AnswerAgent:
    def __init__(self, api_key, model="gemini-1.5-flash-latest", verbose=True):
        """
        Initializes the Answer Agent with the specified LLM configuration.
        :param api_key: API key for Google Generative AI.
        :param model: Model version to use.
        :param verbose: Whether to enable verbose logging.
        """
        self.llm = GoogleGenerativeAI(model=model, google_api_key=api_key)
        self.verbose = verbose
        self.agent = self._initialize_agent()

    def _rewrite_text(self, input_text):
        """
        Rewrites the input text to make it clear, simple, and user-friendly.
        :param input_text: The text to rewrite.
        :return: The rewritten text.
        """
        prompt = f"Rewrite the following text in a clear, simple, and user-friendly way:\n\n{input_text}"
        response = self.llm.predict(prompt)
        return response

    def _initialize_agent(self):
        """
        Initializes the agent with the rewrite tool.
        :return: An initialized agent.
        """
        rewrite_tool = Tool(
            name="Answer Agent",
            func=self._rewrite_text,
            description="Rewrites the provided text to make it clear and user-friendly."
        )
        return initialize_agent(
            tools=[rewrite_tool],
            llm=self.llm,
            agent="zero-shot-react-description",
            verbose=self.verbose
        )

    def run(self, input_text):
        """
        Runs the agent on the provided input text.
        :param input_text: The input text to process.
        :return: The rewritten response.
        """
        return self.agent.run(input_text)


# Example usage
if __name__ == "__main__":
    api_key = os.getenv("GEMINI_KEY")  # Replace with your actual API key
    input_text = "The artificial intelligence system generates responses based on an advanced predictive model."

    answer_agent = AnswerAgent(api_key=api_key)
    response = answer_agent.run(input_text)
    print("User-friendly response:", response)
