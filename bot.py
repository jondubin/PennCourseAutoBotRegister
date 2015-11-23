from flask import Flask, render_template, request
import requests
import json
import re
import os

app = Flask(__name__)
app.config.from_object('config')


class api:
    def __init__(self):
        self.AUTH_TOKEN = app.config["AUTH_TOKEN"]
        self.AUTH_BEARER = app.config["AUTH_BEARER"]

    def api_request(self, search_url, params=""):
        """Used to make all API request, returns JSON"""
        base_url = "https://esb.isc-seo.upenn.edu/8091/open_data/"
        url = "{}{}{}".format(base_url, search_url, params)
        headers = {"Authorization-Bearer": self.AUTH_BEARER,
                   "Authorization-Token": self.AUTH_TOKEN,
                   "Content-Type": "application/json; charset=utf-8"}
        r = requests.get(url, headers=headers)
        return r.json()

    def get_departments_list(self):
        """Gets a list of all the available departments"""
        search_url = "course_section_search_parameters"
        json_content = self.api_request(search_url)
        dept_json = json_content["result_data"][0]["departments_map"]
        departments = [dept for dept in dept_json]
        return departments

    def get_page_numbers_for_dept(self, dept):
        """Returns a list of how many pages we'll need to parse through"""
        search_url = "course_section_search"
        params = "?course_id={}".format(dept)
        api_return = self.api_request(search_url, params)
        meta = api_return["service_meta"]
        number_of_pages = meta["number_of_pages"]
        return number_of_pages

    def get_dept_for_page_number(self, dept, page_number):
        """For a given department and page number, query the page"""
        search_url = "course_section_search"
        params = "?course_id={}&page_number={}".format(dept, page_number)
        api_return = self.api_request(search_url, params)
        return api_return

    def get_courses_for_dept(self, json_obj, dept):
        """Get all courses for a department, page-by-page"""
        number_of_pages = self.get_page_numbers_for_dept(dept)
        for page in range(1, number_of_pages + 1):
            api_return = self.get_dept_for_page_number(dept, page)
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
                            sub = recitation["subject"]
                            course_section_id = sub + course_id + section_id
                            self.add_course_to_json(json_obj, dept,
                                                    title, "Recitation",
                                                    course_section_id)
                    if labs:
                        for lab in labs:
                            course_id = lab["course_id"]
                            section_id = lab["section_id"]
                            sub = lab["subject"]
                            course_section_id = sub + course_id + section_id
                            self.add_course_to_json(json_obj, dept, title,
                                                    "Laboratory",
                                                    course_section_id)
                    instructor = instructor_block[0]["name"]
                    course_section_id = instructor_block[0]["section_id"]
                    self.add_course_to_json(json_obj, dept, title, activity,
                                            course_section_id, instructor)
                except:
                    pass

    def add_course_to_json(self, obj, dept, title, activity, full_id,
                           instructor=""):
        """Adds a course to the JSON file"""
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


def create_courses_json():
    """Creates the json file for population the auto-complete"""
    json_obj = []
    api_search = api()
    departments = api_search.get_departments_list()
    for dept in departments:
        api_search.get_courses_for_dept(json_obj, dept)
    with open("static/courses.json", "w") as outfile:
        json.dump(list(set(json_obj)), outfile, indent=4)


@app.route('/closed_status', methods=['GET'])
def get_closed_status():
    """Returns whether a course is open or closed"""
    courseid = request.args.get('courseid')
    base_url = "https://esb.isc-seo.upenn.edu/8091/open_data/"
    search_url = "course_section_search"
    url = "{}{}?course_id={}".format(base_url, search_url, courseid)
    headers = {"Authorization-Bearer": app.config['AUTH_BEARER'],
               "Authorization-Token": app.config['AUTH_TOKEN'],
               "Content-Type": "application/json; charset=utf-8"}
    r = requests.get(url, headers=headers)
    json_data = r.json()
    try:
        closed_status = json_data["result_data"][0]["course_status_normalized"]
        return json.dumps(closed_status).strip('"')
    except:
        return ""


@app.route('/signup', methods=['POST'])
def sign_up_for_class():
    """Signs a user up for a class"""
    username = request.form['pennKey']
    course = request.form['course']
    course_list = course.split(' ')
    dept = course_list[0]
    course = course_list[1]
    sect = course_list[2]
    password = request.form['password']
    os.system(("python register.py {} {} {} {} {}").
              format(username, password, dept, course, sect))
    return render_template('signed_up.html')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
