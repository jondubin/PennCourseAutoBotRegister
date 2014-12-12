from flask import Flask, render_template, request
import requests
import json
import time
import re
from bs4 import BeautifulSoup

from ghost import Ghost
ghost = Ghost(wait_timeout=25, display=True)


app = Flask(__name__)
app.config.from_object('config')

AUTH_TOKEN = app.config["AUTH_TOKEN"]
AUTH_BEARER = app.config["AUTH_BEARER"]


def api_request(search_url, params=""):
    base_url = "https://esb.isc-seo.upenn.edu/8091/open_data/"
    url = "{}{}{}".format(base_url, search_url, params)
    headers = {"Authorization-Bearer": AUTH_BEARER,
           "Authorization-Token": AUTH_TOKEN,
           "Content-Type": "application/json; charset=utf-8"}
    r = requests.get(url, headers=headers)
    return r.json()


def get_departments_list():
    search_url = "course_section_search_parameters"
    json_content = api_request(search_url)
    dept_json = json_content["result_data"][0]["departments_map"]
    departments = [dept for dept in dept_json]
    return departments


def get_page_numbers_for_dept(dept):
    search_url = "course_section_search"
    params = "?course_id={}".format(dept)
    api_return = api_request(search_url, params)
    meta = api_return["service_meta"]
    number_of_pages = meta["number_of_pages"]
    return number_of_pages


def get_dept_for_page_number(dept, page_number):
    search_url = "course_section_search"
    params = "?course_id={}&page_number={}".format(dept, page_number)
    api_return = api_request(search_url, params)
    return api_return


def get_courses_for_dept(json_obj, dept):
    number_of_pages = get_page_numbers_for_dept(dept)
    for page in range(1, number_of_pages + 1):
        api_return = get_dept_for_page_number(dept, page)
        for course in api_return["result_data"]:
            title = course["course_title"]
            instructor_block = course["instructors"]
            activity = course["activity"]
            if activity == "LEC":
                activity = "Lecture"
            elif activity == "REC":
                activity = "Recitation"
            elif activity == "LAB":
                activity = "Laboratory"
            elif activity == "IND":
                activity = "Indepdent Study"
            elif activity == "SEM":
                activity = "Seminar"
            elif activity == "SRT":
                activity = "Senior Thesis"
            elif activity == "STU":
                activity = "Studio"
            elif activity == "CLN":
                activity = "CLINIC"
            elif activity == "PRC":
                activity = "SCUE Preceptorial"
            elif activity == "PRO":
                activity = "NSO Proseminar"
            recitations = course["recitations"]
            labs = course["labs"]
            try:
                if recitations:
                    for recitation in recitations:
                        course_id = recitation["course_id"]
                        section_id = recitation["section_id"]
                        subject = recitation["subject"]
                        course_section_id = subject + course_id + section_id
                        add_course_to_json(json_obj, dept, title, "Recitation",
                                           course_section_id)
                if labs:
                    for lab in labs:
                        course_id = lab["course_id"]
                        section_id = lab["section_id"]
                        subject = lab["subject"]
                        course_section_id = subject + course_id + section_id
                        add_course_to_json(json_obj, dept, title, "Laboratory",
                                           course_section_id)
                instructor = instructor_block[0]["name"]
                course_section_id = instructor_block[0]["section_id"]
                add_course_to_json(json_obj, dept, title, activity,
                                   course_section_id, instructor)
            except:
                pass


def add_course_to_json(obj, dept, title, activity, full_id, instructor=""):
    full_id = full_id.replace(" ", "")
    m = re.search("\d", full_id)
    n = m.start()  # first number position
    section_dept = full_id[0:n]
    course_id = full_id[n:n+3]
    section_id = full_id[n+3:n+6]
    final_id = "{} {} {}".format(section_dept, course_id, section_id)
    #  dict_obj = {"label": final_id, "value": full_id}
    obj.append(final_id)
    # print dept
    # if instructor:
    #     print instructor
    # print title
    # print activity
    # print full_id
    # print "=================="


# one-time function to create courses json file
def create_courses_json():
    json_obj = []
    departments = get_departments_list()
    for dept in departments:
        get_courses_for_dept(json_obj, dept)
    with open("static/courses.json", "w") as outfile:
        json.dump(list(set(json_obj)), outfile, indent=4)


@app.route('/closed_status', methods=['GET'])
def get_closed_status():
    courseid = request.args.get('courseid')
    base_url = "https://esb.isc-seo.upenn.edu/8091/open_data/"
    search_url = "course_section_search"
    url = "{}{}?course_id={}".format(base_url, search_url, courseid)
    headers = {"Authorization-Bearer": AUTH_BEARER,
           "Authorization-Token": AUTH_TOKEN,
           "Content-Type": "application/json; charset=utf-8"}
    r = requests.get(url, headers=headers)
    json_content = r.json()
    try:
        closed_status = json_content["result_data"][0]["course_status_normalized"]
        return json.dumps(closed_status).strip('"')
    except:
        return ""


@app.route('/signup', methods=['POST'])
def sign_up_for_class():
    return "yo"


def intouch_signup(username, password, subject, course, section):
    ghost.open('https://pennintouch.apps.upenn.edu/pennInTouch/jsp/fast.do')
    ghost.wait_for_selector('#password')
    ghost.set_field_value('#password', password)
    ghost.set_field_value('#pennkey', username)
    ghost.fire_on("form", "submit", expect_loading=True)
    ghost.wait_for_selector('.fastMenuLevel2')
    html_content = ghost.content
    js_function = find_register_function(html_content)
    ghost.evaluate(js_function, expect_loading=True)
    ghost.wait_for_page_loaded()
    registration_content = ghost.content
    subject_id = find_subject_id(registration_content, 0)
    course_id = find_subject_id(registration_content, 1)
    section_id = find_subject_id(registration_content, 2)

    set_dropdown(subject_id, subject)
    on_change = "fastElementChange(event, null, null, 'courseEnrollmentForm', false, null, 'subjectPrimary', 'onchange', false, true, this);"
    on_course_change = "fastElementChange(event, null, null, 'courseEnrollmentForm', false, null, 'courseNumberPrimary', 'onchange', false, true, this);"
    ghost.evaluate(on_change)
    process_ghost()
    set_dropdown(course_id, course)
    ghost.evaluate(on_course_change)
    process_ghost()
    set_dropdown(section_id, section)
    process_ghost()
    ghost.wait_for_text("Add request")
    request_function = find_request_function(ghost.content)
    print request_function
    ghost.evaluate(request_function)
    ghost.capture_to('static/registration_complete.png')


def find_request_function(html_content):
    soup = BeautifulSoup(html_content)
    add_request = soup.findAll(text=re.compile('Add request'), limit=1)[0]
    request_function = add_request.parent.parent['onclick'][7:]
    return request_function


def find_register_function(html_content):
    soup = BeautifulSoup(html_content)
    element = soup.body.ul.li.ul.contents[7].a
    js_function = element['onclick'][7:]  # remove "return" from string
    return js_function


def find_subject_id(html_content, select_idx):
    soup = BeautifulSoup(html_content)
    select = soup.find_all('select')
    return select[select_idx]['id']


def set_dropdown(dropdown_id, value):
    subject_selector = (("document.getElementById('{}').value = '{}'")
                        .format(dropdown_id, value))
    print subject_selector
    ghost.evaluate(subject_selector)


def process_ghost():
    ghost._app.processEvents()
    time.sleep(1)
    ghost._app.processEvents()
    time.sleep(1)
    ghost._app.processEvents()
    time.sleep(1)
    ghost._app.processEvents()
    time.sleep(1)


@app.route('/')
def index():
    # form =
    # json_content = r.json()
    # return get_closed_status('ECON211001')
    #return json.dumps(json_content)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
