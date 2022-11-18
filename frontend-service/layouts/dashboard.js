import Image from 'next/image'

import logo from '../public/sac-logo.png'

export default function DashboardLayout({ children }) {
  return <div className="w-screen">
          <div className="bg-green-300 text-center p-2 flex items-center">
              <Image className='p-2' alt='sac-logo' src={logo} height={50} width={70}></Image>
              <p className='p-2 font-bold'>SAC Research Group @ Concordia University, Montreal.</p>
          </div>
          <div>
            {children}
          </div>
        </div>
}