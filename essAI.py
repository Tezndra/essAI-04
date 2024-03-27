from flask import Flask, request, jsonify, render_template
import openai
require('dotenv').config()

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = process.env.API_KEY

@app.route('/', methods=['GET', 'POST'])
def generate_completion():
    if request.method == 'POST':
        essay_title = request.form.get('essay_title')
        essay_content = request.form.get('essay')

        # Construct the prompt
        prompt = f"I need you to evaluate an input essay and generate the output in the below format:\n" \
                 f"Grade: (Letter grade)\n" \
                 f"Relevance to the title: (in %)\n" \
                 f"Grammatical errors: (list of mistakes specifying the line)\n" \
                 f"Feedback: (constructive comments)\n\n" \
                 f"Inputs:\n" \
                 f"Essay Title: {essay_title}\n" \
                 f"Essay: {essay_content}"

        # Call OpenAI API to generate completion
        try:
            response = openai.Completion.create(
                engine="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=500
            )
            completion_text = response.choices[0].text.strip()

            # Split completion text into parts based on keywords
            split_text = completion_text.split("Grade:")
            grade = split_text[1].split("Relevance to the title:")[0].strip()

            relevance = split_text[1].split("Relevance to the title:")[1].split("Grammatical errors:")[0].strip()

            grammatical_errors = split_text[1].split("Grammatical errors:")[1].split("Feedback:")[0].strip()

            feedback = split_text[1].split("Feedback:")[1].strip()


        except Exception as e:
            return f"Error: {str(e)}"

        return render_template('completion.html', grade=grade, relevance=relevance, grammatical_errors=grammatical_errors,
                               feedback=feedback)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
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
