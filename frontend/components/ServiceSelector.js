import { services } from "../data/services"
// import ServiceCard from '../components/ServiceCard'

import { useState } from "react"

const ServiceCard = ({ selection, svc, onSelection }) => {
    return <div onClick={onSelection} className={"flex w-full items-center transition-all p-2 ease-in-out hover:cursor-pointer " + (selection[svc._id] === 1 ? "bg-green-300" : "hover:bg-neutral-300")}>
        <div className="rounded-full h-10 p-1">
          <img className="w-full h-full" src={svc.svc_img}></img>
        </div>
        <div className="h-10 flex justify-center items-center p-1">
          <h2 className="text-md">{svc.svc_name}</h2>
        </div>
  </div>
}

export default function ServiceSelector({setSvc}) { 

  const [selection, setSelection] = useState([0, 0, 0, 0])

  const handleChooseSvc = (s) => {
    switch (s) {
      case 0:
        setSelection([1, 0, 0, 0])
        setSvc(selection)
        break;
      
      case 1:
        setSelection([0, 1, 0, 0])  
        setSvc(selection)
        break;
        
      case 2:
        setSelection([0, 0, 1, 0])
        setSvc(selection)
        break;
        
      case 3:
        setSelection([0, 0, 0, 1])
        setSvc(selection)
        break;
    }
  }
  
  return <aside id="service-selector" className="w-56">
    <div className="overflow-y-auto rounded bg-gray-100 m-4">
      {
        services.map((s, idx) => (
          <ServiceCard key={idx} selection={selection} onSelection={() => handleChooseSvc(s._id)} svc={s}>
          </ServiceCard>
      ))
    }
    </div>
</aside>
}