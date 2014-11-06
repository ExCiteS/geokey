import json
from django import template

register = template.Library()


@register.simple_tag
def filters(rule):
    s = ''

    if rule.min_date is not None or rule.max_date is not None:
        s = s + '<li>the contribution has been created '
        if rule.min_date is not None:
            s = s + 'after %s' % rule.min_date.strftime("%b %d %Y %H:%M")
        if rule.min_date is not None and rule.max_date is not None:
            s = s + ' and '
        if rule.max_date is not None:
            s = s + 'before %s' % rule.max_date.strftime("%b %d %Y %H:%M")
        s = s + '</li>'

    for field in rule.observation_type.fields.all():
        rule_filter = None
        if rule.filters is not None:
            rule_filter = rule.filters.get(field.key)

        if rule_filter is not None:

            if field.fieldtype == 'TextField':
                s = s + '<li> %s contains %s</li>' % (field.name, rule_filter)

            if field.fieldtype == 'NumericField':
                minval = json.loads(rule_filter).get('minval')
                maxval = json.loads(rule_filter).get('maxval')

                s = s + '<li> %s is ' % (field.name)

                if minval is not None:
                    s = s + 'greater than %s' % minval
                if minval is not None and maxval is not None:
                    s = s + ' and '
                if maxval is not None:
                    s = s + 'lower than %s' % maxval
                s = s + '</li>'

            if field.fieldtype == 'DateTimeField':
                minval = json.loads(rule_filter).get('minval')
                maxval = json.loads(rule_filter).get('maxval')

                s = s + '<li> %s is ' % (field.name)

                if minval is not None:
                    s = s + 'after %s' % minval
                if minval is not None and maxval is not None:
                    s = s + ' and '
                if maxval is not None:
                    s = s + 'before %s' % maxval
                s = s + '</li>'

            if field.fieldtype == 'TrueFalseField':
                s = s + '<li> %s is %s</li>' % (field.name, rule_filter)

            if field.fieldtype == 'LookupField':
                values = []
                for lookup in json.loads(rule_filter):
                    values.append(field.lookupvalues.get(pk=lookup).name)

                s = s + '<li>%s is one of %s</li>' % (
                    field.name, ', '.join(values)
                )

            if field.fieldtype == 'MultipleLookupField':
                values = []
                for lookup in json.loads(rule_filter):
                    values.append(field.lookupvalues.get(pk=lookup).name)

                s = s + '<li>%s matches at least one of %s</li>' % (
                    field.name, ', '.join(values)
                )

    return s
