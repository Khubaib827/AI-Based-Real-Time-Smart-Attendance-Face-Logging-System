import re

class Validator:
    @staticmethod
    def validate_student_id(student_id):
        if not student_id:
            return False, "Student ID is required"
        if not re.match(r'^STU\d{5}$', student_id):
            return False, "Format: STUXXXXX"
        return True, None