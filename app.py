from flask import Flask, request, render_template, redirect, url_for, session
import secrets
import datetime
import pytz
from flask import send_from_directory, abort
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import traceback

# Define the scope and credentials
scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)
sheet_key = '10KQWCUQtnT9d90GyEqilKSAVH-0h25ygir4ZQwc_fKE'

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe()

success_token = secrets.token_urlsafe()
timezone = pytz.timezone('UTC')
end_time = datetime.datetime.now(timezone) + datetime.timedelta(minutes=10085)

questions = [
    {"id": 1, "question": "Reverse a String", "function_name": "reverse_string"},
    {"id": 2, "question": "Remove Vowels from a String", "function_name": "remove_vowels"},
    {"id": 3, "question": "Find the Largest Number in a List", "function_name": "find_largest"},
    {"id": 4, "question": "Check for Palindrome", "function_name": "is_palindrome"},
    {"id": 5, "question": "Sum of a List", "function_name": "sum_list"},
    {"id": 6, "question": "Implement Binary Search", "function_name": "binary_search"},
    {"id": 7, "question": "Implement Merge Sort", "function_name": "merge_sort"},
    {"id": 8, "question": "Find the nth Fibonacci Number", "function_name": "fibonacci"},
    {"id": 9, "question": "Check if a Number is Prime", "function_name": "is_prime"},
    {"id": 10, "question": "Find the Longest Common Prefix of an Array of Strings", "function_name": "longest_common_prefix"},
    {"id": 11, "question": "Find the First Unique Character in a String", "function_name": "first_unique_char"},
    {"id": 12, "question": "Check if Two Strings are Anagrams", "function_name": "is_anagram"},
    {"id": 13, "question": "Count the Number of Islands in a 2D Matrix", "function_name": "num_islands"},
    {"id": 14, "question": "Find the Longest Increasing Subsequence", "function_name": "longest_increasing_subsequence"},
    {"id": 15, "question": "Find the Minimum Window Substring", "function_name": "min_window_substring"},
    {"id": 16, "question": "Group Anagrams Together", "function_name": "group_anagrams"},
    {"id": 17, "question": "Rotate a Matrix 90 Degrees", "function_name": "rotate_matrix"},
]

test_cases = {
    "reverse_string": [("Hello",), "olleH"],
    "remove_vowels": [("Programming",), "Prgrmmng"],
    "find_largest": [([1, 2, 3, 4, 5],), 5],
    "is_palindrome": [("racecar",), True],
    "sum_list": [([1, 2, 3, 4, 5],), 15],
    "binary_search": [([1, 2, 3, 4, 5], 3), 2],
    "merge_sort": [([3, 1, 4, 1, 5, 9, 2],), [1, 1, 2, 3, 4, 5, 9]],
    "fibonacci": [(10,), 55],
    "is_prime": [(29,), True],
    "longest_common_prefix": [(["flower", "flow", "flight"],), "fl"],
    "first_unique_char": [("loveleetcode",), 2],
    "is_anagram": [("anagram", "nagaram"), True],
    "longest_increasing_subsequence": [([10, 9, 2, 5, 3, 7, 101, 18],), 4],
    "min_window_substring": [("ADOBECODEBANC", "ABC"), "BANC"],
    "group_anagrams": [(["eat", "tea", "tan", "ate", "nat", "bat"],), [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]],
    "rotate_matrix": [([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [[7, 4, 1], [8, 5, 2], [9, 6, 3]]]
}

def evaluate_answer(function_name, code, test_case):
    try:
        exec(code)
        func = locals()[function_name]
        if func(*test_case[0]) == test_case[1]:
            return True
    except Exception as e:
        print(f"Error evaluating answer: {e}")
    return False

@app.route('/')
def index():
    progress = session.get('progress', {})
    return render_template('index.html', questions=questions, end_time=end_time.isoformat(), progress=progress)

@app.route('/submit', methods=['POST'])
def submit():
    score = 0
    progress = {}
    
    for question in questions:
        code = request.form.get(f'code_{question["id"]}')
        progress[question["id"]] = code
        if code:
            if evaluate_answer(question["function_name"], code, test_cases[question["function_name"]]):
                score += 5
    
    session['progress'] = progress

    if score >= 100:
        return redirect(url_for('success', token=success_token))
    else:
        return redirect(url_for('failure'))

@app.route('/success/<token>')
def success(token):
    if token == success_token:
        return render_template('success.html')
    else:
        return redirect(url_for('failure'))

@app.route('/failure')
def failure():
    return render_template('failure.html')

@app.route('/record_alias', methods=['POST'])
def record_alias():
    hacker_name = request.form['hacker_name']

    try:
        print(f"Received hacker name: {hacker_name}")
        print("Attempting to open Google Sheet with key:", sheet_key)
        sheet = client.open_by_key(sheet_key).sheet1
        print("Google Sheet opened successfully")
        
        print("Appending row to Google Sheet")
        sheet.append_row([hacker_name, datetime.datetime.now().isoformat()])
        print("Row appended successfully")
    except gspread.exceptions.APIError as e:
        print(f"Google Sheets API error: {e.response.json()}")
    except Exception as e:
        print(f"General error: {e}")
        traceback.print_exc()

    return redirect(url_for('download_instructions'))

@app.route('/download_instructions')
def download_instructions():
    try:
        return send_from_directory('static/assets', 'instructions.pdf', as_attachment=True)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
