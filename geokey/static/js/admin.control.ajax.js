/* ***********************************************
 * Module to send asychronous requests to the backend.
 * Singleton, does not net to instancated. Simply call for instance Control.Ajax.get()
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

(function (global) {
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
     * Sets the request header
     * @param {Object} xhr XmlHttpRequest object
     */
    function setHeader(xhr) {
        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
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
        // Append a forward slash to the URL if not present. Needed for POST
        // requests to Django as the forward to the corrent URL drops the POST
        // data.
        if (url.indexOf('?') === -1 && url[url.length -1] !== '/') {
            url = url + '/';
        }

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
    Ajax.prototype.post = function put(url, successCallback, errorCallback, data) {
        request(url, 'post', successCallback, errorCallback, data);
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
     * Request using HTTP DELETE
     * @param  {String}   url             URL the called.
     * @param  {Function} successCallback Function to be called after successful request
     * @param  {Function} errorCallback   Function to be called after request failed
     */
    Ajax.prototype.del = function del(url, successCallback, errorCallback) {
        request(url, 'DELETE', successCallback, errorCallback);
    };

    // Initialize
    global.Ajax = new Ajax();
}(window.Control ? window.Control : window.Control = {}));
