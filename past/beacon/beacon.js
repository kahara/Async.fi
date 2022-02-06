var params = {
    m: undefined,
    a: 0,
    v: 1,
    t: 100,
    f: 700,
    c: 'ffffff'
};
location.search.substr(1).replace(/\/$/g, '').split('&').forEach(function(e) {
	try {
	    var a = e.split('='), k = a[0], v = a[1];
	    if(/^(\-|\+)?([0-9]+)$/.test(v)) {
		params[k] = Number(v);
	    } else {
		params[k] = unescape(v);
	    }
	} catch(e) {}
    });

if(params['m']) {
    document.getElementById('usage').style.display = 'none';
    document.getElementById('beacon').style.display = 'block';
	
    // do main loop once every 'dot' length of time
    var counter = 0, previous_state = 0;
    window.setInterval(function() {
	    if(message[counter] != previous_state) {
		if(message[counter]) key_on();
		else key_off();
	    }
	    previous_state = message[counter];
	    if(counter<message.length-1) {
		counter++;
	    } else {
		counter = 0;
	    }
	}, params['t']);

    var ac = new (window.AudioContext || window.webkitAudioContext());
    var osc = ac.createOscillator();
    var gain = ac.createGain();
    
    osc.connect(gain);
    gain.connect(ac.destination);
    
    osc.frequency.value = params['f'];
    gain.gain.value = 0;
    
    osc.start(0);
    
    function key_on()
    {
	if(params['v'] === 1) document.getElementById('beacon').style.backgroundColor = '#' + params['c'];
	if(params['a'] === 1) gain.gain.value = 1.0;
    }
    
    function key_off()
    {
	if(params['v'] === 1) document.getElementById('beacon').style.backgroundColor = '#000000';
	if(params['a'] === 1) gain.gain.value = 0.0;
    }
    
    var symbols = {
	'letter': '000',
	'word':   '0000000',
	'A':      '10111',
	'B':      '111010101',
	'C':      '11101011101',
	'D':      '1110101',
	'E':      '1',
	'F':      '101011101',
	'G':      '111011101',
	'H':      '1010101',
	'I':      '101',
	'J':      '1011101110111',
	'K':      '111010111',
	'L':      '101110101',
	'M':      '1110111',
	'N':      '11101',
	'O':      '11101110111',
	'P':      '10111011101',
	'Q':      '1110111010111',
	'R':      '1011101',
	'S':      '10101',
	'T':      '111',
	'U':      '1010111',
	'V':      '101010111',
	'W':      '1011101110111',
	'X':      '11101010111',
	'Y':      '1110101110111',
	'Z':      '11101110101',
	'Å':      '101110111010111',
	'Ä':      '10111010111',
	'Ö':      '10111011101',
	'0':      '1110111011101110111',
	'1':      '10111011101110111',
	'2':      '101011101110111',
	'3':      '1010101110111',
	'4':      '10101010111',
	'5':      '101010101',
	'6':      '11101010101',
	'7':      '1110111010101',
	'8':      '111011101110101',
	'9':      '11101110111011101',
	'!':      '1010111011101',
	'?':      '101011101110101',
	'/':      '1110101011101',
	'=':      '1110101010111',
	':':      '11101110111010101',
	',':      '1110111010101110111',
	'.':      '10111010111010111',
	'-':      '111010101010111',
	'(':      '111010111011101',
	')':      '1110101110111010111'
    };

    var message = [];
    params['m'] = params['m'].toUpperCase();

    for(var i=0; i<params['m'].length; i++) {
	if(params['m'][i] in symbols)
	    var symbol = params['m'][i];
	else
	    var symbol = 'word';
    
	symbols[symbol].split('').forEach(function(item) {
		if(item === '0') message.push(0);
		else message.push(1);
	    });
    
	if(i<params['m'].length-1 && params['m'][i] in symbols && params['m'][i+1] in symbols) {
	    symbols['letter'].split('').forEach(function(item) {
		    if(item === '0') message.push(0);
		    else message.push(1);		
		});
	}
    }
    
    symbols['word'].split('').forEach(function(item) {
	    if(item === '0') message.push(0);
	    else message.push(1);
	});

}