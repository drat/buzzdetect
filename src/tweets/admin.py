from django.contrib import admin

from .models import Tweet, Source


class TweetAdmin(admin.ModelAdmin):
    list_display = (
        'parent',
        'text',
        'datetime',
    )

admin.site.register(Tweet, TweetAdmin)


class SourceAdmin(admin.ModelAdmin):
    list_filter = (
        'friend',
    )
admin.site.register(Source)
