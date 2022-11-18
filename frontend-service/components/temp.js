{
  svc[0] == 1 ? (
    <form className="flex flex-wrap justify-center items-center flex-col space-y-4">
    {/* <label className="block mb-2 text-sm font-medium text-gray-900" htmlFor="file_input">Upload image</label> */}
    <input className="block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer focus:outline-none" id="file_input" type="file"></input>
    <label className="">Uploaded</label>
    <img className="w-[224px] h-[224px] rounded-md" src="dashboard_assets/cat-dog-placeholder.jpeg"></img>
  </form>
  ) : svc[1] == 1 ? (
    <form className="flex flex-wrap justify-center items-center flex-col space-y-4">
    {/* <label className="block mb-2 text-sm font-medium text-gray-900" htmlFor="file_input">Upload image</label> */}
    <input className="block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer focus:outline-none" id="file_input" type="file"></input>
    <label className="">Uploaded</label>
    <img className="w-[224px] h-[224px] rounded-md" src="dashboard_assets/cat-dog-placeholder.jpeg"></img>
  </form>
    ) : svc[2] == 1 ? (
      <form className="flex flex-wrap justify-center items-center flex-col space-y-4">
      {/* <label className="block mb-2 text-sm font-medium text-gray-900" htmlFor="file_input">Upload image</label> */}
      <input className="block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer focus:outline-none" id="file_input" type="file"></input>
      <label className="">Uploaded</label>
      <img className="w-[224px] h-[224px] rounded-md" src="dashboard_assets/cat-dog-placeholder.jpeg"></img>
    </form>
  ) : null
}