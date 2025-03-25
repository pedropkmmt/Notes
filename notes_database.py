import json
from datetime import datetime, timedelta

class NotesDatabase:
    def __init__(self):
        """
        Initialize a dummy database for notes with some sample content
        to simulate a real-world note-taking application.
        """
        self.notes = [
            {
                "id": 0,
                "title": "Machine Learning Basics",
                "content": """Machine Learning Overview:
1. Definition: Machine learning is a subset of AI that enables systems to learn and improve from experience.

Key Types of Machine Learning:
- Supervised Learning: Model learns from labeled training data
  * Examples: Classification, Regression
- Unsupervised Learning: Model finds patterns in unlabeled data
  * Examples: Clustering, Dimensionality Reduction
- Reinforcement Learning: Agent learns by interacting with environment

Common Algorithms:
* Linear Regression
* Decision Trees
* Neural Networks
* Support Vector Machines
* K-Means Clustering""",
                "created": datetime.now().timestamp() - timedelta(days=5).total_seconds(),
                "last_edited": datetime.now().timestamp() - timedelta(days=2).total_seconds()
            },
            {
                "id": 1,
                "title": "Python Programming Cheatsheet",
                "content": """Python Essentials:
1. Data Types
- Integers: whole numbers (int)
- Floats: decimal numbers (float)
- Strings: text data (str)
- Lists: ordered, mutable collections []
- Dictionaries: key-value pairs {}

2. Basic Operations
* Arithmetic: +, -, *, /, //, %
* Comparison: ==, !=, <, >, <=, >=
* Logical: and, or, not

3. Control Flow
- if-elif-else statements
- for loops
- while loops
- list comprehensions

4. Functions
def function_name(parameters):
    # function body
    return value""",
                "created": datetime.now().timestamp() - timedelta(days=10).total_seconds(),
                "last_edited": datetime.now().timestamp() - timedelta(days=3).total_seconds()
            }
        ]
    
    def get_note_by_id(self, note_id):
        """Retrieve a note by its ID"""
        for note in self.notes:
            if note['id'] == note_id:
                return note
        return None
    
    def add_note(self, title="Untitled Document", content=""):
        """Add a new note to the database"""
        new_note = {
            "id": len(self.notes),
            "title": title,
            "content": content,
            "created": datetime.now().timestamp(),
            "last_edited": datetime.now().timestamp()
        }
        self.notes.append(new_note)
        return new_note
    
    def update_note(self, note_id, title=None, content=None):
        """Update an existing note"""
        for note in self.notes:
            if note['id'] == note_id:
                if title is not None:
                    note['title'] = title
                if content is not None:
                    note['content'] = content
                note['last_edited'] = datetime.now().timestamp()
                return note
        return None
    
    def search_notes(self, query):
        """Search notes by title or content"""
        return [
            note for note in self.notes 
            if query.lower() in note['title'].lower() or 
               query.lower() in note['content'].lower()
        ]
    
    def to_json(self, filename='notes_database.json'):
        """Export notes to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.notes, f, indent=4)
    
    @classmethod
    def from_json(cls, filename='notes_database.json'):
        """Import notes from a JSON file"""
        database = cls()
        try:
            with open(filename, 'r') as f:
                database.notes = json.load(f)
            return database
        except FileNotFoundError:
            return database