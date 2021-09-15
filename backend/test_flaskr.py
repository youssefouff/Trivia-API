import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        #Sample Question
        self.new_question = {
            'question': 'Which is the most populated city in the world?',
            'answer': 'Tokyo',
            'difficulty': 2,
            'category': 3
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #test GET categories
    def test_get_categories(self):
        #getting response and loading data
        response = self.client().get('/categories')
        data = json.loads(response.data)
        #checking status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'],True)

    #test GET questions
    def test_get_questions(self):
        #getting response and loading data
        response = self.client().get('/questions')
        data = json.loads(response.data)
        #checking status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'],True)
        #checking that total_questions & questions return data
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    #test GET questions with wrong parameter (failure 404)
    def test_get_questions_failure(self):
       #getting response and loading data
        response = self.client().get('/questions?page=999')
        data = json.loads(response.data)
        #checking status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'],False)

    #test DELETE a questions with any existing id
    def test_delete_questions(self):
        response = self.client().delete('/questions/5')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
    
    #test DELETE a question with a non-existing id (failure)
    def test_delete_question_failure(self):
        response = self.client().delete('/questions/3670')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

    #test CREATE questions 
    def test_create_questions(self):
        #creating response and loading data
        response = self.client().post('/questions')
        data = json.loads(response.data)
        #checking status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'],True)

    #test failure of CREATE questions
    def test_create_question_failure(self):
        response = self.client().post('/questions/50', json=self.new_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    #test SEARCH with results
    def test_search_with_results(self):
        response = self.client().post('/questions', json={'searchTerm': 'invented'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    
    #test SERACH with no resluts
    def test_search_with_no_results(self):
        response = self.client().post('/questions', json={'searchTerm':'asdf'})
        data = json.loads(response.data)
        self.assertEqual(data['total_questions'],0)
        self.assertEqual(data['success'], True)
    
    #test GET questions by category
    def test_get_quest_by_cat(self):
        response = self.client().get('/categories/6/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['current_category'], 'Sports')
        self.assertEqual(data['success'], True)

    #test failure of getting questions by category
    def test_get_quest_by_cat_failure(self):
        response = self.client().get('/categories/100/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)
    
    #test playing quiz
    def test_play_quiz(self):
        quiz_round = {'previous_questions': [], 'quiz_category': {'type': 'Sports', 'id': 8}}
        response = self.client().post('/play', json=quiz_round)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    #test playing quiz failure
    def test_play_quiz_failure(self):
        response = self.client().post('/play', json={})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()