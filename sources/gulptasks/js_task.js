module.exports = function (gulp, plugins, options) {

	plugins.sourcemaps = require('gulp-sourcemaps');
	plugins.babel = require('gulp-babel');
	plugins.concat = require('gulp-concat');
	plugins.uglify = require('gulp-uglify');
	plugins.nano = require('gulp-clean-css');
	plugins.copy = require('copy');

	return function () {
		return gulp.src(options.src)
			.pipe(plugins.concat('vi.min.js'))
			.pipe(plugins.uglify())
			.pipe(gulp.dest(options.dest));
	}
};
