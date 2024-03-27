from flask import Flask, request, jsonify, render_template
import openai
import openai.error
import traceback
require('dotenv').config()

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = process.env.API_KEY
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate_text():
    # Extract text data from the POST request form
    essay_title = request.form['essay_title']
    essay = request.form['essay']
    
    try:
        # Generate prompt for OpenAI
        prompt = f"I need you to evaluate an input essay and generate the output in the below format:\n\
Grade: (Letter grade)\n\
Relevance to the title: (in %)\n\
Grammatical errors: (list of mistake specifying the line)\n\
Feedback: (constructive comments)\n\
Improvised essay: (Display essay with changes mentioned)\n\n\
Inputs:\n\
Essay Title: {essay_title}\n\
Essay: {essay}\n"

        # Send prompt to OpenAI API for evaluation
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            temperature=0.7,
            max_tokens=1200
        )

        # Process the API response
        evaluation = response['choices'][0]['text'].strip()

        # Initialize variables for evaluation results
        grade = None
        relevance = None
        errors = None
        feedback = None
        improvised_essay = None

        # Split evaluation into separate components
        components = evaluation.split('\n')

        # Iterate through components to parse evaluation results
        for line in components:
            if line.startswith("Grade:"):
                grade = line.split("Grade:")[1].strip()
            elif line.startswith("Relevance:"):
                relevance = line.split("Relevance:")[1].strip()
            elif line.startswith("Errors:"):
                errors = line.split("Errors:")[1].strip()
            elif line.startswith("Feedback:"):
                feedback = line.split("Feedback:")[1].strip()
            elif line.startswith("Improvised Essay:"):
                improvised_essay = line.split("Improvised Essay:")[1].strip()

        # Pass evaluation results as JSON response
        return jsonify({
            'grade': grade,
            'relevance': relevance,
            'errors': errors,
            'feedback': feedback,
            'improvised_essay': improvised_essay
        })

    except openai.error.RateLimitedError as e:
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429  # Return a 429 status code for rate limit exceeded

    except Exception as e:
        traceback.print_exc()  # Print the exception traceback to the console
        return jsonify({'error': 'Internal server error occurred. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
