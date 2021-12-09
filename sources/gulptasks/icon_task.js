module.exports = function (gulp, plugins, options) {
	plugins.rename = require('gulp-rename');
	plugins.cheerio = require('gulp-cheerio');
	plugins.del = require('del');
	plugins.imagemin = require('gulp-imagemin');
	plugins.flatten = require('gulp-flatten');
	plugins.exec = require("gulp-exec");
	plugins.print = require("gulp-print").default;
	plugins.filter = require("gulp-filter");
	plugins.mozjpeg = require('imagemin-mozjpeg');
	plugins.optipng = require('imagemin-optipng');
	plugins.svgo = require('imagemin-svgo');

	gulp.task("vi_icons_task", function (){
		plugins.del([options.dest + '/**/icon-*',], {force: true});

		return gulp.src(options.src)
			.pipe(plugins.filter(['**/*.svg','!*/logos/**','!*/**/logos/**'])) // alles außer logos
			.pipe(plugins.imagemin([
				plugins.mozjpeg({progressive: true}),
				plugins.optipng({optimizationLevel: 5}),
				plugins.svgo({
					plugins: [
						{removeViewBox: false},
						{removeDimensions: true}
					]
				})
			]))
			.pipe(plugins.cheerio({
				run: function ($, file) {
					$('style').remove();
					$('[id]').removeAttr('id');
					//$('[class]').removeAttr('class')
					$('[fill]').removeAttr('fill');
					$('svg').addClass('icon').removeAttr("x").removeAttr("y");
				},
				parserOptions: {xmlMode: true}
			}))
			.pipe(plugins.rename({prefix: "icon-"}))
			.pipe(plugins.flatten())
			.pipe(gulp.dest(options.dest));
	})

	gulp.task("vi_logos_task", function (){
		plugins.del([options.dest + '/**/logo-*'], {force: true});

		return gulp.src(options.src)
			.pipe(plugins.filter(['embedsvg/logos/**','**/embedsvg/logos/**']))
			.pipe(plugins.imagemin([
				plugins.imagemin.mozjpeg({progressive: true}),
				plugins.imagemin.optipng({optimizationLevel: 5}),
				plugins.imagemin.svgo({
					plugins: [
						{removeViewBox: false},
						{removeDimensions: true}
					]
				})
			]))
			.pipe(plugins.cheerio({
				run: function ($, file) {
					$('svg').addClass('logo').removeAttr('x').removeAttr('y');
				},
				parserOptions: {xmlMode: true}
			}))
			.pipe(plugins.rename({prefix: 'logo-'}))
			.pipe(plugins.flatten())
			.pipe(gulp.dest(options.dest));
	})

	return gulp.series([
		'vi_icons_task',
		"vi_logos_task"
	])
};
