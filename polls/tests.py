import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Question
# Create your tests here.

class QuestionMethodTests(TestCase): #We have class which has a bunch of tests
    def test_was_published_recently_with_future_question(self): 
        time = timezone.now() + datetime.timedelta(days=30) #we set time to the future
        future_question = Question(pub_date=time) #We set the pub_date attribute in question to (the future) time
        self.assertEqual(future_question.was_published_recently(), False) #and then we test to see if the was_published_recently method returns false, like it should
    def test_was_published_recently_with_old_question(self):
        #should return false for questions whose pub_date is older than 1 day.
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)
    def test_was_published_recently_with_recent_question(self):
        #should return true for questions published within the last day.
        time = timezone.now() - datetime.timedelta(hours = 1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(),True)

def create_question(question_text, days): #We create this shortcut function to make it easy to create questions
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date = time)
               
class QuestionViewTests(TestCase):
    #If no questions exist, an appropriate message should be displayed
    def test_index_view_with_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'],[])
    #questions with dates in the past should be displayed
    def test_index_view_with_a_past_question(self):
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
        response.context['latest_question_list'],
        ['<Question: Past question.>']
        )
    def test_index_view_with_a_future_question(self):
        create_question(question_text="Future question.", days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.",
            status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'],[])
        
    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )
        
    def test_index_view_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )
        
class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_quesiton(self):
        #future questions detail view should return 404
        future_question = create_question(question_text='Future question.', days = 5)
        response = self.client.get(reverse('polls:detail',args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)
    
    def test_detail_view_with_a_past_question(self):
        #Detail view of question with pub_date in the past should display question's text
        past_question = create_question(question_text='Past question.', days = -5)
        response = self.client.get(reverse('polls:detail',args= (past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code = 200)