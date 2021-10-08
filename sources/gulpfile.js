/*
import this file using:
	const viBuildTasks = require('./vi/vi_tasks');
in gulpfile.js

and Call:
	`gulp vi` to call all necessary Tasks
 */

const gulp = require('gulp');
const plugins = require('gulp-load-plugins');
const fs = require('fs');

let applicationFolder = "../vi";

let srcpaths = {
	images: './images/**/*',
	editor: './htmleditor/**/*.js',
	js: './js/**/*.js',
	less: './less/vi.less',
	embedsvg: './embedsvg/**/*'
};

let destpaths = {
	css: applicationFolder+'/public/css',
	images: applicationFolder+'/public/images',
	embedsvg: applicationFolder+'/public/svgs',
	editor: applicationFolder+'/public/htmleditor',
	js: applicationFolder+'/public/js',
};


function loadTask(task, options) {
	return require('./gulptasks/' + task)(gulp, plugins, options)
}

//Build Editor
gulp.task("vi_editor", loadTask("editor_task",{
	src: srcpaths.editor,
	dest: destpaths.editor
}));

//less to css
gulp.task('vi_css', loadTask('css_task', {
	src: srcpaths.less,
	dest: destpaths.css
}));

gulp.task('vi_icons', loadTask('icon_task', {
	src: srcpaths.embedsvg,
	dest: destpaths.embedsvg
}));

gulp.task('vi_images', loadTask('image_task', {
	src: srcpaths.images,
	dest: destpaths.images
}));

gulp.task("vi_js", loadTask("js_task",{
	src: srcpaths.js,
	dest: destpaths.js
}));

gulp.task('vi', gulp.series([
	'vi_editor',
	'vi_js',
	"vi_css",
	"vi_icons",
	"vi_images"
]));

gulp.task('default', gulp.series([
	'vi_editor',
	'vi_js',
	"vi_css",
	"vi_icons",
	"vi_images"
]));
