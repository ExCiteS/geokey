module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        handlebars: {
            options: {
                namespace: 'Templates',
                processName: function(filePath) {
                    var file = filePath.split('/')[3];
                    return file.substring(0, file.indexOf('.hbs'));
                },
                processPartialName: function(filePath) {
                    var file = filePath.split('/')[3];
                    return file.substring(1, file.indexOf('.hbs'));
                }
            },

            compile: {
                files: {
                    'geokey/templates/templates.js': 'geokey/templates/handlebars/**/*.hbs'
                }
            }
        },

        concat: {
            options: {
                separator: ';'
            },

            handlebars: {
                src: ['geokey/templates/handlebars/helpers.js', 'geokey/templates/templates.js'],
                dest: 'geokey/static/js/templates.js'
            }
        },

        uglify: {
            handlebars: {
                src: ['geokey/static/js/templates.js'],
                dest: 'geokey/static/js/templates.js'
            }
        },

        watch: {
            options: {
                livereload: true,
            },

            concat: {
                files: ['geokey/templates/handlebars/helpers.js', 'geokey/templates/templates.js'],
                tasks: ['concat'],
                options: {
                    spawn: false,
                }
            },

            handlebars: {
                files: ['geokey/templates/handlebars/**/*.hbs'],
                tasks: ['handlebars'],
                options: {
                    spawn: false,
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-handlebars');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-uglify');

    grunt.registerTask('default', ['handlebars', 'concat', 'uglify', 'watch']);
};
