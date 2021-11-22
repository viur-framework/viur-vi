class FileSystemAccess {
	constructor() {
		this.dirHandler = null;
	}

	/**
		@param {boolean} setnew To set the Dir new
	 */
	async selectDir(setnew = false) {
		if (this.dirHandler != null && setnew) {
			this.dirHandler = await window.showDirectoryPicker();
		} else {
			this.dirHandler = await window.showDirectoryPicker();
		}
	}


	async setMainDir(path) {

		this.dirHandler = await this.dirHandler.getDirectoryHandle(path, {create: true});

	}

	/**
	 *
	 * @returns {boolean} Returns if an Directory is selected
	 */
	checkDirSelected()
	{
		return this.dirHandler!=null;
	}

	/**
	 *	Check if a File or a Directory exist in the actual this.dirHandler or an specific path
	 * @param {string} name File or Directoryname to check if exist
	 * @param {Array} path Path to check where the File or Directory exist
	 * @returns {Promise<boolean>}
	 */
	async checkIfExist(name,path=[])
	{
		let dirHandlerTMP = this.dirHandler;
		for (let i = 0; i < path.length; i++) {
			dirHandlerTMP = await dirHandlerTMP.getDirectoryHandle(path[i]);
		}
		for await (const [key, value] of dirHandlerTMP.entries()) {
    		if(value["name"]==name)
			{
				return true;
			}
		}
		return false;
	}


	/**
	 * @param content
	 * @param {string} name Name of the file
	 * @param path Path of the file relative to the dirHandler
	 * @param append If true content is wirtten at the end of the File
	 * @returns {Promise<void>}
	 */
	async writeFile(content, name, path="", append = false) {
		let dirHandlerTMP = this.dirHandler;
		path=this.splitPath(path);
		for (let i = 0; i < path.length; i++) {
			dirHandlerTMP = await dirHandlerTMP.getDirectoryHandle(path[i], {create: true});
		}
		const fileHandler = await dirHandlerTMP.getFileHandle(name, {create: true});
		const writable = await fileHandler.createWritable();
		if (append) {
			const old_content = await (await fileHandler.getFile()).text();
			await writable.write(old_content+content); // Fixme
		}
		else
		{
			await writable.write(content);
		}


		await writable.close();
	}

	/**
	 *
	 * @param {} path Path of the file to read from
	 */
	async readFile(path){
		let dirHandlerTMP = this.dirHandler;
		path=this.splitPath(path);
		for (let i = 0; i < path.length; i++) {
			dirHandlerTMP = await dirHandlerTMP.getDirectoryHandle(path[i]);
		}

	}
		/**
	 * If path is a String like "/dir1/dir2/" it will split to an Array with the Parts  like ["dir1","dir2"]
	 * @param {} path Path to spit
	 */
	splitPath(path){
		if(typeof(path)==="string")
		{
			let pathArray=path.split("/");
			if (pathArray[pathArray.length-1]=="")
			{
				pathArray.splice(pathArray.length-1, 1);
			}
			return pathArray;
		}
		return path
	}

}
window.top.fsAccess = new FileSystemAccess()

async function selectDir(){
	if (!window.top.fsAccess.checkDirSelected()){
		await window.top.fsAccess.selectDir(true)
	}
}

async function fileDownload(url,filename){
	const resp = await fetch(url)
	if (!resp.ok){
		return -1
	}
	const data = await resp.blob()
	await writeFile(data, filename)
}



async function writeFile(content, name, path, append = false){
	await window.top.fsAccess.writeFile(content, name, path, append)
}


function Sleep(milliseconds) {
 return new Promise(resolve => setTimeout(resolve, milliseconds));
}

/*
async function fileDownload(url,filename){
	await fetch(url).then((resp)=>{
		if (resp.ok) {
			resp.blob().then(data => {
				writeFile(data, filename)
			});
		}
	})
}



async function writeFile(content, name, path, append = false){
	await window.top.fsAccess.writeFile(content, name, path, append)
}*/
