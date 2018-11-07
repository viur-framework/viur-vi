const gulp = require('gulp');
const uglify = require('gulp-uglify');
const concat = require('gulp-concat');
const nano = require('gulp-cssnano');
const copy = require('copy');
const del = require('del');

// clean dist folder
gulp.task('clean', function () {
	return del('public/htmleditor/**/*', {force: true});
});

// copy editor specific fonts
gulp.task('font', function (cb) {
	copy('htmleditor/font/*', 'public/htmleditor/', cb);
});

// merge and minfy js
gulp.task('js', function () {
	return gulp.src([
		"htmleditor/jquery-3.3.1.js",
		"htmleditor/codemirror.js",
		"htmleditor/codemirror_mode_xml.js",
		"htmleditor/summernote-lite.js",
		"htmleditor/summernote-de-DE.js",
		"htmleditor/htmleditor.js"
	])
		.pipe(concat('htmleditor.min.js'))
		.pipe(uglify())
		.pipe(gulp.dest('./public/htmleditor/'))
});

// merge and minfy css
gulp.task('css', function () {
	return gulp.src([
		"htmleditor/codemirror.css",
		"htmleditor/summernote-lite.css"
	])
		.pipe(concat('htmleditor.min.css'))
		.pipe(nano())
		.pipe(gulp.dest('./public/htmleditor/'))
});

gulp.task('watch', function () {
	gulp.watch('htmleditor/**/*.less', ['css']);
	gulp.watch('htmleditor/**/*.css', ['css']);
	gulp.watch('htmleditor/**/*.js', ['js']);
});

// do all
gulp.task('default', ['clean', 'css', 'js', 'font']);
