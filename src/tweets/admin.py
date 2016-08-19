from django.contrib import admin

from .models import TwitterAccount


class TwitterAccountAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'hub',
    )
    list_editable = (
        'hub',
    )


admin.site.register(TwitterAccount, TwitterAccountAdmin)
