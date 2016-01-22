/* ***********************************************
 * Changes the display of radio buttons for
 * contributing permissions on a project.
 *
 * Used in:
 * - projects/project_create.html
 * ***********************************************/

$(function() {
    'use strict';

    $('input[name="isprivate"]').change(function(event) {
        if ($(event.target).attr('id') === 'public') {
            $('.public').removeClass('hidden');
            $('.private').addClass('hidden');
        } else if ($(event.target).attr('id') === 'private') {
            $('.public').addClass('hidden');
            $('.private').removeClass('hidden');
        }
    });
});
