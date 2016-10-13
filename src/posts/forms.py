from django import forms

from .models import Hub, Post


class PostSearchForm(forms.Form):
    ORDER_BY_CHOICES = (
        ('p.datetime DESC', 'Time'),
        ('s.friends_reposts DESC', 'Friend reposts'),
        ('s.reposts DESC', 'Total reposts'),
        (
            's.reposts_per_followers_count DESC',
            'Proportional reposts per follower count'
        ),
        ('s.acceleration DESC', 'Acceleration'),
        ('s.speed DESC', 'Speed'),
    )

    now = forms.DateTimeField(required=False)

    source = forms.ChoiceField(
        choices=(
            ('youtubes', 'Youtube'),
            ('tweets', 'Twitter'),
        )
    )

    order_by = forms.ChoiceField(
        choices=ORDER_BY_CHOICES,
        initial=ORDER_BY_CHOICES[0][0],
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

    max_age_in_minutes = forms.IntegerField(required=False)
    min_friends_reposts = forms.IntegerField(required=False)
    min_average_compare = forms.FloatField(required=False)
    hub = forms.ModelChoiceField(Hub.objects.all(), required=False)
    kind = forms.ChoiceField(
        choices=(('', 'Any'),) + Post.KIND_CHOICES,
        required=False,
        initial=''
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(PostSearchForm, self).__init__(*args, **kwargs)
        if self.user.pk:
            if not self.user.is_superuser:
                self.fields['hub'].queryset = Hub.objects.filter(users=self.user)
                self.fields['hub'].required = True
        self.fields['hub'].initial = self.fields['hub'].queryset.first()

    @classmethod
    def post_list(cls, user, data):
        form = cls(data or None, user=user)

        kwargs = {
            name: field.initial for name, field in form.fields.items()
        }

        if form.is_valid():
            kwargs.update(form.cleaned_data)

        return form, Post.objects.filter_list(**kwargs)
