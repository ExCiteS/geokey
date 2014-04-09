module.exports = function(grunt) {

    // 1. All configuration goes here
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        handlebars: {
            options: {
                namespace: "Templates",
                processName: function(filePath) {
                    var file = filePath.split('/')[2];
                    return file.substring(0, file.indexOf('.hbs'));
                },
                processPartialName: function(filePath) {
                    var file = filePath.split('/')[2];
                    return file.substring(1, file.indexOf('.hbs'));
                }
            },
            compile: {
                files: {
                    "static/js/templates.js": "templates/handlebars/**/*.hbs",
                }
            }
        },

        watch: {
            options: {
                livereload: true,
            },

            handlebars: {
                files: ['templates/**/*.hbs'],
                tasks: ['handlebars'],
                options: {
                    spawn: false,
                }
            },
        }
    });

    // 3. Where we tell Grunt we plan to use this plug-in.
    grunt.loadNpmTasks('grunt-contrib-handlebars');
    grunt.loadNpmTasks('grunt-contrib-watch');

    // 4. Where we tell Grunt what to do when we type "grunt" into the terminal.
    grunt.registerTask('default', ['handlebars', 'watch']);
};