from django import forms

from .models import Post


class PostSearchForm(forms.Form):
    order_by = forms.ChoiceField(
        choices=(
            ('s.average_compare DESC', 'Average compare'),
            ('s.friends_reposts DESC', 'Friend reposts'),
            ('s.reposts DESC', 'Total reposts'),
            (
                's.reposts_per_followers_count DESC',
                'Proportional reposts per follower count'
            ),
            ('s.acceleration DESC', 'Acceleration'),
            ('s.speed DESC', 'Speed'),
            ('p.datetime DESC', 'Time'),
        ),
        initial='time',
        required=False,
    )

    filter_on_stat = forms.ChoiceField(
        choices=(
            ('last', 'last stat'),
            ('1', '1 minute'),
            ('2', '2 minute'),
            ('3', '3 minute'),
            ('4', '4 minute'),
            ('5', '5 minute'),
        ),
        initial='last',
        required=False,
    )

    max_age_in_minutes = forms.IntegerField(required=False, initial=30)
    min_friends_reposts = forms.IntegerField(required=False, initial=2)
    min_average_compare = forms.FloatField(required=False, initial=1)
    min_average_posts = forms.IntegerField(required=False, initial=10)
    min_average_reposts = forms.IntegerField(required=False, initial=7)
