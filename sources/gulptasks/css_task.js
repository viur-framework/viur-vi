module.exports = function (gulp, plugins, options) {

	plugins.path = require('path');
	plugins.less = require('gulp-less');
	plugins.postcss = require('gulp-postcss');
	plugins.zindex = require('postcss-zindex');
	plugins.autoprefixer = require('gulp-autoprefixer');
	plugins.focus = require('postcss-focus');
	plugins.nocomments = require('postcss-discard-comments');
	plugins.nano = require('gulp-clean-css');
	plugins.jmq = require('gulp-join-media-queries');
	plugins.rename = require('gulp-rename')

	return function () {
		return gulp.src(options.src)
			.pipe(plugins.less({
				//relativeUrls: true, //destroys is-loading path
				paths: [plugins.path.join(__dirname, 'less', 'includes')]
			}))
			.pipe(plugins.autoprefixer({
				cascade: false
			})) // add vendor prefixes
			.pipe(plugins.postcss([
				plugins.nocomments, // discard comments
				plugins.focus, // add focus to hover-states
				plugins.zindex, // reduce z-index values
			])) // clean up css
			.pipe(plugins.jmq())
			.pipe(plugins.rename('style.css'))
			.pipe(gulp.dest(options.dest)) // save cleaned version
			.pipe(plugins.nano()) // minify css
			.pipe(plugins.rename(function (path) {
				path.extname = '.min.css';
			})) // save minified version
			.pipe(gulp.dest(options.dest));
	}
};
