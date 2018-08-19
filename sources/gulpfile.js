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
    .pipe(jmq({
      log: true
    }))
    .pipe(rename('style.css'))
    .pipe(gulp.dest(destpaths.css)) // save cleaned version
    .pipe(nano()) // minify css
    .pipe(rename('style.min.css')) // save minified version
    .pipe(gulp.dest(destpaths.css));
});

// reduce images for web
gulp.task('images', function () {
  return gulp.src(srcpaths.images)
    .pipe(imagemin({
      progressive: true,
      svgoPlugins: [{removeViewBox: false}],
      use: [pngquant()]
    }))
    .pipe(gulp.dest(destpaths.images));
});

gulp.task('embedsvg', function () {
  return gulp.src(srcpaths.embedsvg)
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
  gulp.watch(srcpaths.less, ['css']);
  gulp.watch(srcpaths.embedsvg, ['embedsvg']);
  gulp.watch(srcpaths.images, ['images']);
});

gulp.task('default', gulp.series(['css', 'embedsvg', 'images']));
