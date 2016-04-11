"""Template tags for filtering tags."""

from django import template

register = template.Library()


@register.simple_tag
def is_selected(value, arr):
    if str(value) in arr:
        return 'selected'
    return ''


@register.simple_tag
def show_restrict(rules, category):
    if rules:
        if str(category.id) in rules:
            if rules[str(category.id)] == {}:
                return ('<a href="#" class="text-danger activate-detailed">'
                        'Restrict further</a>')

    return ''


@register.filter(name='is_in')
def is_in(d, key_name):
    if d is not None:
        if str(key_name) in d:
            return True

    return False


@register.inclusion_tag('snippets/data_fields_rules.html')
def show_fields(filters, category):
    if filters and str(category.id) in filters:
        cat_rules = filters.get(str(category.id))

        context = {
            'locked': category.project.islocked,
            'min_date': cat_rules.pop('min_date', None),
            'max_date': cat_rules.pop('max_date', None)
        }

        context['fields'] = [{
            'category_id': category.id,
            'field': category.fields.get_subclass(key=key),
            'rule': cat_rules[key]
        } for key in cat_rules]

        return context


@register.filter(name='minval')
def minval(d):
    if d is not None:
        if d.get('minval'):
            return d.get('minval')

    return ''


@register.filter(name='maxval')
def maxval(d):
    if d is not None:
        if d.get('maxval'):
            return d.get('maxval')

    return ''
