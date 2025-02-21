import sys
import csv
import os
from openai import OpenAI
from pdfminer.high_level import extract_text
from dotenv import load_dotenv
import pdfplumber

# !/usr/bin/env python3

def extract_pdf_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    # print(text)
    return text

def extract_pdf_text_with_pdfminer(pdf_path):
    try:
        text = extract_text(pdf_path)
        # print(text)
        return text
    except Exception as e:
        print("Error extracting text from PDF:", e)
        sys.exit(1)

def analyze_report_card(pdf_text):
    prompt = f"""You are an expert educational counselor. Based on the following high school report card data, extract as much detail as possible about the student's academic strengths, extracurricular interests, and any hints about future course preferences. Then summarize your findings by listing up to ten relevant keywords or topics (comma separated).

Report Card:
\"\"\"{pdf_text}\"\"\"

Response:"""
    try:
        client = OpenAI()

        response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": "Extract up to ten keywords from a high school report card text that summarize the student's academic strengths, extracurricular interests, and potential future course preferences. \n\n# Steps\n\n1. **Analyze the Report Card:** \n   - Read through the provided report card text.\n   - Identify sections related to academic performance, extracurricular activities, and any notes on future interests or recommendations.\n\n2. **Identify Key Details:**\n   - Look for patterns or repeated themes in subjects where the student excels.\n   - Note any clubs, sports, or activities mentioned that the student actively participates in.\n   - Recognize any stated interests in specific academic or career fields.\n\n3. **Generate Keywords:**\n   - Based on the analysis, derive up to ten keywords that reflect the student's strengths, interests, and potential academic directions.\n   - Ensure the keywords encompass all three categories: academic, extracurricular, and future preferences.\n\n4. **Present the Findings:**\n   - List the generated keywords in a comma-separated format.\n\n# Output Format\n\nThe output should be a single string of up to ten keywords, separated by commas. Ensure the keywords reflect the student's academic strengths, extracurricular interests, and future course preferences. \n\n# Notes\n\n- Focus on concise and representative keywords.\n- Consider both explicit mentions and implicit signals in the report card.\n- Ensure the list of keywords is balanced across the different aspects (academic, extracurricular, future interests)."
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                }
            ]
            }
        ],
        response_format={
            "type": "text"
        },
        temperature=0.5,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        reply = response.choices[0].message.content.strip()
        if ',' in reply:
            keywords = [word.strip() for word in reply.split(',')]
        else:
            print("Unexpected format in OpenAI API response:", reply)
            sys.exit(1)
        return keywords
        # return ['Programming', 'Calculus', 'Economics', 'Business Fundamentals', 'Software Engineering', 'Machine Learning', 'Information Systems', 'Algorithms', "Dean's List", 'Commerce']
    except Exception as e:
        print("Error during OpenAI API call:", e)
        sys.exit(1)

def load_courses(csv_path):
    courses = []
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=["program_name", "location", "duration", "description"])
            next(reader)
            for row in reader:
                # print(row)
                courses.append(row)
        return courses
    except Exception as e:
        print("Error reading CSV file:", e)
        sys.exit(1)

def score_course(course, keywords):
    score = 0
    description = course["description"].lower()
    for kw in keywords:
        if kw.lower() in description:
            score += 1
    print(course["program_name"], score)
    return score

def recommend_courses(courses, keywords, top_n=5):
    scored_courses = []
    for course in courses:
        course_score = score_course(course, keywords)
        scored_courses.append((course_score, course))
        
    scored_courses.sort(key=lambda x: x[0], reverse=True)
    
    recommendations = [course for score, course in scored_courses if score > 0]
    if len(recommendations) < top_n:
        recommendations = [course for score, course in scored_courses][:top_n]
    else:
        recommendations = recommendations[:top_n]
    return recommendations

def main():
    if len(sys.argv) != 3:
        print("Usage: python rc_recommender.py <report_card.pdf> <courses.csv>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    csv_path = sys.argv[2]

    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    OpenAI.api_key = os.getenv("OPENAI_API_KEY")
    if not OpenAI.api_key:
        print("Error: Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    print("Extracting text from report card...")
    pdf_text = extract_pdf_text(pdf_path)
    
    print("Analyzing report card for interests...")
    keywords = analyze_report_card(pdf_text)
    print("Identified keywords/topics:", keywords)
    
    print("Loading courses data from CSV...")
    courses = load_courses(csv_path)
    
    print("Scoring courses based on identified interests...")
    recommendations = recommend_courses(courses, keywords, top_n=5)
    
    print("\nRecommended University Courses:")
    for course in recommendations:
        print(f"Program: {course['program_name']}")
        print(f"Location: {course['location']}")
        print(f"Duration: {course['duration']}")
        print(f"Description: {course['description']}")
        print("-" * 40)

if __name__ == "__main__":
    main()