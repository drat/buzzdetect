from django.contrib import admin

from .models import Retweets, Tweet


class TweetAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'datetime',
    )

admin.site.register(Tweet, TweetAdmin)


class RetweetsAdmin(admin.ModelAdmin):
    list_display = (
        'retweet_count',
        'retweet_per_minute',
        'acceleration',
        'tweet',
        'datetime',
    )

    list_display_links = ('tweet',)

admin.site.register(Retweets, RetweetsAdmin)
