# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Cloud Datastore NDB API guestbook sample.

This sample is used on this page:
    https://cloud.google.com/appengine/docs/python/ndb/

For more information, see README.md
"""

# [START all]
import os
import urllib

from google.appengine.ext import ndb

import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Book(ndb.Model):
    name = ndb.StringProperty()

    def fetch_greetings(self):
        return Greeting.query(ancestor=self.key).order(-Greeting.date)

    def fetch_greeting_num(self):
        return Greeting.query(ancestor=self.key).count()

    def put_greeting(self, content):
        Greeting(parent=self.key, content=content).put()

    def put_name(self, _name):
        self.name = _name
        self.put()

    @classmethod
    def fetch_books(cls):
        return cls.query().order(cls.name)


# [START greeting]
class Greeting(ndb.Model):
    """Models an individual Guestbook entry with content and date."""
    content = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]


class MainPage(webapp2.RequestHandler):
    def get(self):
        books = Book.fetch_books()

        template_values = {
            'books': books
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        book = Book(
            name = guestbook_name,
        )
        book_key = book.put()
        self.redirect('/books/' + str(book_key.id()))


class BookPage(webapp2.RequestHandler):
    def get(self, guestbook_id):
        book = Book.get_by_id(long(guestbook_id))
        guestbook_name = book.name
        greetings = book.fetch_greetings().fetch(20)

        template_values = {
            'guestbook_id': guestbook_id,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'greetings': greetings
        }

        template = JINJA_ENVIRONMENT.get_template('guestbook.html')
        self.response.write(template.render(template_values))

    def post(self, guestbook_id):
        guestbook_name = self.request.get('guestbook_name')
        book = Book.get_by_id(long(guestbook_id))
        book.put_name(guestbook_name)
        self.redirect('/books/' + str(guestbook_id))


# [START submit]
class SubmitForm(webapp2.RequestHandler):
    def post(self, guestbook_id):
        # We set the parent key on each 'Greeting' to ensure each guestbook's
        # greetings are in the same entity group.
        book = Book.get_by_id(long(guestbook_id))
        book.put_greeting(self.request.get('content'))
# [END submit]
        self.redirect('/books/' + str(guestbook_id))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign/(\d+)', SubmitForm),
    ('/books/(\d+)', BookPage)
])
# [END all]
