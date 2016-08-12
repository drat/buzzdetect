from django import forms

from .models import Post


class PostSearchForm(forms.Form):
    order_by = forms.ChoiceField(
        choices=(
            ('friends_reposts', 'Friend reposts'),
            ('reposts', 'Total reposts'),
            (
                'reposts_per_followers_count',
                'Proportional reposts per follower count'
            ),
            ('acceleration', 'Acceleration'),
            ('speed', 'Speed'),
            ('time', 'Time'),
        ),
        initial='time',
        required=False,
    )

    filter_on_stat = forms.ChoiceField(
        choices=(
            ('current', 'current'),
            ('2 minutes', '2 minutes after creation'),
        ),
        initial='current',
        required=False,
    )

    max_age_in_minutes = forms.IntegerField(required=False, initial=30)
    min_friends_reposts = forms.IntegerField(required=False, initial=2)
    min_average_compare_after_three_minute = forms.FloatField(
        required=False,
        initial=2
    )
