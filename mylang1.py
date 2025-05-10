from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.evaluation import load_evaluator
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

class DocumentProcessor:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def process_uploaded_document(self, file_path: str) -> Tuple[Any, List[Any]]:
        """Process uploaded PDF document and create vector store"""
        try:
            # Load PDF using LangChain
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            # Split text into chunks
            texts = self.text_splitter.split_documents(pages)
            
            # Create vector store with FAISS
            vectorstore = FAISS.from_documents(
                documents=texts,
                embedding=self.embeddings
            )
            
            # Save the vector store
            vectorstore.save_local("./faiss_index")
            
            logging.info(f"Successfully processed PDF '{file_path}' into {len(texts)} chunks.")
            return vectorstore, texts
        except Exception as e:
            logging.error(f"Error processing document: {str(e)}")
            raise

class QuestionGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Better than 3.5
            temperature=0.3
        )

        self.question_template = """
        Based on the following context from study materials:
        {context}
        
        Generate {num_questions} {question_type} questions for:
        Subject: {subject}
        Class: {class_grade}
        Topic: {topic}
        Difficulty: {difficulty}
        Bloom's Level: {bloom_level}
        
        Additional Instructions: {instructions}
        
        Generate questions that:
        1. Are directly related to the provided context
        2. Test understanding at the specified Bloom's level
        3. Match the difficulty level
        4. Include detailed explanations
        
        Format the response as a JSON object with the following structure:
        {{
            "questions": [
                {{
                    "question": "question text",
                    "options": ["option1", "option2", "option3", "option4"],
                    "answer": "correct answer",
                    "explanation": "detailed explanation"
                }}
            ]
        }}
        """
        
        self.prompt = PromptTemplate(
            input_variables=[
                "context", "num_questions", "question_type", "subject",
                "class_grade", "topic", "difficulty", "bloom_level", "instructions"
            ],
            template=self.question_template
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def generate_questions(self, topic_data: Dict[str, Any], vectorstore: Any) -> Dict[str, Any]:
        """Generate questions based on topic data and vector store context"""
        try:
            # Get relevant context from vectorstore
            # relevant_docs = vectorstore.similarity_search(
            #     f"{topic_data['subjectName']} {topic_data['sectionName']}",
            #     k=3
            # )

            query = f"{topic_data['subjectName']} {topic_data['sectionName']} Grade {topic_data['classGrade']} Bloom level {topic_data['bloomLevel']}"
            relevant_docs = vectorstore.similarity_search(query, k=5)


            #context = "\n".join([doc.page_content for doc in relevant_docs])


            from langchain.chains.summarize import load_summarize_chain
            summarizer = load_summarize_chain(llm=self.llm, chain_type="stuff")
            summary = summarizer.run(relevant_docs)

            context = summary
            
            # Generate questions
            response = self.chain.invoke({
                "context": context,
                "num_questions": topic_data['numQuestions'],
                "question_type": topic_data['questionType'],
                "subject": topic_data['subjectName'],
                "class_grade": topic_data['classGrade'],
                "topic": topic_data['sectionName'],
                "difficulty": topic_data['difficulty'],
                "bloom_level": topic_data['bloomLevel'],
                "instructions": topic_data.get('additionalInstructions', '')
            })
            
            logging.info(f"Generated questions for topic: {topic_data['sectionName']}")
            return response
        except Exception as e:
            logging.error(f"Error generating questions: {str(e)}")
            raise

class QuestionEvaluator:
    def __init__(self):
        # Using the correct evaluator type with proper configuration
        self.evaluator = load_evaluator(
            "qa",
            llm=ChatOpenAI(temperature=0),
            criteria={
                "relevance": "Is the answer relevant to the question?",
                "correctness": "Is the answer factually correct based on the context?",
                "completeness": "Does the answer fully address the question?"
            }
        )
        self.feedback_chain = LLMChain(
            llm=ChatOpenAI(temperature=0.3),
            prompt=PromptTemplate(
                input_variables=["question", "feedback"],
                template="""
                Improve the following question based on the feedback:
                Question: {question}
                Feedback: {feedback}
                
                Provide an improved version that addresses the feedback while maintaining
                the original learning objectives and difficulty level.
                """
            )
        )
    
    def evaluate_question(self, question: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Evaluate the quality of a generated question"""
        try:
            logging.info(f"Evaluating question: {question['question']}")
            logging.info(f"Answer: {question['answer']}")
            logging.info(f"Context length: {len(context)} characters")
            
            # Using the correct evaluation method
            evaluation = self.evaluator.evaluate_strings(
                prediction=question['answer'],
                input=question['question'],
                reference=context
            )
            
            logging.info(f"Evaluation results: {evaluation}")
            return evaluation
        except Exception as e:
            logging.error(f"Error evaluating question: {str(e)}")
            logging.error(f"Available evaluator methods: {dir(self.evaluator)}")
            raise
    
    def incorporate_feedback(self, question: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Incorporate feedback to improve a question"""
        try:
            improved_question = self.feedback_chain.invoke({
                "question": question,
                "feedback": feedback
            })
            logging.info("Incorporated feedback into question.")
            return improved_question
        except Exception as e:
            logging.error(f"Error incorporating feedback: {str(e)}")
            raise

# Initialize the components
document_processor = DocumentProcessor()
question_generator = QuestionGenerator()
question_evaluator = QuestionEvaluator()