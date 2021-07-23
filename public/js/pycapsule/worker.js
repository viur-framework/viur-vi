// webworker.js

// Setup your project to serve `py-worker.js`. You should also serve
// `pyodide.js`, and all its associated `.asm.js`, `.data`, `.json`,
// and `.wasm` files as well:

// THIS IS THE DEFAULT PYODIDE WEBWORKER
importScripts('https://cdn.jsdelivr.net/pyodide/v0.17.0/full/pyodide.js');

async function loadScripts(){
	let promises = [];
	let url = "webworker_scripts.py"

	let path = ("/lib/python3.8/site-packages/scripts/"+url).split("/")
	promises.push(
		new Promise((resolve, reject) => {
			fetch("/vi/s/"+url, {}).then((response) => {
				if (response.status === 200) {
					response.text().then((code) => {
						let lookup = "";
						for (let i in path) {
							if (!path[i]) {
								continue;
							}

							lookup += (lookup ? "/" : "") + path[i];
							if (parseInt(i) === path.length - 1) {
								self.pyodide._module.FS.writeFile(lookup, code);
							} else {
								try {
									self.pyodide._module.FS.lookupPath(lookup);
								} catch {
									self.pyodide._module.FS.mkdir(lookup);
								}
							}
						}
						resolve();
					});
				} else {
					reject();
				}
			})
		})
	)
	return Promise.all(promises);
}


async function loadPyodideAndPackages(){
    await loadPyodide({ indexURL : 'https://cdn.jsdelivr.net/pyodide/v0.17.0/full/' });
}
let pyodideReadyPromise = loadPyodideAndPackages();

self.onmessage = async(event) => {
     // make sure loading is done
    await pyodideReadyPromise;
    await loadScripts();

    // Don't bother yet with this line, suppose our API is built in such a way:
    const {python, ...context} = event.data;
    // The worker copies the context in its own "memory" (an object mapping name to values)
    for (const key of Object.keys(context)){
        self[key] = context[key];
    }
    // Now is the easy part, the one that is similar to working in the main thread:
    try {
        self.postMessage({
            results: await self.pyodide.runPythonAsync(python)
        });
    }
    catch (error){
    	console.log(error.message)
        self.postMessage(
            {error : error.message}
        );
    }
}
