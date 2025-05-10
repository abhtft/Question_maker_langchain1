# Preparing a class to find the maximum marks from a list of students, where data is provided as a dictionary of names and marks.

class StudentMarks:
    def __init__(self, marks_dict):
        """
        Initialize the class with a dictionary of student names and their marks.
        :param marks_dict: Dictionary where keys are student names and values are their marks.
        """
        self.marks_dict = marks_dict

    def find_max_marks(self):
        """
        Find the student with the maximum marks.
        :return: A tuple containing the name of the student and their marks.
        """
        if not self.marks_dict:
            return None, None  # Return None if the dictionary is empty

        max_student = max(self.marks_dict, key=self.marks_dict.get)
        max_marks = self.marks_dict[max_student]
        return max_student, max_marks


# Example usage
marks = {
    "Alice": 85,
    "Bob": 92,
    "Charlie": 78,
    "Diana": 95
}

student_marks = StudentMarks(marks)
top_student, top_marks = student_marks.find_max_marks()

if top_student:
    print(f"The student with the highest marks is {top_student} with {top_marks} marks.")
else:
    print("No data available.")


