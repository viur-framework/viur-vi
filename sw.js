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
console.log("FFFFFFF")
console.log(self);
self.addEventListener('fetch', function(event) {
	console.log('Fetch event for ', event.request.url);
  event.respondWith(
    caches.match(event.request).then(function(response) {
    	if (response) {
        console.log('Found ', event.request.url, ' in cache');
        return response;
      }
      console.log('Network request for ', event.request.url);
      return response || fetch(event.request);
    })
  );
});
