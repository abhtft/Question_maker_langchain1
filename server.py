from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_question_prompt(topic_data):
    return f"""Generate {topic_data['numQuestions']} {topic_data['questionType']} questions for the following topic:

Subject: {topic_data['subjectName']}
Class: {topic_data['classGrade']}
Topic: {topic_data['sectionName']}
Difficulty: {topic_data['difficulty']}
Bloom's Level: {topic_data['bloomLevel']}
Intelligence Type: {topic_data['intelligenceType']}

Additional Instructions: {topic_data['additionalInstructions']}

Please generate questions that:
1. Match the specified difficulty level
2. Target the specified Bloom's level
3. Cater to the specified intelligence type
4. Follow the question type format
5. Include answers where appropriate

Format the response as a JSON object with the following structure:
{{
    "questions": [
        {{
            "question": "question text",
            "options": ["option1", "option2", "option3", "option4"],  // for MCQ
            "answer": "correct answer",
            "explanation": "explanation of the answer"
        }}
    ]
}}
"""

@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    try:
        data = request.json
        
        # Generate questions for each topic
        all_questions = []
        for topic in data['topics']:
            # Combine topic data with basic info
            topic_data = {
                **topic,
                'subjectName': data['subjectName'],
                'classGrade': data['classGrade']
            }
            
            # Generate prompt
            prompt = generate_question_prompt(topic_data)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational question generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the response
            questions = json.loads(response.choices[0].message.content)
            all_questions.append({
                'topic': topic['sectionName'],
                'questions': questions['questions']
            })
        
        return jsonify({
            'success': True,
            'questions': all_questions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)