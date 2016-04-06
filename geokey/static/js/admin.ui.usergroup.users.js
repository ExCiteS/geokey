/* ***********************************************
 * Adds and removes members to and from user grouos.
 *
 * Used in:
 * - templates/users/usergroup_users.html
 * - templates/users/usergroup_admins.html
 * - templates/superusertools/manage_users.html
 * ***********************************************/

(function(global) {
    'use strict';

    var url = global.url;

    // Get the elements
    var typeAwayResults = $('.type-away');
    var formField = $('#find-users');
    var userList = $('.user-list');

    if (!url) {
        var projectId = $('body').attr('data-project-id');
        var usergroupId = $('body').attr('data-usergroup-id');

        if (usergroupId) {
            url = 'projects/' + projectId + '/usergroups/' + usergroupId + '/users/';
        } else {
            url = 'projects/' + projectId + '/admins/';
        }
    }

    var numberOfRequests = 0;

    /**
     * Handles the click event when the user clicks on the remove link in the user list.
     * @param  {Event} event The click event fired by the link.
     */
    function handleRemoveUser(event) {
        var userId = $(event.target).parent('a').attr('data-user-id');
        var itemToRemove = $(event.target).parents('li');

        /**
         * Handles the response after the removal of the user from the group was successful.
         */
        function handleRemoveUserSuccess() {
            var html = $('<li class="bg-success message"><span class="text-success"><span class="glyphicon glyphicon-ok"></span> The user has been removed from the user group.</span></li>');
            itemToRemove.before(html);
            setTimeout(function() {
                html.remove();
            }, 5000);

            itemToRemove.remove();

            var numOfUsers = userList.children(':not(.message)').length;

            if (!usergroupId && numOfUsers === 1) {
                userList.find('li a.remove').remove();
            }

            if (numOfUsers === 0) {
                userList.append('<li class="empty">No users have been assigned to this group.</li>');
            }
        }

        /**
         * Handles the response after the removal of the user from the group failed.
         * @param  {Object} response JSON object of the response
         */
        function handleRemoveUserError(response) {
            var html = $('<li class="bg-danger message"><span class="text-danger"><span class="glyphicon glyphicon-remove"></span> An error occured while removing the user. Error text was: ' + response.responseJSON.error + '</span></li>');
            itemToRemove.before(html);
            setTimeout(function() {
                html.remove();
            }, 5000);
        }

        Control.Ajax.del(url + userId + '/', handleRemoveUserSuccess, handleRemoveUserError, {
            'user_id': userId
        });
        event.preventDefault();
    }


    /**
     * Handles the response if the addition of the user to the group was successful.
     * @param  {Object} response JSON object of the response
     */
    function handleAddUserSucess(response) {
        userList.empty();

        if (!userList.length) {
            userList = $('<ul class="user-list"></ul>').appendTo('#members');
            $('#members .empty-list').hide();
        }

        var html = $('<li class="bg-success message"><span class="text-success"><span class="glyphicon glyphicon-ok"></span> The user has been added to the user group.</span></li>');
        userList.append(html);
        setTimeout(function() {
            html.remove();
        }, 5000);

        userList.append(Templates.usergroupusers(response));
        userList.find('li a.remove').click(handleRemoveUser);

        formField.val('');
    }

    /**
     * Handles the response if the addition of the user to the group failed.
     * @param  {Object} response JSON object of the response
     */
    function handleAddUserError(response) {

    }

    /**
     * Handles click events pn items in the user dropdown list. Adds the user to the group.
     * @param  {Event} event The click event on the user link.
     */
    function handleAddUser(event) {
        var userId = $(event.target).attr('data-user-id');

        typeAwayResults.hide();
        Control.Ajax.post(url, handleAddUserSucess, handleAddUserError, {
            'user_id': userId
        });
        event.preventDefault();
    }



    /**
     * Handles the response the the request for the user list was successful. Updates the dropdown list.
     * @param  {Object} response JSON object of the response
     */
    function handleSuccess(response) {
        var users = response;
        var header = (users.length > 0 ? 'Click on item to add user' : 'No records matched your query');

        typeAwayResults.children().not('.dropdown-header').remove();
        numberOfRequests--;
        if (numberOfRequests === 0) {
            formField.removeClass('loading');
        }

        typeAwayResults.append(Templates.userstypeaway(response));

        typeAwayResults.children('.dropdown-header').text(header);
        typeAwayResults.find('li a').click(handleAddUser);
        typeAwayResults.show();
    }

    /**
     * Handles the response the the request for the user list failed.
     */
    function handleError() {
        numberOfRequests--;
        if (numberOfRequests === 0) {
            formField.removeClass('loading');
        }
        typeAwayResults.children().not('.dropdown-header').remove();
        typeAwayResults.children('.dropdown-header').html('<span class="text-danger">An error occured while trying to retrieve the user list. Please try again.</span>');
        typeAwayResults.show();
    }

    /**
     * Handles user type in the search field. Requests for a users list after 3 characters have been typed.
     * @param  {Event} event The keyup event fired by the field.
     */
    function handleFormType(event) {
        var activeLink = typeAwayResults.find('li.active');
        if (event.keyCode === 13) {
            // if user pressed ENTER, programmatically clicks the currently
            // active link in the list of users that match the query
            if (activeLink.length > 0) {
                activeLink.children().click();
            }
        } else if ((event.keyCode === 40 || event.keyCode === 38) && typeAwayResults.is(":visible")) {
            // if user pressed arrow up (keycode == 38) or arrow down (keycode == 40)
            // programmatically activates the previous or next link in the list
            // of users that match the query
            event.preventDefault();
            if (activeLink.length > 0) {
                if (event.keyCode === 38) { // user pressed arrow up
                    // activates the previous link in the list
                    // of users that match the query
                    if (activeLink.prev().not('.dropdown-header').length) {
                        activeLink.removeClass('active');
                        activeLink.prev().addClass('active');
                    }
                }
                if (event.keyCode === 40) { // user pressed arrow down
                    // activates the next link in the list
                    // of users that match the query
                    if (activeLink.next().length) {
                        activeLink.removeClass('active');
                        activeLink.next().addClass('active');
                    }
                }
            } else {
                // if now link in the list of users that match the query was active
                // activate the first item in the list
                typeAwayResults.find('li').not('.dropdown-header').first().addClass('active');
            }
        } else { // all other key strokes
            if (event.target.value.length === 1) {
                // hide the list of users
                typeAwayResults.hide();
            } else if (event.target.value.length >= 2) {
                // get users that match the query
                formField.addClass('loading');
                numberOfRequests++;
                Control.Ajax.get('users/?query=' + event.target.value, handleSuccess, handleError);
            }
        }
    }

    // Register the click event handler of remove links
    userList.find('li a.remove').click(handleRemoveUser);

    // Register the keyup event on the text field.
    formField.keydown(handleFormType);
}(this));
