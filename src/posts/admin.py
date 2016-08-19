from django.contrib import admin

from .models import Post, Poster, PosterAverageStat, Stat


class StatInline(admin.TabularInline):
    model = Stat


class PostAdmin(admin.ModelAdmin):
    inlines = [StatInline]
    list_display = (
        'poster',
        'content',
        'datetime',
    )
    search_fields = (
        'upstream_id',
        'poster__upstream_id',
        '=poster__name',
        '=content',
    )
admin.site.register(Post, PostAdmin)


class PosterAverageStatInline(admin.TabularInline):
    model = PosterAverageStat


class PosterAdmin(admin.ModelAdmin):
    search_fields = (
        '=name',
    )
    list_filter = (
        'friend',
    )
    list_display = (
        'name',
        'followers_count',
        'friend',
    )
    inlines = [
        PosterAverageStatInline,
    ]
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
