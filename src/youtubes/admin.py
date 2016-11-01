from django.contrib import admin

from .models import YoutubeAccount, YoutubeRequest


def sync_accounts(self, request, queryset):
    request = YoutubeRequest()
    for account in queryset:
        account.sync()
sync_accounts.short_description = 'Sync accounts'


class YoutubeAccountAdmin(admin.ModelAdmin):
    actions = [sync_accounts]


admin.site.register(YoutubeAccount, YoutubeAccountAdmin)
