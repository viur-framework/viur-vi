class app {

	constructor(modules){
		languagePluginLoader.then(() => {
			this.fetchSources(modules).then(() => {
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

	fetchSources(modules) {
		let promises = [];

		for( let module of modules )
		{
			promises.push(
				new Promise((resolve, reject) => {
					fetch(`/${module}/s/files.json`, {}).then((response) => {
						if (response.status === 200) {
							response.text().then((list) => {
								let files = JSON.parse(list);

								this.loadSources(module, files).then(() => {
									resolve();
								})
							})
						} else {
							reject();
						}
					})
				}));
		}

		return Promise.all(promises).then(() => {
			for( let module of modules ) {
				window.pyodide.loadedPackages[module] = "default channel";
			}

			window.pyodide.runPython(
				'import importlib as _importlib\n' +
				'_importlib.invalidate_caches()\n'
			);
		});
	}

	initializingComplete() {
		document.body.classList.remove("is-loading")
	}

}

(function () {
	window.top.app = new app(["vi", "vi_plugins"]);
})();
