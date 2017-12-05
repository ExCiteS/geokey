/* ***********************************************
 * Indicates to user how many characters are still
 * left in the post to Twitter
 *
 * if selected #socialaccount is twitter:
 *     #remaining_characters are calculated based on fields: #text_post & #text_link
 *     maxlength attribute in #text_post is dynamically updated
 * else #characters is hidden
 *
 * Used in:
 * - templates/socialinteractions/socialinteraction_post_create.html
 * - templates/socialinteractions/socialinteraction_post_settings.html
 *
 * ***********************************************/

if ($("#socialaccount option:selected").text().match("¦¦ twitter$")) {
    $("#text_post").on('input', function () {
        update_length()
    }).trigger('input')

    $("#text_link").on('input', function () {
        update_length()
    }).trigger('input')

    function update_length() {
        if (/\$link\$/i.test($("#text_post").val())) {
            post_length = $("#text_post").val().length - "\$link\$".length
            url_length = $('#text_link').val().length
            if (/\$project_id\$/i.test($('#text_link').val()))
                url_length = url_length - "\$project_id\$".length + $('body').data('project-id').toString().length
            if (/\$contribution_id\$/i.test($('#text_link').val()))
                url_length = url_length - "\$contribution_id\$".length + $('body').data('contributions-count').toString().length + 1
        } else {
            post_length = $("#text_post").val().length
            url_length = 0
        }
        var remaining = 280 - post_length - url_length
        $('#remaining_characters').text(remaining)
        $('#text_post').attr('maxlength', $("#text_post").val().length + remaining)
    }

}

else {
    $('#characters').hide()
}
