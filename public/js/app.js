class app {

	constructor(){

		languagePluginLoader.then(() => {
			this.fetchSources().then(() => {
				window.pyodide.loadedPackages["vi"] = "default channel";
				window.pyodide.loadedPackages["vi_plugins"] = "default channel";

				window.pyodide.runPython(
						'import importlib as _importlib\n' +
						'_importlib.invalidate_caches()\n'
				);

				window.pyodide.runPythonAsync("import vi\nimport vi_plugins\nvi.start()").then(() => this.initializingComplete());
			});
		});

	}

	loadSources(module, files) {
		let promises = [];
		let baseURL = `/${module}/s/`;

		for (let f in files) {
			promises.push(
					new Promise((resolve, reject) => {
						let file = files[f];
						let url = baseURL + file;

						fetch(url, {}).then((response) => {
							if (response.status === 200)
								return response.text().then((code) => {
									let path = ("/lib/python3.7/site-packages/" + module + "/" + file).split("/");
									let lookup = "";

									for (let i in path) {
										if (!path[i]) {
											continue;
										}

										lookup += "/" + path[i];

										if (parseInt(i) === path.length - 1) {
											window.pyodide._module.FS.writeFile(lookup, code);
											console.debug(`fetched ${lookup}`);
										} else {
											try {
												window.pyodide._module.FS.lookupPath(lookup);
											} catch {
												window.pyodide._module.FS.mkdir(lookup);
												console.debug(`created ${lookup}`);
											}
										}
									}

									resolve();
								});
							else
								reject();
						});
					})
			);
		}

		return Promise.all(promises);
	}

	fetchSources() {
		let promises = [];

		for( let i of ["vi", "vi_plugins"] )
		{
			promises.push(
				new Promise((resolve, reject) => {
					fetch(`/${i}/s/files.json`, {}).then((response) => {
						if (response.status === 200) {
							response.text().then((list) => {
								let files = JSON.parse(list);

								this.loadSources(i, files).then(() => {
									resolve();
								})
							})
						} else {
							reject();
						}
					})
				}));
		}

		return Promise.all(promises);
	}

	initializingComplete() {
		document.body.classList.remove("is-loading")
	}

}

(function () {
	window.top.app = new app();
})();
