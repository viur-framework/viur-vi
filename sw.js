self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open('sw-cache').then(function(cache) {
		return cache.addAll([
	      '/vi/s/pyodide/pyodide.asm.data',
	      '/vi/s/pyodide/pyodide.asm.wasm',
	      '/vi/s/pyodide/pyodide.asm.js',
	      '/vi/s/pyodide/pyodide.asm.data.js',
	      '/vi/s/pyodide/pyodide.js',
		  '/vi/s/main.html'
        ])
    })
  );
});

self.addEventListener('fetch', function(event) {
	//console.debug('Fetch for ', event.request.url);
    event.respondWith(
	    caches.match(event.request).then(function(response) {
	        if (response) {
		        // console.debug('Found ', event.request.url, ' in cache');
		        return response;
	        }
	        //console.debug('Request for ', event.request.url);
	        return response || fetch(event.request);
	    })
    );
});
