"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 20:56:59 
 * @Last Modified by: ThaumicMekanism [Stephan K.]
 * @Last Modified time: 2020-01-23 21:00:23
 */
"""
from flask import Flask, request, send_from_directory, render_template
import argparse
import json

results_file = None
# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='', template_folder='template')

@app.route("/")
def ag():
    with open(results_file, "r") as f:
        ag_json = json.load(f)
        
    autograder_output = ag_json.get("output")
    tests = ag_json["tests"]
    test_cases_body = ""
    passed_tests = []
    failed_tests = []
    set_score = False
    s = 0
    for test in tests:
        score = test.get("score")
        max_score = test.get("max_score")
        title = test.get("name")
        passed = False
        if score is not None:
            set_score = True
            s += float(score)
            if max_score is None:
                status = "testCase-passed"
                t = title
                title += f" ({score})"
                passed_tests.append((t, title))
                passed = True
            elif float(score) >= float(max_score):
                status = "testCase-passed"
                t = title
                title += f" ({score}/{max_score})"
                passed_tests.append((t, title))
                passed = True
            else:
                status = "testCase-failed"
                t = title
                title += f" ({score}/{max_score})"
                failed_tests.append((t, title))
        else:
            status = ""
        test_cases_body += render_template("testCase.html", test_title=test.get("name"), test_title_score=title, test_body=test.get("output"), test_case_status=status)
    sidebar = ""
    if failed_tests:
        sidebar += render_template("testSidebar.html", title="Failed Tests", tests=failed_tests, passfail="failed")
    if passed_tests:
        sidebar += render_template("testSidebar.html", title="Passed Tests", tests=passed_tests, passfail="passed")
    if not set_score:
        s = float(ag_json.get("score"))
    return render_template("submission.html", name="TEST", score=s, out_of="?", test_cases_body=test_cases_body, autograder_output=autograder_output, test_cases_sidebar=sidebar)

@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('template/assets', path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("results_file")
    args = parser.parse_args()
    results_file = args.results_file
    app.run()