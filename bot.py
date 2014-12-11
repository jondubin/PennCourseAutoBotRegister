from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import requests
import json

from ghost import Ghost
ghost = Ghost()

app = Flask(__name__)
app.config.from_object('config')
Bootstrap(app)

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


def get_courses_for_dept(dept):
    number_of_pages = get_page_numbers_for_dept(dept)
    for page in range(1, number_of_pages + 1):
        api_return = get_dept_for_page_number(dept, page)
        for course in api_return["result_data"]:
            course_title = course["course_title"]
            instructor_block = course["instructors"]
            activity = course["activity"]
            #print json.dumps(instructor_block)
            #course_instructor = instructor_block["name"]
            #section_id = instructor_block["section_id"]
            print course_title
            print activity
            #print course_instructor
            #print section_id
            #print json.dumps(course)
            #return json.dumps(api_return)


# one-time function to create courses json file
def create_courses_json():
    courses = open('static/courses.json', 'w')
    departments = get_departments_list()
    # for dept in departments:
    #     dept_courses = get_courses_for_dept(dept)
    #     print dept_courses
    return get_courses_for_dept("MATH")
    courses.close


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


@app.route('/')
def index():
    # form =
    # json_content = r.json()
    # return get_closed_status('ECON211001')
    #return json.dumps(json_content)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

# ghost.open('https://pennintouch.apps.upenn.edu/pennInTouch/jsp/fast.do')
# ghost.set_field_value('#password', '6174Kaprekar')
# ghost.set_field_value('#pennkey', 'dubinj')

# ghost.fire_on("form", "submit", expect_loading=True)
# ghost.click(".fastMenuLevel2Ul:first a:eq(3)")
# ghost.capture_to('header.png')


# class MyTest(GhostTestCase):
#      display = True
