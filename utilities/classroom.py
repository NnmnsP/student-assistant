from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import BatchHttpRequest
from . import color, logger
Color = color.Color()
Logger = logger.Logger()

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.rosters',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/classroom.profile.emails',
    'https://www.googleapis.com/auth/classroom.profile.photos',
    'https://www.googleapis.com/auth/classroom.coursework.me'
]


class ClassroomHelper:
    classroom = None

    def __init__(self, classroom):
        self.classroom = classroom

    def getCourses(self):
        if 'courses' in globals():
            return

        results = self.classroom.service.courses().list(pageSize=100).execute()
        global courses
        courses = results.get('courses', [])

    def listCourses(self):
        self.getCourses()

        res = []

        if not courses:
            Logger.error('No courses found!')
        else:
            res.append("Courses: (" + str(courses.__len__()) + ")")
            for course in courses:
                res.append(course['name'])
                
                # print(course['name'])
            return "\n".join(res)

    def listAssignmentsBatch(self):
        global courseWork
        courseWork = []

        global submissions
        submissions = []

        def courseWorkCallback(request_id, response, exception):
            if exception is not None:
                Logger.error('Error getting course: "{0}" {1}'.format(
                    request_id, exception))
            else:
                courseWork.append(response)

        def submissionsCallback(request_id, response, exception):
            if exception is not None:
                Logger.error('Error getting submission: "{0}" {1}'.format(
                    request_id, exception))
            else:
                submissions.append(response)

        self.getCourses()

        # Get courseWork
        courseWorkBatch = self.classroom.service.new_batch_http_request(
            callback=courseWorkCallback)
        for course in courses:
            if 'ARCHIVED' not in course['courseState']:
                request = self.classroom.service.courses(
                ).courseWork().list(courseId=course['id'])
                courseWorkBatch.add(request, request_id=course['id'])

        courseWorkBatch.execute()

        submissionsBatch = self.classroom.service.new_batch_http_request(
            callback=submissionsCallback)
        for work in courseWork:
            assignmentList = work.get('courseWork')

            if not assignmentList:
                return "No assignments due!"

            # Get submisions
            for assignment in assignmentList:
                request = self.classroom.service.courses().courseWork().studentSubmissions(
                ).list(courseId=assignment['courseId'], courseWorkId=assignment['id'])
                submissionsBatch.add(request, request_id=assignment['id'])

        submissionsBatch.execute()

        dueAssignments = []
        for submission in submissions:
            submission = submission.get('studentSubmissions')[0]
            if submission.get('courseWorkType') == 'ASSIGNMENT':
                if submission.get('state') != 'TURNED_IN' and submission.get('state') != 'RETURNED':
                    dueAssignments.append(submission)

        if dueAssignments == []:
            return "No assignments due!"
        else:
            courseWork.append("Assignments: ")
            for submission in dueAssignments:
                for coursework in courseWork:
                    if coursework.get('courseWork')[0].get('id') == submission.get("courseWorkId"):
                        desc = ""
                        if len(coursework.get('courseWork')[0].get('description').split('\n')[0]) > 100:
                            desc = coursework.get('courseWork')[0].get(
                                'description').split('\n')[0][0:100] + "..."
                        else:
                            desc = coursework.get('courseWork')[0].get(
                                'description').split('\n')[0]

                        courseWork.append("* " + coursework.get('courseWork')[0].get(
                            'title') + " (" + coursework.get('courseWork')[0].get('id') + ")")
                        courseWork.append("  " + desc)

            courseWork.append("Due: " + str(dueAssignments.__len__()))


class Classroom:
    service = None

    def initialize(self):
        creds = None

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('classroom', 'v1', credentials=creds)