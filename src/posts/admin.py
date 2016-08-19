from django.contrib import admin

from .models import Hub, Post, Poster, PosterAverageStat, Stat


admin.site.register(Hub)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'poster',
        'content',
        'datetime',
    )
    search_fields = (
        'upstream_id',
    )
admin.site.register(Post, PostAdmin)


class PosterAdmin(admin.ModelAdmin):
    list_filter = (
        'friend',
    )
    list_display = (
        'name',
        'followers_count',
        'friend',
    )
admin.site.register(Poster, PosterAdmin)


class StatAdmin(admin.ModelAdmin):
    list_display = (
        'added',
        'reposts',
        'speed',
        'acceleration',
        'reposts_per_followers_count',
    )
admin.site.register(Stat, StatAdmin)


class PosterAverageStatAdmin(admin.ModelAdmin):
    list_display = (
        'total_posts',
        'total_reposts',
        'minute',
        'average',
    )

    list_filter = (
        'minute',
    )
admin.site.register(PosterAverageStat, PosterAverageStatAdmin)
