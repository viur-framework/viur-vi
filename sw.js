

self.addEventListener('install', function(event) {
		event.waitUntil(
			fetch('version.json')
			.then((response) => {
				return response.json();
			})
			.then((data) => {
				let versionInfo = data;
				console.log(data)
				let currentCacheName = "sw-cache-"+data["version"];

				caches.keys().then(function(names) {
				    for (let name of names)
				    	if (name != currentCacheName){
				    		caches.delete(name);
					    }

				}).then(()=>{
					caches.open(currentCacheName).then(function(cache) {
					return cache.addAll([
				      '/vi/s/pyodide/pyodide.asm.data',
				      '/vi/s/pyodide/pyodide.asm.wasm',
				      '/vi/s/pyodide/pyodide.asm.js',
				      '/vi/s/pyodide/pyodide.asm.data.js',
				      '/vi/s/pyodide/pyodide.js',
					  '/vi/s/main.html'
			        ])
			    })
				})


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

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.filter(function(cacheName) {
        }).map(function(cacheName) {
          return caches.delete(cacheName);
        })
      );
    })
  );
});



