Handlebars.registerHelper('value', function(feature, field) {
    var value = (feature.properties[field.key] ? feature.properties[field.key] : '—');

    switch (field.fieldtype) {
        case 'LookupField':
            for (var j = 0, lenj = field.lookupvalues.length; j < lenj; j++) {
                if (field.lookupvalues[j].id === value) {
                    value = field.lookupvalues[j].name;
                    break;
                }
            }
            break;
        case 'DateTimeField':
            value = moment(value).fromNow() + ' ('+ moment(value).format('llll') +')';
            break;
    }
    return value;
});