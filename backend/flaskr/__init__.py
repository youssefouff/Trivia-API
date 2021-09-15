import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

db = SQLAlchemy()


#Paginating questions
def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  
  CORS(app, resources={'/':{'origins': '*'}})
  
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
      response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, PATCH, DELETE, OPTIONS')
      return response
  
  
  #Handling GET requests for all available categories
  @app.route("/categories", methods=['GET'])
  def get_all_available_categories():
    if request.method == "GET":
      categories = Category.query.order_by(Category.id).all()
      cat =  {}

      for category in categories:
        cat[category.id] = category.id
      
      #if there is no categories found, abort 404
      if (len(cat) == 0):
        abort(404)

      return jsonify({
        'categories': cat,
        'success': True
      })
  
  
  #Handling GET request for getting all questions
  @app.route('/questions', methods=['GET'])
  def get_questions():
      #get questions and paginate them
      if request.method == "GET":
         questions = Question.query.all()
         total_questions = len(questions)
         paginated_questions = paginate_questions(request, questions)
         
         #if there is no questions, abort 404
         if(len(paginated_questions) == 0):
            abort(404)
            
         categories = Category.query.all()
         cat = {}

         for category in categories:
            cat[category.id] = category.type

         return jsonify({
            'success': True,
            'total_questions': total_questions,
            'categories': cat,
            'questions': paginated_questions
            })
  
  #Handling DELETE requests for deleting a questions by ID
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
     if request.method == "DELETE":
         #get question by its ID
         question = Question.query.filter_by(id=id).one_or_none()
         
         #if no questions found, abort 404
         if question is None:
              abort(404)
         
         #delete questions
         question.delete()
         
         #return success response
         return jsonify({
              'deleted': id,
              'success': True,
              'total_questions': len(Question.query.all())
            })
 
  #Handling POST method to get questions based on a search term 
  @app.route('/questions', methods=['POST'])
  def create_a_question():
      if request.method == "POST":
          body = request.get_json()
          question = body.get('question', None)
          answer = body.get('answer', None)
          difficulty = body.get('difficulty', None)
          category = body.get('category',  None)      
          searchTerm = body.get('searchTerm', None)
          
          try:
              if searchTerm:
                  questions = Question.query.filter(Question.question.ilike(f"%{searchTerm}%")).all()
                  paginated_questions = paginate_questions(request, questions)
                    
                  return jsonify({
                        'success': True,
                        'questions': paginated_questions,
                        'total_questions': len(paginated_questions)
                    })

              else:
                  q = Question(question=question, answer=answer, difficulty=difficulty, category=category)
                  q.insert()

                  questions = Question.query.order_by(Question.id).all()
                  paginated_questions = paginate_questions(request, questions)

                  return jsonify({
                        'success': True,
                        'question_created': q.question,
                        'created': q.id,
                        'questions': paginated_questions,
                        'total_questions': len(Question.query.all())
                    })
          except:
              abort(422)
    

  #Handling GET request tp get questions based on category
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
      if request.method == "GET":
          #get category by its ID
          category = Category.query.filter_by(id=category_id).one_or_none()
          
          #if no categories found
          if category is None:
               abort(404)
          
          #get matching questions and paginate them
          try:
              questions = Question.query.filter_by(category=category.id).all()
              paginated_questions = paginate_questions(request, questions)

              return jsonify({
                  'success': True,
                  'total_questions': len(Question.query.all()),
                  'current_category': category.type,
                  'questions': paginated_questions
                })

          except:
              abort(400)
  
  #Hanling POST requests for playing quiz
  @app.route('/play', methods=['POST'])
  def play_game():
      if request.method == "POST":
         try:
            #load the request body
            body = request.get_json()
            #get the previous questions
            previous_questions = body.get('previous_questions', None)
            #get the cateegory
            category = body.get('quiz_category', None)

            category_id = category['id']
            next_question = None

            #load questions for a given category     
            if category_id != 0:
               q = Question.query.filter_by(category=category_id).filter(Question.id.notin_((previous_questions))).all()    
            #load all questions if 'ALL' is selected
            else:
               q = Question.query.filter(Question.id.notin_((previous_questions))).all()
                
            if len(q) > 0:
                next_question = random.choice(q).format()
                
            return jsonify({
                'question': next_question,
                'success': True,
                })
         except:
             abort(422)

 
  @app.errorhandler(400)
  def bad_request_error(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404
    
  @app.errorhandler(405)
  def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

  @app.errorhandler(422)
  def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 422


  return app

    