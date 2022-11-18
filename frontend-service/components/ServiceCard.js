import Image from "next/image"

export default function ServiceCard({ selection, svc, onSelection }) { 
  return (
    <div onClick={onSelection} className={"flex w-full items-center transition-all p-2 ease-in-out hover:cursor-pointer " + (selection[svc._id] === 1 ? "bg-green-300" : "hover:bg-neutral-300")}>
      <div className="rounded-full h-10 p-1">
        <img className="w-full h-full" src={svc.svc_img}></img>
      </div>
      <div className="h-10 flex justify-center items-center p-1">
        <h2 className="text-md">{svc.svc_name}</h2>
      </div>
    </div>
  )
}