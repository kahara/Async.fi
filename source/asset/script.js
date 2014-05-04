$(document).ready(function() {
    var ww = parseInt($('#wrapper').css('width'));
    var resize = function(img) {
	var iw = parseInt($(img).css('width'));
	if(iw <= ww) return;
	var f = parseInt($(img).css('height')) / iw;
	iw = ww;
	$(img).css({
	    'width': iw + 'px',
	    'height': Math.floor(iw*f) + 'px'
	});
    };    
    $('#wrapper article').each(function(index, article) {
	$('img', article).each(function(index, img) {
	    if(img.complete) {
		resize(img);
	    } else {
		$(img).bind('load', function() {
		    resize(img);
		});
	    }
	});
    });
});