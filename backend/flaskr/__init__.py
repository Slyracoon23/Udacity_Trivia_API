import os, sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

# must import sys path for models module
sys.path.insert(0,'..')
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  # set up CORS, allowing all origins
  CORS(app, resources={'/': {'origins': '*'}})


  @app.after_request
  def after_request(response):
    '''Sets access control'''
    response.headers.add('Access-Control-Alow-Headers',
                         'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response



  @app.route('/categories')
  def get_catergories():
    ''' Handles GET requests for getting all categories. '''

    # TODO: use try except

    categories_query = Category.query.order_by(Category.id).all()

    # TODO: add errorhandling

    formatted_categories = {category.id: category.type for category in categories_query}

    return jsonify({
      'success': True,
      'categories': formatted_categories
    })




  ''' 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
    ''' Handles GET requests for getting all questions '''

    # get all questions
    question_query = Question.query.all()
    formatted_questions = [question.format() for question in question_query]
    # TODO: add pagination

    # get all categoris
    categories_query = Category.query.all()

    formatted_categories = {category.id: category.type for category in categories_query}

    # return data to view
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(question_query),
      'categories': formatted_categories,
      'current_category' : None
        })

    """
     @TODO: 
     Create an endpoint to DELETE question using a question ID. 
  
     TEST: When you click the trash icon next to a question, the question will be removed.
     This removal will persist in the database and when you refresh the page. 
    """

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    error = False
    try:
      question_query = Question.query.filter_by(id=question_id).one_or_none()
      if question_query is None:
        abort(404)  # Question id does not exist
      question_query.delete()
    except:
      error = True
      print(sys.exc_info())
    finally:
      if error:
        abort(422)
      else:
        return jsonify({
          'success': True,
          'deleted': question_id
        })




  @app.route('/questions', methods=['POST'])
  def post_question():
    ''' Handles POST requests for creating new questions and searching questions. '''
    body = request.get_json()

    # if search term is present
    if body.get('searchTerm', None):
      return search_questions()
    else:
      return add_question()

  '''
   @TODO: 
   Create an endpoint to POST a new question, 
   which will require the question and answer text, 
   category, and difficulty score.

   TEST: When you submit a question on the "Add" tab, 
   the form will clear and the question will appear at the end of the last page
   of the questions list in the "List" tab.  
   '''


  def add_question():
    body = request.get_json()

    query_list = ['question', 'answer', 'category', 'difficulty']

    list_request = [body.get(query, None) for query in query_list]
    print(list_request)
    if all(list_request) is False:
      abort(422)

    try:
      question = Question(*list_request) # unpack values

      question.insert()

      return jsonify({
        'succes': True,
        'created': question.id
      })
    except:
      abort(422)


  # @TODO:
  # Create a POST endpoint to get questions based on a search term.
  # It should return any questions for whom the search term
  # is a substring of the question.
  #
  # TEST: Search by any phrase. The questions list will update to include
  # only question that include that string within their question.
  # Try using the word "title" to start.

  def search_questions():
    body = request.get_json()
    query_searchTerm = body.get('searchTerm', None)

    if query_searchTerm:
      search_results = Question.query.filter(
                  Question.question.ilike(f'%{query_searchTerm}%')).all()

      return jsonify({
        'success': True,
        'questions': [question.format() for question in search_results],
        'total_question': len(search_results),
        'current_category': None
      })
    else:
      abort(404)


  # @TODO:
  # Create a GET endpoint to get questions based on category.
  #
  # TEST: In the "List" tab / main screen, clicking on one of the
  # categories in the left column will cause only questions of that
  # category to be shown.

  @app.route('/categories/<int:category_id>/questions')
  def retrieve_questions_by_category(category_id):

    try:
      questions = Question.query.filter(Question.category == str(category_id)).all()

      return jsonify({
        'success': True,
        'questions': [question.format() for question in questions],
        'total_questions': len(questions),
        'current_category' : category_id
      })
    except:
      abort(404)





  # @TODO:
  # Create a POST endpoint to get questions to play the quiz.
  # This endpoint should take category and previous question parameters
  # and return a random questions within the given category,
  # if provided, and that is not one of the previous questions.
  #
  # TEST: In the "Play" tab, after a user selects "All" or a category,
  # one question at a time is displayed, the user is allowed to answer
  # and shown whether they were correct or not.
  
  @app.route('/quizzes', methods=['POST'])
  def get_random_quiz_question():
     try:
          body = request.get_json()

          previous_qustions = body.get('previous_questions', None)
          category = body.get('quiz_category', None)
          print(previous_qustions, category)
          if (previous_qustions is None) or (category is None):
              abort(422)

          if category['id'] == 0: # All category
              available_questions = Question.query.filter(Question.id.notin_(previous_qustions)).all()

          else:
              available_questions = Question.query.filter( Question.category == category['id'],
                Question.id.notin_(previous_qustions)).all()

          new_question = random.choice(available_questions) if available_questions else None

          print(new_question)
          return jsonify({
              'success': True,
              'question': new_question.format() if new_question else None
            })
     except:
         abort(422)

  # @TODO:
  # Create error handlers for all expected errors
  # including 404 and 422.

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
      }), 400



  return app