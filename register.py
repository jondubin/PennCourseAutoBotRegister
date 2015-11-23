import time
import re
from bs4 import BeautifulSoup
from ghost import Ghost
import argparse


def alert_when_finished(func):
    def new_f(*args):
        print "Started registration"
        func(*args)
        print "Finished registration"
    return new_f


@alert_when_finished
def register(username, password, subject, course, section, display_bool):
    """Wrapper for intouch_signup. Registers a user for a course"""
    ghost = Ghost(wait_timeout=25, display=display_bool)
    intouch_signup(ghost, username, password, subject, course, section)


def intouch_signup(ghost, username, password, subject, course, section):
    """Registers the user for the course on InTouch"""
    ghost.open('https://pennintouch.apps.upenn.edu/pennInTouch/jsp/fast.do')
    ghost.wait_for_selector('#password')
    ghost.set_field_value('#password', password)
    ghost.set_field_value('#pennkey', username)
    ghost.fire_on("form", "submit", expect_loading=True)
    ghost.wait_for_selector('.fastMenuLevel2')
    html_content = ghost.content
    js_function = find_register_function(html_content)
    print js_function
    ghost.evaluate(js_function, expect_loading=True)
    ghost.wait_for_page_loaded()
    registration_content = ghost.content
    subject_id = find_subject_id(registration_content, 0)
    course_id = find_subject_id(registration_content, 1)
    section_id = find_subject_id(registration_content, 2)
    set_dropdown(ghost, subject_id, subject)
    on_change = """fastElementChange(event, null, null, 'courseEnrollmentForm',
    false, null, 'subjectPrimary', 'onchange', false, true, this);"""
    on_course_change = """fastElementChange(event, null, null, 'courseEnrollmentForm',
    false, null, 'courseNumberPrimary', 'onchange', false, true, this);"""
    on_section_change = """fastElementChange(event, null, null, 'courseEnrollmentForm',
    false, null, 'sectionNumberPrimary', 'onchange', false, true, this);"""
    request_function = find_request_function(ghost.content)
    ghost.evaluate(on_change)
    process_ghost(ghost)
    set_dropdown(ghost, course_id, course)
    ghost.evaluate(on_course_change)
    process_ghost(ghost)
    set_dropdown(ghost, section_id, section)
    ghost.evaluate(on_section_change)
    process_ghost(ghost)
    try:
        ghost.evaluate(request_function, expect_loading=True)
    except:
        pass
    process_ghost(ghost)
    ghost.capture_to('static/registration_complete.png')


def find_request_function(html_content):
    """Uses BeautifulSoup to find the 'request' JavaScript function"""
    soup = BeautifulSoup(html_content)
    add_request = soup.findAll(text=re.compile('Add request'), limit=1)[0]
    request_function = add_request.parent.parent['onclick'][7:]
    return request_function


def find_register_function(html_content):
    """Uses BeautifulSoup to find the 'register' JavaScript function"""
    soup = BeautifulSoup(html_content)
    element = soup.body.ul.li.ul.contents[7].a
    js_function = element['onclick'][7:]
    return js_function


def find_subject_id(html_content, select_idx):
    """Find the id selector for a course subject"""
    soup = BeautifulSoup(html_content)
    select = soup.find_all('select')
    return select[select_idx]['id']


def set_dropdown(ghost, dropdown_id, value):
    """Set a dropdown to a value"""
    subject_selector = (("document.getElementById('{}').value = '{}'")
                        .format(dropdown_id, value))
    ghost.evaluate(subject_selector)


def process_ghost(ghost):
    """Process the current Ghost environment additional steps"""
    ghost._app.processEvents()
    time.sleep(1)
    ghost._app.processEvents()
    time.sleep(1)
    ghost._app.processEvents()
    time.sleep(1)
    ghost._app.processEvents()
    time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Register for a class')
    parser.add_argument("--display", action='store_true')
    parser.add_argument("username")
    parser.add_argument("password")
    parser.add_argument("subject")
    parser.add_argument("course")
    parser.add_argument("section")
    args = parser.parse_args()
    if args.display:
        display_bool = True
    else:
        display_bool = False
    register(args.username, args.password, args.subject, args.course,
             args.section, display_bool)
