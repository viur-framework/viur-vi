module.exports = function (gulp, plugins, options) {
	plugins.del = require('del');
	plugins.imagemin = require('gulp-imagemin');
	plugins.mozjpeg = require('imagemin-mozjpeg');
	plugins.optipng = require('imagemin-optipng');
	plugins.svgo = require('imagemin-svgo');

	return function () {
		plugins.del([options.dest + '/**/*',], {force: true});

		return gulp.src(options.src)

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
			.pipe(plugins.rename(function(path){
				if (path.extname ) {
					if (path.dirname==="custom/static/images"){
						path.dirname = '';
					}
				}
			}))
			.pipe(gulp.dest(options.dest));
	}
};
