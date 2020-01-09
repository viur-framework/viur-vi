// Gulp Vi

var srcpaths = {
	less: './less/**/*.less',
	images: './images/**/*',
	embedsvg: './embedsvg/**/*',
};

var destpaths = {
	css: '../public/css',
	images: '../public/images',
	embedsvg: '../public/embedsvg',
};

// Variables and requirements

const gulp = require('gulp');

const path = require('path');
const del = require('del');
const rename = require('gulp-rename');

const less = require('gulp-less');
const autoprefixer = require('gulp-autoprefixer');
const postcss = require('gulp-postcss');
const zindex = require('postcss-zindex');
const focus = require('postcss-focus');
const nocomments = require('postcss-discard-comments');
const nano = require('gulp-cssnano');
const jmq = require('gulp-join-media-queries');
const stylefmt = require('gulp-stylefmt');

const imagemin = require('gulp-imagemin');
const cheerio = require('gulp-cheerio');
const concat = require('gulp-concat');
const uglify = require('gulp-uglify');

// clean destination folder
gulp.task('clean', function () {
	return del([
		destpaths.css + '/**/*',
		destpaths.images + '/**/*',
		destpaths.embedsvg + '/**/*',
	], {force: true});
});

// merge and minfy js
gulp.task('js', function () {
	return gulp.src([
		"htmleditor/jquery-3.3.1.js",
		"htmleditor/codemirror.js",
		"htmleditor/codemirror_mode_xml.js",
		"htmleditor/summernote-lite.js",
		"htmleditor/summernote-de-DE.min.js",
		"htmleditor/htmleditor.js"
	])
		.pipe(concat('htmleditor.min.js'))
		.pipe(uglify())
		.pipe(gulp.dest('../public/htmleditor/'))
});


// compilation and postproduction of LESS to CSS
gulp.task('css', function () {
	//gulp.start('dev')
	var processors = [
		nocomments, // discard comments
		focus, // add focus to hover-states
		zindex, // reduce z-index values
	];
	return gulp.src('./less/vi.less')
		.pipe(less({
			paths: [path.join(__dirname, 'less', 'includes')]
		})) // compile less to css
		.pipe(autoprefixer({
			browsers: ['last 2 versions'],
			cascade: false
		})) // add vendor prefixes
		.pipe(postcss(processors)) // clean up css
		.pipe(jmq())
		.pipe(stylefmt()) // syntax formatting
		.pipe(rename('style.css'))
		.pipe(gulp.dest(destpaths.css)) // save cleaned version
		.pipe(nano()) // minify css
		.pipe(rename('style.min.css')) // save minified version
		.pipe(gulp.dest(destpaths.css));
});

// reduce images for web
gulp.task('images', function () {
	return gulp.src(srcpaths.images)
		.pipe(imagemin([
			imagemin.jpegtran({progressive: true}),
			imagemin.optipng({optimizationLevel: 5}),
			imagemin.svgo({
				plugins: [
					{removeViewBox: false},
					{removeDimensions: true}
				]
			})
		]))
		.pipe(gulp.dest(destpaths.images));
});

gulp.task('embedsvg', function () {
	return gulp.src(srcpaths.embedsvg)
		.pipe(imagemin([
			imagemin.jpegtran({progressive: true}),
			imagemin.optipng({optimizationLevel: 5}),
			imagemin.svgo({
				plugins: [
					{removeViewBox: false},
					{removeDimensions: true}
				]
			})
		]))
		.pipe(cheerio({
			run: function ($, file) {
				$('style').remove();
				$('title').remove();
				$('[id]').removeAttr('id')
				//$('[class]').removeAttr('class')
				//$('[fill]').removeAttr('fill')
				$('svg').addClass('icon')
			},
			parserOptions: {xmlMode: true}
		}))
		.pipe(rename(function (path) {
			if (path.extname) {
				if (path.dirname === '.') {
					path.dirname = '';
				}
				path.basename = path.dirname + '-' + path.basename;
				path.dirname = '';
			}
		}))
		.pipe(gulp.dest(destpaths.embedsvg));
});

gulp.task('watch', function () {
	gulp.watch(srcpaths.less, gulp.series(['css']));
	gulp.watch(srcpaths.embedsvg, gulp.series(['embedsvg']));
	gulp.watch(srcpaths.images, gulp.series(['images']));
});

gulp.task('default', gulp.series(['clean', 'css', 'embedsvg', 'images']));
