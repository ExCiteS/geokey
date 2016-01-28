/* ***********************************************
 * This module is a wrapper aroung jQuery's $.ajax method. It simplifies sending
 * asychronous requests to the AJAX API.
 * To use it call: Control.Ajax.get(), Control.Ajax.put(), etc.
 *
 * Used in:
 * - templates/categories/category_list.html
 * - templates/categories/category_overview.html
 * - templates/categories/category_settings.html
 * - templates/categories/field_settings.html
 * - templates/projects/project_settings.html
 * - templates/subsets/subset_data.html
 * - templates/superusertools/manageusers.html
 * - templates/users/usergroup_admins.html
 * - templates/users/usergroup_data.html
 * - templates/users/usergroup_overview.html
 * ***********************************************/

(function(global) {
    'use strict';
    var baseUrl = '/ajax/';

    function Ajax() {

    }

    /**
     * Reads the CSRF token from the cookie. Nessesary to authentication the user with AJAX requests.
     */

    /**
     * Reads the CSRF token from the cookie. Nessesary to authentication the user with AJAX requests.
     * @param  {String} name The name of the cookie to read
     * @return {String}      The cookie value
     */
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Sets the request header.
     * @param {Object} xhr XmlHttpRequest object
     */
    function setHeader(xhr) {
        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    }

    /**
     * Append a forward slash to the URL if not present. Needed for POST requests to Django as the
     * forward to the corrent URL drops the POST data.
     * @param {Object} xhr XmlHttpRequest object
     */
    function fixUrl(url) {
        if (url.indexOf('?') === -1 && url[url.length - 1] !== '/') {
            url = url + '/';
        }

        return url;
    }

    /**
     * Sends the request.
     * @param  {String}   url             URL the called.
     * @param  {String}   method          HTTP method
     * @param  {Function} successCallback Function to be called after successful request
     * @param  {Function} errorCallback   Function to be called after request failed
     * @param  {Object}   data            Optional. Data to be send with the request body
     */
    function request(url, method, successCallback, errorCallback, data) {
        url = fixUrl(url);

        $.ajax({
            url: baseUrl + url,
            method: method,
            xhrFields: {
                withCredentials: true
            },
            success: successCallback,
            error: errorCallback,
            data: JSON.stringify(data),
            beforeSend: setHeader,
            contentType: 'application/json; charset=utf-8'
        });
    }

    /**
     * Request using HTTP GET
     * @param  {String}   url             URL the called.
     * @param  {Function} successCallback Function to be called after successful request
     * @param  {Function} errorCallback   Function to be called after request failed
     */
    Ajax.prototype.get = function get(url, successCallback, errorCallback) {
        request(url, 'GET', successCallback, errorCallback);
    };

    /**
     * Request using HTTP POST
     * @param  {String}   url             URL the called.
     * @param  {Function} successCallback Function to be called after successful request
     * @param  {Function} errorCallback   Function to be called after request failed
     * @param  {Object}   data            Data to be send with the request body
     */
    Ajax.prototype.post = function post(url, successCallback, errorCallback, data) {
        request(url, 'POST', successCallback, errorCallback, data);
    };

    /**
     * Request using HTTP PUT
     * @param  {String}   url             URL the called.
     * @param  {Function} successCallback Function to be called after successful request
     * @param  {Function} errorCallback   Function to be called after request failed
     * @param  {Object}   data            Data to be send with the request body
     */
    Ajax.prototype.put = function put(url, successCallback, errorCallback, data) {
        request(url, 'PUT', successCallback, errorCallback, data);
    };

    /**
     * Request using HTTP PATCH
     * @param  {String}   url             URL the called.
     * @param  {Function} successCallback Function to be called after successful request
     * @param  {Function} errorCallback   Function to be called after request failed
     * @param  {Object}   data            Data to be send with the request body
     */
    Ajax.prototype.patch = function patch(url, successCallback, errorCallback, data) {
        request(url, 'PATCH', successCallback, errorCallback, data);
    };

    /**
     * Request using HTTP DELETE
     * @param  {String}   url             URL the called.
     * @param  {Function} successCallback Function to be called after successful request
     * @param  {Function} errorCallback   Function to be called after request failed
     */
    Ajax.prototype.del = function del(url, successCallback, errorCallback) {
        request(url, 'DELETE', successCallback, errorCallback);
    };

    /**
     * Request using HTTP POST (specificly for files)
     * @param  {String}   url             URL the called.
     * @param  {Function} successCallback Function to be called after successful request
     * @param  {Function} errorCallback   Function to be called after request failed
     * @param  {Object}   data            Data to be send with the request body
     */
    Ajax.prototype.postFiles = function postFiles(url, successCallback, errorCallback, data) {
        url = fixUrl(url);

        $.ajax({
            url: baseUrl + url,
            method: 'POST',
            xhrFields: {
                withCredentials: true
            },
            success: successCallback,
            error: errorCallback,
            data: data,
            beforeSend: setHeader,
            contentType: false,
            processData: false,
            cache: false
        });
    };

    // Initialize
    global.Ajax = new Ajax();
}(window.Control ? window.Control : window.Control = {}));
