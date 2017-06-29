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
    tags = ndb.KeyProperty(kind='Tag', repeated=True)

    def put_name(self, _name):
        self.name = _name

    # Greeting
    def fetch_greetings(self):
        return Greeting.query(ancestor=self.key).order(-Greeting.date)

    def fetch_greeting_num(self):
        return Greeting.query(ancestor=self.key).count()

    def put_greeting(self, content):
        Greeting(parent=self.key, content=content).put()

    def delete_greeting(self, greeting_id):
        Greeting.get_by_id(long(greeting_id), parent=self.key).key.delete()

    # Tag
    def put_tag(self, _name):
        _tag = Tag.query(Tag.name == _name).get()
        if _tag is None:
            tag_key = Tag(name = _name).put()
            self.tags.append(tag_key)
        else:
            self.tags.append(_tag.key)
        return list(set(self.tags)) # Unique list

    @classmethod
    def fetch_books(cls):
        return cls.query().order(cls.name)

    @classmethod
    def fetch_book_by_id(cls, book_id):
        try:
            book = cls.get_by_id(long(book_id))
            book.key
        except:
            raise
        else:
            return book


# [START greeting]
class Greeting(ndb.Model):
    """Models an individual Guestbook entry with content and date."""
    content = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]


class Tag(ndb.Model):
    name =  ndb.StringProperty(required=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        books = Book.fetch_books()

        template_values = {
            'books': books
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class BookPage(webapp2.RequestHandler):
    def get(self, guestbook_id):
        try:
            book = Book.fetch_book_by_id(long(guestbook_id))
        except Exception, e:
            template_values = {'except': True, 'e': e}
            template = JINJA_ENVIRONMENT.get_template('guestbook.html')
            self.response.write(template.render(template_values))
        else:
            guestbook_name = book.name
            tag_keys = book.tags
            greetings = book.fetch_greetings().fetch(20)

            template_values = {
                'guestbook_id': guestbook_id,
                'guestbook_name': urllib.quote_plus(guestbook_name),
                'tag_keys': tag_keys,
                'greetings': greetings
            }

            template = JINJA_ENVIRONMENT.get_template('guestbook.html')
            self.response.write(template.render(template_values))


class BookListHandler(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        tag_name = self.request.get('tag_name')
        book = Book(
            name = guestbook_name
        )
        book.tags = book.put_tag(tag_name)
        book_key = book.put()
        self.redirect('/books/{book_id}'.format(book_id=book_key.id()))


class BookHandler(webapp2.RequestHandler):
    def post(self, guestbook_id):
        guestbook_name = self.request.get('guestbook_name')
        tag_name = self.request.get('tag_name')
        try:
            book = Book.fetch_book_by_id(long(guestbook_id))
        except Exception, e:
            template_values = {'except': True, 'e': e}
            template = JINJA_ENVIRONMENT.get_template('guestbook.html')
            self.response.write(template.render(template_values))
        else:
            book.tags = book.put_tag(tag_name)
            book.put_name(guestbook_name)
            book.put()
            self.redirect('/books/{book_id}'.format(book_id=guestbook_id))


class GreetingListHandler(webapp2.RequestHandler):
    def post(self, guestbook_id):
        try:
            book = Book.fetch_book_by_id(long(guestbook_id))
        except Exception, e:
            template_values = {'except': True, 'e': e}
            template = JINJA_ENVIRONMENT.get_template('guestbook.html')
            self.response.write(template.render(template_values))
        else:
            book.put_greeting(self.request.get('content'))
            self.redirect('/books/{book_id}'.format(book_id=guestbook_id))


class GreetingHandler(webapp2.RequestHandler):
    def post(self, guestbook_id, greeting_id):
        try:
            book = Book.fetch_book_by_id(long(guestbook_id))
        except Exception, e:
            template_values = {'except': True, 'e': e}
            template = JINJA_ENVIRONMENT.get_template('guestbook.html')
            self.response.write(template.render(template_values))
        else:
            book.delete_greeting(greeting_id)
            self.redirect('/books/{book_id}'.format(book_id=guestbook_id))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/books/(\d+)', BookPage),
    ('/api/books', BookListHandler),
    ('/api/books/(\d+)', BookHandler),
    ('/api/books/(\d+)/greetings', GreetingListHandler),
    ('/api/books/(\d+)/greetings/(\d+)', GreetingHandler)
])
# [END all]
