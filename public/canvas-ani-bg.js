//////////////////////////////////////////////////////////////////////////////////
// A demonstration of a Canvas nebula effect
// (c) 2010 by R Cecco. <http://www.professorcloud.com>
// MIT License
//
// Please retain this copyright header in all versions of the software if
// using significant parts of it
//////////////////////////////////////////////////////////////////////////////////

$(document).ready(function(){	
													   
	(function ($) {			
			// The canvas element we are drawing into.      
			var	$canvas = $('#canvas');
			var	$canvas2 = $('#canvas2');
			var	$canvas3 = $('#canvas3');			
			var	ctx2 = $canvas2[0].getContext('2d');
			var	ctx = $canvas[0].getContext('2d');
			var	w = $canvas[0].width, h = $canvas[0].height;		
			var	img = new Image();	
			
			// A puff.
			var	Puff = function(p) {				
				var	opacity,
					sy = (Math.random()*540)>>0,
					sx = (Math.random()*960)>>0;
				
				this.p = p;
						
				this.move = function(timeFac) {						
					p = this.p + 0.1 * timeFac;				
					opacity = (Math.sin(p*0.05)*0.5);						
					if(opacity <0) {
						p = opacity = 0;
						sy = (Math.random()*540)>>0;
						sx = (Math.random()*960)>>0;
					}												
					this.p = p;																			
					ctx.globalAlpha = opacity;						
					ctx.drawImage($canvas3[0], sy+p, sy+p, 960-(p*2),540-(p*2), 0,0, w, h);								
				};
			};
			
			var	puffs = [];			
			var	sortPuff = function(p1,p2) { return p1.p-p2.p; };	
			puffs.push( new Puff(0) );
			puffs.push( new Puff(20) );
			puffs.push( new Puff(40) );
			
			var	newTime, oldTime = 0, timeFac;
					
			var	loop = function()
			{								
				newTime = new Date().getTime();				
				if(oldTime === 0 ) {
					oldTime=newTime;
				}
				timeFac = (newTime-oldTime) * 0.1;
				if(timeFac>3) {timeFac=3;}
				oldTime = newTime;						
				puffs.sort(sortPuff);							
				
				for(var i=0;i<puffs.length;i++)
				{
					puffs[i].move(timeFac);	
				}					
				ctx2.drawImage( $canvas[0] ,0,0,1920,1080);				
				setTimeout(loop, 10 );				
			};
			// Turns out Chrome is much faster doing bitmap work if the bitmap is in an existing canvas rather
			// than an IMG, VIDEO etc. So draw the big nebula image into canvas3
			var	$canvas3 = $('#canvas3');
			var	ctx3 = $canvas3[0].getContext('2d');
			$(img).bind('load',null, function() {  ctx3.drawImage(img, 0,0, 1920, 1080);	loop(); });
			img.src = '/vi/s/bg-login.jpg';
		
	})(jQuery);	 
});

