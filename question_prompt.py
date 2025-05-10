from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import openai
import json
import os
from dotenv import load_dotenv
import mylang1  # Import mylang1 module

load_dotenv()

class QuestionPromptGenerator:
    def __init__(self):
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )

    def generate_general_prompt(self, topic_data):
        """Generate basic prompt without PDF context"""
        return f"""You are an expert educator tasked to create questions.

Generate {topic_data['numQuestions']} {topic_data['questionType']} questions for:

- Subject: {topic_data['subjectName']}
- Class/Grade: {topic_data['classGrade']}
- Topic: {topic_data['sectionName']}
- Difficulty Level: {topic_data['difficulty']}
- Bloom's Taxonomy Level: {topic_data['bloomLevel']}

Additional Instructions: {topic_data['additionalInstructions']}

🔵 Strict Requirements:
1. Match exactly the specified difficulty and Bloom's level.
2. Test deep conceptual understanding, not rote memorization.
3. Use technical language appropriate for Class {topic_data['classGrade']} level.
4. Follow the {topic_data['questionType']} format precisely.
5. If MCQ:
    - Provide exactly 4 options.
    - Ensure all options are realistic and meaningful.
6. For each question, provide:
    - Clear and concise question text
    - Correct answer
    - Step-by-step detailed explanation
7. Avoid ambiguity in question phrasing.
8. Do not repeat or slightly vary questions.

🟢 Output Format (strictly JSON):
{{
  "questions": [
    {{
      "question": "What is the capital of France?",
      "options": ["Berlin", "London", "Paris", "Rome"],
      "answer": "Paris",
      "explanation": "Paris is the capital and most populous city of France."
    }}
  ]
}}
"""

    def generate_enhanced_prompt(self, topic_data, vectorstore):
        """Generate enhanced prompt with PDF context using LangChain"""
        # Get relevant context from PDF
        docs = vectorstore.similarity_search(
            topic_data['sectionName'],
            k=3  # Get top 3 most relevant chunks
        )
        
        # Combine context from PDF
        pdf_context = "\n".join([doc.page_content for doc in docs])
        
        return f"""You are an expert educator tasked to create questions based on the provided context.

Context from uploaded notes:
{pdf_context}

Generate {topic_data['numQuestions']} {topic_data['questionType']} questions for:

- Subject: {topic_data['subjectName']}
- Class/Grade: {topic_data['classGrade']}
- Topic: {topic_data['sectionName']}
- Difficulty Level: {topic_data['difficulty']}
- Bloom's Taxonomy Level: {topic_data['bloomLevel']}

Additional Instructions: {topic_data['additionalInstructions']}

🔵 Strict Requirements:
1. Questions MUST be based on the provided context.
2. Match exactly the specified difficulty and Bloom's level.
3. Test deep conceptual understanding, not rote memorization.
4. Use technical language appropriate for Class {topic_data['classGrade']} level.
5. Follow the {topic_data['questionType']} format precisely.
6. If MCQ:
    - Provide exactly 4 options.
    - Ensure all options are realistic and meaningful.
7. For each question, provide:
    - Clear and concise question text
    - Correct answer
    - Step-by-step detailed explanation
8. Avoid ambiguity in question phrasing.
9. Do not repeat or slightly vary questions.

🟢 Output Format (strictly JSON):
{{
  "questions": [
    {{
      "question": "What is the capital of France?",
      "options": ["Berlin", "London", "Paris", "Rome"],
      "answer": "Paris",
      "explanation": "Paris is the capital and most populous city of France."
    }}
  ]
}}
"""

    def generate_questions(self, topic_data, vectorstore=None):
        """Generate questions using either general or enhanced prompt"""
        try:
            if vectorstore:
                # Use mylang1 for PDF-based question generation
                questions = mylang1.question_generator.generate_questions(topic_data, vectorstore)
                
                # Evaluate questions using mylang1
                evaluated_questions = []
                for question in questions['questions']:
                    evaluation = mylang1.question_evaluator.evaluate_question(
                        question,
                        topic_data['sectionName']
                    )
                    if evaluation['score'] > 0.7:  # Only keep high-quality questions
                        evaluated_questions.append(question)
                
                return {'questions': evaluated_questions}
            else:
                # Use basic prompt for non-PDF questions
                prompt = self.generate_general_prompt(topic_data)
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert educational question generator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            raise

    def evaluate_question(self, question, topic):
        """Evaluate the quality of a generated question"""
        try:
            if hasattr(mylang1, 'question_evaluator'):
                # Use mylang1's question evaluator if available
                return mylang1.question_evaluator.evaluate_question(question, topic)
            else:
                # Fallback to basic evaluation
                evaluation_prompt = f"""Evaluate this question for topic '{topic}':

Question: {question['question']}
Answer: {question['answer']}
Explanation: {question['explanation']}

Rate the question on:
1. Relevance to topic (0-1)
2. Clarity and precision (0-1)
3. Difficulty level appropriateness (0-1)
4. Quality of explanation (0-1)

Output format (JSON):
{{
    "score": <average of all ratings>,
    "feedback": "<detailed feedback>"
}}"""

                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert educational question evaluator."},
                        {"role": "user", "content": evaluation_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"Error evaluating question: {str(e)}")
            return {"score": 0, "feedback": f"Error in evaluation: {str(e)}"}
