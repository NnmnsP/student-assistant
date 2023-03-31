from utilities import color, classroom, logger

Classroom = classroom.Classroom()
ClassroomHelper = classroom.ClassroomHelper(classroom=Classroom)
Color = color.Color()
Logger = logger.Logger()


def help():
    Logger.notice("Student Assistant")
    return "h (help) | Displays this menu\nlc (listcourses) | Lists courses that you are enrolled in\nla (listassignments) | Lists assignments that are due to be turned in"


def menu():
    parseCommand(input(Color.BLUE + "> " + Color.END))


def parseCommand(command):
    if command in ("h", "help"):
       return help()
    elif command in ("lc", "listcourses"):
        return ClassroomHelper.listCourses()
    elif command in ("la", "listassignments"):
        return ClassroomHelper.listAssignmentsBatch()
    else:
        Logger.error("Unknown command!")

    # menu()


def start_main():
    Classroom.initialize()

    # pylint: disable=no-member
    student = Classroom.service.userProfiles().get(userId="me").execute()
    name = student.get("name").get("fullName")

    Logger.success(Color.BOLD + "You are logged in as " + name)
    Logger.info("Type a command or use 'h' or 'help' for help")

    # menu()
