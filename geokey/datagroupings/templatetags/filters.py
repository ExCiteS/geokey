from django import template

register = template.Library()


def get_textfield_filter(field, rule_filter):
    return '<li>%s contains %s</li>' % (field.name, rule_filter)


def get_numericfield_filter(field, rule_filter):
    minval = rule_filter.get('minval')
    maxval = rule_filter.get('maxval')

    filter_string = '<li>%s is ' % (field.name)

    if minval is not None:
        filter_string = filter_string + 'greater than %s' % minval
    if minval is not None and maxval is not None:
        filter_string = filter_string + ' and '
    if maxval is not None:
        filter_string = filter_string + 'lower than %s' % maxval
    filter_string = filter_string + '</li>'

    return filter_string


def get_datefield_filter(field, rule_filter):
    minval = rule_filter.get('minval')
    maxval = rule_filter.get('maxval')

    filter_string = '<li>%s is ' % (field.name)

    if minval is not None:
        filter_string = filter_string + 'after %s' % minval
    if minval is not None and maxval is not None:
        filter_string = filter_string + ' and '
    if maxval is not None:
        filter_string = filter_string + 'before %s' % maxval
    filter_string = filter_string + '</li>'

    return filter_string


def get_singlelookup_filter(field, rule_filter):
    values = []
    for lookup in rule_filter:
        values.append(field.lookupvalues.get(pk=lookup).name)

    return '<li>%s is one of %s</li>' % (
        field.name, ', '.join(values)
    )


def get_multiplelookup_filter(field, rule_filter):
    values = []
    for lookup in rule_filter:
        values.append(field.lookupvalues.get(pk=lookup).name)

    return '<li>%s matches at least one of %s</li>' % (
        field.name, ', '.join(values)
    )


def get_createdate_filter(rule):
    filter_string = '<li>the contribution has been created '
    if rule.min_date is not None:
        filter_string = filter_string + 'after %s' % (
            rule.min_date.strftime("%b %d %Y %H:%M"))
    if rule.min_date is not None and rule.max_date is not None:
        filter_string = filter_string + ' and '
    if rule.max_date is not None:
        filter_string = filter_string + 'before %s' % (
            rule.max_date.strftime("%b %d %Y %H:%M"))
    filter_string = filter_string + '</li>'

    return filter_string


@register.simple_tag
def filters(rule):
    s = ''

    if rule.min_date is not None or rule.max_date is not None:
        s = s + get_createdate_filter(rule)

    for field in rule.category.fields.all():
        rule_filter = None
        if rule.constraints is not None:
            rule_filter = rule.constraints.get(field.key)

        if rule_filter is not None:
            if field.fieldtype == 'TextField':
                s = s + get_textfield_filter(field, rule_filter)

            elif field.fieldtype == 'NumericField':
                s = s + get_numericfield_filter(field, rule_filter)

            elif (field.fieldtype == 'DateTimeField' or
                    field.fieldtype == 'DateField' or
                    field.fieldtype == 'TimeField'):
                s = s + get_datefield_filter(field, rule_filter)

            elif field.fieldtype == 'LookupField':
                s = s + get_singlelookup_filter(field, rule_filter)

            elif field.fieldtype == 'MultipleLookupField':
                s = s + get_multiplelookup_filter(field, rule_filter)

    return s
