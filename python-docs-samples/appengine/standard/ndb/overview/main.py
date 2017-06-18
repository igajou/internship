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
    greeting_number = ndb.IntegerProperty()

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
    def query_book(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.date)
# [END query]


class MainPage(webapp2.RequestHandler):
    def get(self):
        write = self.response.out.write
        write('<html><body>')
        write('<ul>')
        for book in Book.query_book():
            book_item = '<li>{name} : {greeting_num}</li>'.format(
                name = book.name,
                greeting_num = book.greeting_number
            )
            write(book_item)
        write('</ul>')
        write("""
            <hr>
            <form action="/?%s" method="post">
                <form>New guestbook name : <input value="" name="guestbook_name">
                                           <input type="submit" value="add book"></form>
            </form>
            </body></html>""")

    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        book = Book(
            name = guestbook_name,
            greeting_number = 0
        )
        book.put()


class BookPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')
        guestbook_name = self.request.get('guestbook_name')
        ancestor_key = ndb.Key("Book", guestbook_name or "*notitle*")
        greetings = Greeting.query_book(ancestor_key).fetch(20)

        for greeting in greetings:
            self.response.out.write('<blockquote>%s</blockquote>' %
                                    cgi.escape(greeting.content))

        self.response.out.write("""
          <form action="/sign?%s" method="post">
            <div><textarea name="content" rows="3" cols="60"></textarea></div>
            <div><input type="submit" value="Sign Guestbook"></div>
          </form>
          <hr>
          <form>Guestbook name: <input value="%s" name="guestbook_name">
          <input type="submit" value="switch"></form>
        </body>
      </html>""" % (urllib.urlencode({'guestbook_name': guestbook_name}),
                    cgi.escape(guestbook_name)))


# [START submit]
class SubmitForm(webapp2.RequestHandler):
    def post(self):
        # We set the parent key on each 'Greeting' to ensure each guestbook's
        # greetings are in the same entity group.
        guestbook_name = self.request.get('guestbook_name')
        greeting = Greeting(parent=ndb.Key("Book",
                                           guestbook_name or "*notitle*"),
                            content=self.request.get('content'))
        greeting.put()
# [END submit]
        self.redirect('/?' + urllib.urlencode(
            {'guestbook_name': guestbook_name}))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', SubmitForm)
])
# [END all]