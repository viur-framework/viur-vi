// Project data

var appURL = 'http://www.viur.is';
var appName = 'My App';
var appDescription = 'This is my application';

var developerName = 'Mausbrand Infosys';
var developerURL = 'http://mausbrand.de/';

var backgroundColor = '#fff'; // Background color of app icons.

var srcpaths = {
  less: './less/**/*.less',
  icons: './embedsvg/icons/**/*',
  logos: './embedsvg/logos/**/*',
  js : './js/**/*.js'
};

var destpaths = {
  css: '../public/css',
  embedsvg: '../public/embedsvg',
  js: '../public/js'
};

// Variables and requirements

const gulp = require('gulp');
const rename = require('gulp-rename');

const less = require('gulp-less');
const path = require('path');

const postcss = require('gulp-postcss');
const zindex = require('postcss-zindex');
const autoprefixer = require('gulp-autoprefixer');
const focus = require('postcss-focus');
const nocomments = require('postcss-discard-comments');
const nano = require('gulp-cssnano');
const jmq = require('gulp-join-media-queries');

const svgmin = require('gulp-svgmin');
const imagemin = require('gulp-imagemin');
const pngquant = require('imagemin-pngquant');
const cheerio = require('gulp-cheerio');

const favicons = require('gulp-favicons');

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
      		paths: [ path.join(__dirname, 'less', 'includes') ]
    	})) // compile less to css
        .pipe(autoprefixer({
            browsers: ['last 2 versions'],
            cascade: false
        })) // add vendor prefixes
		.pipe(postcss(processors)) // clean up css
		.pipe(jmq({
			log: true
		}))
        .pipe(rename('style.css'))
        .pipe(gulp.dest(destpaths.css)) // save cleaned version
        .pipe(nano()) // minify css
        .pipe(rename('style.min.css')) // save minified version
    	.pipe(gulp.dest(destpaths.css));
});

gulp.task ('icons', function () {
	return gulp.src(srcpaths.icons)
	.pipe(imagemin({
		progressive: true,
		svgoPlugins: [{removeViewBox: false}],
		use: [pngquant()]
	}))
    .pipe(cheerio({
      run: function ($, file) {
        $('style').remove()
        $('[id]').removeAttr('id')
        //$('[class]').removeAttr('class')
        $('[fill]').removeAttr('fill')
        $('svg').addClass('icon')
      },
      parserOptions: {xmlMode: true}
    }))
	.pipe(rename({prefix: "icon-"}))
	.pipe(gulp.dest(destpaths.embedsvg));
});

gulp.task ('logos', function () {
	return gulp.src(srcpaths.logos)
	.pipe(imagemin({
		progressive: true,
		svgoPlugins: [{removeViewBox: false}],
		use: [pngquant()]
	}))
    .pipe(cheerio({
      run: function ($, file) {
        $('svg').addClass('logo')
      },
      parserOptions: {xmlMode: true}
    }))
	.pipe(rename({prefix: "logo-"}))
	.pipe(gulp.dest(destpaths.embedsvg));
});

gulp.task('watch', function () {
   gulp.watch(srcpaths.less, ['css']);
   gulp.watch(srcpaths.icons, ['icons']);
   gulp.watch(srcpaths.logos, ['logos']);
});

gulp.task('default', ['css', 'icons', 'logos']);
