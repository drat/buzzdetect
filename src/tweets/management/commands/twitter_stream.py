import threading
import sys

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from django.conf import settings

from dateutil import parser

from posts.models import Post, Poster

import time

from twitter import TwitterStream
from twitter.api import TwitterHTTPError

from tweets.models import TwitterAccount


# Blocking thread interruption "hack" by
# http://pydev.blogspot.fr/2013/01/interrupting-python-thread-with-signals.html
class SigFinish(Exception):
    pass


def throw_signal_function(frame, event, arg):
    raise SigFinish()


def interrupt_thread(thread):
    for thread_id, frame in sys._current_frames().items():
        if thread_id == thread.ident:  # Note: Python 2.6 onwards
            set_trace_for_frame_and_parents(frame, throw_signal_function)

            while thread in [t for t in threading.enumerate()]:
                time.sleep(3)

def set_trace_for_frame_and_parents(frame, trace_func):
    # Note: this only really works if there's a tracing function set in this
    # thread (i.e.: sys.settrace or threading.settrace must have set the
    # function before)
    while frame:
        if frame.f_trace is None:
            frame.f_trace = trace_func
        frame = frame.f_back
    del frame


class TwitterStreamThread(threading.Thread):
    def __init__(self, account):
        self.account = account
        super(TwitterStreamThread, self).__init__()

    def run(self):
        sys.settrace(lambda *a, **k: None)

        try:
            while True:
                try:
                    self.userstream = TwitterStream(
                        auth=self.account.get_oauth(),
                        domain='userstream.twitter.com'
                    )
                    self.twitter = self.account.get_twitter()
                    self.follow_stream()
                except TwitterHTTPError as e:
                    print e
                    time.sleep(10)
        except SigFinish:
            sys.stderr.write(
                'Finishing thread cleanly for %s\n' % self.account.name
            )

    def follow_stream(self):
        for msg in self.userstream.user():
            print 'Got msg', msg

            if 'friends' in msg:
                self.save_friends(msg['friends'])
                continue

            if 'delete' in msg and 'status' in msg['delete']:
                Post.objects.filter(
                    upstream_id=msg['delete']['status']['id']
                ).delete()
                print 'Deleted', msg
                continue

            if 'id' not in msg:
                print 'Skipping because it has no id'
                continue

            tweet = self.tweet_get_or_create(msg)
            print u'Saved tweet %s' % slugify(tweet)

    def save_friends(self, ids):
        for l in [ids[i:i+100] for i in xrange(0, len(ids), 100)]:
            data = self.twitter.users.lookup(
                user_id=','.join([unicode(x) for x in l])
            )

            for user in data:
                tweeter = self.tweetter_get_or_create(user, friend=True)
                print u'Following %s' % slugify(user['name'])

    def tweet_get_or_create(self, data):
        parent = None

        if 'retweeted_status' in data:
            parent = self.tweet_get_or_create(data['retweeted_status'])

        poster = self.tweetter_get_or_create(data['user'])

        defaults = dict(
            parent=parent,
            poster=poster,
            datetime=parser.parse(data['created_at']),
            content=data['text'],
        )

        obj, created = Post.objects.update_or_create(
            upstream_id=data['id'],
            defaults=defaults,
            content_type=ContentType.objects.get_for_model(self.account),
            object_id=self.account.pk,
        )

        return obj

    def tweetter_get_or_create(self, data, friend=None):
        defaults = dict(
            name=data['name'],
            followers_count=data['followers_count'],
        )

        if friend is not None:
            defaults['friend'] = friend

        obj, created = Poster.objects.update_or_create(
            upstream_id=data['id'],
            defaults=defaults,
        )

        return obj


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            while True:
                self.run()
                time.sleep(15)
        except KeyboardInterrupt:
            for t in threading.enumerate():
                interrupt_thread(t)
            raise

    @staticmethod
    def run():
        main_thread = threading.currentThread()
        accounts = TwitterAccount.objects.filter(follow=True)
        account_ids = [a.pk for a in accounts]

        for t in threading.enumerate():
            thread_account = getattr(t, 'account', None)

            if t.ident == main_thread.ident:
                continue

            # Check if the account of this thread has been deleted
            if thread_account.pk not in account_ids:
                print 'Stopping thread for %s' % thread_account
                interrupt_thread(t)

        for account in accounts:
            start = True
            stop  = False

            for t in threading.enumerate():
                thread_account = getattr(t, 'account', None)

                if thread_account != account:
                    continue

                # Check if the account of this thread has changed
                changed = (
                    thread_account.consumer_key != account.consumer_key
                    or thread_account.consumer_secret != account.consumer_secret
                    or thread_account.token != account.token
                    or thread_account.secret != account.secret
                )
                # Then let's create another thread
                if changed:
                    stop  = True
                    start = True

                # Check if thread is already started for this account
                if thread_account == account:
                    start = False
                    break

            if stop:
                print 'Stopping thread for %s' % thread_account
                interrupt_thread(t)

            if start:
                print 'Starting thread for %s' % account
                t = TwitterStreamThread(account)
                t.start()
