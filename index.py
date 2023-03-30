from utilities import color, classroom, logger

Classroom = classroom.Classroom()
ClassroomHelper = classroom.ClassroomHelper(classroom=Classroom)
Color = color.Color()
Logger = logger.Logger()


def help():
    Logger.notice("Student Assistant")
    print("h (help) | Displays this menu\nlc (listcourses) | Lists courses that you are enrolled in\nla (listassignments) | Lists assignments that are due to be turned in\nexit (stop, x) | Closes the application")


def menu():
    parseCommand(input(Color.BLUE + "> " + Color.END))


def parseCommand(command):
    if command in ("h", "help"):
        help()
    elif command in ("lc", "listcourses"):
        ClassroomHelper.listCourses()
    elif command in ("la", "listassignments"):
        ClassroomHelper.listAssignmentsBatch()
    elif command in ("x", "exit", "stop"):
        exit(0)
    else:
        Logger.error("Unknown command!")

    menu()


if __name__ == '__main__':
    Classroom.initialize()

    # pylint: disable=no-member
    student = Classroom.service.userProfiles().get(userId="me").execute()
    name = student.get("name").get("fullName")

    Logger.success(Color.BOLD + "You are logged in as " + name)
    Logger.info("Type a command or use 'h' or 'help' for help")

    menu()
