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
import cgi
import urllib

from google.appengine.ext import ndb

import webapp2


class Book(ndb.Model):
    name = ndb.StringProperty()

    def get_greeting(self):
        return Greeting.query(ancestor=self.key).order(-Greeting.date)

    def get_greeting_num(self):
        return Greeting.query(ancestor=self.key).count()

    def put_greeting(self, content):
        Greeting(parent=self.key, content=content).put()

    @classmethod
    def query_book(cls):
        return cls.query().order(cls.name)


# [START greeting]
class Greeting(ndb.Model):
    """Models an individual Guestbook entry with content and date."""
    content = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]

# [START query]
    @classmethod
    def query_greeting(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.date)
# [END query]


class MainPage(webapp2.RequestHandler):
    def get(self):
        write = self.response.out.write
        write('<html><body>')
        write('<ul>')
        write('<h2>Guestbook List</h2>')

        for book in Book.query_book():
            book_item = '<li><a href="/books/{id}">{name} : {greeting_num}</a></li>'.format(
                id = book.key.id(),
                name = book.name,
                greeting_num = book.get_greeting_num()
            )
            write(book_item)

        write('</ul>')
        write("""
            <hr>
            <form action="/?%s" method="post">
                <form>New guestbook name : <input value="" name="guestbook_name">
                                           <input type="submit" value="add & switch book"></form>
            </form>
            </body></html>""")

    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        book = Book(
            name = guestbook_name,
        )
        book_key = book.put()
        self.redirect('/books/' + str(book_key.id()))


class BookPage(webapp2.RequestHandler):
    def get(self, guestbook_id):
        write = self.response.out.write
        write('<html><body>')
        book = Book.get_by_id(long(guestbook_id))
        guestbook_name = book.name
        write('<h2>Guestbook: {guestbook_name}</h2>'.format(
            guestbook_name = guestbook_name
        ))
        greetings = book.get_greeting().fetch(20)

        for greeting in greetings:
            write('<blockquote>%s</blockquote>' %
                                    cgi.escape(greeting.content))

        write("""
            <form action="/sign?%s" method="post">
                <div><textarea name="content" rows="3" cols="60"></textarea></div>
                <div><input type="submit" value="Sign Guestbook"></div>
            </form>
            <a href="/">Guestbook List</a> 
            </body></html>""" % urllib.urlencode({'guestbook_id': guestbook_id}))


# [START submit]
class SubmitForm(webapp2.RequestHandler):
    def post(self):
        # We set the parent key on each 'Greeting' to ensure each guestbook's
        # greetings are in the same entity group.
        guestbook_id = self.request.get('guestbook_id')
        book = Book.get_by_id(long(guestbook_id))
        book.put_greeting(self.request.get('content'))
# [END submit]
        self.redirect('/books/' + str(guestbook_id))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', SubmitForm),
    ('/books/(\d+)', BookPage)
])
# [END all]
